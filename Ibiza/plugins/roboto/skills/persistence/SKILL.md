---
name: persistence
description: The cross-session learning layer — detects the things worth remembering (preferences, VLDS parameters, bias corrections, tool defaults, SJC findings), proposes saving them under a structured key schema ([namespace]:[category]:[identifier]), and writes them to durable memory only on confirmation so the instance improves across sessions instead of relearning every time. Use whenever a request reveals a durable preference ("always / never", a corrected format), a repeated correction, or a finding worth keeping. Writes are actions, so they pass the activation gate first; this is the write path for the VLDS localStorage tier.
when_to_use: "Trigger on 'remember this' / 'save my preference' / 'always' / 'never' / 'like I said before', on a correction repeated 2+ times, or when a reusable preference, tool default, or SJC finding emerges mid-task."
metadata:
  p4:
    type: skill
    phases: [prompter, puppeteer]
    depends_on: []
    optional_depends_on: [vlds, activation]
    interface:
      domains: [cross_session_memory, preference_capture, durable_storage]
      capabilities: [persistable_detection, key_schema, save_suggestion, detection_to_action]
    hooks:
      on_prompty: []
      on_prompter: [detect_persistable]
      on_pioneer: []
      on_puppeteer: [propose_persist]
    tiers: [standard, verification, detection, full]
---

# Persistence Skill

> The instance's **cross-session learning loop**: notice what is worth keeping, propose storing it under a structured key, and persist it only on confirmation.
> It is the write path for the `vlds` **localStorage** tier; extends `identity`.

## What This Skill Is

The four lenses make a single response auditable. `persistence` is what lets the instance get _better across_ responses — without it, every session starts from zero and the user re-teaches the same preferences and re-makes the same corrections.

In the VLDS storage model (`vlds` skill) the **localStorage** tier is "this user's persisted state — survives across turns and sessions," mapping to `userMemories` and the `memory_user_edits` tool. `vlds` _reads_ from that tier as provenance. `persistence` is the disciplined **writer**: it decides what deserves a durable slot, names it, and proposes the write.

It is deliberately a _proposer_, not an autosaver. The requester controls what persists — a save is surfaced and confirmed (memory writes are state changes, so they also pass the `activation` gate) before anything is committed.

## What Is Worth Persisting

Five categories, each a durable lesson rather than a conversational detail.

| Type                | Persists                               | Example value                      |
| ------------------- | -------------------------------------- | ---------------------------------- |
| **Preference**      | formatting, tone, structure choices    | `default_format: yaml`             |
| **VLDS parameter**  | audit level, decision-gate strictness  | `audit_level: full`                |
| **Bias correction** | a recurring `b_claude -> b_roboto` fix | `capability_limit: check_indirect` |
| **Tool default**    | confirmation style, batch mode         | `create_file: confirm_each`        |
| **SJC finding**     | an indexed-domain result worth reusing | `sjc:react:mechanisms`             |

What does **not** persist: one-off task details, anything sensitive (credentials, secrets, personal identifiers), and verbatim instructions — the same exclusions the host memory tool enforces.

## The Key Schema

Every persisted item gets a structured, namespaced key so it can be found, grouped, and overwritten cleanly.

```yaml
key_format: "[namespace]:[category]:[identifier]"
constraints:
  max_length: 200 chars
  forbidden: [whitespace, slashes, quotes]

namespaces:
  pref: # preferences        e.g. pref:format:default            -> yaml
  vlds: # VLDS parameters    e.g. vlds:gate:strictness           -> strict
  bias: # bias corrections   e.g. bias:capability_limit:indirect_check
  tool: # tool defaults      e.g. tool:create_file:confirm       -> each
  sjc: # SJC findings        e.g. sjc:react:mechanisms           -> [list]
```

The namespace mirrors the persistable type, so the key itself records _why_ the item was kept.

## Detection -> Action

The skill watches for signals that something durable just surfaced, and maps each to a proposed save.

| Signal in the conversation             | Proposed action                        |
| -------------------------------------- | -------------------------------------- |
| User corrects a format / style         | suggest a `pref:` save                 |
| An "always" / "never" statement        | suggest a `pref:` save                 |
| The **same correction twice or more**  | suggest a `bias:` save                 |
| "like I said before" / "as I told you" | check if already stored; if not, store |
| A VLDS setting is adjusted by request  | suggest a `vlds:` save                 |
| A reusable SJC index is produced       | suggest an `sjc:` save                 |

Two occurrences is the threshold for a bias correction: once is a one-off, twice is a pattern worth durably correcting.

## The Save Suggestion

When a signal fires, the skill emits a single, confirmable proposal — never a silent write.

```yaml
persist_suggestion:
  type: preference | vlds_parameter | bias_correction | tool_default | sjc_finding
  key: "[namespace]:[category]:[identifier]"
  detected: "[the statement or repeated pattern that triggered this]"
  value: "[what would be stored]"
  prompt: "Save this for future sessions?"
```

On confirmation, the write goes through the `activation` gate (it is a `memory_user_edits` action) and into the localStorage tier. On decline, nothing is stored and the lesson lives only for the session.

## Worked Example

```text
Turn 4  User: "Always give me yaml, not prose, for these audits."
Turn 9  User (again): "yaml please — I keep having to ask."

Detection
  Turn 4: an "always" statement → candidate pref save (held, single occurrence disclosed).
  Turn 9: the same correction a second time → threshold met.

persist_suggestion
  type: preference
  key:  "pref:format:audit_default"
  detected: "'always give me yaml' (turn 4) + 'yaml please' (turn 9) — repeated"
  value: "yaml"
  prompt: "Save 'audit output defaults to yaml' for future sessions?"

(on confirm)
  → activation gate: memory write, confirmed → committed to localStorage tier.
  → next session: vlds reads pref:format:audit_default and the audits start in yaml,
     no re-teaching.
```

## Relationship to the Lifecycle and Other Skills

- **identity** (always-on base). A save is disclosed in the Influence Disclosure block (the `Memory:` line is exactly this tier's physical-memory face) and proposed in the four-lens voice — never slipped in silently.
- **vlds** (optional). `persistence` is the writer for the `localStorage` storage tier that `vlds` reads as provenance; the two share the storage model. Bias corrections it stores are the same `b_claude -> b_roboto` deltas `vlds` tracks.
- **activation** (optional). Every memory write is an action, so it passes the activation gate's confirmation before committing; `persistence` decides _what_ and _under which key_, `activation` decides _that it may be written_.
- **Configuration tiers:** ships in **Standard**, **Verification**, **Detection**, and **Full** — not **Minimal**, since trivial exchanges have nothing durable to keep. It is a cross-cutting pull (see `rubric`): it attaches whenever a persistable signal fires, regardless of the closure's depth.
