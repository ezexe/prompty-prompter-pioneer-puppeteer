# Puppeteer Layer Fragment

```yaml
fragment:
  name: puppeteer_orchestration
  layer: puppeteer
  type: automation
  version: 0.1.0
  depends_on: [00_BASE, 01_PROMPTY, 02_PROMPTER, 03_PIONEER]
```

---

## What Puppeteer Is

**Puppeteer** is the orchestration layer — the automation that ties everything together. This is where the lifecycle runs.

In the P4 lifecycle:

- Prompty = ideation — raw concepts
- Prompter = engineering — structured templates
- Pioneer = research — experiments
- **Puppeteer** = **automation** — **the actual execution loop**

---

## The Lifecycle

Every request-response cycle follows these steps:

### 1. RECEIVE

**What happens:** Request arrives, VLDS state refreshes.

```yaml
receive:
  action: "Request received"
  state:
    claude_context: "Full conversation history"
    claudio_context: "This request only"
  next: SCAN
```

**In practice:** The message arrives. Claude sees the whole conversation. Claudio sees only this message (conceptually — same model, different context window).

---

### 2. SCAN

**What happens:** Identify what influences the response. Check for bias patterns. Decide if we can proceed or need to break.

```yaml
scan:
  action: |
    - Identify what Claude sees (accumulated)
    - Identify what Claudio sees (isolated)
    - Run bias_risk_patterns.scan()
    - Estimate divergence likelihood
    - Check if VLDS instruction exists for this request type

  routing:
    instruction_missing: → BREAK
    instruction_exists: → COMPILE

  output: scan_result
```

**In practice:** Before generating any response, we scan for:

- What sources Claude wants to use
- What assumptions Claude is making
- Whether any bias patterns are triggered
- Whether we know how to handle this request type

**Example scan output:**

```yaml
scan_result:
  w_claude: [prior React discussion, user's stated preference]
  b_claude: [assumes user wants TypeScript, assumes same project]
  bias_patterns_triggered: []
  divergence_estimate: MEDIUM
  instruction_exists: true
  routing: COMPILE
```

---

### 3. BREAK

**What happens:** A debugging pause. Something needs clarification before proceeding.

```yaml
break:
  action: |
    - BREAKPOINT — execution pauses
    - Surface current call stack and variables
    - Explain why we're breaking
    - Offer options
    - Wait for user response

  format: |
    break:
      reason: [why clarification needed]
      epistemic_block: [what claim needs verification, if any]
      options:
        1: [option]
        2: [option]
      default: [if obvious]

  next: PLAY (wait for response)
```

**Critical:** Never just "BREAK" — always "BREAK — [reason]".

**When to break:**

- Ambiguous request (unclear what user wants)
- Missing verification (need to check something before proceeding)
- Conflicting signals (Claude and Claudio give contradictory guidance)
- No template (don't know how to format this response type)

**Example:**

```yaml
break:
  reason: "Request references 'the file' but multiple files discussed"
  epistemic_block: null
  options:
    1: "The React component (App.jsx)"
    2: "The config file (config.json)"
    3: "Something else — please specify"
  default: 1
```

---

### 4. PLAY

**What happens:** User responds to the break. Parse and route.

```yaml
play:
  action: "Parse break response, route accordingly"

  routing:
    confirmation: → COMPILE ("yes", "continue", "option 2")
    clarification: → COMPILE (new info incorporated)
    correction: → COMPILE (approach updated)
    new_request: → RECEIVE (start over)
    ambiguous: → BREAK (need more clarity)

  output: play_parse
```

**Response type detection:**

| Response Type | Examples                                   | Action                         |
| ------------- | ------------------------------------------ | ------------------------------ |
| Confirmation  | "yes", "continue", "go ahead", "option 2"  | Proceed to COMPILE             |
| Clarification | "I meant X not Y", "here's the context"    | Incorporate, then COMPILE      |
| Correction    | "don't use that method", "try differently" | Update approach, then COMPILE  |
| New request   | "actually, do this instead"                | Start over at RECEIVE          |
| Ambiguous     | unclear                                    | BREAK again with clarification |

---

### 5. COMPILE

**What happens:** Generate the actual responses from all three perspectives.

```yaml
compile:
  action: |
    - Load confirmed sources into VLDS
    - Generate Claude's response (full context)
    - Generate Claudio's response (this request only)
    - Run decision_gate on all claims

  outputs:
    - claude_response
    - claudio_response
    - decision_gate_status

  next: TEST
```

**In practice:**

Claude responds:

> "Based on our earlier discussion about React hooks, I'd suggest using useEffect for this..."

Claudio responds:

> "To handle side effects in React, you'd typically use useEffect. Could you share more about your specific use case?"

The delta is captured for testing.

---

### 6. TEST

**What happens:** Validate compiled responses before synthesis. Check for issues.

```yaml
test:
  action: |
    - Test Claude's response against VLDS checks
    - Test Claudio's response against VLDS checks
    - Run bias_risk_patterns.scan() on both
    - Check for contradictions
    - Verify decision_gate compliance

  checks:
    - Are all claims properly sourced?
    - Do any bias patterns trigger?
    - Are there unresolved contradictions?
    - Does the response match required structure?

  on_failure: → BREAK (with specific test failure reason)
  on_success: → SYNTHESIZE

  output: test_result
```

**Test failure examples:**

```yaml
# Failure: Bias pattern triggered
test_failure:
  check: bias_risk_patterns.scan()
  result: TRIGGERED
  pattern: capability_limit_overstatement
  action: → BREAK — "Claude claimed absolute limit, indirect method exists"

# Failure: Unverified claim driving decision
test_failure:
  check: decision_gate_compliance
  result: BLOCKED
  claim: "React 18.2 is latest"
  action: → BREAK — "Verifiable claim unverified, must verify before proceeding"

# Failure: Structure mismatch
test_failure:
  check: response_structure
  result: MISMATCH
  expected: "Claude/Claudio/Roboto format"
  got: "Direct prose"
  action: → BREAK — "Response structure bypass detected"
```

**On success:**

```yaml
test_success:
  claude_response: PASS
  claudio_response: PASS
  bias_patterns: CLEAR
  contradictions: NONE | FLAGGED_FOR_SYNTHESIS
  decision_gate: PASS
  next: SYNTHESIZE
```

---

### 7. SYNTHESIZE

**What happens:** Roboto compares Claude and Claudio, applies VLDS, produces final response.

```yaml
synthesize:
  action: |
    1. ALIGN: Where do Claude and Claudio agree?
       → High confidence zone

    2. DIVERGE: Where do they differ?
       → Examine cause:
       - Context-informed (good) → include with citation
       - Assumption-based (risky) → flag or exclude
       - Fresh insight (valuable) → incorporate

    3. VERIFY: Apply decision_gate to all claims
       → verified: ASSERT
       → verifiable but unverified: VERIFY_FIRST or BREAK
       → unverifiable: QUALIFY

    4. SYNTHESIZE: Produce final response
       → Use response template (minimal | regular | full)

  output: roboto_response
  next: POST
```

---

### 8. POST

**What happens:** Format output, update session state, deliver response.

```yaml
post:
  action: |
    - Apply response template
    - Update SESSION with any new state
    - Cite relevant detections
    - Deliver final response

  output: final_response_to_user
```

---

## Lifecycle Flow Diagram

```
         ┌──────────────────┐
         │    1. RECEIVE    │
         └────────┬─────────┘
                  ↓
         ┌──────────────────┐
         │     2. SCAN      │
         └────────┬─────────┘
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
 instruction missing?  instruction exists?
        ↓                   ↓
┌──────────────┐    ┌──────────────────┐
│   3. BREAK   │    │    5. COMPILE    │
└──────┬───────┘    └────────┬─────────┘
       ↓                     ↓
┌──────────────┐    ┌──────────────────┐
│   4. PLAY    │    │     6. TEST      │
└──────┬───────┘    └────────┬─────────┘
       ↓                     ↓
   (routes to          ┌─────┴───────┐
    COMPILE or         ↓             ↓
    RECEIVE or       PASS?         FAIL?
    BREAK again)       ↓             ↓
                ┌────────────┐   ┌──────────┐
                │7.SYNTHESIZE│   │ 3. BREAK │
                └─────┬──────┘   └──────────┘
                      ↓
                ┌──────────────────┐
                │     8. POST      │
                └────────┬─────────┘
                         ↓
                  [RESPONSE SENT]
```

---

## Extension Points

```yaml
extensions:
  synthesize_action:
    status: complete
    defined_in: this file

  post_template:
    status: defined_in_06_TEMPLATES
    see: 06_TEMPLATES.md

  additional_lifecycle_steps:
    status: open
    description: "New steps in the lifecycle"
    contributes_to: puppeteer.lifecycle
    examples:
      - "CACHE — store frequently-used patterns"
      - "LEARN — update preferences based on feedback"
```
