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

## What it's an instance of

The design isn't novel for novelty's sake — it's established engineering applied to knowledge:

- **State Pattern** — epistemic status is a state machine (`PENDING → CONFIRMED` on verification).
- **Null Object** — `HEDGED` is the explicit, safely-handled "unknown," not a crash or a silent gap.
- **Event Sourcing** — the provenance trail records _how_ a claim came to be known (epistemology), not just the conclusion (ontology).
- **Validation pipeline** — `CONFIRMED`-before-act is "validate before you run it."

## The honest limit

A standing check **raises the floor** — it does not deliver certainty. Self-rationalization is the hardest thing to catch from the inside; that is the same epistemic limit, applied to reasoning. **Certainty needs an independent eye.**

## Roadmap

The gate is instrument #1. Two more complete the dashboard:

- **#2 — the guide loop.** Once a claim is _known_, a second question follows: does it serve the user's ask right now, or is it a moment to **teach** (onboard) or **configure** ("want me to remember/enforce this?"). Progressive, like first-run tooltips — heavy at first, fading as the user configures; and bidirectional — the model guides, the user configures. This is how a user is onboarded into operating the dashboard, and how it gets filled in: surface a candidate → user confirms → persisted prompt → refined behavior. ("What the user wants right now" is itself a claim — usually `PENDING`, so the honest move is to _ask_; the guide loop runs the gate on intent.)
- **#3 — the independent checker.** The certainty a lone instrument can't deliver needs an outside eye. Its architecture is the **Blackboard Pattern**: several independent knowledge sources posting to a shared board and converging on a picture no single one holds — the second perspective the gate structurally cannot be.

---

_Install:_ `/plugin marketplace add ./Ibiza` then `/plugin install vlds@p4-marketplace`. The gate triggers on its own when a load-bearing claim is in play, or invoke it directly with `/vlds:gate <claim>`.
