#!/usr/bin/env python3
"""test_frag_gate.py — acceptance tests for the frag gate: code to a temp location asks, code under the store's
src/ or the project tree passes, notes in the scratchpad pass. Run from anywhere: python hooks/test_frag_gate.py
— exit 0 = green."""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "frag_gate.py")
SCRATCH = "C:/Users/someone/AppData/Local/Temp/claude/E--projects-x/abc123/scratchpad"
STORE_SRC = "E:/projects/x/.claude/vlds/src/sweep-20260903"


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
    d = run(write(f"{SCRATCH}/sweep.py"))
    assert d and d["permissionDecision"] == "ask" and "sweep.py" in d["permissionDecisionReason"], d
    assert "src" in d["permissionDecisionReason"], d
    assert run(write(f"{STORE_SRC}/sweep.py")) is None, "store frag asked"
    assert run(write("E:/projects/x/tools/build.py")) is None, "project code asked"
    assert run(write(f"{SCRATCH}/notes.md")) is None, "scratchpad notes asked"
    assert run(write(f"{SCRATCH}/commit-msg.txt")) is None, "scratchpad text asked"
    assert run(bash("cat > /tmp/probe.sh <<'EOF'\necho hi\nEOF\n")) is not None, "bash temp script passed"
    assert run(bash(f'python - <<\'EOF\'\nopen("{SCRATCH}/gen.py", "w").write("x")\nEOF\n')) is not None, "python open to temp passed"
    assert run(bash(f"cp tools/x.py {SCRATCH}/x.py")) is not None, "cp to temp passed"
    assert run(bash(f"cat > {STORE_SRC}/sweep.py <<'EOF'\nprint(1)\nEOF\n")) is None, "bash store frag asked"
    assert run(bash("grep -n def /tmp/probe.sh")) is None, "read of a temp script asked"
    ps = {"tool_name": "PowerShell", "cwd": "E:/projects/x",
          "tool_input": {"command": f'Set-Content -Path "{SCRATCH}/run.ps1" -Value "echo hi"'}}
    assert run(ps) is not None, "Set-Content to temp passed"
    edit = {"tool_name": "Edit", "cwd": "E:/projects/x",
            "tool_input": {"file_path": f"{SCRATCH}/sweep.py", "old_string": "a", "new_string": "b"}}
    assert run(edit) is not None, "Edit of a temp script passed"
    assert run({"tool_name": "Read", "tool_input": {"file_path": f"{SCRATCH}/sweep.py"}}) is None
    print("test_frag_gate.py: all green")


if __name__ == "__main__":
    main()
