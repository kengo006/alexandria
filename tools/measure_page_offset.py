# -*- coding: utf-8 -*-
"""measure_page_offset.py — the offset between a text layer's page anchors and the numbers printed on the page
(shared/evidence-handbook.md, page offsets; shared/page-offset-registry.md).

The registry wants every work measured at ingestion. This does the text-layer half of that measurement.

## The criterion: bare numbers in a running head or footer, and they must agree across pages
A line holding nothing but a number is (usually) the printed page number. Its difference from the page's
anchor is the offset. One page agreeing means nothing; the question is whether the whole work gives the
same difference. So the output is three things: the modal offset, how many pages support it out of how many
had a candidate, and the pages that disagree.
🔑 Low agreement means the offset is not a constant (front matter numbered separately, a work in sections).
   Taking the mode anyway is the error this tool exists to prevent.

⚠ This is text-layer evidence, not image evidence. A quote's page still needs the printed number seen on the
   page image (the folio credential, governance/claims-and-evidence.md §1). Use this to narrow the image check
   and to see whether the offset is constant; tools/folio_probe.py does the same from the PDF's layout.

Usage:
  python tools/measure_page_offset.py <text-layer.txt> [...]
  python tools/measure_page_offset.py --self-test
The text layer carries page anchors of the form `===== page N =====`.
"""
import collections
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ANCHOR = re.compile(r"={3,}\s*page\s+(\d+)\s*={3,}", re.I)
BARE = re.compile(r"(?m)^[ \t]*([1-9]\d{0,3})[ \t]*$")         # a line that is only a number
ROMAN = re.compile(r"(?m)^[ \t]*([ivxlcdm]{1,7})[ \t]*$", re.I)
WINDOW = 60          # only numbers within ±60 of the anchor: excludes table figures, years, note numbers
AGREEMENT_MIN = 0.70


def blocks(t):
    ms = [(m.start(), m.end(), int(m.group(1))) for m in ANCHOR.finditer(t)]
    for i, (s, e, n) in enumerate(ms):
        yield n, t[e:ms[i + 1][0] if i + 1 < len(ms) else len(t)]


def measure(text: str, window: int = WINDOW) -> dict:
    diffs, evid = collections.Counter(), collections.defaultdict(list)
    n_pages = n_with = n_roman = 0
    for anc, body in blocks(text):
        n_pages += 1
        n_roman += bool(ROMAN.search(body))
        cand = [x for x in (int(v) for v in BARE.findall(body)) if abs(x - anc) <= window]
        if not cand:
            continue
        n_with += 1
        for x in cand:
            diffs[x - anc] += 1
            if len(evid[x - anc]) < 4:
                evid[x - anc].append((anc, x))
    out = {"pages": n_pages, "with_number": n_with, "roman_pages": n_roman, "diffs": diffs, "window": window}
    if diffs:
        top, k = diffs.most_common(1)[0]
        total = sum(diffs.values())
        out.update(mode=top, support=k, total=total, agreement=k / total, evidence=evid[top],
                   others=[(d, c) for d, c in diffs.most_common(5) if d != top])
    return out


WIDE = 5000
WIDE_MIN_SUPPORT = 3


def measure_adaptive(text: str) -> dict:
    """The ±60 window keeps years and table figures out, and it also hides a journal article printed in the
    hundreds (an article that starts at p. 100 has an offset near +99). When the narrow pass finds nothing,
    try once with a wide window and accept it only with high agreement and at least three supporting pages."""
    r = measure(text)
    if r["diffs"]:
        return r
    w = measure(text, WIDE)
    if w["diffs"] and w["agreement"] >= AGREEMENT_MIN and w["support"] >= WIDE_MIN_SUPPORT:
        return w
    return r


def report(name: str, r: dict) -> None:
    print(f"\n■ {name[:72]}")
    if not r["diffs"]:
        print("   🔴 no bare page number near the anchors, and no consistent one further away: this tool is blind on "
              "this file (the running heads may not have survived extraction); check the page images")
        return
    if r["window"] != WINDOW:
        print(f"   ⓘ found only with the wide window (±{r['window']}): typical of an article paginated within its volume")
    print(f"   pages {r['pages']} | pages with a bare number {r['with_number']} | candidates {r['total']}")
    print(f"   modal offset = {r['mode']:+d} (printed = anchor {r['mode']:+d}); support {r['support']}/{r['total']} = {r['agreement']:.0%}")
    print("   evidence: " + " / ".join(f"anchor {a} → printed {b}" for a, b in r["evidence"]))
    if r["others"]:
        print("   ⚠ other offsets: " + "  ".join(f"{d:+d}×{c}" for d, c in r["others"])
              + ("   🔴 agreement below 70%: do not take the mode" if r["agreement"] < AGREEMENT_MIN else ""))
    if r["roman_pages"]:
        print(f"   ⓘ {r['roman_pages']} page(s) carry a roman-numeral line: front matter is numbered separately, "
              "and the body's offset does not apply to it")


def _self_test() -> int:
    def page(n, *lines):
        return f"===== page {n} =====\n" + "\n".join(lines) + "\n"
    constant = "".join(page(n, "Some prose that mentions 1998 and a table value 412.", "", str(n + 12)) for n in range(5, 30))
    segmented = "".join(page(n, "text", str(n + (-4 if n < 20 else 2))) for n in range(5, 35))
    front = page(1, "title page") + page(2, "iv") + page(3, "v") + constant
    blind = "".join(page(n, "running text only") for n in range(1, 10))
    article = "".join(page(n, "an article in volume 105", str(n + 399)) for n in range(1, 16))
    noisy = "".join(page(n, str(1990 + n % 7)) for n in range(1, 16))
    cases = [
        ("article printed from p. 400: found with the wide window", measure_adaptive(article),
         lambda r: r["mode"] == 399 and r["window"] == WIDE),
        ("scattered years far away: still blind, not a fake offset", measure_adaptive(noisy), lambda r: not r["diffs"]),
        ("constant +12", measure(constant), lambda r: r["mode"] == 12 and r["agreement"] == 1.0),
        ("year and table figure are not candidates", measure(constant), lambda r: set(r["diffs"]) == {12}),
        ("two segments: agreement below 70%", measure(segmented), lambda r: r["agreement"] < AGREEMENT_MIN and len(r["others"]) == 1),
        ("roman front matter is flagged", measure(front), lambda r: r["roman_pages"] == 2 and r["mode"] == 12),
        ("no running heads: blind, not zero", measure(blind), lambda r: not r["diffs"]),
    ]
    bad = 0
    for name, r, ok in cases:
        good = ok(r)
        bad += not good
        print(("ok   " if good else "FAIL ") + name)
    print(f"{len(cases) - bad} of {len(cases)} as expected")
    return 1 if bad else 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return _self_test()
    if not args:
        print(__doc__)
        return 2
    rc = 0
    for a in args:
        p = Path(a)
        if not p.is_file():
            print(f"🔴 not found: {a}")
            rc = 2
            continue
        report(p.name, measure_adaptive(p.read_text(encoding="utf-8", errors="replace")))
    return rc


if __name__ == "__main__":
    sys.exit(main())
