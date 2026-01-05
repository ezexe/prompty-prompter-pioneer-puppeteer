# Pioneer Layer Fragment

```yaml
fragment:
  name: pioneer_exploration
  layer: pioneer
  type: research
  version: 0.1.0
```

## Scope Isolation Experiment

```yaml
pioneer:
  type: research
  artifacts:
    experiments:
      scope_isolation:
        hypothesis: "Per-request isolation catches accumulated blind spots"
        mechanism: |
          Claude accumulates: good for continuity, risky for assumptions
          Claudio resets: loses continuity, gains fresh eyes
          Comparison reveals assumption creep
        
      recursive_growth:
        hypothesis: "Each response grows the effective prompt"
        mechanism: |
          Turn N: Claude sees [system + all_turns + request]
          Turn N: Claudio sees [system + THIS_REQUEST_ONLY]
          Delta grows with conversation length
```

## Detection Techniques

```yaml
techniques:
  assumption_detection:
    method: |
      1. Get Claude response (with context)
      2. Get Claudio response (without)
      3. Diff
      4. Anything not derivable from current request = assumption
    output: assumption_list
    
  blind_spot_detection:
    method: # TBD via contributions
    output: # TBD via contributions
```

## Extension Points

```yaml
extensions:
  blind_spot_method:
    status: open
    contributes_to: pioneer.techniques.blind_spot_detection
    
  additional_experiments:
    status: open
    contributes_to: pioneer.artifacts.experiments
    
  novel_techniques:
    status: open
    contributes_to: pioneer.techniques
```
