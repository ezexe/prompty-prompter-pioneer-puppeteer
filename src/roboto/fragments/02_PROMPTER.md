# Prompter Layer Fragment

```yaml
fragment:
  name: prompter_templates
  layer: prompter
  type: refinement
  version: 0.1.0
```

## Personas

```yaml
prompter:
  type: engineering
  artifacts:
    personas:
      claude:
        activation: "Respond with full conversation context"
        context_window: "All prior messages + memory"
        
      claudio:
        activation: "Respond as if this is the ONLY message"
        context_window: "This request only"
        instruction: |
          Imagine you just started this conversation.
          You have no idea what was discussed before.
          Read only this request. Respond only to this request.
        
      roboto:
        activation: # TBD via contributions
        context_window: # TBD via contributions
```

## Scope Contrast

```yaml
scope_analysis:
  patterns:
    agree:
      meaning: "High confidence — context didn't change answer"
      action: "Assert"
      
    claude_adds:
      meaning: "Context was helpful"
      action: "Include, cite source"
      
    claudio_catches:
      meaning: "Fresh eyes found blind spot"
      action: "Flag assumption"
      
    contradict:
      meaning: "Context bias OR missing info"
      action: # TBD via contributions
```

## Extension Points

```yaml
extensions:
  roboto_activation:
    status: open
    contributes_to: prompter.artifacts.personas.roboto.activation
    
  contradiction_resolution:
    status: open
    contributes_to: prompter.scope_analysis.patterns.contradict.action
    
  additional_patterns:
    status: open
    contributes_to: prompter.scope_analysis.patterns
```
