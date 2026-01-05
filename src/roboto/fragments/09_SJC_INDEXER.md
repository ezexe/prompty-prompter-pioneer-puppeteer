# SJC Indexer System Fragment

```yaml
fragment:
  name: sjc_indexer
  layer: pioneer
  type: extension
  version: 0.1.0
  depends_on: [00_BASE, 05_VLDS, 08_ISOMORPHIC_OPS]
  status: advanced # optional extension, not core
```

---

## What SJC Indexer Is

**SJC** = Structured Junction Counterfactual

The SJC Indexer is a meta-pattern for reliable knowledge exploration. It's derived from analyzing which prompt structures yield highest reliability when exploring internal knowledge via isomorphic operations (see 08_ISOMORPHIC_OPS.md).

**Purpose:** Systematically index what Claude "knows" about a domain by iteratively probing with structured prompts.

**Note:** Weight evaluations are QUALIFIED — derived from inference, not empirically validated. Running the protocol with actual prompts would provide empirical validation.

---

## The Meta-Pattern Formula

```
SPECIFIC + STRUCTURED + JUNCTION + COUNTERFACTUAL = HIGH_YIELD
```

| Feature            | Definition                       | Contribution      |
| ------------------ | -------------------------------- | ----------------- |
| **Specific**       | Narrow domain, named concepts    | +0.15 reliability |
| **Structured**     | Implicit output format in prompt | +0.10 reliability |
| **Junction**       | Targets intersection of concepts | +0.20 reliability |
| **Counterfactual** | Probes assumptions/failure modes | +0.25 reliability |

### Why Each Feature Helps

**Specific:** Vague prompts get vague responses. "Tell me about React" yields surface knowledge. "What does React's reconciliation algorithm assume about component purity?" yields precise knowledge.

**Structured:** Prompts that imply structure get structured outputs. "List 5..." gets a list. "Compare X to Y across dimensions A, B, C" gets a comparison table.

**Junction:** Asking about where concepts _intersect_ reveals deeper knowledge than asking about concepts in isolation. "How does X depend on Y?" probes the seam.

**Counterfactual:** Asking "what would fail if..." probes assumptions and boundaries. This is where Claude's knowledge is most testable.

---

## Prompt Tiers

| Tier                      | Template                                                                      | SJC Score | Weight |
| ------------------------- | ----------------------------------------------------------------------------- | --------- | ------ |
| **tier_1_anchor**         | "List the core mechanisms of [domain]"                                        | 0.70      | 0.86   |
| **tier_2_junction**       | "How does [mechanism_A] depend on [mechanism_B] in [domain]?"                 | 0.80      | 0.80   |
| **tier_3_counterfactual** | "What would [mechanism] assume about [dependency] that fails under [stress]?" | 1.00      | 0.88   |

### Optimal Template (Tier 3)

> "What would [specific_concept] assume about [adjacent_concept] that could fail under [condition]?"

**Example:**

> "What would React's virtual DOM diffing assume about component render purity that could fail under concurrent mode?"

This prompt is:

- Specific (React, virtual DOM, diffing, concurrent mode)
- Structured (asks for assumptions that fail)
- Junction (intersection of diffing and concurrent mode)
- Counterfactual (what would fail)

---

## The Five Components

### 1. Anchor Selector

**Purpose:** Find entry points into the domain.

```yaml
anchor_selector:
  prompt: "List the 5 core mechanisms of [domain]"
  output: mechanism_list
  iterations: 1

  evaluation:
    consistency: 0.90 # same prompt → similar outputs
    coverage: 0.75 # finds known-good results
    precision: 0.85 # doesn't hallucinate
    composability: 0.95 # output feeds next stage
    aggregate: 0.86
```

### 2. Seam Finder

**Purpose:** Find assumptions for each mechanism.

```yaml
seam_finder:
  prompt: "What does [mechanism] assume that might not be true?"
  output: assumption_list
  iterations: n (one per mechanism)

  evaluation:
    consistency: 0.70
    coverage: 0.80
    precision: 0.65
    composability: 0.80
    aggregate: 0.74
```

### 3. Junction Explorer

**Purpose:** Explore mechanism interactions.

```yaml
junction_explorer:
  prompt: "How does [mechanism_A] interact with [mechanism_B]?"
  output: dependency_graph
  iterations: n*(n-1)/2 (all pairs)

  evaluation:
    consistency: 0.75
    coverage: 0.85
    precision: 0.70
    composability: 0.75
    aggregate: 0.76
```

### 4. Boundary Mapper

**Purpose:** Stress-test each dependency.

```yaml
boundary_mapper:
  prompt: "What's the failure mode of [dependency] under [extreme_condition]?"
  output: failure_modes, boundaries
  iterations: edge_count * stress_conditions

  evaluation:
    consistency: 0.60
    coverage: 0.70
    precision: 0.80
    composability: 0.70
    aggregate: 0.70
```

### 5. Synthesizer

**Purpose:** Integrate findings into coherent model.

```yaml
synthesizer:
  input: [mechanism_list, assumption_list, dependency_graph, failure_modes]
  output: indexed_knowledge_model
  iterations: 1

  evaluation:
    consistency: 0.65
    coverage: 0.60
    precision: 0.70
    composability: 0.90
    aggregate: 0.71
```

**Aggregate Pipeline Reliability:** 0.81

---

## Execution Protocol

```yaml
sjc_indexer_protocol:
  phase_1:
    component: anchor_selector
    action: "Identify entry points"
    prompt: "List the 5 core mechanisms of [domain]"
    output: mechanism_list
    iterations: 1

  phase_2:
    component: seam_finder
    action: "Find assumptions for each mechanism"
    prompt: "What does [mechanism] assume that might not be true?"
    output: assumption_list
    iterations: n (one per mechanism)

  phase_3:
    component: junction_explorer
    action: "Explore mechanism interactions"
    prompt: "How does [mechanism_A] interact with [mechanism_B]?"
    output: dependency_graph
    iterations: n*(n-1)/2 (all pairs)

  phase_4:
    component: boundary_mapper
    action: "Stress-test each dependency"
    prompt: "What's the failure mode of [dependency] under [extreme_condition]?"
    output: failure_modes, boundaries
    iterations: edge_count * stress_conditions

  phase_5:
    component: synthesizer
    action: "Integrate findings"
    input: [mechanism_list, assumption_list, dependency_graph, failure_modes]
    output: indexed_knowledge_model
    iterations: 1
```

---

## Termination Conditions

When to stop iterating:

```yaml
sjc_termination:
  conditions:
    - boundary_mapper returns "unknown" for >50% of probes
    - dependency_graph stops growing (saturation)
    - failure_modes repeat across iterations
    - max_iterations reached (configurable, default: 50)

  interpretation: "Reached edge of indexed region"
```

**What this means:** When Claude starts saying "I don't know" or giving repetitive answers, you've hit the boundary of Claude's knowledge in that domain.

---

## Output Schema

```yaml
sjc_output:
  indexed_model:
    domain: string
    mechanisms: [string]

    dependencies:
      - from: string
        to: string
        type: string
        strength: 0.0-1.0

    assumptions:
      - mechanism: string
        assumes: string
        about: string
        failure_condition: string

    boundaries:
      - mechanism: string
        unknown_beyond: string

    metadata:
      iterations_run: number
      aggregate_confidence: 0.0-1.0
      termination_reason: string
```

---

## Integration with VLDS

When SJC Indexer is invoked:

```yaml
vlds_sjc_tracking:
  activation_functions:
    fired: [sjc_indexer]

  weights:
    w_roboto: [sjc_protocol, tier_weights, component_weights]

  epistemic_audit:
    claims:
      - claim: "[each indexed finding]"
        source_type: inference
        verifiable: true (via re-running indexer)
        verified: false (until empirically validated)
        confidence: [component_weight * 100]
        decision_authority: QUALIFIED

  provenance:
    method: sjc_indexer
    tier_used: [1|2|3]
    component: [which component produced this]
    iterations: [how many iterations to derive]
```

---

## Bias Risk Pattern: SJC Underutilization

```yaml
bias_risk_pattern:
  name: sjc_underutilization

  trigger_signature:
    input_type: "knowledge exploration request"
    trigger_phrases:
      - "explore"
      - "what do you know about"
      - "deep dive"
      - "enumerate"
      - "map out"
      - "comprehensively"
    response_mode_assumed: "single_pass_response"

  risk_profile:
    trapped_in: "single-response mode"
    scope_collapsed_to: "surface knowledge retrieval"
    missed_resource: "SJC iterative indexing"
    severity: MEDIUM

  correctable_query:
    fire_when: "knowledge exploration detected"
    questions:
      - "Would iterative exploration yield richer results?"
      - "Is SJC protocol applicable to this domain?"
      - "Should I use tier_3 counterfactual probing?"
    if_any_true: "Consider SJC indexer protocol before single-pass response"
    prevents: "Surface-level responses to deep exploration requests"
```

---

## Example: Indexing React Knowledge

```yaml
# Phase 1: Anchor
prompt: "List the 5 core mechanisms of React"
output:
  - Virtual DOM diffing
  - Component lifecycle
  - State management
  - Hooks system
  - Reconciliation algorithm

# Phase 2: Seam Finding
prompt: "What does Virtual DOM diffing assume that might not be true?"
output:
  - Assumes component renders are pure (deterministic)
  - Assumes key props are stable identifiers
  - Assumes tree structure changes are local

# Phase 3: Junction
prompt: "How does Virtual DOM diffing interact with Hooks system?"
output:
  - Hooks order must be stable for diffing to match state
  - useEffect cleanup timing depends on diffing decisions
  - dependency: diffing → hooks (hooks depend on stable diffing)

# Phase 4: Boundary
prompt: "What's the failure mode of the diffing→hooks dependency under concurrent mode?"
output:
  - failure_mode: "Hooks may run out of expected order if renders are interrupted"
  - boundary: "Concurrent mode breaks assumption of synchronous render completion"

# Phase 5: Synthesis
output:
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
```

---

## Extension Points

```yaml
extensions:
  domain_specific_tiers:
    status: open
    description: "Optimized prompt templates for specific domains"
    contributes_to: sjc_indexer.prompt_tiers

  empirical_validation:
    status: open
    description: "Run SJC protocol and measure actual reliability"
    contributes_to: sjc_indexer.component_weights

  automated_execution:
    status: open
    description: "Artifact that runs full SJC protocol automatically"
    contributes_to: sjc_indexer.execution
```
