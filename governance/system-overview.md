# System overview (single entry point)

One page to see the whole system: which roles and modes exist, where each rule's single source of truth lives, and what to read first. When the system grows, this page is what keeps skills from colliding and rules from forking.

> Terms: **role** = independently summonable skill (six of them); **mode** = a method folded *inside* a role (not a separate skill — this prevents trigger proliferation); **iron rule** = single-sourced, referenced everywhere, copied nowhere.

## Roles

| Role | One line | Typical triggers |
|---|---|---|
| **Librarian** | ingestion, literature notes, vault integrity, errata | "ingest these PDFs", "fix dead links", "rewrite this note" |
| **Writer** | drafting through six phases; orchestrates Searcher/Critic | "draft this section", "revise this", "polish" |
| **Searcher** | verified verbatim quotes from vault sources (spawned by Writer) | — (not user-summoned) |
| **Critic** | blind first-round review (spawned by Writer) | — (not user-summoned) |
| **Researcher** | idea → writing plan (upstream); also talking an idea through | "I want to write about…", "how should this be structured?", "let me think this through" |
| **Deep-reader** | a whole text → a structured, page-anchored close-read note | "read this book closely", "give me a detailed note on this" |

## Modes

| Mode | Lives in | Source file | Trigger |
|---|---|---|---|
| Topic report / literature review | Writer, mode C | `shared/report-mode.md` | "give me a review of X / a report on this book" |
| Council (whole-piece review / deadlock) | Writer as lead | `shared/council-mode.md` | chapter done; section stuck; go/no-go |
| Retrospective audit | Writer, mode D | `roles/writer.md` §3 | "did that check actually happen?"; inherited draft |
| Consult (talk an idea through) | Researcher | `roles/researcher.md` §2bis | "does this intuition hold?" |
| Scholar evaluation | Librarian, on demand | `shared/scholar-evaluation.md` | "vet this source seriously" |
| Large-work reading strategy | Librarian | `roles/librarian.md` | 100+-page sources |

## Iron rules and their single sources

| Rule | Single source | Referenced by |
|---|---|---|
| Quotes/pages/emphasis from the source PDF only; text layer & notes locate only; three-layer verification; complete-passage presentation | `roles/searcher.md` §1–§2 | Writer, report mode, council, Librarian |
| Blind commitment + anti-sycophancy | `roles/critic.md` §1–§2 | Writer Phase 5, council |
| Ingestion gates G1–G4; error taxonomy; completion protocol | `roles/librarian.md` | — |
| Writer's two information sources; no PDF reading; no second-hand quotes | `roles/writer.md` §1 | summon templates |
| Only the Librarian writes the vault | `governance/role-division.md` | all roles |
| Naming, star convention, rename chain | `obsidian/vault-structure.md` | `shared/naming-conventions.md` (quick card) |

**The referencing discipline**: any file other than the single source *links* to the rule, states at most a one-line digest, and never restates details or numbers. Details restated in two places will disagree within a month — see `sync-matrix.md`.

## Reading order for a new adopter

1. `README.md` — what this is; 2. `GETTING-STARTED.md` — pick your tier; 3. `governance/role-division.md` — the constitution; 4. the role files you're adopting; 5. `obsidian/` if Tier B; 6. this folder's remaining files if Tier C.

## Maintenance

This page and the sync matrix are the two files to update when the system's *shape* changes (roles, modes, rule locations). Content changes stay in their single-source files.
