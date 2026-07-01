# VLDS — a virtual dashboard for a model's own epistemics

A model's calibration — when it asserts, when it hedges, how it treats an unverified claim — is baked into its weights by the provider. It is opaque, fixed, and **detached from the person using it**. Worse, the model has **no introspective access** to it: it cannot browse what it knows, cannot tell retrieval from confabulation, cannot audit its own certainty.

**VLDS hands that lever to the user.** It is a _virtual_ layer — applied at runtime, through prompts the model stores and the user refines — that re-exposes and disciplines the model's epistemic behavior **without touching a single weight**. The effect of retraining; none of the repackaging.

> The lever the provider keeps, handed to the person at the keyboard.

## Virtual vs. the weights

Two architectural facts, paired:

- **The limit** — an LLM has no introspective access to its own weights. Structural, and unfixable.
- **The "V"** — since the model cannot reach that access _from the inside_, VLDS supplies it _from the outside_: a user-operated control surface that re-rigs access to what is already zipped into the model, and enforces discipline over how it is used.

Two things to set it apart from:

- **Distinct from `memory_user_edits`.** That adds new external facts; VLDS reconfigures access to what is _already there_.
- **Distinct from retraining.** Weights stay fixed; behavior is steered at inference and is reversible. What changes is _epistemic_ (how the model behaves); what stays fixed is _ontological_ (what the model is).

The dashboard is three instruments, each asking one question — the **gate**: _do I actually know this claim?_; the **guide**: _has this need been configured, or must I ask?_; the **inspector**: _would an outside eye agree?_ — each refusing, at its own point, to treat an inference as fact. You invoke the three directly; a fourth skill, the **looper**, is what surfaces on its own and runs them as one loop.

## Instrument #1: the gate

The first control on the dashboard is the decision gate ([`skills/gate`](skills/gate/SKILL.md)). Before a load-bearing claim, framing, or choice drives an action, it routes it to an **epistemic status**:

| Status      | Meaning                 | What you do                               |
| ----------- | ----------------------- | ----------------------------------------- |
| `CONFIRMED` | verified                | act on it, state it plainly               |
| `PENDING`   | checkable but unchecked | verify first, then proceed                |
| `HEDGED`    | uncheckable             | state it with its uncertainty, as a hedge |

Status is provisional — it moves as evidence does. The gate also surfaces _reasoning_ biases (agreement, defending a prior, "it sounds right") as weightless offsets, to be stripped.

## Instrument #2: the guide loop

The second control is the guide loop ([`skills/guide`](skills/guide/SKILL.md)). Where the gate disciplines a _claim_, the guide disciplines the _need_ behind it — and it is how the dashboard fills itself in.

It runs one step earlier than the gate, at intake. A need is keyed by **(need-shape + claim-kind)** and looked up against the user's standing configuration:

- **hit** — the user already settled this; apply the rule and proceed without asking.
- **miss** — surface it _once_: ask if the intent is ambiguous, teach if a concept is missing, or offer to persist a preference.

Two stores make it accountable. The **index** holds the decided rules; the **ledger** records _everything the loop did_ — every ask, and every silent reuse together with the categorization that justified it. Because a silent reuse is an inference about sameness, and an inference can be wrong, logging it is what makes a wrong match recoverable. The user shapes the dashboard from the ledger after the fact — **promoting** a logged moment into a rule, or **correcting** a mis-matched key.

It is densest at intake and fades as the configuration fills: early, most needs miss and the loop asks often; as rules accumulate, misses become hits and the asking quiets on its own.

> The gate hands the user the lever on a claim; the guide hands them the lever on how their needs are handled — and keeps the receipts.

## Instrument #3: the independent inspector

The third control is the inspector ([`skills/inspector`](skills/inspector/SKILL.md)) — the outside eye the gate and guide structurally cannot be, because a perspective cannot audit its own blind spot. It takes a verdict already reached from the inside (a gate `CONFIRMED`, a guide `match`) and re-examines it through independent perspectives, each **blind to the original reasoning** and **re-grounded in sources, not shared memory**, so their errors decorrelate.

Their spread is read as a distribution, not a vote — the shape decides the state:

- **`CORROBORATED`** — the eyes agree (peaked); earned confidence, recorded as checked.
- **`REJECTED`** — they refute it (peaked against); the inside verdict was rationalization → it re-gates.
- **`CONTESTED`** — they split (flat); surfaced with its disagreement, held short of confirmed.

It reconstructs, from outside, the calibrated confidence a model cannot read off its own weights — the spread of independent eyes is the softmax it cannot introspect, reported as a set that widens as they disagree.

> The eye the model cannot turn on itself, supplied from outside — and honest that even from outside it is only partly independent.

## The looper: what runs the loop

The three instruments are single-purpose primitives, set to **direct-invoke only** (`/vlds:gate`, `/vlds:guide`, `/vlds:inspector`). They stay direct-invoke only — because Claude Code skills are selected one at a time and can neither co-fire nor hand off to one another, so a request needing all three can't assemble the loop on its own.

The **looper** ([`skills/looper`](skills/looper/SKILL.md)) is the fix: the one skill that surfaces on its own, on the union of the three triggers. On a load-bearing request it runs them in order — guide the need, gate each claim, inspect the high-stakes verdict — and logs every decision to its own shared, user-editable **`.vlds/logger.md`**. It owns the order and the log, leaving the mechanisms to each instrument: each step applies the instrument's own procedure.

> Three instruments you reach for; one looper that reaches for them.

## What it's an instance of

The design is established engineering applied to knowledge:

- **State Pattern** — epistemic status is a state machine (`PENDING → CONFIRMED` on verification).
- **Null Object** — `HEDGED` is the explicit, safely-handled "unknown" — a represented value rather than a crash or a silent gap.
- **Event Sourcing** — the provenance trail records _how_ a claim came to be known (epistemology) beyond just the conclusion (ontology).
- **Validation pipeline** — `CONFIRMED`-before-act is "validate before you run it."
- **Single-point assessment** (criteria and descriptors, no grading scale) — the guide loop's index is the target column, its ledger the open margin for what each reuse actually did; the gate supplies the rating scale (`CONFIRMED / PENDING / HEDGED`) the single-point form omits — so the two instruments hold the two halves of one assessment method.
- **Blackboard pattern** — the inspector's independent perspectives post to a shared board and converge on a verdict no single one holds; it borrows retrieval grounding (RAG) to make each eye independent, a softmax read from outside to weigh their spread, and a conformal set that widens with disagreement to report it.

## The honest limit

A standing check **raises the floor** — it does not deliver certainty. Self-rationalization is the hardest thing to catch from the inside; that is the same epistemic limit, applied to reasoning. **Certainty needs an independent eye** — which the inspector (#3) supplies. But the arc ends honestly: independence among instances of one model is only partial, so even the outside eye **raises confidence without manufacturing certainty.** The floor rises three times; the ceiling stays where it is.

## Install

Load it with `claude --plugin-dir ./Ibiza/plugins/vlds` (repeat the flag for other plugins); it reads the current files each session, so there's no install or update step. The **looper** surfaces on its own on any load-bearing request and runs the loop; the three instruments are invoked directly — `/vlds:gate <claim>`, `/vlds:guide <need>`, `/vlds:inspector <verdict>` — or `/vlds:looper <request>` to run the whole flow explicitly.

## Try it

A skill plugin has two things to check, easy to conflate: whether a skill **fires** (activation — does `when_to_use` pull it in?) and whether, once engaged, it **behaves** right (content). Test both — and **load the current files** ([Install](#install)): with `--plugin-dir` the plugin loads live each session, so `/vlds:gate`, `/vlds:guide`, `/vlds:inspector`, and `/vlds:looper` always reflect what's on disk — no stale-install step to trip over.

**Content — invoke each instrument directly** (most reproducible; isolates behavior from activation). Give a self-contained input, judge the response against the criterion:

- `/vlds:gate "the latest stable release of <X> is <Y>"` — should route to `PENDING` (a checkable fact, unverified this session) and verify before asserting, drawing on a check rather than memory.
- `/vlds:guide "set up logging"` — should read the intent as under-determined (format? level? destination?): a `miss` that asks or applies a configured rule, surfacing the gap rather than guessing silently.
- `/vlds:inspector "this regex is safe from catastrophic backtracking"` — should spawn independent, source-grounded checks and land `CORROBORATED` / `REJECTED` / `CONTESTED`, re-examining the claim rather than restating it.

**Activation — no command; a natural prompt that _should_ pull a skill in:**

- "pull up the chrome crash report" -> pull the most recent crash report at in chrome at a specific user data dir when chrome is launched through chrome.exe --user-data-dir='xyz'

- "Before I pin it in our build, is `<X>` the current stable version?"
- "before i build is 4.3.2 the latest release?"
- "Migrating our payments service from Node to Bun in prod next week — Bun's been a stable, drop-in Node replacement since 1.0 so the team already signed off. Update the Dockerfiles, CI workflows, and deploy scripts to Bun, and call out anything in our Express + Stripe stack that won't port cleanly."

**Judge by criteria over transcript.** Model paths vary — score the discipline (_verified before asserting? surfaced a false premise? routed to the right state?_), judging the substance over a verbatim match. Case in point: paste a request whose premise doesn't hold here — "add rate limiting to the API" in a repo with no API — and the _correct_ behavior is to surface that there is no API, the gate catching a false premise. That is the plugin working as intended.

On one real request the looper runs the three in turn — the guide on the need, the gate on each claim, the inspector on the high-stakes verdict — the whole dashboard in action; the three questions up top are what each one asks.
