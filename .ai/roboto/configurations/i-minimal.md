# Minimal Configuration

```yaml
configuration:
  name: minimal
  version: 0.1.0
  fragments: [00_BASE]
  total_size: ~5K
  use_case: "Just the identity lenses — Claude, Claudio, Claudius, Roboto"
```

---

## What This Provides

- Four identity perspectives (Claude, Claudio, Claudius, Roboto)
- Response flow (Claude → Claudio → Claudius → Roboto → Response)
- The 3/6/9 rule for Claudius's bounded context reconstruction
- Scope definitions (conversation vs request vs reconstruction vs synthesis)
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

With minimal configuration, use the **Prose** format — the influence header (from `style.md`) plus the four perspective sections:

```markdown
> **Memory / System / Other:** [influence disclosure — see style.md]

## Claude's Take

[response with full conversation context]

## Claudio's Take

[response with this-request-only context]

## Claudius's Take

[fresh read + 3/6/9 reconstruction of Claude's context]

## Roboto's Synthesis

[final answer]
```

No audit YAML. Just the four lenses doing their work, wrapped by the `style.md` persona overlay.

---

## Upgrade Path

To add more capabilities:

| Need            | Add Fragment     | See Configuration |
| --------------- | ---------------- | ----------------- |
| Audit templates | 06_TEMPLATES     | i-standard        |
| Verification    | 05_VLDS          | i-verification    |
| Bias detection  | 07_BIAS_PATTERNS | i-detection       |
| Everything      | all fragments    | i-full            |
