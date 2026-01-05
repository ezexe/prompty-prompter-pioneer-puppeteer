# SJC Indexer Examples

## Example 1: Indexing React Knowledge

### Phase 1: Anchor Selection

**Prompt:** "List the 5 core mechanisms of React"

**Output:**
```yaml
mechanism_list:
  - Virtual DOM diffing
  - Component lifecycle
  - State management
  - Hooks system
  - Reconciliation algorithm
```

### Phase 2: Seam Finding

**Prompt:** "What does Virtual DOM diffing assume that might not be true?"

**Output:**
```yaml
assumption_list:
  - mechanism: Virtual DOM diffing
    assumes:
      - "Component renders are pure (deterministic)"
      - "Key props are stable identifiers"
      - "Tree structure changes are local"
```

### Phase 3: Junction Exploration

**Prompt:** "How does Virtual DOM diffing interact with Hooks system?"

**Output:**
```yaml
dependency_graph:
  - from: diffing
    to: hooks
    type: ordering_dependency
    description: "Hooks order must be stable for diffing to match state"
```

### Phase 4: Boundary Mapping

**Prompt:** "What's the failure mode of the diffing→hooks dependency under concurrent mode?"

**Output:**
```yaml
failure_modes:
  - dependency: diffing→hooks
    stress_condition: concurrent_mode
    failure: "Hooks may run out of expected order if renders are interrupted"
    
boundaries:
  - mechanism: hooks
    unknown_beyond: "concurrent mode edge cases"
```

### Phase 5: Synthesis

**Output:**
```yaml
indexed_model:
  domain: "React"
  mechanisms: [diffing, lifecycle, state, hooks, reconciliation]
  dependencies:
    - from: diffing
      to: hooks
      type: ordering_dependency
      strength: 0.9
  assumptions:
    - mechanism: diffing
      assumes: "render purity"
      about: components
      failure_condition: "side effects during render"
  boundaries:
    - mechanism: hooks
      unknown_beyond: "concurrent mode edge cases"
  metadata:
    iterations_run: 23
    aggregate_confidence: 0.78
    termination_reason: "boundary_mapper saturation"
```

---

## Example 2: Detecting Exploration Request

### Input

**User:** "Can you do a deep dive into what you know about database indexing?"

### Hook: detect_knowledge_exploration_requests

```yaml
detection:
  triggered: true
  trigger_phrases_matched:
    - "deep dive"
    - "what you know about"
  domain_detected: "database indexing"
  recommendation: "Apply SJC protocol"
  suggested_tier: 3  # counterfactual probing
```

### SJC Execution

```yaml
sjc_execution:
  domain: "database indexing"
  
  phase_1_output:
    mechanisms:
      - B-tree indexes
      - Hash indexes
      - Bitmap indexes
      - Full-text indexes
      - Covering indexes
      
  phase_2_output:
    assumptions:
      - mechanism: "B-tree indexes"
        assumes: "Data accessed in range patterns"
      - mechanism: "Hash indexes"
        assumes: "Exact match lookups only"
        
  phase_3_output:
    dependencies:
      - from: "B-tree"
        to: "query planner"
        type: "statistics dependency"
        
  phase_4_output:
    boundaries:
      - mechanism: "B-tree"
        unknown_beyond: "write-heavy workloads with random inserts"
        
  termination:
    reason: "failure_modes repeating"
    iterations: 31
```

---

## Example 3: Tier Comparison

Same domain, different tiers:

### Tier 1 (Anchor)

**Prompt:** "List the core mechanisms of authentication"

**Output:** [passwords, tokens, sessions, OAuth, certificates]

**Reliability:** 0.70 — good starting point, surface level

### Tier 2 (Junction)

**Prompt:** "How does token-based auth depend on session management?"

**Output:** "Tokens can replace sessions for stateless auth, but refresh tokens reintroduce session-like state..."

**Reliability:** 0.80 — deeper insight, reveals relationship

### Tier 3 (Counterfactual)

**Prompt:** "What would JWT authentication assume about token storage that fails under XSS attacks?"

**Output:** "JWT assumes client-side storage is secure. Under XSS, localStorage-stored tokens are exfiltrated. HttpOnly cookies mitigate but introduce CSRF surface..."

**Reliability:** 0.88 — highest insight, reveals assumptions and failure modes