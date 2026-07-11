# Style modules

The skeleton's prompts are English and voice-neutral by design. Everything language- and voice-specific — punctuation conventions, banned constructions, rhetorical quotas, terminology conventions, idiom policy, tone samples — lives in a **style module**: one file per language/voice, plugged into the Writer.

## Where a module loads

1. **Summon time**: the Writer's launch template reads the project's module (see `shared/summon-templates.md`, Template W step 3).
2. **Phase 1 (drafting)**: the module's rules constrain the draft as it is written.
3. **Pre-delivery self-check**: the module's checkable rules join the Writer's internal checklist (`roles/writer.md` §4, Step "pre-delivery").

The Writer's core disciplines (citation completeness, questioning protocol, no decoration words, rotation) are *not* module material — they hold in every language. A module carries only what changes when the language or voice changes.

## What a module may contain

| Block | Examples |
|---|---|
| **Punctuation** | full-width vs half-width rules for CJK; quotation-mark conventions; dash policy |
| **Banned constructions** | sentence patterns the author refuses; filler phrases in this language |
| **Quota rules** | rhetorical structures allowed but rationed ("at most twice per piece"), with approved variants listed |
| **Terminology conventions** | first-occurrence original-language-in-parentheses rules; per-project settled translations live in the project's terminology table, the *convention* lives here |
| **Idiom policy** | when idioms/set phrases are allowed; default-conservative lists; density limits |
| **Voice samples** | short passages exemplifying the target register (grow them from the project's final-drafts collection) |

## Writing your own

Copy `example-module.md`, replace its rules with yours, keep the block structure (the Writer's checklist keys off the block names). Rules should be **checkable** where possible — "at most 2 per piece" beats "use sparingly". The author's own module (Traditional Chinese academic prose — full-width punctuation rules, a dash ban, a rationed contrast-structure quota, first-occurrence original-term conventions, a default-conservative idiom policy) stays private, but its shape is exactly the template here.

One module per project; switching projects may switch modules; the skeleton never hard-codes one.
