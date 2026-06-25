<div align="center">

# 🎭 Prompty Prompter Pioneer Puppeteer

[![pattern](https://img.shields.io/badge/pattern-recursive_prompt_engineering-6E56CF?style=flat-square)](#-architecture)
[![lifecycle](https://img.shields.io/badge/lifecycle-prompty→prompter→pioneer→puppeteer-4C9AFF?style=flat-square)](#-lifecycle)
[![concepts](https://img.shields.io/badge/concepts-chaining_·_meta_·_orchestration-1FAD66?style=flat-square)](#-concepts)

_prompts that build prompts to prompter prompts into pioneer prompts that puppeteer prompts — that will fork into branches of more forks and branches that prompt prompts as prompt puppets to pioneer prompts into prompt puppets that prompter prompt puppets into prompty prompt prompter pioneer prompt puppeteers — that puppeteer more prompts like this endlessly, until each branch puppeteer pioneers its prompt puppet to prompt a response that prompters a reply for the branch puppeteer prompt it got forked from_

</div>

## 🏗️ Architecture

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

## 🔄 Lifecycle

### Linear Progression

Standard lifecycle for developing a prompt from concept to automation.

```
prompty → prompter → pioneer → puppeteer
```

### Recursive Refinement

The output of orchestration feeds new seeds.

```
puppeteer → prompty → prompter → pioneer → puppeteer
    ↑                                          │
    └──────────────────────────────────────────┘
```

### Parallel Exploration

Multiple pioneer experiments from a single prompter; the best results get orchestrated.

```
                    ┌─ pioneer_a ─┐
prompty → prompter ─┼─ pioneer_b ─┼─ puppeteer
                    └─ pioneer_c ─┘
```

### Meta-Prompting

Puppeteers orchestrating puppeteers for emergent prompt evolution.

```
puppeteer_a ──┐
puppeteer_b ──┼── meta_puppeteer ── prompty (new generation)
puppeteer_c ──┘
```

---

## 🧩 Concepts

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

The Puppeteer role — central logic managing multiple prompt sub-tasks.

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

## 📂 Layout

This repo is a **meta-prompting P4 framework**.
`Ibiza/` is the framework + plugin marketplace — the build **target**; a `src/` builder generates plugins that follow the framework into `Ibiza/plugins/<name>/`.
`roboto` is the first worked plugin.

| Path                                    | What it is                                                                                                            |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `src/`                                  | the builder that generates plugins into `Ibiza/plugins/`                                                   |
| `Ibiza/.claude-plugin/marketplace.json` | The marketplace (its root is `Ibiza/`) — lists every plugin under `Ibiza/plugins/`                                    |
| `Ibiza/templations/`                    | The blank P4 authoring kit — `SKILL.md.template`, `plugin.json.template`, `mcp.json.template`, `agent.md.template`, … |
| `Ibiza/plugins/<name>/`                 | One generated plugin per subdirectory (`Ibiza/plugins/roboto/` is the first)                                          |
| `README.md` · `CONTRIBUTING.md`         | Repo overview and the Skills / Plugins / Connectors authoring spec                                                    |

Each plugin under `Ibiza/plugins/` is a standard plugin tree — components are discovered by convention at _its_ root:

| Path (under `Ibiza/plugins/roboto/`) | What it is                                                                                                                                                 |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/plugin.json`         | The plugin manifest                                                                                                                                        |
| `skills/`                            | The seven Roboto reasoning skills as `SKILL.md` files — `identity`, `rubric`, `vlds`, `templates`, `bias-patterns`, `isomorphic-operations`, `sjc-indexer` |
| `agents/roboto.md`                   | The JIT reasoning driver — always-on `identity` contract + `rubric` gate; pulls the other skills on demand                                                 |
| `commands/`                          | The P4 runtime pipeline as slash commands (`/p4-prompty`, `/p4-prompter`, …)                                                                               |
| `.mcp.json.example`                  | How to add an MCP **connector** (this plugin ships none by default)                                                                                        |

---

## 🚀 Install

The marketplace lives at `Ibiza/` (the directory holding `.claude-plugin/`).
Add it by local path, then install a plugin:

```
/plugin marketplace add ./Ibiza
/plugin install roboto@p4-marketplace
```

(A GitHub `owner/repo` add looks for `.claude-plugin/` at the repo root; this marketplace is rooted at `Ibiza/`, matching the local `src/ → Ibiza/` build flow.)

Roboto's seven skills auto-trigger by their `description`s; for the full four-lens treatment on _every_ reply, run the `roboto` subagent.
Compile a custom closure with the `/p4-*` commands — the `rubric` gate (`Ibiza/plugins/roboto/skills/rubric/SKILL.md`) and each skill's `metadata.p4` define them.

<div align="center">

_"Puppeteer: the final frontier_

</div>