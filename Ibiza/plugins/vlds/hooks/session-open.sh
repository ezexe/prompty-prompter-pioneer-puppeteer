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

  # Archive only on a positively identified NEW session. No id, or the same id, means do nothing.
  if [ -n "$sid" ] && [ "$sid" != "$prev" ]; then
    # Two guards, both learned from a live restart that rotated a running session's record away.
    #   $prev empty -> no sidecar, so ownership of the existing record is UNPROVABLE. Adopt it rather
    #   than rotate: appending to a stale record is visible and recoverable, archiving a live one costs
    #   the session its working memory mid-run. Same fail-safe direction as every other branch here.
    #   cmp against the seed -> a pristine record has nothing to archive. Without this, one restart
    #   firing SessionStart twice under different ids files a junk archive of an untouched template.
    if [ -n "$prev" ] && [ -f "$store/dispatch.md" ] && ! cmp -s "$store/dispatch.md" "$seed"; then
      mkdir -p "$store/archive"
      # Name by the OUTGOING session, not the clock alone: a timestamp has one-second resolution, and two
      # rotations inside the same second would overwrite — silently turning an archive back into a truncation.
      owner=$(printf '%s' "${prev:-orphan}" | tr -c 'A-Za-z0-9-' '_' | cut -c1-12)
      target="$store/archive/dispatch-$(date +%Y%m%d-%H%M%S)-$owner.md"
      n=1
      while [ -e "$target" ] && [ "$n" -lt 100 ]; do
        target="$store/archive/dispatch-$(date +%Y%m%d-%H%M%S)-$owner-$n.md"
        n=$((n + 1))
      done
      [ -e "$target" ] || mv "$store/dispatch.md" "$target" 2>/dev/null || true
    fi
    printf '%s' "$sid" > "$store/.session"
  fi

  [ -f "$store/dispatch.md" ] || cp "$seed" "$store/dispatch.md" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
