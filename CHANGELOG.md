# Changelog

All notable changes to this repo are recorded here. theres no version numbers because this is a project that from its conception is designed to indefinitely be [Unreleased] at version [0.0.🙃]

## Initial

The **P4** meta-prompting framework and its first worked plugin, `roboto` — "The Init Elegance."

### Framework

- **`Ibiza/`** is the framework + plugin marketplace: `Ibiza/.claude-plugin/marketplace.json`, the `Ibiza/templations/` authoring kit, and plugins under `Ibiza/plugins/<name>/`. A `src/` builder generates plugins into `Ibiza/plugins/`.
- **Runtime model** — every file under a plugin is a runtime logic node resolved per request against its `metadata.p4.depends_on` graph. The four P4 gates (`prompty` / `prompter` / `pioneer` / `puppeteer`) form a fixed chain, and each skill declares its gate hooks via `metadata.p4.phases`.
- **Closures, derived not stored** — a closure's members are the skills whose `metadata.p4.tiers` lists it, resolved at runtime by the `rubric` gate (which holds the `fires_when` signal→closure rows).
- **Naming** — `Ibiza` (capital `I`) and `templations` (kept distinct from the `templates` skill).

### `roboto` plugin — the four-lens reasoning instance

- **Nine skills** — `identity`, `rubric`, `vlds`, `templates`, `bias-patterns`, `isomorphic-operations`, `sjc-indexer`, `activation`, `persistence`.
- **JIT driver** — `agents/roboto.md` always loads the `identity` contract + `rubric` gate, and pulls the remaining skills on demand via the `Skill` tool.
- **Runtime pipeline commands** — `/p4-prompty` (score → pick), `/p4-prompter` (resolve), `/p4-pioneer` (gate-check), `/p4-puppeteer` (compile + emit a closure).
- **Four lenses** — `identity` answers each request through Claude / Claudio / Claudius / Roboto under a strict response contract (Influence Disclosure block, four named perspective sections, deviation clause).
- **Memory model** — roboto is modeled as a computer with two memory faces: **VLDS** is the virtual address space of _claims_; the agent's `memory: project` field is the physical store; **verification** is the MMU-style check between them (PROCEED = mapped, VERIFY_FIRST = page fault, QUALIFY = unbackable).
- **Safety posture** — `activation` is the confirm-before-acting gate: the SAFE / STANDARD / FULL / DEBUG mode dial plus the activation cycle (RECEIVE → SCAN → INTERRUPT → CONFIRM → ACTIVATE → COMPILE → POST-PROCESS). The default posture is SAFE.
- **Cross-session learning** — `persistence` proposes durable saves under a `[namespace]:[category]:[identifier]` key schema, writing to the VLDS `localStorage` tier on confirmation.

Open: `plugin.json` carries `name: "mister"` (should be `roboto`).
