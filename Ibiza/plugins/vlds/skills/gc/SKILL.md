---
name: gc
description: "The epistemic garbage collector — the liveness instrument for STORED state: memories, configured rules, plan-doc rulings, session-summary carryovers, and training-data assumptions. Where the gate asks whether a claim is known now, the gc asks whether a stored decision is still ALIVE: it traces provenance to a live root — a standing user ruling, a currently-verifiable state of the world — before the stored item is allowed to steer a decision. It catches the use-after-free (a retracted ruling still applied), the leak (a directive whose justifying causes were fixed long ago), the dangling pointer (a memory citing what no longer exists), and the stale oldest generation (training data asserting versioned facts as current). Sweeps compact rather than erase — the durable lesson survives, the dead directive dies — and every free is tombstoned so the same garbage is not re-learned. Use when stored state is about to shape an in-session decision, when the user retracts or supersedes a ruling, when a completed arc obsoletes stored claims, or for a full-store audit."
argument-hint: "[stored decision or store to collect | 'full' for a whole-store audit]"
disable-model-invocation: true
---

# VLDS GC

> The gc is **a garbage collector for belief state** — the discipline source-code collectors apply to heap objects, applied to what a model stores and recalls: liveness is provenance-reachability from a live root, never plausibility.
> One question drives it — **"is this stored decision still alive, or am I dereferencing something the user already freed?"** — under one commitment: _a disposed decision stops steering the work the moment it is freed, not whenever it happens to be noticed._

## The heap, the roots, the references

| GC concept       | Epistemic counterpart                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Heap object      | A stored decision or claim: a memory entry, a configured rule (the VLDS store's `index.md`), a logged verdict, a plan-doc ruling, a summary carryover, a training-data assumption |
| Root             | What is live NOW: the user's standing rulings (latest wins), the currently-verifiable state of the world, the live conversation                      |
| Reference        | A provenance edge: the ruling that created a rule, the incident that justified a directive, the observation a claim was read from, links between stored entries |
| Reachable (live) | An unbroken provenance chain to a root: the ruling still stands, the cause still exists, the world still checks out when re-verified                 |
| Free             | A user retraction, correction, or superseding ruling; a fixed cause; a landed change that obsoletes the claim                                        |
| Use-after-free   | Applying a stored derivative of a freed decision                                                                                                    |
| Leak             | An item whose justification no longer exists, surviving only because nothing re-traces its provenance                                               |
| Dangling pointer | A stored item citing a file, flag, symbol, or behavior that no longer exists                                                                        |
| Tombstone        | The record of the free — what was retracted, when, in whose words — which keeps the same garbage from being re-learned                              |

## Liveness classes

Mark every item under collection:

| Class           | Meaning                                                                                | Sweep action                                            |
| --------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `LIVE`          | provenance chain intact to a live root                                                  | keep; apply freely                                      |
| `STALE`         | contradicted by the current world — re-verify against the world, never against the memory of it | rewrite to the current fact, or delete          |
| `FREED-RESIDUE` | derives from a decision the user disposed of                                            | sweep transitively + tombstone                          |
| `UNOWNED`       | no user ruling at its root — self-allocated doctrine                                    | surface as an OPEN point for the user; never apply as settled |
| `EXPIRED`       | lifetime bound reached — a tier-scoped entry whose scope (the turn, the task) has closed | free without a tombstone; promote first if it must outlive its scope |

`EXPIRED` is the ordinary rule, not a new one: the live conversation is already a root, so a turn-scoped entry's root **is** the turn and vanishes with it — and nothing contradicted it, which is why it takes no tombstone.

`UNOWNED` is an allocation bug, not only a collection target: a workaround for an operational annoyance stored as a standing rule was never anyone's decision.
The **write barrier** is its prevention — before persisting any standing rule, name its owner (the user ruling that decided it); with no owner, store an open question instead of doctrine.

## When the collector runs

1. **On free** — the user retracts, corrects, or supersedes: sweep TRANSITIVELY along the reference graph in both directions — everything derived from the freed decision, and every store that cites the swept items. A sweep that leaves an inbound reference has manufactured a dangling pointer.
2. **On recall (the read barrier)** — before a stored rule, memory, or assumption shapes an in-session decision, trace its provenance to a root; unreachable → do not apply, surface instead. A tier-scoped entry whose scope has closed is collected here, which is how turn-end expiry is realized without a turn-end event to hook.
3. **On dispatch (the dispatch barrier)** — before the thought stream commits to answering a message, check it against the dispatch record: already addressed → answer the delta, not the message; superseded → surface the free instead of acting.
4. **On completion** — a landed arc collects what it obsoleted.
5. **Full collection** — `/vlds:gc full`: mark-and-sweep the whole store.
6. **On pressure** — when a landed arc or a full audit shows growth running one way, run the cycle test: per-item tracing cannot see a cluster that only references itself. It previews, never sweeps — [reference.md](reference.md).

## The hazard ranking

- **Avoidance rules are the highest-risk objects.** A rule that prevents an action evades every natural re-verification — you never collide with what you never touch — so it survives on inertia and must be traced proactively at every recall.
- **A directive justified by an incident dies with the incident's causes.** Re-check whether the causes still exist; fixed causes make it `FREED-RESIDUE` even when no explicit retraction ever arrived.
- **Training data is the oldest generation.** Every versioned or dated claim recalled from it is `STALE`-suspect by default — the gate's `source_type: training`, read at store scope.
- **Latest user word wins.** Rulings are ordered; a newer ruling silently frees every older one it contradicts, and the sweep is owed at the moment of contradiction.

## Invalidation — the GC's job, now yours

The web platform teaches this lesson the hard way: `sessionStorage` clears itself when the tab dies, but `localStorage` never expires — invalidation is the developer's job, and state nobody invalidates becomes doctrine by default.
In VLDS the gc is that developer.
The gate's storage tiers persist to partition files, and no partition invalidates itself — so running their expiries is the gc's job.
**Which file takes what is settled in one place: the fires-when table of the always-injected contract** ([../../hooks/memory-override.md](../../hooks/memory-override.md)), which is in context every session; this section owns why those policies are what they are, not a second copy of them.
Two of them are collection triggers already in the list above, met at tier scope: `session-storage.md` clearing at task completion is trigger 4, and `local-storage.md` freeing on retraction is trigger 1.

Persisting an ephemeral tier gives Gen 0 state a Gen 1 body — exactly why its expiry has to be checked rather than assumed: an un-expired `virtual.md` entry is the tenuring hazard on disk.
Nothing here fires on a timer — the expiry is **lazy, enforced at recall**, which is what makes it real without a turn-end event to hook: an entry past its scope never steers, whatever bytes remain on disk.

Which expiries take a tombstone is not uniform, and the split follows what was lost:

- **`virtual.md` and `session-storage.md` — no tombstone.** Turn- and task-scoped state re-derives next time it is needed, so re-minting it is correct behavior, and tombstoning every expired inference would bury the record that matters under the record that doesn't. Mark them `EXPIRED`.
- **`local-storage.md` — tombstone.** It never expires on its own, so anything leaving it left by a user's word — a retraction, a correction, a superseding ruling — which is a free like any other.
- **`data-store.md` — it depends on which way it goes.** An entry **rewritten in place** to the verified current fact is already its own mask and owes nothing further; an entry **dropped** because re-verification failed is a `world-drift` free and owes a tombstone, or the same training prior regenerates the same stale claim with nothing standing in front of it.

## The dispatch barrier — a new message, or the same one twice?

The read barrier guards what you recall and the write barrier guards what you store; the **dispatch barrier** guards what you _answer_.
It fires as the thought stream forms — before a response is committed to, not after it is written — on one question: **is this message new, or am I addressing it a second time believing it new?**
A message, once addressed, is stored state like any other: re-addressing it dereferences a handled message as if unhandled, and re-addressing one that a later message overrode is a use-after-free with a friendly face.

| State | Meaning | Do |
| --- | --- | --- |
| `FRESH` | no matching entry in the dispatch record | address it, then record it |
| `ECHO` | already addressed, and nothing about it changed | answer the delta only — never re-answer the message whole |
| `SUPERSEDED` | addressed, then freed by a later message | surface the free; acting on it is a use-after-free |

**Timing is the whole mechanism.**
Caught while the thought stream forms, an echo costs nothing to drop; caught at emission, the duplicate already exists and every remaining option is bad — ship it and contradict yourself, or retract it and spend the turn on noise.

**Matching is an inference, so log it.**
Messages carry no ids, so a match rests on a fingerprint — the opening clause plus the ask — and is exactly the sameness judgment the guide's `hit` can get wrong.
**When the match is uncertain, default to `FRESH`**: the failure modes are not symmetric — a wrong `FRESH` wastes a turn, a wrong `ECHO` silently drops the user's request, and only the first is recoverable without the user having to notice and ask twice.

The record lives in the store's `dispatch.md`, session-scoped and never promoted to a rule; where echoes come from is in [reference.md](reference.md).
Its collection is a **rotation, not a truncation**: opening a new session moves the prior record into `archive/` and seeds a fresh one, keyed on session identity so a resume — which fires the same event — leaves the live record alone. A record that outlived its session is one whose every entry is an echo by definition, and archiving is what lets it be collected without being destroyed.
The rotation promotes nothing, and cannot: it runs at session open, when the session that could judge what deserved keeping is already gone.
So a misreading that steered work is promoted to the guide's `ledger.md` as a `correction` **when it is caught**, not when the record rotates — the same discipline `virtual.md` follows, where an inference that must outlive its turn is promoted before the turn ends rather than rescued after.

## How to Apply

1. **Identify** the item under collection: what stored decision is about to be applied, was just retracted, or is being audited.
2. **Trace provenance to a root**: who decided it, from what cause, re-verified against the world as it is now — not as the store remembers it.
3. **Mark** its liveness class from the table above.
4. **Sweep**: delete or compact (keep the durable lesson, kill the dead directive), update every inbound reference transitively, and **tombstone** the free in the VLDS store's `tombstones.md` — the retraction, its date, the user's words, and what was swept with it. The tombstone makes the sweep reversible and the same garbage un-relearnable.
5. **Surface the result**: what was collected, what survived compaction, and what is now `UNOWNED` awaiting a ruling.

If a target was passed with the command — `/vlds:gc <target>` — collect **that** first.

## Additional Resources

These load on demand — read them when the moment calls for it:

- [reference.md](reference.md) — the layer behind the collector: the generational model (session context / stored memory / training data), the tombstone schema, the provenance-tracing procedure, and how the gc composes with the gate, guide, inspector, and looper.
- [examples.md](examples.md) — a real use-after-free walked end to end, a read-barrier catch, and a write-barrier refusal.
