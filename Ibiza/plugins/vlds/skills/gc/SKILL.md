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
| Heap object      | A stored decision or claim: a memory entry, a configured rule (`.vlds/index.md`), a logged verdict, a plan-doc ruling, a summary carryover, a training-data assumption |
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

`UNOWNED` is an allocation bug, not only a collection target: a workaround for an operational annoyance stored as a standing rule was never anyone's decision.
The **write barrier** is its prevention — before persisting any standing rule, name its owner (the user ruling that decided it); with no owner, store an open question instead of doctrine.

## When the collector runs

1. **On free** — the user retracts, corrects, or supersedes: sweep TRANSITIVELY along the reference graph in both directions — everything derived from the freed decision, and every store that cites the swept items. A sweep that leaves an inbound reference has manufactured a dangling pointer.
2. **On recall (the read barrier)** — before a stored rule, memory, or assumption shapes an in-session decision, trace its provenance to a root; unreachable → do not apply, surface instead.
3. **On completion** — a landed arc collects what it obsoleted.
4. **Full collection** — `/vlds:gc full`: mark-and-sweep the whole store.

## The hazard ranking

- **Avoidance rules are the highest-risk objects.** A rule that prevents an action evades every natural re-verification — you never collide with what you never touch — so it survives on inertia and must be traced proactively at every recall.
- **A directive justified by an incident dies with the incident's causes.** Re-check whether the causes still exist; fixed causes make it `FREED-RESIDUE` even when no explicit retraction ever arrived.
- **Training data is the oldest generation.** Every versioned or dated claim recalled from it is `STALE`-suspect by default — the gate's `source_type: training`, read at store scope.
- **Latest user word wins.** Rulings are ordered; a newer ruling silently frees every older one it contradicts, and the sweep is owed at the moment of contradiction.

## How to Apply

1. **Identify** the item under collection: what stored decision is about to be applied, was just retracted, or is being audited.
2. **Trace provenance to a root**: who decided it, from what cause, re-verified against the world as it is now — not as the store remembers it.
3. **Mark** its liveness class from the table above.
4. **Sweep**: delete or compact (keep the durable lesson, kill the dead directive), update every inbound reference transitively, and **tombstone** the free in `.vlds/tombstones.md` — the retraction, its date, the user's words, and what was swept with it. The tombstone makes the sweep reversible and the same garbage un-relearnable.
5. **Surface the result**: what was collected, what survived compaction, and what is now `UNOWNED` awaiting a ruling.

If a target was passed with the command — `/vlds:gc <target>` — collect **that** first.

## Additional Resources

These load on demand — read them when the moment calls for it:

- [reference.md](reference.md) — the layer behind the collector: the generational model (session context / stored memory / training data), the tombstone schema, the provenance-tracing procedure, and how the gc composes with the gate, guide, inspector, and looper.
- [examples.md](examples.md) — a real use-after-free walked end to end, a read-barrier catch, and a write-barrier refusal.
