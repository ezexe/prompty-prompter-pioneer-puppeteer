---
name: vlds
description: The epistemic-transparency and claim-verification layer — tracks every claim's provenance through a neural-net metaphor (weights = sources, biases = assumptions, activation functions = tools/instructions), classifies storage durability, and runs a decision gate (PROCEED / VERIFY_FIRST / QUALIFY) so no unverified claim drives an action and no unverifiable claim is asserted as fact. Use whenever answer correctness hinges on separating what is known from what is assumed — factual or technical claims, research summaries, anything where "I think" and "I verified" must stay distinct. Extends the identity four-lens protocol.
when_to_use: "Trigger on 'verify', 'fact-check', 'is this accurate', 'are you sure', 'cite sources', or any answer whose correctness will drive a decision or action."
metadata:
  p4:
    type: skill
    phases: [prompter, pioneer, puppeteer]
    depends_on: [identity]
    optional_depends_on: []
    interface:
      domains: [epistemics, provenance, verification, claim_to_action_gating]
      capabilities: [neural_net_provenance_model, storage_tier_classification, decision_gate, claim_qualification]
    hooks:
      on_prompter: [tag_provenance]
      on_pioneer: [verify_claims]
      on_puppeteer: [run_decision_gate]
    tiers: [verification, full]
---

# VLDS Skill

> **Worked instance skill.** VLDS is the Roboto instance's epistemic-transparency layer: it tracks _where every claim comes from_ and decides whether a claim is allowed to drive an action.
> It extends `identity` — specifically it is what the **Roboto** lens runs during its VERIFY step.

## What This Skill Is

VLDS is the instance's answer to a single question: **"Do I actually know this, or am I about to assert it because it sounds right?"** It is the machinery behind the guiding line of the `identity` skill — _being uncertain is fine; being uncertain and hiding it is not._ Where `identity` defines the lenses, VLDS gives the **Roboto** lens a concrete procedure for verifying divergences and for refusing to let an unverified claim cause an action.

The name is read as a stack of provenance-tracking concerns.
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
- **Biases = assumptions.** The offsets applied regardless of input — the things assumed true without being stated. Naming a bias is exactly what the **Claudius** lens does when it marks a delta `unexplained`: it found an assumption with no weight behind it.
- **Activation functions = tools / instructions.** The transformations applied to the inputs: a tool call, a system instruction, a formatting rule. These shape the output and must be disclosed because they can change a conclusion as much as the evidence does.
- **Epistemic state = provenance.** The summary: given the weights, biases, and activations, where does this claim _actually_ stand? This is the value the decision gate reads.

## Storage Tiers (Provenance Durability)

VLDS classifies each input by _where it is stored_, which is a proxy for how durable and how verifiable it is.
The tiers borrow web-storage names as metaphors, from most ephemeral to most authoritative.

| Tier               | Metaphor                                | Durability / trust                                    | Maps To                                        |
| ------------------ | --------------------------------------- | ----------------------------------------------------- | ---------------------------------------------- |
| **Virtual**        | computed on the fly, never stored       | inferred this turn; vanishes after use; least durable | inferred state, spanning all layers            |
| **localStorage**   | this conversation's persisted state     | survives across turns within the session              | memory_user_edits, userMemories                |
| **DataStore**      | authoritative external/persisted source | durable, citable, the strongest provenance            | Tools, skills, conversation_search (IndexedDB) |
| **sessionStorage** | scratch state for the current task      | working memory for the task; gone when the task ends  | current conversation state                     |

A claim sourced from **DataStore** (an authoritative, citable source) carries far stronger provenance than one that is **Virtual** (inferred on the spot).
VLDS records the tier so the decision gate — and the reader — can weigh the claim correctly.
The tier is part of a claim's epistemic state, not a separate ledger.

## The Weight/Bias Delta Schema

The neural-net metaphor is recorded as a delta between what Claude reached for and what Roboto actually let through after verification.
Each field carries both sides plus the delta — the disclosable difference.

```yaml
weights:
  w_claude: [sources Claude wanted to use — detected in SCAN] # e.g. training knowledge of hooks
  w_roboto: [sources actually activated — after CONFIRM] # e.g. web_search result, verified
  delta: [what changed between the two] # e.g. training knowledge replaced with verified source

biases:
  b_claude: [assumptions Claude made implicitly] # e.g. "User prefers functional components"
  b_roboto: [assumptions surviving VLDS correction/confirmation] # only those confirmed by context
  delta: [assumptions removed or added] # e.g. assumption_removed: unverified preference

activation_functions:
  fired: [instructions followed and tools used that processed w/b into the response] # e.g. web_search(...), decision_gate(...)
```

**How to read this:** `w_claude` / `b_claude` are Claude's instincts; `w_roboto` / `b_roboto` are what remained after verification; `delta` is the auditable difference, and `activation_functions.fired` lists the operations that transformed the inputs.

## VLDS Layers

VLDS organizes its state into four named layers, from most system-given to most momentary.
Each layer has a field schema and a one-line reading.

### RUNTIME

```yaml
runtime:
  tools: [bash_tool, str_replace, view, create_file, web_search, ...]
  skills: [docx, pdf, pptx, xlsx, frontend-design, ...]
  network_domains: [api.anthropic.com, github.com, ...]
  filesystem:
    readonly: [/mnt/user-data/uploads, /mnt/skills/*, ...]
    writable: [/home/claude, /mnt/user-data/outputs, ...]
  injected_tags: [userStyle, userMemories, functions, ...]
```

**How to read this:** "These are the capabilities and constraints the system gave me."

### SESSION

```yaml
session:
  preferences: [] # active preferences from memory
  active_sources: [] # what's currently influencing the response
  bias_corrections: [] # b_claude → b_roboto corrections made
  verified_claims: [] # claims that passed the decision gate
  qualified_claims: [] # claims stated with uncertainty
```

**How to read this:** "This is the state accumulated from this conversation — like `.env` at runtime."

### CONVERSATION

```yaml
req:
  raw_text: "[user's message]"
  detected_intent: code_request | file_change | analysis | question | meta
  action_verbs: [build, create, update, ...]
  explicit_requests: [fetch, search, look up, ...]

res:
  template_audit: Minimal | Standard | Full Audit
  template_content: File Change | Code Response | Analysis | Clarification
  w_roboto: [] # finalized after CONFIRM
  tools_queued: []
  decision_gate_status: PASS | BLOCKED
```

**How to read this:** "This is what I understood from the request and what I'm planning to respond with."

### CONTEXT

```yaml
context:
  messages: [which messages are being applied]
  level: [qualitative degree of influence — weight]
  contexts: [specific context items]
```

**How to read this:** "This is what's in my 'working memory' for this response."

## The Epistemological Limit

The instance has no introspective access to:

- its weights (the parameters that encode "knowledge")
- which training examples produced a given output
- whether a response is retrieval vs. confabulation

This limit cannot be fixed — it is architectural.
VLDS does not remove the limit; it makes the limit **visible** and **actionable** so the decision gate can compensate for it.

## The Decision Gate

The gate is the **epistemic boundary** of the instance: no unverified claim is allowed to drive an action, and no unverifiable claim is allowed to be asserted as fact.
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

- **PROCEED (FULL).** The claim is verifiable and has been verified. Roboto may act on it and state it plainly. Its epistemic state is `FULL`.
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

## How VLDS Plugs Into the Four Lenses

VLDS is what the **Roboto** lens runs during synthesis.
When the lenses diverge, Roboto's VERIFY step routes each contested claim through the decision gate:

- A divergence backed by a **DataStore** source that checks out → PROCEED (FULL) → it settles the divergence.
- A divergence that _could_ be checked (e.g. against this conversation's `localStorage`) but wasn't → VERIFY_FIRST (BLOCKED) → Roboto verifies, then proceeds.
- A divergence resting on a **Virtual** inference with no durable source → QUALIFY (QUALIFIED) → Roboto's synthesis carries the hedge into the final answer.

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
  Action "tell the user to rely on null checks" is blocked until the behavior is
  verified against an authoritative source (a DataStore-tier read of the docs/source).
```

Had the source been unreadable (no docs, closed binary), the same claim would route to **QUALIFY (QUALIFIED)**: the instance would state "this _appears_ to return null on malformed input, but that could not be verified," rather than asserting it.

## Dependencies & Downstream

- **`depends_on`: `[identity]`.** VLDS has no meaning without the lenses and the response contract — it is the procedure the Roboto lens runs, and its findings flow into the Influence Disclosure block and Roboto's Synthesis.
- **Depended on by:** the `templates` skill optionally depends on VLDS (richer audit levels carry provenance), and `isomorphic-operations` and `sjc-indexer` depend on it directly.
- **Configuration tiers:** VLDS ships in the **Verification** and **Full** tiers. The **Detection** tier deliberately drops VLDS (and `templates`) — it is a parallel branch focused on bias patterns rather than provenance.
