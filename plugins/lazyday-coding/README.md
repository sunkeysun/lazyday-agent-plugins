# Lazyday Coding

Lazyday Coding is a Claude Code and Codex compatible plugin for Chinese
repository coding workflows.

## Capabilities

- Technical research and implementation approach design.
- Task breakdown for sequential or multi-agent execution.
- Minimal scoped implementation.
- Bug diagnosis and root-cause analysis.
- Code review.
- Verification planning and evidence reporting.
- Git commit and push handoff.

## Runtime Manifests

- Claude Code: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`

## Skills

- `research-approach`: research approaches, compare implementation options,
  and recommend a bounded plan.
- `break-down-task`: split a confirmed approach into executable, verifiable
  tasks.
- `implement-change`: implement a confirmed repository change with minimal,
  evidence-backed edits.
- `diagnose-problem`: analyze bugs, logs, test failures, and regressions.
- `review-code`: review diffs, files, patches, or branches for correctness and
  regression risk.
- `verify-change`: validate current changes with tests, builds, static checks,
  or manual evidence.
- `commit-changes`: prepare commits and push only when explicitly requested.

## MCP Servers

This plugin does not bundle MCP servers yet. The placeholder `.mcp.json` is not
referenced by either runtime manifest.
