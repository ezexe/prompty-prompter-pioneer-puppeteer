# src-fragger — code the agent writes to finish a task lives in the tracked store, not the ignored scratchpad

A small plugin with one rule, one split, one floor, and one gate: every piece of code the agent authors to complete a task — a sweep, a migration, a probe, a generator, a harness page, a workflow script, anything that replaces manual, user-involved labor with a program the agent builds and runs, and whose job no single tool call does — is a **frag**, and a frag is written to the VLDS store's `src/` directory, registered in `src/frags.md`, and never to a scratchpad or a temp directory.

## The split

Two homes under the project's `.claude/`, one axis — worth, not file type:

- **`.claude/scratchpad/` is the notebook, and it is always git-ignored.** Notes, plans, commit messages, fixtures, logs, captured output, downloaded sources kept for reading. The SessionStart hook seeds a `.gitignore` of `*` inside it, so it ignores itself wherever the project's root `.gitignore` stands; a note there is never committed and costs nothing.
- **`.claude/vlds/src/` is the store's src, and it is git-tracked.** Every reusable and worthwhile output of the work — code or not, whatever someone will run, read, or edit again — lives there and rides in the project's history. The frags are registered; a design landed as a page, a sheet or a README lives beside them under the task's directory, unregistered.

What the work produced on the way stays in the notebook; what it produced that is worth keeping — what a later task runs or edits, what a commit is about to carry — graduates to `src/`: moved, registered, a one-line pointer left behind. A reading a claim cites stays a note; the claim's own entry carries what was read, and the instrument that produced the reading is the output. Nothing in the notebook is force-added to git: a note that seems to need committing is an output that needs moving. A truly throwaway probe — run once to answer a question and never again — may stay in the notebook after the gate's ask; the ask exists because "throwaway" is what every kept script called itself first.

## Why

There are three places agent-written code can land, with three lifetimes:

- **The harness's per-session scratchpad dies with the session.** Code there is invisible to the user, rewritten from scratch by the next task that needs it, and unreachable when it matters most — when the harness refuses the agent's own execution and the user has to run it, a file in a temp directory named after a session id is not something a user can be asked to find.
- **The project's notebook outlives the session but lives on one disk only.** Ignored, never in the project's history — the right lifetime for a build log, the wrong one for the harness that read it.
- **A frag under `<working dir>/.claude/vlds/src/<task>/` outlives the session, is the user's to open and edit (an edit is a ruling), rides in the project's history, and when execution is refused the hand-off is one registered command.**

## The floor

A frag is measured by its job, not by its length.
An exact-match replacement is an Edit call; an append, a store row, or a whole-file write is a Write call; one shell command is a Bash call — and none of these is a frag, however long the text.
The script that does one of those jobs anyway is the tool call in costume, written nearly always because a heredoc failed on the text's backslashes, quotes, or `$`; the fallback from a failing heredoc is the dedicated tool, never a script that does the tool's job.
Such a script is worse than the call it replaces — it keys on text that moves, lands twice when its new text contains its old, and carries a header, a register entry, a state, and a retirement the call never needed — and a per-turn record is a Write call for a second reason: a frag is kept to be run again, and a record written once never is.

## What ships

- [`hooks/src-fragger.md`](hooks/src-fragger.md) — the contract, injected at every SessionStart by [`hooks/session-open.sh`](hooks/session-open.sh), which also creates `store/src/` and the notebook, seeds the register from [`hooks/frags-seed.md`](hooks/frags-seed.md) and the notebook's `.gitignore` of `*` when absent (never overwriting either — a user's edit is a ruling), and prints one notice line when the project's root rules git-ignore `src/` itself (the hook never edits the root `.gitignore` and never touches the index).
- [`hooks/frag_gate.py`](hooks/frag_gate.py) — the `PreToolUse` gate, run through [`hooks/run-hook.sh`](hooks/run-hook.sh): asks before a Write, Edit, Bash, or PowerShell call writes ANY file into the harness's per-session scratchpad, a code file (by extension, a page included, or by a name such as `CMakeLists.txt`) to any other temp location (`/tmp`, the user's temp directory), or a code file to any project's `.claude/scratchpad/` (that ask carries the split and the floor; a page or source captured from elsewhere and kept for reading is a note and may proceed). Asks, never denies. The same script's `register-lint`, the third SessionStart command, prints one line when `src/` holds code the register does not name or the register names a path that is gone and not retired. Acceptance tests for the gate, the lint and the SessionStart hook in [`hooks/test_frag_gate.py`](hooks/test_frag_gate.py).
- [`skills/frag`](skills/frag/SKILL.md) — the procedure: the split, the floor, reuse before rewrite, the header comment, the register shape, the double-check before any hand-off, the user's edits as rulings, graduation from the notebook, retirement without deletion. Direct-invoke (`/src-fragger:frag`); the hook carries the residency.

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
