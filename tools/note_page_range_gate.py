# -*- coding: utf-8 -*-
r"""note_page_range_gate.py — do the page numbers a note cites fall inside the PDF that is actually filed?
(roles/writer.md §5 page precision; roles/librarian.md, replacing a source with another version)

## The case
A source was replaced by a different version: the author's 36-page draft by the publisher's 21-page version. The
text layer was re-extracted; the note's page references stayed with the 36-page draft ("Bibliography pp. 34-36",
a quote at "pp. 33-34"). The file on disk has no page 22. No check looked at this: zero dead links, the index fine,
every health check green, and the note pointed at pages that do not exist, for six days.

## The criterion: the lowest cited page tells which numbering the note uses
| lowest cited | the note uses | verdict |
|---|---|---|
| ≤ 3 (counts from 1) | the PDF's own pages | highest cited > page count, and a large share beyond ⇒ 🔶 out of range |
| above the page count | the printed folios of a journal (offset > 0) | plausible ⇒ ✅ |
| otherwise | cannot tell | ❔ not decided |
🔑 The signature of a shrunken replacement is the first row: references counted from p. 1 running past the end.
A first version looked the offset up in the offset registry by "author and year appear in the row", and rows
full of other people's citations matched at random (it printed an offset of +543 for a 31-page PDF). The page
numbers alone are a steadier criterion.
⚠ Every p./pp. in the note counts, including pages of other people's works the note cites (a reference to "pp.
1533-1543" in a bibliography line). So this is a triage list, not a verdict: each case prints the share of
references beyond the end and the line holding the largest one. A true case runs from p. 1 continuously past
the end; a false one has a few low numbers and a dense cluster far above, with a gap between.

## What it sees, and what it does not
| sees | does not see |
|---|---|
| references beyond the end of the file (a shrunken replacement) | a reference inside the range but on the wrong passage (image check) |
| | a replacement that got LONGER: old numbers still fall inside the new range, so this stays green |
The right-hand column is printed with every report, so a green result is not read as "nothing wrong".

Usage:
  python tools/note_page_range_gate.py [--notes notes] [--sources sources] [--registry degraded.json]
                                       [--file <name fragment>] [--exclude <folder name>]...
  --registry  the degradation registry (shared/degradation-registry.md): a note for a work registered not_citable
              with unusable page numbers should carry no page reference, and is flagged if it does
  python tools/note_page_range_gate.py --self-test
Notes and PDFs are paired by file name ({Author}_{Year}_{Title}.md ⇄ .pdf; a leading ★ on the note is ignored).
Needs PyMuPDF. Exit codes: 0 = nothing out of range / 2 = cases to look at / 3 = cannot run
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CITE = re.compile(r"\bpp?\.\s*(\d{1,4})(?:\s*[-–—]\s*(\d{1,4}))?")
SHARE_MIN = 0.25


def page_count(pdf: Path):
    import pymupdf
    with pymupdf.open(pdf) as d:
        return d.page_count


def judge(body: str, npg: int):
    """(verdict, lowest, highest, evidence) with verdict 'out' / 'unknown' / 'ok' / None (no references)."""
    hits = [(int(a), int(b) if b else int(a), m) for m, (a, b) in zip(CITE.finditer(body), CITE.findall(body))]
    cited = [v for lo, hi, _ in hits for v in (lo, hi)]
    if not cited:
        return None, 0, 0, ""
    mx, mn = max(cited), min(cited)
    over = [v for v in cited if v > npg]
    share = len(over) / len(cited)
    pos = next(m.start() for lo, hi, m in hits if max(lo, hi) == mx)
    s0, e0 = body.rfind("\n", 0, pos) + 1, body.find("\n", pos)
    line = re.sub(r"\s+", " ", body[s0:e0 if e0 > 0 else len(body)])[:150]
    ev = f"beyond the end {len(over)}/{len(cited)} = {share:.0%} | the line with the largest: …{line}…"
    if mn <= 3 and mx > npg and share >= SHARE_MIN:
        return "out", mn, mx, f"counts from p.{mn}, the file has {npg} pages | {ev}"
    if mn > npg or mx <= npg:
        return "ok", mn, mx, ""
    return "unknown", mn, mx, ev


def no_page_stems(registry):
    """Stems of works the degradation registry marks not_citable with page_numbers unusable
    (shared/degradation-registry.md). A note for one of them should carry no page reference at all."""
    if not registry:
        return None
    import json
    data = json.loads(Path(registry).read_text(encoding="utf-8"))
    return {Path(e["rel"]).stem for e in data.get("not_citable", [])
            if not (e.get("usable") or {}).get("page_numbers", False)}


def run(notes: Path, sources: Path, only=None, exclude=(), registry=None):
    if not notes.is_dir() or not sources.is_dir():
        print(f"❌ need --notes and --sources folders (got {notes}, {sources})")
        return 3
    nopage = no_page_stems(registry)
    files = [p for p in sorted(notes.rglob("*.md")) if not p.name.startswith("_")
             and not any(x in p.parts for x in exclude) and (not only or only.lower() in p.name.lower())]
    pdfs = {p.stem: p for p in sources.rglob("*.pdf")}
    out, unk, ok, skip = [], [], 0, 0
    for n in files:
        pdf = pdfs.get(n.stem.lstrip("★ ").strip())
        if pdf is None:
            skip += 1
            continue
        try:
            npg = page_count(pdf)
        except Exception:  # noqa: BLE001
            skip += 1
            continue
        v, mn, mx, why = judge(n.read_text(encoding="utf-8", errors="replace"), npg)
        if v is None:
            skip += 1
        elif nopage and pdf.stem in nopage:
            out.append((n, mn, mx, npg, f"registered not_citable (page numbers unusable), yet cites pages | {why or 'beyond the end 0/0 = 0%'}"))
        elif v == "out":
            out.append((n, mn, mx, npg, why))
        elif v == "unknown":
            unk.append((n, mn, mx, npg, why))
        else:
            ok += 1
    print(f"note page-range gate | {len(files)} notes; {len(files) - skip} with page references and a PDF "
          f"({skip} without a PDF or a page reference: not counted)")
    print(f"\n🔶 to look at: {len(out)} (sorted by share beyond the end; the share and the line are the evidence)")
    print("   triage, not a verdict: a note citing printed folios that also mentions a low page somewhere can land here.")
    print("   true case: references run from p. 1 continuously past the end; false case: a few low numbers, a dense cluster far above.")
    def share(why):
        m = re.search(r"= (\d+)%", why)
        return float(m.group(1)) if m else 0.0
    for n, mn, mx, npg, why in sorted(out, key=lambda x: -share(x[4])):
        print(f"   p.{mn}–p.{mx}  PDF {npg} pages | {why}\n      {n.relative_to(notes)}")
    print(f"\n❔ cannot tell: {len(unk)} (not decided here)")
    for n, mn, mx, npg, why in sorted(unk, key=lambda x: -(x[2] - x[3])):
        print(f"   p.{mn}–p.{mx}  PDF {npg} pages | {why}\n      {n.relative_to(notes)}")
    print(f"\n✅ inside the range: {ok}")
    if nopage is None:
        print("ⓘ no --registry given: notes for works registered not_citable were not checked for page references")
    print("\n🔴 blind spot: a replacement that got LONGER keeps the old numbers inside the new range, so this stays green."
          "\n   That family needs other evidence: page anchors renumbered N → 2N, or an image check.")
    return 2 if out else 0


def _self_test() -> int:
    import tempfile, shutil, io, contextlib
    checks = [
        ("shrunk replacement: p.1…p.36 in a 21-page file", judge(" ".join(f"p. {p}" for p in (1, 4, 9, 16, 20, 24, 29, 33, 36)), 21)[0] == "out"),
        ("printed folios pp. 223–244 in a 23-page file", judge("pp. 223-244 and p. 230", 23)[0] == "ok"),
        ("inside the range", judge("p. 3, p. 12, pp. 14–15", 20)[0] == "ok"),
        ("someone else's pages in a bibliography line: not 'out'", judge("p. 1 … p. 2 … p. 5 … p. 7 … p. 9 … p. 11 … pp. 1533–1543", 18)[0] != "out"),
        ("middle numbers past the end: cannot tell", judge("p. 5, p. 12, p. 30", 20)[0] == "unknown"),
        ("no page reference", judge("no pages here", 20)[0] is None),
    ]
    try:
        import pymupdf
        tmp = Path(tempfile.mkdtemp())
        (tmp / "notes" / "a").mkdir(parents=True)
        (tmp / "sources" / "a").mkdir(parents=True)
        for stem, pages, body in (("Doe_2018_Echo", 21, " ".join(f"p. {p}" for p in range(1, 37, 3))),
                                  ("Roe_2003_Folios", 23, "pp. 223-244"), ("Poe_2010_Fine", 30, "p. 3, p. 28")):
            d = pymupdf.open()
            for _ in range(pages):
                d.new_page()
            d.save(tmp / "sources" / "a" / f"{stem}.pdf")
            d.close()
            (tmp / "notes" / "a" / (("★" if stem.startswith("Roe") else "") + stem + ".md")).write_text(body, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = run(tmp / "notes", tmp / "sources")
        o = buf.getvalue()
        checks.append(("end to end: one case, exit 2, blind spot printed", rc == 2 and "to look at: 1" in o and "Doe_2018_Echo" in o
                       and "inside the range: 2" in o and "blind spot" in o and "no --registry given" in o))
        (tmp / "degraded.json").write_text('{"not_citable": [{"rel": "a/Poe_2010_Fine.txt", "cause": "online-first", '
                                           '"usable": {"page_numbers": false}}]}', encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = run(tmp / "notes", tmp / "sources", registry=tmp / "degraded.json")
        o = buf.getvalue()
        checks.append(("--registry: a not_citable work's note citing pages is flagged", rc == 2 and "to look at: 2" in o
                       and "registered not_citable" in o))
        shutil.rmtree(tmp, ignore_errors=True)
    except ImportError:
        skipped = 2
    else:
        skipped = 0
    bad = 0
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    if skipped:
        print(f"skip  end to end, {skipped} checks (PyMuPDF not installed)")
    print(f"{len(checks) - bad} of {len(checks)} as expected" + (f", {skipped} skipped" if skipped else ""))
    return 1 if bad else 0


def main() -> int:
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()

    def opt(k, d=None):
        return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d
    excl = [a[i + 1] for i, x in enumerate(a) if x == "--exclude" and i + 1 < len(a)]
    return run(Path(opt("--notes", "notes")), Path(opt("--sources", "sources")), opt("--file"), excl, opt("--registry"))


if __name__ == "__main__":
    raise SystemExit(main())
