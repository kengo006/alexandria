# Vault structure: the two-end mirror

The vault's load-bearing idea: **notes and sources are two ends of one structure.** Every literature note has a source; every source is reachable from a note; both live in matching folder trees.

```
your-vault/
├── notes/                 ← literature notes (.md), the Obsidian root
│   ├── <topic>/…          ← your taxonomy (see vault-map-template.md)
│   └── <topic>/<topic>.md ← one MOC per folder (see wikilinks-and-mocs.md)
├── sources/               ← PDFs, mirroring notes/ folder-for-folder
├── text-layer/            ← extracted text mirroring sources/ (optional tier; git-ignored)
└── _trash/                ← single top-level deletion zone (never permanently delete)
```

## Naming rule (iron)

`Author_Year_Title.{pdf,md}` — underscores separate exactly three segments; spaces inside the title.
- Multiple authors: two → `A & B`; three+ → `et al.`
- Year = the **real scholarly publication year** (print over preprint, journal over online-first). When a filename must keep a different year (a lecture year, a preprint year), record the discrepancy in the note's metadata (`year_note`) so searches by either year hit.
- Classical works: era-appropriate years (e.g. `399BCE` in filenames), translation edition recorded in the note.

## The star convention

A leading `★` on the **note filename only** (never the PDF) marks works directly load-bearing for the current project. Renaming a note to add/remove the star is a rename like any other — the chain below applies.

## Rename chain (every rename synchronises all of these)

Renaming one work touches, in one pass:

1. the PDF filename
2. the note filename
3. the note's YAML year field
4. the note's heading (`# Author (Year): Title`)
5. the note's citation line
6. the MOC entries pointing at it
7. every inbound wikilink from other notes (build an old→new mapping; batch-replace; re-scan)
8. the text-layer file (rename with it; re-extract if the PDF itself changed)
9. any conditional mirrors your project keeps (e.g. a submission folder's PDF copies)

Missing any one produces dead links, a stale text layer, or an orphaned mirror. **Before renaming**: glob both ends for the target name — same work already there → confirm with the human; same author, different work → disambiguate with the subtitle; never let a move silently overwrite.

## Mechanical verification

Two scripts (in `governance/scripts/`), run after any large operation and at logical boundaries:

- **`vault_verify.py`** — counts both ends; flags legacy-format remnants; checks every note's category field against its actual folder; checks filename year vs metadata year (respecting `year_note` exemptions); checks two-end filename alignment (star stripped). Listed ≠ wrong: known exemptions (companion translations, web-native sources) are judged by a human.
- **`dead_link_scan.py`** — full-vault wikilink integrity: dead targets and wrong-path-but-resolvable links (see `wikilinks-and-mocs.md`).

## Deletion policy

Deletions are **moves** into `_trash/`, preserving the relative path (`_trash/notes/<topic>/X.md`) so anything can be restored. The zone sits outside the Obsidian root: deleted notes disappear from graph and search, and the verification scripts skip it. Nothing is ever permanently deleted by an agent; emptying the trash is a human decision.
