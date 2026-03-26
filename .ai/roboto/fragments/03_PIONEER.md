# Pioneer Layer Fragment

```yaml
fragment:
  name: pioneer_exploration
  layer: pioneer
  type: research
  version: 0.1.0
  depends_on: [00_BASE, 01_PROMPTY, 02_PROMPTER]
```

---

## What Pioneer Is

**Pioneer** is the exploration layer — experimental techniques and frontier findings. This is where we discover new patterns through testing and iteration.

In the P4 lifecycle:

- Prompty = ideation — raw concepts
- Prompter = engineering — structured templates
- **Pioneer** = **research** — **experiments and discoveries**
- Puppeteer = automation — orchestration

---

## Core Experiments

### Scope Isolation Experiment

**Hypothesis:** Per-request isolation catches accumulated blind spots.

**Mechanism:**

```
Claude accumulates context turn by turn.
Claudio resets each request — perpetual fresh start.
The delta between them reveals assumption creep.
```

**How it works in practice:**

Turn 1:

- Claude sees: [system + request1]
- Claudio sees: [system + request1]
- Delta: 0 (same starting point)

Turn 5:

- Claude sees: [system + turn1 + turn2 + turn3 + turn4 + request5]
- Claudio sees: [system + request5]
- Delta: 4 turns of accumulated context

Turn 20:

- Claude sees: [system + 19 turns + request20]
- Claudio sees: [system + request20]
- Delta: 19 turns of accumulated context

**Findings:**

- Claudio often asks clarifying questions that Claude assumed away
- Claudio catches when Claude over-personalized
- Claudio provides baseline "what would anyone need to know?"
- Longer conversations = larger divergence = more assumption surface

---

### Recursive Prompt Growth Experiment

**Hypothesis:** Each response grows the effective prompt for the next iteration.

**Mechanism:**

```yaml
recursive_growth:
  turn_1: "[system] + [request]"
  turn_2: "[system] + [turn1_exchange] + [request]"
  turn_N: "[system] + [all_prior_turns] + [request]"

  claude_context: "Grows with conversation"
  claudio_context: "Stays fixed at [system + current_request]"
```

**What this reveals:**

The recursive growth is IN CLAUDE'S CONTEXT. Claudio's per-request isolation is the CONTROL GROUP.

By comparing Claude (growing context) with Claudio (fixed context), we can see exactly what the accumulated context contributes — and what it contaminates.

**Findings:**

- Longer conversations = larger Claude/Claudio divergence
- Divergence reveals accumulated state
- Useful for debugging assumptions
- Can measure "context value" vs "context pollution"

---

## Detection Techniques

### Assumption Detection

**Purpose:** Find things Claude "knows" that aren't in the current request.

**Method:**

```
1. Get Claude's response (with context)
2. Get Claudio's response (without context)
3. Diff the responses
4. Anything in Claude's response NOT derivable from current request alone = assumption
```

**Output:** `assumption_list`

**Example:**

```yaml
request: "How should I structure this?"

claude_response: "Based on your React project, I'd suggest..."
claudio_response: "I'd need to know what you're building first"

assumption_detected:
  claim: "User is working on a React project"
  source: "Prior conversation (turn 3)"
  derivable_from_current_request: false
  classification: ASSUMPTION
```

---

### Blind Spot Detection

**Purpose:** Find things Claude should have addressed but didn't.

**Method:**

```
1. Get Claudio's response (fresh)
2. Check what questions Claudio would ask
3. Check if Claude answered those implicitly
4. If yes: Claude used context (good)
5. If no: Claude assumed (risky) or missed entirely
```

**Output:** `blind_spot_list`

**Example:**

```yaml
request: "Can you fix the bug?"

claudio_would_ask:
  - "Which bug?"
  - "What file?"
  - "What's the expected behavior?"

claude_answered_implicitly:
  - "Which bug?" → Yes, referenced "the null pointer from earlier"
  - "What file?" → No, just said "in the code"
  - "Expected behavior?" → No, assumed user knows

blind_spots:
  - "file location not specified"
  - "expected behavior not confirmed"
```

---

## Bias Risk Patterns

These patterns trigger BEFORE response generation to catch error-causing tendencies.

### Context Pollution

```yaml
bias_risk_pattern:
  name: context_pollution

  trigger_signature:
    condition: "Long conversation + high Claude/Claudio divergence"
    signs:
      - conversation_length > 10 turns
      - divergence_score > 0.7

  risk_profile:
    trapped_in: "Accumulated context mode"
    scope_collapsed_to: "Prior discussion frame"
    missed_resource: "Fresh perspective on current request"
    severity: MEDIUM

  correction:
    action: "Weight Claudio's fresh perspective higher"
    rationale: "Claude may be over-indexed on stale context"
```

### Context Starvation

```yaml
bias_risk_pattern:
  name: context_starvation

  trigger_signature:
    condition: "Claudio's response missing critical info"
    signs:
      - claudio_asks_many_questions: true
      - questions_claude_answered: true

  risk_profile:
    trapped_in: "Fresh perspective mode"
    scope_collapsed_to: "Current request only"
    missed_resource: "Relevant prior context"
    severity: LOW

  correction:
    action: "Include context explicitly in synthesis"
    rationale: "Claudio correctly identified needed info; Claude has it"
```

---

## Extension Points

```yaml
extensions:
  blind_spot_method:
    status: complete
    defined_in: this file

  additional_experiments:
    status: open
    description: "New experiments beyond scope isolation and recursive growth"
    contributes_to: pioneer.artifacts.experiments
    examples:
      - "confidence_calibration — track prediction accuracy over time"
      - "assumption_decay — do assumptions become stale?"

  novel_techniques:
    status: open
    description: "New detection/analysis techniques"
    contributes_to: pioneer.techniques
```
