---
name: manage-artifacts
description: 中文 Lazyday 需求产物管理技能。用于创建、选择、切换、列出、读取、更新、检查、归档或修复 `.lazyday/coding/requirements/` 下的跨会话需求产物；用于用户说“创建需求产物”“列出需求”“切换当前需求”“整理 handoff”“检查产物完整性”等请求。只负责产物生命周期管理；如果用户只是说“继续”“上次那个需求”且需要根据描述匹配候选，先使用 `resume-context`。
---

# 产物管理

## 目标

管理目标仓库中的 Lazyday 跨会话需求产物，让不同 skill、不同会话和不同 agent 能围绕同一个需求顺利交接。

本 skill 只负责 `.lazyday/coding/requirements/` 的生命周期管理：创建、选择、切换、列出、读取状态、维护索引、维护 `CURRENT`、维护 `manifest.md`、整理 `handoff.md`、检查完整性、归档和重命名。它不负责上下文语义匹配、方案设计、项目探索、代码实现、问题定位、验证、Review 或 Git 提交。

`lazyday-coding` 的插件产物命名空间固定为 `coding`。所有本插件产物必须写入 `.lazyday/coding/requirements/`；不要写入旧路径 `.lazyday/requirements/`，也不要与其他 Lazyday 插件共享同一个二级目录。

## 产物协议

完整结构和读写规则见 `references/artifact-protocol.md`。需要细节时先读取该文件。

核心结构：

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

需求 ID 使用 `YYYYMMDD-HHMM-短名称`。短名称用小写字母、数字和连字符。

## 默认模式

默认允许写入 `.lazyday/coding/requirements/`，因为这就是本 skill 的职责。

但在写入前仍要：

1. 确认当前目录在目标仓库内。
2. 读取适用的项目级规则。
3. 运行 `git status --short --branch`，保护用户已有改动。
4. 重新读取目标需求的 `manifest.md`、`handoff.md` 和即将写入的文件。
5. 只修改 `.lazyday/coding/requirements/` 下的产物文件。

禁止：

- 修改业务代码。
- 修改其他 skill 的输出内容，除非用户要求整理产物并且改动范围只在 `.lazyday/coding/requirements/`。
- 删除需求目录，除非用户明确要求。
- 把 `.lazyday/` 自动加入业务提交。

## 操作类型

### 列出需求

当用户要求“列出需求”“有哪些需求”“从哪个需求继续”：

1. 读取 `.lazyday/coding/requirements/index.md`。
2. 读取 `CURRENT`。
3. 必要时读取各需求的 `manifest.md`。
4. 输出需求 ID、标题、状态、最后阶段、更新时间和建议下一步。
5. 如果 `index.md` 不存在，说明当前没有 Lazyday 需求产物。

### 选择当前需求

当用户指定需求继续：

1. 确认 `.lazyday/coding/requirements/<需求ID>/` 存在。
2. 将需求 ID 写入 `.lazyday/coding/requirements/CURRENT`。
3. 读取该需求的 `manifest.md`、`handoff.md`、`brief.md` 和可用阶段文件。
4. 必要时更新 `manifest.md` 的 `updated_at`、`current_stage` 和 `next_skill`。
5. 输出当前状态和建议下一步 skill。

如果用户没有指定需求，只是让你根据当前描述判断“继续哪个”，先交给 `resume-context` 排序候选，再由用户确认是否切换。

### 创建新需求

当用户要求记录新需求或后续交接：

1. 生成需求 ID。
2. 如果 `.lazyday/coding/requirements/` 不存在，先创建父目录，并初始化空的 `index.md` 和 `CURRENT`。
3. 创建需求目录。
4. 初始化 `manifest.md`、`brief.md`、`decisions.md`、`open-questions.md`、`handoff.md`。
5. 更新 `index.md`。
6. 更新 `CURRENT`。

如果用户只给了模糊需求，先让 `clarify-task` 补全任务契约；如果用户明确要求直接创建，可以先用当前信息创建草稿，并在 `open-questions.md` 标出缺口。

### 更新阶段产物

其他 skill 通常负责写自己的阶段文件。本 skill 只在用户要求“整理产物”“补 handoff”“汇总当前状态”时更新：

- `handoff.md`
- `index.md`
- `CURRENT`
- `manifest.md`
- `decisions.md`
- `open-questions.md`

如果用户要求改写某个阶段文件，先说明这会覆盖对应 skill 的产物，并确认要改哪些内容。

写入前检查是否存在并发或跨会话更新：

- `CURRENT` 是否仍指向预期需求。
- `manifest.md` 的 `updated_at`、`current_stage`、`next_skill` 或 `summary` 是否在本轮读取后变化。
- `handoff.md` 是否已有新阶段、新风险或不同的下一步 skill。
- 目标文件是否出现未理解的新内容。

发现冲突时先输出差异和合并建议，不要直接覆盖。

### 修复优先级

检查或修复产物时按以下顺序处理：

1. `CURRENT` 指向不存在的需求：不要猜测切换目标；列出候选需求、语义线索和推荐选择，等用户确认后再写入。
2. `index.md` 缺失但存在需求目录：可从各目录的 `manifest.md` 重建候选索引；写入前列出将加入的需求和状态来源。
3. `index.md` 与 `manifest.md` 标题、状态、阶段或下一步不一致：把 `manifest.md` 当作单个需求的事实来源，输出差异；只有用户要求修复时才同步 `index.md`。
4. `manifest.md` 或 `handoff.md` 缺少必填字段：只补可从现有产物确认的事实；未知项写 `unknown`，不要推测。
5. 多个会话或 agent 可能同时更新同一需求：先停止写入，输出冲突文件、读取时值、当前值和建议合并方式。

### 整理 handoff

`handoff.md` 必须保持一页以内，优先使用以下字段：

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

整理时只写已确认事实。未知内容写 `none` 或 `unknown`，不要用推测补空。

### 检查完整性

检查：

- `index.md` 是否包含当前需求。
- `CURRENT` 是否指向存在的需求目录。
- `manifest.md` 是否存在，且包含 id、status、updated_at、current_stage、next_skill 和 summary。
- 需求目录是否缺少基础文件。
- `handoff.md` 是否存在、足够短，且包含 current_stage、goal、done、open_questions、risks、next_skill 和 updated_at。
- 阶段文件之间是否明显矛盾，例如 `plan.md` 指向的目标与 `brief.md` 不一致。

发现问题时输出修复建议；只有用户要求修复时才写入。

### 归档或重命名

归档需求时，优先更新 `index.md` 状态为 `archived`。不要移动或删除目录，除非用户明确要求。

重命名需求 ID 会影响引用，必须先说明影响范围并确认。更推荐只改标题，不改目录名。

## 输出格式

```markdown
**产物操作**
- 操作：
- 需求 ID：
- 当前需求：

**产物状态**
- index：
- CURRENT：
- 已有阶段文件：
- 缺失文件：

**本次更新**
- 写入文件：
- 未写入：

**建议下一步**
- 推荐 skill：
- 交接输入：
```

## 交接规则

- 需要根据用户描述匹配候选需求或恢复上下文：交给 `resume-context`。
- 需要判断该用哪个 skill 或是否需要需求产物：交给 `route-coding-task`。
- 需要澄清任务：交给 `clarify-task`。
- 需要探索仓库：交给 `explore-repo`。
- 需要方案调研：交给 `research-approach`。
- 需要拆任务：交给 `break-down-task`。
- 需要定位问题：交给 `diagnose-problem`。
- 需要实现：交给 `implement-change`。
- 需要验证：交给 `verify-change`。
- 需要 Review：交给 `review-code`。
- 需要提交：交给 `commit-changes`。
