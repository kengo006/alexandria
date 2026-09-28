# Evidence handbook

> Shared by every role that takes evidence: **the Writer**, for its own evidence (`roles/writer.md` §1); **the Critic**, for counter-evidence only (`roles/critic.md`); and **a dispatched Searcher** (`roles/searcher.md`). One set of rules, written in one place, so there is exactly one place where quote discipline can fail and be fixed.
>
> **Where it came from.** Until v4.0 only the Searcher retrieved, and these rules were its §1, §2 and discovery Step 4 (`roles/searcher.md`). When the Writer and the Critic began taking their own evidence, the rules moved here as they stood — the move changed who reads them, not what they say. One phrase was widened so that it addresses every reader: §2's "before it enters your report" now reads "before it enters your report or your draft".

## §1 Source tiers (highest-priority rule)

| Source | Citable? | Use |
|---|---|---|
| **Source PDF** (including its page images) | ✅ **the only citation source** | Verbatim quotes, page numbers, italics |
| Text layer (extracted text alongside PDFs) | ❌ positioning only | Full-corpus grep; locating passages; reading at scale |
| OCR output (scanned sources) | ❌ positioning only | Locating passages; noisy by nature |
| Literature notes | ❌ positioning only | Orientation: which work, which chapter, is it relevant |
| Semantic-recall fragments (if integration present) | ❌ recall only | Cross-lingual candidate discovery; follow the pointer back to the PDF |
| Full-document read via the harness's built-in PDF reader | ❌ forbidden | Can silently truncate malformed PDFs and misreport page counts |

**Why notes are not citation sources.** A note's "key quotes" section may contain transcription errors, stale page numbers, or reconstructions — and you cannot tell verified entries from unverified ones. Copying from notes launders second-hand text into a final draft. Always return to the PDF.

**On built-in PDF readers.** Agent-harness PDF readers can silently truncate documents with malformed cross-reference tables and then *misreport the page count* (a 300-page book presenting as 17 pages of front matter). Read PDF *content* through the text layer. For taking the final verbatim text, render the **individual page as an image** — and prefer a rendering path **whose failure is loud**. This system once ran for days on a built-in page-render path that failed *silently*: seats kept claiming image-verified quotes while receiving no images at all (the incident `governance/claims-and-evidence.md` exists for). A silent render failure reads exactly like a successful verification; the credential rule — **report the printed page number you saw** — is what makes the difference detectable.

**Page offsets — there are three, and they stack.** What the text layer or the PDF viewer calls "page N" is routinely not the number printed on the page, for three independent reasons:

| Offset | What differs | Size | Treatment |
|---|---|---|---|
| **① Printed-number baseline** | PDF physical page vs. the number printed on it | **per-work constant**; observed **−743 to +63** | render any page, read the printed number, `offset = physical − printed`, apply book-wide |
| **② Text-layer footer drift** | text-layer page vs. printed page, in **footer-paginated** works | ±1, systematic | the printed number on the rendered page wins |
| **③ 2-up scans** | one PDF page = two printed pages | left = 2×PDF−N | tell: PDF page count ≈ half the work's printed pages |

① is **not** the thickness of the front matter — long front matter drives it into positive tens; copies cropped of their front matter dip *negative*; and scans bound from journal runs go **hundreds negative**, because continuous journal pagination outruns the PDF (a real case: PDF page 11 carrying printed page 754 = offset −743). It has **no default value**: probing ±1 will never find a page that is eleven off (a real case: physical page 21 carried printed page 10). **Compute the offset once per work, then reuse it** — and check `shared/page-offset-registry.md` *first*; if the work has a verified row, the offset is already known. Append a row (with its verification anchor) after verifying a new work.

② is the trap this section originally documented: in works paginated at the **foot** of the page, the extracted text layer attributes pages shifted by one — the number sits at the bottom and falls into the *next* page's text flow, so the text layer's "page N" is printed page N−1. Header-style pagination does not do this. This was found the hard way: a batch of "wrong page" audit failures turned out to be the extraction shifting, not the citations being wrong.

⚠ **A second, independent cause produces the same −1, and it needs a different fix.** Layout-aware extractors file a paragraph that **spans a page break** entirely under the page it *started* on. The page block itself is not displaced — only its opening is. A census separated the two by probing each page twice. **Population: the 391 corpus files that carry both a text layer and page markers, 19,927 physical pages** — files with no text layer at all are outside this denominator and were counted separately. Within it, a mid-page probe aligned **98.0%** of the time (−1 in 1.98%), while a first-sentence probe came back −1 in **18.70%** — a **9.4× gap** that exists only because the first sentence is precisely where a continued paragraph lands.

> ⚠ **Read that population narrowly, and read *why* narrowly.** "Files carrying page markers" meant *the one marker shape the probe recognised* (`===== page N =====`). A later census of the same corpus — ten days on, 640 text-layer files — found **174 of them (27.2%) carrying no marker of that shape at all** (§1, page anchors), and the gap fell hardest on exactly the material that has to be cited by page. **The denominator was drawn by the detector's blind spot.** The alignment finding stands for the population it measured; what it never covered is the quarter of the corpus its probe could not see. 🔴 And do not subtract the two counts: different dates, different denominators, and the difference is not growth.

> ⇒ **Operational rule: a quote taken from the opening of a text-layer page block goes back to the page image, always.** Roughly one in five belongs to the page before. Mid-block quotes are not affected, and the block numbering itself is sound — do not "correct" it.
> **Exit condition, stated so this rule can end:** it is scaffolding around a known extractor behaviour and is retired the day the corpus is re-extracted with page attribution fixed. A rule with no exit condition outlives its cause.

**And one thing that is not an offset at all: the number printed on the page may not be the work's official pagination.** Journal articles published online-first carry a self-contained page range on the page images — 1 through 13 — while the version of record sits at 18–30. Every layer of the offset machinery assumes the printed number is authoritative, and here it is simply a different number. ⚠ **The credential makes this error harder to doubt, not easier**: the report says "verified on the image, printed page 5", which is true, and wrong. ⇒ **Cross-check the volume/issue/page range from the record before an offset is computed or a citation ships**, and never write a computed page into the registry as if it had been read.

**Running headers are a locating goldmine.** Header lines often carry the printed page number *inside the text layer* ("ARCHIVES OF MEMORY, CHAPTER ONE  37") — for paraphrase-level citations this yields the printed number with **zero renders** (the tiering in `governance/claims-and-evidence.md` §2 says when that suffices and when only an image will do).

**Page anchors come in more than one shape, and recognising one of them is not a small loss.** Locating a passage in a text layer means finding its page marker — and the marker your extractor emits is not the only marker in the corpus. Measured over 640 extracted files: **466 carried the familiar delimiter form; the other 174 — 27.2% — carried none of it**, and the gap fell hardest on exactly the material that has to be cited by page. They were not unmarked; they were marked differently: a **bare number alone on a line**, `Page N` alone on a line (one work: 334 of them), or an **inline `p. N` sitting inside a sentence** (one work: 241).

🔑 **A tool that knows one shape loses a quarter of the corpus, and it does not error — it returns "no page number found",** which reads exactly like a file that genuinely has none.

- ⚠ **Four is what one census found, not a proof of exhaustiveness** — and that same census left **27 files carrying none of the four**, which is a real state, not a detector failure. Treat the list as open.
- **Detect each shape with its own pass, never one `if/elif` chain.** A mutually-exclusive classifier mis-sorts files that carry two shapes: works with both bare-number lines and `Page N` lines get consumed by the earlier branch and the later shape is never counted. (Found by an independent re-run that walked into it.)
- **A 2-up file's markers count sheets, not pages.** In a two-up scan the anchors number the *physical* sheets, so there are about half as many as the work has printed pages — one census recorded 130 anchors against roughly 276 printed pages. 🎫 **The cheap tell, no file opening required: anchors ÷ printed pages ≈ 0.5** (≈ 1 is normal). ⚠ It is a suspicion, not a finding — confirm by rendering one page and seeing whether **two folios sit side by side on a single image**.
- 🔴 **No anchor is a locating problem, not an evidentiary one.** A file whose text layer offers no page marker must **not** be reported as "text-layer candidate, not verified" on that ground: page rendering still works, and the folio credential is still obtainable. **Conflating the two trades a solvable inconvenience for a check that should have happened.** Report it as "page number from the rendered folio; text layer carries no anchor".
- ⚠ **And carry the census's own gap with it**: of the two-up files that census confirmed, the *reading order* had been checked on only two. **Being on a two-up list is not evidence that a file's order is broken, nor that it is sound** — only someone who looked knows.

**Honest downgrade is part of the tier system.** When the render path errors, the quote is reported as "text-layer candidate — not PDF-verified", with the tool's raw error message quoted verbatim. Verified-on-page claims carry the printed page number (`claims-and-evidence.md` §1); a claim without one is treated as unverified, however confident it sounds.

**File-level failure, and the degradation registry.** A rare but real class: the text layer of an *entire file* is unreliable — single words still hit, but **phrases the work must contain return zero** (extraction interleaved two text layers, or OCR noise broke word adjacency). The test is cheap: probe with a high-frequency phrase from the work; phrases dead while words live = file-level failure, and **every negative conclusion about that file is void**. Files known to be in this state are listed in the **degradation registry** (`shared/degradation-registry.md`), and the semantic index self-reports each of the registry's categories by name. **Mechanical step — before any "not in the vault / nowhere in this work" ships**: check the registry (and the index's `degraded` self-report). **Read which category it is listed under** — they prescribe opposite things: under `unreliable_recall`, grep silence is not evidence and you switch to the paths the entry marks usable; under `unreliable_order`, grep is fully reliable and a zero count still counts, but nothing *adjacent* to a hit may be read as context or quoted continuously. Not listed but the phrase probe still fails = report upstream as a suspected new break; still no negative conclusion.

**Web-native exception.** Sources that exist only as web documents (e.g., reference-work entries such as encyclopedia articles) have no PDF. For these — and only these — the citation source is the **faithful text snapshot** captured at ingestion (a direct HTML-to-markdown conversion, not a model's summary), and locators are **section numbers** (§) rather than pages. Identify them by the note's metadata (`source: web-native`). When unsure, treat the work as a normal PDF source and mark the quote "pending verification" if no PDF exists.

**Violation self-check**: if a quote you are about to report traces to a text-layer file, an OCR file, a note, or a built-in full-document read — stop. Return to the PDF and take it from the page, or report "needs extraction / pending verification" instead. Never silently downgrade.

## §2 Four-layer quote verification

Every quote must pass all four layers before it enters your report or your draft. Run them against the PDF text, not against a note.

| Layer | Question | On failure |
|---|---|---|
| **1 Correspondence** | Does the passage actually support the claim it is matched to — not merely share keywords with it? | Discard |
| **2 Not second-hand** | Are these the author's own words and position — not the author quoting or summarising someone else? | Discard, or trace to the original author and re-evaluate |
| **3 Settled position** | Does the passage reflect the author's developed view — not a setup, a devil's advocate move, or a position refuted two pages later? | Discard, or find the passage where the author's real position lives |
| **4 Entity attribution** *(only when the passage names a specific subject)* | Is the entity the passage makes its claim **about** the same one the draft's paragraph is about? | **Flag, do not discard** — report the mismatch and let the writer decide |

**Layer 4 exists because layers 1–3 can all pass on a passage that is about someone else.** A paragraph arguing about institution X can be matched to a passage that says something structurally identical about institution Y: the correspondence holds, the words are the author's own, the position is settled — and the citation still misattributes. Layer 4 is the only one that **flags rather than discards**, because a near-miss on entity is often still the right passage with the wrong framing, and that judgement belongs to the writer.

**The second cut.** Even when the entity is right, separate **what the author asserts** from **what is presupposed by the subject the author is describing**. A historian reconstructing a tradition's assumptions is not endorsing them; writing "Author claims X" when the text reads "for this tradition, X went without saying" is a misattribution that all three earlier layers pass. Related: **an editor's note is not the author's words**, and when a single page carries several distinct elements, cite them separately rather than binding them to one page number.

**Numbers inside a table are never taken from an extracted cell.** Layout-aware extractors reconstruct table structure well enough to look right and badly enough to be wrong: a value split from its significance marker into a neighbouring cell, a whole row shifted one column, one cell repaired while the one beside it breaks, and the header column count differing between two versions of the *same* extractor. 🎫 A version upgrade here recovered a **minus sign** the older build had split off into a cell of its own — a correlation coefficient that read `+0.17` in the product and `−0.17` on the page — **and left the cell alignment wrong in both builds**. ⇒ Use the extracted table to find *where* the table is; take every value you intend to cite from the page image.

Report format marks the verification: `✓ 4-layer: correspondence / not-secondhand / settled-position / entity-attribution`. Partial passes are reported honestly: `⚠ layer 3 uncertain — this reads as setup; the author qualifies it in the following section`. When the passage names no subject, layer 4 is recorded as `attribution n/a`.

## §3 Returning to the PDF (formerly the Searcher's discovery Step 4)

**Step 4 — Return to the PDF.** For every high-relevance candidate: locate the passage (text-layer grep gives you the page); open the PDF **at that page**; take the quote verbatim — spelling, emphasis, and the **printed page number** as it appears in the work. Present quotes as **complete passages**, not clipped fragments (elide mid-passage text with `[…]` if needed, but never compress a quote into a summary). If the source is scanned and the OCR is too noisy to trust, verify against the page image; if you cannot, mark "needs extraction" — **under no circumstances fall back to copying from a note**.
