# VLDS — Reference

The conceptual model behind the gate defined in [SKILL.md](SKILL.md). Load this when you need to _decompose_ a claim into its provenance parts, weigh its storage tier, or record the draft→verified delta. The gate in `SKILL.md` is self-sufficient for routing a claim; this file explains the vocabulary it uses.

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
