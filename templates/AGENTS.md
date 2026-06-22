# AGENTS.md

## Scope

This file defines durable coding-agent rules for this repository.

## Working Rules

- Read the nearest applicable `AGENTS.md` before editing files.
- Preserve user changes. Check `git status --short --branch` before modifications when the target is a Git repository.
- Keep changes minimal and scoped to the current request.
- Reuse existing implementations before adding new abstractions.
- Do not add, remove, or upgrade dependencies without explicit approval.
- Run the smallest relevant verification after changes.
- If verification cannot run, explain why and state residual risk.

## Project Conventions

- Put reusable agent workflows in `skills/<skill-name>/SKILL.md`.
- Keep Claude Code and Codex plugin manifests separate.
- Keep shared templates under `templates/`.
- Runtime files needed by a plugin must live inside that plugin directory.

## Validation

Before delivery, check:

- Modified files match the requested scope.
- Plugin manifests are valid for their target runtimes.
- Marketplace entries point to the correct plugin path.
- Skills have clear trigger descriptions and focused instructions.
