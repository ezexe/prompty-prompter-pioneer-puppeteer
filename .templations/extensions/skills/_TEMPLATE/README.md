# [Skill Name] Skill

> **Template.** Copy this directory to `extensions/skills/[name]/` and fill the manifest block below.
> A skill adds domain knowledge / a named capability the persona performs.
> Worked examples: `.ai/roboto/extensions/skills/isomorphic_operations/`, `sjc_indexer/`.
> Encouraged: inline fenced example blocks in the sections they illustrate.
> Optional siblings: `tests/phase_hook/`, `tests/integration/`.

```yaml
extension:
  name: [skill_name]
  type: skill
  compatibility:
    p4_phases: [] # phases this skill hooks, e.g. [pioneer, puppeteer]
    depends_on: [] # fragment / extension ids, e.g. [identity, vlds]
  interface:
    skill:
      domains: [] # knowledge domains this skill covers
      capabilities: [] # named capabilities it adds
  hooks:
    on_prompty: []
    on_prompter: []
    on_pioneer: []
    on_puppeteer: []
```

[Describe the skill's behavior here.]
