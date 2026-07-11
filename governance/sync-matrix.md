# Sync matrix (anti-drift)

Prompt systems rot in a specific way: **a fact lives in more than one file, and an upgrade touches some copies but not all.** Each survivor tells a different story; agents read whichever they hit first. The counter-method has three parts.

## 1. Mirror reduction

Before managing mirrors, minimise them:
- **Numbers live only at their source** (counts, thresholds, section-tallies). Everything else refers by *name* without the number ("the rename chain", not "the 9-point rename chain") — names survive upgrades; numbers don't.
- Index files (READMEs, quick cards, wrapper digests) carry **pointers and one-line digests**, never rule bodies.
- If you find yourself copying a paragraph between files, stop: one of them is the source; the other gets a link.

## 2. The matrix

List every fact that *must* live in more than one place, with all its mirror locations. When you upgrade the fact, walk its row. The skeleton's own matrix:

| Fact that can drift | Single source | Mirrors to walk on upgrade |
|---|---|---|
| Quote iron rule (source tiers, three layers) | `roles/searcher.md` | README pipeline section · `governance/system-overview.md` rules table · `shared/search-patterns.md` header · `shared/summon-templates.md` spawn prompts · `integration/agents/searcher.md` digest |
| Six-phase pipeline shape | `roles/writer.md` | README · GETTING-STARTED walkthrough · `governance/role-division.md` diagram · Writer wrapper digest |
| Council mechanics (independent seats) | `shared/council-mode.md` | `roles/writer.md` mode row · `roles/critic.md` §5 · Writer wrapper digest |
| Naming / star / rename chain | `obsidian/vault-structure.md` | `shared/naming-conventions.md` card · `governance/system-overview.md` rules table |
| Role boundaries | `governance/role-division.md` | each `roles/*.md` boundary section · wrapper digests |
| Note schema fields | `obsidian/note-schema.md` | `roles/librarian.md` pointers · `governance/scripts/vault_verify.py` regexes |

Adopters extending the system: **add a row the moment a new fact gains a second home.**

## 3. Upgrade discipline

Every rule change, mechanically:
1. Edit the **single source**; record the change in that file's changelog with date and reason.
2. If your files carry version numbers, bump them — and mirror version numbers only in the places your matrix names.
3. **Walk the fact's matrix row**: update every mirror in the same session as the source.
4. Check the wrapper/agent digests (`integration/`) — digests are the most-forgotten mirror class. (The upstream system's audit found exactly this: a mode was redesigned, every document updated, and the wrapper digest still taught the abolished behaviour weeks later.)
5. Run `governance/scripts/health_check.py` — it mechanises what it can (files present, forbidden patterns absent, optional version-mirror equality).

## Exclusion-zone versioning (nothing silently deleted)

When a rule is *replaced*, don't delete it — move it to a marked exclusion zone (the file's changelog, or a dedicated section) with: what replaced it, when, and why. Two payoffs: the system remembers *why* it changed (arguments don't get re-litigated from scratch), and stale copies elsewhere are traceable to a dated decision instead of being ambiguous. The rule of precedence is always: **new overrides old; old is preserved as history, marked as superseded.**
