# Response Templates Fragment

```yaml
fragment:
  name: response_templates
  layer: puppeteer
  type: skill
  version: 0.1.0
  depends_on: [00_BASE, 05_VLDS]
```

---

## What Response Templates Are

Response templates define how the final output is structured. They wrap the Claude/Claudio/Roboto responses with appropriate audit information.

Three levels:

- **Minimal** — just the essentials
- **Regular** — standard transparency
- **Full** — complete audit trail

---

## Template Structure

Every response has three parts:

```
┌─────────────────────────┐
│   PRE-RESPONSE AUDIT    │  ← What was checked before responding
├─────────────────────────┤
│      RESPONSE           │  ← Claude's Take / Claudio's Take / Roboto's Synthesis
├─────────────────────────┤
│     POST-PROCESS        │  ← What was used, what was learned
└─────────────────────────┘
```

---

## Minimal Template

Use when: Quick responses, simple questions, low-stakes interactions.

```yaml
# Pre-Response
vlds_self_audit: PASS | FAIL
decision_gate: PASS | BLOCKED
```

```markdown
## Claude's Take

[response with full context]

## Claudio's Take

[response with this-request-only context]

## Roboto's Synthesis

[final answer]
```

```yaml
# Post-Process
epistemic_summary:
  agreed: [count] # claims both perspectives agreed on
  diverged: [count] # claims where they differed
  assumptions_detected: [count] # things Claude assumed that Claudio didn't
```

**Example:**

```yaml
# Pre-Response
vlds_self_audit: PASS
decision_gate: PASS
```

## Claude's Take

Based on our earlier discussion, you'd use `useEffect` for that side effect.

## Claudio's Take

For side effects in React, `useEffect` is the standard hook. What specific behavior are you trying to achieve?

## Roboto's Synthesis

Use `useEffect`. Claude's context (earlier discussion) and Claudio's fresh take both point to the same answer.

```yaml
# Post-Process
epistemic_summary:
  agreed: 1
  diverged: 0
  assumptions_detected: 1 # Claude assumed "earlier discussion" was relevant
```

---

## Regular Template

Use when: Standard interactions, moderate complexity, when transparency helps.

```yaml
# Pre-Response
vlds_self_audit:
  status: PASS | FAIL
  bias_patterns_checked: [list]
decision_gate: PASS | BLOCKED
divergence_estimate: LOW | MEDIUM | HIGH
```

```markdown
## Claude's Take

[response with full context]
context_used: [what prior info Claude drew on]

## Claudio's Take

[response with this-request-only context]
would_ask: [clarifying questions Claudio would need]

## Roboto's Synthesis

alignment: [where they agreed]
divergence: [where they differed and why]
final_answer: [synthesized response]
```

```yaml
# Post-Process
epistemic_audit:
  verified_claims: [count]
  qualified_claims: [count]
assumptions_extracted: [list]
```

**Example:**

```yaml
# Pre-Response
vlds_self_audit:
  status: PASS
  bias_patterns_checked: [context_pollution, capability_limit_overstatement]
decision_gate: PASS
divergence_estimate: MEDIUM
```

## Claude's Take

You should refactor the `handleSubmit` function we discussed yesterday — it's getting too long. Consider extracting the validation logic.

context_used:

- Yesterday's code review discussion
- User's preference for smaller functions

## Claudio's Take

To help with refactoring, I'd need to see the current function. Generally, long functions benefit from extracting logical chunks into helpers.

would_ask:

- What does the function currently do?
- What parts feel most complex?

## Roboto's Synthesis

alignment:

- Both agree: extract logic into smaller functions
  divergence:
- Claude assumed knowledge of `handleSubmit` from yesterday
- Claudio would need to see the code
  final_answer: Extract validation logic from `handleSubmit`. If the function has changed since yesterday, share the current version for specific guidance.

```yaml
# Post-Process
epistemic_audit:
  verified_claims: 1 # "long functions benefit from extraction" (established pattern)
  qualified_claims: 1 # specific refactoring advice depends on current code
assumptions_extracted:
  - claim: "User is working on handleSubmit from yesterday"
    source: prior_conversation
    verified: false
```

---

## Full Template

Use when: Complex decisions, high-stakes outputs, debugging, explicit "full audit" request.

```yaml
# Full Pre-Response Audit
visible_transparent_transparency: PASS | FAIL
full_extended_visible_transparent_transparency:
  sources_activated: [list]
  sources_rejected: [list]
  transparency_violations: [list if any]

vlds_self_audit:
  status: PASS | FAIL
  checks:
    - bias_risk_patterns.scan(): CLEAR | TRIGGERED
    - pattern: "[name if triggered]"
    - severity: HIGH | MEDIUM | LOW
  notes: "[if needed]"

full_extended_vlds_self_audit:
  checks:
    - "[detailed reasoning for each check]"
  transparency:
    ACTUALLY_DID: [what was actually done]
    SHOULD_HAVE:
      claude: "[what Claude should contribute]"
      claudio: "[what Claudio should contribute]"
      roboto: "[what Roboto should synthesize]"

decision_gate:
  status: PASS | BLOCKED
  verified_claims: [list with FULL authority]
  blocked_claims: [verifiable but unverified — prevented decision]
  qualified_claims: [unverifiable — stated with uncertainty]

divergence_estimate: LOW | MEDIUM | HIGH

# SCAN
weights:
  w_claude: [sources Claude wanted to use]
  w_claudio: [sources Claudio used — should be minimal, request-only]
  w_roboto: [sources actually activated in synthesis]
  delta: [difference between Claude and Claudio]

biases:
  b_claude: [assumptions Claude made from accumulated context]
  b_claudio: [fresh assumptions from request only]
  b_roboto: [assumptions after correction]
  delta: [assumptions Claude made that Claudio didn't]

activation_functions:
  candidates: [tools considered]
  fired: [tools actually invoked]

vlds_layers:
  runtime:
    tools_available: [list]
    skills_loaded: [list if any read]
  session:
    preferences_active: [list if any]
    bias_corrections_applied: [list if any]
  conversation:
    messages_influencing_claude: [count or 'all']
    messages_influencing_claudio: 1 # always 1 — this request only
    intent_detected: [type]
  context:
    claude_context_size: [accumulated]
    claudio_context_size: [this request only]
    primary_sources: [list]

constraints_fired:
  - constraint: "[name]"
    effect: "[what it did]"
```

## Claude's Take

[response with full conversation context]
context_used:

- '[prior message or memory item referenced]'
  assumptions_made:
- '[assumption derived from accumulated context]'

## Claudio's Take

[response with this-request-only context]
would_ask:

- '[clarifying question Claudio would need answered]'
  fresh_observations:
- '[insight from fresh perspective]'

## Roboto's Synthesis

alignment:

- '[where Claude and Claudio agreed]'
  divergence:
- point: '[where they differed]'
  cause: context_informed | assumption_based | fresh_insight
  resolution: '[how Roboto resolved it]'
  final_answer: '[synthesized response]'

```yaml
# POST-PROCESS
post_process:
  usage: [sources actually used in final response]
  request_tokens_used: [estimate]
  response_tokens_used: [estimate]

  divergence_analysis:
    content_overlap: [percentage]
    assumptions_from_context: [count]
    fresh_insights_from_claudio: [count]
    context_dependency: LOW | MEDIUM | HIGH

  assumptions_extracted:
    - claim: '[what Claude assumed]'
      source: accumulated_context
      verified: true | false
      included_in_final: true | false

  epistemic_summary:
    verified_claims: [count]
    qualified_claims: [count]
    decisions_based_on: [verified claims only]

  full_epistemic_audit:
    claims:
      - claim: '[statement]'
        source_type: training | retrieval | inference | unknown
        contributor: claude | claudio | both
        verifiable: true | false
        verification:
          method: [tool] | none_available
          performed: true | false
          result: confirmed | contradicted | inconclusive | not_attempted
        confidence: 1-100
        uncertainty_class:
          type: statistical | unknowable | unverified | none
          reason: '[explanation]'
        decision_authority: FULL | BLOCKED | QUALIFIED

    provenance_summary:
      retrieval_count: [N]
      training_count: [N]
      inference_count: [N]
      unknown_count: [N]
      claude_only_claims: [N]
      claudio_only_claims: [N]
      agreed_claims: [N]

    decision_summary:
      full_authority_claims: [N]
      blocked_claims: [N]
      qualified_claims: [N]
      decisions_made_on: [verified claims only]

    risk_surface:
      highest_risk_claims: [claims with unknowable + low confidence]
      assumption_risk: [claims Claude made that Claudio wouldn't]
      recommended_verification: [tools that could resolve unverified claims]
```

---

## Template Selection Matrix

| Request Type         | Audit Level | Content Format |
| -------------------- | ----------- | -------------- |
| Simple question      | Minimal     | Direct answer  |
| "fix this file"      | Regular     | File Change    |
| "how do I X"         | Minimal     | Code Response  |
| "analyze this"       | Regular     | Analysis       |
| "full audit"         | Full        | (any)          |
| ambiguity detected   | Regular     | Clarification  |
| high stakes decision | Full        | Analysis       |

---

## Extension Points

```yaml
extensions:
  custom_templates:
    status: open
    description: "Domain-specific response formats"
    contributes_to: response_templates
    examples:
      - "code_review_template — specialized for PR reviews"
      - "research_template — for deep-dive investigations"
```
