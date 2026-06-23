# [Fragment Title] Fragment

> **Template.** Copy this file to `fragments/NN_NAME.md` inside an instance (e.g.
> `.ai/roboto/fragments/`), fill the bracketed slots, and delete these template
> notes. Worked examples: `.ai/roboto/fragments/00_BASE.md` … `07_BIAS_PATTERNS.md`.

```yaml
fragment:
  name: [snake_case_name] # e.g. base, prompty_identities, response_templates
  layer: [core | prompty | prompter | pioneer | puppeteer]
  type: [identity | seed | refinement | research | automation | skill]
  depends_on: [] # fragment ids REQUIRED for closure, e.g. [00_BASE]
  optional_depends_on: [] # ids that enhance this fragment but aren't required, e.g. [05_VLDS]
  required: false # true only for the root/base fragment (the one all others depend on)
```

---

## What This Is

[1–2 sentences: what this fragment contributes, and which P4 layer it serves.]

---

## [Primary Content Heading]

[The substantive content — tables, definitions, diagrams, YAML schemas, worked
examples. A fragment is a self-contained building block a configuration embeds, so
keep it composable and avoid relying on anything not listed in `depends_on`.]

---

## Dependencies

```
[this fragment]
   ├── depends on: [parent fragment ids — must match the depends_on above]
   └── required by: [child fragments / configurations, if known]
```

---

## Extension Points

```yaml
extensions:
  [extension_point_name]:
    status: open | complete | defined_in_[other_fragment]
    description: "[what a contributor can extend here]"
    contributes_to: [layer.area]
    example: "[concrete example]"
```
