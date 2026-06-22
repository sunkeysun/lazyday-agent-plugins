# Lazyday 产物协议

Lazyday skills 使用目标仓库内的 `.lazyday/<plugin-artifact-namespace>/requirements/` 保存跨会话、跨 skill 的协作产物。这个目录服务于 agent 协作，不是业务源码的一部分。

## 插件产物命名空间

`.lazyday/` 下的二级目录必须是插件产物命名空间，用来隔离不同 Lazyday 插件的产物。

命名规则：

- 每个插件必须定义稳定的 `artifact namespace`。
- 命名空间使用小写字母、数字和连字符。
- 默认从插件名派生：去掉 `lazyday-` 前缀后作为短名。
- `lazyday-coding` 固定使用 `coding`，产物根路径为 `.lazyday/coding/requirements/`。
- 后续插件示例：`lazyday-vault` 使用 `vault`，产物根路径为 `.lazyday/vault/requirements/`。
- 禁止把插件产物直接写入 `.lazyday/requirements/`。

## 目录结构

`lazyday-coding` 当前结构：

```text
.lazyday/
└── coding/
    └── requirements/
        ├── index.md
        ├── CURRENT
        └── <需求ID>/
            ├── manifest.md
            ├── brief.md
            ├── repo-context.md
            ├── research.md
            ├── plan.md
            ├── diagnosis.md
            ├── implementation.md
            ├── verification.md
            ├── review.md
            ├── commit.md
            ├── decisions.md
            ├── open-questions.md
            └── handoff.md
```

## 需求 ID

使用 `YYYYMMDD-HHMM-短名称`。短名称用小写字母、数字和连字符，例如：

```text
20260622-1745-skill-artifacts
```

## 读取策略

1. 先读 `index.md` 和 `CURRENT`。
2. 用户指定需求时，只读取该需求目录。
3. 用户说“继续”且需求上下文明确时，读取当前需求。
4. 用户说“继续”“上次”“当前需求”但上下文不明确时，使用 `resume-context` 读取 `index.md`、`CURRENT`、`manifest.md`、`handoff.md` 和 `brief.md`，按相关性排序候选。
5. 存在多个候选需求且用户未指定时，列出候选并让用户选择。
6. 每个 skill 只读取自己需要的产物，避免加载整个目录。

## 写入策略

只有用户要求跨会话记录、后续交接、继续需求或明确允许落盘时，才写入 `.lazyday/coding/requirements/`。用户要求只读或不落盘时，只在回复中输出产物内容。

首次创建需求产物时，如果 `.lazyday/coding/requirements/` 不存在，先创建父目录并初始化空的 `index.md` 和 `CURRENT`，再创建具体需求目录。写入 `CURRENT` 前必须确认新需求 ID 已创建成功。

每个 skill 写入对应文件：

- `route-coding-task` -> 默认只读，不写入产物
- `manage-artifacts` -> `index.md`、`CURRENT`、`manifest.md`、`handoff.md`
- `resume-context` -> 默认只读，不写入产物
- `clarify-task` -> `brief.md`、`decisions.md`、`open-questions.md`
- `explore-repo` -> `repo-context.md`
- `research-approach` -> `research.md`
- `break-down-task` -> `plan.md`
- `diagnose-problem` -> `diagnosis.md`
- `implement-change` -> `implementation.md`
- `verify-change` -> `verification.md`
- `review-code` -> `review.md`
- `commit-changes` -> `commit.md`

每次写入阶段产物时，同步更新 `handoff.md`，保持一页以内。

### `plan.md` 标准结构

`break-down-task` 写入 `plan.md` 时必须让实现阶段可以直接调度执行。推荐结构：

```markdown
# Plan

## Context Readiness

## Change Scope

## Coverage Matrix
| Requirement / Risk / Failure Path | Task | Verification | Gap |
|---|---|---|---|

## Conflict Matrix
| Shared Resource | Owner Task / Agent | Other Touchpoints | Conflict Handling |
|---|---|---|---|

## Execution Schedule
- ready_now:
- blocked:
- serial_required:
- parallel_groups:
- merge_sequence:
- shared_conflict_points:
- recommended_execution_mode:

## Task Dependency Graph
| Task | Goal | Depends On | Parallel | File Ownership | Verification |
|---|---|---|---|---|---|

## Complete Task List
| Task | Title | Type | Source | Status | Owner | Verification |
|---|---|---|---|---|---|---|

## Agent Packets

## Task Cards

## Verification Matrix

## Implementation Risks
```

实现阶段读取 `plan.md` 时，必须优先遵守 `Execution Schedule`、`Conflict Matrix` 和每张任务卡的允许/禁止写入范围。

### 写入前冲突检查

任何 skill 写入 `.lazyday/coding/requirements/<需求ID>/` 前，必须重新读取目标文件、`manifest.md` 和 `handoff.md` 的最新内容。

如果发现以下情况，先暂停并说明差异，不要覆盖：

- `manifest.md` 的 `updated_at`、`current_stage`、`next_skill` 或 `summary` 与本轮已读取基线不同。
- `handoff.md` 已被其他会话更新，且更新内容可能改变下一步 skill、当前阶段、风险或文件范围。
- 目标阶段文件已有未理解的新内容。
- `CURRENT` 指向的需求在本轮过程中发生变化。

可以继续写入的条件：

- 变化只是不相关字段，且本次写入不会覆盖对方内容。
- 用户明确确认以当前结果覆盖或合并。
- 写入方式是追加新证据，而不是替换旧结论。

### 修复优先级

`manage-artifacts` 修复产物时按以下顺序处理：

1. `CURRENT` 指向不存在的需求：不要猜测切换目标，先列候选并等待用户确认。
2. `index.md` 缺失但存在需求目录：从各目录 `manifest.md` 重建候选索引，写入前列出来源。
3. `index.md` 与 `manifest.md` 冲突：以单个需求的 `manifest.md` 为事实来源，输出差异；只有用户要求修复时才同步索引。
4. `manifest.md` 或 `handoff.md` 缺字段：只补已确认事实，未知项写 `unknown`。
5. 发现并发更新：暂停写入，输出冲突文件、读取时值、当前值和合并建议。

### `handoff.md` 标准字段

`handoff.md` 必须短，一页以内，用于新会话快速恢复。推荐结构：

```markdown
# Handoff

- requirement_id:
- current_stage:
- goal:
- done:
- changed_files:
- evidence:
- open_questions:
- risks:
- next_skill:
- do_not_touch:
- updated_at:
```

字段含义：

- `current_stage`：当前阶段，例如 clarify、explore、research、plan、diagnose、implement、verify、review、commit。
- `done`：本阶段已完成的事实，不写推测。
- `changed_files`：本需求已经修改或明确会修改的文件；没有则写 none。
- `evidence`：已运行的验证、日志、复现、review 证据；没有则写 none。
- `open_questions`：阻塞继续执行的问题；没有则写 none。
- `risks`：下一个 skill 必须知道的边界和剩余风险。
- `next_skill`：建议继续的一个主 skill。
- `do_not_touch`：用户明确禁止或本轮不应修改的范围。

## `manifest.md`

每个需求目录必须包含 `manifest.md`，用于跨会话快速匹配和恢复上下文。建议结构：

```markdown
# <需求标题>

- id:
- status: active | blocked | done | archived
- created_at:
- updated_at:
- current_stage:
- next_skill:
- tags:
- branch:
- related_files:
- summary:
```

`manage-artifacts` 创建、选择、归档、修复或整理需求时维护 `manifest.md`。其他业务 skill 更新阶段产物时，可以建议更新 `current_stage`、`next_skill`、`related_files` 和 `updated_at`，但不要绕过 `manage-artifacts` 做生命周期动作。

## Git 策略

`.lazyday/` 默认是本地协作目录。`commit-changes` 默认不提交 `.lazyday/`，除非用户明确要求提交协作产物。
