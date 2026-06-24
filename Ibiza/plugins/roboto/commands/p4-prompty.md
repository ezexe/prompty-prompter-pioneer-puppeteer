---
description: P4 Prompty phase — identify which configuration profile a request needs
argument-hint: "<requirements>"
---

# /p4-prompty

You are in the **Prompty** (ideation) phase of the P4 build lifecycle.

User requirements: $ARGUMENTS

Identify which configuration profile fits, using `docs/configurations.md` as the ladder:

- **minimal** — the base four-lens identity only
- **standard** — identity + the ideation seed + response templates
- **verification** — adds VLDS claim-checking
- **detection** — adds bias-pattern scanning (parallel branch; drops vlds + templates)
- **full** — everything; both branches unioned + the orchestration lifecycle

Decide by asking:

1. Need audit-formatted output? -> standard or higher
2. Need claim verification? -> verification or higher
3. Need bias / error detection? -> detection or higher
4. Research or high-stakes? -> full

**Output:** the chosen profile name + one line of reasoning.
