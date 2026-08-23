# -*- coding: utf-8 -*-
"""Link integrity, in two passes.

Usage:  python dead_link_scan.py [vault_notes_root]

  1. **Document links** — the `[text](relative/path)` links inside this repository's
     own `.md` files. Always runs; needs nothing but the repo.
  2. **Wikilinks** — `[[target]]` integrity across a vault's notes tree. Runs when a
     notes root is supplied or found, and is reported as *not run* otherwise.

⚠ **"Not run" and "ran and found nothing" must not print the same thing.** Until v3.8
this script did only pass 2, and on a checkout with no vault it exited with
`notes root not found` and a failure status — which reads as *your links are broken*
when it means *I had nothing to look at*. Meanwhile the repository's own 23 document
links had never been checked by anything. 🔑 A tool whose whole subject is broken
references spent seven releases unable to see the references in the tree it shipped in.

Output per pass: what was scanned (the denominator), then findings. A pass with an
empty denominator says so and does not count as green — same rule as `health_check.py`.
"""
import re
import sys
from pathlib import Path

# ── config ──────────────────────────────────────────────────────────
NOTES_ROOT = Path("notes")                       # your vault's notes root
DOC_ROOT = Path(__file__).resolve().parents[2]   # this repository
EXCLUDE = ("_trash", ".obsidian", ".smart-env", ".git")
SHOW_MAX = 80
# ────────────────────────────────────────────────────────────────────


def skip(p: str) -> bool:
    return any(x in p for x in EXCLUDE)


fail = False

# ── pass 1: document links (always runs) ────────────────────────────
# [text](target) — skip absolute URLs, mail, and pure anchors.
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Markdown inside a code span or fence is not a link — it is documentation *about*
# links, and this repository writes plenty of it. Strip both before matching, or the
# scanner reports its own changelog for explaining what a link looks like. (v3.8: it did.)
FENCE = re.compile(r"(?ms)^```.*?^```")
CODESPAN = re.compile(r"`[^`]*`")


def strip_code(text: str) -> str:
    return CODESPAN.sub("", FENCE.sub("", text))


docs = [p for p in sorted(DOC_ROOT.rglob("*.md")) if not skip(str(p))]
doc_dead, doc_total = [], 0
for md in docs:
    src = md.relative_to(DOC_ROOT).as_posix()
    for m in MD_LINK.finditer(strip_code(md.read_text(encoding="utf-8"))):
        target = m.group(2).split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        doc_total += 1
        if not (md.parent / target).resolve().exists():
            doc_dead.append((src, m.group(1)[:40], target))

print("=== document links ===")
if not docs:
    print("  🔴 no .md files found under %s — empty sample, not a pass" % DOC_ROOT)
    fail = True
else:
    print("  files scanned:        %d" % len(docs))
    print("  relative links:       %d" % doc_total)
    print("  dead:                 %d" % len(doc_dead))
    if doc_total == 0:
        print("  ⚠ zero links found across %d files — check the pattern before trusting this" % len(docs))
    for s, txt, t in doc_dead[:SHOW_MAX]:
        print("    🔴 [%s] -> [%s](%s)" % (s, txt, t))
    fail = fail or bool(doc_dead)

# ── pass 2: vault wikilinks (runs only if there is a vault) ─────────
root = Path(sys.argv[1]) if len(sys.argv) > 1 else NOTES_ROOT
print("")
print("=== vault wikilinks ===")
if not root.is_dir():
    print("  ⏭ not run — no notes root at '%s'." % root)
    print("     Pass one as an argument, or edit NOTES_ROOT. This is *not* a finding:")
    print("     nothing was examined, so nothing is being asserted about your vault.")
else:
    existing_full, existing_basename = set(), {}
    for md in root.rglob("*.md"):
        if skip(str(md)):
            continue
        rel = md.relative_to(root).as_posix().removesuffix(".md")
        existing_full.add(rel)
        existing_basename.setdefault(md.stem, []).append(rel)

    # Handles [[target]], [[target|alias]], [[target\|alias]] (table-escaped), [[target#heading]]
    LINK_RE = re.compile(r"\[\[([^\[\]\|#\\]+?)(?:#[^\[\]\|]+)?(?:\\?\|[^\[\]]+?)?\]\]")
    dead, wrong, total = [], [], 0
    for md in root.rglob("*.md"):
        if skip(str(md)):
            continue
        content = md.read_text(encoding="utf-8")
        src = md.relative_to(root).as_posix()
        for m in LINK_RE.finditer(content):
            target = m.group(1).strip().replace("\\", "/").removesuffix(".md")
            bn = target.rsplit("/", 1)[-1]
            total += 1
            if bn not in existing_basename:
                dead.append((src, target))
            elif "/" in target and target not in existing_full:
                wrong.append((src, target, existing_basename[bn]))

    print("  files scanned:            %d" % len(existing_full))
    print("  wikilinks total:          %d" % total)
    print("  dead (target missing):    %d" % len(dead))
    print("  wrong-path (found elsewhere): %d" % len(wrong))
    if len(existing_full) == 0:
        print("  🔴 zero notes under the given root — empty sample, not a pass")
        fail = True
    if dead:
        print("  --- dead links ---")
        for s, t in dead[:SHOW_MAX]:
            print("    🔴 [%s] -> [[%s]]" % (s, t))
    if wrong:
        print("  --- wrong-path links ---")
        for s, t, actual in wrong[:SHOW_MAX]:
            print("    ⚠ [%s] -> [[%s]]  (actually at: %s)" % (s, t, actual))
    fail = fail or bool(dead or wrong)

print("")
print("result: %s" % ("🔴 findings above" if fail else "✅ no findings"))
sys.exit(1 if fail else 0)
