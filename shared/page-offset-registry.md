# Page-offset registry (template)

A durable, **append-only** data table: one row per work whose printed↔physical page offset has been verified on a rendered page. Roles consult it *before* taking page numbers from a work (compute the offset once, reuse it book-wide) and append a row after verifying a new work.

**Why this file carries no version number — deliberately.** It is a *data table*, not a rules file: bumping a version per appended row would be absurd, and "how complete is this registry" is countable (count the rows). The *rules* about offsets live in `roles/searcher.md` and change under version control there; this file only accumulates verified facts.

## Iron rules

- **No row without a verification anchor.** A row without one teaches the next reader a guess as a fact — exactly what this registry exists to prevent.
- **Offsets have no default value.** Production observations span **−743 to +63**: long front matter drives it into positive tens; copies cropped of their front matter dip *negative*; scans bound from journal runs sit **hundreds negative** (continuous journal pagination outruns the PDF). Never probe ±1 and call it verified.
- **2-up scans get a formula, not a number** (left page = 2 × PDF-page − N). The tell: the PDF's page count is roughly half the work's printed pages.
- **Found an error in an existing row → report it to the registry's owner; do not edit in place.** Append-only files shared by several roles are concurrency hotspots.

## Registry

| Work | Offset (physical − printed) | Verification anchor |
|---|---|---|
| Doe (2011), *Archives of Memory* † | +14 | physical p.20 → printed "6"; two-column layout; ch. 1 opens at physical p.15, number suppressed there — computed from p.20 |
| Roe (1998), *Commemoration and Its Discontents* † | 2-up: left = 2×PDF−4 | PDF p.30 renders printed pp. 56–57 side by side; count tell: 178 PDF pages vs. ~340 printed |
| *(append verified rows here; never delete)* | | |

† Illustrative placeholder rows — replace with your first verified works.
