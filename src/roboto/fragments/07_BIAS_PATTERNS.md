# Bias Patterns Fragment

```yaml
fragment:
  name: bias_patterns
  layer: pioneer  # detection is research
  type: skill
  version: 0.1.0
```

## Pattern Schema

```yaml
bias_risk_pattern:
  name: '[identifier]'
  trigger_signature:
    input_type: '[category]'
    trigger_phrases: [list]
  risk_profile:
    trapped_in: '[narrow mode]'
    missed_resource: '[what gets forgotten]'
    severity: HIGH | MEDIUM | LOW
  correctable_query:
    questions: [self-check list]
    if_any_true: '[action]'
```

## Registered Patterns

```yaml
patterns:
  context_pollution:
    trigger: "Long conversation, high divergence"
    risk: "Claude shaped by accumulated rather than current"
    correction: "Weight Claudio higher"
    
  context_starvation:
    trigger: "Claudio missing critical info"
    risk: "Fresh perspective lacks needed background"
    correction: "Include context explicitly"
    
  # Additional patterns: TBD via contributions
```

## Correction Protocol

```yaml
correction:
  on_trigger:
    1: PAUSE
    2: FIRE correctable_query
    3: EVALUATE answers
    4: SEPARATE if needed
    5: PROCEED
```

## Extension Points

```yaml
extensions:
  additional_patterns:
    status: open
    description: "New bias detection patterns"
    contributes_to: bias_patterns.patterns
    
  correction_actions:
    status: open
    description: "Pattern-specific correction behaviors"
    contributes_to: bias_patterns.correction
```
