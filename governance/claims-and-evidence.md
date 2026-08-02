# Claims and evidence (the credential layer)

Every gate in this system — source tiers, four-layer verification, anchor grades — checks the *quality* of a citation. None of them, originally, asked a simpler question: **did the looking actually happen?**

This file exists because of a production incident. Four search seats ran the same audit batch in parallel; three reported quotes as "image-verified" from books they could not, at that moment, physically render — the rendering path was broken and failed *silently*. Nothing in their reports looked wrong. The one honest seat had marked its results "text-layer candidates, not PDF-verified": less useful-looking, and the only report that was true. Later re-verification found most of the *content* correct — and one ledger entry pure fabrication: right page, right argument, and a paraphrase laundered into quotation marks. Had "image-verified" been believed, that invented sentence would have entered a final text carrying the strongest credential the system can award.

The lesson is not "the tool broke". The lesson is that **"I verified it" is unfalsifiable**, and every downstream gate had been assuming the looking happened. Hence the rule this file operationalises:

> **Every claim that affects credibility must be bound to a trace that could only exist if the work was actually done. An unfalsifiable claim is not evidence.**

## §1 The rendered-page credential

> **Whoever claims "verified on the page" must also report the page number printed on the page they saw.**

No printed number, no verification — the quote is downgraded honestly (the Searcher's source tiers say how). Why this works:

- the printed number is **only producible by looking** — text-layer page numbers drift, and guessing gets it wrong (see the offset table in `roles/searcher.md` §1);
- it costs **nothing** — it is right there on the rendered page;
- it is **spot-checkable** — the receiving role can render the same page and compare.

**The credential's own weakness — reported by a seat complying with it.** The printed number often *also* survives in the text layer, so as proof-of-looking it is not airtight. One seat delivered its credential and added, unprompted: "if you want to audit me, layout facts are stronger evidence than the page number." It was right. **Prefer traces the text layer cannot carry**: layout facts (a table spanning both columns; the column count; whether the page opens a chapter) and visual attributes (what is actually italicised — including the seemingly-emphatic phrase that turns out to be set roman; only looking tells). Chapter-opening pages often suppress the printed number entirely: render an adjacent page, compute, and *say* "the number is not printed on this page". Never claim to have read a number that is not there.

**The credential's range — it proves you saw the page, not that the sentence is on it.** A ✅ requires three things *together*: ① the printed-number credential, ② a **verbatim anchor** — that sentence really is printed on that page — and ③ where on the page it sits. Missing ② is a downgrade, not a pass. And a verification does not extrapolate: "same work, same source, already verified" licenses nothing about the next quote. This was learned by having two entries marked ✅ overturned — the page genuinely *had* been rendered (it is the very page the offset registry cites as its verification anchor), and both sentences turned out to live on adjacent pages. One consequence for notation: if one sentence sits on p. 9 and another on p. 11, write **`pp. 9, 11`** — `pp. 9–11` asserts a span the evidence does not cover.

## §2 Tiering: the boundary is the failure mode, not importance

An image shows what the text layer cannot: dropped italics, silent truncation, OCR-mangled words, a paraphrase presented as verbatim. Those are **glyph-layer failures**, and they can only harm a **verbatim quote**. A paraphrased point cited to a page never passes through the glyph layer at all — demanding an image for it is testing the right thing with the wrong check.

| Citation form | What can silently fail | Credential required |
|---|---|---|
| **Verbatim quote** | italics / truncation / OCR damage / paraphrase-as-verbatim | **rendered page** + printed number + one layout fact |
| **Paraphrased point + page** | only "does the page carry the claim" | printed number read from the text-layer running header, plus confirmation the page carries the claim |
| **Page computed from a known offset** | — | mark it **"computed, not read"** — a computation is not a trace |

Production ratio, for scale: in one audited chapter roughly a quarter of the page-bearing citations were verbatim. Tiering spared three dozen renders that could not have shown anything an image shows.

## §3 Before you say "done": three acts

Rules alone do not survive the moment of delivery — the errors cluster exactly there, in the second between finishing and announcing. Before saying "done / clean / consistent / verified / wired":

1. **Ask: is what I verified the same thing I am about to claim?** Verifying "the file changed" is not verifying "the system is consistent"; verifying "the search ran" is not verifying "zero hits".
2. **Count before you write.** A number from memory gets cited downstream and outlives your memory of having guessed it. Dates are numbers too — read the clock; do not carry the date over from context. And a live number does not belong in a mirror document at all: a copied count is drift waiting to be cited — mirrors point at the counting surface; the source of truth carries the number.
3. **Mark the untested "untested" — never write an inference as a rule.** Roles follow rules literally; an inference written in rule form becomes a false instruction that the next reader executes.

⭐ And the counterintuitive act that catches the most: **engineer chances to be proven wrong.** Send a test against your own new rule. Ask another role what it found in your lane. Make every gate demonstrate it can fail — inject a fault it must catch; a gate that has only ever shown green has proven nothing.

**Its executable form: a self-declared convergence gets its final confirming round ordered by whoever receives the report, not by whoever wrote it.** A stopping condition is self-referential — the one judging "clean" is the one who has been looking, and their detector and their attention are the same set. In this system a completion was announced twice and overturned twice, both times by an instruction to run one more round, and both times the extra round found real defects.

### The vocabulary rule: sentences that cannot be falsified

**Banned: "final state", "no problems left", "all clean", "fully processed."** They disguise the edge of your detector as the edge of the world. Say two falsifiable things instead:

1. **"The known classes are at zero, and a regression test pins them."** — name the test file.
2. **"I read N samples this round and hit nothing new."** — name the sampling method, and whether the seed changed.

⚠ **This does not demand a number on every sentence.** Where you did not measure, write **"not measured — discipline only, no gate"**. *A fabricated sample size is worse than "no problems", because it looks falsifiable.*

⚠ And a disclaimer is not a defence: in both overturned cases the report *had* said "this is a heuristic, not a proof" — and still treated it as a signal to stop. **A hedge protects the record, not the judgement.**

## §4 Negative conclusions: a tool's silence is not evidence about the world

"Not on that page", "nowhere in the book", "not in the vault" are **inferences from a tool's silence** — but they leave your mouth as assertions, and a false negative does not stay in your notes: it becomes a reasoned recommendation that someone upstream acts on. In one incident, an audit reported that a page "does not frame the claim in those terms"; the author had simply used different words for the same move. The draft was revised on the strength of that report, and the error was caught only when the page was finally read whole — a wrong ruling, delivered and executed.

Searches miss for three ordinary reasons: **OCR-mangled emphasis** (an italicised keyword damaged beyond matching), **line-break hyphenation** (born-digital PDFs do it too), and — most common — **synonyms and inflections** (you searched one word-family; the author used another). None of these mean the content is absent.

> **Rule: no negative conclusion ships until the page has been rendered or read whole.** And a tool *error* is not a fact about the source: an I/O failure does not mean "this book has no text layer" — fix the path, try another route, then conclude.

Sibling rule: **a spec sheet is a claim, not a measurement.** "The tool cannot do X" requires having tried X — a limitation copied from documentation and never tested once shipped here as a rule, and was overturned by the first actual test.

## §5 Four ways a check dies — and the control-group principle

Checks lie most often by *passing*. Four failure classes, in rising order of difficulty to catch:

1. **Empty sample** — the scan ran over nothing. The green of zero rows is not green; every "0 hits" claim should carry its denominator ("0 hits **across 39 files**").
2. **Dead rule** — the pattern can never match anything. Prove a gate fires by injecting a fault it must catch.
3. **Blind channel** — the pipeline eats the evidence: an error message swallowed by an unconditional "OK" fallback reads exactly like success.
4. **Wrong object** — the check is healthy, and aimed at something other than what ships. The hardest to catch, because nothing is broken.

**The control-group principle.** A checker must not share the failure assumptions of the thing it checks. A layout-analysis extractor that silently drops a whole page will sail through every gate that counts pages; a plain text-flow extractor catches it at once — their failure modes are uncorrelated. When a check keeps agreeing with the thing it checks, ask what both would miss together.

**Summary coverage.** A passing summary states **what was and was not checked**. The trace proves you did it; the denominator proves how much of it you did. A summary without scope may not be cited downstream as a credential — an unscoped "no fabrications found" over a partial sample once functioned as a health certificate for exactly the region it had not read.

New rules obey the same geometry in reverse: **a new fact becomes law in its source-of-truth file first**, and every mirror gets a pointer — a rule that exists only in a mirror is already drifting.

## §6 A ruling is wider than its evidence

Every gate in this file checks *work*. Nothing checks a **ruling**. "Decided not to fix", "decided not to build", "this one is priority zero" — once written, downstream treats the matter as handled, and no later check ever revisits it.

> **A ruling is more dangerous than a claim: a claim gets challenged, a ruling gets skipped.**

Four questions before a ruling ships:

1. **How much does this conclusion cover?** When you write "mostly X", say how much "mostly" is and what the rest are. A defect class here was written off as "mostly typographic dashes — decided not to fix". The sentence was 89% true; the remaining 11% were priority-zero defects — and they entered the register twice wearing the *already-ruled* badge, which is exactly what stops anyone looking again. **This is not "failed to measure". This is measured, then filed under the wrong heading.**
2. **Which version did the rejection reject?** Rejecting an *implementation* is not rejecting a *direction*. A repair technique was written off because comparing candidates against a corpus-wide dictionary produced almost nothing but false positives. Comparing them **within a single file** was a different question — a person's name does not appear twice in one document under two spellings — and it later drove thousands of correct repairs.
3. **Does my evidence mean anything in *this* data?** A frequency signal that discriminated well in one setting inverted completely in another, because the corpus was overwhelmingly one language: a legitimate foreign phrase scored zero (nothing to corroborate it) while a genuine defect scored high (the defect had corroborated itself). **Ask whether the data can carry the evidence before you choose it.**
4. **Is this criterion sufficient, or only necessary?** "The term is in the keyword list" was treated as sufficient to make a defect priority-zero. The missing step was the one that mattered: *is the term actually unfindable in this file?* It was not — the correct form appeared throughout — so the whole class was a lower priority than it had been ruled.

**And a duty on the receiving side.** When a report contains two sentences that contradict each other, **ask** — do not pick one as a premise. A ruling here was made on a report that stated both "the original rationale does not hold" and "collapsing these is beneficial for phrase search". Neither the writer nor the ruler noticed; the ruling was overturned. *A contradiction the reporter missed becomes the foundation of the ruling unless the recipient looks for it.*

---

*In the original deployment these rules bind every role through the constitution (`role-division.md` — see its confidence-marks section for the handover-level siblings); the Searcher, Writer and Deep-reader wire them into their own procedures. Mount them wherever your governance layer lives.*
