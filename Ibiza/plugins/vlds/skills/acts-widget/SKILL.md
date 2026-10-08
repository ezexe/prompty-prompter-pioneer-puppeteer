---
name: acts-widget
description: "The session's acts page — one self-contained HTML page per session, recycled at every closing: each closing's pending acts are appended as a new round, the owner ticks acts and copies the Markdown prompt the page assembles, and when that prompt arrives the reply records the pick into the same page before acting, so the page reads as the session's log of closings — what was offered, what was picked, what was left — oldest first, with the open closing at the bottom."
when_to_use: "At a closing with pending acts, when the session serves it through the acts page; and on a message carrying an `<!-- acts-widget round=N picked=... -->` line, which is a pick from that page to record before running the acts it names."
argument-hint: "[append ACTS.json | pick --acts ID,ID | show]"
---

# Acts widget

One page per session, at `<working dir>/.claude/scratchpad/acts-widget/<session short id>.html` — the git-ignored notebook, since the page is the session's own working surface and nothing reads it after the session.
The page is its own state: the rounds live in a JSON block inside it, `build_acts_widget.py` reads that block back on every call and rewrites the page whole, so there is never a second file to keep in step.
A path that already holds something other than an acts page is refused, never overwritten.

## At a closing

1. Write the closing's acts as JSON to the notebook — one object per act: `id`, `title`, `goal` required; `summary`, `files`, `constraints`, `done`, `recommended` optional; `title`, `repo`, `branch` at the top.
The `goal` is the instruction the prompt carries, so write it as the act exactly as it should run.
2. Append it as the next round:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/acts-widget/build_acts_widget.py" append <acts.json> --session <short id> --now "<the latest now:>"
```

A round still open when the next one is appended is marked superseded — the owner never answered it — so only one closing is ever open.
3. Open the page in the built-in browser: `mcp__Claude_Browser__preview_start` with `url` set to the page's `file:///` URL.
The pane shows a local file as a snapshot, so after every append or pick, navigate to the same URL again to show the new round.
The page's Copy button runs the copy itself, in the click — `execCommand("copy")` first, which needs no clipboard permission, then the clipboard API, and only when both are blocked does it select the prompt for a manual copy.
Where the page runs inside the chat's widget frame, the host's `sendPrompt` exists and a Send button appears that puts the prompt in as the next message, so nothing is copied at all.
4. In the final message, say that the closing is on the acts page and name what it asks.

## When the pick arrives

The prompt the page assembles ends with `<!-- acts-widget round=N picked=ID,ID -->`.
Before running any act it names, record the pick into the page, carrying any per-act context the owner added:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/acts-widget/build_acts_widget.py" pick --session <short id> --round N --acts ID,ID --note "ID=context" --now "<the latest now:>"
```

Then run exactly the picked acts, in the order the prompt lists them, and report as its "How to report" section says.
A message that answers the closing some other way — a skip, a typed reply — is recorded with `pick --skipped`, so the round does not stay open.

`show --session <short id>` prints the rounds and their state without touching the page.

## Files

- `build_acts_widget.py` — the `append`, `pick` and `show` commands, and the page build.
- `template.html` — the page: earlier closings as a log, the open closing's acts beside the prompt they assemble.
- `assemble.js` — the prompt builder, inlined into the page and required by the test.
- `test_acts_widget.py` — acceptance tests: the build, the session round trip, the prompt, and the page's script run under node.
