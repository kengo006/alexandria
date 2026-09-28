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


def self_test() -> int:
    """Prove the matcher discriminates, without trusting anyone's word for it.

    Builds fixtures in a temp directory (document links for pass 1, wikilinks for
    pass 2) and asserts the matcher's verdict on each. Run it with --self-test; it
    touches nothing outside the temp directory.

    ⚠ Range, stated because a green self-test invites the wrong conclusion: this
    shows the matcher separates the cases *it was shown*. It says nothing about
    link forms nobody thought to write down here — reference-style links, HTML
    anchors, links split across a line. A passing self-test is evidence about the
    cases below and about nothing else. (Until v4.0 it covered pass 1 only, so the
    wikilink pattern had no test at all — which is how the double-escaped alias pipe
    stayed invisible; see LINK_RE.)
    """
    import tempfile
    nl = chr(10)
    cases = [
        ("doc",  "live link",              "[ok](target.md)",              False),
        ("doc",  "dead link",              "[bad](missing.md)",            True),
        ("doc",  "dead link in code span", "`[bad](missing.md)`",          False),
        ("doc",  "dead link in a fence",   "```" + nl + "[bad](missing.md)" + nl + "```", False),
        ("wiki", "wikilink, live",         "[[target]]",                   False),
        ("wiki", "wikilink, dead",         "[[missing]]",                  True),
        ("wiki", "dead, alias escaped once",  "| [[missing\\|alias]] |",   True),
        ("wiki", "dead, alias escaped twice", "| [[missing\\\\|alias]] |", True),
    ]
    tmp = Path(tempfile.mkdtemp(prefix="dls_selftest_"))
    (tmp / "target.md").write_text("x", encoding="utf-8")
    bad = 0
    print("=== self-test ===")
    for kind, name, body, should_flag in cases:
        p = tmp / "case.md"
        p.write_text(body, encoding="utf-8")
        text = p.read_text(encoding="utf-8")
        flagged = False
        if kind == "doc":
            for m in MD_LINK.finditer(strip_code(text)):
                tgt = m.group(2).split("#")[0].strip()
                if tgt and not tgt.startswith(("http://", "https://", "mailto:", "#")):
                    flagged = flagged or not (p.parent / tgt).resolve().exists()
        else:
            for tgt in wikilink_targets(text):
                flagged = flagged or not (tmp / (tgt.rsplit("/", 1)[-1] + ".md")).exists()
        ok = flagged == should_flag
        bad += 0 if ok else 1
        print("  %-27s expected flag=%-5s got=%-5s %s"
              % (name, should_flag, flagged, "OK" if ok else "FAIL"))
    print("  --")
    print("  %s" % ("all %d as expected" % len(cases) if not bad else "%d of %d wrong" % (bad, len(cases))))
    print("  Range: proves separation on these %d cases only. Link forms not" % len(cases))
    print("  represented here are untested, and their absence is not evidence.")
    return 1 if bad else 0


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


# ── wikilink pattern (pass 2; module level so the self-test exercises the real one) ──
# Handles [[target]], [[target|alias]], [[target#heading]], and a table-escaped alias pipe.
# 🔴 A wikilink written inside a Markdown table must escape its alias pipe, as `\|`, and
#    Obsidian often writes it as `\\|`. Until v4.0 the alias branch allowed at most one
#    backslash while the target class excludes backslashes, so `[[target\\|alias]]` did not
#    match at all: the link was invisible to this scan, dead or alive. Upstream found it by
#    reconciling two independent link counts that disagreed by ten; all ten targets happened
#    to exist, which was luck and not a guarantee. 🔑 Two green reports need not be looking
#    at the same set of links.
LINK_RE = re.compile(r"\[\[([^\[\]\|#\\]+?)(?:#[^\[\]\|]+)?(?:\\{0,2}\|[^\[\]]+?)?\]\]")


def wikilink_targets(content: str):
    for m in LINK_RE.finditer(content):
        yield m.group(1).strip().replace("\\", "/").removesuffix(".md")


if "--self-test" in sys.argv:
    sys.exit(self_test())


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

    # LINK_RE and wikilink_targets() are defined at module level (see above).
    dead, wrong, total = [], [], 0
    for md in root.rglob("*.md"):
        if skip(str(md)):
            continue
        content = md.read_text(encoding="utf-8")
        src = md.relative_to(root).as_posix()
        for target in wikilink_targets(content):
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
