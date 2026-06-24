---
description: P4 pioneer stage — gate-check that a closure is dependency-closed and coherent
argument-hint: "<closure>"
arguments: [closure]
---

# /p4-pioneer

The **pioneer** stage of the P4 runtime pipeline — gate-check the closure.

Closure to validate: $closure

Checks:

1. **Closure** — every member's `metadata.p4.depends_on` is satisfied by the set. Two id-spaces: skill names resolve to `skills/<name>/`, P4 **gate** ids (`prompty | prompter | pioneer | puppeteer`) resolve to the gate graph in `skills/rubric` — don't treat a gate id as a missing skill.
2. **No conflicts** — e.g. the `detection` closure deliberately drops `vlds` + `templates`.
3. **Appropriate** for the `fires_when` it claims.

**Output:** `valid` (true/false), `issues`, `recommendations`.
