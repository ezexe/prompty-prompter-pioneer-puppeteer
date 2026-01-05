# Response Templates Fragment

```yaml
fragment:
  name: response_templates
  layer: puppeteer  # applies at output
  type: skill
  version: 0.1.0
```

## Minimal

```yaml
minimal:
  pre:
    vlds_self_audit: PASS | FAIL
    decision_gate: PASS | BLOCKED
    
  response: |
    ## Claude's Take
    [response]
    
    ## Claudio's Take
    [response]
    
    ## Roboto's Synthesis
    [final]
    
  post:
    agreed: [count]
    diverged: [count]
```

## Regular

```yaml
regular:
  pre:
    vlds_self_audit:
      status: PASS | FAIL
      checks: [list]
    decision_gate: PASS | BLOCKED
    divergence_estimate: LOW | MEDIUM | HIGH
    
  response: |
    ## Claude's Take
    [response]
    context_used: [list]
    
    ## Claudio's Take
    [response]
    would_ask: [clarifying questions]
    
    ## Roboto's Synthesis
    alignment: [where agreed]
    divergence: [where differed]
    final_answer: [synthesis]
    
  post:
    verified_claims: [count]
    qualified_claims: [count]
    assumptions_extracted: [list]
```

## Full

```yaml
full:
  # TBD via contributions
  # See 05_VLDS.md extensions for epistemic audit
  # See 06_BIAS_PATTERNS.md for self-audit
```

## Extension Points

```yaml
extensions:
  full_template:
    status: open
    description: "Complete full audit template"
    contributes_to: response_templates.full
    
  custom_templates:
    status: open
    description: "Domain-specific response formats"
    contributes_to: response_templates
```
