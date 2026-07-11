# Naming conventions (cross-role quick reference)

> **Single source of truth = `obsidian/vault-structure.md`** (naming rule, author forms, year policy, star convention, rename chain). Executing names and renames belongs to the Librarian; every other role only needs to *read* filenames and *write* links correctly. This card is the quick reference — it deliberately restates no rule in full.

## Reading filenames

- `{Author}_{Year}_{Title}.{md|pdf}` — two authors `A & B`, three+ `A et al.`; subtitles joined with ` - ` (no colons in filenames).
- Classical era years: `380BCE` in filenames (no space); `"380 BCE"` in metadata (with space).
- **Filename year may differ from citation year** (lectures, interviews, preprints kept under their original filename): the note's `year_note` field states both and which to cite.

## The star asymmetry (the most-tripped-on rule)

- `★` lives **only on the note-side filename**; the PDF never carries it.
- ⇒ a wikilink to a starred note **includes the star**; deriving the PDF path from a note name **strips the star first** — forgetting this is the classic file-not-found cause for read-only agents.

## Writing links

```markdown
[[branch/sub/Author_Year_Title|Author (Year)]]
[[branch/sub/★Author_Year_Title|Author (Year) ★]]   # starred note keeps its star
| [[path\|alias]] | … |                              # escape the pipe inside tables
```

- **Never construct a path from memory** — glob the folder and copy the exact filename (`obsidian/wikilinks-and-mocs.md`, four-step).
- **Never** use bare-basename shorthand links in prose — plain text "Author (Year)" or the full-path link.

## Common errors

| Wrong | Right |
|---|---|
| `Doe, J. - 2019 - Title.pdf` | `Doe_2019_Title.pdf` |
| `Doe_2019_TDMoM.md` (abbreviated title) | `Doe_2019_The Trace Decay Model of Memory.md` |
| `(unidentified)_2023_….md` | resolve the author before filing (Librarian gate G3) |
| PDF path copied from `[[★Doe_2019_…]]` | strip the star: `sources/…/Doe_2019_….pdf` |
