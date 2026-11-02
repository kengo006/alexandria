# -*- coding: utf-8 -*-
"""ledger_to_bibliography.py — build the reference list from the ledger and the notes, not by retyping
(roles/writer.md §8 ledger; Phase 6 bibliography check; Layer 1 "every bibliographic detail checked").

Purpose: remove the whole class of transcription errors in a hand-typed bibliography (two real cases: a URL that
lost its "https", a DOI that picked up a full-width quotation mark and returned 404). Structured fields (author,
year, title, DOI) come from the ledger and the note's front matter, never retyped; a CSL processor formats them.

⚠ Honest limits: this removes transcription errors; it is not the bibliographic check itself. The note schema has
no volume / issue / publisher fields, so missing fields are flagged "to fill", never guessed. --enrich asks
CrossRef through the same conservative gate as tools/crossref_lookup.py (confident matches only, source noted).
The first-hand check before anything goes out (writer Layer 1) still applies: this list is its input.

What stays out, and why it is said:
  withdrawn  a ledger row struck through (~~…~~) or marked withdrawn/retracted in a cell: the ledger's own words
             are quoted as the reason
  blocklist  --blocklist FILE (one surname per line; "!Surname_YYYY" lines exempt one work): a surname hit is HELD
             for a human to confirm it is the same person, never treated as decided; without a file the report says
             the blocklist was not checked
  problems   no note, several notes that cannot be told apart, a note without a title

Usage:
  python tools/ledger_to_bibliography.py --project <dir> [--notes notes] [--enrich] [--blocklist FILE] [--csl STYLE.csl]
  python tools/ledger_to_bibliography.py --self-test
Writes <project>/_outputs/bibliography.csl.json (always) and <project>/_outputs/references_<date>.md (rendered with
pandoc --citeproc if pandoc is installed; otherwise the file lists the entries and says it was not rendered).
"""
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from crossref_lookup import best_match  # noqa: E402  the conservative gate lives there
from retraction_check import note_doi, CITE_RE  # noqa: E402  one reading of DOIs and of "Author (Year)"

SOURCE_HEAD = re.compile(r"source|citation|cite|work|reference", re.I)
WITHDRAWN = re.compile(r"withdrawn|retracted|struck|removed|❌", re.I)


def parse_ledger(ledger: Path, source_col=None):
    """{(author, year): {"rows", "hints", "struck", "why"}}, unparsed rows, row count."""
    works, unparsed, n, col = {}, [], 0, source_col
    for ln in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.lstrip().startswith("|") or re.match(r"^\s*\|[\s:|\-]+\|\s*$", ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if cells[0].lower() in ("id", "#"):
            if col is None:
                col = next((i for i, c in enumerate(cells) if i and SOURCE_HEAD.search(c)), None)
            continue
        n += 1
        rid = cells[0]
        si = col if col is not None and col < len(cells) else next(
            (i for i, c in enumerate(cells) if i and CITE_RE.search(re.sub(r"~~|\*\*|`", "", c))), len(cells))
        src = cells[si] if si < len(cells) else ""
        # Struck or withdrawn? Only the source cell's strikethrough or a status cell to its right counts (a claim
        # that mentions a retracted paper is not a withdrawn row). The reason is the ledger's own words.
        after = cells[si + 1:]
        struck = src.startswith("~~") or any(WITHDRAWN.search(c) for c in after)
        why = next((c for c in reversed(after) if WITHDRAWN.search(c)), next((c for c in reversed(after) if c), ""))
        # Strip markup and leading status symbols before parsing the author: "~~Wright 2025~~" once parsed as "~~Wright"
        src = re.sub(r"~~|\*\*|`", "", src)
        while src[:1] and (unicodedata.category(src[0]) in ("So", "Sk", "Cf") or src[0] == " "):
            src = src[1:]
        clean = re.sub(r"\bpp?\.\s*[\d\-–, ]+", " ", src)
        hits = [(m.group("author").strip(), m.group("year")) for m in CITE_RE.finditer(clean)]
        if not hits or src.lstrip().startswith("*"):            # an italic title first is a task row, not a citation
            unparsed.append((rid, src[:50]))
            continue
        hint = "; ".join(re.findall(r"\*([^*]+)\*", src))      # italics = journal or book title
        for key in dict.fromkeys(hits):
            w = works.setdefault(key, {"rows": [], "hints": set(), "struck": False, "why": ""})
            w["rows"].append(rid)
            if struck:
                w["struck"], w["why"] = True, w["why"] or re.sub(r"\s+", " ", why)[:180]
            if hint:
                w["hints"].add(hint)
    return works, unparsed, n


def load_blocklist(path):
    """(surnames, exemptions {(surname, year)}). None when no file was given: the caller says so."""
    if not path:
        return None, set()
    lines = [l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    allow = {tuple(l[1:].split("_", 1)) for l in lines if l.startswith("!") and "_" in l}
    names = {l for l in lines if not l.startswith("!")}
    if not names:
        raise SystemExit("🔴 the blocklist file parses to zero names: refusing (an empty blocklist would read as 'checked')")
    return names, allow


def find_notes(notes: Path, author: str, year: str):
    hits = [f for f in notes.rglob(f"*{author}_{year}*.md") if f.name.lstrip("★").startswith(f"{author}_{year}")]
    if hits or " " not in author or "&" in author or "et al" in author:
        return hits, False
    surname = author.split()[-1]          # "J. Cohen" in the ledger, "Cohen_YYYY" on disk: retry, and flag it
    hits = [f for f in notes.rglob(f"*{surname}_{year}*.md") if f.name.lstrip("★").startswith(f"{surname}_{year}")]
    return hits, bool(hits)


def read_front(nf: Path) -> dict:
    head = nf.read_text(encoding="utf-8", errors="replace")[:2500]
    y = {}
    for k in ("title", "author", "year", "source"):
        m = re.search(rf"^{k}:\s*(.+)$", head, re.M | re.I)
        if m:
            y[k] = m.group(1).strip().strip('"').strip("'")
    d = note_doi(nf)
    if d:
        y["doi"] = d
    return y


def pick_note(found, hints):
    """Several notes: use the ledger's italic title hint against the note titles; if they cannot be told apart, say so."""
    if len(found) == 1:
        return found[0], ""
    scored = sorted(((max((len(set(h.lower().split()) & set((read_front(nf).get("title") or "").lower().split()))
                           for h in hints), default=0), nf) for nf in found), key=lambda x: -x[0])
    if scored and scored[0][0] >= 2 and (len(scored) < 2 or scored[0][0] > scored[1][0]):
        return scored[0][1], f"(several notes; chose {scored[0][1].name} by the ledger's title hint)"
    return None, "; ".join(n.name for n in found)


def csl_authors(raw):
    """Conservative: only a plain 'Given Family' is split; anything else stays literal and is flagged."""
    out, flag = [], False
    for name in re.split(r"\s*[;&]\s*|,\s(?=[A-Z][a-z]+\s[A-Z])", raw or ""):
        name = name.strip().rstrip(",")
        if not name:
            continue
        toks = name.split()
        if 2 <= len(toks) <= 3 and all(re.match(r"^[A-Z][\w.\-']*$", t) for t in toks) and "et" not in toks:
            out.append({"family": toks[-1], "given": " ".join(toks[:-1])})
        else:
            out.append({"literal": name})
            flag = True
    return (out or [{"literal": raw or "?"}]), flag


def fetch_by_doi(doi):
    req = urllib.request.Request(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}",
                                 headers={"User-Agent": "alexandria-bibliography/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))["message"]


def enrich(entry, cache):
    key = f"{entry['_author']}|{entry['issued']['date-parts'][0][0]}|{entry['title'][:60]}"
    if key in cache:
        return cache[key]
    bm = best_match(entry["title"], entry["_author"].split()[0], int(entry["issued"]["date-parts"][0][0]))
    res = {"verdict": bm.get("verdict"), "note": bm.get("note", "")}
    if bm.get("verdict") == "confident" and bm.get("doi"):
        try:
            it = fetch_by_doi(bm["doi"])
            res["fields"] = {"DOI": it.get("DOI"), "container-title": (it.get("container-title") or [None])[0],
                             "volume": it.get("volume"), "issue": it.get("issue"), "page": it.get("page"),
                             "publisher": it.get("publisher"),
                             "type": {"journal-article": "article-journal", "book": "book", "book-chapter": "chapter",
                                      "monograph": "book"}.get(it.get("type"))}
        except Exception as e:  # noqa: BLE001
            res["note"] = f"fetching the DOI record failed: {e}"
    cache[key] = res
    time.sleep(1.1)              # CrossRef public pool: be polite
    return res


def build(proj: Path, notes: Path, do_enrich=False, blocklist=None, csl=None, source_col=None, render=True):
    ledger = proj / "ledger.md"
    if not ledger.exists():
        return 3, f"❌ no {ledger}"
    works, unparsed, n_rows = parse_ledger(ledger, source_col)
    if not works:
        return 3, "❌ no parseable ledger row (a list of zero rows is not a list)"
    out_dir = proj / "_outputs"
    out_dir.mkdir(exist_ok=True)
    cache_f = out_dir / ".bib_enrich_cache.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    bl_names, bl_allow = load_blocklist(blocklist)
    entries, gaps, problems, excluded = [], [], [], []
    for (author, year), w in sorted(works.items()):
        who = f"{author} {year}"
        if w["struck"]:
            excluded.append((who, w["why"] or "struck in the ledger (no reason in the row)"))
            continue
        surname = re.split(r"\s+(?:&|and|et al\.)", author)[0].split()[-1]
        if bl_names is not None and surname in bl_names and (surname, year) not in bl_allow:
            excluded.append((who, "⛔ surname on the blocklist and not exempted: HELD until a human confirms it is the same person"))
            continue
        found, loose = find_notes(notes, author, year)
        if not found:
            why = f"no note (rows {','.join(w['rows'])})"
            if any(notes.rglob(f"*{surname}_*.md")):
                why += "; ⚠ a note by the same author with another year exists: edition year vs first publication?"
            problems.append((who, why))
            continue
        nf, msg = pick_note(found, w["hints"])
        if nf is None:
            problems.append((who, f"several notes, cannot tell them apart: {msg}"))
            continue
        y = read_front(nf)
        if not y.get("title"):
            problems.append((who, f"the note has no title ({nf.name})"))
            continue
        authors, name_flag = csl_authors(y.get("author", author))
        e = {"id": f"{author}_{year}".replace(" ", "").replace("&", "+"), "type": "book", "title": y["title"],
             "author": authors, "issued": {"date-parts": [[int(re.sub(r"\D", "", str(y.get("year", year)))[:4] or year)]]},
             "_author": author, "_rows": w["rows"], "_hints": sorted(w["hints"]), "_note": nf.name, "_flags": [], "_enrich": ""}
        if name_flag:
            e["_flags"].append("name kept literal: check the sorting position by hand")
        if loose:
            e["_flags"].append(f"ledger author '{author}' matched this note by surname only: confirm it is the same person")
        if y.get("doi"):
            e["DOI"] = y["doi"]
        if do_enrich and "DOI" not in e:
            r = enrich(e, cache)
            if r.get("fields"):
                e.update({k: v for k, v in r["fields"].items() if v and k != "type"})
                e["type"] = r["fields"].get("type") or e["type"]
                e["_enrich"] = "CrossRef confident match (DOI / container / volume / issue / pages / publisher): still needs the first-hand check"
            elif r.get("verdict") == "weak":
                e["_flags"].append(f"CrossRef weak match not used: {r.get('note', '')[:60]}")
        missing = [k for k in ("container-title", "volume", "page") if k not in e] if e["type"] == "article-journal" \
            else (["publisher / place"] if e["type"] == "book" and "publisher" not in e else [])
        if missing:
            gaps.append((e["id"], missing))
        entries.append(e)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    csl_path = out_dir / "bibliography.csl.json"
    csl_path.write_text(json.dumps([{k: v for k, v in e.items() if not k.startswith("_")} for e in entries],
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    rendered, how = "", ""
    if render and shutil.which("pandoc"):
        stub = out_dir / "_bib_stub.md"
        stub.write_text(f"---\nbibliography: {csl_path.name}\nnocite: '@*'\n---\n", encoding="utf-8")
        cmd = ["pandoc", stub.name, "--citeproc", "-t", "markdown", "--wrap=none"] + (["--csl", str(Path(csl).resolve())] if csl else [])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=str(out_dir))
        stub.unlink()
        rendered = re.sub(r":::+[^\n]*\n?", "", re.sub(r"^.*?(?=:::)", "", r.stdout, flags=re.S) if ":::" in r.stdout else r.stdout).strip()
        how = f"pandoc --citeproc ({Path(csl).name if csl else 'its default style'})" if r.returncode == 0 and rendered else f"pandoc failed: {r.stderr[:200]}"
    else:
        how = "not rendered (pandoc not found): the CSL-JSON is complete; render it with any CSL processor"
    date = time.strftime("%Y-%m-%d")
    blk = "not checked (no --blocklist given)" if bl_names is None else f"checked against {len(bl_names)} surname(s)"
    L = [f"# References (built from the ledger, {date})", "",
         f"> Chain: `ledger.md` ({n_rows} rows → {len(works)} sources) → note front matter → CSL-JSON → {how}.",
         "> This removes transcription errors; it does not replace the first-hand check before anything goes out. "
         "Missing fields are flagged, never guessed.", "", "## Rendered", "",
         rendered or "\n".join(f"- {e['id']}: {e['title']}" for e in entries), "", "## Honest buckets",
         f"- ✅ in the list: {len(entries)} / {len(works)} sources",
         f"- ⬜ fields to fill: {len(gaps)}" + ("" if not gaps else " → " + "; ".join(f"{i} (missing {', '.join(m)})" for i, m in gaps)),
         f"- ⛔ left out on purpose (withdrawn in the ledger / blocklist; reasons quoted): {len(excluded)}"
         + ("" if not excluded else " → " + "; ".join(f"{w} [{why}]" for w, why in excluded)),
         f"- ⚠ could not be built: {len(problems)}" + ("" if not problems else " → " + "; ".join(f"{w} [{why}]" for w, why in problems)),
         f"- ⚠ rows not parsed: {len(unparsed)}" + ("" if not unparsed else f" → {unparsed[:4]}"),
         f"- blocklist: {blk}"]
    flagged = [e for e in entries if e["_flags"] or e["_enrich"] or e["_hints"]]
    if flagged:
        L += ["", "## Per-entry notes"] + [f"- **{e['id']}** ({e['_note']}): " + "; ".join(
            e["_flags"] + ([e["_enrich"]] if e["_enrich"] else []) + [f"ledger hint: {h}" for h in e["_hints"]]) for e in flagged]
    out = out_dir / f"references_{date}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return 0, (f"✅ {out}: {len(entries)}/{len(works)} in the list (to fill {len(gaps)} · left out {len(excluded)} · "
               f"could not build {len(problems)} · not parsed {len(unparsed)}) · {how}")


def _self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    notes, proj = tmp / "notes" / "memory", tmp / "project"
    notes.mkdir(parents=True)
    proj.mkdir()
    (notes / "Doe_2011_Monuments and Memory.md").write_text('---\ntitle: "Monuments and Memory"\nauthor: "Jane Doe"\nyear: 2011\n'
                                                            'note: "journal · DOI 10.1234/abc.1"\n---\n', encoding="utf-8")
    (notes / "★Roe_1998_Commemoration and Its Discontents.md").write_text('---\ntitle: "Commemoration and Its Discontents"\n'
                                                                            'author: "Richard Roe"\nyear: 1998\n---\n', encoding="utf-8")
    (notes / "Poe_2005_Assembly.md").write_text('---\nauthor: "Edgar Poe"\nyear: 2005\n---\n', encoding="utf-8")
    (notes / "Ives_2010_Earlier.md").write_text('---\ntitle: "Earlier"\nauthor: "Ann Ives"\n---\n', encoding="utf-8")
    (proj / "ledger.md").write_text(
        "| ID | section | claim | source | status |\n|---|---|---|---|---|\n"
        "| L-1 | 1 | a | Doe (2011) p. 47 | ok |\n| L-2 | 1 | b | Roe (1998) p. 12 | ok |\n"
        "| L-3 | 2 | c | Poe (2005) p. 208 | ok |\n| L-4 | 2 | d | ~~Moe (2001) p. 5~~ | withdrawn: the page says the opposite |\n"
        "| L-5 | 3 | e | Ives (2014) pp. 3, 9 | ok |\n| L-6 | 3 | f | Wright (2025) p. 1 | ok |\n"
        "| L-7 | 3 | a claim about a retracted study | Doe (2011) p. 48 | ok |\n", encoding="utf-8")
    bl = tmp / "blocklist.txt"
    bl.write_text("# surnames held for a human\nWright\n", encoding="utf-8")
    code, msg = build(proj, tmp / "notes", blocklist=str(bl), render=False)
    rep = next((proj / "_outputs").glob("references_*.md")).read_text(encoding="utf-8")
    csl = json.loads((proj / "_outputs" / "bibliography.csl.json").read_text(encoding="utf-8"))
    checks = [
        ("2 of 6 in the list (Doe, Roe)", code == 0 and "2/6 in the list" in msg and {e["id"] for e in csl} == {"Doe_2011", "Roe_1998"}),
        ("DOI carried from the note: field", next(e for e in csl if e["id"] == "Doe_2011").get("DOI") == "10.1234/abc.1"),
        ("starred note found", any(e["id"] == "Roe_1998" for e in csl)),
        ("'Given Family' split into CSL names", next(e for e in csl if e["id"] == "Doe_2011")["author"] == [{"family": "Doe", "given": "Jane"}]),
        ("withdrawn row left out with the ledger's own words", "Moe 2001 [withdrawn: the page says the opposite]" in rep),
        ("'retracted' in a claim cell does not withdraw the row", "Doe 2011 [" not in rep),
        ("blocklist hit is held, not decided", "Wright 2025 [⛔ surname on the blocklist" in rep and "HELD" in rep),
        ("note without a title is a problem, not an entry", "Poe 2005 [the note has no title" in rep),
        ("same author, other year: flagged", "Ives 2014 [no note" in rep and "another year exists" in rep),
        ("book without publisher: field to fill", "Roe_1998 (missing publisher / place)" in rep),
        ("not rendered is said, not hidden", "not rendered" in rep),
    ]
    code2, msg2 = build(proj, tmp / "notes", render=False)
    rep2 = sorted((proj / "_outputs").glob("references_*.md"))[-1].read_text(encoding="utf-8")
    checks.append(("no --blocklist: says 'not checked'", "blocklist: not checked" in rep2))
    shutil.rmtree(tmp, ignore_errors=True)
    bad = 0
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    print(f"{len(checks) - bad} of {len(checks)} as expected")
    return 1 if bad else 0


def main() -> int:
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()

    def opt(k, d=None):
        return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d
    if not opt("--project"):
        print(__doc__)
        return 3
    col = opt("--source-col")
    code, msg = build(Path(opt("--project")), Path(opt("--notes", "notes")), "--enrich" in a, opt("--blocklist"),
                      opt("--csl"), int(col) if col else None)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
