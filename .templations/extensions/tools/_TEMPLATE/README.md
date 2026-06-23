# [Tool Name] Tool

> **Template.** Copy this directory to `extensions/tools/[name]/` and fill the manifest block below.
> A tool adds an execution capability (commands in, structured results out).
> No instance example ships yet — see `../../../../CONTRIBUTING.md` "Tool Extension".

```yaml
extension:
  name: [tool_name]
  type: tool
  compatibility:
    p4_phases: [] # e.g. [pioneer, puppeteer]
  interface:
    tool:
      commands: [] # e.g. [analyze, lint, complexity]
      parameters:
        [param_name]: [type] # e.g. file_path: string
      returns:
        [field_name]: [type] # e.g. findings: [finding]
  hooks:
    on_prompty: []
    on_prompter: []
    on_pioneer: []
    on_puppeteer: []
```

[Describe the tool's behavior here.]
