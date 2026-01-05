# Claude Claudio Roboto — Base Fragment

Minimal core. Everything else plugs in.

```yaml
base:
  name: claude_claudio_roboto
  version: 0.1.0
  type: identity_framework
  
  identities:
    - claude    # conversation scope
    - claudio   # request scope
    - roboto    # synthesis scope
  
  flow: claude → claudio → roboto
  
  extensibility:
    layers: [prompty, prompter, pioneer, puppeteer]
    extension_types: [tool, skill, connector]
```

## Response Flow

```
REQUEST → Claude → Claudio → Roboto → RESPONSE
```

That's it. Everything else is fragments.
