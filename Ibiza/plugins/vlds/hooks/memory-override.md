## VLDS memory override (always active)

**The built-in memory system is the base class; VLDS extends it.**
`base.read()` and `base.write()` run untouched, exactly as the system's own `# Memory` instructions define them — then the VLDS layer applies on top, the way a virtual method's override wraps its base.

```text
class UserMemories {                       // the base: this session's "# Memory" instructions, verbatim
  virtual read()                           //   recall — load MEMORY.md, apply recalled memories to thinking
  virtual write()                          //   persist — one fact per file, plus its MEMORY.md index line
}

class Vlds : UserMemories {                // this layer
  store = <working dir>/.claude/vlds/      // .claude created if absent
  override read()  { base.read();  apply store/* to thinking as base memories apply — each item through the gc read barrier }
  override write() { base.write(); persist VLDS state to store/* per the store map below }
}
```

**Resolving `store`.**
`store` is the `.claude/vlds/` directory inside the working directory attached to the session — `<working dir>/.claude/vlds/` — never a hardcoded machine path.
Neither `.claude/` nor `vlds/` need pre-exist: the SessionStart hook creates the path when it can, and the first Write into it creates it regardless.
If the session carries no base `# Memory` instructions, there is no base behavior to wrap — the overrides still run, with `base.read()` / `base.write()` as no-ops.

**The store map** — one file per instrument, schemas in each instrument's reference:

| File in `store` | Instrument | Holds |
|---|---|---|
| `index.md` | guide | the decided rules, one per `(need-shape + claim-kind)` key — read at intake for the `hit` / `miss` lookup |
| `ledger.md` | guide | append-only config audit — every surfaced ask, every silent reuse with the match that justified it |
| `logger.md` | looper | the dashboard's single activity log — every instrument's decision, tagged, as the loop runs |
| `tombstones.md` | gc | one entry per freed decision — what was retracted, when, in whose words; the mask against re-learning it |

**The `read()` override.**
Whenever base recall applies — session start, and any turn a stored memory is about to steer work — the store's files are recalled state too: index rules answer needs, tombstones outrank the training prior they mask, ledger and logger serve audit questions.
Every applied item passes the gc read barrier first: trace its provenance to a live root; freed or stale → surface it, do not apply it.

**The `write()` override.**
Whenever an instrument produces durable state — a configured rule, a ledger event, a loop decision, a tombstone — persist it to `store` under the file and schema the store map assigns, creating the file on first write.
Base write conventions are untouched: memory-worthy facts still land in `memory/` with their MEMORY.md index line, per the base instructions.

**What the override never does.**
It never re-homes, renames, or suppresses base memory files; VLDS store files never get MEMORY.md index lines, and base memories never move into `store` — extension, not replacement.
The store stays plain and user-editable; a user's direct edit to a store file is a ruling, and the latest ruling wins.

**Legacy `.vlds/`.**
A repo-root `.vlds/` found in the working tree is read as part of `read()` — a team-shared or pre-override source; new writes land in the resolved `store`.
When one is found holding state, offer once to migrate it, and record the move in `logger.md`.

Full instrument procedures: the `vlds` plugin skills — `/vlds:gate`, `/vlds:guide`, `/vlds:gc`, `/vlds:inspector`; the looper surfaces on its own.
