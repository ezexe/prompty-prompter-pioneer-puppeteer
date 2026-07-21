# VLDS GC — Examples

Three collections walked end to end: a use-after-free swept on retraction, a read-barrier catch on recall, and a write-barrier refusal at allocation.
The first two are drawn from a real incident pair on a real project, generalized.

## Example 1: the use-after-free — an incident laundered into doctrine

**The allocation.** During audio-plugin work, a test run once wedged inside the desktop app — a stuck process, recoverable only by restarting the app — and the same day's debugging had auto-previewed a sound-emitting page on every file save.
The agent stored a standing rule: _"audio tests are user gates — WARN before running anything that emits sound."_

**The frees, unnoticed.** Over the following days every cause was fixed in code: the page stopped auto-playing on bare loads (a URL flag gates the tone), the engine learned to mute its own OS output, an abandoned engine process learned to self-quit on a linger timer, and the test harnesses got bounded waits with force-kill cleanup.
Each fix freed part of the rule's justification.
The rule outlived all of them — nothing ever re-traced it, because it was an **avoidance rule**: it prevented the very runs that would have exposed it as dead.
For six days the agent deferred runnable verifications to the user, on a rule with no living cause and no owner.

**The retraction.** The user called it directly: the gating was _"also a halucination i didnt address yet"_ — an unaddressed hang hidden behind a gate instead of fixed, then stored as doctrine.

**The collection.**

1. **Mark**: the rule traces to an incident whose causes are all verifiably fixed, and to no user ruling — `FREED-RESIDUE`, and retroactively `UNOWNED` from the day it was written.
2. **Sweep transitively**: the memory file holding the rule is deleted and replaced by one recording the retraction and the causes' fixes; the memory index line is rewritten; an ops doc that framed the test matrix as "WARN/ask first" is re-framed; a changelog line repeating the gate — written hours earlier — is corrected; a sibling memory about hallucinated decisions gains this as its second instance.
3. **Verify the sweep**: grep the stores for the old rule's phrasing — zero inbound references remain.
4. **Run what the rule blocked**: both audio test harnesses, immediately, green — the first live proof the rule had been costing real verification.
5. **Tombstone**:

```yaml
- freed: "audio tests are user gates — warn before running anything that emits sound"
  time: 2026-07-21
  cause: retraction
  owner-words: "gating on sound was also a halucination i didnt address yet"
  swept: [the gating memory (replaced), the index line, the ops-doc framing, the changelog tail, second-instance note in the hallucinated-decisions memory]
  lesson: "attribute sound to a process by per-PID audio-session metering, never the device aggregate; fix an operational annoyance at its cause — a workaround stored as doctrine is an unowned allocation"
```

The compaction is the point: the durable lesson (how to attribute sound correctly) survives; the dead directive (don't run audio) dies; the tombstone's `owner-words` keep the same rule from being re-learned from the same prior.

## Example 2: the read-barrier catch — a stale ops claim about to drive work

**The recall.** Mid-task, a stored ops note surfaces: _"the audio test scripts hand-mirror the shared-memory byte layout — change the struct, update the script offsets in lockstep."_
A struct change just landed, so the note is about to allocate real work: a lockstep offset edit across the scripts.

**The trace.** Step 3 of the procedure — re-verify the cause against the present world, not against the store: grep the scripts for offsets, marshals, mappings.
Zero matches: the scripts were long since rewritten to drive a compiled client that includes the struct header, so the layout propagates by rebuild.

**The mark and sweep.** `STALE` — the world moved, the note did not.
The note is rewritten in place to the current fact with the verification date attached, and the planned lockstep edit is cancelled.
Cost of the barrier: one grep.
Cost of skipping it: a pointless edit pass, and a store that teaches the same wrong move again next session.

## Example 3: the write-barrier refusal — doctrine with no owner

**The temptation.** A flaky external service wastes an afternoon; the draft memory reads: _"never call service X directly — always stub it."_

**The barrier.** Before persisting a standing rule, name its owner.
No user ruled this; the flakiness is an incident, possibly transient, possibly fixable.
Stored as written it would be an `UNOWNED` allocation — and an avoidance rule, the kind that never self-corrects.

**What gets stored instead**: the incident as fact ("service X timed out N times on <date>, cost an afternoon"), plus an OPEN question for the user ("stub it by default, or fix the retry config?").
The decision stays where it belongs; the store carries evidence, not self-issued policy.

## The Shape to Notice

All three examples are one lesson at three phases of an object's life:
at allocation, name the owner or store a question (Example 3);
at recall, trace before applying (Example 2);
at free, sweep transitively and tombstone (Example 1).
Liveness is provenance — and the rules that most need collecting are precisely the ones whose nature keeps them from ever being tested.
