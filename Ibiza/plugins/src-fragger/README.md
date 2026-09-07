# src-fragger — code the agent writes to finish a task lives in the store, not the scratchpad

A small plugin with one rule, one floor, and one gate: every piece of code the agent authors to complete a task — a sweep, a migration, a probe, a generator, anything that replaces manual, user-involved labor with a script the agent builds and runs, and whose job no single tool call does — is a **frag**, and a frag is written to the VLDS store's `src/` directory, registered in `src/frags.md`, and never to the session scratchpad or a temp directory.

## Why

The agent's scratchpad is session-scoped and temporary. Code written there has three failure modes, all observed:

- **It dies with the session.** The next task that needs the same labor rewrites it from scratch, with new mistakes.
- **The user never sees it.** A script that reshapes the user's own state is invisible to the one party who could read and correct it.
- **It is unreachable when it matters most.** When the harness refuses the agent's own execution of the script, the only recovery is for the user to run it — and a file in a temp directory named after a session id is not something a user can be asked to find.

A frag under `<working dir>/.claude/vlds/src/<task>/` fixes all three: it outlives the session, the user can open and edit it (an edit is a ruling), and when execution is refused the hand-off is one registered command.

## The floor

A frag is measured by its job, not by its length.
An exact-match replacement is an Edit call; an append, a store row, or a whole-file write is a Write call; one shell command is a Bash call — and none of these is a frag, however long the text.
The script that does one of those jobs anyway is the tool call in costume, written nearly always because a heredoc failed on the text's backslashes, quotes, or `$`; the fallback from a failing heredoc is the dedicated tool, never a script that does the tool's job.
Such a script is worse than the call it replaces — it keys on text that moves, lands twice when its new text contains its old, and carries a header, a register entry, a state, and a retirement the call never needed — and a per-turn record is a Write call for a second reason: a frag is kept to be run again, and a record written once never is.

## What ships

- [`hooks/src-fragger.md`](hooks/src-fragger.md) — the contract, injected at every SessionStart by [`hooks/session-open.sh`](hooks/session-open.sh), which also creates `store/src/` and seeds the register from [`hooks/frags-seed.md`](hooks/frags-seed.md) when absent (never overwriting it).
- [`hooks/frag_gate.py`](hooks/frag_gate.py) — the `PreToolUse` gate, run through [`hooks/run-hook.sh`](hooks/run-hook.sh): asks before a Write, Edit, Bash, or PowerShell call writes ANY file into the harness's per-session scratchpad, a code file (by extension) to any other temp location (`/tmp`, the user's temp directory), or a code file to any project's `.claude/scratchpad/` (that ask carries the floor). Asks, never denies. Acceptance tests in [`hooks/test_frag_gate.py`](hooks/test_frag_gate.py).
- **Working files that are not code** go under the project's own `.claude/scratchpad/`, created by the SessionStart hook: the harness's temp scratchpad is named after a session id, invisible to the user, and gone with the session, so nothing lives there. Code never goes to a scratchpad: a script there is neither a frag nor a tool call, and the gate asks.
- [`skills/frag`](skills/frag/SKILL.md) — the procedure: the floor, reuse before rewrite, the header comment, the register shape, the double-check before any hand-off, the user's edits as rulings, retirement without deletion. Direct-invoke (`/src-fragger:frag`); the hook carries the residency.

## Before interrupting the user

A hand-off costs the user exactly the labor the frag exists to remove, so it is the last resort, and the contract makes the agent verify four things first: the frag is registered under `src/` (one click, not a search); the refusal is durable — the same call is retried once, unchanged, in a fresh tool call, because a refusal announced "for the rest of this conversation" is bound to the conversation's content rather than the process: a fresh tool call has passed where the first was refused, a fresh conversation opened with a hand-off summary clears it, and a resume of the same conversation does not; the user's word already given still covers the act; and the interruption is a decision only the user can make rather than labor the agent could still do. The retry is recorded in the register's `retry:` field, and `state: handed-off` is not written without it. When the hand-off does happen it is one `bash`-tagged fence per command, written for the user's own shell, so the chat can run it on click — the click runs in the user's terminal, not the agent's.

## The register

`store/src/frags.md`, one entry per frag:

```yaml
- frag: [path relative to src/]
  time: [YYYY-MM-DD HH:MM — copied from the hook stream's now:]
  task: [the task it completes, and the manual labor it replaces]
  run: [the exact command, from the project root]
  state: live | handed-off | superseded | retired
```

## Relation to vlds

src-fragger shares the VLDS store (`<working dir>/.claude/vlds/`) and nothing else. The vlds plugin's `pre-write` gate ignores `src/` (no store file name lives there) and its `phi.py check` does not scan it; a frag's provenance — which ruling asked for it, which session wrote it — belongs in the store's own files, never in the frag, so the frag stays portable.

## Install

Add the marketplace and install at user level — `/plugin marketplace add <path-or-url-of>/Ibiza` then `/plugin install src-fragger@p4-marketplace` — which activates both hooks in every repo. For a single session, `claude --plugin-dir ./Ibiza/plugins/src-fragger`.
