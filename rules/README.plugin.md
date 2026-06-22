# Plugin README

## Purpose

Describe what this plugin helps the agent do and when it should be used.

## Contents

- `.claude-plugin/plugin.json`: Claude Code manifest.
- `.codex-plugin/plugin.json`: Codex manifest.
- `skills/`: Shared workflows.
- `templates/`: Runtime templates packaged with the plugin.
- `.mcp.json`: Optional MCP server configuration.

## Install

Use the marketplace catalog for the target runtime:

- Claude Code: `.claude-plugin/marketplace.json`
- Codex: `.agents/plugins/marketplace.json`

## Validate

Run the repository validation script:

```bash
./scripts/validate.sh plugins/<plugin-name>
```
