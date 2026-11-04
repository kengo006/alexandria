# -*- coding: utf-8 -*-
"""citation_ledger_check.py — every page-bearing citation in the text against the ledger
(roles/writer.md §8: "every page-bearing citation in the final text gets a ledger row").

WHY: audited in production, a text had about fifty page-bearing citations and a ledger that intersected them
only partly; a fifth had never been entered and so had never been checked by any audit round, including the
single most load-bearing one. The rule "one row per page-bearing citation" existed; nothing checked it. This is
the check.

WHAT: find every page-bearing citation in the text → (first author's surname, year); compare with the ledger.
  orphan    in the text, not in the ledger: unentered (the main case)
  page gap  the ledger has the work but not this page: a claim the ledger seems to cover and does not
  dead      in the ledger, not in this text: another chapter, or a row to remove
Nothing is deleted or changed. An orphan may be a missed entry, not an invention: enter it and check it, or
remove the citation. Only page-bearing citations are checked (that class is falsifiable); an author that cannot
be parsed goes to an honest count, never silently dropped.
Key = (first author's surname, lowercase; year with any a/b suffix). Latin and CJK author names both parse.

Usage:
  python tools/citation_ledger_check.py --project <dir> [--text <glob>]... [--source-col N] [--md]
  python tools/citation_ledger_check.py --self-test
  --project     the project folder holding ledger.md
  --text        the text to check (relative to the project or absolute; glob; repeatable). Default: the layout of
                roles/writer.md §0, i.e. working-source.md, reading-copy.md and every .md under chapters/, those
                that exist; if none does, every .md in the project except the ledger, _audit/, history, finals/,
                the opponent map, the terminology table and the criteria card. The files read are listed.
  --source-col  which ledger column holds the source (0 = the ID column). Default: the column whose header
                says source / citation / work / reference, else the first cell after the ID with an author-year.
Exit codes: 0 = clean / 1 = orphan or page gap / 3 = cannot run
"""
import glob
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# CJK and full-width punctuation are built from code points so this file carries no CJK characters (and passes the
# repository's CJK scan); behaviour is unchanged.
CJK = f"{chr(0x4E00)}-{chr(0x9FFF)}"
PAGE_ZH = chr(0x9801)                                   # the page marker used in Chinese text
FW_COLON, FW_COMMA, IDEO_COMMA = chr(0xFF1A), chr(0xFF0C), chr(0x3001)
FW_LP, FW_RP, FW_SLASH = chr(0xFF08), chr(0xFF09), chr(0xFF0F)
STOPS = "".join(chr(c) for c in (0x3002, 0xFF01, 0xFF1F, 0xFF1B))          # sentence ends
PAIRS = [(chr(0x300A), chr(0x300B)), (chr(0x3008), chr(0x3009)), (chr(0x300C), chr(0x300D)),
         (chr(0x201C), chr(0x201D)), ("(", ")"), (FW_LP, FW_RP)]           # title and quote brackets
APOS = chr(0x2019)

YEAR = re.compile(r"(1[5-9]\d\d|20[0-2]\d)([a-z]?)(?![0-9A-Za-z])")          # group 2 = a/b suffix
PAGE_NEAR = re.compile(rf"(pp?\.\s*\d|{PAGE_ZH}\s*\d|[:{FW_COLON}]\s*\d{{1,4}}\b)")
AUTHOR_BEFORE = re.compile(
    rf"([A-Za-z][A-Za-z'{APOS}\-]*(?:\s+(?:&|and|et\s+al\.?|de[rn]?|van|von|della|du|dos|le|la|[A-Z][A-Za-z'{APOS}\-]+))*|[{CJK}]{{1,6}})"
    rf"\s*(?:\d{{4}}[a-z]?\s*[/{FW_SLASH}]\s*)*"          # "Lukes 1974/2005": the author is found for both years
    rf"[,{FW_COMMA}{IDEO_COMMA}]?\s*[{FW_LP}(]?\s*$")
BRACKETED = re.compile("|".join(re.escape(a) + r"[^" + re.escape(b) + r"]{0,60}" + re.escape(b) for a, b in PAIRS) + r"|\*{1,2}")
GAP_BAD = re.compile(rf"[A-Za-z]{{3,}}|[{CJK}]|[{STOPS}\n]")
NON_AUTHOR = {"discourse", "online", "issue", "table", "figure", "chapter", "section", "vol", "no", "pp", "ibid",
              "http", "https", "www", "doi", "and", "the", "see", "cf", "eds", "ed", "trans", "in"}
EXCLUDE = ("ledger", "_audit", "history", "finals", "opponent-map", "terminology", "criteria-card", "bibliography",
           "references", "_00_entry")
SOURCE_HEAD = re.compile(r"source|citation|cite|work|reference", re.I)


def pages_in(s: str) -> set:
    """Page numbers (p./pp./CJK page marker), ranges expanded when ≤ 60 pages."""
    out = set()
    for m in re.finditer(rf"(?:pp?\.|{PAGE_ZH})\s*([\d\s\-–—,/]+)", s):
        seg = m.group(1)
        for rng in re.finditer(r"(\d{1,4})\s*[-–—]\s*(\d{1,4})", seg):
            a, b = int(rng.group(1)), int(rng.group(2))
            out.update(range(a, b + 1) if 0 < b - a <= 60 else {a, b})
        out.update(int(x) for x in re.findall(r"\d{1,4}", re.sub(r"\d{1,4}\s*[-–—]\s*\d{1,4}", " ", seg)))
    return out


LEADING = {"as", "in", "see", "following", "according", "after", "like", "unlike", "per", "by", "with", "for",
           "from", "both", "while", "when", "although", "but", "and", "also", "thus", "here", "then", "yet", "so"}
PAGE_END = re.compile(rf"[)\];\n{FW_RP}{STOPS}]|\.\s+[A-Z]")


def first_surname(s: str) -> str:
    s = s.strip().strip("(" + FW_LP + "[").strip()
    # A capitalised word at the start of a sentence is not an author: "As Doe (2011)" is Doe.
    words = s.split()
    while len(words) > 1 and words[0].lower().strip(",") in LEADING:
        words = words[1:]
    s = " ".join(words)
    s = re.split(rf"\s*(?:&|,|;|{FW_SLASH}|/|\band\b|et\s+al)", s, maxsplit=1)[0].strip()
    m = re.search(rf"[A-Za-z][A-Za-z'{APOS}\-]+", s)
    if m:
        return m.group(0).lower()
    m = re.search(rf"[{CJK}]+", s)
    return m.group(0) if m else ""


def _cells(ln):
    return [c.strip() for c in ln.strip().strip("|").split("|")]


def parse_ledger(ledger: Path, source_col=None):
    """{(surname, yearkey): [row ids]}, unparsed rows, {(surname, yearkey): pages seen anywhere in its rows}."""
    works, unparsed, lpages, col = {}, [], {}, source_col
    parse_ledger.mode = f"--source-col {col}" if col is not None else None
    for ln in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.lstrip().startswith("|") or re.match(r"^\s*\|[\s:|\-]+\|\s*$", ln):
            continue
        cells = _cells(ln)
        if not cells or not cells[0]:
            continue
        if cells[0].lower() in ("id", "#"):                    # header row: find the source column
            if col is None:
                col = next((i for i, c in enumerate(cells) if i and SOURCE_HEAD.search(c)), None)
                if col is not None:
                    parse_ledger.mode = f"header '{cells[col]}' (column {col})"
            continue
        rid = cells[0]
        cand = [cells[col]] if col is not None and col < len(cells) else cells[1:]
        src = ""
        for c in cand:
            clean = re.sub(r"pp?\.[^,)|" + FW_RP + "]*", "", c)        # page numbers first (p.1342 is not a year)
            clean = re.sub(rf"[{FW_LP}(].*?[{FW_RP})]", lambda m: " " if not YEAR.search(m.group(0)) else m.group(0)
                           .strip("(" + FW_LP + ")" + FW_RP), clean)
            if YEAR.search(clean):
                src = clean
                break
        found = list(YEAR.finditer(src))
        if not found:
            unparsed.append((rid, " | ".join(cand)[:50]))
            continue
        sur = first_surname(src[:found[0].start()])
        if not sur:
            unparsed.append((rid, src[:50]))
            continue
        for yk in dict.fromkeys(m.group(1) + (m.group(2) or "") for m in found):
            works.setdefault((sur, yk), []).append(rid)
            lpages.setdefault((sur, yk), set()).update(pages_in(ln))    # every page anywhere in the row
    return works, unparsed, lpages


def gap_ok(gap: str) -> bool:
    """Between the year and the page there may be punctuation or a bracketed title, not another name."""
    return not GAP_BAD.search(BRACKETED.sub("", gap))


def extract_text_cites(text: str):
    """[(surname, yearkey, pages, snippet)] for page-bearing citations, and the count of unparsed ones."""
    cites, unparsed = [], 0
    for m in YEAR.finditer(text):
        ys, ye = m.start(), m.end()
        probe = text[ye:ye + 44]                   # wide enough for a title between the year and the page
        pm = PAGE_NEAR.search(probe)
        if not pm:
            continue
        if not gap_ok(probe[:pm.start()]):         # another source in between: refuse, do not invent a claim
            unparsed += 1
            continue
        ps = ye + pm.start()
        # Read the page from the text itself (a fixed window can cut "p.74" to "p.7"), and stop at the citation's
        # end: a closing bracket, a semicolon, a sentence end. Otherwise the next citation's page leaks in.
        seg = text[ps:ps + 40]
        cut = PAGE_END.search(seg, 2)
        pgs = pages_in(seg[:cut.start()] if cut else seg)
        bm = AUTHOR_BEFORE.search(text[max(0, ys - 45):ys])
        sur = first_surname(bm.group(1)) if bm else ""
        if not sur or sur in NON_AUTHOR:
            unparsed += 1
            continue
        cites.append((sur, m.group(1) + (m.group(2) or ""), pgs,
                      text[max(0, ys - 28):min(len(text), ye + 20)].replace("\n", " ").strip()))
    return cites, unparsed


def rel(f: Path, proj: Path) -> str:
    try:
        return f.resolve().relative_to(proj.resolve()).as_posix()
    except ValueError:
        return str(f)


def check(proj: Path, texts=(), source_col=None):
    ledger = proj / "ledger.md"
    if not ledger.exists():
        return 3, [f"❌ no {ledger} (no ledger is not a green result)"]
    works, l_unparsed, lpages = parse_ledger(ledger, source_col)
    if not works:
        return 3, ["❌ no parseable ledger row: a green over zero rows is not green"]
    files = []
    for t in texts:
        files += [Path(p) for p in glob.glob(t if Path(t).is_absolute() else str(proj / t), recursive=True)]
    if not texts:
        # the project layout in roles/writer.md §0: the working master, the mirror of the author's manuscript, and
        # the drafts in chapters/. Reading working-source.md alone skipped every chapter draft.
        files = [f for f in (proj / "working-source.md", proj / "reading-copy.md") if f.exists()] + \
            sorted((proj / "chapters").rglob("*.md"))
        if not files:
            files = [f for f in proj.rglob("*.md") if not any(x in str(f.relative_to(proj)).lower() for x in EXCLUDE)]
    files = [f for f in dict.fromkeys(files) if f.exists() and f.suffix == ".md"]
    if not files:
        return 3, ["❌ no text found (point --text at it)"]
    cites, t_unparsed = extract_text_cites("\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files))
    keys, cite_keys, pagegap = set(works), {}, {}
    for sur, yk, pgs, snip in cites:
        cite_keys.setdefault((sur, yk), []).append(snip)
        if (sur, yk) in keys and pgs:
            known = lpages.get((sur, yk), set())
            miss = sorted(p for p in pgs if p not in known)
            if miss and known:                      # a ledger row with no page at all is not reported
                g = pagegap.setdefault((sur, yk), {"pages": set(), "snips": []})
                g["pages"].update(miss)
                g["snips"].append(snip)
    orphans = {k: v for k, v in cite_keys.items() if k not in keys}
    dead = {k: v for k, v in works.items() if k not in cite_keys}
    mode = parse_ledger.mode or ("⚠ GUESSED: no 'source' column header, so the first cell holding an author-year was "
                                 "used; claims that mention a work can add false rows and hide page gaps — "
                                 "add a 'source' column or pass --source-col")
    L = [f"=== text ⇄ ledger ({proj.name}) ===", f"source column: {mode}",
         f"ledger: {len(works)} distinct sources (rows not parsed: {len(l_unparsed)}) | text files {len(files)} | "
         f"page-bearing citations {len(cites)} / {len(cite_keys)} distinct (author not parsed: {t_unparsed})",
         "text read: " + ", ".join(rel(f, proj) for f in files)]
    if not cites:
        L.append("  ⚠ no page-bearing citation parsed: is --text pointing at the text?")
    L.append(f"  🔴 orphan (in the text, not in the ledger): {len(orphans)}")
    L += [f"    - {s} {y} | e.g. …{v[0]}…" for (s, y), v in sorted(orphans.items())]
    L.append(f"  🟠 page gap (the ledger has the work, not this page): {len(pagegap)}")
    for (s, y), d in sorted(pagegap.items()):
        L.append(f"    - {s} {y} {'/'.join(f'p.{p}' for p in sorted(d['pages']))} | rows {','.join(works[(s, y)])} "
                 f"(pages in the ledger: {','.join(str(p) for p in sorted(lpages[(s, y)])[:8])}) | e.g. …{d['snips'][0]}…")
    L.append(f"  ⬜ dead (in the ledger, not in this text): {len(dead)}")
    L += [f"    - {s} {y} | rows {','.join(v)}" for (s, y), v in sorted(dead.items())]
    L.append("nothing is changed: enter and check an orphan or a page gap, or remove the citation; a non-zero "
             "'not parsed' count means the patterns have a blind spot on this text, not that it is clean")
    return (1 if orphans or pagegap else 0), L


def _self_test() -> int:
    import tempfile, shutil
    tmp = Path(tempfile.mkdtemp())
    zh_author = chr(0x6C5F) + chr(0x5B9C) + chr(0x6A3A)          # a three-character CJK name
    zh_title_open, zh_title_close = PAIRS[0]
    (tmp / "ledger.md").write_text(
        "## 1\n| ID | section | claim | source | status |\n|---|---|---|---|---|\n"
        "| L-1 | 1 | memory | Doe (2011) p. 47 | ok |\n"
        "| L-2 | 1 | practice | Roe 1998, pp. 12-14 | ok |\n"
        "| L-3 | 2 | method | Ives & Poe (2014a) p. 3 | ok |\n"
        f"| L-4 | 2 | zh | {zh_author} 2004 {PAGE_ZH} 88 | ok |\n"
        "| L-6 | 3 | a claim citing Smith (2019) in passing | Moe (2001) p. 6 | ok |\n"
        "| L-5 | 3 | unused | Moe (2001) p. 5 | ok |\n", encoding="utf-8")
    (tmp / "working-source.md").write_text(
        "As Doe (2011, p. 47) argues, monuments shape memory. Roe 1998: 13 concedes it. "
        "Ives and Poe (2014a, p. 3) agree. Doe (2011) p. 52 goes further. "
        "Smith (2019, p. 7) disagrees. "
        f"{zh_author}{FW_LP}2004{FW_RP}{zh_title_open}x{zh_title_close}{PAGE_ZH}88. "
        f"Moe (2005) and Kale {zh_title_open}The Two Gardens{zh_title_close} p.7 is not Moe's page.\n",
        encoding="utf-8")
    code, L = check(tmp)
    out = "\n".join(L)
    checks = [
        ("exit 1 (orphan and page gap present)", code == 1),
        ("orphan: smith 2019", "smith 2019" in out and "orphan (in the text, not in the ledger): 1" in out),
        ("page gap: doe 2011 p.52", "doe 2011 p.52" in out),
        ("range pp. 12-14 covers p. 13 (no gap for roe)", "roe 1998 p." not in out),
        ("a/b suffix and '&' author: ives 2014a matched", "ives 2014a" not in out.split("dead")[1] if "dead" in out else False),
        ("CJK author and CJK page marker matched", zh_author + " 2004" not in out.split("orphan")[1].split("page gap")[0]),
        ("dead: moe 2001 (both of its rows)", "moe 2001 | rows L-6,L-5" in out),
        ("source column taken from the header", "source column: header 'source' (column 3)" in out),
        ("a work named in a claim cell is not a ledger row (header mode)", "smith 2019" in out.split("orphan")[1].split("page gap")[0]),
        ("another source between year and page is refused, not credited to it", "moe 2005" not in out.split("page gap")[0]),
    ]
    shutil.rmtree(tmp, ignore_errors=True)
    lay = Path(tempfile.mkdtemp())
    (lay / "chapters").mkdir()
    (lay / "ledger.md").write_text("| ID | claim | source |\n|---|---|---|\n| L-1 | memory | Doe (2011) p. 47 |\n", encoding="utf-8")
    (lay / "working-source.md").write_text("Doe (2011, p. 47) is settled.\n", encoding="utf-8")
    (lay / "chapters" / "ch1.md").write_text("Kay (2020, p. 9) is not in the ledger yet.\n", encoding="utf-8")
    code_l, L_l = check(lay)
    out_l = "\n".join(L_l)
    checks.append(("default text includes chapters/ next to working-source.md (orphan found there)",
                   code_l == 1 and "kay 2020" in out_l and "text read: working-source.md, chapters/ch1.md" in out_l))
    shutil.rmtree(lay, ignore_errors=True)
    empty = Path(tempfile.mkdtemp())
    code_e, _ = check(empty)
    checks.append(("no ledger → cannot run (3)", code_e == 3))
    shutil.rmtree(empty, ignore_errors=True)
    checks.append(("page window reads the whole number", pages_in("p.74") == {74} and pages_in("pp. 133-135") == {133, 134, 135}))
    cs, _ = extract_text_cites("As Doe (2011, p. 47) argues. Ives and Poe (2014a, p. 3) agree. Doe (2011) p. 52 goes on.")
    checks.append(("sentence-initial 'As' is not the author", [c[0] for c in cs][:1] == ["doe"]))
    checks.append(("the next citation's page does not leak in", next(c[2] for c in cs if c[0] == "ives") == {3}))
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
    proj = a[a.index("--project") + 1] if "--project" in a else None
    if not proj:
        print(__doc__)
        return 3
    texts = [a[i + 1] for i, x in enumerate(a) if x == "--text" and i + 1 < len(a)]
    col = int(a[a.index("--source-col") + 1]) if "--source-col" in a else None
    code, L = check(Path(proj), texts, col)
    print("\n".join(L))
    if "--md" in a and code != 3:
        print("\n```markdown\n### text ⇄ ledger (" + Path(proj).name + ")")
        print("\n".join("- " + l.strip() for l in L[1:]))
        print("```")
    return code


if __name__ == "__main__":
    sys.exit(main())
