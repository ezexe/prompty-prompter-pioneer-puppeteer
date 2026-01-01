# Prompty Prompter Pioneer Puppeteer the P4

<div align="center">

**P4** — The Recursive Prompt 🕸️

[![Lifecycle](https://img.shields.io/badge/lifecycle-prompty→prompter→pioneer→puppeteer-blue)](#-lifecycle-cycle-recycler)
[![Protocol](https://img.shields.io/badge/protocol-recursive--discovery-purple)](#️-architecture)
[![Extensions](https://img.shields.io/badge/extensions-tools%20%7C%20skills%20%7C%20connectors-green)](#-extensibility)

</div>

---

> _A prompty prompt that a prompter-pioneer can promptly puppeteer, when a pioneering promptly-prompted prompt needs to get prompted to promptly prompt a pioneering puppeteer's prompt. Is the prompty prompt that needs to be promptly-prompted when a prompty-prompter-pioneer-puppeteer needs prompts for a prompt to prompt a prompt, to get prompted by a prompt, to prompt the prompts that should prompt the prompter—so it could puppeteer the prompt that would prompt a prompty prompt puppet prompt to puppeteer the prompt as a prompter to pioneer the prompt that a prompty-prompter-pioneer-puppeteer could prompt to be the puppet of the prompter pioneer puppeteer._

While it sounds like a tongue-twister, this "word salad" encodes the **Prompty Thy Prompt** technical philosophy: _prompts that build prompts that orchestrate prompts_.

The _3core prompty thy prompt_ philosophy:

---

## 🛠️ Philosophy

The P4 operates on the _3core prompty thy prompt_ principles:

| Principle              | Phase               | Description                                                   |
| ---------------------- | ------------------- | ------------------------------------------------------------- |
| **Engineering-Ready**  | Prompty → Prompter  | Transform raw concepts into refined, deliverable instructions |
| **Discovery-Driven**   | Prompter → Pioneer  | Push into frontier research and emergent reasoning patterns   |
| **Automation-Focused** | Pioneer → Puppeteer | Orchestrate agents with full control over prompt chains       |

Every prompt exists in a state of becoming. A **Prompty** seed contains the potential for a **Prompter** template, which can evolve into a **Pioneer** experiment, which can mature into a **Puppeteer** orchestration—and the cycle recurses.


---

## 🔄 Lifecycle Cycle Recycler

> _P4 b4 its 2 l8 in the after 8_

```
  ┌──────────┐      ┌───────────┐      ┌──────────┐
  │  PROMPTY │      │ PROMPTER  │      │ PIONEER  │
  │          │ ───▶ │           │ ───▶ │          │
  │  seed    │      │  refine   │      │  explore │
  └──────────┘      └───────────┘      └──────────┘
        ▲                                    │     
        │                                    ▼     
        │           ┌───────────┐            |   
        └────────── │ PUPPETEER │ ◀──────────┘     
                    │           │                  
                    │ automate  │                  
                    └───────────┘
```

### Phase Definitions

| Phase         | Purpose                                                         | Artifacts                              | Outputs To        |
| ------------- | --------------------------------------------------------------- | -------------------------------------- | ----------------- |
| **Prompty**   | Lightweight templates, raw seed-ideas, initial concepts         | `.prompty` files, sketches, fragments  | Prompter          |
| **Prompter**  | Refined personas, system-level instructions, validated patterns | `.prompter` configs, style guides      | Pioneer           |
| **Pioneer**   | Experimental techniques, frontier research, novel reasoning     | `.pioneer` experiments, findings       | Puppeteer         |
| **Puppeteer** | Agent loops, orchestration logic, automated workflows           | `.puppeteer` orchestrations, pipelines | Prompty (recurse) |

---

## 🏗️ Architecture

### Core Narrative: Prompts Building Prompts

P4 implements **recursive prompting**—a method where an AI (the Puppeteer) generates, refines, and orchestrates other prompts through systematic phases.

```yaml
architecture:
  pattern: recursive_prompt_engineering

  layers:
    seed_layer: # Prompty
      type: ideation
      artifacts: [concepts, fragments, raw_templates]

    refinement_layer: # Prompter
      type: engineering
      artifacts: [personas, system_prompts, validated_patterns]

    exploration_layer: # Pioneer
      type: research
      artifacts: [experiments, novel_techniques, frontier_findings]

    orchestration_layer: # Puppeteer
      type: automation
      artifacts: [agent_loops, pipelines, meta_controllers]

  recursion:
    trigger: orchestration_output
    feeds_into: seed_layer
    enables: continuous_evolution
```

### The Manifesto Decoded

Stripping away the phonetic play, the mission is:

1. **"A good prompt that an expert can use to control an AI..."**
   - Prompty seeds become Prompter-refined instructions

2. **"...is needed when you want to discover new AI behaviors..."**
   - Pioneer phase explores what prompts _can_ do

3. **"...especially when that AI needs to be told exactly how to behave by another prompt."**
   - Puppeteer orchestrates prompt-to-prompt control

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

## 📖 Usage Patterns

### Pattern 1: Linear Progression

```
prompty → prompter → pioneer → puppeteer
```

Standard lifecycle for developing a prompt from concept to automation.

```bash
# 1. Create seed
p4 prompty create "chatbot personality" --output ./seeds/

# 2. Refine into prompter
p4 prompter refine ./seeds/chatbot-personality.prompty

# 3. Pioneer experimental variations
p4 pioneer explore ./prompters/chatbot-personality.prompter

# 4. Puppeteer into automation
p4 puppeteer orchestrate ./pioneers/chatbot-personality.pioneer
```

### Pattern 2: Recursive Refinement

```
puppeteer → prompty → prompter → pioneer → puppeteer
       ↑___________________________________|
```

The output of orchestration feeds new seeds.

```yaml
recursive_refinement:
  trigger: puppeteer_output_analysis

  cycle:
    - phase: analyze
      action: Extract patterns from orchestration results

    - phase: seed
      action: Generate new prompty seeds from patterns

    - phase: refine
      action: Develop seeds through prompter phase

    - phase: explore
      action: Pioneer test new refinements

    - phase: integrate
      action: Puppeteer incorporates validated improvements
```

### Pattern 3: Parallel Exploration

```
              ┌─ pioneer_a ─┐
prompty ─ prompter ─┼─ pioneer_b ─┼─ puppeteer
              └─ pioneer_c ─┘
```

Multiple pioneer experiments from single prompter, best results orchestrated.

### Pattern 4: Meta-Prompting

```
puppeteer_a ──┐
puppeteer_b ──┼── meta_puppeteer ── prompty (new generation)
puppeteer_c ──┘
```

Puppeteers orchestrating puppeteers for emergent prompt evolution.

---

## 🧩 Technical Concepts

### Prompt-Chaining

The output of one prompt becomes the input for the next.

```yaml
prompt_chain:
  - id: extract
    prompt: "Extract key entities from: {input}"
    output: entities

  - id: analyze
    prompt: "Analyze relationships between: {entities}"
    output: relationships

  - id: generate
    prompt: "Generate summary from: {relationships}"
    output: final
```

### Meta-Prompting

Writing prompts that create better prompts for specific tasks.

```yaml
meta_prompt:
  purpose: prompter_generator

  template: |
    Given the task domain: {domain}
    And the target audience: {audience}
    And the desired output format: {format}

    Generate a system prompt that will:
    1. Establish appropriate persona
    2. Define clear constraints
    3. Specify output structure
    4. Include relevant examples

  produces: prompter_configuration
```

### Agentic Orchestration

The Puppeteer role—central logic managing multiple prompt sub-tasks.

```yaml
orchestration:
  controller: puppeteer_main

  agents:
    - name: researcher
      prompts: [search_prompt, analyze_prompt]
      triggers: [new_query, ambiguity_detected]

    - name: writer
      prompts: [draft_prompt, refine_prompt]
      triggers: [research_complete]

    - name: critic
      prompts: [evaluate_prompt, improve_prompt]
      triggers: [draft_complete]

  flow:
    - researcher.search → researcher.analyze
    - researcher.analyze → writer.draft
    - writer.draft → critic.evaluate
    - critic.evaluate → writer.refine | complete
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


<div align="center">

_Created for and by the prompty-prompter-pioneer-puppeteer riding "all the king's horses" and leading "all the king's men" through prompty prompts that are "Great" who prompter more prompts "Again & Again"._

**Draft it. Deliver it. Discover the frontier. Pull the strings.**

</div>

---

## Table of Contents

- [Philosophy](#-philosophy)
- [The P4 Lifecycle](#-the-p4-lifecycle)
- [Architecture](#-architecture)
- [Extensibility](#-extensibility)
- [Usage Patterns](#-usage-patterns)
- [Technical Concepts](#-technical-concepts)
- [Integration Guide](#-integration-guide)
