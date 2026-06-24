---
description: P4 Pioneer phase — validate that a skill/layer selection is dependency-closed and coherent
argument-hint: "<selection>"
---

# /p4-pioneer

You are in the **Pioneer** (research / validation) phase.

Selection to validate: $ARGUMENTS

Checks:

1. **Closure** — every selected item's `metadata.p4.depends_on` is satisfied by the selection. Note the two id-spaces: skill names resolve to `skills/<name>/`, while P4 **layer** ids (`prompty | prompter | pioneer | puppeteer`) resolve to `docs/fragments.md` sections — do not treat a layer id as a missing skill.
2. **No conflicts** — e.g. the Detection branch deliberately drops `vlds` + `templates`.
3. **Appropriate** for the stated use case.

**Output:** `valid` (true/false), `issues`, `recommendations`.
