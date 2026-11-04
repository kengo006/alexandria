# -*- coding: utf-8 -*-
r"""d4_quote_check.py — are the quotations in the notes really in the source, and can they be found?
(shared/evidence-handbook.md, the text layer locates; obsidian/note-schema.md "Key quotes")

## The case: a "13 of 13 core phrases exactly searchable" result could not be re-run
Nobody had kept the script or the list: the result was recorded, the input was not, so the green light could not
be checked by anyone. A pass that leaves no criterion behind is a record, not a protection.

## What it does
The probes are not invented: they are cut mechanically from each note's own quotation blocks. So it answers two
questions at once:
| question | criterion | meaning |
|---|---|---|
| ① is this quotation really in the source? | found in the work's text layer with whitespace relaxed to \s+ | 🔴 not found = the quotation and the text disagree (a transcription error, an invention, another edition). This is the cell that matters |
| ② is it findable by an exact search? | found with single spaces | information only: a miss is usually a line break inside the phrase, not a defect |
⚠ Only ① is a red light. Treating ② as one would push people to flatten the text layer, which destroys page anchors.

Normalisation is limited to presentation: quotation marks, apostrophes, dashes, ellipses, non-breaking spaces and
accents (the text layer may fold accents; a quotation copied from the page image keeps them, and the two must be
compared under one policy). It never touches the letters, or it could no longer catch a transcription error.

Usage:
  python tools/d4_quote_check.py [--notes notes] [--text-layer text-layer] [name fragment ...]
  python tools/d4_quote_check.py --self-test
A note maps to <text-layer>/<same relative path>.txt (a leading ★ on the note's name is dropped: the text layer
mirrors sources/, which never carries it). The vault map (notes/vault-map.md) and each folder's MOC are not
literature notes: they are set aside, and the count is printed.
Exit codes: 0 = every probe found / 1 = some not found (a reading list, not a verdict) / 2 = nothing was checked
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MIN_WORDS = 6        # shorter phrases do not discriminate ("of the" is everywhere)
MAX_WORDS = 14       # longer ones cross lines more often, and one transcription slip fails the whole probe
CJK = re.compile(f"[{chr(0x4E00)}-{chr(0x9FFF)}]")
FW_SLASH = chr(0xFF0F)
_PUNCT = {chr(0x2018): "'", chr(0x2019): "'", chr(0x201B): "'",          # curly single quotes / apostrophe
          chr(0x201C): '"', chr(0x201D): '"', chr(0x201F): '"',          # curly double quotes
          chr(0x2013): "-", chr(0x2014): "-", chr(0x2015): "-", chr(0x2212): "-",   # dashes, minus
          chr(0x00A0): " ", chr(0x202F): " ", chr(0x2007): " ",          # non-breaking spaces
          chr(0x2026): "..."}
OPEN_Q = '"' + chr(0x201C) + chr(0x00AB)
CLOSE_Q = '"' + chr(0x201D) + chr(0x00BB)


def norm_punct(s: str) -> str:
    for k, v in _PUNCT.items():
        s = s.replace(k, v)
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def strip_md(s: str) -> str:
    s = re.sub(r"^\s*>+\s?", "", s, flags=re.M)          # line by line; a second guard in _usable catches leftovers
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s, flags=re.S)
    return s.replace("[", "").replace("]", "")


def quote_blocks(text: str):
    """Blockquote runs, plus numbered or bulleted lines that open with a quotation mark.
    Blockquotes alone were not enough: a common note layout lists its key quotes as `1. "…" (p. 3)`, and a note
    reported zero probes. A gate whose domain is written too narrow is quiet, and quiet looks like clean. Callouts
    (`> [!note]`) are not quotations."""
    out, cur = [], []
    for ln in text.splitlines():
        if re.match(rf"^\s*(?:\d+\.|[-*])\s+[{re.escape(OPEN_Q)}]", ln):
            out.append(ln)
    for ln in text.splitlines():
        if ln.startswith(">"):
            if re.match(r">\s*\[!", ln):
                if cur:
                    out.append("\n".join(cur))
                    cur = []
                continue
            cur.append(ln)
        elif cur:
            out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return [b for b in out if any(q in b for q in OPEN_Q)]       # French guillemets count too


def _usable(seg: str) -> bool:
    """Can this segment be a probe? A first full run reported 75% found, and most failures were this function's:
    an ellipsis marks omitted words (not source characters); a leftover `>` from merged lines; a note's own
    annotation in quotation marks; a page reference. A new gate's first output is a reading list, not a verdict."""
    if "..." in seg:
        return False
    if ">" in seg or "|" in seg or FW_SLASH in seg or chr(0x00B7) in seg:
        return False
    if CJK.search(seg):
        return False
    if re.search(r"\bp\.\s*\d", seg):
        return False
    return sum(c.isalpha() for c in seg) >= len(seg) * 0.6


def probes(block: str):
    """Up to three non-overlapping phrases (start, middle, end) from inside the quotation marks."""
    t = norm_punct(re.sub(r"\s+", " ", strip_md(block)).strip())
    res = []
    for m in re.finditer(r'["' + chr(0x00AB) + r']([^"' + chr(0x00BB) + r']{40,})["' + chr(0x00BB) + r']', t):
        words = m.group(1).split()
        for start in (0, len(words) // 2, max(0, len(words) - MAX_WORDS)):
            seg = words[start:start + MAX_WORDS]
            if len(seg) >= MIN_WORDS and _usable(" ".join(seg)):
                res.append(" ".join(seg))
    return list(dict.fromkeys(res))[:3]


def probe_rx(ph: str) -> str:
    """Words joined by \\s+; edge punctuation stripped from the first and last word only (the probe's edges are
    where this tool cut, not where the quotation ends: a sentence-final full stop inside the note is not evidence).
    A leading bare number (a marginal paragraph number copied with the quote) is dropped. Inside the phrase,
    punctuation is compared strictly. Three probes per quotation, so one bad edge (an editorial insertion in
    brackets) cannot fail the whole quotation."""
    ws = ph.split()
    if not ws:
        return re.escape(ph)
    ws[0] = re.sub(r"^[^\w]+", "", ws[0])
    ws[-1] = re.sub(r"[^\w]+$", "", ws[-1])
    ws = [w for w in ws if w]
    while ws and ws[0].isdigit():
        ws.pop(0)
    if ws:
        ws[0] = re.sub(r"^[^\w]+", "", ws[0])          # the new first word gets the same edge treatment
    return r"\s+".join(re.escape(w) for w in ws if w)


def text_for(note: Path, notes: Path, layer: Path):
    rel = note.relative_to(notes)
    p = layer / rel.parent / (rel.name.lstrip("★").rsplit(".", 1)[0] + ".txt")
    return p if p.exists() else None


def literature_notes(notes: Path):
    """The notes to scan, and the files set aside: the vault map at the root and each folder's MOC (named after its
    folder, as governance/scripts/vault_verify.py counts them), and anything under a folder starting with _ or '.'.
    The map and the MOCs have no text layer by design; listed as 'without a text layer' they buried the notes that
    really lack one."""
    keep, nav, hidden = [], 0, 0
    for p in notes.rglob("*.md"):
        rel = p.relative_to(notes)
        if any(x.startswith(("_", ".")) for x in rel.parts):
            hidden += 1
        elif rel.as_posix() == "vault-map.md" or p.stem == p.parent.name:
            nav += 1
        else:
            keep.append(p)
    return keep, nav, hidden


def run(notes: Path, layer: Path, frags=()):
    files, nav, hidden = literature_notes(notes)
    if frags:
        files = [p for p in files if any(f.lower() in p.name.lower() for f in frags)]
    if not files:
        print(f"❌ no note matched {list(frags)}: that is 'not scanned', not 'clean'")
        return 2, None
    n_probe = n_loose = n_exact = 0
    missing, no_text = [], []
    for note in sorted(files):
        c = text_for(note, notes, layer)
        if c is None:
            no_text.append(note.name)
            continue
        txt = norm_punct(c.read_text(encoding="utf-8", errors="replace"))
        for blk in quote_blocks(note.read_text(encoding="utf-8", errors="replace")):
            for ph in probes(blk):
                n_probe += 1
                rx = probe_rx(ph)
                if re.search(rx, txt):
                    n_loose += 1
                    n_exact += bool(re.search(rx.replace(r"\s+", " "), txt))
                else:
                    missing.append((note.name, ph))
    print(f"=== quotation check · {len(files)} notes · {n_probe} probes  (set aside: vault map and MOCs {nav}, "
          f"under _ or . folders {hidden})")
    if not n_probe:
        print("🔴 zero probes: this run checked nothing and is not a pass (no quotation blocks? the extractor broken?)")
        return 2, (n_probe, n_loose, n_exact, missing, no_text)
    print(f"    ① present (whitespace relaxed): {n_loose}/{n_probe} = {n_loose / n_probe:.1%}   "
          + ("✅" if n_loose == n_probe else "🔴 some quotations are not in the text layer"))
    print(f"    ② exact: {n_exact}/{n_probe} = {n_exact / n_probe:.1%}   (the gap is line breaks, not a red light)")
    if no_text:
        print(f"    ⚠ {len(no_text)} note(s) without a text layer (web-native or not extracted):")
        for f in no_text:
            print(f"      - {f}")
    if missing:
        print(f"\n🔴 these {len(missing)} are a reading list, not a verdict. Known false positives: a quoted title (not body"
              " text); a web snapshot that is not the stored copy; two passages joined with the gap unmarked. Open each.")
        for f, ph in missing:                       # all of them: a cut list hides the ones past the cut
            print(f"    · {f}\n        not found: {ph}")
    return (1 if missing else 0), (n_probe, n_loose, n_exact, missing, no_text)


def _self_test() -> int:
    import tempfile, shutil, io, contextlib
    checks = []
    b = '> "Sometimes it is **epistemically** beneficial to form a belief on authority.\n> When you do, what happens?"'
    pr = probes(quote_blocks(b)[0])
    checks.append(("blockquote extracted, markdown removed", bool(pr) and "epistemically beneficial" in pr[0] and "**" not in pr[0]))
    checks.append(("a callout is not a quotation", quote_blocks('> [!danger] a callout "with quotes"') == []))
    guil = chr(0x00AB) + " La volont" + chr(0x00E9) + " de savoir n'est pas une facult" + chr(0x00E9) + " permanente de l'esprit humain " + chr(0x00BB)
    checks.append(("numbered line with guillemets is a quotation", len(quote_blocks("1. " + guil + " (p. 3)")) == 1))
    checks.append(("an ellipsis makes a segment unusable", not _usable("the docile body ... subjected and used")))
    checks.append(("edge punctuation and a leading paragraph number are dropped",
                   probe_rx('1 "weaknesses and vulnerabilities.') == r"weaknesses\s+and\s+vulnerabilities"))
    tmp = Path(tempfile.mkdtemp())
    (tmp / "notes" / "m").mkdir(parents=True)
    (tmp / "text-layer" / "m").mkdir(parents=True)
    (tmp / "text-layer" / "m" / "Doe_2011_Monuments.txt").write_text(
        "===== page 4 =====\nPublic memory is not stored in monuments; it is produced\nby the practices that gather around them, "
        "and it changes when they do.\n===== page 5 =====\nLa volont" + chr(0x00E9) + " de savoir n" + chr(0x2019) + "est pas une "
        "facult" + chr(0x00E9) + " permanente de l" + chr(0x2019) + "esprit humain.\n", encoding="utf-8")
    (tmp / "notes" / "m" / "★Doe_2011_Monuments.md").write_text(
        '## Key quotes\n> "Public memory is not stored in monuments; it is produced by the practices that gather around them, '
        'and it changes when they do." (p. 4)\n\n1. ' + guil + ' (p. 5)\n\n'
        '> "Memory is a warehouse in which every object keeps its original meaning for ever and ever." (p. 9)\n', encoding="utf-8")
    (tmp / "notes" / "vault-map.md").write_text('## Taxonomy\n> "A map quotes nothing from a source, and has no text layer."\n', encoding="utf-8")
    (tmp / "notes" / "m" / "m.md").write_text("# m\n- [[★Doe_2011_Monuments]]\n", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        code, r = run(tmp / "notes", tmp / "text-layer")
    n_probe, n_loose, n_exact, missing, no_text = r
    checks.append(("starred note maps to its text layer", "★Doe_2011_Monuments.md" not in no_text))
    checks.append(("vault map and MOC set aside and counted, not 'without a text layer'",
                   not no_text and "vault map and MOCs 2" in buf.getvalue()))
    checks.append(("present across a line break, not exact", n_loose > n_exact))
    checks.append(("curly apostrophe and accents compared under one policy", all("volont" not in ph for _, ph in missing)))
    checks.append(("an invented quotation is not found (exit 1)", code == 1 and any("warehouse" in ph for _, ph in missing)))
    (tmp / "notes" / "m" / "Empty_2020_None.md").write_text("no quotations here", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        code2, _ = run(tmp / "notes", tmp / "text-layer", ["Empty_2020"])
    checks.append(("zero probes is not a pass (exit 2)", code2 == 2))
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

    def opt(k, d):
        return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d
    skip = {opt("--notes", None), opt("--text-layer", None)}
    frags = [x for x in a if not x.startswith("--") and x not in skip]
    code, _ = run(Path(opt("--notes", "notes")), Path(opt("--text-layer", "text-layer")), frags)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
