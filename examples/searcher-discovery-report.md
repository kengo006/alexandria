# Example — Searcher, discovery mode

> 🔴 **Fabricated example.** Every work, quotation and page number here is invented; see [`README.md`](README.md). Copy the shape, never the content.

**The request it answers** (what the Writer sent):

```
You are the Searcher (discovery). You own ONE concept family:
[F2: "the productive account of memorials" — seed terms: produce/constitute/
performative, seed authors: Doe, Roe].
The passage you serve: "Monuments do not preserve a memory that already exists;
they are one of the things that bring it into being."
```

---

## Literature match report

### Core proposition (my reformulation)

The passage claims a **constitutive** relation, not a **preservative** one: the monument is a condition of the memory rather than a container for it. Two commitments follow that the sources must be able to bear — that the memory does not fully precede the monument, and that this is a claim about how public memory forms, not about what individuals happen to recall.

### Primary recommendations (HIGH relevance)

- [[sources/memory-studies/Doe_2011_Archives of Memory|Doe (2011)]] — states the constitutive claim directly, and in the strong form the passage needs.
  - Quote: "A monument does not hold a memory the way an archive holds a document. It is one of the operations by which a public comes to have that memory at all — which is why the argument over what to build is never merely an argument over how to commemorate." (Doe, 2011, **p. 47**)
  - 📄 Source: `sources/memory-studies/Doe_2011_Archives of Memory.pdf` p. 47 (read from the PDF)
  - 🎫 Image credential: rendered PDF page 61, printed folio **47** (offset +14, registry row verified)
  - ✓ 4-layer: correspondence / not-secondhand / settled position / entity attribution — **all pass**. Entity note: the sentence is Doe's own analytical assertion, not a position she is describing.

- [[sources/memory-studies/Poe_2005_On Assembly|Poe (2005)]] — the same relation reached from the other side (assembly rather than object); useful because it stops the claim from reading as a thesis about stone.
  - Quote: "What gathers people is not the thing in the square but the occasion the thing supplies; remove the occasion and the object is only large." (Poe, 2005, **p. 208**)
  - 📄 Source: `sources/memory-studies/Poe_2005_On Assembly.pdf` p. 208
  - 🎫 Image credential: rendered PDF page 104, printed folio **208** — ⚠ **this work is a two-up scan** (one sheet carries two printed pages; left = 2 × sheet − 0). The folio was read off the image, not computed.
  - ✓ 4-layer: all pass.
  - ⚠ **Registry**: this file is listed under `unreliable_order` — grep on it is fully reliable, but **nothing adjacent to a hit may be read as context**. The quotation above was taken from the page image, not from the text layer, for that reason.

### Background (MEDIUM relevance)

- [[sources/memory-studies/Ives_2014_Ruins and Registers|Ives (2014)]] — supplies the vocabulary distinction (preservative vs. productive) the passage is implicitly using, without arguing for either.

### Opposing / complicating positions — **mandatory, never blank**

- [[sources/memory-studies/Roe_1998_Commemoration and Its Discontents|Roe (1998)]] — argues the reverse: that monuments are built *because* a memory already has a constituency, and that treating them as generative mistakes an effect for a cause.
  - Quote: "Nothing is raised in a public square that did not already have people willing to raise it. The stone is downstream of the wanting." (Roe, 1998, **p. 12**)
  - 📄 Source: `sources/memory-studies/Roe_1998_Commemoration and Its Discontents.pdf` p. 12
  - 🎫 Image credential: rendered PDF page 12, printed folio **12** (offset 0)
  - 🔑 **This is the strongest available objection and the draft does not currently answer it.**

### Pending verification (honest gaps)

- [[sources/memory-studies/Halvard_1987_Public Grief|Halvard (1987)]] — a passage on p. 90 looks directly relevant, but the render path returned an error and I could not confirm it:
  `page-render tool: failed to open document (xref table malformed)`
  ⇒ reported as **🟨 text-layer candidate — not PDF-verified**. Not quotable in this state; routed upstream.
  ⚠ Note: the failure is a *rendering* failure, not an absence. Do not record this work as "nothing found in it".

### Concept-family cross-links

`constitutive` ⇄ `performative` ⇄ `world-making` — Doe (2011) and Poe (2005) use the first two interchangeably; Ives (2014) treats them as distinct and would object to the substitution. If the draft leans on the equivalence, it needs a sentence saying so.

### Evidence sufficiency (group-level rubric)

| Dimension | Assessment |
|---|---|
| On-topic | Strong — all four cited works address the constitutive claim directly. |
| Diversity | Adequate — two supporting, one opposing, one definitional; single research tradition, however. |
| Concreteness | Strong — three direct quotations at verified pages. |
| Completeness | **Weak on one axis**: nothing here is empirical. Every source is conceptual, so the passage is currently supported only by other people's arguments, not by any case. |

### Caveats

- Searched: `sources/memory-studies/` and `sources/public-history/`, English and the other working language, with the variants `produce / constitute / performative / world-making / bring into being` and their nominal forms. **Not searched**: the periodicals folder (no page-anchored text layer at present).
- The Poe (2005) quotation sits mid-page and is unaffected by the page-opening rule; the Doe (2011) quotation is also mid-page. **Neither is a page-block opening**, so neither carries the one-in-five chance of belonging to the previous page.
