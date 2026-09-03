#!/usr/bin/env python3
"""vlds_hooks.py — the VLDS plugin's hook bodies: mechanical and judgment-free, in the phi.py mold.

Subcommands, each reading the harness's JSON payload on stdin (decoded as UTF-8 — the harness writes UTF-8
whatever the console codepage says):
  session-open            SessionStart, the recall's index slot: print the clock (`now:`), phi-index.md, the
                          inject/digest lists, a digest line per digest file, the owner-voice digest, and the
                          verdict of `phi.py check`. On `source` resume, fork, or compact print only the clock,
                          the digest lines, and the verdict — the conversation already holds its own recall —
                          and record the session id in `.sessions`, so a fork's first prompt (a new id over a
                          live conversation) and a pre-hook session's next prompt do not pour rows that are
                          still live.
  session-open --slot N   SessionStart, one chunk slot: the index's `inject:` files are split at entry boundaries
                          into chunks under the harness's per-hook output cap, and slot N prints the N-th chunk
                          (header with the first chunk of each file). Nothing on resume / fork / compact, nothing
                          when the plan is shorter than N+1. One hook per slot, because the harness caps EACH
                          hook's output at 10,000 characters: one process printing everything would be spilled
                          to a file and replaced by a preview. A single entry over the cap, or a chunk beyond the
                          registered slots, arrives as a marker line to read by hand.
  prompt-open             UserPromptSubmit: print the clock, stamp the message's dispatch row (fingerprint /
                          time / arrival; the model completes state and addressed) and, on the FIRST prompt a
                          session id ever submits, pour dispatch.md whole-file into arc/ — a sha-verified
                          byte-identical copy, then a reseed that preserves the file's own header (a user's
                          header edit is a ruling).
  pre-write               PreToolUse: when a Write, Edit, Bash, or PowerShell call is about to write a file
                          that carries a store file's NAME, ask before it lands anywhere but a `.claude/vlds/`
                          directory (the path is resolved against the call's cwd and any `cd` earlier in the
                          same command — a bare `ledger.md` that was true under one `cd` is false under
                          another), ask before a persisted entry carries a placeholder `time:` (`12:4x`,
                          `TBD`) instead of a stamp copied from the stream's `now:`, and ask before one carries
                          a `time:` guessed AHEAD of the clock — later than the write's own `now:` by more than
                          a minute (one session stamped rows up to fifty minutes ahead). Silent otherwise. Always
                          `ask`, never `deny`: `index.md` and `ledger.md` are legitimate names in a docs tree,
                          and only the user can say which this one is.
  post-write              PostToolUse: when a Write, Edit, Bash, or PowerShell call touched the store, or wrote
                          a store-named file anywhere, print the clock and run `phi.py check`, handing its
                          verdict back as additionalContext — a mis-homed write is followed at once by a check
                          whose `[STRAY]` line names the file.

Everything here is mechanical. The stamp carries no judgment; the pour moves a file whose every entry belongs to
a conversation that is not this one (a new id that reaches its first prompt unrecorded) and destroys nothing (the
copy is verified before the reseed, and the copy stays); the check only reports; the pre-write gate only asks.
What the hooks never do: register the poured file in the index (a sweep's judged act), pour any other hot file
(cold spans are scored, not counted), complete a dispatch row (state and addressed are the model's), delete or
move a stray file (the user disposes of it), or block a prompt — every failure prints a one-line notice and
exits 0.

The clock: every subcommand's output carries a `now: YYYY-MM-DD HH:MM` line, so a store write anywhere in the
turn has an authoritative stamp to copy — the model never guesses a digit.

First-prompt detection: `<store>/.sessions` holds one line per session id that has submitted a prompt or been
recorded at a resume / fork / compact start. An id absent from it at its first prompt is a new session; a resumed
conversation keeps its id, a fork is recorded at its SessionStart, and a transient SessionStart firing never
submits a prompt — so a live conversation's rows are never poured out from under it.
"""

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter

DEFAULT_INJECT = ["local-storage.md", "index.md", "tombstones.md", "ledger.md", "session-storage.md",
                  "virtual.md"]
DEFAULT_DIGEST = ["data-store.md", "logger.md"]
LOCK_STALE_S = 3600
FINGERPRINT_CHARS = 200
HOOK_OUTPUT_CAP = 10000     # the harness's per-hook output cap, in characters
SLOT_BUDGET = 9500          # what one slot may print, head line included, to stay under the cap
SLOT_HEAD = 200             # reserved for the slot's head line when chunking
SLOTS = 12                  # slots hooks.json registers: --slot 0 .. --slot 11
HELD_SOURCES = ("resume", "fork", "compact")   # SessionStart sources whose conversation holds its own recall
# the store's file names — the same set as scripts/phi.py STORE_FILES; a file carrying one of these names
# outside a `.claude/vlds/` directory is what the pre-write gate asks about and the check reports as [STRAY]
STORE_FILES = {"dispatch.md", "index.md", "ledger.md", "logger.md", "tombstones.md", "virtual.md",
               "session-storage.md", "local-storage.md", "data-store.md", "phi-index.md"}
NOW_FMT = "%Y-%m-%d %H:%M"
VOICE_CAP = 1200            # the owner-voice digest's size cap, in characters
VOICE_TOKEN_WORDS = 3       # a message of at most this many words counts as an adoption token
VOICE_TOKENS = 10           # how many adoption tokens the digest lists
VOICE_RULINGS = 5           # how many delivery-form rulings the digest lists
VOICE_FORM_WORDS = ("fence", "file", "message", "artifact", "text box")


def payload_from_stdin():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def resolve_store(payload):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return os.path.join(root, ".claude", "vlds")


def plugin_root():
    return os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def sha12(data):
    return hashlib.sha256(data).hexdigest()[:12]


def session_tag(payload):
    sid = str(payload.get("session_id") or "unknown")
    return sid, sid[:8]


def now_line(now):
    """The clock line every hook output carries — the one value a `time:` field is copied from."""
    return f"now: {now:{NOW_FMT}}"


def split_header(data):
    """Return (header_bytes, separator_bytes, body_bytes) at the first column-0 '---' line, or None."""
    for sep in (b"\n---\n", b"\n---\r\n"):
        i = data.find(sep)
        if i >= 0:
            return data[:i], sep, data[i + len(sep):]
    return None


def entry_lines(text, after_separator=True):
    """Column-0 '- ' lines — after the header separator when the text is a whole file, everywhere when the
    text is already a body (a stray '---' after the last entry must not hide the entries before it)."""
    lines = text.split("\n")
    start = 0
    if after_separator:
        try:
            start = lines.index("---") + 1
        except ValueError:
            start = 0
    return [l for l in lines[start:] if l.startswith("- ")]


def run_check(store):
    phi = os.path.join(plugin_root(), "scripts", "phi.py")
    if not os.path.exists(phi):
        return "phi.py not found beside the hooks — check skipped"
    try:
        r = subprocess.run([sys.executable or "python3", phi, "--store", store, "check"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=20)
    except Exception as e:  # noqa: BLE001 — a hook degrades, never raises
        return f"phi.py check could not run: {e}"
    out = (r.stdout or "").strip()
    return out if out else f"phi.py check produced no output (exit {r.returncode})"


def check_summary(store):
    """The verdict line plus every CORRUPT, DEBT, and STRAY line; notes are counted, not listed."""
    out = run_check(store)
    lines = out.split("\n")
    keep = [l for l in lines if l.startswith("[CORRUPT]") or l.startswith("[DEBT]") or l.startswith("[STRAY]")
            or l.startswith("phi.py check")]
    notes = sum(1 for l in lines if l.startswith("[note]"))
    if not keep:
        return out
    if notes:
        keep.append(f"({notes} note(s) withheld — judged-repair items; run `phi.py check` to list them)")
    return "\n".join(keep)


def record_seen(store, sid, now):
    """True when this session id was not yet in `.sessions`; records it either way."""
    ledger = os.path.join(store, ".sessions")
    seen = set()
    if os.path.exists(ledger):
        seen = {l.split(" ", 1)[0] for l in read_text(ledger).split("\n") if l.strip()}
    if sid in seen:
        return False
    with open(ledger, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"{sid} {now:{NOW_FMT}}\n")
    return True


# ─── the store-path matcher (pre-write and post-write share it) ─────────────────────────────────────────

_STORE_ALT = "|".join(re.escape(f) for f in sorted(STORE_FILES))
_QUOTED = r"(?:[A-Za-z]:)?[^\"'<>|;&\n]*?(?:%s)" % _STORE_ALT      # inside quotes: spaces allowed
_BARE = r"(?:[A-Za-z]:)?[^\s\"'<>|;&()`]*?(?:%s)" % _STORE_ALT     # unquoted: stops at whitespace
_PATH = r"(?:\"(%s)\"|'(%s)'|(%s))(?![\w.-])" % (_QUOTED, _QUOTED, _BARE)
_PY_PATH = r"(?:\"(%s)\"|'(%s)')" % (_QUOTED, _QUOTED)
# write positions in a shell command: redirects, tee, the PowerShell content cmdlets, python's open() in a
# write mode and Path().write_*; cp / mv / Copy-Item / Move-Item destinations are handled by COPY_RE
WRITE_RES = [
    re.compile(r">{1,2}[ \t]*" + _PATH),
    re.compile(r"\btee\b(?:[ \t]+-[A-Za-z]+)*[ \t]+" + _PATH),
    re.compile(r"\b(?:Set-Content|Add-Content|Out-File)\b[^\n|;]*?" + _PATH),
    re.compile(r"\bopen\(\s*" + _PY_PATH + r"\s*,\s*[\"'][aw]\+?b?[\"']"),
    re.compile(r"\bPath\(\s*" + _PY_PATH + r"\s*\)\.(?:write_text|write_bytes|open)\("),
]
COPY_RE = re.compile(r"\b(?:cp|mv|Copy-Item|Move-Item)\b((?:[ \t]+(?:-\S+|\"[^\"\n]*\"|'[^'\n]*'|[^\s;&|>]+))+)")
CD_RE = re.compile(r"(?:^|&&|\|\||;|\n)[ \t]*(?:cd|Set-Location|pushd)[ \t]+(?:\"([^\"\n]+)\"|'([^'\n]+)'|([^\s;&|]+))")
HEREDOC_RE = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?=\r?\n|$)", re.S)
PS_HERE_RE = re.compile(r"@(['\"])\r?\n(.*?)\r?\n\1@", re.S)
SH_QUOTED_RE = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", re.S)
TIME_FIELD_RE = re.compile(r"^[ \t]*(?:- )?time:[ \t]*(.*?)[ \t]*$", re.M)
TIME_OK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?$")
STORE_TAIL = os.path.normcase(os.sep + ".claude" + os.sep + "vlds")


def _resolve(path, cwd):
    """An absolute, normalized path for a spelling in a command — relative spellings against `cwd`."""
    p = path.strip()
    m = re.match(r"^/([A-Za-z])/(.*)$", p)
    if m and os.name == "nt":          # Git Bash spells E:/ as /e/
        p = f"{m.group(1).upper()}:/{m.group(2)}"
    if not os.path.isabs(p) and not re.match(r"^[A-Za-z]:", p):
        p = os.path.join(cwd, p)
    return os.path.normpath(os.path.abspath(p))


def _homed(abs_path):
    """True when the file sits directly in a `.claude/vlds/` directory — this store's or a peer store's (a
    session legitimately writes a peer store's files; a bare spelling that lands in a repo root does not)."""
    return os.path.normcase(os.path.dirname(abs_path)).endswith(STORE_TAIL)


def _first_group(m):
    return next((g for g in m.groups() if g), "")


def write_targets(payload):
    """[(spelled, absolute)] — every store-NAMED file the call is about to write: a Write/Edit file_path, or
    each write-position path in a shell command, resolved against the payload's cwd and any `cd` earlier in
    the same command (that is exactly how a bare spelling goes wrong). Empty when nothing store-named is
    written."""
    tool = str(payload.get("tool_name") or "")
    inp = payload.get("tool_input") or {}
    if not isinstance(inp, dict):
        return []
    cwd = str(payload.get("cwd") or os.getcwd())
    if tool in ("Write", "Edit", "NotebookEdit"):
        fp = str(inp.get("file_path") or "")
        if fp and os.path.basename(fp) in STORE_FILES:
            return [(fp, _resolve(fp, cwd))]
        return []
    if tool not in ("Bash", "PowerShell"):
        return []
    cmd = str(inp.get("command") or "")
    if not any(f in cmd for f in STORE_FILES):
        return []
    events = []
    for m in CD_RE.finditer(cmd):
        events.append((m.start(), "cd", _first_group(m)))
    for rx in WRITE_RES:
        for m in rx.finditer(cmd):
            events.append((m.start(), "write", _first_group(m)))
    for m in COPY_RE.finditer(cmd):
        args = [a for a in re.findall(r"\"[^\"\n]*\"|'[^'\n]*'|\S+", m.group(1)) if not a.startswith("-")]
        if len(args) >= 2:
            dest = args[-1].strip("\"'")
            if os.path.basename(dest) in STORE_FILES:
                events.append((m.start(), "write", dest))
    out, seen = [], set()
    for _off, kind, value in sorted(events, key=lambda e: e[0]):
        if kind == "cd":
            cwd = _resolve(value, cwd)
            continue
        if not value or os.path.basename(value) not in STORE_FILES:
            continue
        a = _resolve(value, cwd)
        key = os.path.normcase(a)
        if key not in seen:
            seen.add(key)
            out.append((value, a))
    return out


def stray_targets(payload):
    """The subset of write_targets() that lands outside every `.claude/vlds/` directory."""
    return [(s, a) for s, a in write_targets(payload) if not _homed(a)]


def written_text(payload):
    """The text a call persists: a Write's content, an Edit's new_string, or — for a shell command — every
    heredoc body, PowerShell here-string, and quoted argument (a `printf '...' >> file` persists too)."""
    tool = str(payload.get("tool_name") or "")
    inp = payload.get("tool_input") or {}
    if not isinstance(inp, dict):
        return ""
    if tool == "Write":
        return str(inp.get("content") or "")
    if tool == "Edit":
        return str(inp.get("new_string") or "")
    if tool in ("Bash", "PowerShell"):
        cmd = str(inp.get("command") or "")
        bodies = [m.group(3) for m in HEREDOC_RE.finditer(cmd)]
        bodies += [m.group(2) for m in PS_HERE_RE.finditer(cmd)]
        bodies += [(m.group(1) or m.group(2) or "").replace("\\n", "\n") for m in SH_QUOTED_RE.finditer(cmd)]
        return "\n".join(bodies)
    return ""


def placeholder_times(text):
    """Every `time:` value in the text that is not a stamp: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`, digits only.
    Exempt: an empty value, a bracketed template (`[YYYY-MM-DD HH:MM]` in a header shape), and a value holding
    a runtime placeholder (`{now:...}`, `$now`, `%H`) — those do not survive as literals, which is R2's own
    allowance. A trailing `# comment` is ignored."""
    bad = []
    for m in TIME_FIELD_RE.finditer(text):
        v = re.sub(r"\s+#.*$", "", m.group(1)).strip().strip("\"'")
        if not v or v.startswith("[") or any(c in v for c in "{$%"):
            continue
        if not TIME_OK_RE.match(v) and v not in bad:
            bad.append(v)
    return bad


FUTURE_SLACK = datetime.timedelta(minutes=1)   # a write that straddles a minute boundary is not a guess


def future_times(text, now):
    """Every well-formed `time:` value in the text that lies LATER than `now` by more than FUTURE_SLACK — a stamp
    guessed ahead of the clock rather than copied from it (one session stamped rows up to fifty minutes past the
    hook stream's `now:`). A date-only value counts when its date is past today's. Same exemptions as
    placeholder_times(); a value that does not parse is that scan's finding, not this one's."""
    bad = []
    limit = now + FUTURE_SLACK
    for m in TIME_FIELD_RE.finditer(text):
        v = re.sub(r"\s+#.*$", "", m.group(1)).strip().strip("\"'")
        if not v or v.startswith("[") or any(c in v for c in "{$%") or not TIME_OK_RE.match(v):
            continue
        clocked = " " in v
        try:
            stamp = datetime.datetime.strptime(v, NOW_FMT if clocked else "%Y-%m-%d")
        except ValueError:
            continue    # well-shaped but impossible (a 13th month) — not a guess ahead, and not this scan's call
        if (stamp > limit if clocked else stamp.date() > now.date()) and v not in bad:
            bad.append(v)
    return bad


# ─── session-open ───────────────────────────────────────────────────────────────────────────────────────

def recall_lists(index_text):
    """(inject, digest, from_index) — the lists under the index's `## recall` section, or the defaults."""
    inject, digest = None, None
    in_recall = False
    for l in index_text.split("\n"):
        if l.startswith("## "):
            in_recall = l[3:].strip().lower() == "recall"
            continue
        if not in_recall:
            continue
        m = re.match(r"^(inject|digest):\s*(.*)$", l.strip())
        if m:
            names = [n.strip() for n in m.group(2).split(",") if n.strip()]
            if m.group(1) == "inject":
                inject = names
            else:
                digest = names
    return (inject if inject is not None else DEFAULT_INJECT,
            digest if digest is not None else DEFAULT_DIGEST,
            inject is not None or digest is not None)


def digest_line(store, fname):
    path = os.path.join(store, fname)
    if not os.path.exists(path):
        return f"- {fname} — absent"
    entries = entry_lines(read_text(path))
    last = entries[-1][:100] if entries else "(no entries)"
    return f"- {fname} — {len(entries)} entries, {os.path.getsize(path):,} B; last: {last}"


def session_source(payload):
    return str(payload.get("source") or payload.get("mode") or "startup")


def split_entries(text):
    """(header, [entry blocks]) — the header runs up to and including the first column-0 '---' line; entry
    blocks are column-0 '- ' lines with their continuation lines, in order; prose before the first entry rides
    as the first block, prose after the last entry with the last."""
    lines = text.split("\n")
    try:
        sep = lines.index("---")
    except ValueError:
        sep = -1
    header = "\n".join(lines[:sep + 1]) if sep >= 0 else ""
    blocks, cur = [], []
    for l in lines[sep + 1:]:
        if l.startswith("- ") and cur:
            blocks.append("\n".join(cur))
            cur = []
        cur.append(l)
    if cur:
        blocks.append("\n".join(cur))
    return header, blocks


def chunk_plan(store, inject):
    """[(fname, part, parts, text)] — every inject file split at entry boundaries into chunks that fit a slot.
    Deterministic from the files alone, so every slot process computes the same plan."""
    plan = []
    for fname in inject:
        path = os.path.join(store, fname)
        if not os.path.exists(path):
            plan.append((fname, 1, 1, None))
            continue
        header, blocks = split_entries(read_text(path).rstrip("\n"))
        chunks, cur = [], header
        for b in blocks:
            cand = (cur + "\n" + b) if cur else b
            if len(cand) > SLOT_BUDGET - SLOT_HEAD and cur:
                chunks.append(cur)
                cur = b
            else:
                cur = cand
        if cur or not chunks:
            chunks.append(cur)
        for i, c in enumerate(chunks, 1):
            plan.append((fname, i, len(chunks), c))
    return plan


def plan_label(item):
    fname, part, parts, _text = item
    return fname if parts == 1 else f"{fname} (part {part}/{parts})"


def cmd_session_slot(payload, store, slot):
    """One chunk per hook output — the only way past the per-hook cap."""
    if session_source(payload) in HELD_SOURCES:
        return 0
    index_path = os.path.join(store, "phi-index.md")
    if not os.path.exists(index_path):
        return 0
    inject, _digest, _from_index = recall_lists(read_text(index_path))
    plan = chunk_plan(store, inject)
    if slot >= len(plan):
        return 0
    item = plan[slot]
    fname, _part, _parts, text = item
    head = f"### {plan_label(item)} — recall slot {slot} (SessionStart hook; every item still passes the gc read barrier)"
    print(head)
    if text is None:
        print("(absent)")
    elif len(head) + len(text) + 2 > SLOT_BUDGET:
        print(f"NOT injected: this part alone is {len(text):,} characters, over the harness's {HOOK_OUTPUT_CAP:,}-"
              f"character hook-output cap — read it by hand before anything in it steers")
        print(digest_line(store, fname))
    else:
        print(text)
    return 0


# ─── the owner-voice digest ─────────────────────────────────────────────────────────────────────────────

FIELD_RE = re.compile(r"^[ \t]*(?:- )?(owner-words|fingerprint|by):[ \t]*(.*?)[ \t]*$", re.M)


def _field_value(raw):
    v = raw.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def _token(text):
    t = text.lower().replace("…", " ").replace("\u2019", "'")
    t = re.sub(r"[^\w\s'/-]", " ", t)
    return " ".join(t.split())


def voice_corpus(store):
    """Every verbatim owner field in the store: owner-words and by in the hot files, fingerprint in
    dispatch.md and every poured dispatch record under arc/. Header template lines ([...] values) are skipped."""
    texts = []
    paths = [os.path.join(store, f) for f in ("local-storage.md", "tombstones.md", "dispatch.md")]
    arc = os.path.join(store, "arc")
    if os.path.isdir(arc):
        paths += [os.path.join(arc, f) for f in sorted(os.listdir(arc))
                  if f.startswith("dispatch-") and f.endswith(".md")]
    for p in paths:
        if not os.path.exists(p):
            continue
        for m in FIELD_RE.finditer(read_text(p)):
            v = _field_value(m.group(2))
            if v and not v.startswith("["):
                texts.append(v)
    return texts


def voice_rulings(store):
    """[(time, form, owner-words)] for every local-storage ruling that carries a `form:` field or whose
    owner-words name a delivery form — in file order, so the tail is the latest."""
    path = os.path.join(store, "local-storage.md")
    if not os.path.exists(path):
        return []
    _header, blocks = split_entries(read_text(path))
    out = []
    for b in blocks:
        if not b.startswith("- "):
            continue
        fields = {}
        for l in b.split("\n"):
            mm = re.match(r"^(?:- |  )([a-z-]+):[ \t]*(.*?)[ \t]*$", l)
            if mm and mm.group(1) not in fields:
                fields[mm.group(1)] = mm.group(2)
        words = _field_value(fields.get("owner-words", ""))
        form = _field_value(fields.get("form", ""))
        if not words or words.startswith("["):
            continue
        low = words.lower()
        if form or any(w in low for w in VOICE_FORM_WORDS):
            out.append((fields.get("time", "").strip(), form, words))
    return out


def owner_voice(store):
    """The `### owner voice` block: a mechanical digest of the store's verbatim owner fields — median message
    length, the most frequent short messages (adoption tokens), and the latest delivery-form rulings. No
    judgment here; the model derives a short, typo'd, or truncated message's intent from it before asking."""
    texts = voice_corpus(store)
    if not texts:
        return None
    lengths = sorted(len(t) for t in texts)
    median = lengths[len(lengths) // 2]
    tokens = Counter(_token(t) for t in texts if 0 < len(_token(t).split()) <= VOICE_TOKEN_WORDS)
    top = tokens.most_common(VOICE_TOKENS)
    rulings = voice_rulings(store)[-VOICE_RULINGS:]
    lines = [f"### owner voice (mechanical digest of {len(texts)} verbatim owner fields — derive a short, typo'd, "
             f"or truncated message's intent from these before asking)",
             f"- median message length: {median} characters"]
    if top:
        lines.append(f"- adoption tokens (most frequent messages of at most {VOICE_TOKEN_WORDS} words): "
                     + ", ".join(f'"{t}" ×{c}' for t, c in top))
    if rulings:
        lines.append(f"- delivery-form rulings, latest {len(rulings)} (form: {' | '.join(VOICE_FORM_WORDS)}):")
        for t, form, words in rulings:
            w = words if len(words) <= 160 else words[:159] + "…"
            lines.append(f'  - {t or "(undated)"} form={form or "(named in the words)"}: "{w}"')
    out = "\n".join(lines)
    if len(out) > VOICE_CAP:
        out = out[:VOICE_CAP].rsplit("\n", 1)[0] + "\n  (digest cut at the cap)"
    return out


def cmd_session_open(payload, store):
    source = session_source(payload)
    held = source in HELD_SOURCES
    now = datetime.datetime.now()
    print(f"## VLDS recall (SessionStart hook, source={source}) — every item still passes the gc read barrier: "
          f"freed, stale, or unowned → surface it, do not apply it")
    print(now_line(now))
    if held:
        sid, tag = session_tag(payload)
        if sid != "unknown":
            os.makedirs(store, exist_ok=True)
            fresh = record_seen(store, sid, now)
            print(f"{source}: session {tag} {'recorded as seen' if fresh else 'already seen'} — its next prompt "
                  f"pours nothing; the conversation holds its own recall, so digest and verdict only")
    index_path = os.path.join(store, "phi-index.md")
    if not os.path.exists(index_path):
        print("no phi-index.md yet — cold-start: read store/* yourself, then bootstrap the register per /vlds:gc")
        return 0
    index_text = read_text(index_path)
    inject, digest, from_index = recall_lists(index_text)
    print(f"lists from {'the index’s ## recall section' if from_index else 'the hook defaults (the index has no ## recall section)'}"
          f" — inject: {', '.join(inject)}; digest: {', '.join(digest)}")
    if held:
        for fname in inject + digest:
            print(digest_line(store, fname))
    else:
        print("\n### phi-index.md")
        print(index_text.rstrip("\n"))
        plan = chunk_plan(store, inject)
        print(f"\n### inject — each chunk arrives as its own hook output (slots 0..{SLOTS - 1}), split at entry "
              f"boundaries under the harness's {HOOK_OUTPUT_CAP:,}-character cap")
        for i, item in enumerate(plan[:SLOTS]):
            print(f"- slot {i}: {plan_label(item)}")
        if len(plan) > SLOTS:
            print(f"- beyond the registered slots, NOT injected: "
                  f"{', '.join(plan_label(it) for it in plan[SLOTS:])} — read by hand before it steers")
        print("\n### digest — read on demand, when an entry there is about to steer")
        for fname in digest:
            print(digest_line(store, fname))
        voice = owner_voice(store)
        if voice:
            print()
            print(voice)
    print("\n### phi.py check")
    print(check_summary(store))
    return 0


# ─── prompt-open ────────────────────────────────────────────────────────────────────────────────────────

def lock_holder(store, sid):
    """The other session holding a fresh sweep lock, or None."""
    lock = os.path.join(store, "arc", ".sweep-lock")
    if not os.path.exists(lock):
        return None
    holder = (read_text(lock).split() or ["?"])[0]
    age = datetime.datetime.now().timestamp() - os.path.getmtime(lock)
    if holder != sid and age < LOCK_STALE_S:
        return f"{holder} ({int(age)} s old)"
    return None


def pour_dispatch(store, sid, tag, now):
    path = os.path.join(store, "dispatch.md")
    if not os.path.exists(path):
        return "pour: dispatch.md absent — nothing to pour (the SessionStart hook seeds it)"
    data = read_bytes(path)
    parts = split_header(data)
    if parts is None:
        return "pour: dispatch.md has no header/entries separator — skipped (pre-canonical; the gc judges)"
    head, sep, body = parts
    entries = entry_lines(body.decode("utf-8", errors="replace"), after_separator=False)
    if not entries:
        return "pour: dispatch.md holds no entries — nothing to pour"
    held = lock_holder(store, sid)
    if held:
        return (f"pour: skipped — sweep lock held by {held}; this session is recorded as seen, so the entries "
                f"stay hot until the next new session's first prompt or an in-session sweep")
    arc = os.path.join(store, "arc")
    os.makedirs(arc, exist_ok=True)
    name = f"dispatch-{now:%Y%m%d-%H%M%S}-{tag}.md"
    target = os.path.join(arc, name)
    if os.path.exists(target):
        return f"pour: skipped — arc/{name} already exists"
    digest = sha12(data)
    write_bytes(target, data)
    if sha12(read_bytes(target)) != digest:
        os.remove(target)
        return "pour: ABORTED — the arc copy did not read back byte-identical; dispatch.md left untouched"
    write_bytes(path, head + sep)
    return (f"pour: {len(entries)} entries ({len(data):,} B) → arc/{name} (sha {digest}, verified byte-identical); "
            f"dispatch.md reseeded from its own header — registering the copy as an attachment is owed to the "
            f"next sweep")


def stamp(store, prompt, tag, now):
    path = os.path.join(store, "dispatch.md")
    if not os.path.exists(path):
        return None
    fp = " ".join(str(prompt).split())
    if len(fp) > FINGERPRINT_CHARS:
        fp = fp[:FINGERPRINT_CHARS - 1] + "…"
    fp = fp.replace('"', "'")
    nl = "\r\n" if b"\r\n" in read_bytes(path)[:4096] else "\n"
    entry = (f'{nl}- fingerprint: "{fp}"{nl}'
             f"  time: {now:{NOW_FMT}}{nl}"
             f"  arrival: turn (stamped by the prompt hook, session {tag}){nl}")
    with open(path, "ab") as f:
        f.write(entry.encode("utf-8"))
    return fp


def cmd_prompt_open(payload, store):
    prompt = payload.get("prompt") or payload.get("user_input") or ""
    if not str(prompt).strip():
        return 0
    sid, tag = session_tag(payload)
    now = datetime.datetime.now()
    os.makedirs(store, exist_ok=True)
    lines = [f"## VLDS prompt hook (session {tag})", "- " + now_line(now)]
    if record_seen(store, sid, now):
        lines.append("- " + pour_dispatch(store, sid, tag, now))
    fp = stamp(store, prompt, tag, now)
    if fp is None:
        lines.append("- stamp: dispatch.md absent — the row is yours to append")
    else:
        lines.append(f'- stamped: dispatch.md row "{fp[:80]}" at {now:{NOW_FMT}} — check it against the '
                     f"rows already there; complete its state: before answering and its addressed: by turn end")
    print("\n".join(lines))
    return 0


# ─── pre-write ──────────────────────────────────────────────────────────────────────────────────────────

def cmd_pre_write(payload, store):
    """Ask before a store-named file lands outside every `.claude/vlds/`, before a persisted entry carries a
    placeholder time, and before one carries a time guessed ahead of the clock; silent when the call writes
    nothing store-named."""
    targets = write_targets(payload)
    if not targets:
        return 0
    now = datetime.datetime.now()
    reasons = []
    for _spelled, a in targets:
        if not _homed(a):
            name = os.path.basename(a)
            reasons.append(f"{name} resolves to {a}, outside the store {store}; a store entry belongs at "
                           f"{os.path.join(store, name)} — proceed only if this file is not VLDS state")
    text = written_text(payload)
    for v in placeholder_times(text):
        reasons.append(f"placeholder time `{v}` in a persisted entry — copy the latest `now:` from the hook "
                       f"stream ({now_line(now)})")
    for v in future_times(text, now):
        reasons.append(f"guessed-ahead time `{v}` in a persisted entry — later than the latest `now:` "
                       f"({now_line(now)}) by more than a minute; a stamp is copied from the hook stream, never "
                       f"written ahead of it")
    if not reasons:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": "; ".join(reasons)}}))
    return 0


# ─── post-write ─────────────────────────────────────────────────────────────────────────────────────────

def touched_store(payload, store):
    """What the call wrote, when it is the store's business: a file under the store, a store-named file
    anywhere (stray or homed — the same matcher as pre-write), or a shell command that names the store."""
    tool = str(payload.get("tool_name") or "")
    inp = payload.get("tool_input") or {}
    if not isinstance(inp, dict):
        return None
    fp = inp.get("file_path")
    if fp:
        a = os.path.normcase(os.path.abspath(str(fp)))
        s = os.path.normcase(os.path.abspath(store))
        if a.startswith(s + os.sep):
            return os.path.relpath(a, s)
    targets = write_targets(payload)
    if targets:
        strays = [os.path.basename(a) for _s, a in targets if not _homed(a)]
        if strays:
            return f"a store-named file OUTSIDE the store ({', '.join(sorted(set(strays)))})"
        return "a store file, via " + ("a shell command" if tool in ("Bash", "PowerShell") else tool)
    if fp:
        return None
    if tool in ("Bash", "PowerShell"):
        cmd = str(inp.get("command") or "")
        if re.search(r"\.claude[\\/]+vlds", cmd):
            return "the store, via a shell command"
    return None


def cmd_post_write(payload, store):
    what = touched_store(payload, store)
    if not what or not os.path.isdir(store):
        return 0
    now = datetime.datetime.now()
    text = f"{now_line(now)}\nVLDS check after the write to {what}:\n{check_summary(store)}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:]
    sub = argv[0] if argv else ""
    slot = None
    if "--slot" in argv:
        try:
            slot = int(argv[argv.index("--slot") + 1])
        except (IndexError, ValueError):
            slot = None
    payload = payload_from_stdin()
    store = resolve_store(payload)
    try:
        if sub == "session-open" and slot is not None:
            return cmd_session_slot(payload, store, slot)
        if sub == "session-open":
            return cmd_session_open(payload, store)
        if sub == "prompt-open":
            return cmd_prompt_open(payload, store)
        if sub == "pre-write":
            return cmd_pre_write(payload, store)
        if sub == "post-write":
            return cmd_post_write(payload, store)
        print(f"vlds_hooks.py: unknown subcommand {sub!r}")
        return 0
    except Exception as e:  # noqa: BLE001 — a hook degrades, never raises
        print(f"VLDS hook ({sub}) degraded: {type(e).__name__}: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
