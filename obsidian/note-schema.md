# Literature note schema

One consistent note format is what lets every role navigate the vault without reading sources: the Writer orients by it, the Searcher locates by it, the verification scripts check it. Two variants share one discipline: **ingest** (new source) and **upgrade** (rewriting an existing note against its source). Both presuppose the Librarian's gates — above all G1: the source was actually read.

## Ingest format (new sources)

````markdown
---
title: "Full title (including subtitle)"
author: "Full name(s), verified against the PDF byline"
year: 2021                # print year; classical eras as strings ("380 BCE")
year_note: ""             # only when filename year ≠ citation year: state both and which to cite
category: memory-studies/consolidation   # full path = the note's actual folder
tags: [reconsolidation, "memory consolidation"]
note: "Publication form (journal/monograph/chapter · volume·pages · DOI) · edition caveats · one-line positioning"
source: "PDF provenance and pagination status · text-layer extraction record · citation-rule notes (e.g. no-pagination preprint → cite by section)"
read_scope: "Ingest date · what was actually read and how deep · honest statement of unread parts · quote count and locator form"
---

# Author (Year): Title

> Full citation (APA or your standard)

## Summary
Synthesised overview in your working language: core claim + method + conclusion; final sentence = what this work is *for* in your project.

## Chapter/section list (from the actual PDF · real pages or section numbers)
Per item, 1–2 sentences of real content. Empty-shell entries ("this part addresses core issues") are banned — they are the signature of a note written without reading.

## Core arguments
- Bulleted, bold-labelled; every named concept carries a precise locator (invented frameworks die here)
- Last bullet: connection to your project (wikilinked if it engages other notes)

## Related works
- [[full/path/filename|display name]] — one sentence on the relation (3–8 links; every target must exist — see wikilinks-and-mocs.md)

## Key quotes (three · real pages)
1. "[verbatim quote]" (p. X)
````

**Key-quote rules**: exactly three; chosen to represent the work's **conclusions and considered position** (not random highlights); real page numbers; kept in the original language, untranslated. These are *orientation* quotes — the Searcher still returns to the PDF for anything that enters a draft.

**Metadata discipline**: `source` and `read_scope` are mandatory honesty fields — they record where the text came from and how much was actually read. A note that reads everything says so; a note that read the TOC and two chapters says *that*.

## Upgrade format (rewriting existing notes)

Same skeleton; two blocks differ by publication type:

- **Articles**: add a faithful full translation of the **abstract** and of the **conclusion** (word-for-word, not condensed — these two anchors are where inverted-takeaway errors get caught), plus a section-by-section guide.
- **Books**: full chapter list from the actual TOC, plus 100–300-word summaries per chapter.

An upgrade always re-runs the metadata taxonomy checks (librarian §2) — upgrades exist precisely because old notes predate the gates.

## Design notes

- **Why exactly three quotes**: enough to anchor the work's position, few enough to force selection — and a fixed count is mechanically checkable.
- **Why full-path categories**: the category field mirrors the folder; `vault_verify.py` cross-checks them, catching silent moves.
- **Why translation anchors in upgrades**: abstract and conclusion are where a work says what it actually claims — faithful translation of both is the cheapest defence against summarising a work into its opposite.
