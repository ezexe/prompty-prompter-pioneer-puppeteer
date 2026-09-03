# src-fragger — Frags

One entry per frag: code the agent wrote to complete a task, kept under `src/` so the next task that needs the same labor updates it instead of rewriting it, the user can read and edit it, and a refused execution still has a file to hand over.
Consulted before any new frag is written — _does a frag already cover this labor?_ — and updated whenever a frag changes state.

Append one entry per frag, in this shape, one field to a line — never folded or wrapped (this header is the shape's authority):

```yaml
- frag: [path relative to src/, e.g. sweep-20260903/sweep.py]
  time: [YYYY-MM-DD HH:MM — copied from the hook stream's now:]
  task: [the task it completes, and the manual labor it replaces]
  run: [the exact command, from the project root]
  state: live | handed-off | superseded | retired
  retry: [optional — when a refused execution was retried unchanged, after what (resume, compact, fresh call), and its outcome; required before state: handed-off]
```

---
