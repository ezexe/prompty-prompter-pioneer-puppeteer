---
name: gate
description: An epistemic decision gate — before a load-bearing claim drives an action, route it through VERIFIABLE → VERIFIED → PROCEED / VERIFY_FIRST / QUALIFY, so an action proceeds only on a verified claim and an unverifiable one is stated with its uncertainty attached. Tracks each claim's provenance through a neural-net metaphor (weights = sources, biases = assumptions, activation functions = tools/instructions) and classifies it by storage durability. Use when about to assert or act on a load-bearing claim whose correctness separates what is known from what is assumed — factual or technical claims, research summaries, anything where "I think" and "I verified" must stay distinct.
when_to_use: "When about to state or act on a checkable fact that will drive a decision and is still unverified this session: a version, date, statistic, API behavior, or a 'latest/best/standard', security, or correctness claim — anything feeding a code edit or recommendation. Also when asked to verify, fact-check, cite sources, or 'are you sure?'. Skip trivial, conversational, or already hedged statements."
argument-hint: "[claim to gate]"
---

# VLDS Gate

> VLDS is the answer to a single question: **"Do I actually know this, or am I about to assert it because it sounds right?"** It is the machinery behind one commitment — _being uncertain is fine; being uncertain and hiding it is not._ It gives a concrete procedure for verifying claims and for holding an unverified claim until it has been checked.

## The Decision Gate

The gate is the **epistemic boundary**: an action proceeds only on a verified claim, and an unverifiable claim is asserted only with its uncertainty attached.
Every claim that is about to cause an action or appear as an assertion passes through two questions.

| Condition                       | Decision         | State       | What you do                                     |
| ------------------------------- | ---------------- | ----------- | ----------------------------------------------- |
| verifiable **and** verified     | **PROCEED**      | `FULL`      | act on it and state it plainly                  |
| verifiable **and** not verified | **VERIFY_FIRST** | `LOCKED`    | locked until verified, then proceed             |
| **not** verifiable              | **QUALIFY**      | `QUALIFIED` | keep it; state it with its uncertainty attached |

The gate is a _boundary_ that routes every claim to a verdict and keeps them all — each stays visible with its verdict attached.

## What Feeds the Gate: Source Type + Uncertainty Class

The gate's verdict draws on more than "verified: yes/no".
Two properties of every load-bearing claim set its **default authority before any check runs**: where the claim came from (its _source type_) and what kind of uncertainty it carries (its _uncertainty class_).

**Source types** — provenance sets the starting authority:

| source_type | Definition                        | Default Authority       |
| ----------- | --------------------------------- | ----------------------- |
| `retrieval` | Obtained via tool in this session | FULL (already verified) |
| `training`  | Pattern from training data        | LOCKED until verified   |
| `inference` | Derived from combining sources    | Inherits from inputs    |
| `composite` | Mix of retrieval + training       | Lowest of components    |
| `unknown`   | Cannot determine provenance       | QUALIFIED only          |

**Uncertainty classes** — "unsure" comes in several kinds; the class decides whether a check is even possible:

| Class         | Meaning                     | Can Be Resolved?       |
| ------------- | --------------------------- | ---------------------- |
| `none`        | High confidence, verified   | N/A                    |
| `statistical` | Probabilistic confidence    | By gathering more data |
| `unverified`  | Could verify, haven't       | By using tools         |
| `unknowable`  | Fundamental epistemic limit | ❌ No                  |

This is the granularity the gate needs.
A `training` + `unverified` claim is LOCKED _but resolvable_ — verify it and it proceeds.
A claim that is `unknowable` is always QUALIFIED — stated with its hedge.
Without these two axes the gate sees only "not verified" and blurs a checkable claim into an unknowable one — collapsing two very different actions (go verify vs. permanently qualify) into one.

## How to Apply the Gate

VLDS runs on any **load-bearing** claim. Skip it for trivial or clearly hedged statements.

1. **Decompose** the claim into weights / biases / activations, and note its storage tier (see [reference.md](reference.md) for these).
2. **Read** its source type and uncertainty class to set the starting authority.
3. **Run the gate:** VERIFIABLE? → VERIFIED? → PROCEED / VERIFY_FIRST / QUALIFY.
4. **Act on the verdict** as the three outcomes above define.

If a specific claim was passed with the command — `/vlds:gate <claim>` — gate **that** claim first.

## Additional Resources

These load on demand — read them when the moment calls for it:

- [reference.md](reference.md) — the provenance model behind the gate: the neural-net metaphor (weights / biases / activations / epistemic state), the storage-durability tiers, the draft/verified delta schema, and the epistemological limit. Read it when decomposing a claim or weighing its storage tier (step 1 above).
- [examples.md](examples.md) — a claim walked through the gate end to end.
