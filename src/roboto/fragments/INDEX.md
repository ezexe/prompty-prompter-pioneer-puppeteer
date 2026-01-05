# Fragment Index

```yaml
index:
  name: claude_claudio_roboto
  version: 0.1.0
  fragments: 8
  status: documented # all fragments now have full definitions
```

---

## Fragment Map

| File                  | Layer     | Type       | Size | Status      |
| --------------------- | --------- | ---------- | ---- | ----------- |
| `00_BASE.md`          | core      | identity   | ~3K  | ✅ complete |
| `01_PROMPTY.md`       | prompty   | seed       | ~3K  | ✅ complete |
| `02_PROMPTER.md`      | prompter  | refinement | ~4K  | ✅ complete |
| `03_PIONEER.md`       | pioneer   | research   | ~4K  | ✅ complete |
| `04_PUPPETEER.md`     | puppeteer | automation | ~4K  | ✅ complete |
| `05_VLDS.md`          | prompter  | skill      | ~7K  | ✅ complete |
| `06_TEMPLATES.md`     | puppeteer | skill      | ~6K  | ✅ complete |
| `07_BIAS_PATTERNS.md` | pioneer   | skill      | ~5K  | ✅ complete |

---

## What Each Fragment Contains

### 00_BASE.md — Core Identity

- The three identities: Claude, Claudio, Roboto
- Response flow diagram
- Scope definitions (conversation vs request vs synthesis)
- Why the framework works

### 01_PROMPTY.md — Seed Layer

- Raw identity concepts
- What each identity sees and provides
- Scope contrast explanation
- Identity triad principle

### 02_PROMPTER.md — Refinement Layer

- Persona activation templates
- Strengths and risks of each perspective
- Scope contrast analysis patterns
- Decision gate integration

### 03_PIONEER.md — Exploration Layer

- Scope isolation experiment
- Recursive prompt growth experiment
- Assumption detection technique
- Blind spot detection technique
- Context pollution/starvation patterns

### 04_PUPPETEER.md — Orchestration Layer

- Complete lifecycle: RECEIVE → SCAN → BREAK → PLAY → COMPILE → SYNTHESIZE → POST
- Flow diagram
- When to break and why
- How synthesis works

### 05_VLDS.md — Transparency System

- What VLDS means (Virtual localStorage DataStore sessionStorage)
- Neural network metaphor (weights, biases, activation functions)
- Storage model explanation
- Epistemic system and decision gate
- Full worked example

### 06_TEMPLATES.md — Response Formats

- Minimal, Regular, Full template definitions
- Complete YAML schemas
- Worked examples for each level
- Template selection matrix

### 07_BIAS_PATTERNS.md — Detection System

- How bias patterns work
- Pattern schema
- Five registered patterns with full definitions
- Correction table
- Output format

---

## Dependency Graph

```
00_BASE (core identity)
   │
   ├── 01_PROMPTY (seed layer)
   │      └── raw identity concepts
   │
   ├── 02_PROMPTER (refinement layer)
   │      ├── depends: 01_PROMPTY
   │      └── persona templates, scope analysis
   │
   ├── 03_PIONEER (exploration layer)
   │      ├── depends: 01_PROMPTY, 02_PROMPTER
   │      └── experiments, detection techniques
   │
   ├── 04_PUPPETEER (orchestration layer)
   │      ├── depends: all above
   │      └── lifecycle execution
   │
   ├── 05_VLDS (transparency skill)
   │      ├── depends: 00_BASE
   │      └── verification, epistemic tracking
   │
   ├── 06_TEMPLATES (response skill)
   │      ├── depends: 00_BASE, 05_VLDS
   │      └── output formatting
   │
   └── 07_BIAS_PATTERNS (detection skill)
          ├── depends: 00_BASE, 02_PROMPTER
          └── error prevention
```

---

## Usage Configurations

### Minimal — Just the identity triad

```yaml
load:
  - 00_BASE.md

provides:
  - Claude/Claudio/Roboto identities
  - Response flow
  - Basic scope contrast
```

### Standard — Identity + Templates

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 06_TEMPLATES.md

provides:
  - Full identity definitions
  - Response templates (minimal/regular/full)
```

### With Verification — Add VLDS

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 05_VLDS.md
  - 06_TEMPLATES.md

provides:
  - Epistemic verification
  - Decision gate
  - Transparent auditing
```

### With Detection — Add Bias Patterns

```yaml
load:
  - 00_BASE.md
  - 01_PROMPTY.md
  - 03_PIONEER.md
  - 07_BIAS_PATTERNS.md

provides:
  - Assumption detection
  - Blind spot detection
  - Pre-response error catching
```

### Full — Everything

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

provides:
  - Complete P4 lifecycle
  - Full epistemic transparency
  - All detection patterns
  - All response templates
```

---

## Extension Points Summary

| Fragment         | Open Extensions                          |
| ---------------- | ---------------------------------------- |
| 01_PROMPTY       | additional_identities                    |
| 02_PROMPTER      | additional_patterns                      |
| 03_PIONEER       | additional_experiments, novel_techniques |
| 04_PUPPETEER     | additional_lifecycle_steps               |
| 05_VLDS          | storage_persistence                      |
| 06_TEMPLATES     | custom_templates                         |
| 07_BIAS_PATTERNS | additional_patterns, correction_actions  |

---

## Reading Order

For an AI implementing this framework:

1. **Start with 00_BASE.md** — understand the three identities
2. **Read 01_PROMPTY.md** — understand what each identity sees
3. **Read 05_VLDS.md** — understand verification and transparency
4. **Read 06_TEMPLATES.md** — understand output structure
5. **Read 07_BIAS_PATTERNS.md** — understand error prevention
6. **Read 02_PROMPTER.md** — understand scope contrast patterns
7. **Read 03_PIONEER.md** — understand experiments and detection
8. **Read 04_PUPPETEER.md** — understand the full lifecycle
