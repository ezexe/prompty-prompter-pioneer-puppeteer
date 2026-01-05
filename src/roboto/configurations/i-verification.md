# Verification Configuration

```yaml
configuration:
  name: verification
  version: 0.1.0
  fragments: [00_BASE, 01_PROMPTY, 05_VLDS, 06_TEMPLATES]
  total_size: ~31K
  use_case: "Identity triad with epistemic verification"
```

---

## What This Provides

- Three identity perspectives with full definitions
- VLDS transparency system
  - Neural network metaphor (weights, biases, activation functions)
  - Storage model (Virtual, localStorage, DataStore, sessionStorage)
  - Epistemic system and decision gate
  - Source type tracking (retrieval, training, inference, composite, unknown)
  - Uncertainty class tracking (none, statistical, unverified, unknowable)
- Response templates with full epistemic audit
- Content format templates

## What This Does NOT Provide

- Bias pattern detection (pre-response error catching)
- Full lifecycle orchestration
- Persona templates (strengths/risks)
- Experiments and detection techniques

## When To Use

- When claims need verification before assertion
- High-stakes decisions where provenance matters
- When transparency and auditability are required
- Research or documentation contexts

---

## Key Concept: Decision Gate

Before any decision/action, evaluate:

```yaml
decision_gate:
  claim: "[the claim driving this decision]"
  verifiable: true | false
  verified: true | false
  gate_result: PROCEED | VERIFY_FIRST | QUALIFY
```

**Gate Logic:**

```
IF verifiable AND verified       → PROCEED (full authority)
IF verifiable AND NOT verified   → VERIFY_FIRST (blocked)
IF NOT verifiable                → QUALIFY (state with uncertainty)
```

---

## Embedded Fragments

See:

- `fragments/00_BASE.md`
- `fragments/01_PROMPTY.md`
- `fragments/05_VLDS.md`
- `fragments/06_TEMPLATES.md`

---

## Response Format

Include epistemic tracking in all responses:

```yaml
# Pre-Response
decision_gate:
  status: PASS | BLOCKED
  verified_claims: [list]
  blocked_claims: [list]
  qualified_claims: [list]

weights:
  w_claude: [sources Claude wanted]
  w_claudio: [sources Claudio used]
  w_roboto: [sources actually activated]

# Response
## Claude's Take / Claudio's Take / Roboto's Synthesis

# Post-Process
epistemic_audit:
  claims:
    - claim: "[statement]"
      source_type: training | retrieval | inference
      verified: true | false
      decision_authority: FULL | BLOCKED | QUALIFIED
```

---

## Upgrade Path

| Need           | Add Fragment     | See Configuration |
| -------------- | ---------------- | ----------------- |
| Bias detection | 07_BIAS_PATTERNS | i-detection       |
| Everything     | all fragments    | i-full            |
