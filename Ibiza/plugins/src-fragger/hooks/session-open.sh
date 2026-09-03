#!/bin/sh
# src-fragger SessionStart: make sure the store's src/ directory and its register exist, then emit the contract.
#
# This hook prints the contract and nothing else: the harness caps each hook's output at 10,000 characters, and
# the contract is the only thing that has to be resident. The register is seeded from hooks/frags-seed.md when
# absent and never overwritten — a user's edit to it is a ruling.
set -u

seed="${CLAUDE_PLUGIN_ROOT}/hooks/frags-seed.md"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  src="${CLAUDE_PROJECT_DIR}/.claude/vlds/src"
  mkdir -p "$src"
  [ -f "$src/frags.md" ] || cp "$seed" "$src/frags.md" 2>/dev/null || true
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/src-fragger.md"
