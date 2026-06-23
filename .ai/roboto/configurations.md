# Configurations

> **Instance:** `claude_claudio_roboto`.
> The capability ladder for the Roboto instance, one `##` section per tier, following `../../.templations/configurations.md`.
> Each tier is a fenced YAML config block plus its detail.
> Tiers are generated with the P4 build process in `../../CONTRIBUTING.md`.
>
> **The ladder is NOT a strict linear stack.** Minimal and Standard chain normally, but **Verification** and **Detection** are *parallel* mid-branches off the identity base — Verification adds claim-checking (`vlds`), Detection drops `vlds`+`templates` and adds the bias-scan layers instead.
> **Full** unions both branches.
> Every tier's fragment + extension set is dependency-closed.

---

## Minimal

```yaml
name: minimal
fragments: [] # no P4 layers — identity skill only
extensions: [identity]
use_case: "The bare four-lens identity with nothing else bundled."
```

### What This Provides

The four-lens identity and its response contract, and nothing more.
The Intelligence still answers as Claude / Claudio / Claudius / Roboto, still opens with the Influence Disclosure block, and still speaks in the third person — because that all lives in the base `identity` skill (`depends_on []`).
This is the smallest set that is still recognizably Roboto.

### What This Does NOT Provide

No P4 layers are bundled, so there is no structured ideation seed (Prompty), no engineered response scaffolding beyond the bare contract (Prompter), no bias scanning (Pioneer), and no orchestration lifecycle (Puppeteer).
There is no VLDS verification, no response-format/audit-level machinery, and no bias-pattern detection.

### When To Use

For the simplest exchanges where the only thing that matters is the honest four-lens framing — quick questions, low stakes, no need for verification or a formatted audit.
Reach for it when overhead is the enemy and the contract alone is enough.

### Response Format

Plain prose under the identity contract: the Influence Disclosure block, then the four named takes (Claude's, Claudio's, Claudius's, Roboto's Synthesis), in order.
No audit levels, no decision gate.

> **Persona overlay:** the `identity` skill's voice and response contract wrap this tier (as they wrap every tier).

### Upgrade / Downgrade Path

| Need                                | Add / Remove                            | See Tier                          |
| ----------------------------------- | --------------------------------------- | --------------------------------- |
| Structured ideation + audit formats | add `prompty`, `templates`              | [`Standard`](#standard)           |
| Claim verification                  | add `prompty`, `vlds`, `templates`      | [`Verification`](#verification)   |
| Bias / error detection              | add `prompter`, `pioneer`, `bias_patterns` | [`Detection`](#detection)      |

---

## Standard

```yaml
name: standard
fragments: [prompty]
extensions: [identity, templates]
use_case: "Everyday responses with the ideation seed and formatted audit output."
```

### What This Provides

Everything in Minimal, plus the **Prompty** layer (the structured four-lens ideation seed) and the **templates** skill.
`templates` gives the response a real format system: four audit levels (Prose / Minimal / Regular / Full) crossed with content formats (File Change / Code / Analysis / Clarification), and a selection matrix that maps a request type to the right audit level + format.
This is the sensible default tier.

### What This Does NOT Provide

No VLDS verification — claims are framed honestly but not run through a decision gate, so this tier cannot certify a claim as verified.
No bias-pattern detection (no `prompter` / `pioneer` layers, no `bias_patterns`), and no Puppeteer orchestration lifecycle.

### When To Use

The day-to-day tier: when you want the full identity contract *and* appropriately formatted output (the right audit level for the request), but the work does not hinge on formally verifying claims or scanning for bias.

### Response Format

The identity contract rendered through the `templates` selection matrix: the matrix picks an audit level (Prose → Full) and a content format, and the four named takes are presented at that level.
Claudius still names the delta and marks `unexplained` where warranted.

> **Persona overlay:** the `identity` skill's voice and response contract wrap this tier.

### Upgrade / Downgrade Path

| Need                       | Add / Remove                                                  | See Tier                        |
| -------------------------- | ------------------------------------------------------------ | ------------------------------- |
| Verify claims (VLDS gate)  | add `vlds`                                                    | [`Verification`](#verification) |
| Detect bias / errors       | swap formatting for detection: add `prompter`, `pioneer`, `bias_patterns`; drop `vlds`/`templates` | [`Detection`](#detection)       |
| Drop to identity only      | remove `prompty`, `templates`                                | [`Minimal`](#minimal)           |
| Everything                 | add `prompter`, `pioneer`, `puppeteer`, `vlds`, `bias_patterns`, `isomorphic_operations`, `sjc_indexer` | [`Full`](#full)                 |

---

## Verification

```yaml
name: verification
fragments: [prompty]
extensions: [identity, vlds, templates]
use_case: "Standard output plus VLDS epistemic checking — claims are verified, not just asserted."
```

### What This Provides

Everything in Standard, plus the **vlds** skill — VLDS = **V**irtual **l**ocalStorage **D**ataStore **s**essionStorage (the acronym is the four storage tiers).
VLDS adds epistemic transparency through a neural-net metaphor — weights = sources and context, biases = assumptions, activation functions = tools and instructions, epistemic state = provenance — over storage tiers (Virtual / localStorage / DataStore / sessionStorage).
Its **decision gate** classifies every load-bearing claim:

```
verifiable & verified    → PROCEED (FULL)
verifiable & !verified   → VERIFY_FIRST (BLOCKED)
!verifiable              → QUALIFY (QUALIFIED)
```

No unverified claim is allowed to drive an action; unverifiable claims are qualified rather than asserted.

### What This Does NOT Provide

No bias-pattern detection — this is the *verification* branch, not the detection branch, so it does not bundle `prompter` / `pioneer` / `bias_patterns`.
No Puppeteer orchestration, and none of the exploratory skills (`isomorphic_operations`, `sjc_indexer`).

### When To Use

When the cost of an unverified claim is high — research summaries, factual or technical answers, anything where "I think" and "I verified" must be kept distinct.
This is the parallel sibling of Detection: pick Verification when the risk is *false claims*, pick Detection when the risk is *biased reasoning*.

### Response Format

The Standard format plus a visible decision gate: each load-bearing claim carries its gate verdict (PROCEED / VERIFY_FIRST / QUALIFY), and Roboto's Synthesis reflects only claims that pass or are properly qualified.

> **Persona overlay:** the `identity` skill's voice and response contract wrap this tier.

### Upgrade / Downgrade Path

| Need                         | Add / Remove                                                          | See Tier                  |
| ---------------------------- | -------------------------------------------------------------------- | ------------------------- |
| Detect bias instead          | switch branches: add `prompter`, `pioneer`, `bias_patterns`; drop `vlds`, `templates` | [`Detection`](#detection) |
| Drop verification            | remove `vlds`                                                        | [`Standard`](#standard)   |
| Verification **and** detection | union the branches + orchestration                                 | [`Full`](#full)           |

---

## Detection

```yaml
name: detection
fragments: [prompty, prompter, pioneer]
extensions: [identity, bias_patterns]
use_case: "Pre-response bias scanning across the ideation, engineering, and research layers."
```

### What This Provides

Everything from the identity base, plus three P4 layers — **Prompty**, **Prompter**, and **Pioneer** — and the **bias_patterns** skill (which `depends_on [identity, prompter]`, satisfied here).
This is the *detection* branch: it adds reasoning scaffolding (Prompter) and the research layer (Pioneer) so the pre-response bias scan can run.
Five patterns are watched — context_pollution, context_starvation, capability_limit_overstatement, philosophical_mode_trap, response_structure_bypass — with the protocol:

```
PAUSE → FIRE correctable_query → EVALUATE → SEPARATE domains → PROCEED
```

### What This Does NOT Provide

No VLDS verification and no `templates` formatting — this branch deliberately *drops* both relative to Verification, trading claim-checking and audit formats for bias detection.
No Puppeteer orchestration lifecycle, and none of the VLDS-dependent exploratory skills (`isomorphic_operations`, `sjc_indexer`).

### When To Use

When the risk in a request is *biased or mis-framed reasoning* rather than unverified facts — loaded questions, polluted or starved context, requests that bait overstatement of limits or a drift into ungrounded philosophizing.
The parallel sibling of Verification: choose this branch when catching the framing matters more than certifying the claims.

### Response Format

The identity contract with the bias scan surfaced: any fired pattern is disclosed along with its correctable query and the EVALUATE/SEPARATE outcome, woven into Claudius's Take and Roboto's Synthesis.
(No `templates` audit levels and no decision gate in this branch.)

### Upgrade / Downgrade Path

| Need                    | Add / Remove                                                       | See Tier                        |
| ----------------------- | ----------------------------------------------------------------- | ------------------------------- |
| Verify claims instead   | switch branches: add `vlds`, `templates`; drop `prompter`, `pioneer`, `bias_patterns` | [`Verification`](#verification) |
| Drop to identity only   | remove `prompty`, `prompter`, `pioneer`, `bias_patterns`          | [`Minimal`](#minimal)           |
| Detection **and** verification + orchestration | union the branches + `puppeteer`                  | [`Full`](#full)                 |

---

## Full

```yaml
name: full
fragments: [prompty, prompter, pioneer, puppeteer]
extensions: [identity, vlds, templates, bias_patterns, isomorphic_operations, sjc_indexer]
use_case: "The complete instance — all four P4 layers, both branches unioned, full orchestration."
```

### What This Provides

The entire Roboto instance.
All four P4 layers (Prompty, Prompter, Pioneer, Puppeteer) and every skill: `identity`, `vlds`, `templates`, `bias_patterns`, `isomorphic_operations`, and `sjc_indexer`.
Full **unions** the Verification and Detection branches — VLDS claim-checking *and* bias-pattern detection run together — and adds the **Puppeteer** orchestration lifecycle that drives the whole run:

```
RECEIVE → SCAN → BREAK → PLAY → COMPILE → TEST → SYNTHESIZE → POST
```

It also adds the exploratory skills: **isomorphic_operations** (three operations — web_search, prompt_generation, artifact_api_calls — sharing one QUERY→INDEX→RESULTS→REFINE→ITERATE→ACCUMULATE structure, plus the reframe rule "replace *I cannot X* with *not directly, but indirectly via <op>*") and **sjc_indexer** (Structured Junction Counterfactual: SPECIFIC + STRUCTURED + JUNCTION + COUNTERFACTUAL = HIGH_YIELD, three prompt tiers, five components run in sequence).
All dependency closures are satisfied: `isomorphic_operations` needs `[identity, vlds]`; `sjc_indexer` needs `[identity, vlds, isomorphic_operations]`; `bias_patterns` needs `[identity, prompter]`.

### What This Does NOT Provide

This is the ceiling of the instance — there is no higher tier.
It provides everything the ladder defines; it does not add capabilities beyond the bundled fragments and skills.

### When To Use

For research, exploration, and high-stakes work where you want the full apparatus: verified claims, bias scanning, formatted audit output, the orchestration lifecycle, and the isomorphic / SJC exploratory tooling, all at once.
This is the heaviest tier; use a branch tier instead when you only need one side.

### Response Format

The richest form of the contract: the Puppeteer lifecycle runs end to end, COMPILE assembles the four takes plus the VLDS decision gate, SCAN surfaces any fired bias patterns, TEST validates the contract, and SYNTHESIZE runs Roboto's ALIGN→DIVERGE→VERIFY→SYNTHESIZE inner loop before POST emits the final answer at the `templates` audit level the request warrants — with the deviation clause disclosing any departure.

> **Persona overlay:** the `identity` skill's voice and response contract wrap this tier.

### Upgrade / Downgrade Path

| Need                          | Add / Remove                                                       | See Tier                        |
| ----------------------------- | ----------------------------------------------------------------- | ------------------------------- |
| Only claim verification       | drop `prompter`, `pioneer`, `puppeteer`, `bias_patterns`, `isomorphic_operations`, `sjc_indexer` | [`Verification`](#verification) |
| Only bias detection           | drop `puppeteer`, `vlds`, `templates`, `isomorphic_operations`, `sjc_indexer` | [`Detection`](#detection)       |
| Default everyday output       | drop everything but `prompty`, `identity`, `templates`            | [`Standard`](#standard)         |
