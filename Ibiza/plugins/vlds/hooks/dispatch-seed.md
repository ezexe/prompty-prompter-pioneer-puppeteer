# VLDS Partition — Dispatch

One entry per message this session has addressed: how it arrived, what was done about it, and whether a later message freed it.
Consulted by the **dispatch barrier** as the thought stream forms — _is this message new, or am I answering it twice?_ — before a response is committed to.
One shared file: at a new session's first turn the model pours every entry already here into `arc/` (verbatim, verified, then trimmed) and the dispatcher starts fresh — a resume keeps its own; entries are never promoted to a standing rule.

States: `FRESH` (no match — address it, then record it) · `ECHO` (already addressed, unchanged — answer the delta, never the whole message again) · `SUPERSEDED` (addressed, then freed by a later message — surface the free; acting on it is a use-after-free).
When a match is uncertain, default to `FRESH`: re-answering wastes a turn, but wrongly suppressing drops the user's request entirely, and only one of those is recoverable.

Append one entry per message, in this shape:

```yaml
- fingerprint: [the opening clause plus the ask, enough to recognize it again]
  time: [YYYY-MM-DD HH:MM]
  arrival: turn | mid-turn interleave | hook injection | summary replay | task notification
  state: FRESH | ECHO | SUPERSEDED
  addressed: [what was actually done about it]
  match: [what justified an ECHO or SUPERSEDED call]
  freed-by: [the later message that superseded it]
```

---
