# VLDS GC — Reference

The model behind the collector defined in [SKILL.md](SKILL.md).
Load this for the generational model, the tombstone schema, the provenance-tracing procedure, and how the gc composes with the other instruments.

## The Generational Model

Source-code collectors treat object age as a signal; the epistemic heap has three generations with opposite collectability:

| Generation | Store                                                             | Collectability                                                                                              |
| ---------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Gen 0      | The live session context (claims made this conversation)          | Cheapest to re-verify; collected naturally by the conversation moving on — but see the tenuring hazard below |
| Gen 1      | Persisted stores: memory files, `.vlds/index.md`, plan docs, CLAUDE.md directives | The gc's main heap: collected on free, on recall, on completion, and by full audit             |
| Gen 2      | Training data                                                     | Permanently allocated — never collectable, only maskable: tombstones + verification discipline sit in front of it |

**The tenuring hazard**: context summarization is a copying collector for Gen 0 — and it copies garbage as faithfully as live objects.
A stale claim carried forward by a summary arrives in the next window looking fresh, its provenance stripped by the copy.
Treat summary-carried claims as Gen 1 objects with weakened provenance: re-traceable on recall, not pre-trusted.

**The Gen 2 mask**: a training-data assumption cannot be deleted, so collecting it means writing what masks it — a tombstone or verified current fact in Gen 1 that the read barrier finds first.
This is why sweeping without a tombstone fails against Gen 2 garbage: the same prior re-generates the same stale claim, and nothing stands in front of it the next time.

## The Tombstone Schema

`.vlds/tombstones.md` is the gc's own store — append-only, user-editable, one entry per free:

```yaml
- freed: [the decision/rule/claim that was disposed]
  time: [YYYY-MM-DD HH:MM]   # local wall-clock at write time; date alone if minutes aren't real
  cause: retraction | superseded | fixed-cause | world-drift
  owner-words: "[the user's actual words, when the free was a retraction or supersession]"
  swept: [the items removed or rewritten with it — every store touched]
  lesson: [what survived compaction — the durable fact worth keeping, if any]
```

Tombstones serve three jobs: they make a sweep **reversible** (a wrongly-collected item can be resurrected from its entry), they make the collector **auditable** (the user reviews what was killed and why), and they **mask Gen 2** (the recorded free outranks the training prior that would otherwise re-learn the same rule).

## The Provenance-Tracing Procedure

Liveness is decided by tracing, never by how plausible the item still sounds:

1. **Find the allocation site** — what created this item: a user ruling, an incident, an observation, an inference?
2. **Find the owner** — which USER decision anchors it. No owner → `UNOWNED`, whatever else is true.
3. **Re-verify the load-bearing cause against the present world** — grep the code, run the check, read the source. The store's own restatement of the cause is not evidence; that is verifying memory against memory.
4. **Check supersession** — scan later rulings for contradiction; the latest user word frees every older one it contradicts.
5. **Walk the references both ways** — what this item derives from (dead upstream → dead here) and what derives from it (a sweep here owes a sweep there).

Two structural biases to trace against:

- **Self-defense at collection time.** The same reasoning that allocated a rule will defend it when audited; provenance-tracing is mechanical precisely to route around that — the chain either reaches a root or it does not.
- **The avoidance-rule blind spot.** A rule that prevents an action is never falsified by use, because it prevents the very runs that would falsify it. The longer an avoidance rule has survived, the LESS that survival means; seniority is not liveness.

## Composing With the Other Instruments

- **Gate** — the gate stamps a claim's status now; the gc governs how long a stamp stays good. A recalled `CONFIRMED` whose verification has aged re-enters as `PENDING`: verification decays, and the gc's read barrier is where the decay is noticed. The gate's `source_type: training` is the gc's Gen 2, met at claim scope.
- **Guide** — the guide's `hit` is a read from the rule heap, so every hit passes the gc's read barrier before it is applied: a hit on a freed rule is exactly a use-after-free with good intentions. The guide's ledger records the liveness call beside the reuse it justified.
- **Inspector** — a contested liveness call (the trace is ambiguous, or the sweep is consequential) escalates to the inspector's independent eyes before anything is deleted.
- **Looper** — the looper carries the gc's triggers (the instruments' own `when_to_use` is inert): it runs the read barrier at intake on whatever stored state the request leans on, and runs the transitive sweep the moment a turn contains a retraction.

## The Honest Limit

The collector runs on the same substrate that allocated the garbage, and a bias that planted a rule can defend it under audit.
Mechanical tracing narrows that gap; the tombstone record hands the user the final audit; and the inspector supplies the outside eye on contested sweeps.
The floor rises; the ceiling stays where it is — a gc pass raises the odds that stored state is live, and manufactures no certainty that it is.
