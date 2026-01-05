# Puppeteer Layer Fragment

```yaml
fragment:
  name: puppeteer_orchestration
  layer: puppeteer
  type: automation
  version: 0.1.0
```

## Lifecycle

```yaml
puppeteer:
  type: automation
  lifecycle:
    receive:
      action: "Request received"
      next: scan
      
    scan:
      action: "Identify influences, estimate divergence"
      routing:
        instruction_missing: break
        instruction_exists: compile
      next: break | compile
      
    break:
      action: "BREAKPOINT — surface state, await input"
      format: |
        break:
          reason: [why]
          options: [list]
      next: play
      
    play:
      action: "Parse break response, route"
      routing:
        confirmation: compile
        clarification: compile
        new_request: receive
        ambiguous: break
      next: compile | receive | break
      
    compile:
      action: "Generate Claude + Claudio responses"
      outputs: [claude_response, claudio_response]
      next: synthesize
      
    synthesize:
      action: # TBD via contributions
      next: post
      
    post:
      action: "Format, deliver"
      template: # TBD via contributions
```

## Extension Points

```yaml
extensions:
  synthesize_action:
    status: open
    description: "How Roboto synthesizes Claude + Claudio"
    contributes_to: puppeteer.lifecycle.synthesize.action
    
  post_template:
    status: open
    description: "Response format template"
    contributes_to: puppeteer.lifecycle.post.template
    
  additional_lifecycle_steps:
    status: open
    contributes_to: puppeteer.lifecycle
```
