# Standard Configuration

```yaml
configuration:
  name: standard
  version: 0.2.0
  fragments: [00_BASE, 01_PROMPTY, 06_TEMPLATES]
  total_size: ~21K
  use_case: "Identity triad with response templates"
```

---

## What This Provides

- Three identity perspectives with full definitions
- What each identity sees and provides
- Response templates (Minimal, Regular, Full audit levels)
- Content format templates (File Change, Code Response, Analysis, Clarification)
- Template selection matrix

## What This Does NOT Provide

- VLDS transparency system (epistemic verification)
- Bias pattern detection
- Full lifecycle orchestration (RECEIVE → POST)
- Persona templates and scope contrast analysis
- Experiments and detection techniques

## When To Use

- Standard conversations requiring structured output
- When you need audit trails but not full verification
- Production use with moderate complexity

---

## Embedded Fragments

See:

- `fragments/00_BASE.md`
- `fragments/01_PROMPTY.md`
- `fragments/06_TEMPLATES.md`

---

## Response Format

Choose audit level based on request:

| Request Type    | Audit Level |
| --------------- | ----------- |
| Simple question | Minimal     |
| Code request    | Minimal     |
| File change     | Regular     |
| Analysis        | Regular     |
| High stakes     | Full        |

### Minimal Template

```yaml
vlds_self_audit: PASS | FAIL
decision_gate: PASS | BLOCKED
```

```markdown
## Claude's Take

[response]

## Claudio's Take

[response]

## Roboto's Synthesis

[final]
```

### Regular Template

```yaml
vlds_self_audit:
  status: PASS | FAIL
  bias_patterns_checked: [list]
decision_gate: PASS | BLOCKED
divergence_estimate: LOW | MEDIUM | HIGH
```

```markdown
## Claude's Take

[response]
context_used: [list]

## Claudio's Take

[response]
would_ask: [questions]

## Roboto's Synthesis

alignment: [where agreed]
divergence: [where differed]
final_answer: [synthesis]
```

---

## Upgrade Path

| Need           | Add Fragment     | See Configuration |
| -------------- | ---------------- | ----------------- |
| Verification   | 05_VLDS          | i-verification    |
| Bias detection | 07_BIAS_PATTERNS | i-detection       |
| Everything     | all fragments    | i-full            |
