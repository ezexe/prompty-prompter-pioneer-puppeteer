# emission-discipline — prose may hedge, fences execute

A standalone plugin holding one framework: **Emission Discipline**, the _what-may-be-released_ gate that decides what is licensed to cross into a code fence — and therefore into the user's systems — while it is being generated.

Its doctrine lives in [`skills/discipline`](skills/discipline/SKILL.md) — the provenance header, the core model (consequence asymmetry, the fence as a jurisdiction change, knowledge–emission divergence, defect classes A–G, the mandate), the 15 rules in four groups, the resident trigger table, the one-sentence forms, a proposed mapping onto the P4 gates, the residency map, and the live case study the whole thing was derived from.
It ships a second skill, [`skills/p4-emission-discipline`](skills/p4-emission-discipline/SKILL.md) — the **resident-gate wrapper**: the trigger table plus a pointer back to the doctrine, packaged for installation outside this repo.
The [`residency/`](residency/) directory carries the claude.ai deployment block.

## Where it sits

It is the sibling of [`verification-discipline`](../verification-discipline), deliberately never merged with it:

- **verification-discipline** gates what the model _believes_ — when a stale-or-wrong prior must be re-checked before it drives an action (claim admission, half-life classes, assertion-indexed gating).
- **emission-discipline** gates what the model _releases_ — what is licensed to cross into a code fence, form (rules 1–12) and license (rules 13–15) both.

The parent split — epistemic vs consequential actions, drawn in [verification-discipline's core model](../verification-discipline/skills/discipline/SKILL.md#epistemic-vs-consequential-actions) — is the boundary between the two docs, and the code fence is where jurisdiction changes.
Verification-discipline closes the gap between world and belief; emission-discipline closes the gap between belief and release.

Like its sibling it is standalone (no `metadata.p4`), so its **stage mapping is a prose cross-reference** to the four P4 gates defined in [`roboto`](../roboto) (`prompty → prompter → pioneer → puppeteer`), not a machine-checked `phases` binding.

## Why the skill is not the primary vehicle

Verification-discipline is doctrine consulted at research time; emission-discipline's rules are trigger-phrased to fire _mid-generation_, so the gate must be resident while code is being produced.
As of Claude Code circa 2026-07 (Class-1 claims by verification-discipline's Rule 1 — verify against your version): skill residency is per-runtime, and skill triggering keys on task formality — which this framework's own Rule 12 forbids as a gate input, so a skill cannot be the primary vehicle for its own payload.
**Always-resident text is primary; skills are secondary everywhere.**
The full residency map — which surface is primary and which is secondary, per runtime — is recorded in the [doctrine doc](skills/discipline/SKILL.md#residency-map--how-the-gate-stays-resident), and the deployables are versioned here:

- the wrapper skill, [`skills/p4-emission-discipline/SKILL.md`](skills/p4-emission-discipline/SKILL.md) — copy the directory to `~/.claude/skills/p4-emission-discipline/` for user-level Claude Code residency, or install it as a claude.ai profile skill;
- the userStyle block, [`residency/claude-ai-userstyle.md`](residency/claude-ai-userstyle.md) — paste into a claude.ai userStyle for the always-resident primary in that runtime;
- the Claude Code primary is the trigger table itself — paste the doctrine doc's [trigger table](skills/discipline/SKILL.md#trigger-table-working-context-form) into `~/.claude/CLAUDE.md` as a standing block.

## The framework obeys itself

Per its sibling's Rule 1, the skill opens with a provenance header carrying its stamp and expiry:

- **Derived** 2026-07-16, from the live host-election review in the skill's Appendix A — every defect's correction was producible on demand one turn later, which is the phenomenon (knowledge–emission divergence) the framework targets.
- **Amended same session:** rules 13–15 (the mandate cluster) and defect Class G, added after the freshly written rules 1–12 failed to catch a live scope breach (Appendix A-7) — doctrine falsified and patched by its own transcript evidence.
- **Review triggers:** Claude Code changes skill loading or triggering semantics (voids the residency map); six months elapse from the derived date; or any rule fires incorrectly in practice.

## Install

Load it with `claude --plugin-dir ./Ibiza/plugins/emission-discipline` (repeat the flag for other plugins).
As of Claude Code circa 2026-07, `--plugin-dir` loads the plugin live from disk each session, so there is no separate install or update step — but by the sibling framework's Rule 1 that is a Class-1 (version-indexed) claim about the loader's default behavior, stamped here rather than asserted as timeless: if a later Claude Code major changes plugin loading, verify against your version.
The doctrine skill is **direct-invoke only** (`disable-model-invocation: true`, matching verification-discipline) — reach it with `/emission-discipline:discipline`, optionally passing an emission to test against the discipline.
The wrapper skill is deliberately **model-invocable** — being consulted before fences is its entire job — but per the residency map it undertriggers on casual turns, which is exactly why it is the secondary vehicle in every runtime.

## Wording deltas from the canonical payload

The 15 rule statements, the core-model prose, the defect-class table, the trigger table, the one-sentence forms, and Appendix A are reproduced **verbatim** from the source framework; markdown formatting (bold paragraph leads promoted to headings, one-sentence-per-line prose, underscore italics per the house style, rules kept one-per-line) is not a wording change.
Everything the plugin _added_ around or changed in that canonical text is logged here:

- **Provenance header** — added (mandated by the integration brief); its facts are transcribed from the brief's provenance notice, with the "authored without repo access" hypothesis resolved: the stage mapping is derived from this repo's gate definitions, as the brief required.
- **Skill intro blockquote** — added framing: positions the skill as the consequential-side twin of verification-discipline. Drawn from the brief's provenance notice; no rule semantics touched.
- **"The only tool-behavior claims…" line** — added, to satisfy verification-discipline Rule 1's self-application (declares that the only tool claims present are the two stamped residency facts).
- **Group headings over the rules** ("Rules 1–7 — mid-stream", etc.) — added for navigation; the canonical grouping sentence they are derived from is reproduced verbatim above them.
- **Trigger-table heading and lead-in** — the payload's parenthetical "this is what the live skill carries" was moved out of the heading into an added lead-in sentence pointing at the wrapper skill. Table contents verbatim.
- **Stage mapping** — added in full: this section is a proposal, not part of the canonical payload. P4 gate semantics are derived from the roboto plugin's command docs, not from the source brief's hypotheses.
- **Residency map** — recorded from the brief's Phase 2 (mandated); the two Claude Code behavior claims it rests on were **unstamped in the brief** and are stamped here (circa 2026-07, Class 1) — a deliberate semantic addition, made so the framework obeys its sibling's Rule 1.
- **Appendix A** — reproduced from the payload; layout is one sentence per line, and one typo was corrected ("the only possible deciphere" → "the only possible decipherer"). No other wording changed.
- **Cross-reference links** (verification-discipline sections, roboto commands, the wrapper, the residency file) — added for navigation.
- **Wrapper skill** — installed as supplied by the brief with **one correction**: its closing pointer read "defect classes (A–F)" while the doctrine it points to defines classes A–G; the count was a fossil from before the same-session Class G amendment, and shipping it knowingly would violate the framework's own Rules 4 and 5. One token changed: `(A–F)` → `(A–G)`. Nothing else in the wrapper was touched — including its `p4-`prefixed sibling names, which are the framework's portable names rather than this repo's directory names.
- **claude.ai userStyle block** — versioned verbatim inside a fence at [`residency/claude-ai-userstyle.md`](residency/claude-ai-userstyle.md); only the file's preamble (what it is, where to paste it) is added.
- **Reciprocal cross-reference** — one line added to [verification-discipline's SKILL.md](../verification-discipline/skills/discipline/SKILL.md#epistemic-vs-consequential-actions) pointing here for the release-side rules, and logged in that plugin's own delta log.

No rule's _wording_ was changed.
No claim's _semantics_ were altered, except the two residency stamps and the wrapper's class-count correction noted above.
