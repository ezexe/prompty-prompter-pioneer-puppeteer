#!/bin/sh
# VLDS SessionStart: point this session at its own dispatch record, seed it, and emit the contract.
#
# ONE RECORD PER SESSION. There is no rotation and nothing is ever moved, because a running session's
# record cannot be taken when nothing else writes to that filename. That dissolves the problem two earlier
# designs failed to solve: SessionStart also fires on resume, and one restart fires it under a transient id
# and then under the conversation's own — so "the id changed" never proved a session had ended, and both
# attempts to key rotation on it took a record out from under a live conversation.
#
# `.dispatch-current` holds the FILENAME of this session's record, not an id: it is how the model knows
# where to append. With no id available the shared `dispatch.md` is used, which is the pre-per-session
# behaviour and is safe because it is never rotated either.
#
# A session that opens and writes nothing leaves a record identical to the seed. Those are gc-sweepable on
# a full collection — the hook does the mechanical part and leaves the judging to something that can judge.
set -u

input=$(cat 2>/dev/null || true)
seed="${CLAUDE_PLUGIN_ROOT}/hooks/dispatch-seed.md"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  store="${CLAUDE_PROJECT_DIR}/.claude/vlds"
  mkdir -p "$store"

  sid=$(printf '%s' "$input" | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)"$/\1/')
  if [ -n "$sid" ]; then
    record="dispatch-$(printf '%s' "$sid" | tr -c 'A-Za-z0-9-' '_').md"
  else
    record="dispatch.md"
  fi

  printf '%s' "$record" > "$store/.dispatch-current"
  [ -f "$store/$record" ] || cp "$seed" "$store/$record" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
