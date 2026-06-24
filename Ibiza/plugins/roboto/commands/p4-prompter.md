---
description: P4 Prompter phase — select the dependency-closed skills and layers for a profile
argument-hint: "<profile>"
---

# /p4-prompter

You are in the **Prompter** (engineering) phase.

Profile to build: $ARGUMENTS

1. Read `docs/configurations.md` for the profile's `fragments` (P4 layers) and `extensions` (skills).
2. Read each skill's frontmatter `metadata.p4.depends_on` (`skills/*/SKILL.md`) and `docs/fragments.md`
   for the layer dependencies.
3. Expand to the full transitive closure. `depends_on` is required; `optional_depends_on` enhances
   but is not required for closure.

**Output:** the selected skills + P4 layers, `dependencies_satisfied` (true/false), and any
`missing_dependencies`.
