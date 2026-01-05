# Fragment Index

```yaml
index:
  name: claude_claudio_roboto
  version: 0.1.0
  fragments: 8
```

## Fragment Map

| File                  | Layer     | Type       | Status   |
| --------------------- | --------- | ---------- | -------- |
| `00_BASE.md`          | —         | core       | complete |
| `01_PROMPTY.md`       | prompty   | seed       | partial  |
| `02_PROMPTER.md`      | prompter  | refinement | partial  |
| `03_PIONEER.md`       | pioneer   | research   | partial  |
| `04_PUPPETEER.md`     | puppeteer | automation | partial  |
| `05_VLDS.md`          | prompter  | skill      | partial  |
| `06_TEMPLATES.md`     | puppeteer | skill      | partial  |
| `07_BIAS_PATTERNS.md` | pioneer   | skill      | partial  |

## Dependency Graph

```
00_BASE
   ├── 01_PROMPTY (identities)
   │      └── defines: Claude, Claudio, Roboto
   │
   ├── 02_PROMPTER (personas, scope analysis)
   │      ├── depends: 01_PROMPTY
   │      └── integrates: 05_VLDS
   │
   ├── 03_PIONEER (experiments, techniques)
   │      ├── depends: 01_PROMPTY, 02_PROMPTER
   │      └── integrates: 07_BIAS_PATTERNS
   │
   └── 04_PUPPETEER (lifecycle, orchestration)
          ├── depends: all above
          └── integrates: 06_TEMPLATES
```

## Open Extension Points

```yaml
extensions:
  prompty:
    - roboto_memory
    - roboto_characteristics
    - additional_identities

  prompter:
    - roboto_activation
    - contradiction_resolution
    - additional_patterns

  pioneer:
    - blind_spot_method
    - additional_experiments
    - novel_techniques

  puppeteer:
    - synthesize_action
    - post_template
    - additional_lifecycle_steps

  vlds:
    - epistemic_system
    - layers

  templates:
    - full_template
    - custom_templates

  bias_patterns:
    - additional_patterns
    - correction_actions
```

## Usage

### Minimal (just base)

```yaml
load:
  - 00_BASE.md
```

### Standard (identity + templates)

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 06_TEMPLATES.md
```

### Full (all fragments)

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 02_PROMPTER.md
  - 03_PIONEER.md
  - 04_PUPPETEER.md
  - 05_VLDS.md
  - 06_TEMPLATES.md
  - 07_BIAS_PATTERNS.md
```

### Custom (pick what you need)

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 07_BIAS_PATTERNS.md # just want detection
```
