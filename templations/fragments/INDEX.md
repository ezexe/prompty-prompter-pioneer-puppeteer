# Fragments — Base Templates

This directory holds the **untargeted, generic** P4 fragment templates. A _fragment_
is a composable building block of a prompt-engineering instance; fragments are
assembled into named **configurations** (see `../configurations.md`). These root
templates are identity-agnostic — fill them to produce a concrete instance.

**Worked example instance:** `.ai/roboto/` (the "Roboto" / "The Intelligence"
identity) is a complete, filled instance. Read its `fragments/INDEX.md` for a real
fragment map, dependency graph, and configuration composition.

---

## The P4 Layers

A fragment declares which lifecycle layer it serves:

| Layer         | Role        | Question it answers          |
| ------------- | ----------- | ---------------------------- |
| **Prompty**   | ideation    | what are we building?        |
| **Prompter**  | engineering | how do we structure it?      |
| **Pioneer**   | research    | what experiments can we run? |
| **Puppeteer** | automation  | how do we orchestrate it?    |

A `core` layer holds the base identity that every other fragment depends on.

---

## Authoring a Fragment

1. Copy `_TEMPLATE.md` to `NN_NAME.md` (the numeric prefix orders the reading sequence).
2. Fill the frontmatter — especially `depends_on`.
3. Write the substantive content; keep it self-contained.
4. Register it in your instance's `fragments/INDEX.md`.

---

## Dependency Graph (template)

Every fragment lists `depends_on` in its frontmatter; the instance INDEX renders the
full graph. Generic form:

```
00_BASE (core identity, required: true)
   ├── 01_... (depends: 00_BASE)
   ├── 02_... (depends: 00_BASE, 01_...)
   └── ...    (depends: ...)
```

**Rule:** a configuration must include every fragment in the transitive closure of
its members' `depends_on`. A fragment may also list `optional_depends_on` — those
enhance it but are not required for closure (omitting one just disables the feature
it powers). Validate before shipping (see `../../CONTRIBUTING.md`).

---

## Configuration Composition (template)

Configurations bundle fragments by capability tier. The concrete map for a given
instance lives in that instance's `fragments/INDEX.md`. Generic form:

```
[level]: [fragment_id, ...]
```

See `.ai/roboto/fragments/INDEX.md` → "Configuration Composition" for a filled map.

---

## Files Here

| File           | Purpose                                            |
| -------------- | -------------------------------------------------- |
| `INDEX.md`     | This file — the fragment pattern + templates guide |
| `_TEMPLATE.md` | Skeleton for a single fragment                     |
