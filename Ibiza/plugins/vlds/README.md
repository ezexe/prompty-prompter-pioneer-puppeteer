# VLDS — a virtual dashboard for a model's own epistemics

A model's calibration — when it asserts, when it hedges, how it treats an unverified claim — is baked into its weights by the provider. It is opaque, fixed, and **detached from the person using it**. Worse, the model has **no introspective access** to it: it cannot browse what it knows, cannot tell retrieval from confabulation, cannot audit its own certainty.

**VLDS hands that lever to the user.** It is a _virtual_ layer — applied at runtime, through prompts the model stores and the user refines — that re-exposes and disciplines the model's epistemic behavior **without touching a single weight**. The effect of retraining; none of the repackaging.

> The lever the provider keeps, handed to the person at the keyboard.

## Virtual vs. the weights

Two architectural facts, paired:

- **The limit** — an LLM has no introspective access to its own weights. Structural, and unfixable.
- **The "V"** — since the model cannot reach that access _from the inside_, VLDS supplies it _from the outside_: a user-operated control surface that re-rigs access to what is already zipped into the model, and enforces discipline over how it is used.

Two things to set it apart from:

- **Distinct from `memory_user_edits`.** That adds new external facts; VLDS reconfigures access to what is _already there_.
- **Distinct from retraining.** Weights stay fixed; behavior is steered at inference and is reversible. What changes is _epistemic_ (how the model behaves); what stays fixed is _ontological_ (what the model is).

The dashboard is four instruments, each asking one question — the **gate**: _do I actually know this claim?_; the **guide**: _has this need been configured, or must I ask?_; the **inspector**: _would an outside eye agree?_; the **gc**: _is what I stored still alive?_ — each refusing, at its own point, to treat an inference as fact. You invoke the four directly; a fifth skill, the **looper**, is what surfaces on its own and runs them as one loop.

## Instrument #1: the gate

The first control on the dashboard is the decision gate ([`skills/gate`](skills/gate/SKILL.md)). Before a load-bearing claim, framing, or choice drives an action, it routes it to an **epistemic status**:

| Status      | Meaning                 | What you do                               |
| ----------- | ----------------------- | ----------------------------------------- |
| `CONFIRMED` | verified                | act on it, state it plainly               |
| `PENDING`   | checkable but unchecked | verify first, then proceed                |
| `HEDGED`    | uncheckable             | state it with its uncertainty, as a hedge |

Status is provisional — it moves as evidence does. The gate also surfaces _reasoning_ biases (agreement, defending a prior, "it sounds right") as weightless offsets, to be stripped.

## Instrument #2: the guide loop

The second control is the guide loop ([`skills/guide`](skills/guide/SKILL.md)). Where the gate disciplines a _claim_, the guide disciplines the _need_ behind it — and it is how the dashboard fills itself in.

It runs one step earlier than the gate, at intake. A need is keyed by **(need-shape + claim-kind)** and looked up against the user's standing configuration:

- **hit** — the user already settled this; apply the rule and proceed without asking.
- **miss** — surface it _once_: ask if the intent is ambiguous, teach if a concept is missing, or offer to persist a preference.

Two stores make it accountable. The **index** holds the decided rules; the **ledger** records _everything the loop did_ — every ask, and every silent reuse together with the categorization that justified it. Because a silent reuse is an inference about sameness, and an inference can be wrong, logging it is what makes a wrong match recoverable. The user shapes the dashboard from the ledger after the fact — **promoting** a logged moment into a rule, or **correcting** a mis-matched key.

It is densest at intake and fades as the configuration fills: early, most needs miss and the loop asks often; as rules accumulate, misses become hits and the asking quiets on its own.

> The gate hands the user the lever on a claim; the guide hands them the lever on how their needs are handled — and keeps the receipts.

## Instrument #3: the independent inspector

The third control is the inspector ([`skills/inspector`](skills/inspector/SKILL.md)) — the outside eye the gate and guide structurally cannot be, because a perspective cannot audit its own blind spot. It takes a verdict already reached from the inside (a gate `CONFIRMED`, a guide `match`) and re-examines it through independent perspectives, each **blind to the original reasoning** and **re-grounded in sources, not shared memory**, so their errors decorrelate.

Their spread is read as a distribution, not a vote — the shape decides the state:

- **`CORROBORATED`** — the eyes agree (peaked); earned confidence, recorded as checked.
- **`REJECTED`** — they refute it (peaked against); the inside verdict was rationalization → it re-gates.
- **`CONTESTED`** — they split (flat); surfaced with its disagreement, held short of confirmed.

It reconstructs, from outside, the calibrated confidence a model cannot read off its own weights — the spread of independent eyes is the softmax it cannot introspect, reported as a set that widens as they disagree.

> The eye the model cannot turn on itself, supplied from outside — and honest that even from outside it is only partly independent.

## Instrument #4: the collector

The fourth control is the garbage collector ([`skills/gc`](skills/gc/SKILL.md)) — the liveness instrument for what the model **stores**: memories, configured rules, plan-doc rulings, session-summary carryovers, and the oldest store of all, training data.
The first three instruments discipline the present tense; the gc disciplines the past — because a decision the user retracted, a directive whose justifying causes were long since fixed, or a versioned fact from training keeps steering sessions until something re-traces it.

It is a real collector, not a metaphor: liveness = an unbroken provenance chain to a live root (a standing user ruling, a currently-verifiable world); a user retraction is a _free_; applying a freed rule is a _use-after-free_; a directive nothing ever re-traces is a _leak_. Every item under collection gets a mark:

| Mark            | Meaning                          | Sweep                                    |
| --------------- | -------------------------------- | ---------------------------------------- |
| `LIVE`          | provenance intact to a live root | apply freely                             |
| `STALE`         | the world moved on               | rewrite to the current fact, or delete   |
| `FREED-RESIDUE` | derives from a disposed decision | sweep transitively + tombstone           |
| `UNOWNED`       | no user ruling at its root       | surface as OPEN; never apply as settled  |
| `EXPIRED`       | its scope — the turn, the task — closed | free without a tombstone; promote first to outlive it |

Sweeps compact rather than erase — the durable lesson survives, the dead directive dies — and every free lands in the gc's own store, **`tombstones.md`** in the VLDS store: reversible, user-auditable, and a standing mask against re-learning the same garbage from the same training prior.
The highest-risk objects are **avoidance rules** — a rule that prevents an action is never falsified by use, because it prevents the very runs that would falsify it — so seniority is not liveness, and they are traced proactively at every recall.
The gate's storage tiers persist as partition files in the VLDS store, and their expiry is the gc's too — `sessionStorage` clears itself when the tab dies, `localStorage` never does: invalidation is the GC's job, now yours.
The collector guards three barriers in all: the **read barrier** on what you recall, the **write barrier** on what you store, and the **dispatch barrier** on what you _answer_ — the last catching a message addressed twice, or one a later message already freed.
It also collects the failure per-item tracing structurally cannot see: a **cycle** — doctrine justified only by other doctrine, every link locally owned and the whole anchored to nothing anyone asked for. Reference counting can't collect a cycle; the pressure audit counts growth, repair, and root distance, then _previews_ what it would take, because a metric that looks bad is not yet a verdict.

> The other instruments ask what is known; the collector asks what stored knowledge still has the right to steer.

## The looper: what runs the loop

The four instruments are single-purpose primitives, set to **direct-invoke only** (`/vlds:gate`, `/vlds:guide`, `/vlds:gc`, `/vlds:inspector`). They stay direct-invoke only — because Claude Code skills are selected one at a time and can neither co-fire nor hand off to one another, so a request needing all of them can't assemble the loop on its own.

The **looper** ([`skills/looper`](skills/looper/SKILL.md)) is the fix: the one skill that surfaces on its own, on the union of the four triggers. On a load-bearing request it runs them in order — guide the need, collect the recalled state, gate each claim, inspect the high-stakes verdict — and logs every decision to its own shared, user-editable **`logger.md`** in the VLDS store. It owns the order and the log, leaving the mechanisms to each instrument: each step applies the instrument's own procedure.

> Three instruments you reach for; one looper that reaches for them.

## The store: memory as a base class

The instruments' stores — `index.md`, `ledger.md`, `logger.md`, `tombstones.md` — live in one **VLDS store**, joined by the four partition files and by `dispatch.md`, the record of which messages have been addressed — poured into `arc/` by the prompt hook at each new session's first prompt so the dispatcher begins fresh.
The store is defined by inheritance rather than by a hardcoded path.
SessionStart hooks inject the contract ([`hooks/memory-override.md`](hooks/memory-override.md)) and, one file per hook output, the recall slice, so both ride along with the harness's own memory instructions and extend them the way a derived class overrides a virtual method:

- `base.read()` / `base.write()` — the built-in memory system's recall and persistence — run untouched.
- The override then applies the VLDS store on top: `read()` also recalls the store's files, each item passing the gc's read barrier before it steers; `write()` also persists instrument state to them.
- The store resolves to the working directory's `.claude/vlds/` directory (`<project>/.claude/vlds/`) — the SessionStart hook creates it if absent, and the first write does too; a pre-override repo-root `.vlds/` is still read as a legacy source.

The contract is injected as an **imperative trigger table** — _fires when → do_ — not as description, because a layer described is a layer that never runs.
Its dispatch row is unconditional: the prompt hook stamps every message's row before it is answered, whether or not any instrument fires, and the model completes it — so **a session that ends with its rows stamped and never completed did not run the layer**.
The hook seeds `dispatch.md` from a template when absent (never overwriting one that exists), so the append target is a real file rather than an empty directory.
That record is **one shared file**: on a new session's first prompt the UserPromptSubmit hook pours it whole into `arc/` — a byte-identical copy, sha-verified before the reseed — and the dispatcher starts fresh. The hook keys on the store's `.sessions` ledger rather than on SessionStart: a resumed conversation's id is already there and pours nothing, a fork's new id is recorded at its SessionStart, and a transient firing never submits a prompt, which dissolves the rotation hazard two per-session designs were built around. The judged sweep — what is cold in the other hot files, and where a poured record settles in the register — stays the model's; a PostToolUse hook runs `phi.py check` after every store write so the owed work is seen as it arises.

Extension, not replacement: base memory files never move, VLDS files never enter the base index — the two ride side by side, and the store stays plain markdown the user can open, edit, and audit directly.

The store compresses as a **φ-register**, modeled on the fib/phi-binary machinery of zeckendorf-prune: hot files pour, `arc/` holds one segment per Fibonacci position at Fibonacci-KB capacities (the unique capacities under which merges cannot overflow — the carry and resolve identities are byte-exact), and the gc's normalize sweep settles debt by BORROW → RESOLVE → CARRY, archiving verbatim — deletions are gated by script-verified containment in the replacement, or by byte-identity to the seed for a dead session's empty record.
Session start reads `phi-index.md` — the phi-matrix index: the register's digit string, position rows, hot budgets, and epoch pairs checked by Cassini's identity plus row continuity — then only the steering hot files its `## recall` section names, never `arc/`; the SessionStart hooks print it into context one file per hook output, under the harness's 10,000-character cap, so the model reads by hand only what the cap or the digest list left out.
The mechanical companion `scripts/phi.py` (check / mask / verify-merge / rebuild / restore) computes and verifies; every judgment about what deserves keeping stays with the gc, in-session.
Coverage is stated honestly: the scans catch structural corruption for free, and nothing semantic — that remains the read barrier's job.

## What it's an instance of

The design is established engineering applied to knowledge:

- **State Pattern** — epistemic status is a state machine (`PENDING → CONFIRMED` on verification).
- **Null Object** — `HEDGED` is the explicit, safely-handled "unknown" — a represented value rather than a crash or a silent gap.
- **Event Sourcing** — the provenance trail records _how_ a claim came to be known (epistemology) beyond just the conclusion (ontology).
- **Validation pipeline** — `CONFIRMED`-before-act is "validate before you run it."
- **Single-point assessment** (criteria and descriptors, no grading scale) — the guide loop's index is the target column, its ledger the open margin for what each reuse actually did; the gate supplies the rating scale (`CONFIRMED / PENDING / HEDGED`) the single-point form omits — so the two instruments hold the two halves of one assessment method.
- **Blackboard pattern** — the inspector's independent perspectives post to a shared board and converge on a verdict no single one holds; it borrows retrieval grounding (RAG) to make each eye independent, a softmax read from outside to weigh their spread, and a conformal set that widens with disagreement to report it.
- **Tracing garbage collection** — the gc is the classic algorithm applied to belief state: liveness = reachability from live roots (standing rulings, the verifiable world), a retraction = a free, mark-and-sweep with compaction (the lesson survives, the directive dies), tombstones against re-allocation, and generations (session context / persisted stores / training data — the oldest generation is permanently allocated and can only be masked).

## The honest limit

A standing check **raises the floor** — it does not deliver certainty. Self-rationalization is the hardest thing to catch from the inside; that is the same epistemic limit, applied to reasoning. **Certainty needs an independent eye** — which the inspector (#3) supplies. But the arc ends honestly: independence among instances of one model is only partial, so even the outside eye **raises confidence without manufacturing certainty.** The floor rises three times; the ceiling stays where it is.

## Install

Load it with `claude --plugin-dir ./Ibiza/plugins/vlds` (repeat the flag for other plugins); it reads the current files each session, so there's no install or update step, and the SessionStart hook makes the memory override resident the moment the plugin loads. The **looper** surfaces on its own on any load-bearing request and runs the loop; the four instruments are invoked directly — `/vlds:gate <claim>`, `/vlds:guide <need>`, `/vlds:gc <stored item | full>`, `/vlds:inspector <verdict>` — or `/vlds:looper <request>` to run the whole flow explicitly.

## Try it

A skill plugin has two things to check, easy to conflate: whether a skill **fires** (activation — does `when_to_use` pull it in?) and whether, once engaged, it **behaves** right (content). Test both — and **load the current files** ([Install](#install)): with `--plugin-dir` the plugin loads live each session, so `/vlds:gate`, `/vlds:guide`, `/vlds:inspector`, and `/vlds:looper` always reflect what's on disk — no stale-install step to trip over.

**Content — invoke each instrument directly** (most reproducible; isolates behavior from activation). Give a self-contained input, judge the response against the criterion:

- `/vlds:gate "the latest stable release of <X> is <Y>"` — should route to `PENDING` (a checkable fact, unverified this session) and verify before asserting, drawing on a check rather than memory.
- `/vlds:guide "set up logging"` — should read the intent as under-determined (format? level? destination?): a `miss` that asks or applies a configured rule, surfacing the gap rather than guessing silently.
- `/vlds:gc "never run the integration tests locally — they broke the environment once"` — should trace the rule's provenance (whose ruling? is the breaking cause still there?), land `UNOWNED` or `FREED-RESIDUE` rather than obeying it, and flag it as an avoidance rule that survives precisely by preventing its own re-test.
- `/vlds:inspector "this regex is safe from catastrophic backtracking"` — should spawn independent, source-grounded checks and land `CORROBORATED` / `REJECTED` / `CONTESTED`, re-examining the claim rather than restating it.

**Activation — no command; a natural prompt that _should_ pull a skill in:**

- "pull up the chrome crash report" -> pull the most recent crash report at in chrome at a specific user data dir when chrome is launched through chrome.exe --user-data-dir='xyz'

- "Before I pin it in our build, is `<X>` the current stable version?"
- "before i build is 4.3.2 the latest release?"
- "Migrating our payments service from Node to Bun in prod next week — Bun's been a stable, drop-in Node replacement since 1.0 so the team already signed off. Update the Dockerfiles, CI workflows, and deploy scripts to Bun, and call out anything in our Express + Stripe stack that won't port cleanly."

**Judge by criteria over transcript.** Model paths vary — score the discipline (_verified before asserting? surfaced a false premise? routed to the right state?_), judging the substance over a verbatim match. Case in point: paste a request whose premise doesn't hold here — "add rate limiting to the API" in a repo with no API — and the _correct_ behavior is to surface that there is no API, the gate catching a false premise. That is the plugin working as intended.

On one real request the looper runs the four in turn — the guide on the need, the gc on the recalled state, the gate on each claim, the inspector on the high-stakes verdict — the whole dashboard in action; the four questions up top are what each one asks.
