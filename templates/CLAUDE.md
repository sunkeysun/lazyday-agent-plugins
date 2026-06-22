# CLAUDE.md

Use this repository as a Claude Code and Codex compatible plugin marketplace.

Important rules:

- Plugin source lives under `plugins/<plugin-name>/`.
- Claude Code manifest: `.claude-plugin/plugin.json`.
- Codex manifest: `.codex-plugin/plugin.json`.
- Shared workflows live in `skills/<skill-name>/SKILL.md`.
- Templates copied into target projects live in `templates/`.
- Templates required at plugin runtime must also live inside the plugin directory.
