# Lazyday Coding

Lazyday Coding is a Claude Code and Codex compatible plugin for Chinese
repository coding workflows.

## Capabilities

- Entry routing for choosing the right coding skill without forcing a fixed
  workflow.
- Task clarification, requirement contract creation, and continuation from
  saved requirement artifacts.
- Requirement artifact lifecycle management under `.lazyday/coding/requirements/`,
  where `coding` is the plugin artifact namespace.
- Context recovery and requirement matching from saved artifacts.
- Repository exploration, call-chain mapping, reusable pattern discovery, and
  validation command discovery.
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

- `route-coding-task`: choose the right Lazyday Coding skill, decide whether to
  recover context or use artifacts, and support direct single-skill execution.
- `clarify-task`: clarify vague requests, define task contracts, choose or
  create saved requirement artifacts.
- `manage-artifacts`: create, select, switch, inspect, repair, and summarize
  `.lazyday/coding/requirements/` artifacts.
- `resume-context`: read saved artifacts, rank candidate requirements, and
  recommend the next skill for continuation.
- `explore-repo`: explore repository structure, rules, entry points,
  call chains, reusable patterns, and validation commands.
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

## Artifact Handoff

Skills can hand work across sessions through target-repository artifacts under:

```text
.lazyday/coding/requirements/<requirement-id>/
```

`lazyday-coding` owns the `coding` artifact namespace. Future Lazyday plugins
must use their own second-level namespace under `.lazyday/`, for example
`.lazyday/vault/requirements/`; do not write shared plugin artifacts directly
to `.lazyday/requirements/`.

Use `resume-context` when the user wants to continue but the active requirement
is unclear; use `manage-artifacts` when the requirement needs to be created,
switched, repaired, archived, or summarized. The artifact protocol is managed by
`manage-artifacts` and documented in
`skills/manage-artifacts/references/artifact-protocol.md`. Artifacts are local
collaboration state by default and should not be included in business commits
unless the user explicitly asks to commit them.

## MCP Servers

This plugin does not bundle MCP servers yet. The placeholder `.mcp.json` is not
referenced by either runtime manifest.
