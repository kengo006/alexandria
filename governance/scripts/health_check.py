# -*- coding: utf-8 -*-
"""System health check — mechanises the sync matrix (see ../sync-matrix.md).

Three checks, three-part output (pass / warn / fail):
  1. required files present (roles, shared methods, obsidian layer)
  2. forbidden patterns absent from live files (e.g. a banned fallback creeping back,
     or an abolished mechanism still being taught somewhere)
  3. (optional) version mirrors consistent — if you version your files, list the
     source-of-truth header and every location that mirrors it

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
    "roles/critic.md", "roles/researcher.md",
    "shared/report-mode.md", "shared/council-mode.md", "shared/scholar-evaluation.md",
    "shared/correction-report.md", "shared/search-patterns.md",
    "shared/naming-conventions.md", "shared/summon-templates.md",
    "obsidian/vault-structure.md", "obsidian/note-schema.md",
    "obsidian/wikilinks-and-mocs.md", "obsidian/vault-map-template.md",
    "governance/system-overview.md", "governance/role-division.md",
    "governance/sync-matrix.md",
]

# pattern -> why it is banned (checked case-insensitively in all live .md files;
# lines mentioning the ban itself are tolerated via the allow marker)
FORBIDDEN = {
    r"reconstruct(ed|ing)? from (general|scholarly) knowledge":
        "the banned fallback — fabrication's historical root cause",
    r"wear(ing)? the (sceptic|critic|assessor)'?s? hat":
        "abolished self-played review (council mode uses independent seats)",
}
ALLOW_MARKERS = ("banned", "abolished")   # a line containing the pattern AND one of these words is the ban's own documentation

# optional: {"source_file": (header_regex, [("mirror_file", mirror_regex), ...])}
VERSION_MIRRORS = {}
# ────────────────────────────────────────────────────────────────────

ok, warn, fail = [], [], []

# 1. required files
missing = [f for f in REQUIRED if not (SKELETON / f).is_file()]
if missing:
    fail.append(f"missing required files: {missing}")
else:
    ok.append(f"required files present ({len(REQUIRED)})")

# 2. forbidden patterns
hits = []
for md in SKELETON.rglob("*.md"):
    rel = md.relative_to(SKELETON).as_posix()
    if rel.startswith((".git", "_")):
        continue
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        for pat, why in FORBIDDEN.items():
            if re.search(pat, line, re.I) and not any(a in line.lower() for a in ALLOW_MARKERS):
                hits.append(f"{rel}:{i}  [{why}]")
if hits:
    fail.append("forbidden patterns found:\n     " + "\n     ".join(hits[:10]))
else:
    ok.append(f"forbidden-pattern scan clean ({len(FORBIDDEN)} patterns)")

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

print("=== health check ===")
for x in ok:   print(f"  PASS  {x}")
for x in warn: print(f"  WARN  {x}")
for x in fail: print(f"  FAIL  {x}")
print(f"result: {len(ok)} pass / {len(warn)} warn / {len(fail)} fail")
print("(links & vault structure: run dead_link_scan.py / vault_verify.py)")
sys.exit(1 if fail else 0)
