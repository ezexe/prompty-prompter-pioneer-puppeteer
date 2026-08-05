#!/bin/sh
# VLDS SessionStart: archive a PRIOR session's dispatch record, seed a fresh one, emit the contract.
#
# The dispatch record is session-scoped, but SessionStart also fires on resume — so the decision keys on
# session IDENTITY, not on the event. A resume carries the same session_id and must leave the live record
# alone; only a genuinely new session archives. Every uncertain path declines to archive: losing a rotation
# costs nothing, archiving mid-session would destroy the record the barrier is reading.
set -u

input=$(cat 2>/dev/null || true)
seed="${CLAUDE_PLUGIN_ROOT}/hooks/dispatch-seed.md"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  store="${CLAUDE_PROJECT_DIR}/.claude/vlds"
  mkdir -p "$store"

  sid=$(printf '%s' "$input" | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)"$/\1/')
  prev=""
  [ -f "$store/.session" ] && prev=$(cat "$store/.session" 2>/dev/null || true)

  # ROTATION IS SUSPENDED — pending a ruling on what actually proves a new session.
  #
  # It was tried twice and failed twice, each time rotating a conversation that was still running:
  #   1. an absent sidecar was read as proof the record was a prior session's orphan — it was the live one;
  #   2. a single restart fires SessionStart under a transient id and THEN under the conversation's own id,
  #      so any trigger keyed on "the id changed" rotates a session that never ended.
  # session_id is therefore not a signal for "a new session began," and no third guess is being made here:
  # a mechanism that cannot decide competently should not be the one deciding. The record now simply
  # accumulates, which is the known, survivable state this replaced — and collecting it is the gc's job,
  # where there is a judge, not a shell script inferring from an unstable id.
  #
  # The sidecar is still written: it costs nothing and it is the evidence any future trigger would be built on.
  if [ -n "$sid" ] && [ "$sid" != "$prev" ]; then
    printf '%s' "$sid" > "$store/.session"
  fi

  [ -f "$store/dispatch.md" ] || cp "$seed" "$store/dispatch.md" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
