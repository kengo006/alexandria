# -*- coding: utf-8 -*-
"""Vault-wide wikilink integrity scan: dead links + wrong-path links.

Usage:  python dead_link_scan.py [vault_notes_root]
Output: file count / link count / dead links (target basename doesn't exist)
        / wrong-path links (file exists elsewhere: Obsidian still resolves by
        basename, but the recorded path is stale — technical debt that breaks
        on the next move).

Configure NOTES_ROOT and EXCLUDE below, or pass the root as argv[1].
"""
import re
import sys
from pathlib import Path

# ── config ──────────────────────────────────────────────────────────
NOTES_ROOT = Path("notes")                     # your vault's notes root
EXCLUDE = ("_trash", ".obsidian", ".smart-env")  # substrings of paths to skip
SHOW_MAX = 80                                  # max findings printed per class
# ────────────────────────────────────────────────────────────────────

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else NOTES_ROOT
if not ROOT.is_dir():
    sys.exit(f"notes root not found: {ROOT}")

def skip(p: str) -> bool:
    return any(x in p for x in EXCLUDE)

existing_full, existing_basename = set(), {}
for md in ROOT.rglob("*.md"):
    if skip(str(md)):
        continue
    rel = md.relative_to(ROOT).as_posix().removesuffix(".md")
    existing_full.add(rel)
    existing_basename.setdefault(md.stem, []).append(rel)

# Handles [[target]], [[target|alias]], [[target\|alias]] (table-escaped), [[target#heading]]
LINK_RE = re.compile(r"\[\[([^\[\]\|#\\]+?)(?:#[^\[\]\|]+)?(?:\\?\|[^\[\]]+?)?\]\]")

dead, wrong, total = [], [], 0
for md in ROOT.rglob("*.md"):
    if skip(str(md)):
        continue
    content = md.read_text(encoding="utf-8")
    src = md.relative_to(ROOT).as_posix()
    for m in LINK_RE.finditer(content):
        target = m.group(1).strip().replace("\\", "/").removesuffix(".md")
        bn = target.rsplit("/", 1)[-1]
        total += 1
        if bn not in existing_basename:
            dead.append((src, target))
        elif "/" in target and target not in existing_full:
            wrong.append((src, target, existing_basename[bn]))

print(f"files scanned:            {len(existing_full)}")
print(f"wikilinks total:          {total}")
print(f"dead (target missing):    {len(dead)}")
print(f"wrong-path (found elsewhere): {len(wrong)}")
if dead:
    print("\n--- dead links ---")
    for s, t in dead[:SHOW_MAX]:
        print(f"  [{s}] -> [[{t}]]")
if wrong:
    print("\n--- wrong-path links ---")
    for s, t, actual in wrong[:SHOW_MAX]:
        print(f"  [{s}] -> [[{t}]]  (actually at: {actual})")
sys.exit(1 if (dead or wrong) else 0)
