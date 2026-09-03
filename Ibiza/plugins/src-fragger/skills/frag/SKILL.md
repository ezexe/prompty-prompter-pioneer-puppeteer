---
name: frag
description: "src-fragger — the procedure for frags: code the agent writes to complete a task, kept under the VLDS store's src/ directory and registered in src/frags.md so it outlives the session, can be reused and updated instead of rewritten, can be edited by the user (an edit is a ruling), and is already in the user's hands when the harness refuses the agent's own execution. Use when about to write a script or program to complete a task, when a task repeats labor a frag may already cover, when an execution was refused, or to list, update, hand off, or retire a frag."
argument-hint: "[list | new <task-slug>/<name.ext> | update <frag> | handoff <frag> | retire <frag>]"
disable-model-invocation: true
---

# frag — code the agent writes to finish a task, kept where it can be reused, edited, and run

> The scratchpad is a convenience for the agent and a loss for everyone else.
> A frag is the same code written where it survives the session, where the user can read and change it, and where it can still be run when the agent cannot run it.

## What a frag is

Any code the agent authors to complete a task rather than to ship as product: a sweep, a migration, a probe, a generator, a bulk edit, a verification harness — anything that replaces manual, user-involved labor with a script the agent builds and executes.
Product code is not a frag; it belongs in the project tree under the project's own conventions.
Notes, plans, and data files are not frags either; they may live in the scratchpad.

## Where it lives

- **Directory:** `<working dir>/.claude/vlds/src/<task-slug>/` — one directory per task, inside the VLDS store, so it rides with the store's other state and stays out of the project tree and out of version control with it.
- **Register:** `<working dir>/.claude/vlds/src/frags.md` — one entry per frag in the shape its header declares (`frag`, `time`, `task`, `run`, `state`, and `retry` once a refusal has been retried). The SessionStart hook seeds it and never overwrites it.
- **Header comment:** every frag opens with the task it completes, the date copied from the hook stream's `now:`, and the exact command that runs it from the project root.

## The procedure

1. **Before writing:** read `src/frags.md`. A frag that already covers the labor is updated in place; its register entry's `time:` and `state:` move with it.
2. **Writing:** the file goes under `src/<task-slug>/`; the register entry is appended before the first run, `state: live`.
3. **Running:** run it from the project root with the registered command. Dry-run flags first when the frag deletes, moves, or rewrites anything.
4. **When execution is refused by the harness — double-check before interrupting the user.** An interruption costs the user the labor the frag exists to remove, so it is the last resort, and four things are verified first:
   - the frag is under `src/` and registered, so the hand-off would be one click, not a search through a temp directory;
   - the refusal is durable: the SAME call is retried once, unchanged, after a resume, a compact, or in a fresh tool call — a refusal announced "for the rest of this conversation" is bound to the process that announced it, and one did not survive a resume;
   - the user's word already covers the act: a word given once in the conversation still stands, and a retry needs no new one;
   - the interruption is a decision only the user can make, not labor the agent could still do.
   The retry and its outcome go in the register entry's `retry:` field. Only then: hand the registered command in ONE `bash`-tagged fence, one command per fence so the chat can run it on click, mark the entry `state: handed-off`, and say plainly what was and was not run. Never rewrite the frag, and never reroute the call through another tool or agent to get past a refusal — a retry is the same call again, nothing else.
5. **When the user edits a frag:** the edit is a ruling. Re-read the file before running or updating it; never overwrite it from memory or from an earlier copy.
6. **When the task is done for good:** mark the entry `state: retired`. Delete nothing; the user disposes of frags.

## The gate

The plugin's `PreToolUse` hook (`hooks/frag_gate.py`) asks before a Write, Edit, Bash, or PowerShell call writes a code file to a temp location — the session scratchpad, `/tmp`, the user's temp directory. It asks, never denies: a truly throwaway probe may proceed, and only the agent knows which this one is. Markdown and data files in the scratchpad pass; code under the project tree passes.

## Relation to vlds

src-fragger shares the VLDS store and nothing else. The vlds `pre-write` hook does not concern itself with `src/` (no store file name lives there), and `phi.py check` does not scan it. A frag's provenance — which ruling asked for it, which session wrote it — belongs in the store's own files, not in the frag.
