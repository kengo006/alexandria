# Search patterns (corpus-first)

> Teaching file, mainly for the Searcher; the Writer and Librarian use the same moves for locating. **The iron rule first** (single source: `roles/searcher.md` §1): the text layer, notes, and OCR output **locate only** — verbatim quotes, page numbers, and emphasis come from the source PDF at the page. Never full-read a PDF through the harness's built-in reader (silent truncation); compare reported page counts against `/Count` before viewing page images.
>
> Examples below use the synthetic `memory-studies` taxonomy from `obsidian/vault-map-template.md`. Invocation snippets are **pseudo-calls** for a Claude Code-style toolset (`Grep`/`Glob`/`Read`); adapt names and parameters to your harness.

## 0. The standard three-step (memorise this one)

1. **Grep the text layer corpus-wide** — find *which work, which passage*.
2. **Check the note / MOC** — judge relevance, find the chapter.
3. **Return to the PDF** — take verbatim + real page + emphasis from the page → three-layer verification.

## 0-bis. Semantic recall (optional layer, if the integration is present)

Grep is literal; for **paraphrase and cross-lingual recall** use semantic search over the text layer.
- 2–3 phrasings per concept (wording-sensitive: one phrasing can miss entirely — try plain-language *and* term-of-art versions).
- Low scores plus topic drift = out-of-scope signal → fall back to grep.
- The index is built offline: new sources hit grep immediately but appear in semantic recall only after the index updates — **a semantic zero never proves absence; always follow with a corpus grep.**
- Fragments are pointers; steps 2–3 above still apply.

## 1. Corpus-wide text-layer grep (the recall workhorse)

```python
# concept sweep across the whole corpus (notes only summarise; this is how you find what notes missed)
Grep("memory consolidation", path="text-layer/", glob="*.txt", output_mode="files_with_matches")

# once a candidate is found, pull context to locate the passage
Grep("memory consolidation", path="text-layer/memory-studies/", output_mode="content", -C=3)

# expand synonyms BEFORE grepping: translations / broader-narrower terms / school vocabulary
Grep("(consolidation|reconsolidation|systems-level stabilisation)", path="text-layer/", output_mode="content")
```

Uncovered files (new arrivals, exclusions) → a read-only agent marks "needs extraction: `sources/….pdf`" for an upstream session to extract. The text layer is an extraction artefact: complete for reading, unreliable for italics and page breaks — locate with it, never quote from it.

## 2. Note-side grep (relevance and families)

```python
Grep("reconsolidation", path="notes/", glob="*.md", output_mode="content", -C=3)
Grep("(collective memory|social frameworks of memory)", path="notes/", output_mode="content")
Grep("consolidation", path="notes/memory-studies/", glob="*.md", output_mode="files_with_matches")
```

## 3. Author tracking

```python
Glob("notes/**/Doe_*.md")
Glob("notes/**/★*.md")     # all load-bearing works
```

## 4. Metadata search

```python
Grep("^category: memory-studies/consolidation", path="notes/", glob="*.md", output_mode="files_with_matches")
```

## 5. Building a concept family

```python
# 1. both ends: which works carry the concept
Grep("trace decay", path="text-layer/", output_mode="files_with_matches")
Grep("trace decay", path="notes/", output_mode="files_with_matches")
# 2. read the branch MOC to rank candidates
Read("notes/memory-studies/consolidation/consolidation.md")
# 3. shortlist 5–10 → per-note relevance check → back to the PDFs
```

## 6. Single-family deep search (the per-family discovery seat)

```python
# you own family F_n only: expand its variants → sweep its branch → locate via notes → back to PDFs
Grep("(reconsolidat|labile trace|memory updating)", path="text-layer/memory-studies/", output_mode="content", -C=2)
Glob("notes/memory-studies/**/*.md")
Read("notes/memory-studies/memory-studies.md")   # the family's MOC entry point
```

## 7. Opposing positions

```python
# the author argues X → hunt the counter-position deliberately
Grep("(consolidation is not|against the standard model|fails to replicate)", path="text-layer/", output_mode="content")
```

Report the absence of opposition explicitly if the hunt comes up empty — silence is a finding.

## 8. When everything returns zero

1. Widen the terms (synonyms, broader/narrower, other languages in the corpus).
2. Switch branch — concepts cross taxonomy lines.
3. **Re-sweep the whole corpus root** (a note-side zero never proves the corpus lacks it).
4. Still zero → report honestly: "the vault likely lacks sources on this; suggest routing acquisitions to the Librarian."
