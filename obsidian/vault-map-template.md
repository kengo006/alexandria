# Vault map (template)

The vault map is the one page describing your taxonomy: what branches exist, what belongs where, and the filing conventions the Librarian applies. Roles read it instead of re-deriving your structure; keep it a **pointer document** — structure lives here, counts and inventories live in the folders themselves (numbers in prose go stale).

Copy, replace the synthetic example with your own taxonomy, save as `notes/vault-map.md`.

````markdown
---
title: "Vault map"
updated: YYYY-MM-DD
status: pointer — structure only; no counts, no inventories
---

# Vault map

> Two-end mirror: `notes/` ↔ `sources/` (matching trees). Naming: `Author_Year_Title`.
> ★ prefix (notes only) = load-bearing for the current project. One MOC per folder.

## Taxonomy

<!-- SYNTHETIC EXAMPLE — replace with your own field's structure -->
- `memory-studies/` — empirical and theoretical work on memory
  - `consolidation/` — systems and synaptic consolidation, reconsolidation
  - `collective-memory/` — social and political memory studies
- `philosophy-of-mind/`
  - `extended-mind/` — vehicle externalism and its critics
  - `personal-identity/`
- `methods/` — methodology and research design sources
- `_off-topic/` — kept for reference, outside the project's scope

## Filing rules of thumb
- A work engaging two branches files under the one it *argues in*, and is wikilinked from the other branch's MOC.
- New branch when a folder's MOC stops fitting on one screen **and** a natural seam exists; splits cascade through the rename chain (see vault-structure.md).
- <your own conventions: translations, edited volumes, grey literature…>

## Non-literature zones
- `notes/_project/` — the project's own thinking notes (not literature; excluded from two-end checks)
- <anything else roles should not treat as literature>
````

**Maintenance**: owned by the Librarian; updated when the taxonomy changes shape (new/split/merged branches), not per ingestion. The verification scripts, not this file, are the authority on what currently exists.
