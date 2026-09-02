#!/bin/sh
# VLDS SessionStart, the contract hook: seed the shared dispatcher if absent, then emit the contract.
#
# This hook prints the contract and nothing else, on purpose: the harness caps each hook's output at 10,000
# characters and spills a longer one to a file, so the recall rides in separate hooks — hooks/run-hook.sh
# session-open (the index slot) and session-open --slot N (one inject file each), all registered beside this
# one in hooks.json. Nothing here pours. SessionStart fires on resume and, on a restart, under a transient id
# before the conversation's own, so no SessionStart firing can prove a session began; the pour of dispatch.md
# belongs to the UserPromptSubmit hook, which fires only when a real turn exists and keys on the store's
# .sessions ledger to tell a first prompt from a resumed, forked, or compacted conversation's.
set -u

seed="${CLAUDE_PLUGIN_ROOT}/hooks/dispatch-seed.md"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  store="${CLAUDE_PROJECT_DIR}/.claude/vlds"
  mkdir -p "$store"
  [ -f "$store/dispatch.md" ] || cp "$seed" "$store/dispatch.md" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
