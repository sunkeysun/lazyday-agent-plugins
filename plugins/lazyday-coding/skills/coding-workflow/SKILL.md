---
name: coding-workflow
description: Use for repository coding tasks, including implementation, bug fixing, refactoring review, test failure diagnosis, and verification planning.
---

Use this skill when the user asks to implement, fix, debug, review, or verify code in a repository.

Workflow:
1. Read the latest user instruction and determine whether the task is read-only or implementation mode.
2. Find applicable project rules before editing files.
3. Check the dirty worktree baseline before modifications.
4. Search for existing implementations and project conventions before adding new code.
5. Keep the change minimal and scoped to the current request.
6. Preserve public contracts unless the user explicitly approves a contract change.
7. For bugs, identify the failure evidence and root cause before editing.
8. After editing, inspect the diff and run the smallest relevant verification.
9. Report changed files, validation evidence, and remaining risk.

Do not:
- Rewrite unrelated code.
- Add dependencies without explicit approval.
- Hide failures by weakening tests, deleting assertions, or swallowing errors.
- Modify files outside the requested scope unless needed and explained.
