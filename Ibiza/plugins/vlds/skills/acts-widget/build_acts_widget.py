#!/usr/bin/env python3
"""Keep a session's one acts page: every closing appends a round of acts, every pick is recorded into it.

Usage:
  build_acts_widget.py append ACTS.json (--page PAGE | --session ID [--root DIR]) [--now TIME]
  build_acts_widget.py pick (--page PAGE | --session ID [--root DIR]) (--acts ID,ID | --skipped)
                            [--round N] [--note ID=TEXT ...] [--now TIME]
  build_acts_widget.py show (--page PAGE | --session ID [--root DIR])

ACTS.json is one closing:
  {"title": "...", "repo": "owner/name", "branch": "...",
   "acts": [{"id": "...", "title": "...", "summary": "...", "goal": "...",
             "files": ["..."], "constraints": ["..."], "done": "...", "recommended": true}]}

Every act needs id, title and goal; ids are unique within a round. --session alone puts the page at
<root>/.claude/scratchpad/acts-widget/<session>.html (root defaults to the working directory), so a session
recycles one page. The page is its own state: the rounds live in a JSON block inside it, read back on every
append or pick, and the page is rewritten whole. It inlines assemble.js, so the prompt it shows is built by the
same function the test runs.
"""
import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ("id", "title", "goal")
STATE_RE = re.compile(r'<script type="application/json" id="acts-state">(.*?)</script>', re.S)


def validate(data):
    acts = data.get("acts")
    if not isinstance(acts, list) or not acts:
        raise ValueError("acts: a non-empty list is required")
    seen = set()
    for i, act in enumerate(acts):
        missing = [k for k in REQUIRED if not str(act.get(k, "")).strip()]
        if missing:
            raise ValueError(f"acts[{i}]: missing {', '.join(missing)}")
        if act["id"] in seen:
            raise ValueError(f"acts[{i}]: duplicate id {act['id']!r}")
        seen.add(act["id"])
        for key in ("files", "constraints"):
            if not isinstance(act.get(key, []), list):
                raise ValueError(f"acts[{i}].{key}: a list is required")


def new_state(session=None):
    return {"session": session or "", "rounds": []}


def load_state(page_path):
    """The rounds a page already holds; a fresh state when the page does not exist yet."""
    if not os.path.exists(page_path):
        return None
    with open(page_path, encoding="utf-8") as f:
        m = STATE_RE.search(f.read())
    if not m:
        raise ValueError(f"{page_path}: no acts-state block — not an acts page, refusing to overwrite it")
    return json.loads(m.group(1))


def append_round(state, data, now=None):
    validate(data)
    open_round = state["rounds"][-1] if state["rounds"] else None
    if open_round and open_round.get("picked") is None:
        # a closing the owner never answered is superseded by the next one, not left pending beside it
        open_round["picked"], open_round["skipped"], open_round["superseded"] = [], True, True
    for key in ("title", "repo", "branch"):
        if data.get(key):
            state[key] = data[key]
    rnd = {"n": len(state["rounds"]) + 1, "at": now or "", "title": data.get("title", ""),
           "acts": data["acts"], "picked": None, "notes": {}}
    state["rounds"].append(rnd)
    return rnd


def record_pick(state, ids=None, round_n=None, notes=None, skipped=False, now=None):
    if not state["rounds"]:
        raise ValueError("no round to record a pick into: append a closing first")
    rnd = state["rounds"][-1] if round_n is None else next((r for r in state["rounds"] if r["n"] == round_n), None)
    if rnd is None:
        raise ValueError(f"no round {round_n}")
    known = [a["id"] for a in rnd["acts"]]
    ids = [] if skipped else list(ids or [])
    unknown = [i for i in ids if i not in known]
    if unknown:
        raise ValueError(f"round {rnd['n']}: unknown act id(s) {', '.join(unknown)}; known: {', '.join(known)}")
    if not skipped and not ids:
        raise ValueError("a pick names at least one act, or is --skipped")
    rnd["picked"] = [i for i in known if i in ids]
    rnd["skipped"] = skipped
    rnd["notes"] = {k: v for k, v in (notes or {}).items() if k in rnd["picked"] and v.strip()}
    rnd["picked_at"] = now or ""
    return rnd


def build(state):
    """The whole page for a state; its title is the latest closing's."""
    if not state["rounds"]:
        raise ValueError("a page needs at least one round")
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        page = f.read()
    with open(os.path.join(HERE, "assemble.js"), encoding="utf-8") as f:
        assemble = f.read()
    # "</" or "<!--" inside an inlined script can end it early; "<" is the same JSON string, and in
    # assemble.js "<\/" and "<\!--" are the same JS strings
    payload = json.dumps(state, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    assemble = assemble.replace("</", "<\\/").replace("<!--", "<\\!--")
    title = state["rounds"][-1].get("title") or state.get("title") or "Pending acts"
    # this order keeps an act's own text from being taken for a later placeholder: each first match is the template's
    page = page.replace("/*__ASSEMBLE__*/", assemble, 1)
    page = page.replace("__STATE__", payload, 1)
    page = page.replace("__TITLE__", html.escape(title), 1)
    return page


def write_page(page_path, state):
    os.makedirs(os.path.dirname(os.path.abspath(page_path)), exist_ok=True)
    tmp = page_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(state))
    os.replace(tmp, page_path)


def page_path_of(args):
    if args.page:
        return args.page
    if not args.session:
        raise ValueError("--page or --session is required")
    return os.path.join(args.root or os.getcwd(), ".claude", "scratchpad", "acts-widget", f"{args.session}.html")


def summary(state):
    out = []
    for r in state["rounds"]:
        if r.get("picked") is None:
            what = "open"
        elif r.get("skipped"):
            what = "superseded" if r.get("superseded") else "skipped"
        else:
            what = "picked " + ", ".join(r["picked"])
        out.append(f"  round {r['n']} ({len(r['acts'])} acts{', ' + r['at'] if r.get('at') else ''}): {what}")
    return "\n".join(out)


def main(argv):
    p = argparse.ArgumentParser(prog="build_acts_widget.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("append", "pick", "show"):
        s = sub.add_parser(name)
        if name == "append":
            s.add_argument("acts_json")
        s.add_argument("--page")
        s.add_argument("--session")
        s.add_argument("--root")
        if name != "show":
            s.add_argument("--now")
        if name == "pick":
            s.add_argument("--acts", default="")
            s.add_argument("--skipped", action="store_true")
            s.add_argument("--round", type=int)
            s.add_argument("--note", action="append", default=[])
    args = p.parse_args(argv[1:])
    try:
        path = page_path_of(args)
        state = load_state(path)
        if args.cmd == "show":
            if state is None:
                raise ValueError(f"{path}: no page yet")
            print(f"{path}\n{summary(state)}")
            return 0
        if args.cmd == "append":
            with open(args.acts_json, encoding="utf-8") as f:
                data = json.load(f)
            state = state or new_state(args.session)
            rnd = append_round(state, data, args.now)
            write_page(path, state)
            print(f"appended round {rnd['n']} ({len(rnd['acts'])} acts) to {path}\n{summary(state)}")
            return 0
        if state is None:
            raise ValueError(f"{path}: no page yet — append a closing first")
        notes = {}
        for n in args.note:
            k, sep, v = n.partition("=")
            if not sep:
                raise ValueError(f"--note {n!r}: expected ID=TEXT")
            notes[k] = v
        ids = [i.strip() for i in args.acts.split(",") if i.strip()]
        rnd = record_pick(state, ids, args.round, notes, args.skipped, args.now)
        write_page(path, state)
        print(f"recorded round {rnd['n']} in {path}\n{summary(state)}")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"build_acts_widget: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
