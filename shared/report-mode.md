# Topic report mode

A **research-material report** on a topic, a book, or a set of sources — survey, literature review, single-work deep read, multi-source synthesis, or a structured face-off between positions. It is *input material* for later writing, not final prose. Produced by the **Writer + Searcher** together; invoked when the author asks for "a review of X", "a report on this book", "put these sources side by side".

## 1. Pick the type (four options; auto-select from the input or let the author choose)

| Type | When | Body's organising axis |
|---|---|---|
| ① Single-work report | Deep read of one book | **chapter by chapter** (with page ranges) |
| ② Multi-source synthesis | A set of primary + secondary sources | **source by source** (each gets the sub-template) |
| ③ Literature review / field map | Survey a domain | **axes or phases** of the debate |
| ④ Structured face-off | Two positions in conflict | **position A vs position B → diagnosis** |

## 2. Six shared blocks (fixed skeleton, all four types)

1. **Positioning & inventory** — what this report is, what materials it uses, what the vault already holds.
2. **Body** — organised along the type's axis (chapters / sources / axes / positions).
3. **Verbatim quote list** — grouped by theme or use, real page numbers, each marked "verified against the source" (§4).
4. **Connection to the project** *(signature block, mandatory)* — which sections or claims of the author's own work this feeds; direction of citation; overall stance; options.
5. **Recommendations to the author** *(signature block, mandatory)* — space allocation, writing risks, actions, next steps.
6. **Appendices** — verification changelog, quick citation index, works covered, works not expanded.

The two signature blocks are what make it a *report to someone* rather than a summary: they force the jump from "what the sources say" to "what you should do about it".

## 3. Reusable sub-templates

- **Per source** (type ②): `[Basics] [Core interpretation/framework] [Key-chapter guide] [Key quotes | pages] [Value for the project]`
- **Per chapter** (type ①): `Chapter title (pp. X–Y) → its argument → key quotes/concepts`

## 4. Quote layer: delegated, not copied

Vault location for the body and the verbatim quote list come **from the Searcher** — source-tier discipline, real pages, complete passages, three-layer verification (`roles/searcher.md`). The report **does not restate quote rules**; it cites the Searcher's file as the single source. For large works, locate via the text layer, but quotes and page numbers always come from the source itself.

## 5. Style

A report is **research-material register** — structured, listy, typographically pragmatic; the strict prose rules of your style module are relaxed here. Quote discipline (pages, verification) and first-occurrence original-language terms still apply.

## 6. Division of labour and output

- **Searcher**: vault location + the verified quote list. **Writer**: type judgment, six-block assembly, synthesis prose, both signature blocks.
- Output goes to the current project's own `_outputs/` folder, named `{topic}_{descriptor}_{type}_v{YYMMDD}{a/b…}.md`.

## 7. Publication-grade reviews

If a review must support publication or strong claims (predefined protocol, reproducible search, explicit inclusion/exclusion), add a standard systematic-review method on top: search protocol and log, deduplication, staged screening with recorded exclusions, and confidence tiers. This mode governs the *output form and quote discipline*; the protocol governs *search reproducibility* — quote gates here remain the stricter of the two.
