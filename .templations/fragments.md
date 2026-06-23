# Fragments

> **Template.** The four P4 layers of an instance, one `#` section each.
> Copy this file to `<instance>/fragments.md` and fill each layer's body.
> Capabilities that aren't one of the four layers (identity, transparency, formatting, detection, …) live as **skills** under `extensions/skills/`, not here.
> Worked example: `.ai/roboto/fragments.md`.

The P4 layers and their roles:

| Layer     | Role        | Question it answers          |
| --------- | ----------- | ---------------------------- |
| Prompty   | ideation    | what are we building?        |
| Prompter  | engineering | how do we structure it?      |
| Pioneer   | research    | what experiments can we run? |
| Puppeteer | automation  | how do we orchestrate it?    |

**Dependency rule:** each layer's `depends_on` typically chains to the prior layers plus the `identity` skill.
A configuration must include the transitive closure of its members' `depends_on`; `optional_depends_on` enhances but isn't required.

---

# Prompty

```yaml
layer: prompty
depends_on: [identity]
```

[The seed / ideation layer — the raw concepts the instance starts from.]

---

# Prompter

```yaml
layer: prompter
depends_on: [identity, prompty]
```

[The engineering / refinement layer — structured templates and validated patterns.]

---

# Pioneer

```yaml
layer: pioneer
depends_on: [identity, prompty, prompter]
```

[The research layer — experiments and detection techniques.]

---

# Puppeteer

```yaml
layer: puppeteer
depends_on: [identity, prompty, prompter, pioneer]
```

[The automation / orchestration layer — the lifecycle that ties everything together.]
