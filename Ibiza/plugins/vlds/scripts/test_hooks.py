#!/usr/bin/env python3
"""test_hooks.py — acceptance tests for the hooks' write-side mechanics: the `pre-write` gate, the `[STRAY]`
scan, the `now:` clock in every hook output, the widened post-write trigger, and the owner-voice digest.

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
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("session title: green")


if __name__ == "__main__":
    test_pre_write()
    test_stray_scan()
    test_clock_and_post_write()
    test_owner_voice()
    test_session_title()
    print("test_hooks.py: all green")
