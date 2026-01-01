# 🤝 Contributing

## Adding Extensions

1. **Identify the extension type** (tool, skill, connector)
2. **Determine phase affinity** (which P4 phases benefit)
3. **Create extension manifest** following the schema
4. **Implement hooks** for relevant phases
5. **Document capabilities** in extension README
6. **Submit for integration**

## Extension Guidelines

```yaml
guidelines:
  naming:
    pattern: lowercase_with_underscores
    prefix_by_type: false # Let type field distinguish

  versioning:
    scheme: semver
    breaking_changes: major_bump_required

  documentation:
    required: [README.md, EXTENSION.yaml]
    recommended: [EXAMPLES.md, CHANGELOG.md]

  testing:
    required: phase_hook_tests
    recommended: integration_tests
```

## Roadmap Contributions

Priority areas for extension development:

| Area                      | Type      | Priority | Description                       |
| ------------------------- | --------- | -------- | --------------------------------- |
| Multi-model orchestration | Connector | High     | Cross-LLM prompt routing          |
| Prompt versioning         | Tool      | High     | Git-like prompt history           |
| A/B testing framework     | Tool      | Medium   | Comparative prompt evaluation     |
| Visual prompt builder     | Skill     | Medium   | Graphical P4 lifecycle management |
| Telemetry connector       | Connector | Medium   | Prompt performance analytics      |
