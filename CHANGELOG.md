# Changelog

All notable changes to this repo are recorded here.

## [0.1.0] — 2026-06-24 — Migration to the Claude Skills / Plugins / Connectors standard

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

A "connector" is now an MCP server, configured in `.mcp.json`. The bespoke `connector:` manifest maps onto the standard:

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
