#!/usr/bin/env python3
"""Build the acts widget page: one self-contained HTML file from a closing's acts.

Usage: build_acts_widget.py ACTS.json OUT.html

ACTS.json:
  {"title": "...", "repo": "owner/name", "branch": "...",
   "acts": [{"id": "...", "title": "...", "summary": "...", "goal": "...",
             "files": ["..."], "constraints": ["..."], "done": "...", "recommended": true}]}

Every act needs id, title and goal; ids are unique. The page inlines assemble.js, so the prompt
it shows is built by the same function the test runs.
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ("id", "title", "goal")


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


def build(data):
    validate(data)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        page = f.read()
    with open(os.path.join(HERE, "assemble.js"), encoding="utf-8") as f:
        assemble = f.read()
    # "</" inside inlined script would close the <script> element early
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = page.replace("__TITLE__", html.escape(data.get("title") or "Pending acts"), 1)
    page = page.replace("/*__ASSEMBLE__*/", assemble.replace("</", "<\\/"), 1)
    page = page.replace("/*__DATA__*/null", payload, 1)
    return page


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        data = json.load(f)
    try:
        page = build(data)
    except ValueError as e:
        print(f"build_acts_widget: {e}", file=sys.stderr)
        return 1
    with open(argv[2], "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    print(f"wrote {argv[2]} — {len(data['acts'])} acts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
