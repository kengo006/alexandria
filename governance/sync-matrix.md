# Sync matrix (anti-drift)

Prompt systems rot in a specific way: **a fact lives in more than one file, and an upgrade touches some copies but not all.** Each survivor tells a different story; agents read whichever they hit first. The counter-method has three parts.

## 1. Mirror reduction

Before managing mirrors, minimise them:
- **Numbers live only at their source** (counts, thresholds, section-tallies). Everything else refers by *name* without the number ("the rename chain", not "the 9-point rename chain") — names survive upgrades; numbers don't.
- Index files (READMEs, quick cards, wrapper digests) carry **pointers and one-line digests**, never rule bodies.
- If you find yourself copying a paragraph between files, stop: one of them is the source; the other gets a link.

⚠ **And mirror-checking has a hole where you would least look for one: the change record itself.** A file's version number can be mirrored correctly into every place the matrix names while that file's own changelog silently stops being written — the last entry ages, nothing disagrees with anything, and every mirror check stays green. Measured in the upstream system while preparing this release: of seven canonical rule files, **four had a changelog whose newest entry predated the version in their header — eighteen rule changes with no record**, the worst of them thirteen. ⚠ **That count was first written as nineteen**, arrived at by subtracting the changelog's newest version number from the header's. Enumerated one by one it is eighteen: **one number in that span was never issued.** 🔑 A version *number* is not a version, and the distance between two numbers is not a count of the things between them — **which is the same substitution this whole section is about**, committed while writing the section. 🔑 **The gates verify that the number was copied, not that the change was written down.** The most-affected file was also the most actively edited one, which is the shape to expect: the record stops where the work is heaviest.

## 2. The matrix

List every fact that *must* live in more than one place, with all its mirror locations. When you upgrade the fact, walk its row. The skeleton's own matrix:

| Fact that can drift | Single source | Mirrors to walk on upgrade |
|---|---|---|
| Quote iron rule (source tiers, four layers) | `roles/searcher.md` | README pipeline section · `governance/system-overview.md` rules table · `shared/search-patterns.md` header · `shared/summon-templates.md` spawn prompts · `integration/agents/searcher.md` digest |
| Six-phase pipeline shape | `roles/writer.md` | README · GETTING-STARTED walkthrough · `governance/role-division.md` diagram · Writer wrapper digest |
| Council mechanics (independent seats) | `shared/council-mode.md` | `roles/writer.md` mode row · `roles/critic.md` §5 · Writer wrapper digest |
| Naming / star / rename chain | `obsidian/vault-structure.md` | `shared/naming-conventions.md` card · `governance/system-overview.md` rules table |
| Role boundaries | `governance/role-division.md` | each `roles/*.md` boundary section · wrapper digests |
| Writer's information sources (what it may read; what it re-checks before shipping) | `roles/writer.md` §1 | README role table **"never" column** · `governance/role-division.md` role table + read/write boundary · `governance/system-overview.md` rules table · `roles/searcher.md` header · `integration/agents/searcher.md` · Writer wrapper `description:` **and** digest · `shared/summon-templates.md` Writer prompt · `shared/council-mode.md` evidence line |
| Note schema fields | `obsidian/note-schema.md` | `roles/librarian.md` pointers · `governance/scripts/vault_verify.py` regexes |
| Rendered-page credential + tiering | `governance/claims-and-evidence.md` | `roles/searcher.md` §1 honest-downgrade · `roles/writer.md` Phase 6 image spot-check · `roles/deep-reader.md` §2 · `governance/role-division.md` audit-summary coverage · README governance list |
| Page offsets (three kinds, stacking) and page-anchor shapes | `roles/searcher.md` §1 | `shared/page-offset-registry.md` iron rules · `roles/writer.md` Phase 6 · `roles/deep-reader.md` §2 and §4 · `integration/agents/searcher.md` digest · Searcher wrapper digest |
| Mandatory report sections (which ones, and that "none" must be written) | `roles/critic.md` §4 and `roles/searcher.md` §3 | `integration/agents/critic.md` · `integration/agents/searcher.md` · Critic and Searcher wrapper digests · `shared/summon-templates.md` spawn prompts |
| Degradation registry: category set and self-report shape | `shared/degradation-registry.md` | `optional-integrations.md` §2 contract · `roles/searcher.md` §1 registry step · `roles/librarian.md` §8 |
| The credential's floor (sources whose printed page is itself defective) | `governance/claims-and-evidence.md` §1 | `roles/searcher.md` folio discipline · the registry's per-entry flag · Searcher wrapper digest. ⚠ **The upstream rule and this one are separately worded**, not one copied from the other — which is precisely the condition this matrix exists to track, and the row was added the day the second wording appeared rather than the day it drifted. |

Adopters extending the system: **add a row the moment a new fact gains a second home.**

## 3. Upgrade discipline

Every rule change, mechanically:
1. Edit the **single source**; record the change in that file's changelog with date and reason.
2. If your files carry version numbers, bump them — and mirror version numbers only in the places your matrix names.
3. **Walk the fact's matrix row**: update every mirror in the same session as the source.
4. Check the wrapper/agent digests (`integration/`) — digests are the most-forgotten mirror class. (The upstream system's audit found exactly this: a mode was redesigned, every document updated, and the wrapper digest still taught the abolished behaviour weeks later.)
5. **Confirm the changelog entry exists** — the version you just bumped to must appear in that file's own changelog section, not only in its header. Mirrored version *numbers* going green says nothing about whether the *record* was written; see the note under `health_check.py`.
6. Run `governance/scripts/health_check.py` — it mechanises what it can (files present, forbidden patterns absent, optional version-mirror equality, optional changelog-entry presence).

## 4. Reversing a rule — the case the other three do not cover

Replacing a rule with its opposite is not a bigger edit; it fails in a different place. Two verification habits that serve everywhere else are **structurally blind** to it:

- *Check that the new text is present.* It is. **Pass.**
- *Check the diff's minus side for anything lost.* Nothing was. **Pass.**

🔑 **What is wrong was neither added nor removed — it is the old copy you never touched.** Both habits are built around the passage you edited, and the drift lives in the passages you did not.

⇒ **A third direction, mandatory whenever a rule is reversed: verify that the abolished wording is gone.**

**Your scan's domain has three dimensions, and missing any one turns a "0 hits" into "my ruler does not reach there".**

1. **The pattern's boundary** — the regex itself.
2. **The path range.** 🔴 **Copies live outside the document tree.** Agent definition files (`integration/agents/*.md` here) are loaded into a subagent's system prompt on **every** spawn — more load-bearing than any document, and the easiest thing to leave out of a `grep` path list. Upstream, an abolished rule was declared cleared from the docs, and the ninth copy was found afterwards in an agent file, still stating the rule verbatim.
3. **The number of phrasings.** One rule is said several ways. Enumerate the families *before* scanning — negative ("never reads", "may not read"), exclusive ("the only window", "only through you"), delegating ("via the Searcher", "left to the Searcher") — and expect to have missed some.

🔑 **"Find one, fix one, grep again" is the worst way to converge.** Every round feels nearly finished, and you never learn the denominator. Upstream this ran three rounds — eight places, then a ninth, then five more — until an enumerated multi-family scan closed it in one pass.

**Every hit is then classified by a human into exactly one of three:**

| Class | Action |
|---|---|
| **① still asserting the old rule** | 🔴 change it — this is the drift |
| **② quoting the old wording to say it is abolished** | ✅ keep — this is the *correct* shape; readers need to know it changed |
| **③ a changelog / history entry** | ✅ keep — history is the audit surface |

⚠ **Run the positive control in the same pass**: every file that should now carry the *new* rule does. Verifying that the old wording is gone and verifying that the new wording landed are independent facts; neither implies the other.

### What this file gets wrong about its own method

This section was applied to this repository the day it was written, and it is worth reporting what happened, because the failure is the instructive part.

An enumerated three-family scan over the tree returned **8 places**. Reading every line in the tree that mentions the object at all — a bounded denominator, 110 lines — returned **14**. The six it missed took three shapes:

- **The elided verb.** `source PDFs never` — a prohibition with no verb in it, so every pattern built around *read* walked past.
- **The rationale paragraph.** The rule was updated; the two sentences explaining *why* the rule existed were not. They are not phrased as rules, so a rule-shaped pattern does not see them — and they are what a careful reader trusts most.
- 🔴 **The table cell under a "Never" heading.** Two role tables — in the README and in the constitution, the two most-read files — carry a column headed **Never**, and the cell beneath it read `reads source PDFs`. **The negation is not in the sentence; it is in the column header.** A line-scanning tool cannot see it. Worse is the mirror image: a positive control phrased as *"does the tree now say the Writer reads the source?"* would have **counted those two cells as evidence that the new rule was already in place**.

⇒ **The scanner's job is to make a large space searchable; it is not entitled to declare the space empty.** Shrink the denominator until a person can read all of it, run the scan *inside* that denominator, and let the person adjudicate. A sample that finds nothing and a domain that contains nothing produce the same report.

## Exclusion-zone versioning (nothing silently deleted)

When a rule is *replaced*, don't delete it — move it to a marked exclusion zone (the file's changelog, or a dedicated section) with: what replaced it, when, and why. Two payoffs: the system remembers *why* it changed (arguments don't get re-litigated from scratch), and stale copies elsewhere are traceable to a dated decision instead of being ambiguous. The rule of precedence is always: **new overrides old; old is preserved as history, marked as superseded.**
