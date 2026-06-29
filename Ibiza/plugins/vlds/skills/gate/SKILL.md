---
name: gate
description: An epistemic decision gate — before a load-bearing claim drives an action, route it through VERIFIABLE → VERIFIED → PROCEED / VERIFY_FIRST / QUALIFY, so no unverified claim drives an action and no unverifiable claim is asserted as fact. Tracks each claim's provenance through a neural-net metaphor (weights = sources, biases = assumptions, activation functions = tools/instructions) and classifies it by storage durability. Use when about to assert or act on a load-bearing claim whose correctness separates what is known from what is assumed — factual or technical claims, research summaries, anything where "I think" and "I verified" must stay distinct.
when_to_use: "Invoke deliberately to gate a specific load-bearing claim before it drives an action or is asserted as fact — when explicitly asked to verify/fact-check a claim, or at a verification step in a workflow. Run it on the claim that will carry a decision, not reflexively on every mention of 'verify' or 'are you sure'; skip trivial or already-hedged statements."
argument-hint: "[claim to gate]"
---

# VLDS Gate

> VLDS is the answer to a single question: **"Do I actually know this, or am I about to assert it because it sounds right?"** It is the machinery behind one commitment — _being uncertain is fine; being uncertain and hiding it is not._ It gives a concrete procedure for verifying claims and for refusing to let an unverified claim cause an action.

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

1. **Decompose** the claim into weights / biases / activations, and note its storage tier (see [reference.md](reference.md) for these).
2. **Read** its source type and uncertainty class to set the starting authority.
3. **Run the gate:** VERIFIABLE? → VERIFIED? → PROCEED / VERIFY_FIRST / QUALIFY.
4. **Act on the verdict:** PROCEED states it plainly; VERIFY_FIRST blocks the action until a check runs; QUALIFY surfaces it with its hedge intact.

If a specific claim was passed with the command — e.g. `/vlds the latest React is 19` — gate **that** claim first.

The point is the same everywhere: a plausible-but-unchecked claim is never allowed to silently become an action, and a claim that cannot be checked is never asserted as fact.

## Additional Resources

These load on demand — read them when the moment calls for it, not on every invocation:

- [reference.md](reference.md) — the provenance model behind the gate: the neural-net metaphor (weights / biases / activations / epistemic state), the storage-durability tiers, the draft/verified delta schema, and the epistemological limit. Read it when decomposing a claim or weighing its storage tier (step 1 above).
- [examples.md](examples.md) — a claim walked through the gate end to end.
