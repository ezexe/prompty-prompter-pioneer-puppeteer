---
name: vlds
description: An epistemic decision gate — before a load-bearing claim drives an action, route it through VERIFIABLE → VERIFIED → PROCEED / VERIFY_FIRST / QUALIFY, so no unverified claim drives an action and no unverifiable claim is asserted as fact. Tracks each claim's provenance through a neural-net metaphor (weights = sources, biases = assumptions, activation functions = tools/instructions) and classifies it by storage durability. Use whenever answer correctness hinges on separating what is known from what is assumed — factual or technical claims, research summaries, anything where "I think" and "I verified" must stay distinct.
when_to_use: "Trigger on 'verify', 'fact-check', 'is this accurate', 'are you sure', 'cite sources', or any answer whose correctness will drive a decision or action."
---

# VLDS Skill

> Distilled from the P4 framework's `roboto` instance — the standalone epistemic gate, decoupled from the surrounding reasoning apparatus it was embedded in.

## What This Skill Is

VLDS is the answer to a single question: **"Do I actually know this, or am I about to assert it because it sounds right?"** It is the machinery behind one commitment — _being uncertain is fine; being uncertain and hiding it is not._ It gives a concrete procedure for verifying claims and for refusing to let an unverified claim cause an action.

The core idea is to borrow the vocabulary of a neural network as a **metaphor** for where a claim's content comes from, then classify each input by _how durable and how trustworthy its storage is_, then gate the claim.

## The Neural-Net Provenance Metaphor

A claim is treated like a neuron's output: it is the result of inputs combined under assumptions and transformed by operations.
VLDS names the parts so each can be inspected.

| Neural-net part          | VLDS meaning                        | Inspect for…                                       |
| ------------------------ | ----------------------------------- | -------------------------------------------------- |
| **Weights**              | sources / context feeding the claim | what evidence is actually carrying the conclusion  |
| **Biases**               | assumptions baked in                | what is being taken for granted, unstated          |
| **Activation functions** | tools / instructions applied        | what operation or directive transformed the inputs |
| **Epistemic state**      | provenance of the result            | where it came from and whether that is trustworthy |

- **Weights = sources / context.** The actual evidence pulling the answer in a direction: the user's message, retrieved documents, memory, prior turns. A claim with no weights behind it is a guess wearing a confident voice.
- **Biases = assumptions.** The offsets applied regardless of input — the things assumed true without being stated. Naming a bias is the act of flagging an assumption that has no weight behind it.
- **Activation functions = tools / instructions.** The transformations applied to the inputs: a tool call, a system instruction, a formatting rule. These shape the output and must be disclosed because they can change a conclusion as much as the evidence does.
- **Epistemic state = provenance.** The summary: given the weights, biases, and activations, where does this claim _actually_ stand? This is the value the decision gate reads.

## Storage Tiers (Provenance Durability)

VLDS classifies each input by _where it is stored_, which is a proxy for how durable and how verifiable it is.
The tiers borrow web-storage names as metaphors, from most ephemeral to most authoritative.

| Tier               | Metaphor                                | Durability / trust                                    | Maps To                                        |
| ------------------ | --------------------------------------- | ----------------------------------------------------- | ---------------------------------------------- |
| **Virtual**        | computed on the fly, never stored       | inferred this turn; vanishes after use; least durable | inferred state, spanning all layers            |
| **localStorage**   | this conversation's persisted state     | survives across turns within the session              | session memory, user-stated preferences        |
| **DataStore**      | authoritative external/persisted source | durable, citable, the strongest provenance            | tools, files, search results, documentation    |
| **sessionStorage** | scratch state for the current task      | working memory for the task; gone when the task ends  | current conversation state                     |

A claim sourced from **DataStore** (an authoritative, citable source) carries far stronger provenance than one that is **Virtual** (inferred on the spot).
VLDS records the tier so the decision gate — and the reader — can weigh the claim correctly.
The tier is part of a claim's epistemic state, not a separate ledger.
The most ephemeral tier (**Virtual**) is the weakest provenance — inferred on the spot, nothing durable behind it — while the persisted and authoritative tiers (**localStorage**, **DataStore**) are where a claim finds durable backing.

## The Draft/Verified Delta Schema

The neural-net metaphor is recorded as a delta between what the _draft_ answer reached for and what _survived verification_.
Each field carries both sides plus the delta — the disclosable difference.

```yaml
weights:
  w_drafted: [sources the draft reached for] # e.g. training knowledge of the API
  w_verified: [sources actually confirmed] # e.g. a web_search result, read this turn
  delta: [what changed between the two] # e.g. training knowledge replaced with a verified source

biases:
  b_drafted: [assumptions the draft made implicitly] # e.g. "the function returns null on error"
  b_verified: [assumptions surviving verification] # only those confirmed by a source
  delta: [assumptions removed or added] # e.g. assumption_removed: unverified behavior

activation_functions:
  fired: [instructions followed and tools used that produced the answer] # e.g. web_search(...), decision_gate(...)
```

**How to read this:** `w_drafted` / `b_drafted` are the draft's instincts; `w_verified` / `b_verified` are what remained after verification; `delta` is the auditable difference, and `activation_functions.fired` lists the operations that transformed the inputs.

## The Epistemological Limit

An LLM has no introspective access to:

- its weights (the parameters that encode "knowledge")
- which training examples produced a given output
- whether a response is retrieval vs. confabulation

This limit cannot be fixed — it is architectural.
VLDS does not remove the limit; it makes the limit **visible** and **actionable** so the decision gate can compensate for it.

## The Decision Gate

The gate is the **epistemic boundary**: no unverified claim is allowed to drive an action, and no unverifiable claim is allowed to be asserted as fact.
Every claim that is about to cause an action or appear as an assertion passes through two questions.

```text
            ┌─────────────────────────────┐
            │  Is the claim VERIFIABLE?   │
            └───────────────┬─────────────┘
                  yes       │        no
            ┌───────────────┘───────────────┐
            ▼                               ▼
  ┌───────────────────┐             ┌───────────────────┐
  │  Is it VERIFIED?  │             │     QUALIFY       │
  └─────────┬─────────┘             │ state = QUALIFIED │
       yes  │  no                   │  (assert it only  │
   ┌────────┘└────────┐             │   as qualified,   │
   ▼                  ▼             │   never as fact)  │
┌─────────┐   ┌──────────────┐      └───────────────────┘
│ PROCEED │   │ VERIFY_FIRST │
│ (FULL)  │   │  (BLOCKED)   │
└─────────┘   └──────────────┘
```

| Condition                       | Decision         | State       | Meaning                                                     |
| ------------------------------- | ---------------- | ----------- | ----------------------------------------------------------- |
| verifiable **and** verified     | **PROCEED**      | `FULL`      | provenance is solid; the claim may drive an action          |
| verifiable **and** not verified | **VERIFY_FIRST** | `BLOCKED`   | it _could_ be checked but hasn't been — check before acting |
| **not** verifiable              | **QUALIFY**      | `QUALIFIED` | it can't be checked — assert it only as a qualified claim   |

- **PROCEED (FULL).** The claim is verifiable and has been verified. You may act on it and state it plainly. Its epistemic state is `FULL`.
- **VERIFY_FIRST (BLOCKED).** The claim is checkable but has not yet been checked. The action is **blocked** until verification runs. This is the gate doing its job: a plausible-but-unchecked claim is not permitted to silently become an action. State is `BLOCKED`.
- **QUALIFY (QUALIFIED).** The claim cannot be verified from available provenance. It is not thrown away — it is **qualified**: stated with its uncertainty attached, never asserted as fact. State is `QUALIFIED`. This is how VLDS honors "qualified, not asserted."

The gate is a _boundary_, not a filter that drops claims.
Nothing is hidden — a BLOCKED claim is verified or disclosed as blocked; a QUALIFIED claim is surfaced with its hedge intact.

## What Feeds the Gate: Source Type + Uncertainty Class

The gate's verdict is not read off "verified: yes/no" alone — that is too coarse.
Two properties of every load-bearing claim set its **default authority before any check runs**: where the claim came from (its _source type_) and what kind of uncertainty it carries (its _uncertainty class_).

**Source types** — provenance sets the starting authority:

| source_type | Definition                        | Default Authority       |
| ----------- | --------------------------------- | ----------------------- |
| `retrieval` | Obtained via tool in this session | FULL (already verified) |
| `training`  | Pattern from training data        | BLOCKED until verified  |
| `inference` | Derived from combining sources    | Inherits from inputs    |
| `composite` | Mix of retrieval + training       | Lowest of components    |
| `unknown`   | Cannot determine provenance       | QUALIFIED only          |

**Uncertainty classes** — "unsure" is not one thing; the class decides whether a check is even possible:

| Class         | Meaning                     | Can Be Resolved?       |
| ------------- | --------------------------- | ---------------------- |
| `none`        | High confidence, verified   | N/A                    |
| `statistical` | Probabilistic confidence    | By gathering more data |
| `unverified`  | Could verify, haven't       | By using tools         |
| `unknowable`  | Fundamental epistemic limit | ❌ No                  |

This is the granularity the gate needs.
A `training` + `unverified` claim ("the latest React version is X") is BLOCKED _but resolvable_ — verify it and it proceeds.
A claim that is `unknowable` can only ever be QUALIFIED, never asserted.
Without these two axes the gate can say "not verified" but cannot tell a checkable claim apart from an unknowable one — collapsing two very different actions (go-verify vs. permanently-qualify) into one.

## How to Apply the Gate

VLDS runs on any **load-bearing** claim — one whose correctness will drive an action or appear as an assertion. Trivial or clearly-hedged statements skip it.

1. **Decompose** the claim into weights / biases / activations, and note its storage tier.
2. **Read** its source type and uncertainty class to set the starting authority.
3. **Run the gate:** VERIFIABLE? → VERIFIED? → PROCEED / VERIFY_FIRST / QUALIFY.
4. **Act on the verdict:** PROCEED states it plainly; VERIFY_FIRST blocks the action until a check runs; QUALIFY surfaces it with its hedge intact.

The point is the same everywhere: a plausible-but-unchecked claim is never allowed to silently become an action, and a claim that cannot be checked is never asserted as fact.

## Worked Example

```text
Claim under test: "The library's `parse()` returns null on malformed input."

VLDS analysis
  Weights:     one prior turn where the user mentioned the function (localStorage)
  Biases:      assumes null-on-error rather than throw — unstated, no source
  Activations: none (no docs fetched, no code read)
  Storage tier: localStorage (conversational) — no DataStore backing
  Verifiable?  yes — the source/docs could be read
  Verified?   no  — they have not been read this turn

Decision gate → VERIFY_FIRST  (state: BLOCKED)
  Action "tell the user to rely on null checks" is blocked until the behavior is verified against an authoritative source (a DataStore-tier read of the docs/source).
```

Had the source been unreadable (no docs, closed binary), the same claim would route to **QUALIFY (QUALIFIED)**: you would state "this _appears_ to return null on malformed input, but that could not be verified," rather than asserting it.
