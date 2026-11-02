# -*- coding: utf-8 -*-
"""split_2up.py — split a two-up scan (two printed pages on one PDF page) into one printed page per PDF page
(roles/librarian.md, the page-anchor gate; shared/evidence-handbook.md, page offset ③).

## Why it has to be split (not for looks)
Two parts of the citation chain assume one PDF page = one printed page:
| mechanism | assumption |
|---|---|
| `===== page N =====` anchors | the text under one anchor belongs to one printed page |
| the folio credential (render page n, report the printed number) | the image shows one printed number |
A two-up scan breaks both: one PDF page holds printed pages 70 and 71, so an anchor mixes two pages' text and
the image shows two numbers, with no way to tell which page the quote is on. An offset can be corrected; a
multiple cannot.

## 🔴🔴 The vector path is broken for rotated pages, and it breaks quietly
A source whose pages all carried /Rotate 270: the first version computed the halves from the rotated frame and
passed them as `clip` to show_pdf_page, whose clip lives in the unrotated mediabox. It cut "the top-left 65% x 77%
of the unrotated page": across both printed pages, with line ends cut off. Measured on that file's text layer:
10.1% of lines ended in a fragment, against 0.8% for unrotated two-up sources. The original was intact; the words
were lost by the split, not the scan. Sixteen combinations of clip x target size x rotate, compared by pixels
against "render as displayed, then cut", all gave the same wrong answer: there is no right parameter.
⇒ ① rotation guard: a source with any /Rotate ≠ 0 makes the vector path refuse (exit 3) instead of producing a
     plausible-looking wrong file; ② --raster renders as displayed and cuts the image, the only path verified to
     handle /Rotate. ⚠ It destroys the text layer, so it is for image-only scans, which need OCR anyway.

## 🔑 The vector split is lossless
show_pdf_page(clip=left/right half) embeds the original page content (including any OCR text layer) with new
page bounds. The source is never changed; the result is a new file.

## Three things a human must look at
1. Where two-up starts: covers and title pages are often single (--from).
2. Order: left to right is assumed (Western books).
3. After splitting: --verify prints sizes and text samples, but "one printed number on the image" only a human
   eye can confirm; this tool does not claim to have checked it.

Usage:
  python tools/split_2up.py <in.pdf> <out.pdf> [--gutter] [--raster [--dpi 300]] [--from 2] [--axis v|h]
                            [--rotate 0|90|180|270] [--probe-axis] [--verify]
  python tools/split_2up.py --self-test
Needs PyMuPDF (pip install pymupdf).
"""
import argparse
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")


def gutter_x(page, r) -> float:
    """Cut at the gutter (the white band between the pages), not at the geometric middle.
    The middle is a proxy for "where the pages meet", and a scan need not be symmetric: one left page crossed the
    middle and the cut went through its line ends ("each c" for "each class", plus orphan fragments). One page in
    156, but that page's content was wrong. ⇒ measure the thing itself: in the central band, the column with the
    least ink is the gutter. Only ±12% around the middle, or the blank margin wins."""
    import pymupdf
    band = 0.12
    pix = page.get_pixmap(dpi=36, colorspace=pymupdf.csGRAY, clip=r)
    w, h, s = pix.width, pix.height, pix.samples
    lo, hi = int(w * (0.5 - band)), int(w * (0.5 + band))
    best_x, best_ink = None, None
    for x in range(lo, hi):
        ink = sum(255 - s[y * w + x] for y in range(h))
        if best_ink is None or ink < best_ink:
            best_ink, best_x = ink, x
    return r.x0 + (best_x + 0.5) * r.width / w


def gutter_px(gray, w, h, band=0.12) -> int:
    """Raster gutter (vertical cut): the pixel column with the least ink in the central band."""
    lo, hi = int(w * (0.5 - band)), int(w * (0.5 + band))
    best_x, best_ink = w // 2, None
    for x in range(lo, hi):
        ink = sum(255 - gray[y * w + x] for y in range(0, h, 3))   # every third row: as good, three times faster
        if best_ink is None or ink < best_ink:
            best_ink, best_x = ink, x
    return best_x


def gutter_py(gray, w, h, band=0.12) -> int:
    """Raster gutter (horizontal cut): the pixel row with the least ink.
    A two-up scan can stack its pages top and bottom, each turned 90°, inside a portrait frame, so "wider than
    tall" cannot detect it. 🔑 The axis is measured, not inferred from the page shape: --probe-axis compares the
    least-ink ratio on both axes, on at least three pages (a blank page fools one)."""
    lo, hi = int(h * (0.5 - band)), int(h * (0.5 + band))
    best_y, best_ink = h // 2, None
    for y in range(lo, hi):
        base = y * w
        ink = sum(255 - gray[base + x] for x in range(0, w, 3))
        if best_ink is None or ink < best_ink:
            best_ink, best_y = ink, y
    return best_y


def _ink(gray) -> int:
    """Total ink (sum of 255 - grey): what the raster path must conserve."""
    return sum(255 - v for v in gray)


def run(argv) -> int:
    import pymupdf
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--gutter", action="store_true", help="cut at the detected gutter (recommended; the middle can cut into text)")
    ap.add_argument("--raster", action="store_true", help="raster path: destroys the text layer; image-only scans, and the only path for rotated sources")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--from", dest="start", type=int, default=1, help="first page (1-based) to split; earlier pages are kept as they are")
    ap.add_argument("--axis", choices=("v", "h"), default="v", help="v = left/right (default); h = top/bottom (raster only). Measure with --probe-axis")
    ap.add_argument("--rotate", type=int, default=0, choices=(0, 90, 180, 270), help="turn each half (raster only)")
    ap.add_argument("--probe-axis", action="store_true", help="measure the cut axis on three pages and stop")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    src, dst = pathlib.Path(a.src), pathlib.Path(a.dst)
    if not src.exists():
        print(f"❌ {src} not found (that is 'not read', not 'nothing to do')")
        return 2
    if dst.exists() and not a.probe_axis:
        print(f"❌ {dst} exists; not overwriting (remove it yourself to redo)")
        return 2
    d = pymupdf.open(src)

    if a.probe_axis:
        pts = [n for n in (d.page_count // 5, d.page_count // 2, d.page_count * 4 // 5) if 1 <= n <= d.page_count]
        print(f"🔬 {src.name[:56]}  pages {d.page_count}  rotation {sorted({d[i].rotation for i in range(d.page_count)})}")
        for n in pts:
            pm = d[n - 1].get_pixmap(dpi=36, colorspace=pymupdf.csGRAY)
            w, h, s = pm.width, pm.height, pm.samples
            col = [sum(255 - s[y * w + x] for y in range(h)) for x in range(w)]
            row = [sum(255 - s[y * w + x] for x in range(w)) for y in range(h)]

            def ratio(v, n_):
                lo, hi = int(n_ * 0.38), int(n_ * 0.62)
                avg = sum(v) / len(v)
                return (min(v[lo:hi]) / avg) if avg else 9.0
            rv, rh = ratio(col, w), ratio(row, h)
            print(f"   p{n:<4} {w}x{h}  vertical {rv:.3f}  horizontal {rh:.3f}  ⇒ {'--axis h' if rh < rv else '--axis v'}")
        print("⚠ the three pages must agree: a blank page makes one axis look small")
        d.close()
        return 0

    if (a.rotate or a.axis == "h") and not a.raster:
        print("🔴 --rotate and --axis h work only on the raster path (the vector clip and rotation interfere); refusing, "
              "not falling back to a left/right cut")
        d.close()
        return 3
    rots = sorted({d[i].rotation for i in range(d.page_count)})
    if rots != [0] and not a.raster:
        print(f"🔴 source pages carry rotation {rots}: the vector path is wrong for rotated pages; refusing")
        print("   if the file is image-only (no text layer to lose), add --raster")
        d.close()
        return 3

    out = pymupdf.open()
    n_kept = n_split = ink_src = ink_out = 0
    for i in range(d.page_count):
        pg = d[i]
        if i + 1 < a.start:
            out.insert_pdf(d, from_page=i, to_page=i)
            n_kept += 1
            continue
        if a.raster:
            pm = pg.get_pixmap(dpi=a.dpi, colorspace=pymupdf.csGRAY)   # renders as displayed (handles /Rotate)
            w, h, g = pm.width, pm.height, pm.samples
            ink_src += _ink(g)
            if a.axis == "h":
                y = gutter_py(g, w, h) if a.gutter else h // 2
                pieces = [(w, y, g[0:y * w]), (w, h - y, g[y * w:h * w])]   # top first: check on --verify
            else:
                x = gutter_px(g, w, h) if a.gutter else w // 2
                pieces = []
                for x0, x1 in ((0, x), (x, w)):
                    cw = x1 - x0
                    buf = bytearray(cw * h)
                    for yy in range(h):
                        buf[yy * cw:(yy + 1) * cw] = g[yy * w + x0:yy * w + x1]
                    pieces.append((cw, h, bytes(buf)))
            for cw, ch, buf in pieces:
                sub = pymupdf.Pixmap(pymupdf.csGRAY, cw, ch, bytes(buf), False)
                ink_out += _ink(sub.samples)
                pt_w, pt_h = cw * 72.0 / a.dpi, ch * 72.0 / a.dpi
                if a.rotate in (90, 270):
                    pt_w, pt_h = pt_h, pt_w
                np_ = out.new_page(width=pt_w, height=pt_h)
                np_.insert_image(np_.rect, pixmap=sub, rotate=a.rotate)
        else:
            r = pg.rect
            mid = gutter_x(pg, r) if a.gutter else (r.x0 + r.width / 2)
            for hf in (pymupdf.Rect(r.x0, r.y0, mid, r.y1), pymupdf.Rect(mid, r.y0, r.x1, r.y1)):
                np_ = out.new_page(width=hf.width, height=hf.height)
                np_.show_pdf_page(np_.rect, d, i, clip=hf)
        n_split += 1
    out.save(dst, garbage=3, deflate=True)
    print(f"✅ {src.name[:52]}")
    print(f"   path: {'raster (' + str(a.dpi) + ' dpi; text layer destroyed; OCR needed)' if a.raster else 'vector (lossless; text layer kept)'}"
          f" · cut: {'gutter' if a.gutter else 'middle'} · {'top/bottom' if a.axis == 'h' else 'left/right'}"
          f"{f' · each half turned {a.rotate}°' if a.rotate else ''}")
    print(f"   {d.page_count} pages → {out.page_count} pages (kept {n_kept} · split {n_split} x 2)")

    # Conservation gates. show_pdf_page does not carry annotations: a cover's bibliographic line inside a rotated
    # FreeText annotation was lost entirely. And a text-conservation gate is blind on image-only files (0 words
    # before, 0 after, whatever happened), which are the files that most need checking: say so in the line it
    # prints, and conserve ink on the raster path (a cut through text loses no ink; a dropped region does).
    def _words(doc):
        return len("".join(doc[j].get_text() for j in range(doc.page_count)).split())
    res = pymupdf.open(dst)
    a_n, b_n = _words(d), _words(res)
    res.close()
    n_annot = sum(1 for j in range(d.page_count) for _ in (d[j].annots() or []))
    rc = 0
    if a_n == 0:
        print("   ⚪ text conservation: BLIND on this file (no text layer); right split and wrong split both give 0. Not a green light.")
    elif a.raster:
        print(f"   ⚪ text conservation: not applicable (the raster path drops the {a_n:,}-word text layer by design; ink is checked instead)")
    else:
        delta = (b_n - a_n) / a_n * 100
        ok = abs(delta) < 0.5
        rc |= 0 if ok else 1
        print(f"   {'✅' if ok else '🔴'} text conservation: {a_n:,} words → {b_n:,} (Δ {delta:+.2f}%)" + ("" if ok else "  ⇒ content lost; check before use"))
    if a.raster:
        dl = (ink_out - ink_src) / ink_src * 100 if ink_src else 0.0
        ok = abs(dl) < 0.5
        rc |= 0 if ok else 1
        print(f"   {'✅' if ok else '🔴'} ink conservation: {ink_src:,} → {ink_out:,} (Δ {dl:+.2f}%)" + ("" if ok else "  ⇒ an image region was lost"))
    if n_annot:
        print(f"   ⚠ the source has {n_annot} annotation(s); the vector split does not carry them, so their text is lost")
    if a.verify:
        print("\n-- verify: sizes and text of sample pages --")
        res = pymupdf.open(dst)
        for j in sorted({0, 1, res.page_count // 2, res.page_count - 1}):
            if j < res.page_count:
                t = res[j].get_text().strip()
                print(f"   new p{j + 1}: {res[j].rect.width:.0f}x{res[j].rect.height:.0f}pt · {len(t)} characters · first line "
                      f"{t.splitlines()[0][:48] if t else '(empty)'!r}")
        res.close()
        print("⚠ sizes and counts prove it was split, not that it was split right: look at the rendered pages.")
    d.close()
    out.close()
    return rc


def _self_test() -> int:
    import io, contextlib, tempfile
    try:
        import pymupdf
    except ImportError:
        print("skip  PyMuPDF not installed")
        return 0
    tmp = pathlib.Path(tempfile.mkdtemp())
    src = tmp / "twoup.pdf"
    doc = pymupdf.open()
    for n in range(3):
        pg = doc.new_page(width=840, height=600)
        # left page slightly wider than half: the middle would cut into it, the gutter does not
        pg.insert_textbox(pymupdf.Rect(30, 40, 438, 560), f"Left page {70 + 2 * n}. " + "lorem ipsum dolor " * 30, fontsize=9)
        pg.insert_textbox(pymupdf.Rect(462, 40, 810, 560), f"Right page {71 + 2 * n}. " + "sit amet consectetur " * 25, fontsize=9)
    doc.save(src)
    rot = tmp / "rotated.pdf"
    doc[0].set_rotation(270)
    doc.save(rot)
    doc.close()
    checks = []
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        rc = run([str(src), str(tmp / "out.pdf"), "--gutter"])
    res = pymupdf.open(tmp / "out.pdf")
    t0, t1 = res[0].get_text(), res[1].get_text()
    checks.append(("vector split: 3 → 6 pages, exit 0", rc == 0 and res.page_count == 6))
    checks.append(("left half holds the left page only", "Left page 70" in t0 and "Right page" not in t0))
    checks.append(("right half holds the right page only", "Right page 71" in t1 and "Left page" not in t1))
    checks.append(("text conservation printed green", "✅ text conservation" in buf.getvalue()))
    res.close()
    with contextlib.redirect_stdout(io.StringIO()):
        rc_rot = run([str(rot), str(tmp / "out_rot.pdf")])
    checks.append(("rotated source: vector path refuses (exit 3), no file", rc_rot == 3 and not (tmp / "out_rot.pdf").exists()))
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        rc_r = run([str(rot), str(tmp / "out_raster.pdf"), "--raster", "--dpi", "72", "--gutter"])
    checks.append(("rotated source on the raster path: ink conserved", rc_r == 0 and "✅ ink conservation" in buf.getvalue()))
    checks.append(("raster output: text conservation reports itself blind or lost, never silent green",
                   "text conservation" in buf.getvalue()))
    with contextlib.redirect_stdout(io.StringIO()):
        rc_dst = run([str(src), str(tmp / "out.pdf")])
    checks.append(("existing output is not overwritten", rc_dst == 2))
    with contextlib.redirect_stdout(io.StringIO()):
        rc_h = run([str(src), str(tmp / "out_h.pdf"), "--axis", "h"])
    checks.append(("--axis h without --raster refuses", rc_h == 3))
    bad = 0
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    print(f"{len(checks) - bad} of {len(checks)} as expected")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        raise SystemExit(_self_test())
    raise SystemExit(run(sys.argv[1:]))
