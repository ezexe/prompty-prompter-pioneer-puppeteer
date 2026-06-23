# [Connector Name] Connector

> **Template.** Copy this directory to `extensions/connectors/[name]/` and fill the manifest block below.
> A connector bridges to an external system (API / data source / agent framework).

```yaml
extension:
  name: [connector_name]
  type: connector
  compatibility:
    p4_phases: [] # e.g. [puppeteer]
  interface:
    connector:
      protocol: [rest | graphql | websocket | mcp]
      endpoints:
        - path: [/path]
          method: [GET | POST | ...]
          purpose: "[what this endpoint is for]"
      auth:
        type: [none | bearer | api_key | oauth]
        env_var: [ENV_VAR_NAME] # if applicable
  hooks:
    on_prompty: []
    on_prompter: []
    on_pioneer: []
    on_puppeteer: []
```

[Describe the connector's behavior here.]
