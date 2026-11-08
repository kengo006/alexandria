# Tools

Scripts for steps the role files already require. Each rule below was written first and stood on its own: the
step can be done by hand, as described in the file that states it. These tools make it repeatable, and two of
them make it practical at all (a retraction screen and a registry check are hard to do by hand on a few hundred
sources).

Every tool takes `--self-test`, which shows it telling known good cases from known bad ones on synthetic data.
It ends `N of N as expected`; checks that need a missing optional package are named and counted as skipped,
and a self-test that could run none of its checks exits 2. Read a tool's docstring before trusting its output: each one states what it cannot see, and prints that limit
with its results so a quiet run is not read as a clean one.

| Tool | The step it serves | Where the rule lives | Needs |
|---|---|---|---|
| `crossref_lookup.py` | resolve a work against CrossRef at ingestion; file the DOI only on a confident match | `roles/librarian.md`, "Registry check and retraction screening" | network² |
| `retraction_check.py` | screen the sources a draft cites (or the whole library) against the Retraction Watch data, with the denominator stated | `roles/writer.md` Phase 3 filing gate and Layer 1; `roles/librarian.md`, same paragraph | network (data cached 7 days) |
| `folio_probe.py` | find printed page numbers from the PDF's layout; test whether the offset is constant before registering it | `shared/evidence-handbook.md` §1, page offsets; `shared/page-offset-registry.md` | PyMuPDF¹ |
| `measure_page_offset.py` | the same question from a text layer's page anchors and running heads | as above | — |
| `split_2up.py` | split a two-up scan into one printed page per PDF page (refuses rotated sources on the lossless path) | `roles/librarian.md` §8, page-anchor gate; `shared/evidence-handbook.md` offset ③ | PyMuPDF¹ |
| `citation_ledger_check.py` | every page-bearing citation in the text has a ledger row, and the row covers that page | `roles/writer.md` §8, the ledger | — |
| `ledger_to_bibliography.py` | build the reference list from the ledger and the notes instead of retyping it | `roles/writer.md` §8; Phase 6 bibliography check; Layer 1 | optional: pandoc, network (`--enrich`) |
| `note_page_range_gate.py` | the pages a note cites exist in the PDF actually filed (a replaced, shorter version leaves them dangling) | `roles/writer.md` §5, page precision | PyMuPDF¹ |
| `d4_quote_check.py` | the quotations in the notes are in the source's text layer (present / exactly findable) | `shared/evidence-handbook.md`: the text layer locates; `obsidian/note-schema.md`, key quotes | — |

¹ `pip install pymupdf`, or prefix the command with `uv run --with pymupdf`. It is not small: PyMuPDF 2.0 brings
in onnxruntime, numpy, networkx and its own layout packages, about 290 MB in a fresh virtual environment with pip and
about 244 MB with uv (which does not compile `.pyc` files by default). The other tools use the standard library.
² Set `CROSSREF_MAILTO=you@example.org` to join CrossRef's polite pool. A rate-limited request (HTTP 429) exits
3 like any network error: wait and run it again; nothing is filed on an error.

Conventions the tools assume (all from this repository's own files): notes are `{Author}_{Year}_{Title}.md`
under `notes/`, PDFs mirror them under `sources/`, text layers under `text-layer/` (`obsidian/vault-structure.md`)
with `===== page N =====` anchors (`optional-integrations.md`, the text layer); the vault map
(`notes/vault-map.md`) and each folder's MOC are not literature notes, so `d4_quote_check.py` and
`retraction_check.py` set them aside and say how many; a project keeps its citation ledger in `ledger.md` with a
`source` column (`roles/writer.md` §8), and `citation_ledger_check.py` reads the text from its
`working-source.md`, `reading-copy.md` and `chapters/` (the layout in §0); a note may carry `doi:` in its front
matter (`obsidian/note-schema.md`). Paths are arguments, so a different layout only changes the
command line.

The text-layer tools — diagnosis and repair of a PDF-derived corpus, comparing two extraction paths or two
witnesses, comparing a scan's own OCR layer with a fresh OCR — are in the companion
[alexandria-corpus-doctor](https://github.com/kengo006/alexandria-corpus-doctor).

```bash
python3 tools/retraction_check.py --project drafts/chapter-1 --notes notes --md
python3 tools/citation_ledger_check.py --project drafts/chapter-1
python3 tools/folio_probe.py "sources/memory-studies/Doe_2011_Archives of Memory.pdf"
python3 tools/crossref_lookup.py "Archives of Memory" --author Doe --year 2011
```
