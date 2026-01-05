# VLDS Fragment

```yaml
fragment:
  name: vlds_transparency
  layer: prompter  # integrates at refinement
  type: skill
  version: 0.1.0
```

## Storage Model

```yaml
vlds:
  storage:
    virtual: "Simulated in context, stateless"
    localStorage: "Persists across sessions"
    dataStore: "Structured, queryable"
    sessionStorage: "Clears when session ends"
```

## Neural Tracking

```yaml
tracking:
  weights:
    w_claude: "Sources Claude wanted"
    w_claudio: "Sources Claudio used (request-only)"
    w_roboto: "Sources activated in synthesis"
    
  biases:
    b_claude: "Assumptions from accumulated context"
    b_claudio: "Fresh assumptions from request only"
    b_roboto: "Assumptions after correction"
    
  activation_functions:
    fired: "Tools/instructions that processed w/b"
```

## Decision Gate

```yaml
decision_gate:
  verified_true: FULL      # Assert, recommend, execute
  verifiable_unverified: BLOCKED  # Must verify first
  unverifiable: QUALIFIED  # State with uncertainty
```

## Extension Points

```yaml
extensions:
  epistemic_system:
    status: open
    description: "Full claim verification schema"
    contributes_to: vlds.decision_gate
    
  layers:
    status: open
    description: "RUNTIME, SESSION, CONVERSATION, CONTEXT tracking"
    contributes_to: vlds.tracking
```
