# Correction report (the no-silent-changes protocol)

Everyone stumbles on small fixable defects while doing their main task — typos, dead links, a wrong metadata field. Fixing them on the spot is efficient; the risk is *silent mutation of shared state*. This protocol allows in-lane immediate fixes while guaranteeing that **no autonomous change ever happens silently**: every fix or finding is reported.

**Scope**: changes to **already-delivered / settled artefacts** made outside the current main task, plus findings that must be escalated. In-flight work (a note being written, a chapter mid-pipeline) follows its normal process and is *not* reported here.

**The master rule: when in doubt, report (B) — don't fix (A).** Immediate fixing is a convenience door for the unambiguous, not for judgment calls.

## A or B?

**Immediate fix (A) — all conditions must hold:**
- Inside your own write permission (Librarian → vault; Writer → its own project outputs). Cross-domain is never A.
- Objectively decidable (typo, plainly dead link, metadata field contradicting the folder, obvious format breakage).
- Reversible and low-risk.
- Touches no meaning — no claims, no interpretation.
- If it involves a **quote or page number**: only if verified against the source PDF first; otherwise it is B by definition.

**Escalate (B) — never fix immediately:**
- Cross-domain (Writer spotting a vault defect; read-only roles spotting anything).
- Structural (moves, renames, folder splits, rename-chain, MOC skeletons).
- Ambiguous or interpretive (two defensible fixes; author's stance in question).
- Quote fidelity that could not be verified against the source.
- Anything cascading into multiple files, mirror alignment, or version bumps — report first, then do it as one coordinated change.

## Format

```markdown
## 🔧 Correction report — {role} | {one-line context}
> Trigger task: {what I was doing} | date: {…}

### A. Fixed immediately ({n})
| # | Location | Type | Old → New | Basis (why this is right) | Risk |
|---|---|---|---|---|---|
| 1 | `path:line` | dead link | `[[old]]` → `[[new]]` | target renamed | 🟢 |

### B. Found, not fixed — escalated ({m})
| # | Location | Problem | Why not fixed here | Suggested handling |

### C. Knock-on effects / for you to decide
- mirror alignment? version bump? MOC update? …
```

Risk flags: 🟢 trivial-reversible (glance and move on) · 🟡 please look (borderline, fixed but flagged) · 🔴 should not be in A (if it's 🔴, it belonged in B).

## Per role

- **Librarian**: main producer of A; over-threshold items go to B; reports may be folded into the errata queue.
- **Writer** (narrowest A): own delivered outputs only. **Quote and page-number corrections may be A**, on the general condition above — checked against the page image first — with the folio you saw in the Basis column and a risk flag of at least 🟡; if the correction changes whether the quote still supports its sentence, it touches meaning and is B. (Until v4.0 the Writer's A never touched quotes, because the Writer had no source access. It now takes its own evidence, so the general condition applies to it too.) Quote doubts → go back to the page image yourself: verified and meaning-neutral → A; not verifiable, or two defensible readings → B; a note-level defect it reveals → B for the Librarian. Reports ride along with the section's delivery summary.
- **Searcher / Critic**: read-only, **B only**. The Searcher's errata section (see `roles/searcher.md` §6) *is* its B, in this format.

## Where reports go

To whoever operates the system (the human, or a coordinating role): A = audit trail, revert if needed; B = decision queue, routed to the owning role.
