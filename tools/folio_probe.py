# -*- coding: utf-8 -*-
r"""folio_probe.py — find the printed page numbers from the PDF's layout, report the offset, and first ask
whether the offset is a constant at all (shared/evidence-handbook.md, page offsets; shared/page-offset-registry.md).

## Why
Every registry row says "printed = PDF + k". That formula assumes k is constant, and it need not be. This
tool's first job is to test that assumption; only then does it give k.

🔴 The case behind it: a monograph whose k was segmented (−10 / −8 / −6 / −4, every step at a chapter
opening, because the blank verso before each chapter was not in the PDF). A single offset would have been six
pages wrong by the end of the book, and every image check *inside one segment* would have passed.

## Three traps in "take the first number on the page" (all met in practice)
| Trap | What happened | What this tool does |
|---|---|---|
| a chapter number read as the folio | a chapter's first page carries "1" for chapter 1 | only page-edge blocks and the first/last two lines; prefer blocks that are nothing but a number |
| a folio in the Private Use Area | a publisher's small-caps running head has no ToUnicode mapping, so digits extract as PUA code points | detect and decode them (PUA_BASE: 0xF643 = "0" in the cases met) |
| a note number or a year read as the folio | a year inside a quotation | an upper bound (--max, default 2000) and a distribution, so outliers do not decide |

🔑 The last line of defence is not these three but printing the distribution: "one value" and "four values" look
   different at a glance, and a report that prints only the mode shows the second as the first.

## What it does not do
- It does not look at images. It reads the text layer. A quote's page needs the printed number seen on the page
  image (governance/claims-and-evidence.md §1); this tool gives candidates and tests the assumption.
- It does not decide whether missing pages had content; it only says where the printed numbering jumps.

Usage:
  python tools/folio_probe.py <file.pdf> [...] [--all] [--max N] [--book]
  python tools/folio_probe.py --self-test
Needs PyMuPDF (pip install pymupdf).
Exit codes: 0 = an offset (constant or segmented) / 2 = no folio found / 3 = numbers found but none usable,
or a reflowed conversion (do not register an offset)
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PUA_BASE = 0xF643          # met in practice: 0xF643 = '0'
EDGE = 0.10                # page edge = top and bottom 10%
NUM_ONLY = re.compile(r"^\s*(\d{1,4})\s*$")
NUM_HEAD = re.compile(r"^\s*(\d{1,4})\b")
# A journal's folio is often not a block of its own but sits in the running-head line or carries a prefix:
# "JOURNAL 07 371" (after the journal name), "[ E-44 ]" (brackets and an E- prefix), and on some even pages no
# page number at all. ⇒ a short edge block (< 40 characters) may yield its trailing number; an E- prefix is kept.
NUM_TAIL = re.compile(r"(?:^|\s)(?:E-)?(\d{1,4})\s*\]?\s*$")
EPREFIX = re.compile(r"\bE-(\d{1,4})\b")
# Letter-spaced or OCR-split numbers ("1 5" = 15, "23 1" = 231, "3 1 1" = 311). Taking only the last group read
# "1 5" as 5 and reported three segments for what was a constant offset. ⇒ a line or block holding only digits and
# single spaces, at most four digits in all, is joined before it is judged. Numbers inside text are not joined.
SPACED = re.compile(r"^\s*(\d{1,3}(?: \d{1,3}){1,3})\s*$")
# "Offset 0 and the whole document numbered ⇒ a reflowed conversion" holds only for books: a printed book has
# front matter. Articles are numbered from 1 routinely (article-number journals, e-locators, preprints), and
# sixteen of them were once wrongly flagged. ⇒ up to ARTICLE_MAX pages counts as article length. --book forces book mode.
ARTICLE_MAX = 80
# A typesetter's PDF (not a word-processor or e-book conversion) numbered from 1 is a self-paginated document
# (an institutional report, a white paper) whatever its length.
TYPESET_RX = re.compile(r"InDesign|pdfTeX|XeTeX|LuaTeX|LaTeX|QuarkXPress|Arbortext|FrameMaker|Antenna House|Prince", re.I)
CONVERT_RX = re.compile(r"Microsoft[ ®]*Word|\.rtf|\.docx?\b|LibreOffice|OpenOffice|calibre|EPUB", re.I)
# "Page k of M" and "k of M": otherwise the article number at the page edge, or M, is taken as the folio and every
# page gives a different offset. ⇒ a short edge line (< 50 characters) is searched for "k of M" (k ≤ M) first.
OF_M = re.compile(r"(?:^|\s)(?:Page\s+)?(\d{1,4})\s+of\s+(\d{1,4})(?=\s|$)", re.I)
# "k / M": spaces on both sides of the slash and M ≤ 300, so years ("2019/2020") and dates are not taken.
SLASH_M = re.compile(r"(?:^|\s)(\d{1,3})\s+/\s+(\d{1,3})(?=\s|$)")
RUN_MIN = 4                # a real segment shows the same offset on at least 4 consecutive PDF pages
ALT_NUM = re.compile(r"^\s*(\d{1,5})\s*$")


def _k_of_m(s: str):
    if len(s) >= 50:
        return None
    m = OF_M.search(s)
    if m and 1 <= int(m.group(1)) <= int(m.group(2)):
        return int(m.group(1))
    m = SLASH_M.search(s)
    if m and 1 <= int(m.group(1)) <= int(m.group(2)) <= 300:
        return int(m.group(1))
    return None


def _join_spaced(s: str) -> str:
    m = SPACED.match(s)
    if m and len(m.group(1).replace(" ", "")) <= 4:
        return m.group(1).replace(" ", "")
    return s


def _decode_pua(s: str) -> str:
    """Small-caps PUA digits → ASCII (anything outside the range is left alone)."""
    return "".join(chr(ord(c) - PUA_BASE + 0x30) if PUA_BASE <= ord(c) <= PUA_BASE + 9 else c for c in s)


def _edge_lines(page):
    """The top two and bottom two lines of the page, with their y.
    Blocks alone are not enough: one article had no block at all in the top or bottom 10% (very wide margins),
    and a tightly cropped scan had body text in its edge blocks. The folio is almost always the page's first or
    last line; position in the sequence is steadier than position in the frame."""
    lines = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            txt = "".join(sp["text"] for sp in ln["spans"]).strip()
            if txt:
                lines.append((ln["bbox"][1], txt))
    lines.sort(key=lambda x: x[0])
    return [(y, t, "top") for y, t in lines[:2]] + [(y, t, "bottom") for y, t in lines[-2:]]


def folio_of(page, strict: bool, vmax: int):
    """(folio, position). Looks at edge blocks and the first/last two lines; prefers blocks that are only a number."""
    H = page.rect.height
    loose = None
    cands = [(b[1], b[3], b[4].strip()) for b in page.get_text("blocks")]
    cands = [(y0, y1, t) for y0, y1, t in cands if y0 < H * EDGE or y1 > H * (1 - EDGE)]
    cands += [(y, y, t) for y, t, _ in _edge_lines(page)]
    for y0, y1, raw in cands:                       # "k of M" first (per-article numbering)
        for part in raw.split("\n"):
            k = _k_of_m(part.strip())
            if k is not None and k <= vmax:
                return k, ("top" if y0 < H * 0.5 else "bottom")
    for y0, y1, raw in cands:
        txt = _join_spaced(_decode_pua(raw))
        pos = "top" if y0 < H * 0.5 else "bottom"
        m = NUM_ONLY.match(txt)
        if m and int(m.group(1)) <= vmax:
            return int(m.group(1)), pos
        if not strict and loose is None:
            if len(txt) < 40:                        # trailing number of a short running head
                m3 = NUM_TAIL.search(txt) or EPREFIX.search(txt)
                if m3 and int(m3.group(1)) <= vmax:
                    loose = (int(m3.group(1)), pos)
                    continue
            m2 = NUM_HEAD.match(txt)                 # leading number ("114 author and author")
            if m2 and int(m2.group(1)) <= vmax:
                loose = (int(m2.group(1)), pos)
    return loose if loose else (None, None)


def all_numeric_cands(page) -> set:
    """Every bare number (up to five digits) on every edge line. A paper in conference proceedings printed
    "6" over "14279" (its own page number and the proceedings page); folio_of sees only the 6."""
    H = page.rect.height
    texts = [b[4] for b in page.get_text("blocks") if b[1] < H * EDGE or b[3] > H * (1 - EDGE)]
    texts += [t for _, t, _ in _edge_lines(page)]
    out = set()
    for t in texts:
        for part in t.split("\n"):
            m = ALT_NUM.match(_join_spaced(_decode_pua(part.strip())))
            if m:
                out.add(int(m.group(1)))
    return out


def classify(rows, n, alt, meta="", force_book=False):
    """Pure decision step (testable without a PDF). rows = [(pdf_page, folio, pos)]; alt = Counter of offsets
    from secondary numbers. Returns (code, kind, details)."""
    if not rows:
        return 2, "none", {}
    offs = Counter(fo - pg for pg, fo, _ in rows)
    span = {}
    for o in offs:
        ps = [pg for pg, fo, _ in rows if fo - pg == o]
        span[o] = (min(ps), max(ps))
    # Noise is told by shape, not by count. A first version kept every offset seen 3+ times, and in a 20-page
    # article a note number seen 4 times survived beside the real offset seen 5 times: a false "not constant".
    # A real offset's pages form a consecutive run; noise lives inside another offset's run. And a run is
    # counted page by page (a gap breaks it), threshold 4: aphorism numbers on three nearby pages once
    # formed a fake segment at threshold 3.
    longest, cur, cnt, prev = Counter(), None, 0, None
    for pg, fo, _ in rows:
        o = fo - pg
        cnt = cnt + 1 if (o == cur and prev is not None and pg == prev + 1) else 1
        cur, prev = o, pg
        longest[o] = max(longest[o], cnt)
    real = {o for o in offs if longest[o] >= RUN_MIN}
    for o in sorted(offs, key=lambda x: -offs[x]):
        if o in real:
            continue
        a, b = span[o]
        if any(offs[r] > offs[o] and not (b < span[r][0] or a > span[r][1]) for r in real):
            continue                                 # inside a stronger offset's range ⇒ noise
        if offs[o] >= 3 or (offs[o] >= 2 and len(rows) < 40):
            real.add(o)
    # Two numberings (a paper's own page number and the volume's): if a second set of numbers is on nearly
    # every page too, both are printed, and the citable one is the larger.
    if alt:
        ao, ac = alt.most_common(1)[0]
        if ac >= max(3, 0.8 * len(rows)) and ao not in real:
            main = max(real, key=lambda x: offs[x]) if real else None
            if main is None or ao > main:
                return 0, "dual", {"offset": ao, "pages": ac, "main": main, "offs": offs}
    kept = [(pg, fo) for pg, fo, _ in rows if (fo - pg) in real]
    if not real:
        return 3, "unusable", {"offs": offs, "rows": len(rows)}
    if len(real) == 1:
        k = next(iter(real))
        cover = len(kept) / n
        typeset = bool(TYPESET_RX.search(meta)) and not CONVERT_RX.search(meta)
        if k == 0 and cover > 0.90 and n > ARTICLE_MAX and typeset and not force_book:
            return 0, "self-paginated", {"offset": 0, "offs": offs}
        if k == 0 and cover > 0.90 and n <= ARTICLE_MAX and not force_book:
            return 0, "per-article", {"offset": 0, "offs": offs}
        if k == 0 and cover > 0.90:
            # The one branch where a beautiful answer must be stopped: a printed book has front matter, so k
            # cannot be 0. Offset 0 on nearly every page means the numbers were added by a converter (a 294-page
            # book reflowed into 203 PDF pages, each "numbered").
            return 3, "reflowed", {"offs": offs}
        thin = len(kept) < 5 or cover < 0.05      # thin evidence must not look like thick evidence
        return 0, "constant", {"offset": k, "kept": kept, "thin": thin, "offs": offs}
    seg, prev = [], None
    for pg, fo in kept:
        o = fo - pg
        if o != prev:
            seg.append([o, pg, pg]); prev = o
        else:
            seg[-1][2] = pg
    merged = []
    for o, a, b in seg:
        if merged and merged[-1][0] == o:
            merged[-1][2] = b
        else:
            merged.append([o, a, b])
    return 0, "segmented", {"segments": merged, "spread": max(real) - min(real), "offs": offs}


def probe(pdf: Path, show_all=False, vmax=2000, force_book=False) -> int:
    import pymupdf
    d = pymupdf.open(pdf)
    n = d.page_count
    meta = " ".join(str(v) for v in (d.metadata or {}).values() if v)
    rows, alt = [], Counter()
    for pg in range(1, n + 1):
        fo, pos = folio_of(d[pg - 1], strict=True, vmax=vmax)
        if fo is None:
            fo, pos = folio_of(d[pg - 1], strict=False, vmax=vmax)
        if fo is not None:
            rows.append((pg, fo, pos))
        alt.update({c - pg for c in all_numeric_cands(d[pg - 1]) if c != fo and c > pg})
    d.close()
    print(f"\n== {pdf.name[:78]}")
    print(f"   {n} pages · folio found on {len(rows)} ({len(rows) / n:.0%})")
    code, kind, x = classify(rows, n, alt, meta, force_book)
    if kind == "none":
        print("   🔴 no folio at all: this is not 'offset 0', it is 'not measured'. Check the page images.")
        return code
    print(f"   offset distribution (all): {x['offs'].most_common(8)}")
    if kind == "dual":
        print(f"   🔶 two numberings: a second set is on {x['pages']} pages, offset {x['offset']:+d}"
              + (f"; main set {x['main']:+d}" if x["main"] is not None else ""))
        print(f"   ⇒ register: printed = PDF {x['offset']:+d} (the volume's numbering; check a page foot on the image)")
    elif kind == "unusable":
        print(f"   🔴 numbers on {x['rows']} pages, none of them a page number (note numbers, chapter numbers, years).")
        print("   ⇒ no usable folio signal: do not register a computed offset; page every quote from the image.")
    elif kind == "reflowed":
        print("   🔴🔴 offset 0 on nearly every page of a book-length file: these are PDF page numbers, not printed ones.")
        print("   A printed book has front matter, so k cannot be 0 ⇒ a reflowed conversion: register no offset, cite no page.")
    elif kind == "per-article":
        print(f"   🟡 offset 0 on nearly every page, {n} pages (article length): per-article numbering. Check the first page's masthead on the image.")
        print("   ⇒ register: printed = PDF +0 (per article), with an image point")
    elif kind == "self-paginated":
        print(f"   🟡 offset 0 on nearly every page, {n} pages, made by a typesetter: a self-paginated document (a report, a white paper).")
        print("   ⇒ register: printed = PDF +0, with an image point")
    elif kind == "constant":
        lo, hi = x["kept"][0][0], x["kept"][-1][0]
        print(f"\n   {'🟡 thin evidence:' if x['thin'] else '✅'} offset is constant {x['offset']:+d} · "
              f"{len(x['kept'])} points · PDF p{lo}–p{hi}")
        if x["thin"]:
            print("      ⚠ check at least two points on the image before registering, far apart (one segment agreeing says nothing about the rest)")
        print(f"   ⇒ register: printed = PDF {x['offset']:+d}")
    else:
        print(f"\n   🔴🔴 offset is NOT constant: a single offset would be up to {x['spread']} pages wrong. Register segments:")
        for o, a, b in x["segments"]:
            print(f"      PDF p{a:>4}–p{b:<4}  printed = PDF {o:+d}" + ("  ⚠ single-point segment, probably noise" if a == b else ""))
        print("   ⚠ a human should look at the boundaries: they are usually chapter openings (a blank verso left out of the PDF).")
    if show_all:
        print("\n   page by page:")
        for pg, fo, pos in rows:
            print(f"      p{pg:>4} → {fo:>5} ({pos}) {fo - pg:+d}")
    print("\n   🎫 this reads the text layer; it is not an image check.")
    return code


def _self_test() -> int:
    bad = 0
    pos = {"Page 2 of 20": 2, "24   Page 2 of 24": 2, "Page 5 of 24 24": 5, "2 of 8": 2, "page 13 of 13": 13,
           "3 / 17": 3, "JOURNAL | https://doi.org/10.1/x  5 / 17": 5}
    neg = ["164", "Journal (2026) 208:164", "9 of 8", "one of the three", "x" * 60 + " 2 of 8",
           "2019/2020", "3/17", "18 / 17", "12 / 400"]
    for s, k in pos.items():
        bad += _k_of_m(s) != k
    for s in neg:
        bad += _k_of_m(s) is not None
    print(("ok   " if not bad else "FAIL ") + f"'k of M' and 'k / M': {len(pos)} positive, {len(neg)} negative")
    checks = [
        ("letter-spaced number joined", _join_spaced("1 5") == "15" and _join_spaced("3 1 1") == "311" and _join_spaced("12 34 5") == "12 34 5"),
        ("PUA digits decoded", _decode_pua(chr(PUA_BASE + 4) + chr(PUA_BASE + 2)) == "42"),
    ]
    R = lambda pairs: [(pg, fo, "bottom") for pg, fo in pairs]
    const = R([(p, p + 12) for p in range(5, 205)])
    seg = R([(p, p - 10) for p in range(20, 80)] + [(p, p - 8) for p in range(80, 150)] + [(p, p - 6) for p in range(150, 230)])
    noisy = R([(p, p + 165) for p in range(1, 21) if p not in (3, 7, 11, 15)] + [(p, p - 2) for p in (3, 7, 11, 15)])
    reflow = R([(p, p) for p in range(1, 204)])
    article = R([(p, p) for p in range(1, 21)])
    thin = R([(10, 22), (40, 52), (90, 102)])
    cases = [
        ("constant +12", classify(const, 210, Counter()), ("constant", 12)),
        ("segmented, three values", classify(seg, 230, Counter()), ("segmented", None)),
        ("note numbers inside a run are noise", classify(noisy, 20, Counter()), ("constant", 165)),
        ("offset 0 on a 203-page book: reflowed", classify(reflow, 203, Counter(), meta="Microsoft Word - book.rtf"), ("reflowed", None)),
        ("offset 0 on a 20-page article: per-article", classify(article, 20, Counter()), ("per-article", None)),
        ("three points: constant but thin", classify(thin, 300, Counter()), ("constant", 12)),
        ("no rows: not measured", classify([], 50, Counter()), ("none", None)),
        ("second numbering on every page wins", classify(R([(p, 6 if p == 1 else p + 5) for p in range(1, 13)]), 12,
                                                         Counter({14273: 12})), ("dual", 14273)),
    ]
    for name, (code, kind, x), (want_kind, want_off) in cases:
        ok = kind == want_kind and (want_off is None or x.get("offset") == want_off)
        if name.startswith("three points"):
            ok = ok and x["thin"]
        checks.append((name, ok))
    try:
        import pymupdf
        doc = pymupdf.open()
        for p in range(1, 31):
            pg = doc.new_page(width=420, height=600)
            pg.insert_text((60, 120), "Chapter text that mentions 1987 in passing.", fontsize=10)
            pg.insert_text((205, 585), str(p + 8 if p < 16 else p + 10), fontsize=9)
        rows, alt = [], Counter()
        for i in range(doc.page_count):
            fo, pos_ = folio_of(doc[i], True, 2000)
            if fo is not None:
                rows.append((i + 1, fo, pos_))
        doc.close()
        code, kind, x = classify(rows, 30, alt)
        checks.append(("synthetic PDF, offsets +8 then +10: segmented", kind == "segmented"
                       and [s[0] for s in x["segments"]] == [8, 10]))
    except ImportError:
        print("skip  synthetic PDF (PyMuPDF not installed)")
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    print("all as expected" if not bad else f"{bad} unexpected")
    return 1 if bad else 0


def main() -> int:
    if "--self-test" in sys.argv:
        return _self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()]
    if not args:
        print(__doc__)
        return 2
    vmax = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 2000
    rc = 0
    for a in args:
        rc = max(rc, probe(Path(a), show_all="--all" in sys.argv, vmax=vmax, force_book="--book" in sys.argv))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
