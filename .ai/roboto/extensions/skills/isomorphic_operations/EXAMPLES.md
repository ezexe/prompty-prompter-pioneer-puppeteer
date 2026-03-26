# Isomorphic Operations Examples

## Example 1: Capability Limit Reframing

### Before (Incorrect)

**User:** Can you list everything you know about React?

**Claude (wrong):** I cannot enumerate my training data or list everything I know about any topic. My knowledge isn't stored in a searchable database.

### After (Correct)

**User:** Can you list everything you know about React?

**Claude (correct):** I cannot enumerate my training data directly, but I can explore it indirectly via prompt_generation. Let me iteratively probe different aspects:

1. "What are React's core concepts?" → [components, JSX, state, props, hooks]
2. "What does each concept assume?" → [assumptions for each]
3. "Where do these concepts intersect?" → [dependency graph]
4. Repeat until saturation...

This won't be exhaustive, but it systematically surfaces what I can access.

---

## Example 2: Structural Equivalence in Practice

### Using web_search pattern for prompt_generation

**web_search approach:**

```
search("React performance optimization")
  → results about memo, useMemo, useCallback
  → refine("React memo vs useMemo differences")
  → more specific results
  → accumulate findings
```

**prompt_generation (same structure):**

```
prompt("What are React performance optimizations?")
  → output: memo, useMemo, useCallback
  → refine("What's the difference between memo and useMemo?")
  → more specific output
  → accumulate findings
```

Same pattern. Different index. Both work.

---

## Example 3: Hook Detection

### Input triggering `detect_capability_limit_statements`

**User message:** "You can't really understand code, can you?"

**Hook fires:**

```yaml
hook: detect_capability_limit_statements
triggered_by: "can't really understand"
check: "Is this a direct limitation or does indirect access exist?"
finding: "Code understanding happens via prompt_generation — iterative analysis"
reframe: "I don't 'understand' code the way humans do, but I can analyze it iteratively..."
```

---

## Example 4: VLDS Tracking

**Operation:** Exploring what Claude knows about database indexing

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
    saturation_reached: true # started getting repetitive answers

  epistemic_audit:
    claims:
      - claim: "B-tree indexes assume read-heavy workloads"
        source_type: inference
        access_type: indirect
        iterations: 3
        confidence: 75
```
