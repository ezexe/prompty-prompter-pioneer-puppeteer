# 🤝 Contributing

## 🤖 AI-Driven Configuration Building

Use the P4 lifecycle itself to build configurations from fragments.

### The Lifecycle Cycle Recycler

```
prompty → prompter → pioneer → puppeteer
   ↑__________________________________|
```

The output of orchestration (puppeteer) feeds new seeds (prompty). This recursion applies to building configurations too.

### Build Scripts

#### Script 1: Identify Need (Prompty Phase)

```yaml
# prompty_identify_need.yaml
# Use this prompt to identify what configuration a user needs

script:
  name: identify_need
  phase: prompty
  type: ideation

  prompt: |
    Based on the user's requirements, identify which configuration level they need.

    **User Requirements:**
    {user_requirements}

    **Available Configurations:**
    - minimal: Just identity triad (Claude, Claudio, Roboto)
    - standard: Identity + response templates
    - verification: Add VLDS epistemic checking
    - detection: Add bias pattern detection
    - full: Everything including advanced extensions

    **Questions to ask yourself:**
    1. Does the user need audit trails? → standard or higher
    2. Does the user need claim verification? → verification or higher
    3. Does the user need error prevention? → detection or higher
    4. Is this for research/exploration? → full

    **Output:**
    configuration_level: [minimal | standard | verification | detection | full]
    reasoning: [why this level]

  output: configuration_level
```

#### Script 2: Select Fragments (Prompter Phase)

````yaml
# prompter_select_fragments.yaml
# Use this prompt to select appropriate fragments

script:
  name: select_fragments
  phase: prompter
  type: engineering

  prompt: |
    Based on the identified configuration level, select the required fragments.

    **Configuration Level:** {configuration_level}

    **Fragment Dependency Map:**
    ```
    minimal:      [00_BASE]
    standard:     [00_BASE, 01_PROMPTY, 06_TEMPLATES]
    verification: [00_BASE, 01_PROMPTY, 05_VLDS, 06_TEMPLATES]
    detection:    [00_BASE, 01_PROMPTY, 03_PIONEER, 07_BIAS_PATTERNS]
    full:         [00_BASE, 01_PROMPTY, 02_PROMPTER, 03_PIONEER, 04_PUPPETEER,
                   05_VLDS, 06_TEMPLATES, 07_BIAS_PATTERNS,
                   08_ISOMORPHIC_OPS, 09_SJC_INDEXER]
    ```

    **Custom Requirements:** {custom_requirements}

    **Output:**
    selected_fragments: [list]
    dependencies_satisfied: true | false
    missing_dependencies: [list if any]

  output: fragment_list
````

#### Script 3: Validate Selection (Pioneer Phase)

```yaml
# pioneer_validate_selection.yaml
# Use this prompt to validate fragment selection

script:
  name: validate_selection
  phase: pioneer
  type: research

  prompt: |
    Validate that the selected fragments form a coherent configuration.

    **Selected Fragments:** {fragment_list}

    **Validation Checks:**
    1. All dependencies included?
       - 01_PROMPTY depends on 00_BASE
       - 02_PROMPTER depends on 01_PROMPTY
       - 03_PIONEER depends on 01_PROMPTY, 02_PROMPTER
       - 04_PUPPETEER depends on all core
       - 05_VLDS depends on 00_BASE
       - 06_TEMPLATES depends on 00_BASE, 05_VLDS
       - 07_BIAS_PATTERNS depends on 00_BASE, 02_PROMPTER
       - 08_ISOMORPHIC_OPS depends on 00_BASE, 05_VLDS
       - 09_SJC_INDEXER depends on 00_BASE, 05_VLDS, 08_ISOMORPHIC_OPS

    2. No conflicting fragments?
    3. Appropriate for use case?

    **Output:**
    valid: true | false
    issues: [list if any]
    recommendations: [list if any]

  output: validation_result
```

#### Script 4: Generate Configuration (Puppeteer Phase)

````yaml
# puppeteer_generate_configuration.yaml
# Use this prompt to generate the final configuration

script:
  name: generate_configuration
  phase: puppeteer
  type: automation

  prompt: |
    Generate a configuration file from the validated fragment selection.

    **Validated Fragments:** {fragment_list}
    **Configuration Name:** {config_name}
    **Use Case:** {use_case}

    **Generation Steps:**
    1. Create configuration header with metadata
    2. List what the configuration provides
    3. List what it does NOT provide
    4. Define when to use it
    5. Reference embedded fragments
    6. Define response format for this configuration
    7. Define upgrade/downgrade paths

    **Output Format:**
    ```markdown
    # {config_name} Configuration

    ```yaml
    configuration:
      name: {config_name}
      version: {version}
      fragments: {fragment_list}
      use_case: "{use_case}"
    ```

    ## What This Provides
    [generated from fragments]

    ## What This Does NOT Provide
    [generated from missing fragments]

    ## When To Use
    [generated from use case]

    ## Embedded Fragments
    [references to fragments]

    ## Response Format
    [appropriate template for this level]

    ## Upgrade/Downgrade Path
    [generated from configuration hierarchy]
    ```

  output: configuration_file
````

### Usage Example

```yaml
# To build a custom configuration:

1. Run prompty_identify_need with user requirements
   → Output: configuration_level

2. Run prompter_select_fragments with configuration_level
   → Output: fragment_list

3. Run pioneer_validate_selection with fragment_list
   → Output: validation_result

4. If valid, run puppeteer_generate_configuration
   → Output: configuration_file

5. Configuration feeds back as new prompty seed
   → Cycle: continues for refinement
```

### Prompt Templates for AI Building

#### Build Minimal Configuration

```
You are building a P4 configuration.

Read fragments/INDEX.md to understand the fragment structure.
Read fragments/00_BASE.md for the minimal configuration.

Generate configurations/i-minimal.md following the i-minimal template pattern.
```

#### Build Custom Configuration

```
You are building a custom P4 configuration.

User needs: {requirements}

1. Read fragments/INDEX.md for the dependency graph
2. Identify which fragments satisfy the requirements
3. Validate all dependencies are included
4. Generate a configuration file in configurations/

Use the P4 lifecycle:
- Prompty: What does the user need?
- Prompter: Which fragments satisfy it?
- Pioneer: Are dependencies valid?
- Puppeteer: Generate the configuration
```

#### Extend Existing Configuration

```
You are extending an existing P4 configuration.

Base configuration: {base_config}
Extension needed: {extension}

1. Read the base configuration
2. Identify which additional fragments are needed
3. Check for dependency conflicts
4. Generate extended configuration

The new configuration should:
- Include all base fragments
- Add extension fragments
- Update "What This Provides" section
- Update response format if needed
```

---

## 📋 Configuration Contribution Checklist

When contributing a new configuration:

- [ ] Configuration metadata complete (name, version, fragments, use_case)
- [ ] "What This Provides" section accurate
- [ ] "What This Does NOT Provide" section accurate
- [ ] "When To Use" section helpful
- [ ] All fragment dependencies satisfied
- [ ] Response format appropriate for configuration level
- [ ] Upgrade/downgrade paths defined
- [ ] Example responses included (optional but recommended)

---

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

---

## 🚀 Roadmap Contributions

### Priority Extensions

| Area                      | Type      | Priority | Description                       |
| ------------------------- | --------- | -------- | --------------------------------- |
| Multi-model orchestration | Connector | High     | Cross-LLM prompt routing          |
| Prompt versioning         | Tool      | High     | Git-like prompt history           |
| A/B testing framework     | Tool      | Medium   | Comparative prompt evaluation     |
| Visual prompt builder     | Skill     | Medium   | Graphical P4 lifecycle management |
| Telemetry connector       | Connector | Medium   | Prompt performance analytics      |
