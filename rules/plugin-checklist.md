# Plugin Release Checklist

## Structure

- [ ] `.claude-plugin/plugin.json` exists when Claude Code support is required.
- [ ] `.codex-plugin/plugin.json` exists when Codex support is required.
- [ ] `skills/<skill-name>/SKILL.md` exists for each bundled workflow.
- [ ] `.mcp.json` exists only when MCP servers are bundled.
- [ ] Runtime templates are inside the plugin directory.

## Marketplace

- [ ] `.claude-plugin/marketplace.json` lists Claude Code plugins.
- [ ] `.agents/plugins/marketplace.json` lists Codex plugins.
- [ ] Marketplace paths are relative to the marketplace root.

## Validation

- [ ] Codex plugin validation passes.
- [ ] Claude Code plugin validation passes when `claude` is available.
- [ ] Install or reload instructions are documented.
