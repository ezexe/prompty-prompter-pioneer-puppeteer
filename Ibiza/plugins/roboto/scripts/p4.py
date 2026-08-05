#!/usr/bin/env python3
"""p4.py — the P4 closure resolver/validator for the roboto plugin.

This turns the otherwise-inert `metadata.p4` frontmatter into something that
actually runs. The Claude Code harness never parses `metadata.p4` (it reads only
`name`/`description`/`when_to_use` etc. and lets the model decide what to load),
so the closure/dependency model used to live purely as prose the model *might*
follow. This script makes that model executable and checkable.

It reads every `skills/<name>/SKILL.md`, derives the closures from each skill's
`metadata.p4.tiers` (nothing is stored — closures are computed), builds the
dependency + gate graph, and resolves/validates it.

Usage:
  p4.py                     Same as `validate`.
  p4.py validate            Validate every closure + the whole graph. Exit 1 on any issue.
  p4.py resolve <closure>   Resolve one closure: members, transitive deps, active gates, satisfied?
  p4.py check <closure>     Gate-check one closure: valid?, issues. Exit 1 if invalid.
  p4.py list                List skills and a summary of their metadata.p4.

Model (derived, not stored):
  * `identity` + `rubric` are the ALWAYS-ON base: members of every closure, and
    deliberately never listed in any skill's `depends_on` (declared once in the
    roboto agent). This script flags any skill that re-lists them.
  * A closure's members = `identity` + `rubric` + every skill whose
    `metadata.p4.tiers` lists that closure.
  * `depends_on` uses two id-spaces: skill names (must resolve to a skill dir,
    and be present in the closure) and P4 gate ids (prompty|prompter|pioneer|
    puppeteer), which resolve to the fixed gate graph rather than to a skill.
  * `optional_depends_on` enhances but is NOT required for closure.
  * A skill's `hooks.on_<gate>` and its `phases` are two declarations of the same
    fact. A non-empty hook on a gate absent from `phases` is an undeclared hook.

The puppeteer->prompty edge:
  `/p4-puppeteer` registers a closure with TWO writes -- a row in the `rubric`
  gate table and the closure name in each member's `tiers` -- and `/p4-prompty`
  then selects that closure by scoring the request against those same rubric
  rows. The tiers half is a graph this script derives; the rubric half was, until
  now, unvalidated prose. `reconcile_rubric` closes that loop: it parses the gate
  table out of `skills/rubric/SKILL.md` and checks it against the derived
  closures, so a row without a closure (unselectable phantom), a closure without
  a row (unreachable), a false marginal-capability claim, or a rung that drops
  what the rung below it declared all fail the gate instead of shipping.
"""

import re
import sys
from pathlib import Path

ALWAYS_ON = ("identity", "rubric")
GATES = ("prompty", "prompter", "pioneer", "puppeteer")
# Fixed gate chain (each gate pulls the gates before it). identity is always-on,
# so it is omitted here; this models gate prerequisites only.
GATE_CHAIN = {
    "prompty": [],
    "prompter": ["prompty"],
    "pioneer": ["prompty", "prompter"],
    "puppeteer": ["prompty", "prompter", "pioneer"],
}

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


# --- parsing -------------------------------------------------------------

def _inline_list(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [x.strip().strip('"').strip("'") for x in raw.split(",") if x.strip()]


def _frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[4:end] if end != -1 else None


def _parse(fm):
    """Pull name + the metadata.p4 fields we need.

    Prefers a real YAML parser; falls back to targeted regex for the inline-list
    style this repo uses uniformly, so the script needs no third-party deps.
    """
    try:
        import yaml  # optional; nicer if present
        data = yaml.safe_load(fm) or {}
        p4 = (data.get("metadata") or {}).get("p4") or {}
        hooks = p4.get("hooks") or {}
        return {
            "name": data.get("name"),
            "depends_on": list(p4.get("depends_on") or []),
            "optional_depends_on": list(p4.get("optional_depends_on") or []),
            "tiers": list(p4.get("tiers") or []),
            "phases": list(p4.get("phases") or []),
            "hooked": sorted(k[3:] for k, v in hooks.items() if k.startswith("on_") and v),
        }
    except Exception:
        def grab(pat):
            m = re.search(pat, fm, re.M)
            return _inline_list(m.group(1)) if m else []
        name_m = re.search(r"^name:\s*(.+)$", fm, re.M)
        return {
            "name": name_m.group(1).strip() if name_m else None,
            # negative lookbehind so this does not also match optional_depends_on
            "depends_on": grab(r"(?<![\w_])depends_on:\s*(\[.*?\])"),
            "optional_depends_on": grab(r"optional_depends_on:\s*(\[.*?\])"),
            "tiers": grab(r"tiers:\s*(\[.*?\])"),
            "phases": grab(r"phases:\s*(\[.*?\])"),
            "hooked": sorted(m.group(1) for m in re.finditer(r"on_(\w+):\s*\[\s*\w", fm)),
        }


def load_skills():
    if not SKILLS_DIR.is_dir():
        sys.exit(f"error: skills dir not found at {SKILLS_DIR}")
    skills = {}
    for d in sorted(SKILLS_DIR.iterdir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        fm = _frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            continue
        skills[d.name] = _parse(fm)
    return skills


# --- graph helpers -------------------------------------------------------

def all_closures(skills):
    cs = set()
    for s in skills.values():
        cs.update(s["tiers"])
    return sorted(cs)


def members(skills, closure):
    m = set(ALWAYS_ON)
    for name, s in skills.items():
        if closure in s["tiers"]:
            m.add(name)
    return sorted(m)


def active_gates(skills, member_names):
    g = set()
    for n in member_names:
        for p in skills.get(n, {}).get("phases", []):
            if p in GATES:
                g.add(p)
                g.update(GATE_CHAIN[p])
    return sorted(g, key=GATES.index)


def skill_deps(deps):
    return [d for d in deps if d not in GATES]


def gate_deps(deps):
    return [d for d in deps if d in GATES]


def gate_hookers(skills, member_names):
    """How many members hook each gate directly, by their own `phases`.

    The bare list of active gates cannot discriminate between closures: the
    always-on base declares all four phases, so every closure activates the whole
    chain. The per-gate count is the part that actually varies.
    """
    return {g: sum(1 for n in member_names if g in skills.get(n, {}).get("phases", []))
            for g in GATES}


# --- the rubric gate table (the puppeteer->prompty half) -----------------

RUBRIC_MD = SKILLS_DIR / "rubric" / "SKILL.md"


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _ticked(cell):
    """The backticked identifiers in a table cell, in order."""
    return re.findall(r"`([\w-]+)`", cell)


def load_rubric_rows(path=RUBRIC_MD):
    """Parse the rubric gate table -- the surface `prompty` selects a closure from.

    Columns, in order: #, signal, marginal capability it adds, builds on, closure.
    Returns (rows, error); `error` is set whenever the table cannot be found or no
    row parses, so the caller fails closed instead of silently checking nothing.
    """
    if not path.is_file():
        return [], f"rubric gate table: {path} not found"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        c = _cells(line)
        if len(c) < 5 or not c[0].isdigit():
            continue
        rows.append({
            "n": int(c[0]),
            "marginal": _ticked(c[2]),
            "builds_on": _ticked(c[3]),
            "closure": (_ticked(c[4]) or [None])[0],
        })
    if not rows:
        return [], f"rubric gate table: no numbered rows parsed from {path}"
    return rows, None


def reconcile_rubric(skills, rows):
    """Check the rubric gate table against the derived closure graph.

    This is the puppeteer->prompty edge: `/p4-puppeteer` writes a rubric row AND
    the members' tiers, and `/p4-prompty` selects on the row. Returns a list of
    (closure, message) pairs so a single-closure gate-check can filter.
    """
    out = []
    derived = set(all_closures(skills))
    seen = {}

    for r in rows:
        c, n = r["closure"], r["n"]
        if c is None:
            out.append((None, f"rubric row {n}: closure cell names no backticked closure"))
            continue
        if c in seen:
            out.append((c, f"rubric row {n}: closure '{c}' already selected by row {seen[c]}"))
        seen[c] = n
        if c not in derived:
            out.append((c, f"rubric row {n}: '{c}' is selectable but no skill's tiers lists it (phantom row)"))
            continue
        mem = set(members(skills, c))
        for parent in r["builds_on"]:
            if parent not in derived:
                out.append((c, f"rubric row {n}: builds on '{parent}', which is not a closure"))
                continue
            pmem = set(members(skills, parent))
            dropped = sorted(pmem - mem)
            if dropped:
                out.append((c, f"rubric row {n}: '{c}' builds on '{parent}' but drops {', '.join(dropped)}"))
            for skill in r["marginal"]:
                if skill in pmem:
                    out.append((c, f"rubric row {n}: '{skill}' is claimed as marginal but is already in '{parent}'"))
        for skill in r["marginal"]:
            if skill not in skills:
                out.append((c, f"rubric row {n}: marginal capability '{skill}' resolves to no skill"))
            elif skill not in mem:
                out.append((c, f"rubric row {n}: claims marginal '{skill}', which is not a member of '{c}'"))

    for c in sorted(derived - set(seen)):
        out.append((c, f"closure '{c}' has no rubric row -- prompty can never select it (unreachable)"))
    return out


# --- commands ------------------------------------------------------------

def cmd_resolve(skills, closure):
    cs = all_closures(skills)
    if closure not in cs:
        print(f"unknown closure: {closure!r}. known closures: {', '.join(cs)}")
        return 2
    m = members(skills, closure)
    pulled = [n for n in m if n not in ALWAYS_ON]
    missing = {}
    gates_from_deps = set()
    absent = [n for n in m if n not in skills]
    for n in m:
        if n in absent:
            continue
        deps = skills[n]["depends_on"]
        gates_from_deps.update(gate_deps(deps))
        miss = [d for d in skill_deps(deps) if d not in m]
        if miss:
            missing[n] = miss
    gates = sorted(set(active_gates(skills, m)) | gates_from_deps, key=GATES.index)

    print(f"closure: {closure}")
    print(f"  members ({len(m)}): {', '.join(m)}")
    print(f"    always-on: {', '.join(ALWAYS_ON)}")
    print(f"    pulled by tier: {', '.join(pulled) or '(none)'}")
    if absent:
        print(f"    MISSING SKILL.md: {', '.join(absent)}")
    hookers = gate_hookers(skills, m)
    print(f"  active gates: {', '.join(gates) or '(none)'}")
    print(f"    members hooking each: {', '.join(f'{g}={hookers[g]}' for g in gates)}")
    print(f"  dependencies_satisfied: {str(not missing and not absent).lower()}")
    if missing:
        for n, miss in sorted(missing.items()):
            print(f"    missing: {n} -> {', '.join(miss)}")
    return 0 if not missing and not absent else 1


def _closure_issues(skills, closure):
    issues = []
    m = set(members(skills, closure))
    for n in sorted(m):
        if n not in skills:
            # Only the always-on base can be a member without a SKILL.md behind it,
            # and it is the model's most load-bearing assumption -- report it, never crash.
            issues.append(f"always-on base skill '{n}' has no skills/{n}/SKILL.md")
            continue
        for d in skills[n]["depends_on"]:
            if d in GATES:
                continue
            if d not in skills:
                issues.append(f"{n}: depends_on '{d}' resolves to no skill (dangling)")
            elif d not in m:
                issues.append(f"{n}: depends_on '{d}' not present in closure '{closure}'")
        for p in skills[n]["phases"]:
            if p not in GATES:
                issues.append(f"{n}: phase '{p}' is not a valid gate id")
        for a in ALWAYS_ON:
            if a in skills[n]["depends_on"]:
                issues.append(f"{n}: lists always-on '{a}' in depends_on (should be implicit)")
    return issues


def cmd_check(skills, closure):
    cs = all_closures(skills)
    if closure not in cs:
        print(f"unknown closure: {closure!r}. known closures: {', '.join(cs)}")
        return 2
    issues = _closure_issues(skills, closure)

    rows, err = load_rubric_rows()
    if err:
        issues.append(err)
        row = None
    else:
        issues.extend(msg for c, msg in reconcile_rubric(skills, rows) if c == closure)
        row = next((r for r in rows if r["closure"] == closure), None)

    print(f"closure: {closure}")
    print(f"  members: {', '.join(members(skills, closure))}")
    if row:
        builds = ", ".join(row["builds_on"]) or "(base)"
        adds = ", ".join(row["marginal"]) or "(contract only)"
        print(f"  rubric row: {row['n']} -- builds on {builds}; adds {adds}")
    elif not err:
        print("  rubric row: (none -- prompty can never select this closure)")
    print(f"  valid: {str(not issues).lower()}")
    for i in issues:
        print(f"  issue: {i}")
    return 0 if not issues else 1


def cmd_validate(skills):
    names = set(skills)
    issues = []
    for n, s in sorted(skills.items()):
        for d in s["depends_on"]:
            if d in GATES:
                continue
            if d in ALWAYS_ON:
                issues.append(f"{n}: depends_on lists always-on '{d}' (should be implicit -- declared in agents/roboto.md)")
            elif d not in names:
                issues.append(f"{n}: depends_on '{d}' resolves to no skill (dangling)")
        for d in s["optional_depends_on"]:
            if d in GATES or d in names:
                continue
            issues.append(f"{n}: optional_depends_on '{d}' resolves to no skill (dangling)")
        for p in s["phases"]:
            if p not in GATES:
                issues.append(f"{n}: phase '{p}' is not a valid gate id")
        for g in s["hooked"]:
            if g not in GATES:
                issues.append(f"{n}: hook 'on_{g}' is not a valid gate id")
            elif g not in s["phases"]:
                issues.append(f"{n}: hooks on_{g} is non-empty but '{g}' is absent from phases (undeclared hook)")
        if not s["tiers"]:
            issues.append(f"{n}: no tiers (member of no closure)")
    for c in all_closures(skills):
        issues.extend(_closure_issues(skills, c))

    rows, err = load_rubric_rows()
    if err:
        issues.append(err)
    else:
        issues.extend(msg for _, msg in reconcile_rubric(skills, rows))

    closures = all_closures(skills)
    print(f"skills: {len(skills)}  |  closures: {', '.join(closures)}  |  rubric rows: {len(rows)}")
    if not issues:
        print("VALID: every closure is dependency-closed; no dangling refs; hooks match phases;")
        print("       every rubric row resolves and every closure is selectable; convention holds.")
        return 0
    issues = sorted(set(issues))  # the same defect reaches this list once per closure it breaks
    print(f"INVALID: {len(issues)} issue(s):")
    for i in issues:
        print(f"  - {i}")
    return 1


def cmd_list(skills):
    width = max(len(n) for n in skills) if skills else 0
    for n, s in sorted(skills.items()):
        tier = ",".join(s["tiers"]) or "-"
        dep = ",".join(s["depends_on"]) or "-"
        opt = ",".join(s["optional_depends_on"]) or "-"
        ph = ",".join(s["phases"]) or "-"
        print(f"{n.ljust(width)}  tiers=[{tier}]  depends_on=[{dep}]  optional=[{opt}]  phases=[{ph}]")
    return 0


def main(argv):
    skills = load_skills()
    cmd = argv[0] if argv else "validate"
    if cmd == "validate":
        return cmd_validate(skills)
    if cmd == "list":
        return cmd_list(skills)
    if cmd in ("resolve", "check"):
        if len(argv) < 2:
            print(f"usage: p4.py {cmd} <closure>   (closures: {', '.join(all_closures(skills))})")
            return 2
        fn = cmd_resolve if cmd == "resolve" else cmd_check
        return fn(skills, argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
