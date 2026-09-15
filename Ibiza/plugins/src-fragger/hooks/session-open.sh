#!/bin/sh
# src-fragger SessionStart: make sure the store's src/ directory, its register, and the project's notebook
# exist, then emit the contract.
#
# Two hook commands in hooks.json, one subcommand each, because the harness caps EACH hook's output at
# 10,000 characters and the contract alone fills most of one: `seed` creates the directories, seeds the
# register and the notebook's .gitignore, and prints at most one notice line; `contract` prints
# hooks/src-fragger.md and nothing else. With no subcommand both run in order, which is what a hand run or a
# test wants.
#
# The register is seeded from hooks/frags-seed.md when absent and never overwritten — a user's edit to it
# is a ruling. The notebook (.claude/scratchpad/) is seeded with a .gitignore of `*` on the same terms, so
# it ignores itself wherever the project's root .gitignore stands: the split — src/ tracked, the notebook
# ignored — holds without an edit to the project's own rules, and nothing in the notebook can be added
# without -f. The hook never touches the index and never edits the root .gitignore; where a root rule
# ignores .claude/ wholesale, src/ is not tracked either, and that is said in one line for the user to act
# on, never acted on for them.
set -u

step="${1:-all}"

if [ "$step" = "seed" ] || [ "$step" = "all" ]; then
  seed="${CLAUDE_PLUGIN_ROOT}/hooks/frags-seed.md"
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    src="${CLAUDE_PROJECT_DIR}/.claude/vlds/src"
    pad="${CLAUDE_PROJECT_DIR}/.claude/scratchpad"
    mkdir -p "$src" "$pad"
    [ -f "$src/frags.md" ] || cp "$seed" "$src/frags.md" 2>/dev/null || true
    [ -f "$pad/.gitignore" ] || printf '*\n' > "$pad/.gitignore" 2>/dev/null || true
    if command -v git >/dev/null 2>&1 && git -C "$CLAUDE_PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      rule=$(git -C "$CLAUDE_PROJECT_DIR" check-ignore -v --no-index .claude/vlds/src 2>/dev/null | cut -f1)
      if [ -n "$rule" ]; then
        echo "src-fragger: this project's own rules git-ignore the store's src/ ($rule) — frags here are not tracked until the user narrows that rule; say so once, never edit it for them."
      fi
    fi
  fi
fi

if [ "$step" = "contract" ] || [ "$step" = "all" ]; then
  cat "${CLAUDE_PLUGIN_ROOT}/hooks/src-fragger.md"
fi
