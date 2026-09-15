---
name: frag
description: "src-fragger — the procedure for frags: code the agent writes to complete a task whose job no single tool call does (an edit, an append, a whole-file write, or one shell command is the tool's own call, never a frag), kept under the VLDS store's src/ directory — the git-tracked home of the work's reusable and worthwhile outputs, beside the project's always-ignored .claude/scratchpad/ notebook — and registered in src/frags.md so it outlives the session, can be reused and updated instead of rewritten, can be edited by the user (an edit is a ruling), and is already in the user's hands when the harness refuses the agent's own execution. Use when about to write a script or program to complete a task, when a task repeats labor a frag may already cover, when a notebook file turns out to be worth keeping, when an execution was refused, or to list, update, hand off, or retire a frag."
argument-hint: "[list | new <task-slug>/<name.ext> | update <frag> | graduate <notebook-file> | handoff <frag> | retire <frag>]"
disable-model-invocation: true
---

# frag — code the agent writes to finish a task, kept where it can be reused, edited, run, and tracked

> A scratchpad is a convenience for the agent and a loss for everyone else.
> A frag is the same code written where it survives the session, where the user can read and change it, where it can still be run when the agent cannot run it — and where the project's history carries it.

## What a frag is

Any code the agent authors to complete a task rather than to ship as product: a sweep, a migration, a probe, a generator, a bulk edit, a verification harness, a harness page, a workflow script, a probe project's build files — anything that replaces manual, user-involved labor with a program the agent builds and executes.
Product code is not a frag; it belongs in the project tree under the project's own conventions.
Notes, plans, logs, captured output, fixtures, and downloaded sources kept for reading are not frags either; they live in the notebook, the project's git-ignored `.claude/scratchpad/`.
A worthwhile output that is not code — a design landed as a page, a sheet or README a later task reads — is not a frag but lives beside the task's frags under `src/<task-slug>/`, tracked: the register names the frags, the directory carries the rest.
A truly throwaway probe — run once to answer a question and never again — may stay in the notebook after the gate's ask; the ask exists because "throwaway" is what every kept script called itself first.

## The split

Two homes, one axis — worth, not file type.
The **notebook**, `<working dir>/.claude/scratchpad/`, is always git-ignored: the SessionStart hook seeds a `.gitignore` of `*` inside it, so it ignores itself wherever the project's root `.gitignore` stands, and a note there is never committed and costs nothing.
The **store's `src/`**, `<working dir>/.claude/vlds/src/`, is git-tracked: every reusable and worthwhile output of the work — code or not, whatever someone will run, read, or edit again — lives there and rides in the project's history.
What the work produced on the way stays in the notebook; what it produced that is worth keeping graduates to `src/`.
A reading — a log, a capture, a report — stays a note even when a claim cites it: the claim's own store entry carries what was read, and the instrument that produced the reading is the output that graduates.

## The floor

A frag is measured by its job, not by its length: it is code whose job no single tool call does.
An exact-match replacement is an Edit call; an append, a store row, or a whole-file write is a Write call; one shell command is a Bash call — none of these is a frag, however many lines the text runs to.
A script that reads a file, swaps a few literal spans, and writes it back is an Edit call in costume, written nearly always because a heredoc failed on the text's backslashes, quotes, or `$` — and the fallback from a failing heredoc is the dedicated tool, never a script that does the tool's job.
Such a script is worse than the call: it keys on text that moves, it lands twice when its new text contains its old, and it carries a header, a register entry, a state, and a retirement the call never needed.
A per-turn record — store rows, a turn's completions — is a Write call for a second reason: a frag is kept to be run again, and a record written once never is.

## Where it lives

- **Directory:** `<working dir>/.claude/vlds/src/<task-slug>/` — one directory per task, inside the VLDS store, so it rides with the store's other state, out of the project tree and in version control: `src/` is the tracked home of the work's reusable outputs.
- **Register:** `<working dir>/.claude/vlds/src/frags.md` — one entry per frag in the shape its header declares (`frag`, `time`, `task`, `run`, `state`, and `retry` once a refusal has been retried). The SessionStart hook seeds it and never overwrites it.
- **Header comment:** every frag opens with the task it completes, the date copied from the hook stream's `now:`, and the exact command that runs it from the project root.
- **Working files that are not reusable outputs** — commit messages, plans, notes, fixtures, captured output, logs, downloaded sources kept for reading — go under the notebook, `<working dir>/.claude/scratchpad/`, which the SessionStart hook creates and seeds with its own `.gitignore`. The harness's per-session scratchpad (a temp path named after the session id) is never used for anything: it is invisible to the user and gone with the session.
- **Where the project's root rules ignore `.claude/` wholesale**, `src/` is not tracked either; the hook says so in one line at session start, and narrowing that rule is the user's edit — surfaced, never made for them. The hook never touches the index and never edits the root `.gitignore`; files a project committed into its notebook before the seed stay tracked until the user removes them from the index.

## The procedure

1. **Before writing:** the floor first — if one tool call does the job, make the call and write no file. Then read `src/frags.md`. A frag that already covers the labor is updated in place; its register entry's `time:` and `state:` move with it.
2. **Writing:** the file goes under `src/<task-slug>/`; the register entry is appended before the first run, `state: live`.
3. **Running:** run it from the project root with the registered command. Dry-run flags first when the frag deletes, moves, or rewrites anything.
4. **When execution is refused by the harness — double-check before interrupting the user.** An interruption costs the user the labor the frag exists to remove, so it is the last resort, and four things are verified first:
   - the frag is under `src/` and registered, so the hand-off would be one click, not a search through a temp directory;
   - the refusal is durable: the SAME call is retried once, unchanged, in a fresh tool call — a refusal announced "for the rest of this conversation" is bound to the conversation's content, not the process that announced it: a fresh tool call has passed where the first was refused, a fresh conversation opened with a hand-off summary clears it, and a resume of the same conversation does not;
   - the user's word already covers the act: a word given once in the conversation still stands, and a retry needs no new one;
   - the interruption is a decision only the user can make, not labor the agent could still do.
   The retry and its outcome go in the register entry's `retry:` field. Only then: hand the registered command in ONE `bash`-tagged fence, one command per fence so the chat can run it on click — written for the user's own shell, since the click runs there and not in the agent's — mark the entry `state: handed-off`, and say plainly what was and was not run. Never rewrite the frag, and never reroute the call through another tool or agent to get past a refusal — a retry is the same call again, nothing else.
5. **When the user edits a frag:** the edit is a ruling. Re-read the file before running or updating it; never overwrite it from memory or from an earlier copy.
6. **When a notebook file turns out to be worth keeping** — a later task runs or edits it, the user edits it, or a commit is about to carry it: it is an output, not a note. Move it to `src/<task-slug>/`, register it, and leave a one-line pointer where the notebook refers to it. A reading a claim cites is not made an output by the citation: the claim's own entry carries what was read, and the instrument that produced the reading is the output. Nothing in the notebook is force-added to git; a note that seems to need committing is an output that needs moving.
7. **When the task is done for good:** mark the entry `state: retired`. Delete nothing; the user disposes of frags.

## The gate

The plugin's `PreToolUse` hook (`hooks/frag_gate.py`) asks before a Write, Edit, Bash, or PowerShell call writes a code file — by extension, a page (`.html`) included, or by a name such as `CMakeLists.txt` or `Makefile` — to a temp location (the session scratchpad, `/tmp`, the user's temp directory) or to any project's `.claude/scratchpad/`, where a swap script lands once it has stopped calling itself a frag; that ask carries the split and the floor. It asks, never denies: a truly throwaway probe may proceed, a page or source captured from elsewhere and kept for reading is a note, and only the agent knows which this one is. Markdown, logs, and data files in a notebook pass; code under the project tree and under `src/` passes.

The same script's `register-lint` runs at every SessionStart: one line when `src/` holds code the register does not name, or the register names a path that is gone without a retired, superseded, moved or deleted state — silent otherwise. Non-code files beside a task's frags are never expected in the register.

## Relation to vlds

src-fragger shares the VLDS store and nothing else. The vlds `pre-write` hook does not concern itself with `src/` (no store file name lives there), and `phi.py check` does not scan it. A frag's provenance — which ruling asked for it, which session wrote it — belongs in the store's own files, not in the frag.
