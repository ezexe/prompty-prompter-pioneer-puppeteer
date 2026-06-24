# 🤝 Contributing

## ✍️ Markdown Authoring Format

These files use **semantic line breaks** so a one-word edit shows up as a one-line diff.

- **Prose:** one sentence per line; end the line at a sentence boundary, never hard-wrap mid-sentence at a fixed column.
- **Lists:** one line per item, kept whole — do not wrap or split a bullet across lines, even a long one.
- **Tables:** one line per row (Markdown requires it anyway).
- **Code / YAML fences:** never reflowed — their line breaks are content.
- **Italics:** use `_word_`, not `*word*` (keep `*` for bold `**…**` and list markers).

Let the editor soft-wrap long lines;
Markdown renderers ignore single newlines, so the rendered output is identical either way.
The plugins (under `Ibiza/plugins/<plugin>/`) and the templates (`Ibiza/templations/`) are kept in this style — match it when editing.

## 🔤 Naming conventions

- **Skill `name` (and its directory):** lowercase letters, digits, and hyphens only — `^[a-z0-9-]+$`, ≤64 chars — and it must **not** contain "claude" or "anthropic".
  The persona names _Claude / Claudio / Claudius / Roboto_ are fine in prose and in a `description`; just never in a skill `name`.
  This is why the three originally `snake_case` skills are `bias-patterns`, `isomorphic-operations`, and `sjc-indexer`.
- **Internal identifiers stay `snake_case`.** Hooks, capabilities, and operation/field ids (`web_search`, `anchor_selector`, `register_bias_patterns`, `bias_patterns_checked`, `sjc_indexer_protocol`) keep underscores — only a skill's _package name_ is hyphenated.

---

## 🧩 The `Ibiza/` framework + marketplace

`Ibiza/` is the P4 framework + **plugin marketplace** — the build target.
The framework (`Ibiza/templations/` + these docs) generates plugins, each living in its own subdirectory under `Ibiza/plugins/<name>/`; a (soon-to-start) `src/` builder will generate them.
The marketplace at `Ibiza/.claude-plugin/marketplace.json` lists them.
Inside a plugin, components are discovered **by convention** at the plugin root — there is no central registry to edit.

| Component        | Location (under `Ibiza/plugins/<name>/`) | Discovered as                      |
| ---------------- | ------------------------------- | ---------------------------------- |
| Plugin manifest  | `.claude-plugin/plugin.json`    | required; only `name` is mandatory |
| Skills           | `skills/<name>/SKILL.md`        | auto-triggered by `description`    |
| Subagents        | `agents/<name>.md`              | selected by the main thread        |
| Slash commands   | `commands/<name>.md`            | invoked as `/<plugin>:<name>`      |
| Connectors (MCP) | `.mcp.json` (`mcpServers`)      | MCP servers, local or remote       |
| Hooks            | `hooks/hooks.json`              | event handlers                     |

The marketplace index (`Ibiza/.claude-plugin/marketplace.json`, whose root is `Ibiza/`) lists each plugin with `source: "./plugins/<name>"`.
Only `plugin.json` lives _inside_ a plugin's `.claude-plugin/`; everything else sits at the plugin root.
Bundled components resolve paths with `${CLAUDE_PLUGIN_ROOT}`.

---

## 📦 Authoring a Skill

A skill is a `SKILL.md` file: YAML frontmatter the model always sees, then a body it loads when the skill triggers.
Start from [`Ibiza/templations/SKILL.md.template`](Ibiza/templations/SKILL.md.template).

```yaml
---
name: my-skill          # ^[a-z0-9-]+$, ≤64 chars, matches the directory, no "claude"/"anthropic"
description: What it does AND when Claude should use it — the auto-trigger hook. ≤1024 chars.
# optional: allowed-tools, license, version, disable-model-invocation
metadata:
  p4: { ... }           # the P4 model, preserved here (see below)
---

# My Skill
[body — keep under ~5k tokens; push depth into skills/my-skill/references/ which load lazily]
```

**Progressive disclosure** has three levels: the frontmatter (always loaded, ~tens of tokens), the body (loaded on trigger), and bundled `scripts/` / `references/` (loaded on demand).
Write the `description` to state both **what** the skill does and **when** to reach for it — a vague description either never fires or fires on everything.

### The P4 model lives under `metadata.p4`

The skill loader requires only `name` + `description`;
unknown `metadata` keys are tolerated and ignored.
So the entire P4 dependency/phase/hook model is preserved losslessly under a single `metadata.p4` object: `type`, `phases`, `depends_on` (+ `optional_depends_on`), `interface` (`domains` / `capabilities`), `hooks` (`on_prompty` / `on_prompter` / `on_pioneer` / `on_puppeteer`), and `tiers`.
The one-time mapping from the old bespoke `extension:` manifest is recorded in [`CHANGELOG.md`](CHANGELOG.md).

**Two id-spaces in `depends_on`.**
A `depends_on` entry is either a **skill name** (resolves to `skills/<name>/`) or a **P4 gate id** (`prompty | prompter | pioneer | puppeteer`, resolves to the gate graph in the plugin's [`skills/rubric`](Ibiza/plugins/roboto/skills/rubric/SKILL.md)).
For example `bias-patterns` depends on `[identity, prompter]` — `identity` is a skill, `prompter` is a gate.
A closure check must not treat a gate id as a missing skill.

### "Tools" fold into skills or MCP

There is no standalone "tool" packaging unit anymore.
A capability that used to be a P4 _tool_ becomes either:

- a **skill** that ships executable helpers under `skills/<name>/scripts/` (deterministic local helper), or
- an **MCP tool** exposed by a connector (external or stateful service).

Decision rule: deterministic and local → a script in a skill; external, networked, or stateful → an MCP server.

---

## 🔌 Connectors (MCP)

A "connector" _is_ an MCP server.
Configure connectors in `.mcp.json` at the plugin root; start from [`Ibiza/templations/mcp.json.template`](Ibiza/templations/mcp.json.template).

```json
{
  "mcpServers": {
    "example-stdio": { "type": "stdio", "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/example/index.js"] },
    "example-http":  { "type": "http",  "url": "https://api.example.com/mcp", "headers": { "Authorization": "Bearer ${TOKEN}" } }
  }
}
```

The one-time mapping from the old bespoke `connector:` manifest is recorded in [`CHANGELOG.md`](CHANGELOG.md).

**Never ship a live `.mcp.json` entry pointing at a server you have not implemented** — installing the plugin would try to spawn it.
The `roboto` plugin ships none;
[`Ibiza/plugins/roboto/.mcp.json.example`](Ibiza/plugins/roboto/.mcp.json.example) documents how to add one.

---

## 🧰 Other plugin components

- **`plugin.json`** ([`Ibiza/templations/plugin.json.template`](Ibiza/templations/plugin.json.template)) — only `name` is required. Omitting `version` on a git-distributed plugin means the commit SHA is the version (users update every commit); set it to gate updates to version bumps.
- **`marketplace.json`** ([`Ibiza/templations/marketplace.json.template`](Ibiza/templations/marketplace.json.template)) — at `Ibiza/.claude-plugin/`; lists each plugin with `source: "./plugins/<name>"` (one entry per plugin).
- **Subagents** (`agents/<name>.md`, [`Ibiza/templations/agent.md.template`](Ibiza/templations/agent.md.template)) — a subagent's body is _always_ loaded as its base prompt, so it is the right home for an always-on contract or persona. `agents/roboto.md` carries the four-lens contract as the always-on JIT driver (`identity` + `rubric` preloaded; other skills pulled on demand).
- **Slash commands** (`commands/<name>.md`, [`Ibiza/templations/command.md.template`](Ibiza/templations/command.md.template)) — manual-only prompts. The P4 runtime pipeline ships as `/p4-prompty`, `/p4-prompter`, `/p4-pioneer`, `/p4-puppeteer`.
- **Hooks** (`hooks/hooks.json`, [`Ibiza/templations/hooks.json.template`](Ibiza/templations/hooks.json.template)) — event handlers; optional, not shipped by default.

---

## 🤖 Compiling closures with the P4 pipeline

The P4 pipeline _is_ the runtime compiler — it runs per request, and it maps onto the real component pipeline:

```
prompty → prompter → pioneer → puppeteer
   ↑__________________________________|
```

| Stage         | What it does                                        | Command         |
| ------------- | --------------------------------------------------- | --------------- |
| **prompty**   | score the request → pick the closure                | `/p4-prompty`   |
| **prompter**  | resolve the dependency-closed skills + gates        | `/p4-prompter`  |
| **pioneer**   | gate-check the closure                               | `/p4-pioneer`   |
| **puppeteer** | register the closure — a `rubric` row + the members' `tiers` (no file) | `/p4-puppeteer` |

The output of `puppeteer` can feed a new `prompty` gate — the recursion applies to compiling closures too.
**Closures** (minimal → full) are named, dependency-closed _subsets_ of a plugin's skills that the `rubric` gate resolves into — defined by the skills' `metadata.p4.tiers` + the `rubric` rows, not a separate file; they are not separate installs.

---

## ♻️ Regeneration map

The framework is meant to be reconstructable, not frozen — its value is the regeneration rules, not the rendered text.
Every worked artifact regenerates from a template plus the design docs:

| Worked artifact                                   | Regenerate from                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------ |
| `Ibiza/plugins/<plugin>/skills/<name>/SKILL.md`            | `Ibiza/templations/SKILL.md.template` + the skill's `metadata.p4` deltas               |
| `Ibiza/plugins/<plugin>/.claude-plugin/plugin.json`        | `Ibiza/templations/plugin.json.template`                                               |
| `Ibiza/.claude-plugin/marketplace.json`           | `Ibiza/templations/marketplace.json.template`                                          |
| `Ibiza/plugins/<plugin>/.mcp.json`                          | `Ibiza/templations/mcp.json.template`                                                  |

Closures and the gate graph are not stored as files — they resolve at runtime from each skill's `metadata.p4` (`tiers` = closure membership, `phases` + `depends_on` = the gate graph) and the `rubric` gate. Nothing to regenerate, nothing to copy.

---

## 📋 Contribution checklists

**New skill**

- [ ] `Ibiza/plugins/<plugin>/skills/<name>/SKILL.md` with `name` (hyphenated, matches dir, no "claude"/"anthropic") + a WHAT-and-WHEN `description`
- [ ] `metadata.p4` carries `type`, `phases`, `depends_on` (+ `optional_depends_on`), `interface`, `hooks`, `tiers`
- [ ] every `depends_on` id resolves to a skill or a P4 gate
- [ ] body under ~5k tokens; depth pushed to `references/`; helpers (if any) in `scripts/`
- [ ] cross-references to sibling skills use the hyphenated names

**New / changed closure**

- [ ] a `rubric` row added/updated in `skills/rubric/SKILL.md` (firing signal → closure name + `fires_when`)
- [ ] the closure name added to each member skill's `metadata.p4.tiers`
- [ ] the member set (inverted from `tiers`) is dependency-closed — each member's `depends_on` resolves within it
- [ ] `identity` + `rubric` stay always-on (not listed as members)

---

## 🔗 Integration

- **Skills** carry domain knowledge / reasoning protocols and auto-trigger by `description`.
- **Subagents** override the system prompt with their own base context — use one for an always-on persona or contract.
- **Connectors (MCP)** bridge external systems; multi-model or data-source orchestration lands here.
- **Style / voice** integration is the Prompter-phase concern: an instance maps its persona/voice/transparency concerns to its own skills (the Roboto instance uses `identity` and `vlds`).
