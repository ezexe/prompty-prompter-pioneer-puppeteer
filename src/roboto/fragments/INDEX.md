# Fragment Index

```yaml
index:
  name: claude_claudio_roboto
  version: 0.1.0
  fragments: 10
  configurations: 5
  status: documented
```

---

## Fragment Map

### Core Fragments

| File                  | Layer     | Type       | Size | Status      |
| --------------------- | --------- | ---------- | ---- | ----------- |
| `00_BASE.md`          | core      | identity   | ~4K  | ✅ complete |
| `01_PROMPTY.md`       | prompty   | seed       | ~5K  | ✅ complete |
| `02_PROMPTER.md`      | prompter  | refinement | ~6K  | ✅ complete |
| `03_PIONEER.md`       | pioneer   | research   | ~6K  | ✅ complete |
| `04_PUPPETEER.md`     | puppeteer | automation | ~8K  | ✅ complete |
| `05_VLDS.md`          | prompter  | skill      | ~10K | ✅ complete |
| `06_TEMPLATES.md`     | puppeteer | skill      | ~12K | ✅ complete |
| `07_BIAS_PATTERNS.md` | pioneer   | skill      | ~10K | ✅ complete |

### Extension Fragments

Extensions follow the schema and guidelines from CONTRIBUTING.md:

```
/extensions/skills/[name]/
├── EXTENSION.yaml           # required - manifest
├── README.md                # required - documentation
├── EXAMPLES.md              # recommended
├── CHANGELOG.md             # recommended
└── tests/
    ├── phase_hook_tests/    # required
    └── integration_tests/   # recommended
```

| Extension             | Type  | Phases             | Location                                   |
| --------------------- | ----- | ------------------ | ------------------------------------------ |
| isomorphic_operations | skill | pioneer, puppeteer | `extensions/skills/isomorphic_operations/` |
| sjc_indexer           | skill | pioneer            | `extensions/skills/sjc_indexer/`           |

**isomorphic_operations:**

- Domains: capability_reframing, indirect_access, iterative_exploration
- Hooks: detect_capability_limit_statements, suggest_indirect_access_methods, reframe_absolute_limits_in_synthesis

**sjc_indexer:**

- Domains: knowledge_indexing, iterative_exploration, counterfactual_probing
- Hooks: detect_knowledge_exploration_requests, execute_sjc_protocol, index_domain_knowledge

---

## What Each Fragment Contains

### Core Fragments

**00_BASE.md** — Core Identity

- The three identities: Claude, Claudio, Roboto
- Response flow diagram
- Scope definitions (conversation vs request vs synthesis)
- Why the framework works

**01_PROMPTY.md** — Seed Layer

- Raw identity concepts
- What each identity sees and provides
- Scope contrast explanation
- Identity triad principle

**02_PROMPTER.md** — Refinement Layer

- Persona activation templates
- Strengths and risks of each perspective
- Scope contrast analysis patterns
- Decision gate integration

**03_PIONEER.md** — Exploration Layer

- Scope isolation experiment
- Recursive prompt growth experiment
- Assumption detection technique
- Blind spot detection technique
- Context pollution/starvation patterns

**04_PUPPETEER.md** — Orchestration Layer

- Complete lifecycle: RECEIVE → SCAN → BREAK → PLAY → COMPILE → TEST → SYNTHESIZE → POST
- Flow diagram
- When to break and why
- How synthesis works

**05_VLDS.md** — Transparency System

- What VLDS means (Virtual localStorage DataStore sessionStorage)
- Neural network metaphor (weights, biases, activation functions)
- Storage model explanation
- Epistemic system and decision gate
- Full worked example

**06_TEMPLATES.md** — Response Formats

- Minimal, Regular, Full audit templates
- Content format templates (File Change, Code Response, Analysis, Clarification)
- Complete YAML schemas with examples
- Template selection matrix

**07_BIAS_PATTERNS.md** — Detection System

- How bias patterns work
- Pattern schema
- Five registered patterns with full definitions
- Correction table
- Output format

### Extension Fragments

**08_ISOMORPHIC_OPS.md** — Indirect Access Patterns

- Three isomorphic operations (web_search, prompt_generation, artifact_api_calls)
- Structural equivalence explanation
- Capability limit reframing
- When to use each operation

**09_SJC_INDEXER.md** — Knowledge Indexing System

- Structured Junction Counterfactual meta-pattern
- Five components with weight evaluations
- Execution protocol
- Termination conditions
- Full worked example (React)

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
   │      ├── depends: all core above
   │      └── lifecycle execution (8 steps)
   │
   ├── 05_VLDS (transparency skill)
   │      ├── depends: 00_BASE
   │      └── verification, epistemic tracking
   │
   ├── 06_TEMPLATES (response skill)
   │      ├── depends: 00_BASE, 05_VLDS
   │      └── audit + content format templates
   │
   ├── 07_BIAS_PATTERNS (detection skill)
   │      ├── depends: 00_BASE, 02_PROMPTER
   │      └── error prevention
   │
   └── EXTENSIONS (in /extensions/skills/)
          │
          ├── isomorphic_operations/
          │      ├── depends: 00_BASE, 05_VLDS
          │      ├── EXTENSION.yaml
          │      ├── README.md
          │      ├── EXAMPLES.md
          │      ├── CHANGELOG.md
          │      └── tests/
          │             ├── phase_hook_tests/ (3 tests)
          │             └── integration_tests/ (1 test)
          │
          └── sjc_indexer/
                 ├── depends: 00_BASE, 05_VLDS, isomorphic_operations
                 ├── EXTENSION.yaml
                 ├── README.md
                 ├── EXAMPLES.md
                 ├── CHANGELOG.md
                 └── tests/
                        ├── phase_hook_tests/ (3 tests)
                        └── integration_tests/ (1 test)
```

---

## Usage Configurations

Pre-built configurations for different use cases. See `configurations/` directory.

| Configuration | File                | Fragments | Use Case                        |
| ------------- | ------------------- | --------- | ------------------------------- |
| Minimal       | `i-minimal.md`      | 1         | Just the identity triad         |
| Standard      | `i-standard.md`     | 3         | Identity + Templates            |
| Verification  | `i-verification.md` | 4         | Add VLDS epistemic checking     |
| Detection     | `i-detection.md`    | 4         | Add bias pattern detection      |
| Full          | `i-full.md`         | 10        | Everything including extensions |

---

## Extension Points Summary

### Core Extensions

| Fragment         | Extension Point            | Description                                   |
| ---------------- | -------------------------- | --------------------------------------------- |
| 01_PROMPTY       | additional_identities      | New perspectives beyond Claude/Claudio/Roboto |
| 02_PROMPTER      | additional_patterns        | New scope contrast patterns                   |
| 03_PIONEER       | additional_experiments     | New experiments beyond scope isolation        |
| 03_PIONEER       | novel_techniques           | New detection/analysis techniques             |
| 04_PUPPETEER     | additional_lifecycle_steps | New steps in the lifecycle                    |
| 05_VLDS          | storage_persistence        | How to persist VLDS state                     |
| 06_TEMPLATES     | custom_templates           | Domain-specific response formats              |
| 07_BIAS_PATTERNS | additional_patterns        | New bias detection patterns                   |
| 07_BIAS_PATTERNS | correction_actions         | Pattern-specific corrections                  |

### Advanced Extensions

Extensions follow the full Integration Guide from CONTRIBUTING.md:

```yaml
skill_integration:
  phases: [prompter, pioneer]

  skill_types:
    # Core skills
    document_creation:
      skills: [docx, pptx, xlsx, pdf]
      phase_affinity: prompter

    specialized_knowledge:
      skills: [frontend-design, product-self-knowledge]
      phase_affinity: pioneer

    # Extension skills
    meta_exploration:
      skills: [isomorphic_operations, sjc_indexer]
      phase_affinity: pioneer
```

**Extension Points (for future contributions):**

| Extension             | Open Points                | Description                            |
| --------------------- | -------------------------- | -------------------------------------- |
| isomorphic_operations | additional_isomorphic_ops  | New iterate-refine operations          |
| isomorphic_operations | cross_operation_techniques | Techniques across all operations       |
| sjc_indexer           | domain_specific_tiers      | Optimized prompts for specific domains |
| sjc_indexer           | empirical_validation       | Measure actual SJC reliability         |
| sjc_indexer           | automated_execution        | Artifact for running SJC               |

---

## Reading Order

For an AI implementing this framework:

### Basic Implementation

1. **00_BASE.md** — understand the three identities
2. **01_PROMPTY.md** — understand what each identity sees
3. **06_TEMPLATES.md** — understand output structure

### With Verification

4. **05_VLDS.md** — understand verification and transparency

### With Detection

5. **07_BIAS_PATTERNS.md** — understand error prevention

### Full Understanding

6. **02_PROMPTER.md** — understand scope contrast patterns
7. **03_PIONEER.md** — understand experiments and detection
8. **04_PUPPETEER.md** — understand the full lifecycle

### Advanced Capabilities

9. **08_ISOMORPHIC_OPS.md** — understand indirect access
10. **09_SJC_INDEXER.md** — understand knowledge indexing

---

## Building Configurations

Configurations can be built by:

1. **Manual composition** — Copy fragments into single file
2. **AI-driven composition** — Use prompts to generate configurations
3. **Script generation** — Use roadmap scripts (see CONTRIBUTING.md)

### AI-Driven Configuration Building

Use the P4 lifecycle to build configurations:

```yaml
configuration_building:
  prompty:
    action: "Identify need — what fragments does user require?"
    prompt: "What capability do you need? (identity | verification | detection | full)"

  prompter:
    action: "Select fragments — map need to fragment set"
    prompt: "Based on [need], select from: [fragment_list]"

  pioneer:
    action: "Validate selection — check dependencies"
    prompt: "Verify [selection] includes all dependencies from INDEX.md"

  puppeteer:
    action: "Generate configuration — compose fragments"
    prompt: "Combine [fragments] into single configuration file"
```
