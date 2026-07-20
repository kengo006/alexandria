# Changelog

The skeleton is extracted from a live production system; each release is a **curated snapshot**, not a mirror. Releases are named after the upstream snapshot they carry — the system was already in its third generation when first published, hence the repo's first release was tagged v0.1 and later releases adopt the upstream `v3.x` numbering.

## v3.2 — 2026-07-17 · The claims-and-evidence layer

The governance release: **"verified" must be bound to a trace that could only exist if the looking actually happened.**

- **New** `governance/claims-and-evidence.md` — the credential layer: rendered-page credentials (whoever claims "verified on the page" reports the page number printed on it), credential tiering by failure mode, the negative-conclusion rule (a tool's silence is not evidence about the world), the four ways a check dies, and summary coverage (a summary without scope may not be cited as a credential).
- **New** `shared/page-offset-registry.md` — append-only offset registry template: offsets have no default value; no row without a verification anchor.
- **Searcher**: three stacking page offsets (per-work printed-number baseline / text-layer footer drift / 2-up scans); render pages via paths whose failure is loud; honest downgrade carries the tool's raw error message.
- **Writer**: mechanical ledger inclusion criterion (*every page-bearing citation gets a ledger row* — an inclusion criterion that requires judgment will leak); ledger-only filing (a record kept twice is a mirror, and it drifted); retraction screening at filing time and again before anything goes out, always with denominators.
- **Librarian**: metadata check against an open registry at ingestion; retraction screening at maintenance cadence; deaccession = ingestion run backwards, plus the back-reference preflight ingestion never needs.
- **Deep-reader**: rendered-page credential line. **role-division**: audit-summary coverage. **health_check**: empty-sample guard and denominators, fault-injection verified.
- 39 files.

## v3.1 — 2026-07-16 · The sixth role and the project scaffold

- **New role: Deep-reader** — reads a whole book or lecture series into a structured, page-anchored close-read note; write access bounded to its own notes folder.
- **Writer**: the project scaffold (one piece, one Writer, one folder; an entry file that orients anyone in thirty seconds — *a product that lives only in the conversation does not exist*), retrospective-audit mode, the verification-batch spawn form, and filing gates.
- **Researcher**: consult mode — talking an idea through when nothing will be written yet.
- **role-division**: the six-role constitution, handover confidence marks (🟢 on file / 🟡 reported only — the receiver's first act is an existence check), bounded write-permission carve-outs.
- Companion repository linked: [alexandria-semantic-recall](https://github.com/kengo006/alexandria-semantic-recall) — a reference implementation of the optional semantic-recall integration.
- 37 files.

## 2026-07-14 · Correction

- README: fixed a misattributed fabrication-rate statistic (the cross-model audit covers ten models, 11.4%–56.8%). Corrections happen in the open; the git history is the errata trail.

## v0.1 — 2026-07-11 · Initial public release

- The five-role system (Librarian / Writer / Searcher / Critic / Researcher) and the citation-integrity pipeline: source tiers, three-layer quote verification, blind review under an anti-sycophancy rule, and the final audit that walks every citation-bearing claim.
- The Obsidian layer (note schema, two-end mirror, wikilinks and MOCs), the governance layer (single source of truth, sync matrix, health-check script, exclusion-zone versioning), summon templates, the style-module slot, and optional-integration interfaces.
- 36 files.
