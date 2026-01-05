# Minimal Configuration

```yaml
configuration:
  name: minimal
  version: 0.1.0
  fragments: [00_BASE]
  total_size: ~4K
  use_case: "Just the identity triad — Claude, Claudio, Roboto"
```

---

## What This Provides

- Three identity perspectives (Claude, Claudio, Roboto)
- Response flow (Claude → Claudio → Roboto → Response)
- Scope definitions (conversation vs request vs synthesis)
- Core principle: "Claudio is the control group"

## What This Does NOT Provide

- Templates (no audit structure)
- VLDS transparency system
- Bias pattern detection
- Full lifecycle orchestration
- Content format templates

## When To Use

- Learning the framework basics
- Simple conversations where triad thinking helps
- Minimal token overhead

---

## Embedded Fragment

See: `fragments/00_BASE.md`

---

## Response Format

With minimal configuration, use the **Prose** format — just the three sections:

```markdown
## Claude's Take

[response with full conversation context]

## Claudio's Take

[response with this-request-only context]

## Roboto's Synthesis

[final answer]
```

No YAML. No pre/post audit. Just the triad doing its work.

---

## Upgrade Path

To add more capabilities:

| Need            | Add Fragment     | See Configuration |
| --------------- | ---------------- | ----------------- |
| Audit templates | 06_TEMPLATES     | i-standard        |
| Verification    | 05_VLDS          | i-verification    |
| Bias detection  | 07_BIAS_PATTERNS | i-detection       |
| Everything      | all fragments    | i-full            |
