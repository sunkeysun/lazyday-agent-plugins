---
name: route-coding-task
description: 中文 Lazyday Coding 入口路由技能。用于用户提出日常代码开发请求但还不确定应该使用哪个 coding skill、是否要从已有 `.lazyday/coding/requirements/` 继续、是否要创建需求产物、是否只是单独使用某个 skill、或是否要跳过前序阶段直接实现/验证/review/提交时使用。适用于“继续做这个需求”“我现在该用哪个 skill”“完整跑一个需求”“直接实现这个”“只做 bug 定位/方案探索/review”等请求。默认只读，只做任务识别、上下文恢复建议和下一步 skill 路由；不强制固定流程。
---

# 编码任务路由

## 目标

判断当前用户请求应该进入 Lazyday Coding 的哪个 skill，并区分两种使用场景：

- **完整需求场景**：一个需求可能跨多个 skill、多次会话和多个 agent，需要用 `.lazyday/coding/requirements/` 管理上下文、阶段产物和 handoff。
- **单点工具场景**：用户只想单独使用某个 skill，例如方案调研、bug 定位、项目探索、实现、验证、review 或提交，不要求创建需求产物或继续后续流程。

本 skill 是入口判断层，不是固定工作流控制器。它不要求按 `clarify -> explore -> research -> plan -> implement -> verify -> review -> commit` 顺序执行；用户可以跳过任意阶段，只要目标、授权和风险边界足够清楚。

## 默认模式

默认只读。

允许：

- 读取用户请求、对话上下文、项目规则、`git status --short --branch` 和已有 `.lazyday/coding/requirements/` 索引。
- 判断工作模式、风险等级、是否只读、是否需要恢复上下文、是否需要创建或切换产物。
- 推荐一个主 skill 和必要的前置补充动作。

禁止：

- 修改业务代码。
- 创建、切换或修复 `.lazyday/coding/requirements/` 产物；这些动作交给 `manage-artifacts`。
- 在上下文不明确时替用户选择高风险实现方向。
- 把单点工具请求强行升级成完整需求流程。

## 路由流程

### 1. 判断用户意图

先识别本轮属于哪类：

- 模糊需求、边界不清、验收标准缺失：`clarify-task`
- 继续、上次、当前需求、跨会话恢复：`resume-context`
- 创建、选择、切换、整理、修复需求产物：`manage-artifacts`
- 陌生仓库、找入口、调用链、测试命令、已有实现：`explore-repo`
- 方案、选型、最佳实践、架构取舍、实现路径：`research-approach`
- 拆任务、多 agent、并发边界、实施计划：`break-down-task`
- bug、日志、报错、测试失败、根因分析：`diagnose-problem`
- 已明确授权修改、修复、落地、按方案执行：`implement-change`
- 验证、跑测试、确认修复、交付前证据：`verify-change`
- review、审查 diff、合入前把关、评分：`review-code`
- commit message、提交、推送：`commit-changes`

如果用户目标像是完整需求，但验收标准、范围边界或是否允许修改仍不清楚，默认主 skill 是 `clarify-task`。只有用户明确授权临时探索、直接实现或临时修复，且目标 skill 能在内部补齐最小任务契约和安全门时，才允许跳到后段 skill。

### 2. 判断是否需要需求产物

只有以下情况建议使用 `.lazyday/coding/requirements/`：

- 用户明确要求跨会话记录、后续继续、完整需求管理或多 skill 协作。
- 需求预计跨多次会话、多阶段或多 agent。
- 当前有多个活跃需求，容易混淆上下文。

以下情况不要强制创建产物：

- 用户明确只想单独执行一个 skill。
- 一次性低风险问题、只读咨询、临时 review、临时验证。
- 用户要求不落盘或只在当前回复中给结果。

### 3. 判断是否需要恢复上下文

用户说“继续”“上次”“当前任务”“接着实现/验证/review/提交”，但没有明确需求 ID、文件范围或 diff 范围时，先交给 `resume-context`。

如果用户已经给出明确需求 ID、文件、模块、diff、日志或方案，可以直接进入对应 skill，不必先恢复上下文。

### 4. 支持跳步执行

用户可以直接调用后段 skill：

- 直接实现：允许进入 `implement-change`，但必须由实现 skill 自己补最小任务契约、修改边界、dirty 基线、已有模式和验证计划。
- 直接验证：允许进入 `verify-change`，由验证 skill 从当前 diff 和验收标准推导最小验证集。
- 直接 review：允许进入 `review-code`，由 review skill 自己建立 diff 地图和上下文。
- 直接提交：允许进入 `commit-changes`，但必须重新确认提交范围，不能只依赖前序产物。

跳步不等于跳过安全门。只读边界、确认门、dirty worktree 保护和验证证据仍由目标 skill 执行。

## 输出格式

```markdown
**路由判断**
- 用户意图：
- 使用场景：完整需求 / 单点工具
- 是否只读：
- 是否需要需求产物：
- 是否需要恢复上下文：

**推荐执行**
- 主 skill：
- 原因：
- 交接输入：

**边界**
- 当前不做：
- 需要确认：
- 风险等级：
```

## 后续交接

- 推荐某个 skill 后，给出可直接交给该 skill 的最小输入。
- 如果推荐 `resume-context`，说明要匹配的关键词、文件、阶段或用户描述。
- 如果推荐 `manage-artifacts`，说明需要创建、选择、切换、整理还是修复。
- 如果用户只想单点执行，明确“本轮到该 skill 输出即完成，不要求继续后续流程”。
