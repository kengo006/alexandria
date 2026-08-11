# Changelog

The skeleton is extracted from a live production system; each release is a **curated snapshot**, not a mirror. Releases are named after the upstream snapshot they carry — the system was already in its third generation when first published, hence the repo's first release was tagged v0.1 and later releases adopt the upstream `v3.x` numbering.

## v3.5 — 2026-08-11 · The blind-spot layer

**Every gate has a region it structurally cannot see, and that is where the defect sits.** v3.3 was about a text layer that lies; v3.4 was about rulings that no gate checks. This one is about checks that are healthy, correctly aimed, and still incapable of reporting the thing you need — beginning with a correction to this repo's own spec.

- 🔴 **`claims-and-evidence` §5 is now *five* ways a check dies.** The fifth: **deletion is invisible.** Every gate above it hunts for surplus or difference, and a missing passage produces neither — no stray to sanitize, no mismatch to diff, no syntax to fail, no anchor moved. One lost filename in a changelog line, eaten by a shell command substitution, cleared six gates in a row including a human line-by-line review. 🔑 **The corollary is worth more than the rule: "the two copies match" is a *necessary* condition for completeness, never a sufficient one** — a loss from a single operation lands in both copies, so checksum parity proves the export did not drift and proves nothing about whether the source was whole. *This section had said "four" since v3.2; the family gained its fifth member the same day v3.4 shipped, and the two crossed in the air.*
- **New §7 — what a gate structurally cannot see.** Three of them. **Completeness can only be measured against the source, never the product**: a file that had lost every printed page number, mangled its footnote markup, and misfiled cross-page paragraphs scored *healthy, no action needed* on two independent registers, because both read only the product. 🔑 **What broke thoroughly enough gets caught; what broke just enough to still look right goes straight through.** ⚠ And "against the source" is not yet precise — two probes against the same source disagreed (4-of-7 misaligned vs. 18-of-18 aligned) because one sampled first sentences and the other mid-page; **say which face of the source you measured.** Then: **presence-only gates reward vagueness** (a field reading `not sent` counted as attested), and **the signpost is the thing's most convincing double** (10 of 10 footnote markers verified present; the footnote text they point to had been missing for 34 days).
- **New §8 — the half you did well is why the other half never happens.** Three cases in one day, three people, three objects: a retraction thorough enough to say "that recommendation was mine and was never executed" while two other passages still taught it; a full self-criticism that made its section feel finished, followed by eight more errors of the same shape; a probe validated against 14 negative controls that then could not catch the case which prompted it. ⇒ **The better the finished half reads, the more it needs a last line stating what is still not done.** 📌 Deliberately adds no check — nobody in the three cases was unaware of the second half, so a gate would not have helped.
- **§4 gains a second sibling rule**: *a tool's first-hand source is its code; its output is second-hand.* Diagnosing mechanism from emitted artifacts is inference — and the damage was not the wrong diagnosis but the two fixes prescribed on top of it, both regressions.
- **Searcher §1 — two additions to the page-offset machinery.** A **second, independent cause of the same −1**: layout-aware extractors file a page-spanning paragraph wholly under the page it started on, so a quote from a page block's *opening* has roughly a one-in-five chance of belonging to the page before (census: 391 files / 19,927 pages; mid-page probe aligned 98.0%, first-sentence probe −1 in 18.70% — a 9.4× gap). Rule carries its **exit condition**. And **one thing that is not an offset at all**: online-first articles print a self-contained page range that is not the version of record's — ⚠ the image credential makes this *harder* to doubt, because "verified on the image, printed page 5" is true and wrong.
- **Searcher §2 — numbers inside a table are never taken from an extracted cell.** A version upgrade recovered a **minus sign** the older build had split into a cell of its own (`+0.17` in the product, `−0.17` on the page) — and left the cell alignment wrong in both builds.
- **Librarian §8 — three additions.** 🔑 **The intake probe reads the PDF while the damage happens inside the extractor**: one file measured a healthy 3.42% single-letter rate at source and came out of three extractors at 1.02% / 4.06% / **26.69%** ⇒ choosing an extractor is a decision *followed by a measurement, per file* — and ⚠ *fragment rate* is not *single-letter rate* (43.6% of one work's single letters were legitimate). **Searchability sets severity; provenance decides whether you touch it** — a book's own misprint, corrected, makes every downstream quotation one that does not exist in the source. And a **page-anchor gate**: a two-up split produces a file at twice the original page count, and both numbers report success while counting different objects.
- 41 files.

## v3.4 — 2026-07-31 · The ruling layer

**Gates check work; nothing checks a ruling.** This release adds the fourth verification layer, the boundary of the page credential, and a governance section for the class of error no gate had been catching: a decision written down more confidently than its evidence supports.

- **Searcher §2 is now four layers.** New **entity attribution** — is the passage's claim *about* the same subject the draft is about? It is the only layer that **flags rather than discards**, because a near-miss on entity is often the right passage with the wrong framing. With it, **the second cut**: separate what the author asserts from what is *presupposed by the subject the author describes*; an editor's note is not the author's words.
- **claims-and-evidence §1**: the credential's **range**. A ✅ needs three things together — printed-number credential, **verbatim anchor**, and position on the page. *Seeing the page is not verifying the sentence*, and a verification never extrapolates to the next quote. Notation follows: `pp. 9, 11`, never `pp. 9–11`, when the evidence covers two pages and not the span.
- **claims-and-evidence §3**: the **vocabulary rule** — "final state", "no problems", "all clean" are banned; say two falsifiable sentences instead (known classes at zero with a named regression test / N samples read with the sampling method stated). Where you did not measure, write *"not measured — discipline only, no gate"*: **a fabricated sample size is worse than "no problems", because it looks falsifiable.** And a self-declared convergence gets its final confirming round **ordered by the recipient**, not by the reporter — twice here a completion was announced, and twice one more round found real defects.
- **New `claims-and-evidence` §6 — a ruling is wider than its evidence.** Four questions before a ruling ships (how much does it cover / which *version* did it reject / does the evidence mean anything in *this* data / is the criterion sufficient or only necessary), plus the receiving side's duty: **when a report contains two sentences that contradict each other, ask — do not pick one as a premise.**
- **Librarian §8**: three additions — a repair whose wrong output is a **real word** must never be applied in bulk (the safest-looking case is the dangerous one); **intake runs the full ladder by default**, tiering decides how much a human reads, not what runs (file-level quality indicators measured almost no discriminating power; the producer string was the one that earned its place); and **register a defect type the round you name it, even when the ruling is "not fixing this"** — "new" is a judgement relative to a list, so the list's completeness is part of the criterion.
- 41 files.

## v3.3 — 2026-07-20 · The corpus integrity layer

**Your grep can lie.** A file can pass every size check and still be unsearchable — words split apart character by character, a font's private encoding storing `wkh` for `the`, OCR noise that leaves single words findable while every phrase is dead. Three failure families, each invisible to the others' detector. This release ships the counter-machinery.

- **New** `shared/degradation-registry.md` — the honest-degradation pattern: files repaired to their ceiling are **registered, never hidden**; every entry carries which access paths still work; the search index self-reports the degraded count, and an unreadable registry returns *unknown*, never zero.
- **Librarian §8 (new section)**: the three failure families and their detectors; intake risk probes (font-table checks before extraction; the extractor-as-control-group diagnosis rule); three-layer extraction QA (structure / lexicon / **recall** — each catches what the others miss); and the repair method that actually worked — **corpus-statistics-driven repair of the original text** (use the corpus's own word frequencies), where re-extraction reproduced the damage and OCR traded one disease for another.
- **Searcher**: file-level failure judged by the phrase-probe test (single words hit, phrases dead = every negative conclusion about that file is void); a mechanical pre-step before any "not in the vault" ships — consult the registry and the index's `degraded` self-report.
- **optional-integrations**: the self-report contract (living file, read fresh; *unknown-not-zero*; count mismatches surfaced, never silently resolved).
- 41 files.

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
