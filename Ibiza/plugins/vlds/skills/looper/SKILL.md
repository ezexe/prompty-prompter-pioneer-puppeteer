---
name: looper
description: "The conductor of the VLDS dashboard — the one auto-surfacing skill that runs the loop across the three direct-invoke instruments, because Claude Code skills do not co-fire or hand off to one another. A backstop rather than a wrapper, it catches a load-bearing claim, intent, or verdict about to be acted on unchecked: it disciplines the need (guide), routes each claim (gate), and re-examines high-stakes verdicts (inspector), in that order, then logs every decision to its own shared, user-editable logger. It applies each instrument's procedure rather than invoking it — skills cannot call skills — and owns only the order and the log; the instruments stay single-purpose, reached directly by the user."
when_to_use: "When a request carries something load-bearing at risk of going unchecked — the looper is a backstop for the slip rather than a wrapper for every turn. The tell is subordination to an action: a consequential claim, intent, or verdict ridden in on a request to do something, where default handling would act on it without pausing to route it — unlike the same point raised head-on, which already invites the check and needs no looper. It fires on the slip — a claim about to be acted on unverified, an inferred intent treated as settled, a choice about to drive work, or a high-stakes verdict about to pass as fact — and stays quiet on trivial turns and where the discipline is already applied by reflex. To run one instrument alone, invoke it directly."
argument-hint: "[request to run through the loop]"
---

# VLDS Looper

> The looper is what **runs the loop** — the one skill that surfaces on its own and carries a request through all three instruments in order. Since Claude Code skills neither co-fire nor hand off, the looper **applies** each instrument's procedure rather than _invoking_ it; the user reaches them directly via `/vlds:<name>`. The looper is what makes the loop run **on its own**. One commitment: _it owns the order and the log, leaving the mechanisms to the instruments — each step is the instrument's own._

## The Loop

On a load-bearing request, run the three instruments in order — applying each one's own procedure (the looper only sequences — the mechanism stays the instrument's):

1. **Guide the need** — at intake, treat the intent as a claim: look it up in `.vlds/index.md` (`hit` → apply the rule; `miss` → ask, teach, or offer to configure). Procedure: [../guide/SKILL.md](../guide/SKILL.md).
2. **Gate each claim** — for every load-bearing claim the work rests on, route it to `CONFIRMED` / `PENDING` / `HEDGED` and verify what is `PENDING`. Procedure: [../gate/SKILL.md](../gate/SKILL.md).
3. **Inspect the high-stakes verdicts** — escalate a consequential `CONFIRMED` or applied `match` to independent eyes → `CORROBORATED` / `REJECTED` / `CONTESTED`. Procedure: [../inspector/SKILL.md](../inspector/SKILL.md).

The order is the loop the dashboard is built on — **does the need have a configured answer? → is each claim known? → would an outside eye agree?** Carry state forward: a `REJECTED` verdict re-gates the claim; a `CONTESTED` one is surfaced.

## Log Every Decision

As it runs, the looper appends each instrument's decision to its own shared, user-editable **`.vlds/logger.md`** — the dashboard's single activity log, tagged by instrument and stamped with the local wall-clock time read from the system at write time (schema in [reference.md](reference.md)). This is the looper's store. The guide keeps its own `.vlds/index.md` (rules) and `.vlds/ledger.md` (its config audit), both unique to it; the logger is the looper's record of the whole flow as it conducts it.

## How to Apply

1. Run on any **load-bearing or consequential** request; skip trivial or conversational ones.
2. Run steps 1–3 in order, applying each instrument's procedure.
3. Append each decision to `.vlds/logger.md`.
4. For a heavy independent check, **delegate to an isolated subagent** to run the inspector's eyes apart from the main context and return only a verdict; otherwise run inline.

To use one instrument alone, invoke it directly: `/vlds:gate`, `/vlds:guide`, `/vlds:inspector`. If a request was passed with the command — `/vlds:looper <request>` — run **that** through the loop.

## Additional Resources

- [reference.md](reference.md) — the shared logger schema (tagged entries for all three instruments), how the looper composes the direct-invoke instruments, and when to fork a subagent for heavy checks.
- The instrument procedures: [../gate/SKILL.md](../gate/SKILL.md), [../guide/SKILL.md](../guide/SKILL.md), [../inspector/SKILL.md](../inspector/SKILL.md).
