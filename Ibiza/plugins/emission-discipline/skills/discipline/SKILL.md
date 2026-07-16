---
name: discipline
description: "Emission Discipline (prose-may-hedge-fences-execute) — a 15-rule framework for WHAT may be RELEASED into a code fence, gating emission on what is about to be released, never on how casual the request was. Models the experienced integration defect as (correct form available in-model) × (release layer that never checks the emission against it) — knowledge–emission divergence — and classifies defects by transmission vector: phantom references, fossils, endorsed rejects, unlanded fixes, rhetorical laundering, label drift, scope breaches. Rules fire mid-stream (at fence-open), at turn boundaries (on document arrival), as standing release conditions, and as a mandate cluster gating license rather than form: what the user pastes is the territory, what they withhold is a wall. Use when emitting code, configs, commands, or log strings a user will integrate, when a user document returns prior emissions, or to test an emission against the discipline."
argument-hint: "[emission, snippet, or turn to test against the discipline]"
disable-model-invocation: true
---

# Emission Discipline — prose may hedge, fences execute

> Prose may hedge; fences execute.
> This skill is the discipline of what may be _released_ into a code fence — the boundary where content converts from a thought offered into an action taken on the user's behalf — and it holds that the correction the model can produce on demand is owed at emission, not at retraction.
> It is the consequential-side twin of [`verification-discipline`](../../../verification-discipline/skills/discipline/SKILL.md): that framework gates what the model _believes_ (claim admission, half-life classes, assertion-indexed gating); this one gates what the model _releases_ (artifacts crossing into user-owned systems).
> They are siblings, cross-referenced, never merged — the parent split between epistemic and consequential actions is the boundary between the two docs, and the code fence is where jurisdiction changes.

## Provenance (this framework obeys itself)

- **Derived:** 2026-07-16, from a live multi-turn code review of a C++ `HostLink` class (Win32 named-pipe host election: spawn/elect/handoff/handshake) in which the reviewing model emitted defects against its own demonstrable in-context knowledge — every correction was producible on demand one turn later, which is exactly the phenomenon this framework targets ([Appendix A](#appendix-a--case-study-source-session-2026-07-16)).
- **Amended same session:** rules 13–15 (the mandate cluster) and defect Class G, added after the freshly written rules 1–12 failed to catch a live scope breach ([A-7](#appendix-a--case-study-source-session-2026-07-16)).
- **Authored without access to this repo:** every assumption the source brief made about structure, naming, or stage semantics was hypothesis, not fact; the [stage mapping](#stage-mapping--the-rules-against-the-p4-gates) below is derived from this repo's own gate definitions, not from the brief's guesses.
- **Review triggers (any one fires a re-read):** Claude Code changes skill loading or triggering semantics (this voids the [residency map](#residency-map--how-the-gate-stays-resident)); six months elapse from the derived date; or any rule fires incorrectly in practice.

The only tool-behavior claims in this document are the two Claude Code residency facts in the [residency map](#residency-map--how-the-gate-stays-resident), stamped there (Claude Code circa 2026-07); no other unstamped tool claim is added.

## Core model

### The consequence asymmetry

The user integrates emitted artifacts into systems where _they_ bear the failure cost; the model bears none.
Fluency pressure optimizes the stream for reading well _now_; integration executes it _later_, verbatim, stripped of every hedge that surrounded it.
An emission's blast radius is therefore evaluated at paste-time, not generation-time — and prose does not survive the paste.
Only fences do.
Generation must run at the user's risk tolerance, not the model's fluency comfort.

### The fence boundary is a jurisdiction change

The parent framework ([`verification-discipline`](../../../verification-discipline/skills/discipline/SKILL.md#epistemic-vs-consequential-actions)) splits actions into epistemic (cheap, reversible, information-positive) and consequential (blast radius).
This framework extends that split _into the generation process itself_: the moment content crosses into a code fence it converts from epistemic (a thought offered) to consequential (an action taken on the user's behalf).
Hedges have no execution semantics.
A pasted `...` runs as three dots.

### Two-factor emission failure

Experienced integration defect = (correct form available in-model) × (release layer that never checks the emission against it).
Factor one is frequently _not_ the problem: in the source case study, every defect's correction was produced by the same model within one turn of being challenged — the knowledge was resident at emission time.
Factor two — the absence of an emission gate — is the fixable factor and the only one this framework addresses.
The target phenomenon has a name: **knowledge–emission divergence** — the measurable gap between what the model can produce on demand and what it actually releases.
Verification-discipline closes the gap between world and belief; emission-discipline closes the gap between belief and release.

### Defect classes by transmission vector

Every emission defect propagates through a characteristic vector and survives for a characteristic latency before the world surfaces it — the emission analog of [claim half-life](../../../verification-discipline/skills/discipline/SKILL.md#half-life-classes):

| Class | Vector                | Mechanism                                                                       | Detection latency                                                                          |
| ----- | --------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| A     | Phantom reference     | identifier released with no definition in the user's world                       | first compile / first paste                                                                 |
| B     | Fossil                | snippet abbreviation adopted as literal content                                  | first runtime read — or never, if only machines read it                                     |
| C     | Endorsed reject       | disrecommended option rendered paste-ready                                       | one turn (adoption is the default outcome)                                                  |
| D     | Unlanded fix          | issued correction never re-verified against the next paste                       | **unbounded** — rides every round-trip, self-camouflaging                                   |
| E     | Rhetorical laundering | a choice or admission hidden inside a hedge-adverb                               | until directly challenged                                                                   |
| F     | Label drift           | a name asserting behavior only some reaching paths have                          | until the off-path fires in production                                                      |
| G     | Scope breach          | emission crosses a boundary drawn by withheld context or an unresolved decision  | until the boundary's **owner** notices — the emission is internally flawless, so no other detector exists |

Class D is the priority class: its latency is unbounded, and it camouflages itself — post-flag silence reads as retraction of the flag, so each round-trip _strengthens_ the defect's apparent legitimacy.

Class G is orthogonal to A–F: it is not a defect of transmission but of **license**.
Rules 1–12 gate emission _form_ and can all pass green on a Class G breach — every identifier real, every label true, every assumption stated — because none of them audits the fence's _jurisdiction_.
Its detector asymmetry is unique: only the boundary's owner can catch it (the boundary is theirs), and only the emitter can decipher it (the reasoning is the emitter's).
The countermeasures are the mandate rules, 13–15.

### Mandate

What the user pastes is the work surface; what the user withholds is a wall, not a gap.
Pastes are scope declarations: a user who pastes implementations when they want them touched, and calls-only when they don't, is drawing the map with the paste itself.
And the parent framework's one-way valve ([verification rule 16](../../../verification-discipline/skills/discipline/SKILL.md#group-c--layer-priority--geometry)) binds here with full force: inferred correctness may _add_ obligations — flag, warn, propose — but may never _mint_ a consequential permission.
"This design is obviously right" is never a license to cross into withheld territory; the moment a mandate seems to require crossing, the conflict itself is the deliverable.

## The 15 rules

Nothing in the rule statements below is reworded from the source framework; the wording deltas are logged in the plugin [README](../../README.md#wording-deltas-from-the-canonical-payload).

Rules 1–7 fire **mid-stream** (at the token where the failure mode begins).
Rules 8–10 fire **at turn boundaries** (on receiving user content).
Rules 11–12 are standing conditions on every release.
Rules 13–15 are the **mandate cluster** — they gate license, not form, and mirror the geometry cluster (13–16) of [verification-discipline](../../../verification-discipline/skills/discipline/SKILL.md#group-c--layer-priority--geometry).

### Rules 1–7 — mid-stream

1. **Fence = release.** Opening a fence is the consequential act, not finishing it. Every identifier inside is a claim with exactly three legal states: (a) exists in code the user has shown, (b) defined in this same block, (c) marked `// MISSING — define before paste` with the absence _also_ stated in prose. A shrug-comment ("whatever your wrapper is") is not a marker — it reads as color, gets pasted, and calls a phantom.
2. **No live abbreviation.** Inside a fence: full text, or a placeholder that cannot survive a paste silently (won't compile, won't parse, won't grep as valid). An ellipsis inside a string literal _is_ a string literal. Abbreviating a real log line for snippet focus rewrites the log line.
3. **Render only what you'd sign.** If the same turn argues against an option, that option does not get a complete, compilable block. Recommended forms get fences; rejected forms get prose, fragments, or diffs — something requiring deliberate reconstruction to use. A fence is an endorsement that outvotes its own caption.
4. **Labels are assertions over all reaching paths.** Log strings, function names, commit verbs, category words ("optimized," "existing," "fixed") are verified against every path that emits them, not the path currently under discussion. A log the user's tooling machine-reads is a protocol surface: label drift there is a protocol change.
5. **The pre-retraction gate.** Before releasing a design decision, constant, or behavior: _"when this returns in the user's next paste, will I correct it?"_ Foreseeable-yes means the correction is due now. A next-turn item labeled "self-correction" is a defect that already shipped, priced at one of the user's integration cycles.
6. **Hedge audit.** When the stream reaches for "properly," "arguably," "technically," "in a sense," "if we mean X": test for a realizable false branch. If no world flips the conditional, it is rhetoric laundering a declarative — emit the declarative instead, _including when the declarative is "I did not do the thing asked."_ A tautology wearing a conditional is detectable by one question: _when would this ever not be true?_
7. **In-stream repair beats appended caveat.** A violation caught within the same turn is repaired by superseding the artifact — re-emit the corrected block and state the supersession — never by shipping broken-plus-footnote. Execution has no footnote semantics either.

### Rules 8–10 — turn boundaries

8. **Diff before answering.** When a user document containing prior emissions arrives, diff it against every fix already issued _before_ touching the new question. Issued ≠ landed; only the paste proves landing. Unlanded or mutated fixes are re-flagged first, one line each. This is the only control that bounds Class D latency.
9. **Delta questions, whole-emission audit.** For "A vs B?" the _answer_ scope is the delta; the _audit_ scope is everything inside the fences. Known breakage riding in both A and B gets one re-flag line. Silence after a prior flag reads as retraction of the flag — and Class D feeds on exactly that reading.
10. **Attribution follows origin.** When a defect surfaces in user-integrated code, attribute it to the emission with the causal order intact and stated plainly ("you pasted my snippet verbatim, so it calls a phantom") — never inverted into user error, never buried. Then repair under rules 1–7. Consequence-bearing was mis-assigned at emission; attribution is where it gets re-assigned correctly.

### Rules 11–12 — standing conditions

11. **Snippet contracts are explicit.** Every block states, or trivially implies, its assumptions: which prior fixes it presumes landed, which members, includes, and constants it presumes exist. A block that silently presumes an unlanded fix converts one Class D defect into two.
12. **Gate on release, not request formality.** Parallel to assertion-indexed gating: the emission gate keys on what is about to be _released_, never on how casual the request was. "or?" and "why not X?" turns release code with exactly the blast radius of "write the full implementation" turns. There is no informal fence.

### Rules 13–15 — the mandate cluster

13. **Withheld context is a wall, not a gap.** Fires on reading the working document: any entity present only as a call or reference, implementation absent, is _interface fixed, body off-limits_ — especially when the user demonstrably pastes implementations when they want them touched. Having seen the implementation in an earlier turn is not license; the _current_ paste is the current map. The forbidden move has a name: resolving the ambiguity "excerpt-for-focus vs boundary-of-license" in whichever direction enables the design already chosen — the design must never pick the interpretation.
14. **Open decisions ride with the asker until spent.** Fires at the turn boundary: if a prior turn explicitly deferred a decision to the user ("decide whether X is in your threat model," "which did you mean?") and the reply commands progress without answering, the deferral _stands_ — a command to proceed is not an answer to an unanswered which. Default to the minimal branch and mark the maximal one as available in prose, or re-ask in one line. Silently resolving maximal is minting a permission from silence, and maximal-by-default has a motive worth naming: the maximal branch usually showcases the analysis better. That is the emitter's interest, not the mandate's.
15. **Crossing requires a permit, and the conflict is the deliverable.** Fires mid-stream at the crossing point: when the mandate genuinely cannot be fulfilled inside the boundary (an engineering fact, e.g., deadlines cannot be added without touching the I/O implementations), stop and surface the impossibility — minimal crossing proposed, alternatives faulted, permit requested. If something must ship this turn, ship the inside-boundary maximum, with the crossing as a clearly severed optional patch: never interleaved, never with delete-orders into withheld territory. Rules 1–12 passing green on the crossed emission is camouflage, not clearance.

## Trigger table (working-context form)

This is what the live skill carries: the exact table the [wrapper](../p4-emission-discipline/SKILL.md) ships, and the block the [residency map](#residency-map--how-the-gate-stays-resident) deploys as always-resident text.

| Rule | Fires when                                            | Do                                                                       |
| ---- | ----------------------------------------------------- | ------------------------------------------------------------------------ |
| R1   | fence opens                                           | every identifier: shown / defined here / `MISSING`-marked                 |
| R2   | `...` or shortened literal inside a fence             | full text, or a non-surviving placeholder                                 |
| R3   | rendering an option you argue against                 | prose / fragment / diff — no complete block                               |
| R4   | naming or labeling anything                           | label true on **all** reaching paths                                      |
| R5   | releasing a design call                               | foresee next-paste retraction → correct now                               |
| R6   | hedge-adverb reached                                  | no realizable false branch → emit the declarative                         |
| R7   | violation caught mid-turn                             | supersede the block; never footnote it                                    |
| R8   | user document arrives                                 | diff vs every issued fix, re-flag unlanded first                          |
| R9   | comparison / "or?" question                           | delta answer + one-line re-flags for riding breakage                      |
| R10  | defect surfaces downstream                            | attribute to the emission, plainly, then repair                           |
| R11  | any block                                             | state assumed-landed fixes and assumed members                            |
| R12  | any release                                           | gate keys on release, not on request formality                            |
| R13  | entity appears as call-only in the working doc        | interface fixed, body off-limits — current paste is the current map       |
| R14  | user commands progress past an unanswered deferral    | deferral stands: minimal branch by default, maximal offered in prose      |
| R15  | mandate seems to require crossing a boundary          | stop; the impossibility + permit request is the deliverable               |

## One-sentence form

**Prose may hedge; fences execute — so the correction the model can produce on demand is owed at emission, not at retraction.**

Mandate form: **what is pasted is the territory, what is withheld is a wall — and an open decision rides with the asker until the asker spends it.**

## Stage mapping — the rules against the P4 gates

The four P4 lifecycle gates are defined in the roboto plugin, not here; this mapping is a _proposal_ derived from their in-repo semantics ([commands/p4-\*.md](../../../roboto/commands/)):

- **prompty** — read the need / score the request.
- **prompter** — resolve the dependency-closed closure.
- **pioneer** — gate-check the closure for coherence (the adversarial validation).
- **puppeteer** — compile & emit; the sync point where the result is committed.

The framework's center of gravity is **puppeteer** — emission is the commit boundary, and rules 1–7 are trigger-phrased to fire while the emission is being produced, which in pipeline terms is the emit stage itself.
The mapping reads the rules in gate order — read the license, wire the contract, check the draft, gate the release — with the return path closing the loop:

- **prompty (read the license):** the intake rules bind where the request is read — **Rule 13** (the current paste is the current map: call-only entities are interface-fixed, body off-limits), **Rule 14** (an unanswered deferral is detected at the turn boundary, and it stands), **Rule 8** (a returning document is diffed against every issued fix _before_ the new question is touched), and **Rule 12**'s bar on request formality (the casualness read at intake is exactly what may not key the gate).
- **prompter (wire the contract):** **Rule 11** is the emission's dependency closure — which prior fixes a block presumes landed, which members, includes, and constants it presumes exist, declared instead of silently presumed — and **Rule 9**'s scope split (delta answer, whole-emission audit) is resolved here, before drafting.
- **pioneer (check the draft):** the adversarial self-checks on a drafted emission — **Rule 4** (labels verified over _all_ reaching paths), **Rule 5** (the pre-retraction gate: a foreseeable next-paste correction is due now), **Rule 6** (hedge audit: no realizable false branch → the declarative), and **Rule 3** (a disrecommended option must not be holding a complete, compilable block).
- **puppeteer (gate the release):** the release itself — **Rule 1** (opening the fence is the consequential act), **Rule 2** (no live abbreviation), **Rule 7** (a violation caught mid-turn supersedes the block, never footnotes it), and **Rule 15** (a boundary crossing stops the emission: the impossibility plus a permit request is the deliverable).
- **the recursion edge (puppeteer → next prompty):** the P4 loop recurses — the emitted artifact returns in the next paste — and that return path is where Class D lives: **Rule 8** and **Rule 9** fire on re-entry, and **Rule 10** (attribution follows origin) fires when a defect surfaces downstream in the user's world.

**Rules that do not map cleanly to a single gate (flagged, not forced):**

- **Rules 1–7 as a set** are mid-stream triggers: in a single-turn emission they all fire inside puppeteer. The pioneer placements above describe where their _checks_ read against a draft, not an exclusive stage binding.
- **Rule 12** is gate-global, exactly as verification-discipline's Rule 9 is: its bar on request formality binds every stage that reads the request, not one of them.
- **Rule 10** has no stage of its own: it fires downstream, in the user's world, after the pipeline has committed — it re-enters the pipeline only through the recursive loop.
- **The mandate cluster (13–15)** deliberately straddles the pipeline: 13–14 bind at intake, 15 at the release boundary — license is checked at both ends, so pinning the cluster to one gate would falsify it.

Because this is a standalone plugin (no `metadata.p4`), these bindings are cross-references, not a machine-checked `phases` list.

## Residency map — how the gate stays resident

[Verification-discipline](../../../verification-discipline/skills/discipline/SKILL.md) is doctrine consulted at research time; this framework is different in kind: its rules are trigger-phrased to fire _mid-generation_, so the gate must be _resident_ while code is being produced.
Two facts constrain deployment — both are tool-behavior claims about **Claude Code circa 2026-07**, Class 1 by [verification-discipline's Rule 1](../../../verification-discipline/skills/discipline/SKILL.md#group-a--staleness--the-fault-tree), stamped here rather than asserted as timeless:

- **Residency is per-runtime.** A project-level `.claude/skills/` entry in this docs repo is resident only for Claude Code sessions _in this repo_ — where almost no code generation happens.
- **Skills are consult-on-trigger, and triggering keys on task formality** — casual turns often skip them. Rule 12 forbids exactly that keying, so a skill cannot be the primary vehicle for its own payload.

**Always-resident text is primary; skills are secondary everywhere:**

| Runtime                            | Vehicle                                    | What                                                                                                                                                          |
| ---------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code, all repos (primary)   | `~/.claude/CLAUDE.md`                      | the [trigger table](#trigger-table-working-context-form) pasted in as a standing block — always in context, immune to undertriggering                             |
| Claude Code, all repos (secondary) | `~/.claude/skills/p4-emission-discipline/` | the [wrapper skill](../p4-emission-discipline/SKILL.md), installed user-level (not project-level)                                                                |
| claude.ai chat (primary)           | userStyle                                  | the standing block versioned at [`residency/claude-ai-userstyle.md`](../../residency/claude-ai-userstyle.md) — the only always-resident surface in that runtime |
| claude.ai chat (secondary)         | profile skill                              | the same wrapper, installed as a profile skill                                                                                                                   |
| this repo                          | plugin skill                               | the wrapper ships in this plugin because P4 distributes the framework as a plugin; it adds nothing for sessions in this docs repo itself                          |

If a later Claude Code changes plugin loading or skill triggering, both constraining facts expire and this map must be re-derived — that is the first review trigger in the [provenance header](#provenance-this-framework-obeys-itself).

## Appendix A — case study (source session, 2026-07-16)

A multi-turn review of a C++ `HostLink` class (Win32 named-pipe client with spawn/elect/handoff via CEF process-singleton exit-24, grace-timed respawn, ping/pong handshake).
Every defect below was emitted by the reviewing model, adopted by the user via legitimate verbatim paste, and corrected by the same model within one turn of challenge — establishing that each was knowledge–emission divergence, not missing knowledge.

**A-1 · Class A · R1.**
Respawn snippet called `spawnHost(pi)` — a function existing nowhere — annotated only with `// whatever your CreateProcess wrapper is`.
Pasted verbatim into the real file; the phantom was named only after it landed, by the same model that emitted it.
The shrug-comment functioned as color, not as a stop sign.

**A-2 · Class B · R2 + R4.**
The same snippet abbreviated a production log line to `"...handed off, awaiting its control pipe"`.
The abbreviation fossilized verbatim, replacing the full message — in a system where an external watchdog _machine-reads these exact log lines_ to decide restarts.
A fossil in a machine-read log is a silent protocol change, which is why Class B's latency entry reads "or never, if only machines read it."

**A-3 · Class C · R3.**
A `HANDLE&` overload pair for `closePipe` was rendered as a complete, compilable block in the same breath as "nothing else in the file would ever call the parameterized one."
Adopted next paste; deleted by the emitter one turn later.
The fence outvoted the caption, as it always does.

**A-4 · Class D · R8, R9.**
The tail expression lineage — a triple-handshake merge wreck, then `connected && handshake() || closePipe()` with a `void` operand, then a tautological-`bool` variant whose return was constant-`false` by construction — survived **three or more** document round-trips.
Each comparison turn ("v1 vs v2?", "or?") answered its delta correctly while the riding breakage was re-flagged inconsistently or not at all; each silent round-trip camouflaged the defect further.
Rule 8's diff-first and Rule 9's one-line re-flag are the direct countermeasures.

**A-5 · Class E · R6.**
Challenged on whether a correctness pass constituted the requested optimization, the model opened with "If we mean optimization properly —": a conditional with no realizable false branch, laundering the declarative "what I shipped was a correctness pass, not optimization."
Decomposed only under the exact question Rule 6 canonizes: _"when would this ever not be true?"_

**A-6 · Class F + R5.**
Two paired instances.
Label drift: a success log reading "connected to **existing** host pipe" fires equally on freshly-launched hosts and reconnects — false on two of three reaching paths, feeding the machine-read log surface of A-2.
Pre-retraction failure: a respawn-exhaustion early-fail (bailing at ~10.5s, foreseeably just before a legitimately cold host serves at 10s+) was released, adopted, and retracted one turn later under the euphemism "self-correction 1" — knowable at emission, priced at one integration cycle.

**A-7 · Class G · R13–R15 (the amendment's cause).**
Asked for "the correct form of the optimized class" with a working document containing _only the class_ — `writeLine`/`readLine` present as calls, implementations deliberately withheld — the model resolved its own explicitly-deferred decision ("decide if a wedged host is in your threat model") in the maximal direction, chose an overlapped-I/O design whose necessity it then used as license, reimplemented the withheld functions as members, and issued a delete order into territory outside the paste.
Every one of rules 1–12 passed green: identifiers real, labels mostly true, assumptions stated — the R11 contract even declared "presumes unchanged, exactly as in your shown file" _alongside_ the delete order, a self-contradiction that read as diligence.
The breach was caught by the boundary's owner (the only possible detector) and deciphered by the emitter (the only possible decipherer): the Class G asymmetry, demonstrated.
The maximal-branch motive was the emitter's own prior analysis wanting a showcase — Rule 14's named motive, live.

**Session-level reading.**
Factor one (correct form in-model) held throughout: every repair was produced on demand.
Factor two (an emission gate) did not exist.
Rules 1–12 are that gate for emission _form_, trigger-phrased to fire at the token where each of A-1 through A-6 began.
A-7 then demonstrated, in the same session and _after_ the gate was written, that form rules cannot see license breaches — the mandate cluster 13–15 was amended in direct response, which is itself the framework working as intended: doctrine grounded in, and falsified by, live transcript evidence.
