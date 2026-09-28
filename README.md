# Alexandria

**A citation-integrity-first academic writing system for Claude Code and Obsidian.**

<!-- zh-intro -->

[中文簡介](#中文簡介)

<!-- /zh-intro -->

Large language models fabricate citations. A recent [cross-model audit](https://arxiv.org/abs/2603.03299) of ten models measured reference-fabrication rates between 11.4% and 56.8%, and most tooling attacks the problem *after* the text is written, by detecting hallucinated references. Alexandria attacks it *before*: it is a six-role writing system whose workflow makes fabrication structurally difficult. Every verbatim quote must be read back from the source PDF at a real page number, pass four verification layers, survive a blind review, and be audited line-by-line before a draft is allowed to call itself done.

Alexandria is not a library or a server. It is a set of role definitions, methods, and governance files you drop into [Claude Code](https://claude.com/claude-code), pointed at your own [Obsidian](https://obsidian.md) vault.

> **In thirty seconds.** **You need**: Claude Code, and a folder with your PDFs in it. No server, no database, no key beyond the one you already have; Obsidian and the Python scripts are for later tiers. **You do**: copy two role files into `.claude/skills/` and two agent files into `.claude/agents/`, keep the evidence handbook where they can read it, point them at `sources/` and `notes/`, and ask the Writer for a paragraph. That is Tier A, and the whole citation pipeline runs at it — [GETTING-STARTED.md](GETTING-STARTED.md) has the exact steps. **You see**: [`examples/`](examples/) — a dispatched Searcher's report, a blind review, and the audit that refuses to sign off, all fabricated for illustration. **Everything below this line is why it is built this way**; if you would rather find out by running it, the two links above are the whole path in.

**Where it comes from.** I am a graduate student in Taiwan working at the intersection of political philosophy and AI ethics. Alexandria is the system that carries that research in production — every gate in it was added because something actually went wrong. I am sharing the skeleton so that students in neighbouring humanities fields have a working reference for building their own. It is tuned for interpretive work: close reading, verbatim quotation, page-anchored citation of books and articles. If your research is quantitative or in the natural sciences, the role architecture may still serve you, but the evidence layer assumes texts rather than datasets — expect to study the framework and rework that layer yourself.

**How it grew.** Alexandria was assembled at the end of May 2026 and has been in daily production ever since; the release date at the top of the changelog is how far that run had got when this snapshot was cut. Nothing here was designed on a whiteboard: every gate traces to a documented failure, every default to a measured comparison. The role files carry dated changelogs — the Librarian's rulebook stood at its fourth generation and 129 recorded revisions when v3.7 was cut — and the overhauls that mattered most are told inside the files where they happened: the source-tier rule (after the founding incident of quotes copied from notes), the ban on "reconstructing from general knowledge" (root cause of every serious fabrication), the full-text corpus layer, per-family parallel discovery (adopted after a head-to-head experiment), the council's redesign from self-played review to independent blind seats, and — in v4.0 — the move of evidence-taking out of a dedicated Searcher and into the roles that use it.

**Influences.** Two public projects left direct marks: [academic-research-skills](https://github.com/imbad0202/academic-research-skills) (quote anchors, the blind-review pre-commitment, anti-sycophancy) and [everything-claude-code](https://github.com/affaan-m/everything-claude-code) (the topic-report, council, and scholar-evaluation modes began as adaptations of its method prompts). What was evaluated and deliberately *not* adopted shaped the system just as much.

**The wider system.** Alexandria is one domain of a larger personal multi-agent system, internally called *Chaos*. Around its members Chaos maintains a constitutional layer that every agent re-reads before regulated actions, file-based messaging that lets agents cooperate across sessions, mechanical drift detection, security vetting for anything external, a survival protocol for context compaction, and a standing habit of turning incidents into new gates. Much of what makes Alexandria dependable in production is this reinforcement from above: the roles supply the discipline, and the wider system keeps the discipline honest. Everything published here stands on its own without it — and what is published is Alexandria alone.

<!-- zh-intro -->

## 中文簡介

**為 Claude Code 與 Obsidian 設計、以引文完整性為先的學術寫作系統。**

大型語言模型會捏造引文。一份橫跨十個模型的[稽核研究](https://arxiv.org/abs/2603.03299)量到的參考文獻捏造率，落在 11.4% 到 56.8% 之間；多數工具在文字寫完之後才去偵測捏造。Alexandria 在寫的時候就處理：它是一套分成六個角色的寫作系統，由工作流程本身讓捏造變得困難。每一句逐字引文都要回到原始 PDF、在真實頁碼上讀出來，通過四層核對，經過盲審，並在草稿自稱完成之前逐條稽核。

Alexandria 沒有函式庫或伺服器，只有一組角色定義、方法與治理文件：放進 [Claude Code](https://claude.com/claude-code)，指向你自己的 [Obsidian](https://obsidian.md) 知識庫就能運作。

- **寫作員（Writer）**：依六個階段起草與修改，自己回到原始頁面取證。
- **批評者（Critic）**：先寫下評判標準再讀草稿（盲審），並自己查反面證據。
- **搜尋員（Searcher）**：經你核准後才派出，只負責兩件事：大主題的完整語料蒐集，以及交稿前的最終稽核。
- **管理員（Librarian）**：入庫與撰寫文獻筆記，是唯一能寫入知識庫的角色。
- **研究員（Researcher）**：動筆之前，把一個想法發展成寫作計畫。
- **深讀員（Deep-reader）**：把一整本書讀成附頁碼錨點的結構化筆記。

取證規則集中在一份共用的[取證手冊](shared/evidence-handbook.md)（英文）：自 v4.0 起，寫作員、批評者與派出的搜尋員都照同一套規則取證。

我是台灣的研究生，研究政治哲學與 AI 倫理的交界。Alexandria 是承載這些研究的日常系統，裡面每一道關卡，都是因為真的出過錯才加上去的。分享這副骨架，是希望鄰近人文領域的學生有一個能運作的參考，用來打造自己的系統。它為詮釋性的工作而調校：細讀、逐字引用，以及書籍與論文的頁碼錨定。

最小可用版（Tier A）只需要 Claude Code 和一個放 PDF 的資料夾，步驟見 [GETTING-STARTED.md](GETTING-STARTED.md)，各階段的示範輸出在 [`examples/`](examples/)。文件本體目前只有英文。

<!-- /zh-intro -->

---

## What it is, and is not

**It is:**
- A **role architecture**: six specialised roles with strict separation of duties and write permissions.
- A **citation integrity pipeline**: the discipline that runs through every role, from ingestion to final audit.
- An **Obsidian-native workflow**: your notes and your sources form a mirrored pair the system maintains and verifies.
- A **governance layer**: mechanical defences against the slow drift that kills every complex prompt system.

**It is not:**
- A RAG server or embedding database (semantic recall is an optional integration, with the interface documented).
- An autonomous researcher that writes papers while you sleep. What matters most to me is the preservation of human agency — full participation in the thinking and in the work. The finished text represents *you*; that is why I refuse to build a fully automated text-production system. The human is a working part of this system, not its audience.
- A citation manager. It complements Zotero/BibTeX-style tools; it does not replace them.

## The six roles

| Role | Does | Never does |
|---|---|---|
| **[Librarian](roles/librarian.md)** | Ingests sources, writes literature notes, maintains vault structure, runs integrity gates | Writes your prose |
| **[Writer](roles/writer.md)** | Drafts and revises your text through a six-phase pipeline; **takes its own evidence** — verbatim quotes with real page numbers, read at the source page and verified four ways; orchestrates the other roles | Ships a quote it has not seen on the page; writes into the vault |
| **[Searcher](roles/searcher.md)** | Dispatched, with your approval, for the two jobs too big or too independent for the Writer: a complete sweep of a large topic's sources, and the final audit | Writes anything; paraphrases quotes; runs for an everyday lookup |
| **[Critic](roles/critic.md)** | Reviews your drafts blind, under an explicit anti-sycophancy rule, and looks up its own counter-evidence at the source page | Rewrites your text; softens valid criticism; fetches evidence *for* the draft |
| **[Researcher](roles/researcher.md)** | Upstream planning: topic development, structure design — and talking an idea through when nothing will be written yet | Detailed literature search; final prose; deciding your position for you |
| **[Deep-reader](roles/deep-reader.md)** | Reads a whole book or lecture series into a structured, page-anchored note — a map of the argument, not a summary | Discusses ideas (the Researcher's job); writes your prose |

One permission rule anchors the whole system: **only the Librarian writes to the vault.** The Writer drafts in its own project folder; the Deep-reader adds only its own notes to one dedicated folder; the Searcher and Critic are read-only. This prevents working drafts from contaminating your source of truth, and prevents the echo chamber where a model ends up citing its own earlier output.

**One article, one Writer, one folder.** Every project gets a scaffold whose front door orients anyone who opens it — you after a week away, a review seat, the Critic — in thirty seconds. The rule underneath: *a product that lives only in the conversation does not exist.*

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

Positioning layers tell you *where to look*. Only the source itself tells you *what it says*. Quotes copied from notes are second-hand and carry every error the note ever made; Alexandria forbids them in final drafts. These rules live in one [evidence handbook](shared/evidence-handbook.md) that every role taking evidence follows — the Writer for its own evidence, the Critic for counter-evidence, and a dispatched Searcher.

**2. Four-layer quote verification.** Every quote that enters a draft must pass, whoever took it: (a) **correspondence**: the passage actually supports the claim it is attached to, not merely keyword-matches it; (b) **not second-hand**: the words are the author's own position, not the author quoting or summarising someone else; (c) **settled position**: the passage reflects the author's developed view, not a setup being torn down two pages later; (d) **entity attribution**, when the passage names a specific subject: the claim is about the *same* subject the paragraph is about. Layers (a)–(c) discard on failure; (d) **flags instead**, because a near-miss on entity is often the right passage with the wrong framing — and that judgement belongs to you, not to whoever retrieved the passage.

**3. Blind review and anti-sycophancy.** The Critic commits to its evaluation criteria *before* reading the draft, and operates under a standing rule: criticism is not softened to please, and a weak rebuttal may not dismiss a valid objection. It looks up its own counter-evidence, verbatim and page-anchored, under the same rules.

**4. Final audit.** Before any draft is delivered, a Searcher is dispatched in audit mode — a reader who did not write the text, approved by you like every dispatch — and walks every citation-bearing claim, producing a **support-status list**: ✅ supported / ⚠️ needs adjustment / ❌ unsupported. Unsupported claims are fixed, explicitly re-labelled as the writer's own position, or cut. They are never quietly left in.

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
- **A claims-and-evidence layer**: "verified" must be bound to a trace that could only exist if the looking actually happened — rendered-page credentials on quotes, denominators on every passing summary, and no negative conclusion until the page has been read whole ([claims-and-evidence.md](governance/claims-and-evidence.md)).
- **A corpus integrity layer**: your grep can lie — three file-level failure families each invisible to the others' detector, three-layer extraction QA, corpus-statistics-driven repair, and an honest degradation registry the search index itself reports ([librarian §8](roles/librarian.md), [degradation-registry.md](shared/degradation-registry.md)).
- **Exclusion-zone versioning**: superseded rules are moved to a marked zone with a note on what replaced them, never silently deleted. The system remembers why it changed.

## Getting started

**See it first** if you would rather: [`examples/`](examples/) carries one worked output per stage — a dispatched Searcher's discovery report, a Critic's blind review, and the final audit (which, in the example, refuses to sign the draft off). Everything in them is fabricated on purpose; the file says so at the top.

Three adoption tiers, in [GETTING-STARTED.md](GETTING-STARTED.md):

| Tier | You get | You need |
|---|---|---|
| **A — Minimal** | Writer + Critic, with the Searcher for dispatched jobs: the citation pipeline on a folder of PDFs and notes | Claude Code only |
| **B — Vault** | All six roles on a structured Obsidian vault with the note schema and two-end mirror | + an Obsidian vault |
| **C — Full** | Governance layer, health checks, summon templates, optional integrations | + Python for the scripts |

Start at A. Everything above it is additive.

## Style modules

The skeleton's prompts are English and deliberately voice-neutral. Language- and style-specific rules (punctuation conventions, tone, idiom policies) plug in as **style modules**: a documented slot in the Writer's pipeline, with a synthetic example module included. Write your own; the upstream system this was extracted from runs a Traditional Chinese module with its own typography and idiom rules.

## Optional integrations

Documented as interfaces, not shipped as dependencies: a **full-text corpus layer** (searchable text extracted alongside each PDF), **semantic recall** (an embedding index for cross-lingual candidate discovery, always recall-only, never a citation source), and an **OCR escalation path** for scanned sources. [optional-integrations.md](optional-integrations.md) describes what each contributes, the contract it must satisfy, and where it plugs in. Equivalents are straightforward to build with common tools.

## Status

Extracted from a live system (2026). The upstream continues to evolve; this skeleton is a curated snapshot, not a mirror. Release history, and the reasoning behind each change, is in [CHANGELOG.md](CHANGELOG.md). Issues and adaptations are welcome; the licence is [MIT](LICENSE).
