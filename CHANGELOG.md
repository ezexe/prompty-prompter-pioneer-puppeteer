# Changelog

All notable changes to this repo are recorded here. theres no version numbers because this is a project that from its conception is designed to indefinitely be [Unreleased] at version [0.0.🙃]

## Physical/virtual memory duality

Building on the runtime reframe, the `roboto` instance's memory architecture is made explicit as a single virtual/physical duality threaded through the plugin — roboto is modeled as a computer, and this names its two memory faces.

- **VLDS = the virtual space** — `skills/vlds` is reframed as the instance's virtual address space of _claims_ (what is claimed/known); a new "Virtual space and physical memory" section names the duality, and the storage tiers are marked unbacked (`Virtual`) vs. physical-backed (`localStorage` / `DataStore`).
- **`memory` = the physical space** — the `roboto` agent's `memory: project` field is disclosed first-class as the shared-memory ring the **puppet↔puppeteer bridges** sync through (the per-OS map API, `mmap` / `MapViewOfFile`) — kept and highlighted, not a hidden channel.
- **Verification = the physical↔virtual check** — the VLDS decision gate is recast as the instance's MMU: **PROCEED** = the virtual claim maps to a resident physical page; **VERIFY_FIRST** = a page fault (fault it in / verify); **QUALIFY** = an unbackable page (stays virtual, asserted only as qualified). SYNTHESIZE reconciles physical (what synced) against virtual (what VLDS claims).
- **Disclosure pairs the two faces** — `identity`'s Influence Disclosure block frames its `Memory:` line as the physical-memory channel, surfaced opposite VLDS's virtual provenance.
- **Puppeteer = the sync point** — `/p4-puppeteer` is reframed as where the bridges reconcile physical `memory` against virtual VLDS and commit the synced closure.

## Runtime reframe: gates, closures, and the JIT rubric

The `roboto` plugin was reframed from a build-time catalog into a pure **runtime, just-in-time context compiler**. Nothing in `Ibiza/plugins/roboto/` is build-time: every file is a runtime logic node resolved per request against the `metadata.p4.depends_on` graph.

- **Layers → gates, then dissolved** — the four P4 gates (`prompty` / `prompter` / `pioneer` / `puppeteer`) are no longer a `docs/` file; the fixed gate chain lives in `skills/rubric` and each skill declares its own gate hooks via `metadata.p4.phases`.
- **Profiles → closures, derived not stored** — there is no `docs/configurations.md`; a closure's members = the skills whose `metadata.p4.tiers` lists it, resolved at runtime by the `rubric` gate (which holds the `fires_when` signal→closure rows).
- **New `rubric` skill** — `skills/rubric/SKILL.md` is the always-on **engagement gate**: it scores the request and selects which closure to compile just-in-time.
- **`roboto` is a JIT driver** — preloads only `identity` + `rubric`; pulls the other skills on demand via the `Skill` tool instead of eagerly bundling all six.
- **Commands are runtime pipeline stages** — `/p4-prompty` (score → pick), `/p4-prompter` (resolve), `/p4-pioneer` (gate-check), `/p4-puppeteer` (compile + emit a closure); reframed from "build lifecycle."
- **Newer Claude-standard frontmatter adopted** — `when_to_use` on every skill; named `arguments` on the commands; `tools` / `model` / `effort` / `skills` / `memory` on the `roboto` agent.
- **`docs/` deleted** — `docs/fragments.md`, `docs/configurations.md`, and the now-dead `templations/fragments.md.template` + `configurations.md.template` were removed; the gate graph + closures derive at runtime from `metadata.p4` + `rubric`.

## Migration to the Claude Skills / Plugins / Connectors standard

The framework's bespoke `extension:` packaging model — a fenced-YAML manifest at the top of each skill/tool/connector `README.md` — was migrated to the current Claude **Agent Skills / Plugins / MCP** standard, and the repo was reorganized into the `Ibiza/` framework + marketplace.
`roboto` is the first worked plugin, at `Ibiza/plugins/roboto/`.

### Skills: `extension:` manifest → `SKILL.md` frontmatter

Each skill's `README.md` became `skills/<name>/SKILL.md` with `name` + `description` frontmatter; the bespoke `extension:` fields moved under a tolerated `metadata.p4` object (the loader ignores unknown `metadata` keys, so the P4 model survives losslessly inside a standards-valid file).

| Old `extension:` field                   | New home in `SKILL.md`                         |
| ---------------------------------------- | ---------------------------------------------- |
| `name`                                   | frontmatter `name` (now hyphenated)            |
| `type`                                   | `metadata.p4.type`                             |
| `compatibility.p4_phases`                | `metadata.p4.phases`                           |
| `compatibility.depends_on`               | `metadata.p4.depends_on`                       |
| `compatibility.optional_depends_on`      | `metadata.p4.optional_depends_on`              |
| `interface.skill.{domains,capabilities}` | `metadata.p4.interface.{domains,capabilities}` |
| `hooks.on_*`                             | `metadata.p4.hooks.on_*`                       |
| _(new)_ which profiles ship it           | `metadata.p4.tiers`                            |
| _(new)_ human-readable trigger summary   | the frontmatter `description`                  |

### Connectors: `connector:` manifest → `.mcp.json`

A "connector" is now an MCP server, configured in `.mcp.json`.
The bespoke `connector:` manifest maps onto the standard:

| Old `connector:` field                   | New home in `.mcp.json`                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| `protocol: rest \| graphql \| websocket` | spoken _by_ the server; the Claude-side `type` is `stdio \| http \| sse` |
| `protocol: mcp`                          | native — this file                                                       |
| `endpoints[].path` / `method`            | `url` (remote) or `command` + `args` (local)                             |
| `auth.type` / `auth.env_var`             | `headers` / `env`, with `${VAR}` and `${VAR:-default}` expansion         |

### Other changes

- **"Tools" dropped as a packaging unit** — a capability is now either a skill with bundled `scripts/` or an MCP tool; the `extensions/tools/_TEMPLATE` was removed.
- **Skill names hyphenated** to satisfy `^[a-z0-9-]+$`: `bias_patterns` → `bias-patterns`, `isomorphic_operations` → `isomorphic-operations`, `sjc_indexer` → `sjc-indexer`. Internal ids (hooks, ops, fields) stay `snake_case`.
- **Always-on identity** — added an `agents/roboto.md` subagent that always loads the four-lens contract (skills only load on trigger).
- **Tiers → profiles** — the capability ladder (Minimal … Full) became documented usage profiles over one plugin's skills, recorded per-skill in `metadata.p4.tiers`.
- **Repo reorganized** — `Ibiza/` is the framework + marketplace (`Ibiza/.claude-plugin/marketplace.json`, the `Ibiza/templations/` authoring kit, plugins under `Ibiza/plugins/<name>/`). A future `src/` builder will generate plugins into `Ibiza/plugins/`.
- **Naming quirks** — `Ibiza` (capital `I`, reads "Ibiza"; _not_ lowercase-l `lbiza`) and `templations` (not `templates`, to avoid clashing with the `templates` skill).
