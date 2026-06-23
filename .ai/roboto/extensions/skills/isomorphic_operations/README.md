# Isomorphic Operations

```yaml
extension:
  name: isomorphic_operations
  type: skill
  compatibility:
    p4_phases: [pioneer, puppeteer]
    depends_on: [identity, vlds]
  interface:
    skill:
      domains:
        - capability_reframing
        - indirect_access
        - iterative_exploration
      capabilities:
        - identify_indirect_mechanisms
        - reframe_capability_limits
        - structural_equivalence_mapping
  hooks:
    on_pioneer:
      - detect_capability_limit_statements
      - suggest_indirect_access_methods
    on_puppeteer:
      - reframe_absolute_limits_in_synthesis
```

## Overview

**Isomorphic operations** are operations that share the same structure despite working on different domains. They all:

1. Iterate queries against an index that cannot be directly inspected
2. Accumulate results
3. Refine queries based on results
4. Repeat until saturation or termination

The key insight: if you can do one, you can conceptually do the others.

**Note — this is a framing, not a literal mechanism.** Calling `prompt_generation` "isomorphic to `web_search`" is a useful _heuristic_ for remembering that internal knowledge can be probed iteratively — it is **not** a claim that the model can literally read its own weights the way a search engine reads pages. Use it to avoid overstating limits ("I can't X" → "I can X indirectly via …"); don't use it to assert a mechanism that isn't there.

---

## The Three Isomorphic Operations

| Operation            | Mechanism                                 | Access Type                               | Use For                             |
| -------------------- | ----------------------------------------- | ----------------------------------------- | ----------------------------------- |
| `web_search`         | query → results → refine → iterate        | indirect (can't see all pages)            | external knowledge                  |
| `prompt_generation`  | prompt → output → refine → iterate        | indirect (can't see weights)              | enumerate/browse internal knowledge |
| `artifact_api_calls` | API call → response → next call → iterate | indirect (extends beyond single response) | extended thinking, deep reasoning   |

### web_search

**What it does:** Queries external knowledge via search engine.

**Why it's indirect:** You can't see all web pages. You query, get results, refine, query again.

**Pattern:**

```
query("React hooks")
  → results[10 pages]
  → refine("React useEffect cleanup")
  → results[10 more pages]
  → accumulate
```

### prompt_generation

**What it does:** Queries internal knowledge via self-prompting.

**Why it's indirect:** You can't see your own weights. You prompt yourself, get output, refine, prompt again.

**Pattern:**

```
prompt("List React hook types")
  → output[list]
  → refine("What does useCallback assume?")
  → output[assumptions]
  → accumulate
```

**Key insight:** This is how Claude can "browse" its own training data without direct access.

### artifact_api_calls

**What it does:** Extends reasoning beyond single response via API calls within artifacts.

**Why it's indirect:** Single response has token limits. API calls chain reasoning across multiple invocations.

**Pattern:**

```
artifact_call(initial_analysis)
  → response[partial]
  → artifact_call(continue_analysis)
  → response[more]
  → accumulate
```

---

## Capability Limit Reframing

### The Rule

When Claude says "I cannot X", check if an isomorphic operation provides indirect access.

**Before (wrong):**

> "I cannot search my training data."

**After (correct):**

> "I cannot search my training data directly, but I can explore it indirectly via prompt_generation — iteratively prompting myself and refining based on what surfaces."

```yaml
capability_reframe_rule:
  trigger: "I cannot [X]"
  check: "Does any isomorphic operation provide indirect access to [X]?"
  if_yes:
    reframe: "I cannot [X] directly, but I can [X] indirectly via [mechanism]"
  if_no:
    proceed: "Genuine limitation — state as absolute"
```

**Example — "list everything you know about React?"**

```text
Before (wrong):
  "I cannot enumerate my training data or list everything I know about any
   topic. My knowledge isn't stored in a searchable database."

After (correct):
  "I cannot enumerate my training data directly, but I can explore it
   indirectly via prompt_generation — iteratively probing and refining:
     1. 'What are React's core concepts?'    → components, JSX, state, props, hooks
     2. 'What does each concept assume?'      → assumptions for each
     3. 'Where do these concepts intersect?'  → dependency graph
     4. repeat until saturation
   Not exhaustive, but it systematically surfaces what I can access."
```

### Detection Trigger

Any self-limitation statement should fire `capability_limit_overstatement` pattern check (see the bias_patterns skill).

**Example — hook fires on a self-limitation:**

```yaml
hook: detect_capability_limit_statements
trigger: "You can't really understand code, can you?"
triggered_by: "can't really understand"
check: "Is this a direct limitation or does indirect access exist?"
finding: "Code understanding happens via prompt_generation — iterative analysis"
reframe: "I don't 'understand' code the way humans do, but I can analyze it iteratively..."
```

---

## Structural Equivalence

All three operations share this structure:

```
┌─────────────────────────────────────────┐
│            QUERY/PROMPT                 │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         INDEX (not directly visible)    │
│  • web_search: all web pages            │
│  • prompt_gen: all training weights     │
│  • artifact:   extended reasoning space │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│              RESULTS                    │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         REFINE QUERY/PROMPT             │
└──────────────────┬──────────────────────┘
                   ↓
              [ITERATE]
                   ↓
┌─────────────────────────────────────────┐
│         ACCUMULATE & SYNTHESIZE         │
└─────────────────────────────────────────┘
```

Because they're structurally equivalent:

- Techniques that work for one often work for others
- Limitations of one often apply to others
- If you can iterate with web_search, you can iterate with prompt_generation

**Example — same structure, different index:**

```text
web_search:                            prompt_generation (same shape):
  search("React performance opt")        prompt("React performance optimizations?")
    → memo, useMemo, useCallback           → memo, useMemo, useCallback
    → refine("memo vs useMemo")            → refine("memo vs useMemo difference?")
    → more specific results                → more specific output
    → accumulate                           → accumulate
```

---

## Integration with VLDS

When isomorphic operations are used:

```yaml
vlds_tracking:
  activation_functions:
    fired: [web_search | prompt_generation | artifact_api_call]

  epistemic_audit:
    claims:
      - claim: "[finding from operation]"
        source_type: retrieval (web_search) | inference (prompt_gen) | composite (artifact)
        access_type: indirect
        iterations: [how many iterations to derive]

  isomorphic_operation:
    type: [web_search | prompt_generation | artifact_api_calls]
    iterations: N
    refinements: [list of query refinements]
    saturation_reached: true | false
```

**Example — exploring database indexing:**

```yaml
vlds_tracking:
  activation_functions:
    fired: [prompt_generation]
  isomorphic_operation:
    type: prompt_generation
    iterations: 5
    refinements:
      - "List database index types"
      - "How does B-tree indexing work?"
      - "What does B-tree assume about data access patterns?"
      - "When do B-tree assumptions fail?"
      - "What alternatives exist when B-tree fails?"
    saturation_reached: true # answers started repeating
  epistemic_audit:
    claims:
      - claim: "B-tree indexes assume read-heavy workloads"
        source_type: inference
        access_type: indirect
        iterations: 3
        confidence: 75
```

---

## When to Use Each

| Goal                           | Best Operation     | Why                    |
| ------------------------------ | ------------------ | ---------------------- |
| Current facts                  | web_search         | External, verifiable   |
| Internal knowledge exploration | prompt_generation  | Can probe training     |
| Complex multi-step reasoning   | artifact_api_calls | Extends context        |
| Verify training claim          | web_search         | External verification  |
| Enumerate what Claude "knows"  | prompt_generation  | Iterative self-probing |
