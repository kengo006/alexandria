# -*- coding: utf-8 -*-
"""crossref_lookup.py — registry check at ingestion (roles/librarian.md, "Registry check and retraction screening").

Looks a work up in CrossRef (the DOI registration agency; public GET, no key, no install) and does two things:
  1. fills in a DOI where one exists, which widens what the retraction screen can check
     (tools/retraction_check.py matches by DOI; a source with no DOI is outside its reach);
  2. checks the metadata you filed against the registry, which catches catalogue errors at the source:
     a reprint year filed as the first-edition year, a translation filed under the original's year.

🔒 Conservative by design: a wrong DOI is worse than no DOI, because the retraction screen will then
   report on a different work and say it is clean. A title that is not close enough, a year that does
   not fit, or an --author surname that is not among CrossRef's authors returns "no confident match —
   decide by hand" and never a DOI to paste. Without --author, the author is not checked, and the result says so.
⚠ "Not in CrossRef" is not "does not exist". Monographs, book chapters and venues CrossRef does not index
   are routinely absent; for those, "none" is the expected answer and not a defect.

Usage:
  python tools/crossref_lookup.py "<title>" [--author "<surname>"] [--year 2022] [--json]
  python tools/crossref_lookup.py --self-test
Exit codes: 0 = confident match (DOI printed) / 2 = no confident match / 3 = network or API error
Set CROSSREF_MAILTO=you@example.org to join CrossRef's polite pool (optional).
"""
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
# Redirected to a file or a pipe, Python on Windows writes in the code page (cp1252, cp950), which cannot print
# the marks below or an accented file name, and the run dies with UnicodeEncodeError. Write UTF-8 instead.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

API = "https://api.crossref.org/works"
_MAILTO = os.environ.get("CROSSREF_MAILTO", "").strip()
UA = "alexandria-librarian/1.0" + (f" (mailto:{_MAILTO})" if _MAILTO else "")

# Thresholds. Token Jaccard on normalised titles; calibrated upstream on a few hundred humanities and
# social-science works. Raise them before you lower them: the asymmetry above is the whole point.
CONFIDENT_SIM = 0.7
WEAK_SIM = 0.5
YEAR_TOLERANCE = 1


def norm(s: str) -> str:
    """Lowercase, punctuation to spaces, collapse whitespace."""
    s = (s or "").lower()
    s = re.sub(r"[^\w\s]", " ", s, flags=re.U)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str) -> float:
    """Token Jaccard: intersection over union. Conservative, and enough."""
    ta, tb = set(norm(a).split()), set(norm(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def query(title: str, author: str = "", rows: int = 5) -> list:
    params = {"query.bibliographic": title, "rows": str(rows)}
    if author:
        params["query.author"] = author
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return data.get("message", {}).get("items", [])


def _year(item: dict) -> int:
    for k in ("published-print", "published-online", "published", "issued"):
        dp = (item.get(k) or {}).get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            return int(dp[0][0])
    return 0


def _fold(s: str) -> str:
    """Lowercase, accents removed: 'Lévi' and 'Levi' compare equal."""
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if not unicodedata.combining(c))


def judge(title: str, items: list, year: int = 0, author: str = "") -> dict:
    """Score CrossRef items against the title (and year). Returns
    {doi, sim, cr_title, cr_year, cr_authors, container, verdict, note}; verdict is
    'confident' / 'weak' / 'none'."""
    if not items:
        return {"verdict": "none", "note": "not in CrossRef (common for monographs and chapters; not a defect)"}
    scored = sorted(((title_sim(title, (it.get("title") or [""])[0]), it) for it in items), key=lambda x: -x[0])
    sim, it = scored[0]
    ct, cy = (it.get("title") or [""])[0], _year(it)
    authors = "; ".join((a.get("family") or "").strip() for a in (it.get("author") or [])[:3]) or "?"
    container = (it.get("container-title") or [""])[0]
    year_ok = (year == 0) or (cy and abs(cy - year) <= YEAR_TOLERANCE)
    # The same title by another author is the commonest wrong match (a monograph CrossRef does not index, and a
    # namesake it does): the surname you gave must be among CrossRef's authors.
    want = _fold(author).split()[-1] if author.strip() else ""
    author_ok = not want or want in [_fold(a.get("family") or "") for a in (it.get("author") or [])]
    if sim >= CONFIDENT_SIM and year_ok and author_ok:
        verdict = "confident"
        note = f"⚠ year differs: filed {year}, CrossRef {cy} (check the catalogue entry: reprint? translation?)" \
            if year and cy and cy != year else ""
        if not want:
            note = (note + " · " if note else "") + "author not checked (no --author given)"
    elif sim >= WEAK_SIM:
        verdict = "weak"
        note = (f"⚠ author differs: you gave {author}, CrossRef lists {authors}: check the DOI by hand before filing it"
                if not author_ok else
                f"⚠ title only {sim:.2f} similar (or the year does not fit): check the DOI by hand before filing it")
    else:
        verdict = "none"
        note = f"closest is only {sim:.2f}: no confident match in CrossRef"
    return {"doi": it.get("DOI", ""), "sim": round(sim, 3), "cr_title": ct, "cr_year": cy,
            "cr_authors": authors, "container": container, "verdict": verdict, "note": note}


def best_match(title: str, author: str = "", year: int = 0) -> dict:
    try:
        items = query(title, author)
    except Exception as e:  # noqa: BLE001 — any failure is reported as an error, never as "none"
        return {"verdict": "error", "note": f"CrossRef query failed: {e}"}
    return judge(title, items, year, author)


def _self_test() -> int:
    """Offline: canned CrossRef items, the four verdicts, and the error path."""
    def item(t, y, doi="10.1/x", fam="Doe"):
        return {"title": [t], "issued": {"date-parts": [[y]]}, "DOI": doi, "author": [{"family": fam}],
                "container-title": ["Journal"]}
    cases = [
        ("exact title, same year", "Monuments and Memory", [item("Monuments and memory", 2011)], 2011, "confident", ""),
        ("exact title, year off by one", "Monuments and Memory", [item("Monuments and Memory", 2012)], 2011, "confident", "year differs"),
        ("exact title, year off by ten", "Monuments and Memory", [item("Monuments and Memory", 2021)], 2011, "weak", ""),
        ("half the words", "Monuments and Memory in Public Space", [item("Memory and the City", 2011)], 0, "none", ""),
        ("close but not enough", "Monuments and Public Memory", [item("Monuments and Memory Today", 2011)], 0, "weak", ""),
        ("not in CrossRef", "An Unindexed Monograph", [], 0, "none", "not in CrossRef"),
        ("best of several", "Oral History Methods",
         [item("History of Methods", 2001, "10.1/a"), item("Oral history methods", 2001, "10.1/b")], 2001, "confident", ""),
    ]
    bad = 0
    for name, title, items, year, want, note_has in cases:
        r = judge(title, items, year)
        ok = r["verdict"] == want and note_has in r["note"]
        if name == "best of several":
            ok = ok and r["doi"] == "10.1/b"
        bad += not ok
        print(("ok   " if ok else "FAIL ") + f"{name}: {r['verdict']} (sim {r.get('sim')})")
    global query
    real = query
    def boom(*a, **k):
        raise OSError("offline")
    query = boom
    r = best_match("anything")
    query = real
    ok = r["verdict"] == "error"
    bad += not ok
    print(("ok   " if ok else "FAIL ") + "network failure is an error, not 'none'")
    r = judge("Monuments and Memory", [item("Monuments and Memory", 2011, fam="Smith")], 2011, author="Doe")
    ok = r["verdict"] == "weak" and "author differs" in r["note"]
    bad += not ok
    print(("ok   " if ok else "FAIL ") + "same title and year, another author: weak, not confident")
    print(f"{9 - bad} of 9 as expected")
    return 1 if bad else 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return _self_test()
    title, author, year, as_json, rest, i = "", "", 0, False, [], 0
    while i < len(args):
        if args[i] == "--author" and i + 1 < len(args):
            author = args[i + 1]; i += 2
        elif args[i] == "--year" and i + 1 < len(args):
            year = int(re.sub(r"\D", "", args[i + 1]) or 0); i += 2
        elif args[i] == "--json":
            as_json = True; i += 1
        else:
            rest.append(args[i]); i += 1
    title = " ".join(rest)
    if not title:
        print(__doc__); return 3

    r = best_match(title, author, year)
    code = {"confident": 0, "weak": 2, "none": 2, "error": 3}[r["verdict"]]
    if as_json:
        print(json.dumps(r, ensure_ascii=False))
        return code
    print("=== CrossRef registry check ===")
    if r["verdict"] in ("error", "none"):
        print(("❌ " if r["verdict"] == "error" else "○ ") + r["note"])
        return code
    print(f"{'✅' if r['verdict'] == 'confident' else '🟡'} verdict={r['verdict']}  similarity={r['sim']}")
    print(f"  DOI          : {r['doi']}")
    print(f"  title        : {r['cr_title']}")
    print(f"  year/authors : {r['cr_year']} / {r['cr_authors']}")
    print(f"  container    : {r['container']}")
    if r["note"]:
        print(f"  {r['note']}")
    print(f"  → file it: doi: \"{r['doi']}\"" if r["verdict"] == "confident"
          else "  → check by hand before filing (🔒 a wrong DOI is worse than none)")
    return code


if __name__ == "__main__":
    sys.exit(main())
