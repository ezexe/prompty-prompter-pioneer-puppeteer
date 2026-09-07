#!/usr/bin/env python3
"""test_frag_gate.py — acceptance tests for the frag gate: anything into the harness scratchpad asks, code into
any other temp location asks, code into any project's .claude/scratchpad/ asks (the floor: a frag or a tool
call, never a script there), and files under the store's src/, non-code files in the project's scratchpad, or
the project tree pass. Run from anywhere: python hooks/test_frag_gate.py — exit 0 = green."""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "frag_gate.py")
SCRATCH = "C:/Users/someone/AppData/Local/Temp/claude/E--projects-x/abc123/scratchpad"
STORE_SRC = "E:/projects/x/.claude/vlds/src/sweep-20260903"
PROJECT_PAD = "E:/projects/x/.claude/scratchpad"


def run(payload):
    r = subprocess.run([sys.executable, GATE, "frag-gate"], input=json.dumps(payload).encode("utf-8"),
                       capture_output=True, timeout=60)
    out = r.stdout.decode("utf-8", "replace")
    for line in out.splitlines():
        if line.startswith("{"):
            return json.loads(line)["hookSpecificOutput"]
    assert out.strip() == "", f"unexpected non-JSON output: {out}"
    return None


def write(path):
    return {"tool_name": "Write", "cwd": "E:/projects/x", "tool_input": {"file_path": path, "content": "x"}}


def bash(cmd):
    return {"tool_name": "Bash", "cwd": "E:/projects/x", "tool_input": {"command": cmd}}


def main():
    # the harness scratchpad: everything asks, and the reason names the right home
    d = run(write(f"{SCRATCH}/sweep.py"))
    assert d and d["permissionDecision"] == "ask" and "sweep.py" in d["permissionDecisionReason"], d
    assert "vlds" in d["permissionDecisionReason"] and "src" in d["permissionDecisionReason"], d
    d = run(write(f"{SCRATCH}/commit-msg.txt"))
    assert d and "scratchpad" in d["permissionDecisionReason"], "text in the harness scratchpad passed"
    assert ".claude" in d["permissionDecisionReason"], d
    assert run(write(f"{SCRATCH}/notes.md")) is not None, "notes in the harness scratchpad passed"
    # the project's own homes pass
    assert run(write(f"{STORE_SRC}/sweep.py")) is None, "store frag asked"
    assert run(write(f"{PROJECT_PAD}/commit-msg.txt")) is None, "project scratchpad asked"
    assert run(write(f"{PROJECT_PAD}/run.log")) is None, "a log in the project scratchpad asked"
    assert run(write("E:/projects/x/tools/build.py")) is None, "project code asked"
    # code in a project scratchpad asks, and the ask carries the floor
    d = run(write(f"{PROJECT_PAD}/probe.py"))
    assert d and d["permissionDecision"] == "ask" and "probe.py" in d["permissionDecisionReason"], "code in the project scratchpad passed"
    assert "tool's own call" in d["permissionDecisionReason"] and "frags.md" in d["permissionDecisionReason"], d
    assert run(write(".claude/scratchpad/edit.py")) is not None, "relative code path in the project scratchpad passed"
    assert run(bash("cat > .claude/scratchpad/gen.py <<'EOF'\nprint(1)\nEOF\n")) is not None, "bash heredoc code into the project scratchpad passed"
    assert run(write("E:/other/.claude/scratchpad/swap.py")) is not None, "code in another project's scratchpad passed"
    assert run(write(f"{PROJECT_PAD}/notes.md")) is None, "notes in the project scratchpad asked"
    # other temp locations: code asks, data passes
    assert run(bash("cat > /tmp/probe.sh <<'EOF'\necho hi\nEOF\n")) is not None, "bash temp script passed"
    assert run(bash("cat > /tmp/out.json <<'EOF'\n{}\nEOF\n")) is None, "data in /tmp asked"
    assert run(bash(f'python - <<\'EOF\'\nopen("{SCRATCH}/gen.py", "w").write("x")\nEOF\n')) is not None, "python open to the scratchpad passed"
    assert run(bash(f"cp tools/x.py {SCRATCH}/x.py")) is not None, "cp to the scratchpad passed"
    assert run(bash(f"cat > {STORE_SRC}/sweep.py <<'EOF'\nprint(1)\nEOF\n")) is None, "bash store frag asked"
    assert run(bash("grep -n def /tmp/probe.sh")) is None, "read of a temp script asked"
    ps = {"tool_name": "PowerShell", "cwd": "E:/projects/x",
          "tool_input": {"command": f'Set-Content -Path "{SCRATCH}/run.ps1" -Value "echo hi"'}}
    assert run(ps) is not None, "Set-Content to the scratchpad passed"
    edit = {"tool_name": "Edit", "cwd": "E:/projects/x",
            "tool_input": {"file_path": f"{SCRATCH}/sweep.py", "old_string": "a", "new_string": "b"}}
    assert run(edit) is not None, "Edit of a scratchpad script passed"
    assert run({"tool_name": "Read", "tool_input": {"file_path": f"{SCRATCH}/sweep.py"}}) is None

    # a subagent gets no ask: no hook event injects the contract into a spawned subagent, so its writer was
    # never told, and the human who answers the prompt cannot redirect an agent already running
    for p in (write(f"{SCRATCH}/zz_lines.py"), write(f"{PROJECT_PAD}/probe.py"),
              bash("cat > /tmp/probe.sh <<'EOF'\necho hi\nEOF\n")):
        sub = dict(p, agent_id="agent_01ABC", agent_type="Explore")
        assert run(sub) is None, f"subagent write asked: {p['tool_input']}"
    # ...and the same payload without agent_id still asks, so the suppression is the tell, not the path
    assert run(write(f"{SCRATCH}/zz_lines.py")) is not None, "main-loop scratchpad write stopped asking"

    # the floor's mechanical arm: a read/swap/write-back script is an Edit call in costume, wherever it lands
    COSTUME = ('import pathlib\n'
               'p = pathlib.Path("src/thing.cpp")\n'
               's = p.read_text()\n'
               's = s.replace("oldName", "newName")\n'
               'p.write_text(s)\n')
    d = run({"tool_name": "Write", "cwd": "E:/projects/x",
             "tool_input": {"file_path": f"{STORE_SRC}/swap.py", "content": COSTUME}})
    assert d and d["permissionDecision"] == "ask", "a costume swap script under store/src passed"
    assert "in costume" in d["permissionDecisionReason"], d
    assert "Edit call" in d["permissionDecisionReason"], d
    d = run({"tool_name": "Write", "cwd": "E:/projects/x",
             "tool_input": {"file_path": "E:/projects/x/tools/swap.py", "content": COSTUME}})
    assert d and "in costume" in d["permissionDecisionReason"], "a costume script in the project tree passed"
    # a heredoc carrying the same body is the same costume
    assert run(bash(f"cat > {STORE_SRC}/swap2.py <<'EOF'\n{COSTUME}EOF\n")) is not None, "costume heredoc passed"
    # honest frags are untouched: reads without a swap, writes without a read, and anything long
    assert run({"tool_name": "Write", "cwd": "E:/projects/x",
                "tool_input": {"file_path": f"{STORE_SRC}/scan.py",
                               "content": 'import json\nd = open("a.jsonl").read()\nopen("out.json","w").write(d)\n'}}) is None, \
        "a read-then-write analysis script was called a costume"
    assert run({"tool_name": "Write", "cwd": "E:/projects/x",
                "tool_input": {"file_path": f"{STORE_SRC}/gen.py",
                               "content": 'open("out.txt","w").write("hello")\n'}}) is None, \
        "a plain generator was called a costume"
    assert run({"tool_name": "Write", "cwd": "E:/projects/x",
                "tool_input": {"file_path": f"{STORE_SRC}/big.py",
                               "content": COSTUME + "".join(f"x{i} = {i}\n" for i in range(60))}}) is None, \
        "a long program was called a costume"
    # a costume body under a subagent still says nothing — the ephemeral cases are the subagent's exemption
    assert run({"tool_name": "Write", "cwd": "E:/projects/x", "agent_id": "agent_01ABC",
                "tool_input": {"file_path": f"{STORE_SRC}/swap.py", "content": COSTUME}}) is None, \
        "subagent costume asked"

    # scratch data dropped in the project root asks — and asks for a subagent too, because the file outlives
    # every agent that could have been told and the user is the one who finds it
    for payload in (write("E:/projects/x/_rows.json"), write("_per.json"),
                    bash("python - <<'EOF'\nopen('E:/projects/x/dump.jsonl','w').write('x')\nEOF\n")):
        d = run(payload)
        assert d and d["permissionDecision"] == "ask", f"root data file passed: {payload['tool_input']}"
        assert "project root" in d["permissionDecisionReason"], d
    d = run(dict(write("E:/projects/x/_rows.json"), agent_id="agent_01ABC", agent_type="Explore"))
    assert d and "project root" in d["permissionDecisionReason"], "subagent root dump passed"
    # the project's own root files are not scratch, and neither is anything in a subdirectory
    for ok in ("E:/projects/x/package.json", "E:/projects/x/settings.json", "E:/projects/x/requirements.txt",
               "E:/projects/x/Ibiza/.claude-plugin/marketplace.json", "E:/projects/x/data/rows.json",
               "E:/projects/x/README.md", "E:/projects/x/tools/build.py"):
        assert run(write(ok)) is None, f"a legitimate file asked: {ok}"
    print("test_frag_gate.py: all green")


if __name__ == "__main__":
    main()
