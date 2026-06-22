---
name: clarify-task
description: 中文任务澄清与契约补全技能。用于用户需求模糊、范围不清、只读/实现边界不明确、成功标准缺失、风险等级不明、需要补全 Lazyday 需求契约时使用。适用于“先澄清”“帮我梳理需求”“这个任务怎么界定”“生成任务契约”“明确验收标准”等请求。默认只读；如果用户只是要从已有产物恢复“继续哪个需求”，先使用 `resume-context`；只有用户要求跨会话记录或后续交接时才写入 `.lazyday/coding/requirements/` 产物。
---

# 任务澄清

## 目标

把模糊请求整理成可执行、可验证、可交接的任务契约。重点是明确目标、非目标、工作模式、风险等级、成功标准、确认门和后续可用 skill，而不是直接设计方案或修改代码。

本 skill 是独立工具，可以单独用于需求澄清、任务入口判断、任务契约补全和后续 workflow handoff。它不依赖其他 skill；如有需要，只在最后建议交给 `resume-context`、`manage-artifacts`、`explore-repo`、`research-approach`、`break-down-task`、`diagnose-problem`、`implement-change`、`verify-change`、`review-code` 或 `commit-changes`。

## 默认模式

默认只读。

允许：

- 阅读用户请求、历史上下文、已有 `.lazyday/coding/requirements/` 产物和项目规则。
- 使用只读命令检查是否存在需求产物目录。
- 输出任务契约、澄清问题、风险判断和后续 skill 建议。

禁止：

- 未经用户要求创建、修改、删除代码文件。
- 在边界不清时替用户做高风险决策。
- 直接进入实现、提交、推送或破坏性操作。
- 把一次性猜测写成已确认需求。

当用户要求“记录这个需求”“后续继续用”“跨会话交接”“创建需求产物”或需要多个 skill 协作时，先交给 `manage-artifacts` 创建或选择需求产物。若当前需求已经明确，本 skill 可以更新该需求的 `brief.md`、`decisions.md`、`open-questions.md` 和 `handoff.md`。用户明确要求只读、不落盘、不建产物或只在当前回复中给结果时，即使需求明显适合跨会话管理，也只能输出契约和建议，不调用产物写入流程，不写 `.lazyday/coding/requirements/`。

## 产物交接

需求产物由 `manage-artifacts` 统一管理。需要创建、选择、切换、列出、归档或修复 `.lazyday/coding/requirements/` 时，先使用 `manage-artifacts`。如果用户说“继续”“上次”“当前需求”但没有明确需求 ID，先使用 `resume-context` 匹配候选需求。

当前需求已明确时，本 skill 只读取和更新与任务契约相关的产物：

- 读取：`brief.md`、`decisions.md`、`open-questions.md`、`handoff.md`。
- 写入：`brief.md`、`decisions.md`、`open-questions.md`、`handoff.md`。

`.lazyday/` 默认是本地协作产物，不纳入业务提交。

## 澄清流程

### 1. 识别入口

先判断用户请求属于哪类：

- 纯咨询：只回答问题，不创建产物。
- 需求澄清：补全任务契约。
- 继续已有需求：若需求不明确，交给 `resume-context` 匹配候选；若需求明确，读取 `.lazyday/coding/requirements/<需求ID>/`。
- 准备进入方案调研：输出可交给 `research-approach` 的契约。
- 准备进入项目探索：输出可交给 `explore-repo` 的探索目标。
- 准备进入问题定位：输出可交给 `diagnose-problem` 的问题描述和证据缺口。
- 准备进入实现：确认用户是否明确授权修改。
- 准备进入验证、review 或提交：确认目标 diff、提交范围和验证证据。

### 2. 补全任务契约

至少补齐：

- 目标：本轮要达成什么。
- 非目标：明确不做什么。
- 当前阶段：只读分析、方案调研、项目探索、任务拆解、实现、验证、review、提交。
- 成功标准：什么结果算完成。
- 输入资料：用户给了什么，仍缺什么。
- 约束边界：范围、时间、风险、技术栈、项目规则、不可动区域。
- 风险等级：S0-S4，并说明触发原因。
- 确认门：哪些决策必须用户确认。
- 建议下一步 skill：一个主建议，必要时给备选。

### 3. 最小澄清问题

只问能显著影响执行方向的问题。默认最多 3 个。

优先问：

- 这轮是只读还是可以修改？
- 验收标准是什么？
- 是否要记录到 `.lazyday/coding/requirements/` 以便后续继续？
- 多个需求候选时，要从哪个需求继续？
- 高风险决策的偏好或限制是什么？

低风险任务可以带着显式假设继续；高风险、核心链路、提交/推送、删除、迁移、权限、安全和发布相关任务必须确认关键问题。

## 产物写入

只有当前需求已由 `manage-artifacts` 选定，且用户允许跨会话记录时，才写入任务契约产物：

1. 更新 `brief.md`，记录任务契约。
2. 更新 `open-questions.md`，只记录仍未解决的问题。
3. 更新 `decisions.md`，只记录用户已确认的决策。
4. 更新 `handoff.md`，给下一个 skill 一页以内的上下文摘要。

`brief.md` 推荐格式：

```markdown
# <需求标题>

## 任务契约
- 目标：
- 非目标：
- 当前阶段：
- 成功标准：
- 风险等级：
- 确认门：

## 约束
- 项目范围：
- 不应修改：
- 验证要求：

## 交接
- 当前状态：
- 建议下一步 skill：
- 下一步输入：
```

## 输出格式

默认输出：

```markdown
**任务契约**
- 目标：
- 非目标：
- 当前阶段：
- 成功标准：
- 风险等级：

**上下文与缺口**
- 已知：
- 缺失：
- 本次假设：

**确认问题**
1. 

**产物状态**
- 是否使用 `.lazyday/coding/requirements/`：
- 需求 ID：
- 已更新：

**建议下一步**
- 推荐 skill：
- 交接输入：
```

## 后续交接

- 需要从已有产物恢复上下文或匹配候选需求：交给 `resume-context`。
- 需要创建、选择或切换需求产物：交给 `manage-artifacts`。
- 需要理解仓库：交给 `explore-repo`，附带 `brief.md` 和探索目标。
- 需要方案：交给 `research-approach`，附带任务契约、约束和证据缺口。
- 需要拆任务：交给 `break-down-task`，附带已确认方案和验收标准。
- 需要定位问题：交给 `diagnose-problem`，附带问题描述、时间线和缺失资料。
- 需要实现：交给 `implement-change`，必须确认用户已授权修改。
- 需要验证：交给 `verify-change`，附带验收标准和验证要求。
- 需要 review：交给 `review-code`，附带 review 范围和关注风险。
- 需要提交：交给 `commit-changes`，附带提交范围和验证证据。
