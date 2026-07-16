# Optional integrations

Three capabilities the upstream system runs as local tools. They are **documented as interfaces, not shipped**: each section states what the capability contributes, the contract it must satisfy, and where it plugs in. Build each with whatever tools you prefer — the roles already know how to use them when present, and degrade gracefully when absent.

## 1. Full-text corpus layer (recommended first)

**Contributes**: corpus-wide grep (find *which work, which passage* across everything you own) and a complete reading surface — the built-in PDF readers of agent harnesses can silently truncate malformed PDFs while misreporting page counts; a pre-extracted text layer removes that failure mode from everyday reading.

**Contract**:
- A `text-layer/` tree mirroring `sources/` file-for-file: `text-layer/<branch>/<same-name>.txt`.
- Produced by any extractor (`pdftotext` works well for born-digital; OCR for scans); include page markers (e.g. `===== page N =====`) so hits map back to pages.
- **Known trap — footer pagination shifts by one**: when a work prints its page numbers at the foot, extractors attribute the number to the *following* page's text flow, so the layer's "page N" is printed page N−1, consistently through the whole book. Header-paginated works are unaffected. The layer stays a *locator* either way (the page you cite is the one printed on the PDF page you opened — `roles/searcher.md` §1), but knowing the offset saves a batch of false "wrong page" audit failures.
- Git-ignored (derived data, and your sources' copyright stays local).
- Re-extract on PDF replacement; rename together with the source (it is step 8 of the rename chain).

**Plugs into**: Searcher step 1 (corpus grep), Librarian large-work reading, `shared/search-patterns.md` throughout. **Status in roles**: positioning only — never a citation source.

## 2. Semantic recall

**Contributes**: paraphrase- and cross-lingual recall that literal grep cannot reach (querying in one language, recalling passages in another; concept matches under different wording). In upstream production, queries in the author's working language routinely recalled English passages that no keyword variant hit.

**Contract**:
- An index over the text layer, exposed to read-only agents as a search tool (an MCP server works well): `search(query, k) → fragments with {file, page_start, page_end, score, text}`.
- Fragments are **pointers**: roles follow file+page back to the PDF. Recall-only; never a citation source.
- Index freshness is owned by the Librarian's routine (update on ingestion; note that a stale index means *semantic silence never proves absence* — grep remains the backstop).
- Prefer small local embedding models (multilingual if you work across languages); keep the whole thing offline.

**A runnable implementation** of this contract is published as a companion: [alexandria-semantic-recall](https://github.com/kengo006/alexandria-semantic-recall) (MIT) — the recipe below, packaged. Read on if you would rather build your own.

**Reference recipe** (the upstream production stack, shared so you don't have to guess): [fastembed](https://github.com/qdrant/fastembed) running an ONNX multilingual model (`paraphrase-multilingual-MiniLM-L12-v2`) for embeddings — CPU-only, no PyTorch — over [LanceDB](https://github.com/lancedb/lancedb) as the vector store. Chunk the text layer with its page markers preserved, so every fragment maps back to `{file, page}`. In upstream production this combination indexes ~400k chunks on a 16 GB laptop, with incremental updates running in about 90 seconds. A minimal MCP server exposing a single `search(query, k)` tool is all the roles need.

**Plugs into**: Searcher search path D; Researcher's coverage scans. Degrades to grep when absent — every role treats it as a bonus, not a dependency.

## 3. OCR escalation path

**Contributes**: usable text layers for scanned sources, and a quality ladder for hard pages.

**Contract**:
- Tier 1: standard OCR (e.g. tesseract) for whole scanned works → text layer with page markers, flagged as OCR (noisy; positioning only).
- Tier 2 (optional): a stronger model (e.g. a vision-language OCR) for *selected hard pages* — dense footnotes, critical italics, complex layouts — invoked per page range, never as the bulk default. If your hardware is memory-constrained, batch pages in small chunks and **verify output page counts against the PDF** (silent page-dropping with a success exit code is a real failure mode; treat count mismatch as an error).
- Output lands next to the source or in the text layer, marked as OCR.

**Plugs into**: Librarian ingestion (G1 step 4) and the Searcher's scanned-source handling (verify quotes against page images; OCR text locates only).

## Adding your own

Whatever you integrate, apply the same two tests the three above pass: **(a)** the roles must degrade gracefully without it, and **(b)** it must never become a citation source — the source-tier table (`roles/searcher.md` §1) admits only the source itself.
