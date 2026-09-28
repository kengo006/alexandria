# System overview (single entry point)

One page to see the whole system: which roles and modes exist, where each rule's single source of truth lives, and what to read first. When the system grows, this page is what keeps skills from colliding and rules from forking.

> Terms: **role** = independently summonable skill (six of them); **mode** = a method folded *inside* a role (not a separate skill — this prevents trigger proliferation); **iron rule** = single-sourced, referenced everywhere, copied nowhere.

## Roles

| Role | One line | Typical triggers |
|---|---|---|
| **Librarian** | ingestion, literature notes, vault integrity, errata | "ingest these PDFs", "fix dead links", "rewrite this note" |
| **Writer** | drafting through six phases; takes its own evidence at the source page; spawns the Critic, dispatches the Searcher | "draft this section", "revise this", "polish", "find sources on X", "verify these quotes" |
| **Searcher** | dispatched by the Writer, with the human's approval, for a large topic's complete corpus sweep or the final audit | — (not user-summoned; never for an everyday lookup) |
| **Critic** | blind first-round review; takes its own counter-evidence (spawned by Writer) | — (not user-summoned) |
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
| Quotes/pages/emphasis from the source PDF only; text layer & notes locate only; four-layer verification; complete-passage presentation | `shared/evidence-handbook.md` §1–§3 | Writer, Critic, Searcher, Deep-reader, report mode, council, Librarian |
| Blind commitment + anti-sycophancy | `roles/critic.md` §1–§2 | Writer Phase 5, council |
| Ingestion gates G1–G4; error taxonomy; completion protocol | `roles/librarian.md` | — |
| Who takes evidence (the Writer its own, the Critic counter-evidence); when the Searcher is dispatched (two jobs, each approved); source-page re-check before anything ships; no second-hand quotes | `roles/writer.md` §1 | summon templates, role-division, Writer wrapper, Critic, Searcher |
| Only the Librarian writes the vault | `governance/role-division.md` | all roles |
| Every credibility-affecting claim binds to a trace (rendered-page credential, tiering, negative-conclusion rule, summary denominators) | `governance/claims-and-evidence.md` | evidence handbook §1, Searcher §4, Writer Phase 6, Deep-reader §2, role-division confidence marks |
| Naming, star convention, rename chain | `obsidian/vault-structure.md` | `shared/naming-conventions.md` (quick card) |

**The referencing discipline**: any file other than the single source *links* to the rule, states at most a one-line digest, and never restates details or numbers. Details restated in two places will disagree within a month — see `sync-matrix.md`.

## Reading order for a new adopter

1. `README.md` — what this is; 2. `GETTING-STARTED.md` — pick your tier; 3. `governance/role-division.md` — the constitution; 4. the role files you're adopting; 5. `obsidian/` if Tier B; 6. this folder's remaining files if Tier C.

## Maintenance

This page and the sync matrix are the two files to update when the system's *shape* changes (roles, modes, rule locations). Content changes stay in their single-source files.

**Keeping rulebooks readable: three layers.** A role's rulebook is read in full at every summon, so each paragraph is a context cost paid on every run — and rulebooks grow, because every incident adds its reason next to its rule. Upstream split the four largest into three layers: **the rules**, read in full; **the rationale and case history**, searched on demand (each rule keeps a short pointer to its case entry); and **the changelog**. Three mechanical guards keep the split honest: the move itself is verified line by line (the multiset of lines before equals the multiset after — nothing lost, nothing reworded in transit); every pointer in the rules has a case entry and every case entry has a pointer, checked in both directions; and the rules layer carries a size budget (`scripts/health_check.py` check 5), so it cannot quietly grow back. **Splitting changes no rule**: headings, numbering and every executable line stay in the rules layer; only the reasons move.
