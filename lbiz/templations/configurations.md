# Configurations

> **Template.** One file per instance.
> Each `##` section is one tier: a fenced YAML config block plus that tier's detail.
> Repeat the `## [Tier Name]` block per tier (e.g. minimal → full).

---

## [Tier Name]

```yaml
name: [tier_name]
fragments: [] # fragment ids this tier bundles — must be dependency-closed
extensions: [] # extension ids, if any (omit the key if none)
use_case: "[one-line use case]"
```

### What This Provides

[Capabilities, derived from the bundled fragments.]

### What This Does NOT Provide

[Capabilities from fragments NOT bundled — so a reader knows the ceiling.]

### When To Use

[Guidance on when this tier fits.]

### Response Format

[The output format appropriate for the bundled fragments — from plain prose up to a full audit, depending on what this tier includes.]

> **Persona overlay:** if the instance defines a voice/response contract (e.g. in its `identity` skill), it wraps this tier.

### Upgrade / Downgrade Path

| Need  | Add / Remove Fragment | See Tier              |
| ----- | --------------------- | --------------------- |
| [...] | [...]                 | [`[Other]`](#[other]) |
