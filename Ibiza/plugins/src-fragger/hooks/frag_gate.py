#!/usr/bin/env python3
"""frag_gate.py — src-fragger's mechanical arm: a PreToolUse ask before agent-written code lands in a temp
location.

Subcommand `frag-gate`, reading the harness's JSON payload on stdin (decoded as UTF-8): for a Write or Edit,
the file_path; for a Bash or PowerShell command, every write-position path (redirects, tee, the PowerShell
content cmdlets, python's open() in a write mode, cp / mv destinations). When such a path names a CODE file
(by extension) at a TEMP location (the session scratchpad, /tmp, the user's temp directory, and their spellings),
the gate asks — never denies — and names where a frag belongs: `<store>/src/<task>/`, registered in
`<store>/src/frags.md`.

Silent for everything else: markdown and data files in the scratchpad are working notes, not frags; code under
the project tree is the project's, not a frag. Every failure prints a one-line notice and exits 0 — a gate that
crashes the call it guards is worse than no gate.
"""

import json
import os
import re
import sys

CODE_EXT = {"py", "pyw", "sh", "bash", "zsh", "ps1", "psm1", "bat", "cmd", "js", "mjs", "cjs", "ts", "rb", "pl",
            "lua", "php", "go", "rs", "c", "cc", "cpp", "h", "hpp", "cs", "java", "kt", "swift", "sql", "awk",
            "r", "jl", "scala", "groovy", "tcl", "vbs"}
TEMP_MARKERS = ("/temp/claude/", "/tmp/", "/scratchpad", "/appdata/local/temp/", "/var/folders/", "/private/tmp/",
                "%temp%", "%tmp%", "$tmpdir", "${tmpdir}", "$env:temp", "$env:tmp")
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


def resolve_store(payload):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return os.path.join(root, ".claude", "vlds")


def is_code(path):
    return os.path.splitext(path)[1].lower().lstrip(".") in CODE_EXT


def is_temp(path):
    p = path.replace("\\", "/").lower()
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
            toks = [t.strip("\"'") for t in TOKEN_RE.findall(m.group(1)) if not t.startswith("-")]
            out += toks
    return [p for p in out if p]


def cmd_frag_gate(payload):
    hits = []
    for p in written_paths(payload):
        if is_code(p) and is_temp(p) and p not in hits:
            hits.append(p)
    if not hits:
        return 0
    store = resolve_store(payload)
    named = "; ".join(f"{os.path.basename(p)} at {p}" for p in hits[:3])
    reason = (f"src-fragger: code written to a temp location — {named}. A frag belongs under "
              f"{os.path.join(store, 'src')}{os.sep}<task>{os.sep} and in src{os.sep}frags.md: the scratchpad dies with the "
              f"session and is unreachable when your execution is refused. Proceed only if this file is truly throwaway.")
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
