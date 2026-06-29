---
description: P4 puppeteer stage — register a new closure (a rubric row + the members' tiers)
argument-hint: "<closure> <fires-when>"
arguments: [closure, fires_when]
---

# /p4-puppeteer

The **puppeteer** stage of the P4 runtime pipeline — compile and emit a new closure.

This is the **sync point**: where the **puppet↔puppeteer bridges** meet over the shared-mem `memory` (the physical store) and reconcile it against VLDS (the virtual space) — SYNTHESIZE commits the coherent, synced result as the closure.

Closure + fires-when: $closure / $fires_when

Register the closure — there is no separate file; a closure _is_ its members' `tiers` plus a `rubric` row:

1. Add a row to the `rubric` gate (`skills/rubric/SKILL.md`): the firing signal → the closure name + `fires_when`.
2. Add the closure name to each member skill's `metadata.p4.tiers`.

Keep the closure dependency-closed — each member's `depends_on` resolves within it.
Confirm it with the validator (from the roboto plugin root): `python scripts/p4.py validate` (or `check <closure>`) — it fails if the new closure is not dependency-closed, has a dangling ref, or re-lists the always-on base.
The output of this stage can feed a new `prompty` gate — the loop recurses.
