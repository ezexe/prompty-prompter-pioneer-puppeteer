# VLDS — Worked Examples

Claims walked through the gate end to end. Load this for concrete traces of the procedure in [SKILL.md](SKILL.md); see [reference.md](reference.md) for the vocabulary used below (weights / biases / activations, storage tiers).

## Example: VERIFY_FIRST — a checkable claim that hasn't been checked

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

## Example: QUALIFY — a claim that cannot be checked

```text
Claim under test: "This architecture follows best practices."

VLDS analysis
  Weights:     patterns observed in the code this turn (Virtual — inferred)
  Biases:      assumes "good"/"best practice" is an objective property
  Activations: none — there is no objective standard to apply
  Storage tier: Virtual (inferred on the spot) — no durable backing
  Verifiable?  no — "best practice" is a subjective judgment, not a fact
  Uncertainty class: unknowable (no tool resolves it)

Decision gate → QUALIFY  (state: QUALIFIED)
  Stated with its uncertainty attached, never as fact:
  "Based on common patterns, this architecture appears to follow several
   widely-used conventions — though 'best practice' is a judgment call, not
   something I can verify."
```

A QUALIFIED claim is not thrown away — it is surfaced with the hedge intact. The mistake the gate prevents is laundering a subjective judgment into a flat assertion.

## Example: Mixed provenance — gate each claim independently

A real answer rarely rests on one claim. The gate runs **per claim**, so a single response can assert, hedge, and block at the same time. One answer recommending TypeScript:

```text
Claim 1: "TypeScript provides type safety."
  source_type: retrieval (read from the docs this turn) · verifiable + verified
  → PROCEED (FULL)        — assert it plainly

Claim 2: "TypeScript improves developer experience."
  source_type: inference · verifiable? no (subjective)
  → QUALIFY (QUALIFIED)   — state as opinion: "many developers find that…"

Claim 3: "TypeScript is the industry standard."
  source_type: training · verifiable but not verified this turn
  → VERIFY_FIRST (BLOCKED) — check adoption data before including it
```

The verdicts are per-claim, not per-answer — there is no fourth "partial" verdict. You assemble the response from the survivors: assert claim 1, hedge claim 2, and either verify or drop claim 3.
