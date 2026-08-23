# -*- coding: utf-8 -*-
"""System health check — mechanises the sync matrix (see ../sync-matrix.md).

Four checks, three-part output (pass / warn / fail):
  1. required files present (roles, shared methods, obsidian layer)
  2. forbidden patterns absent from live files (e.g. a banned fallback creeping back,
     or an abolished mechanism still being taught somewhere)
  3. (optional) version mirrors consistent — if you version your files, list the
     source-of-truth header and every location that mirrors it
  4. (optional) the version in a file's header also appears in that file's own
     changelog section — check 3's sibling, and the one it cannot substitute for

Run at logical boundaries (after upgrades, before releases). Delegates link and
structure checks to dead_link_scan.py / vault_verify.py.
"""
import re
import sys
from pathlib import Path

# ── config ──────────────────────────────────────────────────────────
SKELETON = Path(__file__).resolve().parents[2]   # repo root

REQUIRED = [
    "README.md", "GETTING-STARTED.md",
    "roles/librarian.md", "roles/writer.md", "roles/searcher.md",
    "roles/critic.md", "roles/researcher.md", "roles/deep-reader.md",
    "shared/report-mode.md", "shared/council-mode.md", "shared/scholar-evaluation.md",
    "shared/correction-report.md", "shared/search-patterns.md",
    "shared/naming-conventions.md", "shared/summon-templates.md",
    "shared/page-offset-registry.md",
    "obsidian/vault-structure.md", "obsidian/note-schema.md",
    "obsidian/wikilinks-and-mocs.md", "obsidian/vault-map-template.md",
    "governance/system-overview.md", "governance/role-division.md",
    "governance/sync-matrix.md", "governance/claims-and-evidence.md",
]

# pattern -> why it is banned (checked case-insensitively in all live .md files;
# lines mentioning the ban itself are tolerated via the allow marker)
FORBIDDEN = {
    r"reconstruct(ed|ing)? from (general|scholarly) knowledge":
        "the banned fallback — fabrication's historical root cause",
    r"wear(ing)? the (sceptic|critic|assessor)'?s? hat":
        "abolished self-played review (council mode uses independent seats)",
}
ALLOW_MARKERS = ("banned", "abolished", "ban on")   # a line containing the pattern AND one of these is the ban's own documentation
# ("ban on" added after the gate flagged the README's own sentence about the ban — the marker
#  list was narrower than the idiom actually used to document it. Keep markers narrow: a bare
#  "ban" would also match "urban".)

# optional: {"source_file": (header_regex, [("mirror_file", mirror_regex), ...])}
# If you version a file in two places (front-matter field AND the H1 title), mirror BOTH
# here. In production a title version once drifted nine releases behind the front matter
# while the gate stayed green — it was only comparing the one place it knew about.
VERSION_MIRRORS = {}

# optional: {"file": (header_regex, changelog_heading_regex)}
# Check 3 asks whether the version number was copied everywhere. This asks whether the
# change was *recorded* — a different question, and the one that failed. Measured while
# preparing v3.6: of seven canonical rule files upstream, four carried a header version
# that appeared nowhere in their own changelog — eighteen unrecorded rule changes, the
# worst file thirteen of them — with every version mirror green the whole time.
# (Eighteen is a count. The first figure written here was nineteen, from subtracting one
#  version number from another; one number in that span had never been issued.)
# ⚠ Range: this finds a header version missing from the log. It does NOT find a gap in
# the middle of the log (v5 and v3 present, v4 never written) — that needs a different
# check, and this one passing says nothing about it.
CHANGELOG_PRESENT = {}
# ────────────────────────────────────────────────────────────────────

ok, warn, fail = [], [], []

# 1. required files
missing = [f for f in REQUIRED if not (SKELETON / f).is_file()]
if missing:
    fail.append(f"missing required files: {missing}")
else:
    ok.append(f"required files present ({len(REQUIRED)})")

# 2. forbidden patterns
# A passing scan reports its denominator ("across N files"): "0 hits" alone cannot be
# told apart from "the scan saw nothing" — checks die most often by passing over an
# empty sample (see governance/claims-and-evidence.md §5).
hits = []
scanned = 0
for md in SKELETON.rglob("*.md"):
    rel = md.relative_to(SKELETON).as_posix()
    if rel.startswith((".git", "_")):
        continue
    scanned += 1
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        for pat, why in FORBIDDEN.items():
            if re.search(pat, line, re.I) and not any(a in line.lower() for a in ALLOW_MARKERS):
                hits.append(f"{rel}:{i}  [{why}]")
if scanned == 0:
    fail.append("forbidden-pattern scan saw zero files — empty sample; a green over nothing is not green")
elif hits:
    fail.append("forbidden patterns found:\n     " + "\n     ".join(hits[:10]))
else:
    ok.append(f"forbidden-pattern scan clean ({len(FORBIDDEN)} patterns across {scanned} files)")

# 3. version mirrors (if configured)
for src, (src_re, mirrors) in VERSION_MIRRORS.items():
    m = re.search(src_re, (SKELETON / src).read_text(encoding="utf-8"))
    if not m:
        fail.append(f"{src}: version header not found")
        continue
    v = m.group(1)
    bad = False
    for mf, mre in mirrors:
        mm = re.search(mre, (SKELETON / mf).read_text(encoding="utf-8"))
        if not mm or mm.group(1) != v:
            fail.append(f"{src} v{v} != mirror {mf} ({mm.group(1) if mm else 'not found'})")
            bad = True
    if not bad:
        ok.append(f"{src} v{v}: mirrors consistent")

# 4. changelog carries an entry for the current version (if configured)
for f, (head_re, log_re) in CHANGELOG_PRESENT.items():
    text = (SKELETON / f).read_text(encoding="utf-8")
    m = re.search(head_re, text)
    if not m:
        fail.append(f"{f}: version header not found (pattern {head_re!r})")
        continue
    v = m.group(1)
    lm = re.search(log_re, text)
    if not lm:
        fail.append(f"{f}: changelog section not found (pattern {log_re!r})")
        continue
    # only the changelog section counts — the header itself must not satisfy its own check
    if v in text[lm.end():]:
        ok.append(f"{f} v{v}: recorded in its changelog")
    else:
        warn.append(f"{f}: header says v{v}, and v{v} appears nowhere in its changelog "
                    f"— the number was mirrored, the change was not written down")

print("=== health check ===")
for x in ok:   print(f"  PASS  {x}")
for x in warn: print(f"  WARN  {x}")
for x in fail: print(f"  FAIL  {x}")
print(f"result: {len(ok)} pass / {len(warn)} warn / {len(fail)} fail")
print("(links & vault structure: run dead_link_scan.py / vault_verify.py)")
sys.exit(1 if fail else 0)
