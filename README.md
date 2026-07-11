# Alexandria

**A citation-integrity-first academic writing system for Claude Code and Obsidian.**

Large language models fabricate citations. A recent [cross-model audit](https://arxiv.org/abs/2603.03299) put reference-fabrication rates between 14% and 95% across thirteen models, and most tooling attacks the problem *after* the text is written, by detecting hallucinated references. Alexandria attacks it *before*: it is a five-role writing system whose workflow makes fabrication structurally difficult. Every verbatim quote must be read back from the source PDF at a real page number, pass three verification layers, survive a blind review, and be audited line-by-line before a draft is allowed to call itself done.

Alexandria is not a library or a server. It is a set of role definitions, methods, and governance files you drop into [Claude Code](https://claude.com/claude-code), pointed at your own [Obsidian](https://obsidian.md) vault.

**Where it comes from.** I am a graduate student in Taiwan working at the intersection of political philosophy and AI ethics. Alexandria is the system that carries that research in production — every gate in it was added because something actually went wrong. I am sharing the skeleton so that students in neighbouring humanities fields have a working reference for building their own. It is tuned for interpretive work: close reading, verbatim quotation, page-anchored citation of books and articles. If your research is quantitative or in the natural sciences, the role architecture may still serve you, but the evidence layer assumes texts rather than datasets — expect to study the framework and rework that layer yourself.

**How it grew.** Alexandria was assembled at the end of May 2026 and has been in daily production ever since — six weeks of real research at the time of this snapshot. Nothing here was designed on a whiteboard: every gate traces to a documented failure, every default to a measured comparison. The role files carry dated changelogs (the Librarian's rulebook is twenty-six revisions into its third generation), and the overhauls that mattered most are told inside the files where they happened: the source-tier rule (after the founding incident of quotes copied from notes), the ban on "reconstructing from general knowledge" (root cause of every serious fabrication), the full-text corpus layer, per-family parallel discovery (adopted after a head-to-head experiment), and the council's redesign from self-played review to independent blind seats.

**Influences.** Two public projects left direct marks: [academic-research-skills](https://github.com/imbad0202/academic-research-skills) (quote anchors, the blind-review pre-commitment, anti-sycophancy) and [everything-claude-code](https://github.com/affaan-m/everything-claude-code) (the topic-report, council, and scholar-evaluation modes began as adaptations of its method prompts). What was evaluated and deliberately *not* adopted shaped the system just as much.

**The wider system.** Alexandria is one domain of a larger personal multi-agent system, internally called *Chaos*. Around its members Chaos maintains a constitutional layer that every agent re-reads before regulated actions, file-based messaging that lets agents cooperate across sessions, mechanical drift detection, security vetting for anything external, a survival protocol for context compaction, and a standing habit of turning incidents into new gates. Much of what makes Alexandria dependable in production is this reinforcement from above: the roles supply the discipline, and the wider system keeps the discipline honest. Everything published here stands on its own without it — and what is published is Alexandria alone.

---

## What it is, and is not

**It is:**
- A **role architecture**: five specialised roles with strict separation of duties and write permissions.
- A **citation integrity pipeline**: the discipline that runs through every role, from ingestion to final audit.
- An **Obsidian-native workflow**: your notes and your sources form a mirrored pair the system maintains and verifies.
- A **governance layer**: mechanical defences against the slow drift that kills every complex prompt system.

**It is not:**
- A RAG server or embedding database (semantic recall is an optional integration, with the interface documented).
- An autonomous researcher that writes papers while you sleep. What matters most to me is the preservation of human agency — full participation in the thinking and in the work. The finished text represents *you*; that is why I refuse to build a fully automated text-production system. The human is a working part of this system, not its audience.
- A citation manager. It complements Zotero/BibTeX-style tools; it does not replace them.

## The five roles

| Role | Does | Never does |
|---|---|---|
| **[Librarian](roles/librarian.md)** | Ingests sources, writes literature notes, maintains vault structure, runs integrity gates | Writes your prose |
| **[Writer](roles/writer.md)** | Drafts and revises your text through a six-phase pipeline; orchestrates the other roles | Reads source PDFs directly; fabricates citations |
| **[Searcher](roles/searcher.md)** | Finds sources in your vault and returns **verbatim quotes with real page numbers**, verified three ways | Writes anything; paraphrases quotes |
| **[Critic](roles/critic.md)** | Reviews your drafts blind, under an explicit anti-sycophancy rule | Rewrites your text; softens valid criticism |
| **[Researcher](roles/researcher.md)** | Upstream planning: topic development, structure design | Detailed literature search; final prose |

One permission rule anchors the whole system: **only the Librarian writes to the vault.** The Writer drafts in a project folder; the Searcher and Critic are read-only. This prevents working drafts from contaminating your source of truth, and prevents the echo chamber where a model ends up citing its own earlier output.

## The citation integrity pipeline

This is the spine of the system, and the reason it exists.

**1. Source tiers.** Not everything that contains text is allowed to be a citation source:

| Source | Citable? | Role |
|---|---|---|
| The source PDF itself (at the page) | ✅ the only citation source | Final verbatim quotes, page numbers, italics |
| Extracted text layer | ❌ positioning only | Full-corpus search, locating passages |
| OCR output | ❌ positioning only | Locating passages in scanned sources |
| Your literature notes | ❌ positioning only | Orientation: which work, which chapter |
| Semantic search fragments | ❌ recall only | Cross-lingual discovery of candidates |

Positioning layers tell you *where to look*. Only the source itself tells you *what it says*. Quotes copied from notes are second-hand and carry every error the note ever made; Alexandria forbids them in final drafts.

**2. Three-layer quote verification.** Every quote the Searcher returns must pass: (a) **correspondence**: the passage actually supports the claim it is attached to, not merely keyword-matches it; (b) **not second-hand**: the words are the author's own position, not the author quoting or summarising someone else; (c) **settled position**: the passage reflects the author's developed view, not a setup being torn down two pages later.

**3. Blind review and anti-sycophancy.** The Critic commits to its evaluation criteria *before* reading the draft, and operates under a standing rule: criticism is not softened to please, and a weak rebuttal may not dismiss a valid objection.

**4. Final audit.** Before any draft is delivered, the Searcher re-enters in audit mode and walks every citation-bearing claim, producing a **support-status list**: ✅ supported / ⚠️ needs adjustment / ❌ unsupported. Unsupported claims are fixed, explicitly re-labelled as the writer's own position, or cut. They are never quietly left in.

**5. The human is the last line of defence.** The pipeline reduces the error surface; it does not replace your eyes. Final verification against the source is a design assumption, not an afterthought. Every gate in this system was distilled from a real, post-mortemed failure, including entire fabricated summaries traced to "reconstructing from general knowledge", which is why that fallback is banned by name.

## Obsidian integration

Alexandria treats your vault as a **two-end mirror**: a `notes/` tree of literature notes and a `sources/` tree of PDFs, with matched structure and mechanical verification that the two ends stay aligned.

- **Note schema**: a consistent literature-note format (metadata, structured summary, verified key quotes) that both humans and the roles can navigate.
- **Wikilinks and MOCs**: a four-step linking discipline plus Maps of Content, so the graph stays a map instead of becoming spaghetti.
- **Vault map**: a template for describing your taxonomy so the roles can navigate it (a synthetic example is included; bring your own).
- **Hygiene tools**: dead-link scanning, structure verification, and a rename-chain procedure so reorganisations don't silently break references.

## Governance: how it survives its own growth

Prompt systems rot: definitions drift apart across copies, numbers go stale, "temporary" exceptions become permanent. Alexandria ships the counter-machinery it was built with:

- **Single source of truth** per rule, with everything else linking rather than copying.
- **A sync matrix** that lists every fact that lives in more than one place, and where its mirrors are.
- **A health-check script** that mechanically verifies version mirrors, forbidden-pattern usage, and structural invariants.
- **Exclusion-zone versioning**: superseded rules are moved to a marked zone with a note on what replaced them, never silently deleted. The system remembers why it changed.

## Getting started

Three adoption tiers, in [GETTING-STARTED.md](GETTING-STARTED.md):

| Tier | You get | You need |
|---|---|---|
| **A — Minimal** | Writer + Searcher + Critic: the citation pipeline on a folder of PDFs and notes | Claude Code only |
| **B — Vault** | All five roles on a structured Obsidian vault with the note schema and two-end mirror | + an Obsidian vault |
| **C — Full** | Governance layer, health checks, summon templates, optional integrations | + Python for the scripts |

Start at A. Everything above it is additive.

## Style modules

The skeleton's prompts are English and deliberately voice-neutral. Language- and style-specific rules (punctuation conventions, tone, idiom policies) plug in as **style modules**: a documented slot in the Writer's pipeline, with a synthetic example module included. Write your own; the upstream system this was extracted from runs a Traditional Chinese module with its own typography and idiom rules.

## Optional integrations

Documented as interfaces, not shipped as dependencies: a **full-text corpus layer** (searchable text extracted alongside each PDF), **semantic recall** (an embedding index for cross-lingual candidate discovery, always recall-only, never a citation source), and an **OCR escalation path** for scanned sources. [optional-integrations.md](optional-integrations.md) describes what each contributes, the contract it must satisfy, and where it plugs in. Equivalents are straightforward to build with common tools.

## Status

Extracted from a live system (2026). The upstream continues to evolve; this skeleton is a curated snapshot, not a mirror. Issues and adaptations are welcome; the licence is [MIT](LICENSE).
