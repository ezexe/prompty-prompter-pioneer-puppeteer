# 🤝 Contributing

## 🔌 Extensibility

P4 is designed as an open framework. Extensions plug into any lifecycle phase.

### Extension Model

```
  TOOLS          SKILLS           CONNECTORS
  ─────          ──────           ──────────
Execution        Domain           Integration
Capabilities    Knowledge           Bridges

• bash          • docx           • API endpoints
• file_ops      • pptx           • External LLMs
• web_search    • xlsx           • Data sources
• code_exec     • pdf            • Agent frameworks
• ...           • frontend       • MCP servers
                • ...            • ...
```

### Extension Schema

```yaml
# /extensions/[type]/[name]/EXTENSION.yaml

extension:
  name: string
  type: tool | skill | connector
  version: semver

  compatibility:
    p4_phases: [prompty, prompter, pioneer, puppeteer]
    min_version: string

  interface:
    # Tools: execution interface
    tool:
      commands: [string]
      parameters: schema
      returns: schema

    # Skills: knowledge interface
    skill:
      domains: [string]
      capabilities: [string]
      skill_file: path/to/SKILL.md

    # Connectors: integration interface
    connector:
      protocol: rest | graphql | websocket | mcp
      endpoints: [endpoint_schema]
      auth: auth_schema

  hooks:
    on_prompty: [actions] # Seed phase hooks
    on_prompter: [actions] # Refinement phase hooks
    on_pioneer: [actions] # Exploration phase hooks
    on_puppeteer: [actions] # Orchestration phase hooks
```

### Creating Extensions

#### Tool Extension

```yaml
# /extensions/tools/code_analyzer/EXTENSION.yaml

extension:
  name: code_analyzer
  type: tool
  version: 1.0.0

  interface:
    tool:
      commands: [analyze, lint, complexity]
      parameters:
        file_path: string
        language: string?
        depth: shallow | deep
      returns:
        findings: [finding]
        metrics: metrics_object

  hooks:
    on_pioneer:
      - analyze_novel_patterns
    on_puppeteer:
      - automated_code_review
```

#### Skill Extension

```yaml
# /extensions/skills/api_design/EXTENSION.yaml

extension:
  name: api_design
  type: skill
  version: 1.0.0

  interface:
    skill:
      domains: [rest, graphql, grpc, websocket]
      capabilities:
        - schema_generation
        - endpoint_design
        - documentation
      skill_file: ./SKILL.md

  hooks:
    on_prompter:
      - validate_api_patterns
    on_pioneer:
      - explore_novel_architectures
```

#### Connector Extension

```yaml
# /extensions/connectors/openai_bridge/EXTENSION.yaml

extension:
  name: openai_bridge
  type: connector
  version: 1.0.0

  interface:
    connector:
      protocol: rest
      endpoints:
        - path: /v1/chat/completions
          method: POST
          purpose: cross_model_prompting
      auth:
        type: bearer
        env_var: OPENAI_API_KEY

  hooks:
    on_puppeteer:
      - multi_model_orchestration
      - comparative_prompting
```

---

### Adding Extensions

1. **Identify the extension type** (tool, skill, connector)
2. **Determine phase affinity** (which P4 phases benefit)
3. **Create extension manifest** following the schema
4. **Implement hooks** for relevant phases
5. **Document capabilities** in extension README
6. **Submit for integration**

### Extension Guidelines

```yaml
guidelines:
  naming:
    pattern: lowercase_with_underscores
    prefix_by_type: false # Let type field distinguish

  versioning:
    scheme: semver
    breaking_changes: major_bump_required

  documentation:
    required: [README.md, EXTENSION.yaml]
    recommended: [EXAMPLES.md, CHANGELOG.md]

  testing:
    required: phase_hook_tests
    recommended: integration_tests
```

---

## 🔗 Integration Guide

### With Style Instructions

P4 integrates with style systems (like userStyle configurations) at the Prompter phase:

```yaml
style_integration:
  phase: prompter

  mapping:
    identity: persona_configuration
    tone: response_formatting
    memory_system: session_persistence
    epistemic_system: verification_gates
    vlds: transparency_layer

  hooks:
    pre_compile: validate_style_compliance
    post_compile: audit_style_application
```

### With Tool Systems

```yaml
tool_integration:
  phases: [pioneer, puppeteer]

  capabilities:
    file_operations:
      tools: [create_file, str_replace, view]
      phase_affinity: puppeteer

    web_access:
      tools: [web_search, web_fetch]
      phase_affinity: pioneer

    execution:
      tools: [bash_tool]
      phase_affinity: puppeteer
```

### With Skill Systems

```yaml
skill_integration:
  phases: [prompter, pioneer]

  skill_types:
    document_creation:
      skills: [docx, pptx, xlsx, pdf]
      phase_affinity: prompter

    specialized_knowledge:
      skills: [frontend-design, product-self-knowledge]
      phase_affinity: pioneer

    meta_skills:
      skills: [skill-creator]
      phase_affinity: prompty
```

### With Connector Systems

```yaml
connector_integration:
  phases: [puppeteer]

  connector_types:
    llm_bridges:
      purpose: multi_model_orchestration
      protocols: [rest, mcp]

    data_sources:
      purpose: knowledge_augmentation
      protocols: [rest, graphql]

    agent_frameworks:
      purpose: extended_orchestration
      protocols: [mcp, websocket]
```

## Roadmap Contributions

Priority areas for extension development:

| Area                      | Type      | Priority | Description                       |
| ------------------------- | --------- | -------- | --------------------------------- |
| Multi-model orchestration | Connector | High     | Cross-LLM prompt routing          |
| Prompt versioning         | Tool      | High     | Git-like prompt history           |
| A/B testing framework     | Tool      | Medium   | Comparative prompt evaluation     |
| Visual prompt builder     | Skill     | Medium   | Graphical P4 lifecycle management |
| Telemetry connector       | Connector | Medium   | Prompt performance analytics      |
