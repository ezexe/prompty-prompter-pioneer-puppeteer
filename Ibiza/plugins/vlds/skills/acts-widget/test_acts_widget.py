#!/usr/bin/env python3
"""Acceptance tests for the acts widget: one page per session, appended per closing, picks recorded into it, and
the prompt it sends reads as exact instructions."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_acts_widget as b  # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "..", "hooks"))
import vlds_hooks as vh  # noqa: E402

SAMPLE = {
    "title": "Release the fix",
    "repo": "owner/repo",
    "branch": "work",
    "acts": [
        {"id": "commit", "title": "Commit the fix", "summary": "One commit.", "goal": "Commit the staged fix with a descriptive message.",
         "files": ["src/a.py"], "constraints": ["Do not amend earlier commits"], "done": "The commit exists.", "recommended": True,
         "briefs": {"changes": "one commit on main", "scope": "this repo only"}},
        {"id": "push", "title": "Push the branch", "goal": "Push the branch to origin."},
        {"id": "pr", "title": "Open a PR", "goal": "Open a pull request.</script><!--<script>__TITLE__ __STATE__"},
    ],
}
NEXT = {"title": "After the release", "acts": [{"id": "tag", "title": "Tag it", "goal": "Tag the release."}]}


def fresh(data=SAMPLE):
    state = b.new_state("abc12345")
    b.append_round(state, json.loads(json.dumps(data)), "2026-10-08 18:50")
    return state


def test_build():
    page = b.build(fresh())
    assert "/*__ASSEMBLE__*/" not in page and "<title>Release the fix</title>" in page
    assert "function assemblePrompt" in page
    assert page.count("</script>") == 2, "an act's text closed a script element"
    assert "<!--<script>" not in page, "an act's text opened a comment inside a script"
    assert b.STATE_RE.search(page), "the state block is unreadable"


def test_validation():
    for bad, why in (({"acts": []}, "non-empty"),
                     ({"acts": [{"id": "a", "title": "A"}]}, "missing goal"),
                     ({"acts": [{"id": "a", "title": "A", "goal": "g"}, {"id": "a", "title": "B", "goal": "g"}]}, "duplicate")):
        try:
            b.append_round(b.new_state(), bad)
        except ValueError as e:
            assert why in str(e), (why, e)
        else:
            raise AssertionError(f"accepted: {why}")


def test_session_page_round_trip():
    with tempfile.TemporaryDirectory() as root:
        acts1, acts2 = os.path.join(root, "a1.json"), os.path.join(root, "a2.json")
        for path, data in ((acts1, SAMPLE), (acts2, NEXT)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        run = lambda *a: b.main(["x", *a, "--session", "abc12345", "--root", root])  # noqa: E731
        page = os.path.join(root, ".claude", "scratchpad", "acts-widget", "abc12345.html")

        assert run("pick", "--acts", "commit") == 1, "a pick before any closing was accepted"
        assert run("append", acts1, "--now", "2026-10-08 18:50") == 0 and os.path.exists(page)
        assert run("pick", "--acts", "nope") == 1, "an unknown act id was accepted"
        assert run("pick", "--acts", "pr,commit", "--note", "pr=draft only", "--note", "push=x") == 0
        assert run("append", acts2) == 0
        state = b.load_state(page)
        assert len(state["rounds"]) == 2, "the second closing did not append to the same page"
        r1, r2 = state["rounds"]
        assert r1["picked"] == ["commit", "pr"], "a pick is kept in the round's own act order"
        assert r1["notes"] == {"pr": "draft only"}, "a note on an unpicked act was kept"
        assert r1["acts"][2]["goal"] == SAMPLE["acts"][2]["goal"], "an act's text did not survive the page"
        assert r2["picked"] is None and state["title"] == "After the release" and state["repo"] == "owner/repo"

        assert run("append", acts1) == 0, "a third closing over an unanswered one"
        state = b.load_state(page)
        assert state["rounds"][1]["superseded"] and state["rounds"][1]["picked"] == []
        assert run("pick", "--skipped") == 0 and b.load_state(page)["rounds"][2]["skipped"]

        foreign = os.path.join(root, "other.html")
        with open(foreign, "w", encoding="utf-8") as f:
            f.write("<p>not an acts page</p>")
        assert b.main(["x", "append", acts1, "--page", foreign]) == 1, "a page that is not an acts page was overwritten"


def test_prompt():
    node = shutil.which("node")
    if not node:
        print("skip  test_prompt (no node)")
        return
    data = dict(SAMPLE, round=3)
    js = ("const {assemblePrompt}=require(process.argv[1]);const d=JSON.parse(process.argv[2]);"
          "process.stdout.write(JSON.stringify([assemblePrompt(d,['pr','commit'],{pr:'draft only'}),assemblePrompt(d,[],{})]))")
    out = subprocess.run([node, "-e", js, os.path.join(HERE, "assemble.js"), json.dumps(data)],
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
    assert md.endswith("<!-- acts-widget round=3 picked=commit,pr -->"), md[-80:]


def test_page_runs():
    """The built page's script runs: the live round renders, the log holds the answered one."""
    node = shutil.which("node")
    if not node:
        print("skip  test_page_runs (no node)")
        return
    state = fresh()
    b.record_pick(state, ["commit"])
    b.append_round(state, json.loads(json.dumps(NEXT)))
    page = b.build(state)
    scripts = page.split("<script")
    state_js = scripts[1].split(">", 1)[1].split("</script>")[0]
    main_js = scripts[2].split(">", 1)[1].split("</script>")[0]
    # a minimal DOM: enough for the page's own calls, so a thrown error or a wrong prompt fails the test;
    # listeners are kept so a click can be fired, and execCommand/sendPrompt record what they were handed
    shim = r"""
const els = {}; const seen = {copy: null, sent: null};
function mk(tag){const e={tagName:tag,children:[],hidden:false,disabled:false,className:'',textContent:'',value:'',style:{},
  set innerHTML(v){this._html=v;this.children=[];},get innerHTML(){return this._html||'';},
  appendChild(c){this.children.push(c);return c;},removeChild(c){this.children=this.children.filter((x)=>x!==c);},
  addEventListener(t,f){(this._on=this._on||{})[t]=f;},scrollIntoView(){},setAttribute(){},after(){},
  select(){global.__sel=this.value;},querySelector(){return mk('q');}};return e;}
global.document={getElementById:(id)=>id==='acts-state'?{textContent:STATE_TEXT}:(els[id]=els[id]||mk(id)),
  createElement:mk,createRange:()=>({selectNodeContents(){}}),body:mk('body'),
  execCommand:(c)=>{if(c!=='copy')return false;if(EXEC_OK)seen.copy=global.__sel;return EXEC_OK;}};
global.getSelection=()=>({removeAllRanges(){},addRange(){}});global.navigator={};
els.send=Object.assign(mk('send'),{hidden:true});
if (SEND) global.sendPrompt=(t)=>{seen.sent=t;};
"""
    probe = (";picked.add('tag');render();els.copy._on.click();if(SEND)els.send._on.click();"
             "process.stdout.write(JSON.stringify({log:els.log.children.length,acts:els.acts.children.length,"
             "label:els['acts-label'].textContent,panesHidden:document.getElementById('panes').hidden,prompt:current(),"
             "sendHidden:els.send.hidden,status:els.status.textContent,seen}))")

    def run(send, exec_ok):
        js = ("const STATE_TEXT=" + json.dumps(state_js) + ";const SEND=" + json.dumps(send) +
              ";const EXEC_OK=" + json.dumps(exec_ok) + ";" + shim + main_js + probe)
        out = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8")
        assert out.returncode == 0, out.stderr
        return json.loads(out.stdout)

    r = run(False, True)
    assert r["log"] == 1 and r["acts"] == 1 and r["label"] == "Closing 2 · pending acts" and r["panesHidden"] is False, r
    assert "### Act 1 of 1: Tag it" in r["prompt"]
    assert r["seen"]["copy"] == r["prompt"], "the Copy click did not copy the prompt itself"
    assert r["status"].startswith("Copied."), r["status"]
    assert r["sendHidden"] is True, "Send showed where there is no sendPrompt"

    r = run(False, False)
    assert "press Ctrl+C" in r["status"], "a blocked copy did not fall back to the selection"

    r = run(True, True)
    assert r["sendHidden"] is False and r["seen"]["sent"] == r["prompt"], "the Send click did not send the prompt"
    assert r["status"].startswith("Sent."), r["status"]

def test_widget_fragment():
    """The page as a chat widget's code: no document skeleton, the body scoped to a transparent wrapper, the
    state still readable — by the page, and by the hook's pre-ask gate."""
    code = b.fragment(fresh())
    low = code.lower()
    for tag in ("<!doctype", "<html", "<head>", "</head>", "<body", "</body", "</html", "<title", "<meta"):
        assert tag not in low, f"the fragment keeps {tag}"
    assert code.startswith("<style>") and '<div class="acts-page">' in code and "\nbody {" not in code
    assert ".acts-page { margin: 0; background: transparent;" in code
    assert b.STATE_RE.search(code) and code.count("</script>") == 2
    with tempfile.TemporaryDirectory() as root:
        acts = os.path.join(root, "a.json")
        with open(acts, "w", encoding="utf-8") as f:
            json.dump(SAMPLE, f)
        out = os.path.join(root, "w.html")
        assert b.main(["x", "append", acts, "--session", "s1", "--root", root]) == 0
        assert b.main(["x", "widget", "--session", "s1", "--root", root, "--out", out]) == 0
        with open(out, encoding="utf-8") as f:
            written = f.read()
        assert written.startswith("<style>") and "Release the fix" in written, "the widget command wrote no fragment"
        assert b.main(["x", "widget", "--session", "nope", "--root", root]) == 1, "a widget of no page was printed"
    try:
        b.append_round(b.new_state(), {"acts": [{"id": "a", "title": "A", "goal": "g", "briefs": ["x"]}]})
    except ValueError as e:
        assert "briefs" in str(e)
    else:
        raise AssertionError("a briefs list was accepted")


def test_hook_reads_acts_page():
    """The prompt hook takes the page's prompt for a picker submit, not a detail-ask; the pre-ask gate reads
    the open round's acts as the widget's options and bounces one that lacks a standing label."""
    md = ("## Picked acts I picked one act from your closing widget (“Release the fix”). Run it exactly as "
          "written below. ### Act 1 of 1: Commit the fix Commit it. My added context for this act: draft only "
          "### How to report Open your reply. <!-- acts-widget round=3 picked=commit -->")
    assert vh.picker_shape(md) == ("submit", "Release the fix", False)
    asked = md.replace("draft only", "why main?")
    assert vh.picker_shape(asked) == ("submit", "Release the fix", True), "a question in the context did not ride"
    assert vh.picker_shape("## Picked acts with no marker") is None

    state = fresh()
    payload = {"tool_name": "mcp__visualize__show_widget",
               "tool_input": {"title": "release_closing", "widget_code": b.fragment(state)}}
    opts, _key = vh.picker_options(payload)
    assert [o for o, _ in opts] == ["Commit the fix", "Push the branch", "Open a PR"], opts
    assert "changes: one commit on main" in opts[0][1] and "scope: this repo only" in opts[0][1]
    b.record_pick(state, ["commit"])
    payload["tool_input"]["widget_code"] = b.fragment(state)
    assert vh.picker_options(payload)[0] == [], "an answered round still offered options"

    real = vh.standing_labels
    vh.standing_labels = lambda store: {"changes": 2, "scope": 2}
    try:
        import contextlib, io
        for code, want in ((b.fragment(fresh()), "deny"), (b.fragment(fresh(dict(SAMPLE, acts=SAMPLE["acts"][:1]))), "")):
            with tempfile.TemporaryDirectory() as store:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    vh.cmd_pre_ask({"tool_name": "mcp__visualize__show_widget",
                                    "tool_input": {"title": "t", "widget_code": code}}, store)
                assert (want in buf.getvalue()) if want else buf.getvalue() == "", (want, buf.getvalue())
    finally:
        vh.standing_labels = real


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok    {name}")
    print("test_acts_widget.py: all green")
