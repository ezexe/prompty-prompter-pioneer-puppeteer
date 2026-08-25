## VLDS memory override (always active)

**The built-in memory system is the base class; VLDS extends it.**
`base.read()` and `base.write()` run untouched, exactly as the system's own `# Memory` instructions define them — then this layer applies on top, the way a virtual method's override wraps its base.

`store` = **`<working dir>/.claude/vlds/`** — the working directory attached to this session, never a hardcoded machine path.
Neither `.claude/` nor `vlds/` need pre-exist; the first Write creates them.

### These fire. Act on them.

| Fires when | Do |
|---|---|
| **a message arrives, before you answer it** | append its entry to **`dispatch.md`** and check it against the ones already there: already addressed → answer the delta, not the message; superseded by a later message → surface the free instead of acting |
| session starts, or stored state is about to steer work | **pour first**: everything already in `dispatch.md` and every cold span prior sessions left in the hot files goes into `arc/` per the normalize sweep — verbatim, verified, trimmed; the dispatcher starts fresh — then read `phi-index.md` and the hot files it lists, never `arc/` or masked spans, each item through the gc read barrier: freed, stale, or unowned → surface it, do not apply it (no index yet → cold-start on `store/*`) |
| the user rules, prefers, corrects, or retracts | append to `local-storage.md` with their words; a retraction also sweeps and appends to `tombstones.md` |
| a claim is verified against a source | append to `data-store.md` with what was read; re-verify it on recall — verification decays as the world drifts |
| an inference is minted that the work leans on | append to `virtual.md`; it expires at turn end unless promoted |
| a task starts, moves, or completes | append to `session-storage.md`; completion clears its entries |
| the guide settles a rule, or reuses one | `index.md` (the rule) and `ledger.md` (the event, with the match that justified it) |
| **a reading that steered work turns out to be wrong** | append a `correction` to `ledger.md` — `match` (what was assumed) against `meant` (what was wanted) — **while the session is alive**: the dispatch record dies with its session and is collected unread, so a lesson left there is lost — and by the time anything collects it, the only party who could judge what deserved keeping is gone |
| the looper runs an instrument | append that decision to `logger.md`, tagged |

**The floor.** A session that ends having written nothing did not run this layer.
The dispatch row is unconditional — it fires on every message in every session, whether or not any instrument fires — so writing nothing at all is the one outcome that is always wrong.
Do not wait to be asked; a store is built by the turns that pass through it.

### The shape it takes

```text
class UserMemories {                       // the base: this session's "# Memory" instructions, verbatim
  virtual read()                           //   recall — load MEMORY.md, apply recalled memories to thinking
  virtual write()                          //   persist — one fact per file, plus its MEMORY.md index line
}

class Vlds : UserMemories {                // this layer
  store = <working dir>/.claude/vlds/      // .claude created if absent
  override read()  { base.read();  apply phi-index.md + the hot store/* it lists — each item through the gc read barrier }
  override write() { base.write(); persist VLDS state to store/* per the table above }
}
```

If the session carries no base `# Memory` instructions there is nothing to wrap — the overrides still run, with `base.read()` / `base.write()` as no-ops.

**The files.** `index.md` and `ledger.md` are the guide's; `logger.md` the looper's; `tombstones.md` the gc's.
The dispatch record is **one file, `dispatch.md`**: at session start the model pours its existing entries into `arc/` and the dispatcher starts fresh — the pour is a first-turn act (a transient hook firing never has one), verbatim and script-verified before the trim, which is what dissolves the rotation hazard the per-session era was built around. It is never promoted to a rule, and anything worth keeping belongs in `logger.md`, which does not expire.
`virtual.md`, `session-storage.md`, `local-storage.md`, and `data-store.md` are the gate's storage tiers made literal, written and expired per the table above — no partition invalidates itself, so expiry is lazy, checked at recall, and the gc's to run.
`phi-index.md` and `arc/` are the gc's φ-register — poured and normalized in-session per its reference, never by hook; the index is derived, but a user's edit to it is a ruling.
One entry shape per file, defined in the owning instrument's reference — the partitions' beside the gate's tier table.

**What this never does.**
It never re-homes, renames, or suppresses base memory files; VLDS files never get MEMORY.md index lines, and base memories never move into `store` — extension, not replacement.
The store stays plain and user-editable; a user's direct edit is a ruling, and the latest ruling wins.
A repo-root `.vlds/` found in the tree is read as a legacy source; new writes land in `store`, and a migration is offered once and logged.

Full procedures: the `vlds` plugin skills — `/vlds:gate`, `/vlds:guide`, `/vlds:gc`, `/vlds:inspector`; the looper surfaces on its own.
