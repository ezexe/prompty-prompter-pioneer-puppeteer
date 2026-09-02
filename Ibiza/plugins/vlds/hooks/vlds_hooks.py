#!/usr/bin/env python3
"""vlds_hooks.py — the VLDS plugin's hook bodies: mechanical and judgment-free, in the phi.py mold.

Subcommands, each reading the harness's JSON payload on stdin (decoded as UTF-8 — the harness writes UTF-8
whatever the console codepage says):
  session-open            SessionStart, the recall's index slot: print phi-index.md, the inject/digest lists,
                          a digest line per digest file, and the verdict of `phi.py check`. On `source` resume,
                          fork, or compact print only the digest lines and the verdict — the conversation already
                          holds its own recall — and record the session id in `.sessions`, so a fork's first
                          prompt (a new id over a live conversation) and a pre-hook session's next prompt do not
                          pour rows that are still live.
  session-open --slot N   SessionStart, one chunk slot: the index's `inject:` files are split at entry boundaries
                          into chunks under the harness's per-hook output cap, and slot N prints the N-th chunk
                          (header with the first chunk of each file). Nothing on resume / fork / compact, nothing
                          when the plan is shorter than N+1. One hook per slot, because the harness caps EACH
                          hook's output at 10,000 characters: one process printing everything would be spilled
                          to a file and replaced by a preview. A single entry over the cap, or a chunk beyond the
                          registered slots, arrives as a marker line to read by hand.
  prompt-open             UserPromptSubmit: stamp the message's dispatch row (fingerprint / time / arrival; the
                          model completes state and addressed) and, on the FIRST prompt a session id ever
                          submits, pour dispatch.md whole-file into arc/ — a sha-verified byte-identical copy,
                          then a reseed that preserves the file's own header (a user's header edit is a ruling).
  post-write              PostToolUse: when a Write, Edit, Bash, or PowerShell call touched the store, run
                          `phi.py check` and hand its verdict back as additionalContext.

Everything here is mechanical. The stamp carries no judgment; the pour moves a file whose every entry belongs to
a conversation that is not this one (a new id that reaches its first prompt unrecorded) and destroys nothing (the
copy is verified before the reseed, and the copy stays); the check only reports. What the hooks never do:
register the poured file in the index (a sweep's judged act), pour any other hot file (cold spans are scored,
not counted), complete a dispatch row (state and addressed are the model's), or block a prompt — every failure
prints a one-line notice and exits 0.

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
    """The verdict line plus every CORRUPT and DEBT line; notes are counted, not listed."""
    out = run_check(store)
    lines = out.split("\n")
    keep = [l for l in lines if l.startswith("[CORRUPT]") or l.startswith("[DEBT]") or l.startswith("phi.py check")]
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
        f.write(f"{sid} {now:%Y-%m-%d %H:%M}\n")
    return True


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


def cmd_session_open(payload, store):
    source = session_source(payload)
    held = source in HELD_SOURCES
    now = datetime.datetime.now()
    print(f"## VLDS recall (SessionStart hook, source={source}) — every item still passes the gc read barrier: "
          f"freed, stale, or unowned → surface it, do not apply it")
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
             f"  time: {now:%Y-%m-%d %H:%M}{nl}"
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
    lines = [f"## VLDS prompt hook (session {tag})"]
    if record_seen(store, sid, now):
        lines.append("- " + pour_dispatch(store, sid, tag, now))
    fp = stamp(store, prompt, tag, now)
    if fp is None:
        lines.append("- stamp: dispatch.md absent — the row is yours to append")
    else:
        lines.append(f'- stamped: dispatch.md row "{fp[:80]}" at {now:%Y-%m-%d %H:%M} — check it against the '
                     f"rows already there; complete its state: before answering and its addressed: by turn end")
    print("\n".join(lines))
    return 0


# ─── post-write ─────────────────────────────────────────────────────────────────────────────────────────

def touched_store(payload, store):
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
    text = f"VLDS check after the write to {what}:\n{check_summary(store)}"
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
        if sub == "post-write":
            return cmd_post_write(payload, store)
        print(f"vlds_hooks.py: unknown subcommand {sub!r}")
        return 0
    except Exception as e:  # noqa: BLE001 — a hook degrades, never raises
        print(f"VLDS hook ({sub}) degraded: {type(e).__name__}: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
