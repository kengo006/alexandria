# Wikilinks and MOCs

The graph is a map only if links resolve. Every dead-link incident in the upstream system traced to one root cause: **constructing a wikilink from memory or inference instead of from the filesystem.**

## How links die

| Error | Example | Why it dies |
|---|---|---|
| Star prefix dropped | `[[Doe_2019_…]]` but the file is `★Doe_2019_…` | basename mismatch |
| Folder inferred wrongly | filed under a sibling subfolder | path mismatch |
| Root prefix doubled | `[[notes/topic/…]]` from inside the root that *is* `notes/` | resolves to `notes/notes/…` |
| Link invented from memory | target never existed | nothing to resolve |
| Author/year misremembered | `[[Doe_2019_…]]` but the file says `Doe et al._2020_…` | both ends differ |

## The four-step discipline (every time a note gains links)

1. **Glob first.** List the actual files in the target folders before writing a single link.
2. **Copy, never construct.** Take filenames verbatim from the glob output — stars, `et al.`, years, underscores, spaces, full folder path.
3. **Scan immediately.** Run the dead-link scanner after writing.
4. **Fix before reporting.** Dead or wrong-path count > 0 → repair, re-scan, then report.

## Three link formats (any replacement tooling must cover all three)

1. `[[path|alias]]` — standard
2. `[[path\|alias]]` — pipe escaped inside tables
3. `[[path]]` — bare

A scanner or replacer tested only on format 1 will corrupt MOC tables. **In prose**, never use bare-basename shorthand links; use plain text ("Doe (2019)") or the full-path link with alias.

## Scanner notes (for whoever maintains `dead_link_scan.py`)

- Obsidian resolves by **basename**: a wrong-path link that happens to share a basename still resolves — count it as `wrong-path` anyway; it is technical debt that breaks on the next move.
- Exclude the trash zone, tool caches, and any cloud-sync phantom directories.
- **Independent verification**: link reports arriving from outside the canonical scanner (other sessions, ad-hoc regexes, a Searcher's side note) have produced confident false positives (10 reported dead; 0 actually dead). The canonical scanner is ground truth — but external reports are *sometimes* right, so verify case-by-case rather than dismissing.

## MOCs (Maps of Content)

- **One MOC per taxonomy folder**, named after the folder: what this branch holds, its sub-branches, and its load-bearing works. Ingestion updates the folder's MOC in the same pass (a source filed without a MOC entry is invisible to MOC-first navigation).
- The Searcher's second search path is MOC navigation; the Writer's orientation reading is MOCs. They pay for their upkeep.
- **Project-level overview MOCs** (mapping notes onto a project's chapters) are high-churn: update **on request only**, so they don't silently drift against a moving project.
- MOC entries use the table-escaped link format; keep per-entry annotations to one line.

## Cross-work concept clusters

When several works form a recognisable family (four takes on one regulation; three readings of one thinker), link them into a named cluster inside the relevant notes' "Related works" sections. Clusters are what turn a pile of notes into a map of a debate — the Searcher reports in terms of them.
