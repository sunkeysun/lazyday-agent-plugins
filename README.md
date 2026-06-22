# Lazyday Agent Plugins

This repository hosts Lazyday plugins that are intended to work with both
Claude Code and Codex.

## Layout

- `.claude-plugin/marketplace.json`: Claude Code marketplace catalog.
- `.agents/plugins/marketplace.json`: Codex marketplace catalog.
- `plugins/<plugin-name>/.claude-plugin/plugin.json`: Claude Code plugin manifest.
- `plugins/<plugin-name>/.codex-plugin/plugin.json`: Codex plugin manifest.
- `plugins/<plugin-name>/skills/`: Shared agent skills.
- `templates/`: Repository-level templates for bootstrapping target projects.
- `plugins/<plugin-name>/templates/`: Runtime templates packaged with the plugin.

## First Plugin

`lazyday-coding` packages reusable coding workflows for implementation,
debugging, review, and verification.

## Validation

```bash
./scripts/validate.sh
```

The script validates the Codex plugin manifest with the local Codex plugin
validator. If the `claude` command is installed, it also runs Claude Code
plugin validation.
