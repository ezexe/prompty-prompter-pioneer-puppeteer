---
name: rubric
description: The runtime engagement gate — scores the request and resolves which dependency-closed closure to compile just-in-time, from the bare identity contract up to the full apparatus, then discloses the chosen depth. Run first, before reasoning, so the driver pulls only the skills the request actually needs.
when_to_use: "Trigger at the very start of every request to pick engagement depth — 'is this trivial or high-stakes', whether to pull vlds / bias-patterns / templates, which closure to compile just-in-time."
metadata:
  p4:
    type: skill
    phases: [prompty, prompter, pioneer, puppeteer]
    depends_on: []
    optional_depends_on: []
    interface:
      domains: [engagement_selection, dependency_gating, jit_compilation]
      capabilities: [request_scoring, closure_selection, depth_disclosure]
    hooks:
      on_prompty: [score_request]
      on_prompter: [resolve_closure]
      on_pioneer: [gatecheck_closure]
      on_puppeteer: [compile_context]
    tiers: [minimal, standard, verification, detection, full]
---

# Rubric Skill — the just-in-time engagement gate

> The gate the driver runs **first**, before reasoning.
> It reads the request, scores it, and resolves which dependency-closed closure to compile just-in-time — from the bare `identity` contract up to the full apparatus.
> `identity` and this gate are never gated off; everything above is pulled only when its signal fires.

## The gate

Engage the highest row whose signal fires, then compile that closure (it includes every lower layer it depends on).
When nothing above row 0 fires, stay at `identity`.

| # | Signal in the request                       | Marginal capability it adds                            | Closure        |
| - | ------------------------------------------- | ------------------------------------------------------ | -------------- |
| 0 | Trivial / conversational                    | — (contract only)                                      | `minimal`      |
| 1 | Wants a real, shaped answer                 | `templates` (formatting)                               | `standard`     |
| 2 | Load-bearing factual / technical claims     | `vlds` (decision gate)                                 | `verification` |
| 3 | Loaded / polluted / under-specified framing | `bias-patterns` (pre-response scan)                    | `detection`    |
| 4 | Research, **exploration** (enumerate / map out / deep-dive), consequential, or contested | `isomorphic-operations`, `sjc-indexer` + orchestration | `full`         |

The four signals are the same questions the `prompty` stage asks — applied here as a runtime test rather than a build-time menu.

## Gate graph (fixed)

The four P4 gates and their chain — the one structure not declared on a skill:

- `prompty` depends_on `[identity]`
- `prompter` depends_on `[identity, prompty]`
- `pioneer` depends_on `[identity, prompty, prompter]`
- `puppeteer` depends_on `[identity, prompty, prompter, pioneer]`

A skill hooks gates via its `metadata.p4.phases`; resolving a gate resolves its chain, and the active gates for a request are the union of the loaded skills' `phases`.

## Resolution rules

- **Just-in-time** — pull a skill only when its row fires; never preload the whole set.
- **Closed** — pulling a skill pulls its `metadata.p4.depends_on`; a closure's member set = the skills whose `metadata.p4.tiers` lists it (`identity` + `rubric` always-on). This gate _selects_ the closure; the skills declare their own membership.
- **Branches** — `verification` (`vlds`) and `detection` (`bias-patterns`) are parallel branches above `standard`; `full` unions them.
- **Default down** — a lower closure is a declared choice, not a violation.

Row 4's **exploration** signal (enumerate / map out / deep-dive / "what do you know about") is what fires `sjc-indexer` — the runtime exploration check — so a deep-exploration ask reaches the indexer instead of getting a single-pass answer.

## Cross-cutting pulls

Two skills are **not** depth rows — they attach to any closure when their own signal fires, orthogonal to the ladder above:

- **`activation`** — pulled whenever the request will cause a side effect (a tool call, a file or memory write, a search or fetch). It is the confirm-before-acting gate and carries the SAFE / STANDARD / FULL / DEBUG **mode dial**. Mode is orthogonal to closure: a `minimal` closure can still run in SAFE mode.
- **`persistence`** — pulled when a durable preference, a repeated correction, or a reusable finding surfaces (signals like "always / never", "remember this", or a correction seen 2+ times). It proposes a save to the VLDS `localStorage` tier.

Both also auto-trigger by their own `description` / `when_to_use` like every skill; listing them here records that they **compose with** the depth ladder rather than sitting inside it.

## Disclosure

State the resolved closure in the response — which row fired and why — so engagement depth is auditable like every other influence.
