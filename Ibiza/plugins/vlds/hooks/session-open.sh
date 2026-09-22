#!/bin/sh
# VLDS SessionStart, the contract hook: seed the shared dispatcher if absent, then emit ONE part of the contract.
#
# The harness caps each hook's output at 10,000 characters and spills a longer one to a file, of which the model
# sees a 2 KB preview — so a contract past the cap never reaches the model whole. This hook therefore prints one
# part of hooks/memory-override.md per invocation (`--part N`, part 0 when absent), and hooks.json registers it
# once per part, in order. The parts are cut at paragraph boundaries — a table is one paragraph, so no row is
# split — under a 9,500-byte budget that leaves room for a continuation head line, deterministic from the file
# alone, so every invocation computes the same cut; a paragraph over the budget by itself is cut at lines. A part
# past the file's end prints nothing. Nothing here pours: the recall rides in hooks/run-hook.sh session-open (the
# index slot) and session-open --slot N, all registered beside this one in hooks.json. SessionStart fires on
# resume and, on a restart, under a transient id before the conversation's own, so no SessionStart firing can
# prove a session began; the pour of dispatch.md belongs to the UserPromptSubmit hook, which fires only when a
# real turn exists and keys on the store's .sessions ledger to tell a first prompt from a resumed, forked, or
# compacted conversation's.
set -u

seed="${CLAUDE_PLUGIN_ROOT}/hooks/dispatch-seed.md"
contract="${CLAUDE_PLUGIN_ROOT}/hooks/memory-override.md"
part=0
[ "${1:-}" = "--part" ] && part="${2:-0}"

if [ "$part" -eq 0 ] && [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  store="${CLAUDE_PROJECT_DIR}/.claude/vlds"
  mkdir -p "$store"
  [ -f "$store/dispatch.md" ] || cp "$seed" "$store/dispatch.md" 2>/dev/null || true
fi

LC_ALL=C awk -v want="$part" -v budget=9500 -v head=200 '
  function out(s) {
    if (!started) {
      started = 1
      if (want > 0) print "## VLDS memory override, part " want + 1 " (continued from the previous hook output)"
    }
    print s
  }
  { L[NR] = $0 }
  END {
    n = NR; p = 0; size = 0; room = budget - head; i = 1
    while (i <= n) {
      j = i; plen = 0
      while (j <= n) { plen += length(L[j]) + 1; if (L[j] == "") break; j++ }
      if (j > n) j = n
      if (size > 0 && size + plen > room) { p++; size = 0 }
      if (plen > room) {
        for (k = i; k <= j; k++) {
          ll = length(L[k]) + 1
          if (size > 0 && size + ll > room) { p++; size = 0 }
          if (p == want) out(L[k])
          size += ll
        }
      } else {
        for (k = i; k <= j; k++) if (p == want) out(L[k])
        size += plen
      }
      i = j + 1
    }
  }
' "$contract"
