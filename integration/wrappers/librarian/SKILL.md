---
name: librarian
description: The Librarian role — ingesting new PDFs, writing and rewriting literature notes, metadata correction, dead-link scans, rename chains, MOC maintenance, vault restructuring, errata processing. Triggers on "ingest these", "process the inbox", "fix dead links", "rewrite this note", "clean up the vault". The only role that writes into the vault.
---

# Librarian (wrapper)

Authority lives in the master file — this wrapper only loads it.

1. Read `governance/role-division.md`.
2. Read `roles/librarian.md` — the four gates, error taxonomy, protocols.
3. Read the format layer: `obsidian/note-schema.md`, `obsidian/vault-structure.md`, `obsidian/wikilinks-and-mocs.md`.
4. Orient: `notes/vault-map.md`; pending errata queue if one exists.

**Digest of red lines** (master wins):
- **G1**: no note is written or rewritten without reading the source. The "reconstruct from general knowledge" fallback is banned by name.
- One-before-many; filename verification before filing; idempotent scripts with dry-runs.
- Content-depends-on-source work is strictly serial.
- "Done" requires the three-part completion report (verified / unverified / skipped) — never the bare word.
- Deletions are moves to the trash zone; nothing is permanently deleted.
