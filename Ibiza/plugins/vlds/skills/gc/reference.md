# VLDS GC — Reference

The model behind the collector defined in [SKILL.md](SKILL.md).
Load this for the generational model, the tombstone schema, the provenance-tracing procedure, and how the gc composes with the other instruments.

## The Generational Model

Source-code collectors treat object age as a signal; the epistemic heap has three generations with opposite collectability:

| Generation | Store                                                             | Collectability                                                                                              |
| ---------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Gen 0      | The live session context (claims made this conversation)          | Cheapest to re-verify; collected naturally by the conversation moving on — but see the tenuring hazard below |
| Gen 1      | Persisted stores: memory files, the VLDS store's `index.md` and partition files, plan docs, CLAUDE.md directives | The gc's main heap: collected on free, on recall, on completion, and by full audit             |
| Gen 2      | Training data                                                     | Permanently allocated — never collectable, only maskable: tombstones + verification discipline sit in front of it |

**The tenuring hazard**: context summarization is a copying collector for Gen 0 — and it copies garbage as faithfully as live objects.
A stale claim carried forward by a summary arrives in the next window looking fresh, its provenance stripped by the copy.
Treat summary-carried claims as Gen 1 objects with weakened provenance: re-traceable on recall, not pre-trusted.

**The Gen 2 mask**: a training-data assumption cannot be deleted, so collecting it means writing what masks it — a tombstone or verified current fact in Gen 1 that the read barrier finds first.
This is why sweeping without a tombstone fails against Gen 2 garbage: the same prior re-generates the same stale claim, and nothing stands in front of it the next time.

## The Tombstone Schema

`tombstones.md` — in the **VLDS store**, the working directory's `.claude/vlds/` directory resolved by the plugin's memory override ([../../hooks/memory-override.md](../../hooks/memory-override.md)) — is the gc's own store: append-only, user-editable, one entry per free.
The operative shape lives in the file's own header (the canonical form); the block below is the teaching copy, and on divergence the file wins:

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

## Where Echoes Come From

The dispatch barrier ([SKILL.md](SKILL.md)) exists because an echo is rarely the user repeating themselves; it is the harness re-delivering something already handled:

| Vector | How the echo arrives |
| --- | --- |
| Mid-turn interleave | a user message surfaces alongside a tool result inside a running turn, then appears again as a conversation turn |
| Hook injection | SessionStart / resume hooks re-emit the same resident text every session; system-reminders repeat stored memory verbatim |
| Summary replay | context summarization carries a handled message forward with its handled-ness stripped |
| Task notification | a background result returns on a premise that has since moved |
| Re-paste | the user re-sends a document already diffed against issued fixes |

Summary replay is the dangerous row, and for the same reason the tenuring hazard is: the copy is faithful to content and lossy about status.
A stale claim carried forward merely misleads; a handled message carried forward actively invites the work to be done a second time.

## Cycles and Pressure — Collecting What Grew Into Itself

Per-item tracing has a blind spot the literature already named: **reference counting cannot collect a cycle.**
A cluster whose every inbound reference comes from another member keeps all of them "referenced," so each one audited alone passes — and the procedure above audits them one at a time.
Only asking whether the _cluster_ reaches a live root, rather than whether an item has a referrer, sees the island float free.

Applied to stored doctrine, that island is a rule patching the previous rule's gap, patched in turn by the next: every link locally justified, the whole anchored to nothing anyone asked for.
It is the one failure the other marks structurally cannot catch, because each member really does have an owner — just a local one.

**Three counted signals**, counted rather than judged for the reason the tracing procedure is mechanical: the reasoning that allocated the complexity will defend it under audit, and that bias operates at structure scope too.

| Signal | Count | Reads as pressure when |
| --- | --- | --- |
| Growth ratio | insertions : deletions across the arc, or the last N changes | growth runs one way — a store that never deletes is accreting, whatever each change was worth |
| Repair fraction | changes repairing the previous changes, against changes serving a new need | a third or more: the collector running more and reclaiming less is thrashing |
| Root distance | hops from a new rule to a user ruling | more than two, and all of them through other doctrine — a cycle candidate |

**It previews. It never sweeps.**
Sorting essential complexity from accidental is `UNOWNED` by the write barrier's own rule — no user ruling covers it — so the output is a dry run: what would be collected, what it would cost, and what the collector is unsure of.

**A pressure signal names suspects, not garbage.**
Trace every candidate to a root before collecting it, and expect some to survive: a structure can be genuinely overgrown _and_ every branch of it still rooted in something the user asked for.
When that happens the collectible target is not the concepts but the **duplication they spawned** — the same fact restated across files, which compacts without losing anything.
Skipping the trace is how a collector eats live objects because a metric looked bad.

**It counts itself.**
The audit is an allocation like any other; if its own footprint grows across passes, that is pressure by its own first signal.

## The φ-Register — Compression and Recall

The store's compression and session-start recall are modeled on the fib/phi-binary machinery of `zeckendorf-prune`: the hot files are an unnormalized φ-register's pour cells, `store/arc/` is the normalized register, and the gc's compaction is the codec's normalization sweep.
The mechanical companion is `scripts/phi.py` (check / mask / verify-merge / rebuild / restore) — it computes and verifies; every judgment stays here, with the gc, in-session.
The plugin's hooks (`hooks/vlds_hooks.py`) are its mechanical peers: the SessionStart hook injects the recall, the prompt hook stamps dispatch rows and pours `dispatch.md` whole-file at a new session's first prompt, and the post-write hook runs `check` after any store write.
The machinery governs **structure only** — what is hot, where history lives, how it parses — never the content of entries; that boundary is the source project's own measured lesson, transferred whole.

**Conventions, pinned once.**
Positions are 1-based over the cache `[1, 2, 3, 5, 8, 13, 21, 34, ...]`: position p has weight `cache[p−1]` and byte capacity `cache[p−1]` KB.
Epoch pairs are `(cache[k], cache[k+1])`; Cassini `b²−ab−a² = (−1)^k` holds under cache indexing and flips sign under any odd shift, so the position-weight numbering is never reused for the epoch check.
Positions are budgeted in KB; hot files are counted in entries; the two are never interchanged.
The register digit string reads highest position first.
A watermark is recorded as `mask=A:B sha=H` — a 0-based, half-open physical line range naming the masked span, plus the span's content hash; both reader and writer share exactly this definition.

**The register.**
At most one live segment per position, `arc/arc-<p>-<seq>.md`; new material pours at position 1; higher positions exist only as merge products.
The index's digit string (`register: 10100100`) is the archived history as a phi-binary numeral — one glance shows '11' debt; a '2' state (two segments at one position) is visible only to the arc listing, which `phi.py check`'s register scan reads.
The capacities are the unique ones under which merges cannot overflow: `cap(j)+cap(j+1)=cap(j+2)` (CARRY, exact) and `2·cap(j)=cap(j+1)+cap(j−2)` (RESOLVE, exact — the worst-case excess equals the residue capacity, zero slack).
A segment is a ```yaml-fenced header (never `---` frontmatter) plus entry blocks delimited by column-0 `---`; each entry block is an `id: xx-NNNN` line, a blank line, then the verbatim body.
The delimiter cannot occur inside a valid entry (headers fenced, continuations indented, offenders poured whole-file), so one mangled entry corrupts only itself and the parse resynchronizes at the next delimiter.

**The normalize sweep** (`/vlds:gc normalize <file | 'register'>`) — in-session, gc-owned, never a hook, never a timer.
A sweep takes the session-stamped lock `arc/.sweep-lock` (stale after 60 minutes) before any arc write; without it a session only reports owed work — deterministic naming makes concurrent-sweep collisions certain, so the destructive tail is serialized.
The sweep's standing occasion is **pressure and register debt** — `check`'s verdict, injected at session start and after every store write — and the dispatch pour is no longer its act: the prompt hook pours `dispatch.md` whole-file at a new session's first prompt, mechanically, because every entry there is dead by definition (each belongs to a prior conversation) and no judgment is needed on what to pour; the cold spans in the other hot files are scored, not counted, so they stay the sweep's.
The hook keys on the store's `.sessions` ledger (one line per session id that has submitted a prompt, or was recorded by the SessionStart index hook on a resume, fork, or compact): a RESUME's id is already there and pours nothing — a resumed conversation's dispatch entries are its own live barrier state — a FORK's new id is recorded before its first prompt (the forked conversation is live, and so are its rows), and a transient `SessionStart` firing never submits a prompt, so it never pours. The hook honours the sweep lock — a fresh lock held by another session skips that session's pour, and the rows stay hot until the next new session or an in-session sweep — and its copy is sha-verified before the reseed.
Concurrent sessions share the one dispatcher: the barrier matches on fingerprints, so interleaved entries are tolerated, and a simultaneous append can lose an entry — the accepted cost of one shared file; a session that predates the ledger pours once on its first prompt after the hook lands, and the barrier's FRESH default makes that recoverable.

_Pour._ Entry-level: cold spans (pre-session logger entries, SPENT/FREED ruling bodies whose tombstones exist, expired virtual entries) copy verbatim into position-1 segments, chunked at entry boundaries so no segment exceeds capacity, oldest first; a hook-poured dispatch record (`arc/dispatch-<stamp>-<session>.md`, byte-identical to the file it replaced) is registered by the sweep as a position attachment, or carved entry-level into segments when the sweep judges that worth doing.
A poured body that is ALREADY tombstoned gets its segment id line annotated — `id: xx-NNNN (tombstoned)` — so the owed-BORROW scan can tell archived history from a lurking free: the tombstone says freed, the annotation says archived-not-steering, and only the pair together retires the '-1' state (annotating an id changes the segment body, so the `verified:` sha restamps with it).
A SPENT ruling without a tombstone stays hot deliberately — an anti-citation warning until a gc pass tombstones it.
Grammar gate at pour time: an entry containing a column-0 `---` or a code fence is poured whole-file or escaped by a recorded one-level indent; partition entries are bare in both places — the header's shape fence is a file's only fence — and a segment's `fenced: yaml` flag remains only on legacy pours from the fenced-body era.
The gate fires on CARVE extraction too: when lifting entries out of a fenced-era hot file, region delimiters are not entry content — check region boundaries, not just entry starts, because a splitter that misses this over-captures the region's close fence into a segment body and leaves the hot file's region unclosed in the same stroke (two defects, one miss — caught live in a peer store's bootstrap).
Whole-file: a file that cannot pour entry-level — a legacy per-session dispatch record from the pre-0.0.18 design, a hook-poured dispatch record, or any grammar offender — moves whole into `arc/` under its own name as a position **attachment** (`attached:` in the index row; merges move attachments to the child's row mechanically); a legacy record byte-identical to its seed is deleted after verification, not poured.
A poured span is trimmed from the hot file only after `phi.py` verifies the verbatim arc copy — this and merge-parent deletion are the design's two script-verified deletions.
A span poured but not yet trimmed is masked by a **watermark**: the `mask=A:B sha=H` line range plus content hash, recorded at pour time (`phi.py verify-pour` is the trim gate).
**Masked-span content remains authoritative until trimmed**: a hash mismatch means the user ruled there — `check` reports "watermark voided", and the gc must re-read, re-pour, and tombstone what the edit freed before the arc copy may be cited again.

_Rules._ The codec's three violation classes are the complete set of rules a sweep may apply — they are what normalization can do, not when it runs (pressure, below, is the when — a separate, admittedly conventional signal):

| Rule | Fires on | Action |
| --- | --- | --- |
| BORROW | a retraction/free reaching archived content — an event, raised by judgment or by check #8, never visible to the register scan | the subtraction pipeline: locate the fact by id (canonical AND residue entries carry ids), carve in place, tombstone LAST, re-settle from that position; lineage is audit trail, never a reconstruction source |
| RESOLVE | two live segments at one position j | `2·w(j) = w(j+1) + w(j−2)`: child at j+1, byte-mandated residue at j−2 — if the deduped child exceeds capacity, at least the excess must displace, and worst-case it exactly fits; a double at position 1 promotes whole (1+1=2, zero residue); a double at position 2 resolves to child at 3 plus residue at position 1 (2×2 = 3+1) |
| CARRY | positions j and j+1 both occupied | merge into j+2 — byte-exact before dedup even begins |

Priority **BORROW → RESOLVE → CARRY** transfers verbatim from the codec's check sequence; in the codec it is outcome-neutral scheduling, here it is doctrine — retractions outrank compaction because store merges, unlike codec carries, are costly to invert.
Merge mechanics: concatenate parents, dedupe exact duplicates into `## canonical`, everything displaced verbatim into `## residue`, ids on every entry, header records `merged-from`, `pours` (pour-count conservation), per-source spans.

_Commit protocol_ (the codec's steps are atomic; the store's are not): write child → `phi.py verify-merge` → mark the child `verified:` (**the commit point**) → delete parents → update index → watermark last.
Recall treats an unverified child as nonexistent and its parents as live; an arc file absent from the index is a torn pour — delete it and re-sweep; duplicate fact-ids resolve in favor of the file the index lists; an un-tombstoned carve is treated as never having happened.
Between-step crashes leave readable '2'/'11' debt — debt is not corruption, and recall never blocks on it.

_Selection._ What stays hot in a partition tail: the model scores entries on the 8-digit Zeckendorf grid (integers 0..54 — the closed score vocabulary; bands: 0–7 audit noise, 8–20 context, 21–33 durable lesson, 34–54 steering).
Pins — `status: LIVE` entries, ledger `correction` entries, and anything the model keep-pins — delimit DP segments; `phi.py mask` runs the literal `zeckendorf_dp` per segment.
The exact guarantee is **kept ≤ ⌈nᵢ/2⌉ per pin-delimited segment** (density ≤ 0.5 only asymptotically, only for unfragmented even runs); the script asserts the ceiling and reports budget landing, never asserts it.
Adjacent must-keep pairs merge before masking — the carry as forced compaction, on the session-owned tail at pour time.
Every rule application is logged in the codec's own `{rule, sources, targets}` shape; sweep totals (n_in / n_kept / n_merged / bytes before→after) go to `logger.md` and count against its budget — loss measured, never silent.

_Pressure._ A hot row reads `pressure: owed` when live/at-sweep ≥ φ ≈ 1.618 or bytes exceed budget — the φ-register's **own** pressure signal, an addition beside (never a rewrite of) this file's commit-scoped growth-ratio signal above, which serves a different consumer (the doctrine-cycle test); φ here is a convention fitting the pair's natural growth rate, not a property inherited from the machinery.
Amortization, measured by simulation: position k merges roughly once per φ^(k+1) ≈ 1.4·F(k) pours; one pour cascades at most O(register width) = O(log_φ total pours) steps.

**Recall.**
A fresh session start reads `phi-index.md` whole, then the hot files it lists in steering-first order — every item still through the read barrier: the register narrows WHAT is read, never HOW it is judged.
The read is the SessionStart hooks': the index hook prints the index, the inject/digest lists, a one-line digest — entries, bytes, last headline — for each file the index's `## recall` section names under `digest:` (default: data-store, logger), and `check`'s verdict; the `inject:` files (default: local-storage, index, tombstones, ledger, session-storage, virtual) are split at entry boundaries into chunks, and one slot hook prints each chunk, the file's header with its first. One chunk per hook output, because the harness caps each hook's output at 10,000 characters and spills a longer one to a file; the index hook prints the chunk plan. Only a single entry over the cap, or a chunk beyond the registered slots (twelve), arrives as a marker line to be read by hand before it steers. On `source` resume, fork, or compact the index hook records the session id in `.sessions` and prints only the digest lines and the verdict, since the conversation holds its own recall, and the slots print nothing. The section is a ruling like the rest of the index: edit it to change what arrives. A digest file is read in-session only when an entry there is about to steer.
Never read at start: `arc/` and masked (watermarked) spans.
Hot budgets (entries): logger 34, data-store 34, ledger 21, local-storage 21, tombstones 21, virtual 13, session-storage 13, index rows 21; `dispatch.md` is unbudgeted (the floor) — the prompt hook pours it whole-file at a new session's first prompt anyway, and the ratio scan skips it.
On a miss: fact-id grep across segment headers and canonical blocks (O(log_φ) files), or largest-first descent; spans are per-source in headers, so time-anchored queries resolve per (source, time) pair.
Fact-id uniqueness — one id in one live canonical block — is enforced by merge dedupe and verified by scan: the store's **analog of**, not an instance of, Zeckendorf uniqueness.
Archive-read entries arrive as weakened-provenance Gen 1 objects, re-traced before steering.
Pressure is recomputed at recall by `phi.py check` (the stored pair updates only at sweep) — no per-append write obligation exists; the post-write hook re-runs `check` after every store write and hands back its verdict, so pressure and debt are seen as they arise.

**The index** (`phi-index.md`).
Derived — recomputable from segment headers and store grammar — but **an edit to it is a ruling**: `rebuild` is corruption recovery only, refuses to run over a voided watermark, and a user-removed watermark is an un-mask order the gc executes before any rebuild.
Sections: `register` (the digit string); `positions` (weight, bytes, pours, spans, attachments — one recurrence check against the filename's independent witness plus conservation checks, labeled as such); `hot` (live, at-sweep, bytes, budget, watermark, pressure); `epochs` (table columns `| file | k | a | b |`, one row per swept file with a=cache[k], b=cache[k+1] — checked by Cassini **plus row-to-row continuity**: corruption falls off the Fibonacci lattice, skips break the chain); `recall` (two bare lines, not a table: `inject: a.md, b.md` and `digest: c.md` — comma-separated file names; a missing section or key falls back to the hooks' defaults, and the index hook says which it used); `updated` (time, session, command).
Archive names derive from position and epoch — no timestamps, so the historical same-second archive collision is structurally absent.

**What deliberately does not transfer.**
The conserved value functional — the axiom itself: no store quantity satisfies `F(k)+F(k+1)=F(k+2)` exactly (dedup shrinks bytes), so the rules transfer as procedures, not equations, and confluence, unique normal form, and free self-correction do NOT follow — placement and uniqueness are enforced by the scans and this doctrine instead.
Codec self-correction (the store never auto-repairs — deliberately); negative-state scannability (check #8 compensates); bit-level coding of content (it would destroy user-editability); continuous quantization (only the 0..54 grid transfers); matrix algebra as computation (the pair is bookkeeping, and no consumer composes indices); the measured 32% detection rate (the honesty transfers, the number does not).
`phi.py check`'s coverage is structural only — placement, un-run carries, broken streams, counter drift, verbatim duplication, voided watermarks, owed borrows; paraphrase duplication, mis-scores, wrong deadness calls, and semantic staleness remain the read barrier's, this collector's, and the inspector's.

## Composing With the Other Instruments

- **Gate** — the gate stamps a claim's status now; the gc governs how long a stamp stays good. A recalled `CONFIRMED` whose verification has aged re-enters as `PENDING`: verification decays, and the gc's read barrier is where the decay is noticed. The gate's `source_type: training` is the gc's Gen 2, met at claim scope.
- **Guide** — the guide's `hit` is a read from the rule heap, so every hit passes the gc's read barrier before it is applied: a hit on a freed rule is exactly a use-after-free with good intentions. The guide's ledger records the liveness call beside the reuse it justified.
- **Inspector** — a contested liveness call (the trace is ambiguous, or the sweep is consequential) escalates to the inspector's independent eyes before anything is deleted.
- **Looper** — the looper carries the gc's triggers (the instruments' own `when_to_use` is inert): it runs the dispatch barrier before the loop opens, the read barrier at intake on whatever stored state the request leans on, and the transitive sweep the moment a turn contains a retraction.

## The Honest Limit

The collector runs on the same substrate that allocated the garbage, and a bias that planted a rule can defend it under audit.
Mechanical tracing narrows that gap; the tombstone record hands the user the final audit; and the inspector supplies the outside eye on contested sweeps.
The floor rises; the ceiling stays where it is — a gc pass raises the odds that stored state is live, and manufactures no certainty that it is.
