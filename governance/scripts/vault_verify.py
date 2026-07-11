# -*- coding: utf-8 -*-
"""Vault structural verification — run after any large operation.

Five checks:
  1. counts on both ends (notes / source PDFs)
  2. legacy-format remnants (configurable heading patterns; should be 0)
  3. note category field vs actual folder
  4. filename year vs metadata year (year_note-annotated files exempt)
  5. two-end filename alignment (star stripped; configurable exemption marks)

Dead links are a separate scan (dead_link_scan.py).
Configure the block below for your vault.
"""
import re
import sys
from pathlib import Path

# ── config ──────────────────────────────────────────────────────────
VAULT = Path(".")                      # vault root containing notes/ and sources/
NOTES, PDFS = VAULT / "notes", VAULT / "sources"
EXCLUDE = ("_trash", ".obsidian", ".smart-env")
NON_LITERATURE = ("_project",)         # note folders that are not literature (skipped in 1/3/5)
LEGACY_HEADINGS = r"## (Legacy Section A|Legacy Section B)"   # your pre-schema headings, if any
# notes whose header carries any of these marks are design-exempt from two-end alignment
EXEMPT_MARKS = ("no standalone PDF", "web-native", "book-level overview", "chapter-level note")
COMPANION_MARK = "(companion)"         # PDF filename mark for translation companions etc.
SHOW_MAX = 20
# ────────────────────────────────────────────────────────────────────

def mds():
    for md in NOTES.rglob("*.md"):
        p = str(md)
        if any(x in p for x in EXCLUDE) or any(x in p for x in NON_LITERATURE):
            continue
        yield md

problems = 0

# 1. counts
n_md = sum(1 for m in mds() if m.stem != m.parent.name)   # MOCs excluded
n_pdf = sum(1 for f in PDFS.rglob("*.pdf") if not any(x in str(f) for x in EXCLUDE))
print(f"1) notes (non-MOC): {n_md}   source PDFs: {n_pdf}")

# 2. legacy remnants
OLD = re.compile(LEGACY_HEADINGS)
bad = [str(m.relative_to(NOTES)) for m in mds() if OLD.search(m.read_text(encoding="utf-8"))]
print(f"2) legacy-format remnants (expect 0): {len(bad)}")
for b in bad[:SHOW_MAX]:
    print(f"   {b}")
problems += len(bad)

# 3. category vs folder
CAT = re.compile(r'^category:\s*"?([^"\n]+?)"?\s*$', re.M)
mism = []
for m in mds():
    rel_dir = m.parent.relative_to(NOTES).as_posix()
    if rel_dir == "." or m.stem == rel_dir.rsplit("/", 1)[-1]:
        continue   # root files and MOCs exempt
    mt = CAT.search(m.read_text(encoding="utf-8"))
    if mt and mt.group(1).strip() != rel_dir:
        mism.append((str(m.relative_to(NOTES)), mt.group(1).strip(), rel_dir))
print(f"3) category vs folder mismatches: {len(mism)}")
for f, c, d in mism[:SHOW_MAX]:
    print(f"   {f}: metadata[{c}] vs folder[{d}]")
problems += len(mism)

# 4. filename year vs metadata year
FY = re.compile(r"_(\d{3,4})(BCE)?_")
YY = re.compile(r'^year:\s*"?(\d{3,4})', re.M)
ymis, ynoted = [], 0
for m in mds():
    fm = FY.search(m.name)
    if not fm:
        continue
    head = m.read_text(encoding="utf-8")[:1500]
    ym = YY.search(head)
    if ym and fm.group(1) != ym.group(1):
        if "year_note:" in head:
            ynoted += 1
            continue
        ymis.append((m.name, fm.group(1), ym.group(1)))
print(f"4) filename-year vs metadata-year mismatches: {len(ymis)} (year_note-exempt: {ynoted})")
for n, a, b in ymis[:SHOW_MAX]:
    print(f"   {n}: filename[{a}] metadata[{b}]  -> fix (rename chain) or annotate year_note")
problems += len(ymis)

# 5. two-end alignment (star stripped; exemptions honoured)
note_items = {}
for m in mds():
    if m.stem == m.parent.name:
        continue   # MOC
    note_items[(str(m.parent.relative_to(NOTES)), m.stem.lstrip("★"))] = m
pdf_set = {(str(f.parent.relative_to(PDFS)), f.stem) for f in PDFS.rglob("*.pdf")
           if not any(x in str(f) for x in EXCLUDE) and COMPANION_MARK not in f.stem}
only_note, exempt_n = [], 0
for key in sorted(set(note_items) - pdf_set):
    head = note_items[key].read_text(encoding="utf-8")[:2500]
    if any(x in head for x in EXEMPT_MARKS):
        exempt_n += 1
        continue
    only_note.append(key)
only_pdf = sorted(pdf_set - set(note_items))
print(f"5) two-end alignment: note-only {len(only_note)} (exempt {exempt_n})   pdf-only {len(only_pdf)}")
for d, s in only_note[:SHOW_MAX]:
    print(f"   [note only] {d}/{s}")
for d, s in only_pdf[:SHOW_MAX]:
    print(f"   [pdf  only] {d}/{s}")
# note: listed ≠ wrong — pdf-only items may be unprocessed arrivals; judge before acting.

sys.exit(1 if problems else 0)
