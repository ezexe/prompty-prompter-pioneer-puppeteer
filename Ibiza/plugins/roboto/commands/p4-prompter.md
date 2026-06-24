---
description: P4 prompter stage — resolve the dependency-closed skills and gates for a closure
argument-hint: "<closure>"
arguments: [closure]
---

# /p4-prompter

The **prompter** stage of the P4 runtime pipeline — resolve the closure.

Closure to resolve: $closure

1. Resolve the closure's members — the skills whose `metadata.p4.tiers` lists it (`skills/*/SKILL.md`); `identity` + `rubric` are always-on.
2. Read each member's `metadata.p4.depends_on` and the gate graph in `skills/rubric` for the gate dependencies.
3. Expand to the full transitive closure. `depends_on` is required; `optional_depends_on` enhances but is not required for closure.

**Output:** the resolved skills + P4 gates, `dependencies_satisfied` (true/false), and any `missing_dependencies`.
