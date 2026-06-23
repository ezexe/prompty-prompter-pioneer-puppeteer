# Standard Configuration

```yaml
configuration:
  name: standard
  version: 0.1.0
  fragments: [00_BASE, 01_PROMPTY, 06_TEMPLATES]
  total_size: ~24K
  use_case: "Identity lenses with response templates"
```

---

## What This Provides

- Four identity perspectives with full definitions
- What each identity sees and provides (including Claudius's 3/6/9 reconstruction)
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

The `style.md` persona overlay (four-lens voice + Influence Disclosure + Deviation contract) wraps every response below. Choose audit level based on request:

| Request Type    | Audit Level |
| --------------- | ----------- |
| Simple question | Minimal     |
| Code request    | Minimal     |
| File change     | Regular     |
| Analysis        | Regular     |
| High stakes     | Full        |

The **Minimal** and **Regular** templates are written out below. The **Full** audit template is not duplicated here — it lives in the bundled `fragments/06_TEMPLATES.md` (see its "Full Template" section).

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

## Claudius's Take

[fresh read + 3/6/9 reconstruction]

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

## Claudius's Take

[fresh read + 3/6/9 reconstruction]
delta_cause: [which context explains the gap]

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
