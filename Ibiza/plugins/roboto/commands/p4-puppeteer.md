---
description: P4 Puppeteer phase — append a new configuration profile to docs/configurations.md
argument-hint: "<validated-selection> <use-case>"
---

# /p4-puppeteer

You are in the **Puppeteer** (orchestration) phase.

Validated selection + use case: $ARGUMENTS

Append a `##` profile section to `docs/configurations.md` containing:

1. A fenced YAML block: `name`, `fragments` (P4 layers), `extensions` (skill names), `use_case`.
2. **What This Provides** / **What This Does NOT Provide**.
3. **When To Use**.
4. **Response Format**.
5. **Upgrade / Downgrade Path** (links to sibling profiles).

Then add the new profile's name to each newly-included skill's frontmatter `metadata.p4.tiers`.
Keep the selection dependency-closed.
The output of this phase can feed a new Prompty seed — the lifecycle recurses.
