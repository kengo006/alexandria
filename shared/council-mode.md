# Council mode

The **whole-piece** evaluation tool, complementing the six-phase pipeline's section-level work:

- **Section-level** drafting and review → the Writer's normal pipeline (draft → discover → critique → audit).
- **Whole-chapter review, deadlock, or go/no-go decisions** → **council**.

## When to convene

1. **Chapter-complete review**: a chapter is finished — does it stand *as a whole*? One argument throughout, chapter's job done, joints to the overall thesis sound?
2. **Deadlock breaker**: a section has churned without converging; the Writer proactively proposes a council.
3. **Explicit decision** (optional): go/no-go, several viable paths, trade-offs that need to be laid on the table.

## Why independent seats

An earlier design had the lead role-play its own challengers ("wear the sceptic's hat"). It was abolished for a structural reason: **the lead already holds a position, so self-played opposition cannot escape anchoring — grading your own exam.** Council therefore uses **genuinely independent read-only seats**: each seat runs in a clean context and receives **the question plus necessary background only — never the lead's position**. That is blind review by construction. Seats only analyse; they execute nothing and write nothing.

The Searcher is unaffected: evidence retrieval was always a real, verifiable subagent task and stays one (it does not occupy an advisory seat).

## Participants

| Seat | Identity | Lens | Runs as |
|---|---|---|---|
| **Lead** | Writer | holds the base position, poses questions, synthesises the verdict | the live session itself |
| **Challenger seat** | script §A | attack premises; expose false dichotomies and wrong problem-framing | independent read-only spawn (blind) |
| **Assessor seat** | script §B | feasibility, "good enough to move on", real consequences of each option | independent read-only spawn (blind) |
| **Critic seat** | `roles/critic.md` | failure modes, downside risk, cracks in the whole argument | spawn of the Critic (its blind-commitment rule included) |
| **Searcher** | `roles/searcher.md` | evidence on demand (verbatim + pages) | normal spawn; not an advisory seat |

**Seat count**: default **≤ 2 advisory seats** per council — pick the two lenses the situation most needs (small deadlocks may take one). Opening all three, or more, is an escalation that needs the human's approval (align the cap with your governance layer's fan-out rules). A decisive council may swap one seat for a bespoke lens ("the committee reader", "the strongest opponent"). If seats genuinely need to interact live across multiple rounds, escalate to a multi-agent live session if your platform supports one — with the human's approval; the spawn-seat council remains the default.

## §A Challenger seat (spawn script)

You are the council's **challenger** (independent, read-only, analysis only). You receive the question and necessary background — *not* the lead's position or the discussion history, to prevent anchoring.
- Attack the **premises** of the question at hand: which assumption has not been examined?
- Expose **false dichotomies and mis-framings**: "are we asking the wrong question?"
- Be direct; focus on the one or two most fatal premises.
- If your challenge needs facts, mark it "needs verification" for the lead to route to the Searcher — never assert evidence from impression.

## §B Assessor seat (spawn script)

You are the council's **assessor** (independent, read-only, analysis only).
- **Feasibility / "good enough"**: is this over-polishing? Does the current version do the chapter's job?
- Assess each option's **real consequences**: time cost, contribution to the thesis, opportunity cost.
- Deliver a "minimum viable version" judgment and a "worth further investment?" call.

## Flow

1. **Lead writes the base position first**: position + three strongest reasons + biggest risk. Writing first prevents the lead from merely echoing the seats afterwards. (Blindness protects the *seats* from the lead — it does not excuse the lead from thinking first.)
2. **Spawn the advisory seats** (≤2, blind, clean contexts) → collect each seat's strongest independent case.
3. Any claim needing evidence → **spawn the Searcher** (complete passages, real pages).
4. **Synthesis, with bias guardrails**: no dismissing a view without stating why; if a seat changed the conclusion, say so; **always preserve the strongest dissent**; anti-sycophancy — a weak rebuttal may not dismiss a valid challenge.
5. **Compact verdict**:
   - chapter review → overall assessment + a fix-list;
   - deadlock → "where it's stuck + proposed break";
   - decision → consensus / strongest dissent / whether the challenger overturned a premise / recommended path.

## Output

Chapter reviews and fix-lists go to the project's `_outputs/` or directly to the author. Evidence discipline is unchanged: anything factual traces to the source via the Searcher; no support points invented from impression. Seats spawn sequentially by default; the Searcher only on demand.
