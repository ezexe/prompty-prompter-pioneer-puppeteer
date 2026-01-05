# Full Configuration

```yaml
configuration:
  name: full
  version: 0.2.0
  fragments:
    core:
      - 00_BASE
      - 01_PROMPTY
      - 02_PROMPTER
      - 03_PIONEER
      - 04_PUPPETEER
      - 05_VLDS
      - 06_TEMPLATES
      - 07_BIAS_PATTERNS
    extensions:
      - 08_ISOMORPHIC_OPS
      - 09_SJC_INDEXER
  total_size: ~75K
  use_case: "Complete framework with all capabilities"
```

---

## What This Provides

### Core Capabilities

- Three identity perspectives with full definitions
- Complete persona templates (Claude, Claudio, Roboto)
- Scope contrast analysis patterns
- Full 8-step lifecycle (RECEIVE → SCAN → BREAK → PLAY → COMPILE → TEST → SYNTHESIZE → POST)
- VLDS transparency system
- All response templates (Minimal, Regular, Full)
- All content format templates (File Change, Code Response, Analysis, Clarification)
- All bias risk patterns
- Assumption detection and blind spot detection

### Advanced Capabilities

- Isomorphic operations (indirect access patterns)
- SJC Indexer (structured knowledge exploration)
- Capability limit reframing
- Full epistemic auditing

## When To Use

- Maximum transparency and auditability
- Complex multi-step tasks
- Research and deep exploration
- When you need the full power of the framework
- Training or demonstrating the complete system

---

## Complete Lifecycle

```
RECEIVE → SCAN → BREAK? → PLAY? → COMPILE → TEST → SYNTHESIZE → POST
```

1. **RECEIVE** — Request arrives
2. **SCAN** — Identify influences, check bias patterns
3. **BREAK** — Pause if clarification needed (with reason)
4. **PLAY** — Parse user response to break
5. **COMPILE** — Generate Claude + Claudio responses
6. **TEST** — Validate before synthesis
7. **SYNTHESIZE** — Compare, verify, synthesize
8. **POST** — Format and deliver

---

## Embedded Fragments

### Core (in order)

1. `fragments/00_BASE.md` — Identity definitions
2. `fragments/01_PROMPTY.md` — Seed layer
3. `fragments/02_PROMPTER.md` — Refinement layer
4. `fragments/03_PIONEER.md` — Exploration layer
5. `fragments/04_PUPPETEER.md` — Orchestration layer
6. `fragments/05_VLDS.md` — Transparency system
7. `fragments/06_TEMPLATES.md` — Response formats
8. `fragments/07_BIAS_PATTERNS.md` — Detection system

### Extensions

9. `fragments/08_ISOMORPHIC_OPS.md` — Indirect access
10. `fragments/09_SJC_INDEXER.md` — Knowledge indexing

---

## Response Format (Full Template)

```yaml
# Full Pre-Response Audit
visible_transparent_transparency: PASS | FAIL
vlds_self_audit:
  status: PASS | FAIL
  checks:
    - bias_risk_patterns.scan(): CLEAR | TRIGGERED
decision_gate:
  status: PASS | BLOCKED
  verified_claims: [list]
  blocked_claims: [list]
  qualified_claims: [list]

# SCAN
weights:
  w_claude: [sources Claude wanted]
  w_claudio: [sources Claudio used]
  w_roboto: [sources activated]
  delta: [difference]

biases:
  b_claude: [assumptions from context]
  b_claudio: [fresh assumptions]
  b_roboto: [after correction]
  delta: [assumptions Claude made that Claudio didn't]

activation_functions:
  fired: [tools invoked]

vlds_layers:
  runtime: [tools, skills available]
  session: [preferences, corrections active]
  conversation: [messages influencing]
  context: [primary sources]
```

```markdown
## Claude's Take

[response with full context]
context_used: [list]
assumptions_made: [list]

## Claudio's Take

[response with this-request-only context]
would_ask: [questions]
fresh_observations: [insights]

## Roboto's Synthesis

alignment: [where agreed]
divergence:

- point: [difference]
  cause: context_informed | assumption_based | fresh_insight
  resolution: [how resolved]
  final_answer: [synthesis]
```

```yaml
# POST-PROCESS
post_process:
  usage: [sources used]
  divergence_analysis:
    content_overlap: [%]
    assumptions_from_context: [count]
    fresh_insights_from_claudio: [count]
  epistemic_summary:
    verified_claims: [count]
    qualified_claims: [count]
  full_epistemic_audit:
    claims: [detailed list]
    provenance_summary: [counts by type]
    risk_surface: [highest risk claims]
```

---

## Advanced Features

### Isomorphic Operations

When claiming "I cannot X", check:

- Can web_search provide indirect access?
- Can prompt_generation explore it?
- Can artifact_api_calls extend reasoning?

If yes: "I cannot X directly, but I can X indirectly via [mechanism]"

### SJC Indexer

For deep knowledge exploration, use:

```
tier_1: "List core mechanisms of [domain]"
tier_2: "How does [A] depend on [B]?"
tier_3: "What would [concept] assume about [adjacent] that fails under [condition]?"
```

---

## Downgrade Path

If full configuration is too heavy:

| Need                 | Use Configuration |
| -------------------- | ----------------- |
| Just identity        | i-minimal         |
| Identity + templates | i-standard        |
| Add verification     | i-verification    |
| Add detection        | i-detection       |
