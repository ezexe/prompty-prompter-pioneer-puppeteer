#!/bin/sh
# VLDS SessionStart: seed the shared dispatcher if absent, and emit the contract.
#
# ONE DISPATCH FILE, `dispatch.md`, poured into the φ-register at session start BY THE MODEL — never by
# this hook. That division is what makes a single shared file safe where two per-session designs and two
# rotation designs before them were not: SessionStart also fires on resume, and a restart fires it under
# a transient id before the conversation's own, so no hook can ever know whether a session began — but a
# transient firing never gets a model turn, and the pour is the model's first-turn act: verbatim into
# arc/, script-verified before the trim, and reversible. The hook's whole job is mechanical: make sure
# the append target exists, then print the contract.
set -u

seed="${CLAUDE_PLUGIN_ROOT}/hooks/dispatch-seed.md"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  store="${CLAUDE_PROJECT_DIR}/.claude/vlds"
  mkdir -p "$store"
  [ -f "$store/dispatch.md" ] || cp "$seed" "$store/dispatch.md" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
