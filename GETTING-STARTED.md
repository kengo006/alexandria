# Getting started

Alexandria is adopted in tiers. Each tier is additive; start at A and stop wherever your needs are met.

| Tier | You get | You need |
|---|---|---|
| **A — Minimal** | Writer + Searcher + Critic: the citation integrity pipeline over a folder of PDFs and notes | Claude Code |
| **B — Vault** | All six roles over a structured Obsidian vault: note schema, two-end mirror, ingestion gates | + an Obsidian vault |
| **C — Full** | Governance: sync matrix, health checks, summon templates, style modules, optional integrations | + Python 3 for the scripts |

---

## Tier A — Minimal (three roles, zero dependencies)

**What you get.** A Writer that drafts your text and orchestrates two subagents: a Searcher that returns verbatim, page-anchored quotes from your PDFs, and a Critic that reviews drafts blind. The full citation pipeline — source tiers, three-layer quote verification, blind review, final audit — runs at this tier.

**Setup.**

1. Copy the role files into your Claude Code skills directory:
   ```
   .claude/skills/writer/SKILL.md      ← from roles/writer.md
   .claude/skills/searcher/SKILL.md    ← from roles/searcher.md
   .claude/skills/critic/SKILL.md      ← from roles/critic.md
   ```
   Also copy `integration/agents/searcher.md` and `integration/agents/critic.md` into `.claude/agents/` so the Writer can spawn them as subagents with the right toolset (read-only).

   *Two install patterns.* Copying the full role files (above) makes each skill self-contained — simplest for Tier A. The thin wrappers in `integration/wrappers/` are the alternative for Tier B+: the skill file stays a small pointer and the role's **master copy lives in your vault or a cloned repo**, so upgrading a role means editing one file, not re-copying. If you use the wrappers, fix their relative paths to wherever the master files live.

2. Arrange your materials in two folders (names are configurable in each role file):
   ```
   sources/   ← your PDFs (the only citation source)
   notes/     ← your reading notes, if any (used for orientation only)
   ```

3. Start a session and summon the Writer (see `shared/summon-templates.md` for the full template):
   > You are the Writer. Read `.claude/skills/writer/SKILL.md`, then wait for my assignment.

**First session walkthrough.** Give the Writer a paragraph you want to develop. It will: draft from your argument first (without peeking at notes — your reasoning leads, evidence follows); spawn the Searcher to find supporting and opposing passages, returned as verbatim quotes with real page numbers; integrate; spawn the Critic for a blind review; revise with explicit reasons for every accepted or rejected criticism; and finish with a Searcher audit that walks every citation-bearing claim and returns a support-status list (✅/⚠️/❌). Nothing ❌ is quietly left in.

**What Tier A does not give you:** structured ingestion (new PDFs get notes by hand or not at all), vault hygiene, and upstream planning. That is Tiers B and C.

---

## Tier B — Vault (six roles on Obsidian)

**Adds.** The **Librarian** — the only role allowed to write into the vault — handles ingestion: new PDF → quality gates → literature note in a consistent schema → filed into the taxonomy with wikilinks and MOC updates. The **Researcher** handles upstream planning: topic development and structure design before writing starts, and doubles as the role you talk an idea through with. The **Deep-reader** turns a whole book into a structured close-read note (optional — add it when you have a text worth metabolising rather than quoting).

**Setup on top of Tier A.**

1. Adopt the vault layout (details in `obsidian/vault-structure.md`):
   ```
   your-vault/
   ├── notes/       ← literature notes, mirrored to sources/
   ├── sources/     ← PDFs, mirrored to notes/
   └── vault-map.md ← your taxonomy, described for the roles (template in obsidian/)
   ```
   The **two-end mirror** — matched folder structure between `notes/` and `sources/` — is what lets every note trace to its source and every source be discoverable from notes.

2. Copy `roles/librarian.md`, `roles/researcher.md`, and (optionally) `roles/deep-reader.md` into your skills directory as in Tier A.

3. Fill in `vault-map.md` from the template in `obsidian/vault-map-template.md` (a synthetic example is included — replace it with your own taxonomy).

4. Ingest a first batch: summon the Librarian and hand it a few PDFs. Inspect the notes it produces against `obsidian/note-schema.md`; correct the schema file if your field needs different metadata. The schema is a contract between you and the roles, not a straitjacket.

**Write-permission rule (now enforced).** From this tier on, only the Librarian writes inside `notes/` and `sources/`. The Writer works in a separate project folder; the Deep-reader adds only its own notes under `notes/close-reads/`; Searcher and Critic are read-only everywhere. This is what keeps working drafts from contaminating your source of truth.

---

## Tier C — Full (governance and integrations)

**Adds.** The machinery that keeps a growing system honest with itself:

- **`governance/system-overview.md`** — the single entry point: roles, modes, iron rules, and where each rule's single source of truth lives.
- **Sync matrix** (`governance/sync-matrix.md`) — every fact that exists in more than one file, with its mirror locations. When you upgrade a rule, walk its row.
- **Health check** (`governance/scripts/health_check.py`) — mechanical verification: version mirrors consistent, forbidden patterns absent, expected files present. Run it at logical boundaries.
- **Summon templates** (`shared/summon-templates.md`) — standard prompts for launching each role with the right reading list.
- **Style modules** (`style-modules/`) — plug in language- and voice-specific writing rules without touching the role skeletons.
- **Optional integrations** (`optional-integrations.md`) — interfaces for a full-text corpus layer, semantic recall, and OCR escalation. Build them with your preferred tools; the roles already know how to use them if present, and degrade gracefully if absent.

**Configuration.** The scripts take your role names, paths, and version locations from constants at the top of each file. Set them once; the checks are then mechanical.

---

## Suggested path

Week one: Tier A on a folder of ten PDFs — learn the pipeline's rhythm, especially the audit phase. If the discipline earns its keep, migrate to Tier B and re-point the roles at the vault. Adopt Tier C when you notice the system drifting — which, if you use it seriously, you will.
