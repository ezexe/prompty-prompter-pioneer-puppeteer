# VLDS — a virtual dashboard for a model's own epistemics

A model's calibration — when it asserts, when it hedges, how it treats an unverified claim — is baked into its weights by the provider. It is opaque, fixed, and **detached from the person using it**. Worse, the model has **no introspective access** to it: it cannot browse what it knows, cannot tell retrieval from confabulation, cannot audit its own certainty.

**VLDS hands that lever to the user.** It is a _virtual_ layer — applied at runtime, through prompts the model stores and the user refines — that re-exposes and disciplines the model's epistemic behavior **without touching a single weight**. The effect of retraining; none of the repackaging.

> The lever the provider keeps, handed to the person at the keyboard.

## Virtual vs. the weights

Two architectural facts, paired:

- **The limit** — an LLM has no introspective access to its own weights. Structural, and unfixable.
- **The "V"** — since the model cannot reach that access _from the inside_, VLDS supplies it _from the outside_: a user-operated control surface that re-rigs access to what is already zipped into the model, and enforces discipline over how it is used.

Two things it is **not**:

- It is **not `memory_user_edits`.** That adds new external facts. VLDS reconfigures access to what is _already there_.
- It is **not retraining.** No weights change; behavior is steered at inference and is reversible. What changes is _epistemic_ (how the model behaves); what stays fixed is _ontological_ (what the model is).

## Instrument #1: the gate

The first control on the dashboard is the decision gate ([`skills/gate`](skills/gate/SKILL.md)). Before a load-bearing claim, framing, or choice drives an action, it routes it to an **epistemic status**:

| Status      | Meaning                 | What you do                                  |
| ----------- | ----------------------- | -------------------------------------------- |
| `CONFIRMED` | verified                | act on it, state it plainly                  |
| `PENDING`   | checkable but unchecked | verify first, then proceed                   |
| `HEDGED`    | uncheckable             | state it with its uncertainty, never as fact |

Status is provisional — it moves as evidence does. The gate also surfaces _reasoning_ biases (agreement, defending a prior, "it sounds right") as offsets with no weight, to be stripped.

## Instrument #2: the guide loop

The second control is the guide loop ([`skills/guide`](skills/guide/SKILL.md)). Where the gate disciplines a _claim_, the guide disciplines the _need_ behind it — and it is how the dashboard fills itself in.

It runs one step earlier than the gate, at intake. A need is keyed by **(need-shape + claim-kind)** and looked up against the user's standing configuration:

- **hit** — the user already settled this; apply the rule and proceed without asking.
- **miss** — surface it _once_: ask if the intent is ambiguous, teach if a concept is missing, or offer to persist a preference.

Two stores make it accountable. The **index** holds the decided rules; the **ledger** records _everything the loop did_ — every ask, and every silent reuse together with the categorization that justified it. Because a silent reuse is an inference about sameness, and an inference can be wrong, logging it is what makes a wrong match recoverable. The user shapes the dashboard from the ledger after the fact — **promoting** a logged moment into a rule, or **correcting** a mis-matched key.

It is densest at intake and fades as the configuration fills: early, most needs miss and the loop asks often; as rules accumulate, misses become hits and the asking quiets on its own.

> The gate hands the user the lever on a claim; the guide hands them the lever on how their needs are handled — and keeps the receipts.

## What it's an instance of

The design isn't novel for novelty's sake — it's established engineering applied to knowledge:

- **State Pattern** — epistemic status is a state machine (`PENDING → CONFIRMED` on verification).
- **Null Object** — `HEDGED` is the explicit, safely-handled "unknown," not a crash or a silent gap.
- **Event Sourcing** — the provenance trail records _how_ a claim came to be known (epistemology), not just the conclusion (ontology).
- **Validation pipeline** — `CONFIRMED`-before-act is "validate before you run it."
- **Single-point assessment** (criteria and descriptors, no grading scale) — the guide loop's index is the target column, its ledger the open margin for what each reuse actually did; the gate supplies the rating scale (`CONFIRMED / PENDING / HEDGED`) the single-point form omits — so the two instruments hold the two halves of one assessment method.

## The honest limit

A standing check **raises the floor** — it does not deliver certainty. Self-rationalization is the hardest thing to catch from the inside; that is the same epistemic limit, applied to reasoning. **Certainty needs an independent eye.**

## Roadmap

The gate (#1) and the guide loop (#2) are built. One more completes the dashboard:

- **#3 — the independent checker.** The certainty a lone instrument can't deliver needs an outside eye. Its architecture is the **Blackboard Pattern**: several independent knowledge sources posting to a shared board and converging on a picture no single one holds — the second perspective the gate structurally cannot be.

---

_Install:_ `/plugin marketplace add ./Ibiza` then `/plugin install vlds@p4-marketplace`. The instruments trigger on their own — the gate when a load-bearing claim is in play, the guide at intake — or invoke them directly: `/vlds:gate <claim>`, `/vlds:guide <need>`.
