# AGENTS.md

## Scope

This file defines durable coding-agent rules for projects that use Lazyday Coding.

## Working Rules

- Identify whether the user requested read-only analysis or implementation.
- Read project-level rules before changing files.
- Check the dirty worktree baseline before edits when the target is a Git repository.
- Preserve user changes and avoid unrelated formatting.
- Reuse existing implementation patterns before adding new abstractions.
- Make the smallest change that satisfies the task.
- Verify with the smallest relevant test, type check, build, or smoke check.

## Delivery

Report:

- What changed.
- Which files changed.
- Which verification ran.
- What remains unverified, if anything.
