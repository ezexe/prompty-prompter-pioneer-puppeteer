#!/usr/bin/env python3
"""phi.py — the VLDS φ-register's mechanical companion.

Deterministic and judgment-free, in the p4.py mold: it checks, computes, and verifies; it never decides
what deserves keeping, never sweeps on its own, and never deletes anything. The model (the gc, in-session)
judges; this script is the arithmetic and the scans.

Subcommands:
  check         run the nine structural scans over the store; report, never repair (exit 1 = corruption,
                exit 0 = clean or debt-only — '2'/'11' states are owed work, not corruption)
  mask          run the literal zeckendorf_dp over model-supplied scores with pins; pure function,
                JSON in / JSON out; asserts the exact guarantee kept <= ceil(n_i/2) per segment
  verify-merge  the merge deletion gate: every parent entry body must be verbatim-contained in the
                child, and the child may not exceed its parents' bytes (override with --allow-growth)
  verify-pour   the trim deletion gate: every entry body in a hot file's mask=A:B span must be
                verbatim-contained in the target segment before the span may be trimmed
  lock/unlock   the sweep lock (arc/.sweep-lock, session-stamped, stale after 60 minutes) — taken
                before any arc write; without it a session only reports owed work
  rebuild       regenerate phi-index.md from segment headers + store grammar — corruption recovery ONLY:
                refuses to run while the drift scan shows a voided watermark (a user edit is a ruling)
  restore       print a segment's entries to stdout for judged re-insertion

Watermark convention (shared by reader and writer, pinned in gc/reference.md): `mask=A:B sha=H` is a
0-based, HALF-OPEN line range — the masked span is lines[A:B]; live entries are counted outside it.

Conventions (pinned in gc/reference.md "The φ-register"):
  positions are 1-based over the package cache CACHE = [1, 2, 3, 5, 8, ...]; position p has weight
  CACHE[p-1] and byte capacity CACHE[p-1] KB. Epoch pairs are (CACHE[k], CACHE[k+1]); Cassini
  b^2 - a*b - a^2 == (-1)^k holds under cache indexing and flips sign under any odd shift — the
  position-weight numbering must not be reused for the epoch check.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time

CACHE = [1, 2]
while len(CACHE) < 40:
    CACHE.append(CACHE[-1] + CACHE[-2])

SEED_HOT = ["local-storage.md", "index.md", "data-store.md", "ledger.md", "tombstones.md",
            "virtual.md", "session-storage.md", "logger.md"]
LIVENESS_HORIZON_S = 24 * 3600
FACT_ID_RE = re.compile(r"^id: ([a-z]{2}-\d{4})\s*$", re.M)
SEG_NAME_RE = re.compile(r"^arc-(\d+)-([A-Za-z0-9]+)\.md$")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# ─── segment parsing ────────────────────────────────────────────────────────────────────────────────────

def parse_segment(path):
    """A segment = one ```yaml-fenced header block, then entry blocks delimited by column-0 '---'.
    Each entry block: an 'id: xx-NNNN' line, a blank line, then the verbatim body."""
    text = read(path)
    lines = text.split("\n")
    issues = []
    header = {}
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # locate the fenced header
    try:
        first = next(i for i, l in enumerate(lines) if l.strip())
    except StopIteration:
        return {}, [], ["empty segment"]
    if lines[first] != "```yaml":
        issues.append("header is not a ```yaml fence (frontmatter '---' headers breach the grammar)")
        return {}, [], issues
    try:
        close = next(i for i in range(first + 1, len(lines)) if lines[i] == "```")
    except StopIteration:
        return {}, [], ["unterminated header fence"]
    for l in lines[first + 1:close]:
        m = re.match(r"^([A-Za-z-]+):\s*(.*)$", l)
        if m:
            header[m.group(1)] = m.group(2)
    # entries: split the remainder on column-0 '---'
    rest = lines[close + 1:]
    entries, cur = [], []
    for l in rest:
        if l == "---":
            if cur and any(x.strip() for x in cur):
                entries.append("\n".join(cur).strip("\n"))
            cur = []
        else:
            cur.append(l)
    if cur and any(x.strip() for x in cur):
        entries.append("\n".join(cur).strip("\n"))
    # a mid-body column-0 '---' was already consumed by the splitter above; its observable residue is
    # an id-less pseudo-entry, so flag exactly that — plus column-0 fences, which the splitter ignores
    for i, e in enumerate(entries):
        if not FACT_ID_RE.match(e.split("\n", 1)[0] + "\n"):
            issues.append(f"entry {i}: missing id line — possible mid-body '---' split")
        for l in e.split("\n")[2:]:
            if l.startswith("```"):
                issues.append(f"entry {i}: column-0 fence inside body — grammar hazard")
    return header, entries, issues


def entry_id(entry):
    m = FACT_ID_RE.match(entry.split("\n", 1)[0] + "\n")
    return m.group(1) if m else None


def entry_body(entry):
    lines = entry.split("\n")
    if lines and lines[0].startswith("id: "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip("\n")


# ─── phi-index parsing ──────────────────────────────────────────────────────────────────────────────────

def parse_index(store):
    path = os.path.join(store, "phi-index.md")
    if not os.path.exists(path):
        return None
    text = read(path)
    idx = {"register": "", "positions": [], "hot": [], "epochs": [], "raw": text}
    m = re.search(r"^register:\s*([01]+)", text, re.M)
    if m:
        idx["register"] = m.group(1)
    section = None
    for l in text.split("\n"):
        if l.startswith("## "):
            section = l[3:].strip()
            continue
        if not l.startswith("|") or set(l.replace("|", "").strip()) <= {"-", " ", ":"}:
            continue
        cells = [c.strip() for c in l.strip("|").split("|")]
        if section == "positions" and cells[0] != "pos":
            idx["positions"].append(cells)
        elif section == "hot" and cells[0] != "file":
            idx["hot"].append(cells)
        elif section == "epochs" and cells[0] != "file":
            idx["epochs"].append(cells)
    return idx


def hot_entry_count(store, fname, span=None):
    """Entries = column-0 '- ' lines after the header separator, excluding a masked span.
    `span` is the (A, B) half-open line range of the watermarked (poured, untrimmed) region."""
    path = os.path.join(store, fname)
    if not os.path.exists(path):
        return None
    lines = read(path).split("\n")
    try:
        start = lines.index("---") + 1
    except ValueError:
        start = 0
    a, b = span if span else (0, 0)
    return sum(1 for i, l in enumerate(lines[start:], start)
               if l.startswith("- ") and not (a <= i < b))


# ─── the DP (masks.py's zeckendorf_dp, transplanted line-faithfully) ───────────────────────────────────

def zeckendorf_dp(scores):
    n = len(scores)
    if n == 0:
        return []
    if n == 1:
        return [1]
    keep = [0.0] * n
    skip = [0.0] * n
    keep[0], skip[0] = float(scores[0]), 0.0
    for i in range(1, n):
        keep[i] = skip[i - 1] + float(scores[i])
        skip[i] = max(keep[i - 1], skip[i - 1])
    mask = [0] * n
    i = n - 1
    while i >= 0:
        if i == 0:
            if keep[0] >= skip[0]:
                mask[0] = 1
            break
        if keep[i] >= skip[i]:
            mask[i] = 1
            i -= 2
        else:
            i -= 1
    return mask


def verify_mask(mask):
    prev = 0
    for v in mask:
        if v == 1 and prev == 1:
            return False
        prev = v
    return True


# ─── subcommands ────────────────────────────────────────────────────────────────────────────────────────

def cmd_check(store):
    corrupt, debt, notes = [], [], []
    arc = os.path.join(store, "arc")
    idx = parse_index(store)

    # 1. register scan — '2' (two segments at one position) and '11' (adjacent positions) are DEBT
    positions = {}
    if os.path.isdir(arc):
        for f in sorted(os.listdir(arc)):
            m = SEG_NAME_RE.match(f)
            if m:
                positions.setdefault(int(m.group(1)), []).append(f)
    for p, files in sorted(positions.items()):
        if len(files) > 1:
            debt.append(f"register '2' at position {p}: {files} — a RESOLVE is owed")
    occupied = sorted(positions)
    for a, b in zip(occupied, occupied[1:]):
        if b == a + 1:
            debt.append(f"register '11' at positions {a},{b} — a CARRY is owed")
    if idx and idx["register"]:
        derived = "".join("1" if p in positions else "0"
                          for p in range(max(occupied, default=0), 0, -1))
        if derived and derived.lstrip("0") != idx["register"].lstrip("0"):
            corrupt.append(f"index register '{idx['register']}' != derived '{derived}'")
        elif idx["register"].lstrip("0") and not occupied:
            corrupt.append("index register claims occupied positions but arc/ holds no segments")

    # positions-table cross-check — the torn-pour detector and the weight recurrence's independent witness
    if idx is not None:
        table = {}
        for row in idx["positions"]:
            try:
                p, wkb, seg_file = int(row[0]), int(row[1]), row[2]
            except (ValueError, IndexError):
                corrupt.append(f"positions row unparseable: {row}")
                continue
            table[p] = row
            if not (1 <= p <= len(CACHE)):
                corrupt.append(f"positions row names impossible position {p}")
                continue
            if wkb != CACHE[p - 1]:
                corrupt.append(f"positions row {p}: weight {wkb} KB != CACHE[{p - 1}] = {CACHE[p - 1]} KB")
            if not os.path.exists(os.path.join(arc, seg_file)):
                corrupt.append(f"positions row {p} names missing segment {seg_file}")
        for p, files in positions.items():
            if p not in table:
                corrupt.append(f"segment(s) at position {p} absent from the positions table — torn pour: "
                               f"delete and re-sweep ({files})")

    # 2+3. per-segment: grammar, mask records, ids
    all_ids = {}
    for p, files in sorted(positions.items()):
        for f in files:
            header, entries, issues = parse_segment(os.path.join(arc, f))
            for i in issues:
                corrupt.append(f"{f}: {i}")
            w = header.get("weight-kb")
            if w and int(w) != CACHE[p - 1]:
                corrupt.append(f"{f}: header weight {w} KB != position weight {CACHE[p - 1]} KB")
            size = os.path.getsize(os.path.join(arc, f))
            cap = CACHE[p - 1] * 1024
            for att in [a.strip() for a in header.get("attached", "").split(",") if a.strip()]:
                ap = os.path.join(arc, att)
                if os.path.exists(ap):
                    size += os.path.getsize(ap)
                else:
                    corrupt.append(f"{f}: attached file {att} missing from arc/")
            if size > cap:
                debt.append(f"{f}: position bytes {size} > capacity {cap} — settling owed")
            if header.get("mask"):
                if not verify_mask([int(c) for c in header["mask"] if c in "01"]):
                    corrupt.append(f"{f}: recorded mask contains adjacent keeps")
            if "verified" not in header:
                corrupt.append(f"{f}: no 'verified:' commit mark — treat as a torn pour (dead to recall)")
            for e in entries:
                eid = entry_id(e)
                if eid:
                    all_ids.setdefault(eid, []).append(f)

    # 5. uniqueness — one fact-id, one live segment
    for eid, where in sorted(all_ids.items()):
        if len(set(where)) > 1:
            corrupt.append(f"fact-id {eid} live in {sorted(set(where))} — one fact, one place violated")

    # 4. epochs — Cassini + row-to-row continuity
    if idx:
        for row in idx["epochs"]:
            try:
                fname, k, a, b = row[0], int(row[1]), int(row[2]), int(row[3])
            except (ValueError, IndexError):
                corrupt.append(f"epochs row unparseable: {row}")
                continue
            if not (0 <= k < len(CACHE) - 1):
                corrupt.append(f"epoch k={k} for {fname} out of range — corrupt counter")
                continue
            if b * b - a * b - a * a != (-1) ** k:
                corrupt.append(f"epoch pair ({a},{b}) for {fname} falls off the Fibonacci lattice")
            if (a, b) != (CACHE[k], CACHE[k + 1]):
                corrupt.append(f"epoch k={k} for {fname}: pair ({a},{b}) != (CACHE[{k}],CACHE[{k+1}]) — "
                               f"continuity broken (skipped or repeated epoch)")

    # 7. drift — recount hot rows; hash below-watermark spans against their recorded pour hashes
    if idx:
        for row in idx["hot"]:
            fname = row[0]
            wm = row[5] if len(row) > 5 else "—"
            span, wm_hash = None, None
            m = re.match(r"mask=(\d+):(\d+)\s+sha=([0-9a-f]+)", wm)
            if m:
                span, wm_hash = (int(m.group(1)), int(m.group(2))), m.group(3)
            count = hot_entry_count(store, fname, span)
            if count is None:
                corrupt.append(f"hot row names missing file {fname}")
                continue
            try:
                live = int(row[1])
                if live != count:
                    notes.append(f"{fname}: index live={live}, recounted {count} — stale row (updates at sweep)")
            except (ValueError, IndexError):
                pass
            if span and wm_hash:
                # the masked span is lines[A:B], half-open, 0-based — the one shared definition
                masked = "\n".join(read(os.path.join(store, fname)).split("\n")[span[0]:span[1]])
                if sha(masked) != wm_hash:
                    corrupt.append(f"WATERMARK VOIDED on {fname}: the user ruled inside the masked span — "
                                   f"the gc must reconcile before the arc copy may be cited")

    # 6. duplication — verbatim >60-char lines in two hot files ('11' suspects, judged by the gc)
    seen = {}
    for fname in SEED_HOT:
        path = os.path.join(store, fname)
        if not os.path.exists(path):
            continue
        for l in read(path).split("\n"):
            s = l.strip()
            if len(s) > 60 and not s.startswith("#"):
                seen.setdefault(s, set()).add(fname)
    for s, files in seen.items():
        if len(files) > 1:
            notes.append(f"verbatim line in {sorted(files)}: {s[:70]}...")

    # 8. owed borrows — tombstoned fact-ids still live in canonical blocks
    tpath = os.path.join(store, "tombstones.md")
    if os.path.exists(tpath):
        for eid in set(re.findall(r"\b([a-z]{2}-\d{4})\b", read(tpath))):
            if eid in all_ids:
                debt.append(f"'-1' state: tombstoned {eid} still live in {all_ids[eid]} — a BORROW is owed")

    # 9. liveness — classify dispatch records; deadness is age + content, never slot occupancy
    cur = ""
    cur_path = os.path.join(store, ".dispatch-current")
    if os.path.exists(cur_path):
        cur = read(cur_path).strip()
    now = time.time()
    for f in sorted(os.listdir(store)):
        if f.startswith("dispatch-") and f.endswith(".md"):
            age = now - os.path.getmtime(os.path.join(store, f))
            if f == cur:
                notes.append(f"{f}: LIVE (named by .dispatch-current) — untouchable")
            elif age < LIVENESS_HORIZON_S:
                notes.append(f"{f}: within the {LIVENESS_HORIZON_S // 3600}h liveness horizon — untouchable")
            else:
                notes.append(f"{f}: dead candidate (age + content are the standard; the gc judges)")

    for tag, items in (("CORRUPT", corrupt), ("DEBT", debt), ("note", notes)):
        for i in items:
            print(f"[{tag}] {i}")
    print(f"phi.py check: {len(corrupt)} corruption, {len(debt)} debt, {len(notes)} notes")
    return 1 if corrupt else 0


def cmd_mask(args):
    data = json.load(open(args.scores, encoding="utf-8")) if args.scores != "-" else json.load(sys.stdin)
    scores, pins = data["scores"], set(data.get("pins", []))
    if any(not isinstance(s, int) or not (0 <= s <= 54) for s in scores):
        print("scores must be INTEGERS on the 8-digit Zeckendorf grid 0..54", file=sys.stderr)
        return 2
    n = len(scores)
    mask = [None] * n
    seg, segs = [], []
    for i in range(n + 1):
        if i == n or i in pins:
            if seg:
                segs.append(seg)
            if i < n:
                mask[i] = 1  # pins always keep
            seg = []
        else:
            seg.append(i)
    kept_unpinned = 0
    for seg in segs:
        sub = zeckendorf_dp([scores[i] for i in seg])
        for j, i in enumerate(seg):
            mask[i] = sub[j]
        kept = sum(sub)
        kept_unpinned += kept
        # the exact guarantee — kept <= ceil(n_i/2) per pin-delimited segment; density <= 0.5 only
        # asymptotically, and only for unfragmented even-length runs. Explicit checks, not asserts,
        # so python -O cannot strip the guarantee.
        if kept > (len(seg) + 1) // 2 or not verify_mask(sub):
            print("internal error: DP guarantee violated", file=sys.stderr)
            return 1
    # pin adjacency is a model-side owed merge, not a script failure — reported, never asserted
    adjacent_pairs = [(i, i + 1) for i in range(n - 1) if mask[i] == 1 and mask[i + 1] == 1]
    out = {"mask": mask, "kept_unpinned": kept_unpinned, "pinned": len(pins),
           "segments": len(segs), "ceiling": sum((len(s) + 1) // 2 for s in segs),
           "adjacent_keeps": adjacent_pairs}
    print(json.dumps(out))
    return 0


def cmd_verify_merge(args):
    child = read(args.child)
    ok = True
    total_parent_bytes = 0
    for p in args.parents:
        text = read(p)
        total_parent_bytes += len(text.encode("utf-8"))
        _, entries, _ = parse_segment(p)
        blocks = entries if entries else [text]
        for e in blocks:
            body = entry_body(e)
            if body and body not in child:
                ok = False
                print(f"FAIL: parent {os.path.basename(p)} entry not verbatim-contained: {body[:60]}...")
    child_bytes = len(child.encode("utf-8"))
    if child_bytes > total_parent_bytes:
        # merges may only shrink — growth on a deletion gate is a FAIL unless explicitly overridden
        if args.allow_growth:
            print(f"note: child {child_bytes} B > parents {total_parent_bytes} B — allowed by --allow-growth")
        else:
            ok = False
            print(f"FAIL: child {child_bytes} B > parents {total_parent_bytes} B — merges may only shrink")
    print("PASS — parents may be deleted (mark the child 'verified:' FIRST; that is the commit point)"
          if ok else "FAIL — do not delete parents")
    return 0 if ok else 1


def split_span_bodies(lines):
    """Split a hot-file span into entry bodies on column-0 '- ' / '#' starts (the store grammar)."""
    bodies, cur = [], []
    for l in lines:
        if l.startswith("- ") or l.startswith("#"):
            if cur and any(x.strip() for x in cur):
                bodies.append("\n".join(cur).rstrip())
            cur = [l]
        else:
            cur.append(l)
    if cur and any(x.strip() for x in cur):
        bodies.append("\n".join(cur).rstrip())
    return bodies


def cmd_verify_pour(args, store):
    """The trim gate: every entry body in the hot file's mask=A:B span must live verbatim in the segment."""
    seg_text = read(args.segment) if os.path.isabs(args.segment) \
        else read(os.path.join(store, "arc", args.segment))
    a, b = (int(x) for x in args.span.split(":"))
    src_lines = read(os.path.join(store, args.source)).split("\n")[a:b]
    ok = True
    bodies = split_span_bodies(src_lines)
    for bd in bodies:
        if bd.strip() and bd not in seg_text:
            ok = False
            print(f"FAIL: span body not verbatim-contained in segment: {bd[:60]!r}")
    print(f"checked {len(bodies)} bodies from {args.source}[{a}:{b}]")
    print("PASS — the span may be trimmed" if ok else "FAIL — do not trim")
    return 0 if ok else 1


def cmd_lock(args, store, release=False):
    """The sweep lock: session-stamped, stale after 60 minutes; taken before any arc write."""
    lock = os.path.join(store, "arc", ".sweep-lock")
    if release:
        if not os.path.exists(lock):
            print("no lock held")
            return 0
        holder = read(lock).split()[0]
        if holder != args.session:
            print(f"REFUSED: lock held by {holder}, not {args.session}")
            return 1
        os.remove(lock)
        print("released")
        return 0
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    if os.path.exists(lock):
        age = time.time() - os.path.getmtime(lock)
        holder = read(lock).split()[0]
        if holder != args.session and age < 3600:
            print(f"REFUSED: fresh lock held by {holder} ({int(age)} s old) — report owed work instead")
            return 1
        print(f"superseding {'own' if holder == args.session else 'stale'} lock ({holder}, {int(age)} s)")
    with open(lock, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{args.session} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("granted")
    return 0


def cmd_rebuild(store):
    # corruption recovery ONLY: a voided watermark is a user ruling this script must not pave over
    class Silent:
        def write(self, *_):
            pass
        def flush(self):
            pass
    real = sys.stdout
    sys.stdout = Silent()
    try:
        rc = cmd_check(store)
    finally:
        sys.stdout = real
    if rc != 0:
        print("rebuild refused: check reports corruption — reconcile rulings and torn pours first "
              "(a user edit outranks a recomputation)")
        return 1
    print("rebuild: derive the index from arc/ headers and hot recounts, then compare with the model "
          "in-session; this script intentionally does not write phi-index.md unattended — emit follows:")
    arc = os.path.join(store, "arc")
    if os.path.isdir(arc):
        for f in sorted(os.listdir(arc)):
            m = SEG_NAME_RE.match(f)
            if m:
                print(f"position {int(m.group(1))}: {f} "
                      f"({os.path.getsize(os.path.join(arc, f))} B)")
    for fname in SEED_HOT:
        c = hot_entry_count(store, fname)
        if c is not None:
            print(f"hot {fname}: {c} entries, {os.path.getsize(os.path.join(store, fname))} B")
    return 0


def cmd_restore(args):
    header, entries, issues = parse_segment(args.segment)
    for i in issues:
        print(f"[grammar] {i}", file=sys.stderr)
    for e in entries:
        print("---")
        print(e)
    return 0


def main():
    ap = argparse.ArgumentParser(prog="phi.py", description="VLDS φ-register mechanical companion")
    ap.add_argument("--store", default=os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."),
                                                    ".claude", "vlds"))
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check")
    p = sub.add_parser("mask")
    p.add_argument("--scores", required=True, help="JSON file ('-' for stdin): {scores:[0..54], pins:[i]}")
    p = sub.add_parser("verify-merge")
    p.add_argument("--child", required=True)
    p.add_argument("--parents", nargs="+", required=True)
    p.add_argument("--allow-growth", action="store_true")
    p = sub.add_parser("verify-pour")
    p.add_argument("--segment", required=True, help="segment filename (in arc/) or absolute path")
    p.add_argument("--source", required=True, help="hot file (relative to the store)")
    p.add_argument("--span", required=True, help="A:B — the 0-based half-open masked line range")
    p = sub.add_parser("lock")
    p.add_argument("session")
    p = sub.add_parser("unlock")
    p.add_argument("session")
    sub.add_parser("rebuild")
    p = sub.add_parser("restore")
    p.add_argument("segment")
    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check(args.store))
    if args.cmd == "mask":
        sys.exit(cmd_mask(args))
    if args.cmd == "verify-merge":
        sys.exit(cmd_verify_merge(args))
    if args.cmd == "verify-pour":
        sys.exit(cmd_verify_pour(args, args.store))
    if args.cmd == "lock":
        sys.exit(cmd_lock(args, args.store))
    if args.cmd == "unlock":
        sys.exit(cmd_lock(args, args.store, release=True))
    if args.cmd == "rebuild":
        sys.exit(cmd_rebuild(args.store))
    if args.cmd == "restore":
        sys.exit(cmd_restore(args))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
