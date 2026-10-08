#!/usr/bin/env python3
"""Acceptance tests for the acts widget: the page builds, and the prompt it sends reads as exact instructions."""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_acts_widget as b  # noqa: E402

SAMPLE = {
    "title": "Release the fix",
    "repo": "owner/repo",
    "branch": "work",
    "acts": [
        {"id": "commit", "title": "Commit the fix", "summary": "One commit.", "goal": "Commit the staged fix with a descriptive message.",
         "files": ["src/a.py"], "constraints": ["Do not amend earlier commits"], "done": "The commit exists.", "recommended": True},
        {"id": "push", "title": "Push the branch", "goal": "Push the branch to origin."},
        {"id": "pr", "title": "Open a PR", "goal": "Open a pull request.</script><b>x</b>"},
    ],
}


def test_build():
    page = b.build(json.loads(json.dumps(SAMPLE)))
    assert "__TITLE__" not in page and "/*__DATA__*/" not in page and "/*__ASSEMBLE__*/" not in page
    assert "<title>Release the fix</title>" in page
    assert "function assemblePrompt" in page
    assert page.count("</script>") == 1, "an act's text closed the script element"


def test_validation():
    for bad, why in (({"acts": []}, "non-empty"),
                     ({"acts": [{"id": "a", "title": "A"}]}, "missing goal"),
                     ({"acts": [{"id": "a", "title": "A", "goal": "g"}, {"id": "a", "title": "B", "goal": "g"}]}, "duplicate")):
        try:
            b.build(bad)
        except ValueError as e:
            assert why in str(e), (why, e)
        else:
            raise AssertionError(f"accepted: {why}")


def test_prompt():
    node = shutil.which("node")
    if not node:
        print("skip  test_prompt (no node)")
        return
    js = ("const {assemblePrompt}=require(process.argv[1]);const d=JSON.parse(process.argv[2]);"
          "process.stdout.write(JSON.stringify([assemblePrompt(d,['commit','pr'],{pr:'draft only'}),assemblePrompt(d,[],{})]))")
    out = subprocess.run([node, "-e", js, os.path.join(HERE, "assemble.js"), json.dumps(SAMPLE)],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    md, empty = json.loads(out)
    assert empty == ""
    assert md.startswith("## Picked acts\n"), md[:40]
    assert "Run them exactly as written below, in the order listed, and run nothing else from that closing." in md
    assert md.index("### Act 1 of 2: Commit the fix") < md.index("### Act 2 of 2: Open a PR")
    assert "This act is done when the commit exists." in md
    assert "My added context for this act: draft only" in md
    assert "### Not picked" in md and "- Push the branch" in md
    assert "Open your reply with the Deviations block" in md


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok    {name}")
    print("test_acts_widget.py: all green")
