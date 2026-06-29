---
description: P4 pioneer stage — gate-check that a closure is dependency-closed and coherent
argument-hint: "<closure>"
arguments: [closure]
---

# /p4-pioneer

The **pioneer** stage of the P4 runtime pipeline — gate-check the closure.

Closure to validate: $closure

Run the validator — it checks the closure against the actual `metadata.p4` graph.
From the roboto plugin root (`${CLAUDE_PLUGIN_ROOT}` when installed, or `Ibiza/plugins/roboto/` in the source repo), run:

```sh
python scripts/p4.py check $closure       # this closure: valid? + issues
python scripts/p4.py validate             # every closure + the whole graph (exit 1 on failure)
```

The script verifies, mechanically:

1. **Closure** — every member's skill-level `depends_on` is present in the set. `depends_on` is two id-spaces: skill names resolve to `skills/<name>/`; P4 **gate** ids (`prompty | prompter | pioneer | puppeteer`) resolve to the fixed gate graph, not a skill.
2. **No dangling refs** — every `depends_on` / `optional_depends_on` skill name resolves to a real skill, and every `phases` entry is a valid gate id.
3. **Convention** — no skill re-lists the always-on base (`identity` / `rubric`) in `depends_on`.

Then judge the one thing the script cannot: whether the closure is **appropriate** for the `fires_when` it claims (a semantic call left to you).

**Output:** `valid` (true/false), `issues`, and any recommendations.
