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
- **Register:** `<working dir>/.claude/vlds/src/frags.md` — one entry per frag in the shape its header declares (`frag`, `time`, `task`, `run`, `state`). The SessionStart hook seeds it and never overwrites it.
- **Header comment:** every frag opens with the task it completes, the date copied from the hook stream's `now:`, and the exact command that runs it from the project root.

## The procedure

1. **Before writing:** read `src/frags.md`. A frag that already covers the labor is updated in place; its register entry's `time:` and `state:` move with it.
2. **Writing:** the file goes under `src/<task-slug>/`; the register entry is appended before the first run, `state: live`.
3. **Running:** run it from the project root with the registered command. Dry-run flags first when the frag deletes, moves, or rewrites anything.
4. **When execution is refused by the harness:** do not rewrite the frag, do not reroute the call through another tool or agent to get past the refusal. The frag is already where the user can run it: hand the registered command in ONE fenced block, mark the entry `state: handed-off`, and say plainly what was and was not run.
5. **When the user edits a frag:** the edit is a ruling. Re-read the file before running or updating it; never overwrite it from memory or from an earlier copy.
6. **When the task is done for good:** mark the entry `state: retired`. Delete nothing; the user disposes of frags.

## The gate

The plugin's `PreToolUse` hook (`hooks/frag_gate.py`) asks before a Write, Edit, Bash, or PowerShell call writes a code file to a temp location — the session scratchpad, `/tmp`, the user's temp directory. It asks, never denies: a truly throwaway probe may proceed, and only the agent knows which this one is. Markdown and data files in the scratchpad pass; code under the project tree passes.

## Relation to vlds

src-fragger shares the VLDS store and nothing else. The vlds `pre-write` hook does not concern itself with `src/` (no store file name lives there), and `phi.py check` does not scan it. A frag's provenance — which ruling asked for it, which session wrote it — belongs in the store's own files, not in the frag.
