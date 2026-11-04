# -*- coding: utf-8 -*-
"""retraction_check.py — screen cited sources against the Retraction Watch data
(roles/writer.md Phase 3 filing gate and Layer 1; roles/librarian.md, "Registry check and retraction screening").

Matches DOIs filed in your notes against the Retraction Watch database (the open copy Crossref hosts on
GitLab, updated every working day, free since 2023-09).

⚠ This is a thin net. It can only see sources that carry a DOI, and in the humanities most monographs do
not. So a clean result is not a certificate that nothing you cite was retracted; it says the checkable part
was checked. Every report states its denominator — "0 hits across N checkable / M not checkable" — because
a zero without one reads as "all clear". The cure for coverage is filing DOIs at ingestion
(tools/crossref_lookup.py).

Two modes:
  library  python tools/retraction_check.py [--notes notes] [--refresh]
           every note under --notes (default ./notes)
  project  python tools/retraction_check.py --project <project folder> [--notes notes] [--md]
           only the sources the draft actually cites: reads <project>/ledger.md, takes every
           Author (Year) in its table rows, finds the note, takes its DOI. Four honest buckets:
           checkable / no DOI / no note found / row not parsed.
  --md     also print a markdown block to paste into the audit file
  --cache  where the downloaded data lives (default ./.cache); refreshed after 7 days or with --refresh
  --self-test  offline, synthetic notes, ledger and data

The DOI is read from the note's front matter: a `doi:` key if there is one, otherwise the first DOI-shaped
string (10.xxxx/...) in the front matter (the note schema's `note:` field carries it in prose).
Exit codes: 0 = no hit / 1 = at least one hit / 3 = cannot run (no data, no ledger, nothing to check)
"""
import csv
import io
import re
import sys
import time
import urllib.request
from pathlib import Path

RW_URL = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
MAX_AGE_DAYS = 7
MIN_ROWS = 10_000   # the database has tens of thousands of rows; fewer means a bad download, not a good world
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>|]+", re.I)
# Author (Year) in a ledger row: "Doe (2011)", "Doe 2011", "Doe & Roe (2011)", "Doe et al. (2011a)".
CITE_RE = re.compile(r"(?P<author>[A-Z][A-Za-z'’\-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z'’\-]+|\s+et al\.)?)"
                     r"\s*,?\s*\(?(?P<year>1[5-9]\d\d|20\d\d)[a-z]?\)?")


class CannotRun(Exception):
    pass


def norm_doi(s: str) -> str:
    s = s.strip().strip('"').strip("'").lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    return s.rstrip(".,;")


def load_rw(cache: Path, refresh: bool, url: str = RW_URL, min_rows: int = MIN_ROWS):
    """Return ({doi: row}, data date). Fails loudly: never an empty set reported as clean."""
    cache.mkdir(parents=True, exist_ok=True)
    csv_path = cache / "retraction_watch.csv"
    fresh = csv_path.exists() and (time.time() - csv_path.stat().st_mtime) < MAX_AGE_DAYS * 86400
    if refresh or not fresh:
        print(f"downloading Retraction Watch data … {url}")
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            if len(data) < 1_000_000 and min_rows >= MIN_ROWS:
                raise ValueError(f"download suspiciously small ({len(data)} bytes)")
            csv_path.write_bytes(data)
        except Exception as e:  # noqa: BLE001
            if not csv_path.exists():
                raise CannotRun(f"download failed and no cached copy: {e} (no data is not a green result)")
            age = (time.time() - csv_path.stat().st_mtime) / 86400
            print(f"⚠ download failed ({e}); using the cached copy from {age:.0f} days ago — say so in the result")
    reader = csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8", errors="replace")))
    col = next((c for c in (reader.fieldnames or []) if c and c.lower() == "originalpaperdoi"), None)
    if not col:
        raise CannotRun(f"no OriginalPaperDOI column (columns: {(reader.fieldnames or [])[:8]}): the format changed")
    rw = {}
    for row in reader:
        d = norm_doi(row.get(col, "") or "")
        if d and d not in ("unavailable", "0"):
            rw[d] = row
    if len(rw) < min_rows:
        raise CannotRun(f"only {len(rw)} rows with a DOI: the data looks wrong")
    return rw, time.strftime("%Y-%m-%d", time.localtime(csv_path.stat().st_mtime))


def note_doi(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---", text.replace("\r\n", "\n"), re.S)
    front = m.group(1) if m else text[:2000]
    k = re.search(r"^doi:\s*(\S.*)$", front, re.M | re.I)
    if k and k.group(1).strip().strip('"\'') and DOI_RE.search(k.group(1)):
        return norm_doi(DOI_RE.search(k.group(1)).group(0))
    d = DOI_RE.search(front)
    return norm_doi(d.group(0)) if d else None


def notes_for(notes: Path, author: str, year: str):
    # filenames are {Author}_{Year}_{Title}.md; a starred note carries ★ in front (shared/naming-conventions.md)
    return [f for f in notes.rglob(f"*{author}_{year}*.md") if f.name.lstrip("★").startswith(f"{author}_{year}")]


def hit_line(row):
    return f"{row.get('RetractionNature', '?')} | {row.get('RetractionDate', '?')} | {(row.get('Reason', '?') or '?')[:110]}"


def literature_notes(notes: Path):
    """The notes in the denominator, and how many files were set aside: the vault map at the root and each folder's
    MOC (named after its folder, as governance/scripts/vault_verify.py counts them), and anything under a folder
    starting with _ or '.'. A map or a MOC has no DOI by design; counted as 'not checkable' it inflated the share
    the screen could not see."""
    keep, nav, hidden = [], 0, 0
    for p in sorted(notes.rglob("*.md")):
        rel = p.relative_to(notes)
        if any(x.startswith(("_", ".")) for x in rel.parts):
            hidden += 1
        elif rel.as_posix() == "vault-map.md" or p.stem == p.parent.name:
            nav += 1
        else:
            keep.append(p)
    return keep, nav, hidden


def library_mode(notes: Path, rw, rw_date):
    have, none, hits = [], 0, []
    files, nav, hidden = literature_notes(notes)
    for f in files:
        d = note_doi(f)
        if not d:
            none += 1
            continue
        have.append(f)
        if d in rw:
            hits.append(f"  - {f.relative_to(notes)}\n    DOI {d} | {hit_line(rw[d])}")
    print("=== retraction screen (library) ===")
    print(f"Retraction Watch: {len(rw):,} DOIs (data of {rw_date})")
    print(f"notes: {len(have)} checkable (with a DOI) / {none} NOT checkable (no DOI; not a clean bill)"
          f"  (set aside: vault map and MOCs {nav}, under _ or . folders {hidden})")
    if not have:
        raise CannotRun("zero checkable notes: the screen has nothing to run on (file DOIs at ingestion first)")
    if hits:
        print(f"🔴 {len(hits)} hit(s):\n" + "\n".join(hits))
        return 1
    print(f"✅ 0 hits (across {len(have)} checkable / {none} not checkable, data of {rw_date})")
    return 0


def parse_ledger(ledger: Path):
    """(works {(author, year): [row ids]}, rows parsed, rows not parsed)."""
    works, unparsed, n = {}, [], 0
    for ln in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.lstrip().startswith("|") or re.match(r"^\s*\|[\s:|\-]+\|\s*$", ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() in ("id", "#"):
            continue
        n += 1
        rid = cells[0]
        body = " | ".join(cells[1:])
        body = re.sub(r"\bpp?\.\s*[\d\-–, ]+", " ", body)   # page numbers first: "p. 1999" is not a year
        found = [(m.group("author").strip(), m.group("year")) for m in CITE_RE.finditer(body)]
        if not found:
            unparsed.append((rid, body[:40]))
            continue
        for key in dict.fromkeys(found):
            works.setdefault(key, []).append(rid)
    return works, n, unparsed


def project_mode(proj: Path, notes: Path, rw, rw_date, md: bool):
    ledger = proj / "ledger.md"
    if not ledger.exists():
        raise CannotRun(f"no {ledger} (no ledger is not a green result)")
    works, n, unparsed = parse_ledger(ledger)
    if not n:
        raise CannotRun("the ledger has no rows: a green over zero rows is not green")
    checkable, nodoi, unmapped, hits = {}, [], [], []
    for (author, year), rids in sorted(works.items()):
        found = notes_for(notes, author, year)
        if not found:
            unmapped.append(f"{author} {year}")
            continue
        doi = next((d for d in (note_doi(f) for f in found) if d), None)
        if not doi:
            nodoi.append(f"{author} {year}")
            continue
        checkable[(author, year)] = rids
        if doi in rw:
            hits.append(f"  - {author} {year} | DOI {doi} | {hit_line(rw[doi])} | rows: {', '.join(rids)}")
    lines = [f"=== retraction screen ({proj.name}) ===",
             f"ledger: {n} rows → {len(works)} distinct sources (rows not parsed: {len(unparsed)})",
             f"  ✅ checkable (DOI): {len(checkable)} sources",
             f"  ⬜ not checkable (no DOI, mostly monographs): {len(nodoi)} — not a clean bill",
             f"  ⚠ no note found: {len(unmapped)}" + (f" → {unmapped[:6]}" if unmapped else "")]
    if unparsed:
        lines.append(f"  ⚠ rows not parsed: {unparsed[:4]}")
    lines.append(f"Retraction Watch: {len(rw):,} DOIs (data of {rw_date})")
    if hits:
        lines.append(f"🔴 {len(hits)} hit(s):")
        lines += hits
    else:
        lines.append(f"✅ 0 hits (across {len(checkable)} checkable / {len(nodoi) + len(unmapped)} not checkable, "
                     f"data of {rw_date})")
    print("\n".join(lines))
    if md:
        print("\n```markdown\n### Retraction screen (" + time.strftime("%Y-%m-%d") + ")")
        for l in lines[1:]:
            print("- " + l.strip())
        print("```")
    return 1 if hits else 0


def _self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    notes, proj, cache = tmp / "notes", tmp / "project", tmp / "cache"
    for p in (notes / "memory", proj, cache):
        p.mkdir(parents=True)
    (notes / "memory" / "Doe_2011_Monuments and Memory.md").write_text(
        '---\ntitle: "Monuments and Memory"\ndoi: "https://doi.org/10.1234/ABC.1"\n---\n', encoding="utf-8")
    (notes / "memory" / "★Roe_1998_Commemoration.md").write_text(
        '---\ntitle: "Commemoration"\nnote: "journal · DOI 10.5555/rw.77 · reprint"\n---\n', encoding="utf-8")
    (notes / "memory" / "Ives_2014_Practice.md").write_text('---\ntitle: "Practice"\nnote: "monograph"\n---\n', encoding="utf-8")
    (notes / "vault-map.md").write_text("## Taxonomy\n- `memory/` - works on memory\n", encoding="utf-8")
    (notes / "memory" / "memory.md").write_text("# memory\n- [[Doe_2011_Monuments and Memory]]\n", encoding="utf-8")
    (cache / "retraction_watch.csv").write_text(
        "Record ID,OriginalPaperDOI,RetractionNature,RetractionDate,Reason\n"
        "1,10.5555/RW.77,Retraction,2020-01-01,+Data fabrication\n2,unavailable,Retraction,2020,x\n3,10.9/other,Correction,2021,y\n",
        encoding="utf-8")
    (proj / "ledger.md").write_text(
        "## §1\n| ID | section | claim | passage + page | status |\n|---|---|---|---|---|\n"
        "| L-1 | 1 | memory | Doe (2011) p. 47 \"…\" | ✅ |\n"
        "| L-2 | 2 | practice | Roe (1998) p. 1999 | ✅ |\n"
        "| L-3 | 2 | settled | Ives (2014) pp. 3, 9 | ✅ |\n"
        "| L-4 | 3 | missing | Poe (2005) p. 208 | ✅ |\n"
        "| L-5 | 3 | no source here | — | ✅ |\n", encoding="utf-8")
    bad = 0
    rw, date = load_rw(cache, refresh=False, min_rows=1)
    checks = []
    checks.append(("DOI from a doi: key (URL form, upper case)", note_doi(notes / "memory" / "Doe_2011_Monuments and Memory.md") == "10.1234/abc.1"))
    checks.append(("DOI from the note: field, starred note", note_doi(notes / "memory" / "★Roe_1998_Commemoration.md") == "10.5555/rw.77"))
    checks.append(("no DOI → None", note_doi(notes / "memory" / "Ives_2014_Practice.md") is None))
    checks.append(("'unavailable' rows are dropped", "unavailable" not in rw and len(rw) == 2))
    works, n, unparsed = parse_ledger(proj / "ledger.md")
    checks.append(("ledger: 5 rows, 4 sources, 1 unparsed", (n, len(works), len(unparsed)) == (5, 4, 1)))
    checks.append(("p. 1999 is a page, not a year", ("Roe", "1998") in works and not any(y == "1999" for _, y in works)))
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        code_lib = library_mode(notes, rw, date)
        code_proj = project_mode(proj, notes, rw, date, md=False)
    out = buf.getvalue()
    checks.append(("library mode: 1 hit, exit 1, denominator stated", code_lib == 1 and "2 checkable" in out and "1 NOT checkable" in out))
    checks.append(("library mode: vault map and MOC set aside and counted, not 'NOT checkable'", "vault map and MOCs 2" in out))
    checks.append(("project mode: hit on Roe, 2 checkable / 1 no DOI / 1 no note", code_proj == 1 and "Roe 1998 | DOI 10.5555/rw.77" in out
                   and "checkable (DOI): 2" in out and "no DOI, mostly monographs): 1" in out and "no note found: 1" in out))
    try:
        load_rw(tmp / "empty-cache", refresh=False, url="http://127.0.0.1:9/nothing", min_rows=1)
        checks.append(("no data and no cache → cannot run", False))
    except CannotRun:
        checks.append(("no data and no cache → cannot run", True))
    try:
        load_rw(cache, refresh=False, min_rows=10)
        checks.append(("too few rows → cannot run", False))
    except CannotRun:
        checks.append(("too few rows → cannot run", True))
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    print(f"{len(checks) - bad} of {len(checks)} as expected")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


def main() -> int:
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default
    notes = Path(opt("--notes", "notes"))
    try:
        if not notes.is_dir():
            raise CannotRun(f"notes folder {notes} not found (pass --notes)")
        rw, date = load_rw(Path(opt("--cache", ".cache")), refresh="--refresh" in a)
        proj = opt("--project")
        if proj:
            return project_mode(Path(proj), notes, rw, date, md="--md" in a)
        return library_mode(notes, rw, date)
    except CannotRun as e:
        print(f"❌ {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
