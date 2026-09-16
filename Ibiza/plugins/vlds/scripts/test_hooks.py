#!/usr/bin/env python3
"""test_hooks.py — acceptance tests for the hooks' mechanics: the `pre-write` gate, the `[STRAY]` scan, the `now:`
clock in every hook output, the widened post-write trigger and its unchanged-verdict delta, the owner-voice digest,
the session title, the pooled recall mode (directive, silent slots, first-prompt nudge, compact re-inject, the
`pool: inject` fallback), and the turn-close light sweep (pour, expire, attach, index rewrite, the report at the
next prompt, the lock).

Run from anywhere:  python scripts/test_hooks.py
Each test seeds a throwaway project under a temp dir (a `.claude/vlds/` store with the dispatch seed, a ledger,
a local-storage file), points CLAUDE_PROJECT_DIR at it, and runs the hook or phi.py as the harness would —
a subprocess with the JSON payload on stdin. Exit 0 = every test green; the first failing assertion names
the test. Nothing here touches a real store.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
HOOKS = os.path.join(PLUGIN, "hooks", "vlds_hooks.py")
PHI = os.path.join(HERE, "phi.py")
SEED = os.path.join(PLUGIN, "hooks", "dispatch-seed.md")
NOW_RE = re.compile(r"^(?:- )?now: \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", re.M)

LEDGER_HEADER = """# VLDS Guide — Ledger

Append-only config audit.

```yaml
- correction: [the mis-matched key]
  time: [YYYY-MM-DD HH:MM]
  match: [what was assumed]
  meant: [what was actually wanted]
  delta: [the fix applied]
```

---
"""

LOCAL_STORAGE = """# VLDS Partition — localStorage

The user's stated preferences and rulings, in their words.

```yaml
- ruling: [the ruling, distilled]
  time: [YYYY-MM-DD HH:MM]
  owner-words: "[the user's actual words, verbatim]"
  scope: [what it governs, and for how long]
  status: LIVE | SPENT | FREED
  form: [optional — fence | file | artifact | message]
```

---

- ruling: "the plan goes in the reply as one fenced block"
  time: 2026-09-03 10:00
  owner-words: "should have just been the md fence in the reply for the text box"
  scope: durable
  status: LIVE
  form: fence

- ruling: "go"
  time: 2026-09-03 10:05
  owner-words: "go"
  scope: this turn
  status: SPENT
"""

# the incident fence, in shape: a python heredoc, a correctly homed dispatch append, and a ledger append whose
# path is spelled bare (true under an earlier fence's `cd .claude/vlds`, false at the repo root) with a hedged
# minute digit
INCIDENT = (
    'cd "{root}" && python - <<\'EOF\'\n'
    'print("the by-value fix")\n'
    'EOF\n'
    'cat >> .claude/vlds/dispatch.md <<\'EOF\'\n'
    '  addressed: the by-value fix landed\n'
    'EOF\n'
    'cat >> ledger.md <<\'EOF\'\n'
    '\n'
    '- correction: the first build after the handoff carried a dangling callback reference; two runs were read as a window cause\n'
    '  time: 2026-09-02 12:4x\n'
    'EOF\n'
)


def seed_project():
    root = tempfile.mkdtemp(prefix="vlds-test-")
    store = os.path.join(root, ".claude", "vlds")
    os.makedirs(store)
    shutil.copy(SEED, os.path.join(store, "dispatch.md"))
    with open(os.path.join(store, "ledger.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(LEDGER_HEADER)
    with open(os.path.join(store, "local-storage.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(LOCAL_STORAGE)
    return root, store


def run_hook(sub, payload, root):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, CLAUDE_PLUGIN_ROOT=PLUGIN)
    r = subprocess.run([sys.executable, HOOKS, sub], input=json.dumps(payload).encode("utf-8"),
                       capture_output=True, env=env, timeout=60)
    return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")   # Windows text-mode stdout is CRLF


def run_check(store):
    r = subprocess.run([sys.executable, PHI, "--store", store, "check"], capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")


def decision(out):
    for line in out.splitlines():
        if line.startswith("{"):
            return json.loads(line)["hookSpecificOutput"]
    return None


def bash(cmd, cwd):
    return {"tool_name": "Bash", "cwd": cwd, "tool_input": {"command": cmd}}


def write(path, content, cwd):
    return {"tool_name": "Write", "cwd": cwd, "tool_input": {"file_path": path, "content": content}}


def stamped(v, cwd):
    """A homed ledger append carrying one `time:` value — the gate's clock cases."""
    return bash(f'cat >> .claude/vlds/ledger.md <<\'EOF\'\n- correction: x\n  time: {v}\nEOF\n', cwd)


def norm(p):
    return os.path.normcase(os.path.normpath(p))


def test_pre_write():
    root, store = seed_project()
    try:
        # (a) the incident fence: ask, naming <root>/ledger.md — and the hedged minute
        d = decision(run_hook("pre-write", bash(INCIDENT.format(root=root.replace("\\", "/")), root), root))
        assert d and d["permissionDecision"] == "ask", "(a) no ask on the incident fence"
        reason = d["permissionDecisionReason"]
        assert norm(os.path.join(root, "ledger.md")) in norm(reason), f"(a) stray path not named: {reason}"
        assert "12:4x" in reason, f"(a) placeholder time not named: {reason}"
        assert "dispatch.md resolves to" not in reason, "(a) the homed dispatch append was reported as stray"
        # (b) the same fence homed: nothing for the path, ask for the time
        homed = INCIDENT.format(root=root.replace("\\", "/")).replace("cat >> ledger.md", "cat >> .claude/vlds/ledger.md")
        d = decision(run_hook("pre-write", bash(homed, root), root))
        assert d and "12:4x" in d["permissionDecisionReason"], "(b) placeholder time not asked about"
        assert "outside the store" not in d["permissionDecisionReason"], "(b) homed path reported as stray"
        # (c) time corrected: silence
        fixed = homed.replace("12:4x", "11:27")
        assert run_hook("pre-write", bash(fixed, root), root).strip() == "", "(c) clean fence produced output"
        # (d) a Write to <root>/docs/index.md: ask
        d = decision(run_hook("pre-write", write(os.path.join(root, "docs", "index.md"), "# docs\n", root), root))
        assert d and d["permissionDecision"] == "ask", "(d) docs/index.md not asked about"
        # (e) a Write to the store's index.md: silence
        out = run_hook("pre-write", write(os.path.join(store, "index.md"), "- key: x\n  decision: rule\n", root), root)
        assert out.strip() == "", f"(e) homed Write produced output: {out}"
        # (f) the cd-into-store spelling is homed; a bare spelling with no cd resolves to the root
        out = run_hook("pre-write", bash('cd .claude/vlds && cat >> ledger.md <<\'EOF\'\n- key: x\nEOF\n', root), root)
        assert out.strip() == "", f"(f) cd-into-store spelling reported: {out}"
        d = decision(run_hook("pre-write", bash('cat >> ledger.md <<\'EOF\'\n- key: x\nEOF\n', root), root))
        assert d and "outside the store" in d["permissionDecisionReason"], "(f) bare spelling not asked about"
        # (g) a peer store's file is homed; a Git Bash /e/ spelling resolves; a PowerShell cmdlet is matched
        peer = os.path.join(root, "peer", ".claude", "vlds", "ledger.md").replace("\\", "/")
        assert run_hook("pre-write", bash(f'cat >> "{peer}" <<\'EOF\'\n- key: x\nEOF\n', root), root).strip() == "", \
            "(g) peer store write reported as stray"
        ps = {"tool_name": "PowerShell", "cwd": root,
              "tool_input": {"command": 'Add-Content -Path ledger.md -Value "- key: x"'}}
        d = decision(run_hook("pre-write", ps, root))
        assert d and "outside the store" in d["permissionDecisionReason"], "(g) Add-Content to a bare path not asked about"
        # (h) a runtime placeholder in a generating script is exempt
        gen = 'python - <<\'EOF\'\nwith open(".claude/vlds/ledger.md", "a") as f:\n    f.write(f"  time: {now:%Y-%m-%d %H:%M}\\n")\nEOF\n'
        assert run_hook("pre-write", bash(gen, root), root).strip() == "", "(h) runtime placeholder was flagged"
        # (i) a stamp guessed ahead of the clock: ask, naming the value and the latest now:; a stamp behind the
        # clock and today's date alone are silent; a date past today's asks
        now = datetime.datetime.now()
        ahead = (now + datetime.timedelta(minutes=50)).strftime("%Y-%m-%d %H:%M")
        d = decision(run_hook("pre-write", stamped(ahead, root), root))
        assert d and "guessed-ahead" in d["permissionDecisionReason"] and ahead in d["permissionDecisionReason"], \
            f"(i) a stamp 50 minutes ahead not asked about: {d}"
        assert re.search(r"now: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", d["permissionDecisionReason"]), \
            "(i) the latest now: not named in the ask"
        behind = (now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
        assert run_hook("pre-write", stamped(behind, root), root).strip() == "", "(i) a stamp behind the clock was flagged"
        assert run_hook("pre-write", stamped(now.strftime("%Y-%m-%d"), root), root).strip() == "", \
            "(i) today's date alone was flagged"
        tomorrow = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        d = decision(run_hook("pre-write", stamped(tomorrow, root), root))
        assert d and "guessed-ahead" in d["permissionDecisionReason"], "(i) a date past today's not asked about"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("pre-write: green")


def test_stray_scan():
    root, store = seed_project()
    try:
        with open(os.path.join(root, "ledger.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n- correction: a reading that landed wrong\n  time: 2026-09-02 11:27\n")
        os.makedirs(os.path.join(root, "docs"))
        with open(os.path.join(root, "docs", "index.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# Documentation index\n\nPlain prose here.\n")
        out = run_check(store)
        strays = [l for l in out.splitlines() if l.startswith("[STRAY]")]
        assert len(strays) == 1 and "ledger.md" in strays[0], f"expected one [STRAY] for ledger.md, got: {strays}"
        assert re.search(r"phi\.py check: \d+ corruption, \d+ debt, 1 stray, \d+ notes", out), out.splitlines()[-1]
        # re-homed: the entry appended into the store's ledger, the root file gone
        with open(os.path.join(root, "ledger.md"), encoding="utf-8") as f:
            body = f.read()
        with open(os.path.join(store, "ledger.md"), "a", encoding="utf-8", newline="\n") as f:
            f.write(body)
        os.remove(os.path.join(root, "ledger.md"))
        out = run_check(store)
        assert not [l for l in out.splitlines() if l.startswith("[STRAY]")], "stray still reported after re-home"
        assert "0 stray" in out, out.splitlines()[-1]
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("stray scan: green")


def test_clock_and_post_write():
    root, store = seed_project()
    try:
        out = run_hook("session-open", {"source": "startup", "session_id": "test-session"}, root)
        assert NOW_RE.search(out), f"session-open carries no now: line:\n{out}"
        out = run_hook("prompt-open", {"session_id": "test-session", "prompt": "hello"}, root)
        assert NOW_RE.search(out), f"prompt-open carries no now: line:\n{out}"
        # post-write on the incident fence: the widened trigger runs the check, and [STRAY] names the file
        with open(os.path.join(root, "ledger.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n- correction: a reading that landed wrong\n  time: 2026-09-02 11:27\n")
        out = run_hook("post-write", bash(INCIDENT.format(root=root.replace("\\", "/")), root), root)
        ctx = decision(out)["additionalContext"]
        assert ctx.startswith("now: "), f"post-write context lacks the clock prefix:\n{ctx}"
        assert "[STRAY]" in ctx and "ledger.md" in ctx, f"post-write context lacks the [STRAY] line:\n{ctx}"
        assert "OUTSIDE the store" in ctx, ctx
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("clock + post-write: green")


def test_owner_voice():
    root, store = seed_project()
    try:
        with open(os.path.join(store, "phi-index.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# index\n\n## recall\n\ninject: local-storage.md\ndigest: ledger.md\n")
        with open(os.path.join(store, "dispatch.md"), "a", encoding="utf-8", newline="\n") as f:
            for msg in ("go", "go", "y", "land it", "verify it", "fix this and re-emit the whole plan as one fence"):
                f.write(f'\n- fingerprint: "{msg}"\n  time: 2026-09-03 10:10\n  arrival: turn\n  state: FRESH\n')
        out = run_hook("session-open", {"source": "startup", "session_id": "voice-session"}, root)
        assert "### owner voice" in out, f"no owner-voice block:\n{out}"
        block = out.split("### owner voice", 1)[1].split("### phi.py check", 1)[0]
        assert len(block) <= 1300, f"voice block over the cap: {len(block)}"
        assert '"go" ×3' in block, block   # two dispatch fingerprints plus one local-storage owner-words
        assert "form=fence" in block, block
        assert "median message length" in block, block
        held = run_hook("session-open", {"source": "resume", "session_id": "voice-session"}, root)
        assert "### owner voice" not in held, "voice block printed on a held source"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("owner voice: green")


def test_session_title():
    root, store = seed_project()
    try:
        # (a) the chat title comes from the transcript's LAST custom-title record and names the session, beside
        # its short id, in the prompt hook's header and in the stamp; (b) the .sessions ledger carries it
        transcript = os.path.join(root, "first.jsonl")
        with open(transcript, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"type":"custom-title","customTitle":"Old name","sessionId":"first-session"}\n'
                    '{"type":"user","message":"a line that is not a title"}\n'
                    '{"type":"custom-title","customTitle":"First  session:  the real title","sessionId":"first-session"}\n')
        out = run_hook("prompt-open", {"session_id": "first-session", "prompt": "hello", "transcript_path": transcript}, root)
        assert 'session first-se "First session: the real title"' in out, f"(a) id + title not in the prompt-hook header:\n{out}"
        with open(os.path.join(store, "dispatch.md"), encoding="utf-8") as f:
            assert 'session first-se "First session: the real title"' in f.read(), "(a) id + title not in the stamp"
        with open(os.path.join(store, ".sessions"), encoding="utf-8") as f:
            ledger = f.read()
        assert ledger.strip().endswith("First session: the real title"), f"(b) .sessions lacks the title: {ledger}"
        # (c) a second session with no transcript is named by its short id alone, and its first prompt's pour is
        # named after the id of the session whose rows it holds — the first one
        out = run_hook("prompt-open", {"session_id": "second-session", "prompt": "hi"}, root)
        assert "session second-s" in out and '"' not in out.split("\n")[0], f"(c) short id alone expected:\n{out}"
        poured = [f for f in os.listdir(os.path.join(store, "arc")) if f.startswith("dispatch-")]
        assert len(poured) == 1 and poured[0].endswith("-first-se.md"), f"(c) pour name: {poured}"
        # (d) the check recognizes the pour as the hook's
        assert "hook-poured dispatch record" in run_check(store), "(d) the pour not recognized by check"
        # (e) the transcript lags (no title record yet) but .sessions already holds this session's title — the
        # ledger's title is used; (f) with neither, the prompt hook says so
        empty = os.path.join(root, "empty.jsonl")
        with open(empty, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"type":"mode","mode":"normal","sessionId":"third-session"}\n')
        with open(os.path.join(store, ".sessions"), "a", encoding="utf-8", newline="\n") as f:
            f.write("third-session 2026-09-03 20:00 Ledger title\n")
        out = run_hook("prompt-open", {"session_id": "third-session", "prompt": "hey", "transcript_path": empty}, root)
        assert 'session third-se "Ledger title"' in out, f"(e) the ledger's title not used when the transcript lags:\n{out}"
        assert "title: none yet" not in out, "(e) the none-yet line printed although the ledger had a title"
        out = run_hook("prompt-open", {"session_id": "fourth-session", "prompt": "yo", "transcript_path": empty}, root)
        assert "session fourth-s" in out and "title: none yet" in out, f"(f) the none-yet line missing:\n{out}"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("session title: green")


INDEX_HEAD = """# VLDS φ-Register — Index

Derived — recomputable; an edit to this file is a ruling.

register: 0

## positions

| pos | weight-kb | segment | bytes | pours | span | attached |
| --- | --- | --- | --- | --- | --- | --- |

## hot

| file | live | at-sweep | bytes | budget | watermark | pressure |
| --- | --- | --- | --- | --- | --- | --- |
| local-storage.md | 2 | 2 | 100 | 21 | — | ok |
| logger.md | 0 | 0 | 0 | 34 | — | ok |
| virtual.md | 0 | 0 | 0 | 13 | — | ok |

## recall

inject: local-storage.md
digest: logger.md
{recall}
## epochs

| file | k | a | b |
| --- | --- | --- | --- |

updated: 2026-09-03 10:00 by seed
"""

LOGGER_HEADER = "# VLDS Looper — Logger\n\nTagged entries.\n\n---\n"
VIRTUAL_HEADER = """# VLDS Partition — Virtual

Load-bearing inferences minted this turn.

```yaml
- inference: [the inference]
  time: [YYYY-MM-DD HH:MM]
  basis: [what it was inferred from]
  minted: [session + turn]
  disposition: pending | promoted -> <file> | expired
```

---
"""


def seed_register(store, recall="", logger_entries=0, virtual=()):
    """A bootstrapped-but-empty register plus a logger and a virtual file — what the light sweep reads."""
    with open(os.path.join(store, "phi-index.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(INDEX_HEAD.replace("{recall}", recall))
    with open(os.path.join(store, "logger.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(LOGGER_HEADER)
        for i in range(logger_entries):
            f.write(f"\n- `[gc]` 2026-09-03 {10 + i // 60:02d}:{i % 60:02d} — **Entry {i + 1}.** A logged decision, number {i + 1}.\n")
    with open(os.path.join(store, "virtual.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(VIRTUAL_HEADER)
        for sid, txt in virtual:
            f.write(f"\n- inference: {txt}\n  time: 2026-09-03 10:30\n  basis: a reading\n  minted: session {sid}, turn 1\n  disposition: pending\n")
    os.makedirs(os.path.join(store, "arc"), exist_ok=True)


def count_entries(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    return sum(1 for l in lines[lines.index("---") + 1:] if l.startswith("- "))


def test_pool_mode():
    root, store = seed_project()
    try:
        seed_register(store)
        # (a) the default is the pooled mode: the directive, no hot-file text, silent slots
        out = run_hook("session-open", {"source": "startup", "session_id": "pool-session"}, root)
        assert "the operator subagent, never this context" in out, f"(a) no operator directive:\n{out}"
        assert "operator-prompt.md" in out and "pool-prompt.md" in out and "record.py" in out, \
            f"(a) a brief or the record script missing:\n{out}"
        assert "on sonnet; the barrier" in out and "on haiku)" in out and "at most 4 continuations" in out, \
            f"(a) the per-moment models or the continuation bound missing:\n{out}"
        assert "Launch it once" in out and "SendMessage" in out, f"(a) the one-per-session continuation missing:\n{out}"
        assert "pool: subagent (operator haiku, pool sonnet, sweep sonnet; 4 continuations)" in out, f"(a) the mode line missing:\n{out}"
        assert "the plan goes in the reply" not in out, "(a) a hot-file entry was injected in the pooled mode"
        assert "register: 0" in out and "hot (live/budget)" in out, f"(a) the index digest missing:\n{out}"
        assert "### owner voice" in out, "(a) the owner voice missing in the pooled mode"
        assert run_hook("session-open", {"source": "startup", "session_id": "pool-session"}, root) and \
            run_hook_slot(0, root).strip() == "", "(a) slot 0 printed in the pooled mode"
        # (b) the first prompt carries the nudge; the second does not
        out = run_hook("prompt-open", {"session_id": "pool-session", "prompt": "hello"}, root)
        assert "not yet pooled" in out, f"(b) no nudge on the first prompt:\n{out}"
        out = run_hook("prompt-open", {"session_id": "pool-session", "prompt": "again"}, root)
        assert "not yet pooled" not in out, f"(b) nudge repeated on the second prompt:\n{out}"
        # (c) a compact re-injects this session's pool, and names another session's as not this one's
        with open(os.path.join(store, "recall-pool.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# VLDS Recall Pool\n\nsession: pool-ses \"A title\"\ntask: test the pool\npooled: 2026-09-03 10:00\n\n## steering\n\n- [local-storage 2026-09-03 10:00 LIVE] the plan goes in the reply as one fence\n")
        out = run_hook("session-open", {"source": "compact", "session_id": "pool-session"}, root)
        assert "re-injected after the compact" in out and "task: test the pool" in out, f"(c) pool not re-injected:\n{out}"
        out = run_hook("session-open", {"source": "compact", "session_id": "other-session"}, root)
        assert "belongs to session pool-ses" in out and "task: test the pool" not in out, f"(c) another session's pool re-injected:\n{out}"
        out = run_hook("session-open", {"source": "resume", "session_id": "pool-session"}, root)
        assert "re-injected" not in out, "(c) a resume re-injected the pool"
        # (d) `pool: inject` restores the slot injection; `operator-model:` (or the older `pool-model:`) picks the model
        seed_register(store, recall="pool: inject\n")
        out = run_hook("session-open", {"source": "startup", "session_id": "pool-session"}, root)
        assert "### inject —" in out and "the operator subagent" not in out, f"(d) inject mode not restored:\n{out}"
        assert "the plan goes in the reply" in run_hook_slot(0, root), "(d) slot 0 silent in the inject mode"
        seed_register(store, recall="operator-model: opus\npool-model: haiku\nsweep-model: opus\noperator-moments: 2\n")
        out = run_hook("session-open", {"source": "startup", "session_id": "pool-session"}, root)
        assert "on haiku; the barrier" in out and "on opus)" in out and "at most 2 continuations" in out, \
            f"(d) the model keys or the continuation bound not honoured:\n{out}"
        assert "operator opus, pool haiku, sweep opus; 2 continuations" in out, f"(d) the mode line lacks the models:\n{out}"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("pool mode: green")


def run_hook_slot(slot, root):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, CLAUDE_PLUGIN_ROOT=PLUGIN)
    payload = {"source": "startup", "session_id": "pool-session"}
    r = subprocess.run([sys.executable, HOOKS, "session-open", "--slot", str(slot)],
                       input=json.dumps(payload).encode("utf-8"), capture_output=True, env=env, timeout=60)
    return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")


def test_turn_close():
    root, store = seed_project()
    try:
        seed_register(store, logger_entries=40, virtual=[("other-session", "an inference another session minted"),
                                                          ("test-session", "an inference this session minted")])
        arc = os.path.join(store, "arc")
        with open(os.path.join(arc, "dispatch-20260903-100000-other-se.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# VLDS Partition — Dispatch\n\n---\n\n- fingerprint: \"hello\"\n  time: 2026-09-03 10:00\n  arrival: turn\n")
        # (a) the Stop hook: the logger past its budget pours its oldest down to the low-water mark, the other
        # session's virtual entry expires and pours with them, the record attaches to the child — one child,
        # register 100000 = Zeckendorf(13): 12 logger + 1 virtual (15, 14, 13 would open two positions)
        out = run_hook("turn-close", {"session_id": "test-session", "cwd": root}, root)
        assert out.startswith("turn-close: poured 13 (1 virtual.md, 12 logger.md) into arc-6-a.md"), f"(a) report:\n{out}"
        assert "attached dispatch-20260903-100000-other-se.md to arc-6-a.md" in out, f"(a) the record not attached:\n{out}"
        assert count_entries(os.path.join(store, "logger.md")) == 29, "(a) logger: 40 - 12 poured + the sweep's own entry"
        assert count_entries(os.path.join(store, "virtual.md")) == 1, "(a) this session's virtual entry was poured"
        with open(os.path.join(store, "virtual.md"), encoding="utf-8") as f:
            assert "other session" not in f.read(), "(a) the other session's entry still hot"
        with open(os.path.join(arc, "arc-6-a.md"), encoding="utf-8") as f:
            seg = f.read()
        assert "disposition: expired (turn close" in seg and "Entry 1." in seg and "Entry 12." in seg and "Entry 13." not in seg, \
            "(a) the child holds the wrong entries"
        assert "attached: dispatch-20260903-100000-other-se.md" in seg and "verified: " in seg, "(a) child header incomplete"
        check = run_check(store)
        assert "0 corruption, 0 debt" in check, f"(a) check after the sweep:\n{check}"
        with open(os.path.join(store, "phi-index.md"), encoding="utf-8") as f:
            index = f.read()
        assert "register: 100000" in index and "| logger.md | 29 | 29 |" in index and "| logger.md | 1 | 2 | 3 |" in index, \
            f"(a) index not rewritten:\n{index}"
        assert "inject: local-storage.md" in index, "(a) the recall section was lost in the rewrite"
        # (b) the next prompt prints the report and takes it; a second Stop with nothing to move is silent
        out = run_hook("prompt-open", {"session_id": "test-session", "prompt": "next"}, root)
        assert "- turn-close (" in out and "poured 13" in out, f"(b) report not printed at the next prompt:\n{out}"
        assert not os.path.getsize(os.path.join(store, ".turn-close")), "(b) the report was not taken"
        out = run_hook("turn-close", {"session_id": "test-session", "cwd": root}, root)
        assert out.strip() == "", f"(b) a Stop with nothing to move printed:\n{out}"
        # (c) another session's Stop expires this session's entry: one pour, a fresh position 1 — register 100001
        out = run_hook("turn-close", {"session_id": "third-session", "cwd": root}, root)
        assert "poured 1 (1 virtual.md) into arc-1-a.md" in out and "register 100001" in out, f"(c) report:\n{out}"
        assert count_entries(os.path.join(store, "virtual.md")) == 0, "(c) the entry still hot"
        check = run_check(store)
        assert "0 corruption, 0 debt" in check, f"(c) check:\n{check}"
        # (d) a fresh lock held by another session skips the sweep and says so
        seed_register(store, logger_entries=40)
        with open(os.path.join(arc, ".sweep-lock"), "w", encoding="utf-8", newline="\n") as f:
            f.write("holder-session 2026-09-03 10:00:00\n")
        out = run_hook("turn-close", {"session_id": "test-session", "cwd": root}, root)
        assert "skipped" in out and "holder-session" in out, f"(d) lock not honoured:\n{out}"
        assert count_entries(os.path.join(store, "logger.md")) == 40, "(d) the sweep ran under another session's lock"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("turn-close: green")


def test_barrier():
    root, store = seed_project()
    dispatch = os.path.join(store, "dispatch.md")
    try:
        # (a) a first message resembles no row: FRESH written by the hook, addressed left to the operator
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": "run the acceptance tests again"}, root)
        assert "no earlier row resembles it" in out and "state: FRESH written" in out, f"(a) barrier line:\n{out}"
        with open(dispatch, encoding="utf-8") as f:
            assert f.read().count("  state: FRESH\n") == 1, "(a) FRESH not written into the row"   # the header's shape line reads 'FRESH | ECHO …'
        # (b) a near-repeat: the candidate is named, state left open for the operator
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": "run the acceptance tests again please"}, root)
        assert "resembles 1 earlier row" in out and "state: left open" in out, f"(b) candidate not named:\n{out}"
        with open(dispatch, encoding="utf-8") as f:
            assert f.read().count("  state: FRESH\n") == 1, "(b) FRESH written despite a candidate"
        # (c) a short, unknown message: FRESH, called short and unknown; the identical short message next is a
        # candidate (seen once — not yet a known command); by its third arrival it is a known command: no
        # candidate, FRESH written, the derivation printed from the last row that carried it
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": "ship"}, root)
        assert "short message (1 word), not a known command" in out and "no earlier row resembles it" in out, f"(c) short line:\n{out}"
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": "ship"}, root)
        assert "resembles 1 earlier row" in out and 'latest: "ship"' in out, f"(c) identical short message not a candidate:\n{out}"
        with open(dispatch, "a", encoding="utf-8", newline="\n") as f:
            f.write("  state: FRESH\n  addressed: shipped the build to staging\n")
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": "ship"}, root)
        assert 'short message, known: "ship" ×2' in out and "shipped the build to staging" in out, f"(c) known command not derived:\n{out}"
        assert "state: FRESH written" in out and "state: left open" not in out, \
            f"(c) a known command was treated as a candidate:\n{out}"
        with open(dispatch, encoding="utf-8") as f:
            assert f.read().count("  state: FRESH\n") == 4, "(c) FRESH not written for the known command"   # rows a, c1, the manual c2 completion, c3
        # (d) a task notification is stamped complete on arrival — no barrier, no short line, nothing for the operator
        note = "<task-notification> <task-id>abc</task-id> <status>completed</status> <result>done</result> </task-notification>"
        out = run_hook("prompt-open", {"session_id": "barrier-session", "prompt": note}, root)
        assert "a task notification: its row is complete on arrival" in out, f"(d) notification line missing:\n{out}"
        assert "barrier:" not in out and "short message" not in out, f"(d) barrier or short line printed for a notification:\n{out}"
        with open(dispatch, encoding="utf-8") as f:
            text = f.read()
        assert "  arrival: task notification (stamped" in text and "  addressed: a task notification" in text, \
            "(d) the notification's row not stamped complete"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("barrier: green")


RECORD = """# the turn's record

## dispatch.md
- fingerprint: "run the acceptance tests"
  state: FRESH
  addressed: run, nine groups green

## local-storage.md
- ruling: "the record script closes the turn"
  time: 2026-09-03 10:20
  owner-words: "close it by script"
  scope: durable
  status: LIVE

## local-storage.md
- ruling: "go"
  status: FREED

## logger.md
- `[gc]` 2026-09-03 10:20 — **The record script's first close.** Applied by the test.

## ledger.md
- correction: (a + b)
  time: 2026-09-03 10:2x
  match: x
  meant: y
  delta: z

## ledger.md
- key: (c + d)
  event: surfaced
  outcome: done. 2026-09-03 10:20
  verdict: not a field

## data-store.md
- claim: "nothing"
  time: 2026-09-03 10:20
"""


def test_record():
    root, store = seed_project()
    try:
        with open(os.path.join(store, "logger.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(LOGGER_HEADER)
        run_hook("prompt-open", {"session_id": "record-session", "prompt": "run the acceptance tests"}, root)
        rec = os.path.join(root, "record.md")
        with open(rec, "w", encoding="utf-8", newline="\n") as f:
            f.write(RECORD)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=root, CLAUDE_PLUGIN_ROOT=PLUGIN)
        r = subprocess.run([sys.executable, os.path.join(HERE, "record.py"), "--store", store, "--session", "record-session",
                            "--now", "2026-09-03 10:21", "--record", rec], capture_output=True, env=env, timeout=120)
        out = r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
        assert out.startswith("derivation — close, session record-s, 2026-09-03 10:21 (mechanical: scripts/record.py)"), out
        # appended: the ruling and the logger line; updated: the SPENT 'go' ruling's status and the dispatch row
        assert 'local-storage.md — - ruling: "the record script closes the turn" — 2026-09-03 10:20' in out, out
        assert "logger.md — - `[gc]` 2026-09-03 10:20" in out, out
        assert 'local-storage.md — - ruling: "go" — status' in out, f"upsert by head did not update the 'go' ruling:\n{out}"
        assert 'dispatch.md — - fingerprint: "run the acceptance tests" — state, addressed' in out, out
        # refused: the placeholder time, the field outside the ledger's shape, the file with no header shape match
        assert "placeholder time `2026-09-03 10:2x`" in out, out
        assert "not in the header shape:" in out and "verdict" in out, out   # the seed's ledger header declares the correction shape only
        assert "data-store.md — - claim" in out and "file absent" in out, out
        assert r.returncode == 1, "refusals must exit 1"
        with open(os.path.join(store, "local-storage.md"), encoding="utf-8") as f:
            ls = f.read()
        assert ls.count("- ruling:") == 4 and "  status: FREED" in ls and "  status: SPENT" not in ls, ls[-600:]
        with open(os.path.join(store, "dispatch.md"), encoding="utf-8") as f:
            d = f.read()
        assert "  addressed: run, nine groups green" in d and d.count("  state: FRESH\n") == 1, d[-400:]
        with open(os.path.join(store, "ledger.md"), encoding="utf-8") as f:
            assert "- correction:" not in f.read().split("---", 1)[1], "a refused block was written"
        assert "check: " in out and "phi.py check:" in out, out
        # a dry run writes nothing
        r = subprocess.run([sys.executable, os.path.join(HERE, "record.py"), "--store", store, "--session", "record-session",
                            "--now", "2026-09-03 10:21", "--record", rec, "--dry"], capture_output=True, env=env, timeout=120)
        out = r.stdout.decode("utf-8", "replace")
        assert "dry run — nothing written" in out, out
        with open(os.path.join(store, "local-storage.md"), encoding="utf-8") as f:
            assert f.read().count("- ruling:") == 4, "the dry run wrote"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("record: green")


def test_pour():
    root, store = seed_project()
    try:
        seed_register(store, logger_entries=10)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=root, CLAUDE_PLUGIN_ROOT=PLUGIN)
        norm = os.path.join(HERE, "normalize.py")
        # (a) 4 pours from an empty register: Zeckendorf(4) = [3, 1] opens two positions — refused, the counts
        # that open one named; (b) 3 pours → position 3, accepted and run; (c) a wrong head line is refused
        base = [sys.executable, norm, "--store", store, "--session", "pour-session", "--now", "2026-09-03 10:30"]
        r = subprocess.run(base + ["--pour", "logger.md:7,9,11,13", "--dry"], capture_output=True, env=env, timeout=120)
        out = r.stdout.decode("utf-8", "replace")
        assert "would open 2 positions" in out and "counts that open exactly one: [1, 2, 3, 5, 8" in out, out
        r = subprocess.run(base + ["--pour", "logger.md:7,9,11"], capture_output=True, env=env, timeout=120)
        out = r.stdout.decode("utf-8", "replace")
        assert "sweep: poured 3 (3 logger.md) into arc-3-a.md" in out and "register 100" in out, out
        assert count_entries(os.path.join(store, "logger.md")) == 8, "7 left + the sweep's own entry"
        assert "0 corruption, 0 debt" in run_check(store), run_check(store)
        with open(os.path.join(arc_path := os.path.join(store, "arc"), "arc-3-a.md"), encoding="utf-8") as f:
            seg = f.read()
        assert "Entry 1." in seg and "Entry 2." in seg and "Entry 3." in seg and "Entry 4." not in seg, seg
        r = subprocess.run(base + ["--pour", "logger.md:8", "--dry"], capture_output=True, env=env, timeout=120)
        out = r.stdout.decode("utf-8", "replace")
        assert "line 8 is not an entry head" in out, out
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("pour: green")


def test_check_delta():
    root, store = seed_project()
    try:
        payload = bash('cat >> .claude/vlds/ledger.md <<\'EOF\'\n- correction: x\n  time: 2026-09-02 11:27\nEOF\n', root)
        payload["session_id"] = "delta-session"
        first = decision(run_hook("post-write", payload, root))["additionalContext"]
        second = decision(run_hook("post-write", payload, root))["additionalContext"]
        assert "unchanged since the last check" not in first, first
        assert "unchanged since the last check" in second and "phi.py check:" in second, second
        payload["session_id"] = "another-session"
        third = decision(run_hook("post-write", payload, root))["additionalContext"]
        assert "unchanged" not in third, "(delta) another session's first check came back short"
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("check delta: green")


if __name__ == "__main__":
    test_pre_write()
    test_stray_scan()
    test_clock_and_post_write()
    test_owner_voice()
    test_session_title()
    test_pool_mode()
    test_turn_close()
    test_barrier()
    test_record()
    test_pour()
    test_check_delta()
    print("test_hooks.py: all green")
