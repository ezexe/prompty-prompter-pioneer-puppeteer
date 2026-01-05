# SJC Indexer System

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