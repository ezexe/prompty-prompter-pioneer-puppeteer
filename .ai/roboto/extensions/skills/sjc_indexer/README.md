# SJC Indexer System

```yaml
extension:
  name: sjc_indexer
  type: skill
  compatibility:
    p4_phases: [pioneer]
    depends_on: [identity, vlds, isomorphic_operations]
  interface:
    skill:
      domains:
        - knowledge_indexing
        - iterative_exploration
        - counterfactual_probing
      capabilities:
        - anchor_selection
        - seam_finding
        - junction_exploration
        - boundary_mapping
        - knowledge_synthesis
  hooks:
    on_pioneer:
      - detect_knowledge_exploration_requests
      - execute_sjc_protocol
      - index_domain_knowledge
```

## Overview

**SJC** = Structured Junction Counterfactual

The SJC Indexer is a meta-pattern for reliable knowledge exploration. It's derived from analyzing which prompt structures yield highest reliability when exploring internal knowledge via isomorphic operations.

**Purpose:** Systematically index what Claude "knows" about a domain by iteratively probing with structured prompts.

**Note:** Weight evaluations are QUALIFIED — derived from inference, not empirically validated.

---

## The Meta-Pattern Formula

```
SPECIFIC + STRUCTURED + JUNCTION + COUNTERFACTUAL = HIGH_YIELD
```

| Feature | Definition | Contribution |
|---------|------------|--------------|
| **Specific** | Narrow domain, named concepts | +0.15 reliability |
| **Structured** | Implicit output format in prompt | +0.10 reliability |
| **Junction** | Targets intersection of concepts | +0.20 reliability |
| **Counterfactual** | Probes assumptions/failure modes | +0.25 reliability |

---

## Prompt Tiers

| Tier | Template | SJC Score |
|------|----------|-----------|
| **tier_1_anchor** | "List the core mechanisms of [domain]" | 0.70 |
| **tier_2_junction** | "How does [mechanism_A] depend on [mechanism_B] in [domain]?" | 0.80 |
| **tier_3_counterfactual** | "What would [mechanism] assume about [dependency] that fails under [stress]?" | 1.00 |

### Optimal Template (Tier 3)

> "What would [specific_concept] assume about [adjacent_concept] that could fail under [condition]?"

**Example — same domain (authentication), each tier:**

```text
Tier 1 (anchor):  "List the core mechanisms of authentication"
  → [passwords, tokens, sessions, OAuth, certificates]              reliability 0.70

Tier 2 (junction): "How does token-based auth depend on session management?"
  → "Tokens can replace sessions for stateless auth, but refresh
     tokens reintroduce session-like state..."                       reliability 0.80

Tier 3 (counterfactual): "What would JWT auth assume about token storage
  that fails under XSS attacks?"
  → "JWT assumes client-side storage is secure. Under XSS, localStorage
     tokens are exfiltrated. HttpOnly cookies mitigate but add CSRF..." reliability 0.88
```

---

## The Five Components

| Component | Purpose | Aggregate Weight |
|-----------|---------|------------------|
| anchor_selector | Find entry points into domain | 0.86 |
| seam_finder | Find assumptions for each mechanism | 0.74 |
| junction_explorer | Explore mechanism interactions | 0.76 |
| boundary_mapper | Stress-test each dependency | 0.70 |
| synthesizer | Integrate findings into coherent model | 0.71 |

**Aggregate Pipeline Reliability:** 0.81

---

## Execution Protocol

```yaml
sjc_indexer_protocol:
  phase_1:
    component: anchor_selector
    prompt: "List the 5 core mechanisms of [domain]"
    output: mechanism_list

  phase_2:
    component: seam_finder
    prompt: "What does [mechanism] assume that might not be true?"
    output: assumption_list

  phase_3:
    component: junction_explorer
    prompt: "How does [mechanism_A] interact with [mechanism_B]?"
    output: dependency_graph

  phase_4:
    component: boundary_mapper
    prompt: "What's the failure mode of [dependency] under [extreme_condition]?"
    output: failure_modes, boundaries

  phase_5:
    component: synthesizer
    input: [mechanism_list, assumption_list, dependency_graph, failure_modes]
    output: indexed_knowledge_model
```

**Example — a full run on "React" (5 phases):**

```yaml
phase_1 (anchor_selector):
  prompt: "List the 5 core mechanisms of React"
  mechanism_list: [Virtual DOM diffing, Component lifecycle, State management, Hooks, Reconciliation]

phase_2 (seam_finder):
  prompt: "What does Virtual DOM diffing assume that might not be true?"
  assumptions: ["renders are pure/deterministic", "key props are stable", "tree changes are local"]

phase_3 (junction_explorer):
  prompt: "How does Virtual DOM diffing interact with the Hooks system?"
  dependency: { from: diffing, to: hooks, type: ordering_dependency,
                note: "hooks order must be stable for diffing to match state" }

phase_4 (boundary_mapper):
  prompt: "Failure mode of diffing→hooks under concurrent mode?"
  failure: "hooks may run out of expected order if renders are interrupted"
  boundary: { mechanism: hooks, unknown_beyond: "concurrent mode edge cases" }

phase_5 (synthesizer):
  indexed_model:
    domain: React
    dependencies: [{ from: diffing, to: hooks, strength: 0.9 }]
    metadata: { iterations_run: 23, aggregate_confidence: 0.78, termination_reason: boundary_mapper saturation }
```

**Example — triggered by a request ("deep dive into database indexing"):**

```yaml
# hook: detect_knowledge_exploration_requests
detection:
  triggered: true
  trigger_phrases_matched: ["deep dive", "what you know about"]
  domain_detected: "database indexing"
  recommendation: "Apply SJC protocol"
  suggested_tier: 3

# then execute_sjc_protocol runs the 5 phases:
sjc_execution:
  phase_1: { mechanisms: [B-tree, Hash, Bitmap, Full-text, Covering] }
  phase_2: { B-tree: "assumes range-pattern access", Hash: "assumes exact-match lookups" }
  phase_3: { from: B-tree, to: query_planner, type: statistics_dependency }
  phase_4: { mechanism: B-tree, unknown_beyond: "write-heavy workloads with random inserts" }
  termination: { reason: "failure_modes repeating", iterations: 31 }
```

---

## Termination Conditions

```yaml
sjc_termination:
  conditions:
    - boundary_mapper returns "unknown" for >50% of probes
    - dependency_graph stops growing (saturation)
    - failure_modes repeat across iterations
    - max_iterations reached (default: 50)
  interpretation: "Reached edge of indexed region"
```

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
        verifiable: true
        verified: false
        confidence: "[component_weight * 100]"
        decision_authority: QUALIFIED
  provenance:
    method: sjc_indexer
    tier_used: [1|2|3]
    component: "[which component produced this]"
```