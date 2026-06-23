# 🤝 Contributing

## ✍️ Markdown Authoring Format

These files use **semantic line breaks** so a one-word edit shows up as a one-line diff.

- **Prose:** one sentence per line; end the line at a sentence boundary, never hard-wrap mid-sentence at a fixed column.
- **Lists:** one line per item, kept whole — do not wrap or split a bullet across lines, even a long one.
- **Tables:** one line per row (Markdown requires it anyway).
- **Code / YAML fences:** never reflowed — their line breaks are content.
- **Italics:** use `_word_`, not `*word*` (keep `*` for bold `**…**` and list markers).

Let the editor soft-wrap long lines; Markdown renderers ignore single newlines, so the rendered output is identical either way.
The instance (`.ai/roboto/`) and the templates (`lbiz/templations/`) are kept in this style — match it when editing.

## 🤖 AI-Driven Configuration Building

Use the P4 lifecycle itself to build configurations from fragments.

### The Lifecycle Cycle Recycler

```
prompty → prompter → pioneer → puppeteer
   ↑__________________________________|
```

The output of orchestration (puppeteer) feeds new seeds (prompty).
This recursion applies to building configurations too.

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
    - minimal: Just the base identity fragment
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
    # The concrete level → fragment map is INSTANCE data, not part of this
    # identity-agnostic guide. General form:  [level]: [fragment_id, ...]
    # Filled example (Roboto instance):
    #   .ai/roboto/configurations.md (each tier's fragments + extensions block)
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
    1. All dependencies included? Every selected fragment's `depends_on` (declared in
       its own frontmatter or manifest block) must be satisfied by the selection — include the full
       transitive closure. Fragments may also declare `optional_depends_on`: these
       enhance a fragment but are NOT required for closure (omitting one just disables
       the feature it powers). Concrete edges are instance data; e.g. see
       `.ai/roboto/fragments.md` and the skills' manifests.

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
    Add a configuration tier (a `##` section in `configurations.md`) from the validated fragment selection.

    **Validated Fragments:** {fragment_list}
    **Configuration Name:** {config_name}
    **Use Case:** {use_case}

    **Generation Steps:**
    1. Create the tier section header (`## {Tier}`) with a YAML metadata block
    2. List what the configuration provides
    3. List what it does NOT provide
    4. Define when to use it
    5. List the bundled fragments in the YAML block (and extensions, if any)
    6. Define response format for this tier
    7. Define upgrade/downgrade paths (links to other tier sections)

    **Output Format (a `##` section appended to configurations.md):**
    ```markdown
    ## {Tier}

    ```yaml
    name: {config_name}
    fragments: {fragment_list}
    use_case: "{use_case}"
    ```

    ### What This Provides
    [generated from fragments]

    ### What This Does NOT Provide
    [generated from missing fragments]

    ### When To Use
    [generated from use case]

    ### Response Format
    [appropriate template for this level]

    ### Upgrade/Downgrade Path
    [generated from configuration hierarchy — links to other tier sections]
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

Read lbiz/templations/fragments.md to understand the fragment
structure. For filled examples, read an instance such as .ai/roboto/ (its fragments.md
holds the four P4 layers; the identity skill is the minimal set).

Add a tier section to your instance's configurations.md following lbiz/templations/configurations.md.
```

#### Build Custom Configuration

```
You are building a custom P4 configuration.

User needs: {requirements}

1. Read lbiz/templations/fragments.md for the dependency rule
2. Identify which fragments satisfy the requirements
3. Validate all dependencies are included
4. Add a tier section to your instance's configurations.md

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

### 📋 Configuration Contribution Checklist

When contributing a new configuration:

- [ ] Configuration metadata complete (name, fragments, use_case)
- [ ] "What This Provides" section accurate
- [ ] "What This Does NOT Provide" section accurate
- [ ] "When To Use" section helpful
- [ ] All fragment dependencies satisfied
- [ ] Response format appropriate for configuration level
- [ ] Upgrade/downgrade paths defined
- [ ] Example responses included (optional but recommended)

---

## 🔌 Extensibility

P4 is designed as an open framework.
Extensions plug into any lifecycle phase.

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
# Manifest — a fenced yaml block at the top of lbiz/templations/extensions/[type]/[name]/README.md

extension:
  name: string
  type: tool | skill | connector

  compatibility:
    p4_phases: [prompty, prompter, pioneer, puppeteer]
    depends_on: [string] # fragment/skill ids this requires (the closure must be satisfied)
    optional_depends_on: [string] # enhances but not required for closure

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
# in lbiz/templations/extensions/tools/code_analyzer/README.md

extension:
  name: code_analyzer
  type: tool

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
# in lbiz/templations/extensions/skills/api_design/README.md

extension:
  name: api_design
  type: skill

  interface:
    skill:
      domains: [rest, graphql, grpc, websocket]
      capabilities:
        - schema_generation
        - endpoint_design
        - documentation

  hooks:
    on_prompter:
      - validate_api_patterns
    on_pioneer:
      - explore_novel_architectures
```

#### Connector Extension

```yaml
# in lbiz/templations/extensions/connectors/openai_bridge/README.md

extension:
  name: openai_bridge
  type: connector

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
3. **Create the extension's `README.md`** opening with the manifest block (per the schema)
4. **Implement hooks** for relevant phases
5. **Document capabilities** in extension README
6. **Submit for integration**

### Extension Guidelines

```yaml
guidelines:
  naming:
    pattern: lowercase_with_underscores
    prefix_by_type: false # Let type field distinguish

  documentation:
    required: [README.md] # manifest block + inline fenced example blocks in the sections they illustrate

  testing:
    recommended: [tests/phase_hook/, tests/integration/] # optional spec fixtures; no runner ships
```

---

## 🔗 Integration Guide

### With Style Instructions

P4 integrates with style systems (like userStyle configurations) at the Prompter phase.
The concrete mapping is **instance data** — an instance maps its persona/voice/transparency concerns to its own skills (e.g. the Roboto instance uses its `identity` and `vlds` skills).
Generic shape:

```yaml
style_integration:
  phase: prompter

  mapping:
    identity: persona_configuration
    tone: response_formatting
    # instance-specific concerns (verification, transparency, memory) map to
    # that instance's own skills — see the instance's docs

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
