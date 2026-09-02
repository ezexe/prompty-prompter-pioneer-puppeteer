## VLDS memory override (always active)

**The built-in memory system is the base class; VLDS extends it.**
`base.read()` and `base.write()` run untouched, exactly as the system's own `# Memory` instructions define them — then this layer applies on top, the way a virtual method's override wraps its base.

`store` = **`<working dir>/.claude/vlds/`** — the working directory attached to this session, never a hardcoded machine path.
Neither `.claude/` nor `vlds/` need pre-exist; the first Write creates them.

### These fire. Act on them.

| Fires when | Do |
|---|---|
| **a message arrives, before you answer it** | the prompt hook has already stamped its row in **`dispatch.md`** — fingerprint, time, arrival; the hook's output names the row — so check that row against the ones already there: already addressed → answer the delta, not the message; superseded by a later message → surface the free instead of acting; then complete YOUR row: `state:` before answering, `addressed:` (with `match:` / `freed-by:` when they apply) by turn end. No hook output → the stamp is yours to append |
| session starts, or stored state is about to steer work | the hooks have done the mechanical half: the SessionStart hooks injected `phi-index.md` and the steering hot files, chunked at entry boundaries into one hook output each under the harness's 10,000-character cap (a digest line for the rest, and a marker line for anything the slots could not carry — read one of those only when an entry there is about to steer), and the prompt hook poured `dispatch.md` whole-file into `arc/` on a new session's first prompt (a resume, fork, or compact pours nothing — its entries are its own). Read nothing by hand that the injection already carries, and never `arc/` or masked spans; every injected item still passes the gc read barrier: freed, stale, or unowned → surface it, do not apply it. What stays yours: cold spans in the other hot files pour on pressure via `/vlds:gc normalize`, and a hook-poured record's registration as an attachment is owed to that sweep. No injection → the hook degraded: read `phi-index.md` and the hot files yourself (no index yet → cold-start on `store/*`) |
| the user rules, prefers, corrects, or retracts | append to `local-storage.md` with their words; a retraction also sweeps and appends to `tombstones.md` |
| a claim is verified against a source | append to `data-store.md` with what was read; re-verify it on recall — verification decays as the world drifts |
| an inference is minted that the work leans on | append to `virtual.md`; it expires at turn end unless promoted |
| a task starts, moves, or completes | append to `session-storage.md`; completion clears its entries |
| the guide settles a rule, or reuses one | `index.md` (the rule) and `ledger.md` (the event, with the match that justified it) |
| **a reading that steered work turns out to be wrong** | append a `correction` to `ledger.md` — `match` (what was assumed) against `meant` (what was wanted) — **while the session is alive**: the dispatch record dies with its session and is collected unread, so a lesson left there is lost — and by the time anything collects it, the only party who could judge what deserved keeping is gone |
| the looper runs an instrument | append that decision to `logger.md`, tagged |

**The floor.** A session that ends with its dispatch rows stamped but never completed did not run this layer.
The stamp is mechanical now — the prompt hook writes one on every message in every session — so the floor moved up: a row without its `state:` and `addressed:` is a message received and never recorded as addressed, and leaving every row that way is the one outcome that is always wrong.
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
The dispatch record is **one file, `dispatch.md`**: on a NEW session's first prompt the prompt hook pours it whole-file into `arc/` — a byte-identical copy, sha-verified before the reseed, the header preserved — and the dispatcher starts fresh. The pour keys on the store's `.sessions` ledger: a resumed conversation's id is already there and pours nothing, a fork's new id is recorded at its SessionStart, and a transient firing never submits a prompt, which is what dissolves the rotation hazard the per-session era was built around. The poured copy sits in `arc/` unregistered until a sweep attaches it. The record is never promoted to a rule, and anything worth keeping belongs in `logger.md`, which does not expire.
`virtual.md`, `session-storage.md`, `local-storage.md`, and `data-store.md` are the gate's storage tiers made literal, written and expired per the table above — no partition invalidates itself, so expiry is lazy, checked at recall, and the gc's to run.
`phi-index.md` and `arc/` are the gc's φ-register — normalized in-session per its reference, never by hook; the one hook-side arc write is the whole-file dispatch pour above. The index is derived, but a user's edit to it is a ruling — its `## recall` section is where the injected slice is chosen.
One entry shape per file, defined in the file's own header — title, short description, schema prose, and the yaml shape, dispatch-seed style; the owning instrument's reference carries the why, and on divergence the file wins (a user edit is a ruling).

**What this never does.**
It never re-homes, renames, or suppresses base memory files; VLDS files never get MEMORY.md index lines, and base memories never move into `store` — extension, not replacement.
The store stays plain and user-editable; a user's direct edit is a ruling, and the latest ruling wins.
A repo-root `.vlds/` found in the tree is read as a legacy source; new writes land in `store`, and a migration is offered once and logged.

Full procedures: the `vlds` plugin skills — `/vlds:gate`, `/vlds:guide`, `/vlds:gc`, `/vlds:inspector`; the looper surfaces on its own.
