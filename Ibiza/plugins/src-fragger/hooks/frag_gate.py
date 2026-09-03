#!/usr/bin/env python3
"""frag_gate.py — src-fragger's mechanical arm: a PreToolUse ask before agent-written files land where they die.

Subcommand `frag-gate`, reading the harness's JSON payload on stdin (decoded as UTF-8): for a Write or Edit,
the file_path; for a Bash or PowerShell command, every write-position path (redirects, tee, the PowerShell
content cmdlets, python's open() in a write mode, cp / mv destinations). Two cases ask — never deny:

  the harness scratchpad   ANY file written into the per-session temp directory the system prompt names
                           (`.../Temp/claude/<project>/<session>/scratchpad/`): code belongs under
                           `<store>/src/<task>/` as a frag; everything else belongs under the project's own
                           `.claude/scratchpad/`, which the user can see and which outlives the session
  any other temp location  a CODE file (by extension) written to /tmp, the user's temp directory, and their
                           spellings — a frag belongs under `<store>/src/<task>/`

Silent for everything else: files under the project tree are the project's; data a tool drops in /tmp is
normal. Every failure prints a one-line notice and exits 0 — a gate that crashes the call it guards is worse
than no gate.
"""

import json
import os
import re
import sys

CODE_EXT = {"py", "pyw", "sh", "bash", "zsh", "ps1", "psm1", "bat", "cmd", "js", "mjs", "cjs", "ts", "rb", "pl",
            "lua", "php", "go", "rs", "c", "cc", "cpp", "h", "hpp", "cs", "java", "kt", "swift", "sql", "awk",
            "r", "jl", "scala", "groovy", "tcl", "vbs"}
SCRATCHPAD_MARKERS = ("/temp/claude/", "/tmp/claude/")          # the harness's per-session scratchpad
TEMP_MARKERS = ("/tmp/", "/appdata/local/temp/", "/var/folders/", "/private/tmp/", "%temp%", "%tmp%",
                "$tmpdir", "${tmpdir}", "$env:temp", "$env:tmp")
_PATH = r"(?:\"([^\"\n]+)\"|'([^'\n]+)'|([^\s\"'<>|;&()`]+))"
WRITE_RES = [
    re.compile(r">{1,2}[ \t]*" + _PATH),
    re.compile(r"\btee\b(?:[ \t]+-[A-Za-z]+)*[ \t]+" + _PATH),
    re.compile(r"\bopen\(\s*(?:\"([^\"\n]+)\"|'([^'\n]+)')\s*,\s*[\"'][aw]"),
]
ARGS_RES = [
    re.compile(r"\b(?:Set-Content|Add-Content|Out-File)\b([^\n|;]*)"),
    re.compile(r"\b(?:cp|mv|Copy-Item|Move-Item)\b([^\n|;&]*)"),
]
TOKEN_RE = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'|\S+")


def payload_from_stdin():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def project_root(payload):
    return os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()


def is_code(path):
    return os.path.splitext(path)[1].lower().lstrip(".") in CODE_EXT


def _norm(path):
    return path.replace("\\", "/").lower()


def in_scratchpad(path):
    p = _norm(path)
    return any(m in p for m in SCRATCHPAD_MARKERS) and "/scratchpad" in p


def in_temp(path):
    p = _norm(path)
    return any(m in p for m in TEMP_MARKERS)


def _first(m):
    return next((g for g in m.groups() if g), "")


def written_paths(payload):
    tool = str(payload.get("tool_name") or "")
    inp = payload.get("tool_input") or {}
    if not isinstance(inp, dict):
        return []
    if tool in ("Write", "Edit", "NotebookEdit"):
        fp = str(inp.get("file_path") or "")
        return [fp] if fp else []
    if tool not in ("Bash", "PowerShell"):
        return []
    cmd = str(inp.get("command") or "")
    out = []
    for rx in WRITE_RES:
        out += [_first(m) for m in rx.finditer(cmd)]
    for rx in ARGS_RES:
        for m in rx.finditer(cmd):
            out += [t.strip("\"'") for t in TOKEN_RE.findall(m.group(1)) if not t.startswith("-")]
    return [p for p in out if p]


def cmd_frag_gate(payload):
    root = project_root(payload)
    src = os.path.join(root, ".claude", "vlds", "src")
    pad = os.path.join(root, ".claude", "scratchpad")
    reasons = []
    seen = set()
    for p in written_paths(payload):
        if p in seen:
            continue
        seen.add(p)
        name = os.path.basename(p)
        if in_scratchpad(p):
            home = f"{src}{os.sep}<task>{os.sep} as a registered frag" if is_code(p) else pad
            reasons.append(f"{name} is headed for the harness's per-session scratchpad ({p}) — it belongs under {home}: "
                           f"that directory is named after a session id, invisible to the user, and gone with the session")
        elif in_temp(p) and is_code(p):
            reasons.append(f"{name} is code headed for a temp location ({p}) — a frag belongs under {src}{os.sep}<task>{os.sep} "
                           f"and in src{os.sep}frags.md")
    if not reasons:
        return 0
    reason = "src-fragger: " + "; ".join(reasons[:3]) + ". Proceed only if this file is truly throwaway."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": reason}}))
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sub = sys.argv[1] if len(sys.argv) > 1 else ""
    payload = payload_from_stdin()
    try:
        if sub == "frag-gate":
            return cmd_frag_gate(payload)
        print(f"frag_gate.py: unknown subcommand {sub!r}")
        return 0
    except Exception as e:  # noqa: BLE001 — a gate degrades, never raises
        print(f"src-fragger ({sub}) degraded: {type(e).__name__}: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
