---
name: vault-deep-research
description: 中文 Lazyday Vault 深入研究技能。用于基于个人 vault 的多源资料做 NotebookLM 式研究、专题分析、项目复盘、竞品/技术/问题研究、长报告、表格、证据地图和研究结论；可在用户明确允许时结合外部联网研究，但必须区分 vault 证据、外部来源、推断和建议，并把有价值结果写入可引用的 wiki/reports。
---

# 深入研究

## 目标

围绕一个研究问题，综合 vault 内部资料和用户允许的外部资料，形成可复用、可追溯、可继续迭代的研究产物。

## 默认模式

默认先只用 vault。只有用户明确要求或研究问题明显需要最新外部事实时，才联网，并优先使用官方文档、标准、源码、release note、论文或一手资料。

## 读取协议

先读取：

- `../route-vault-task/references/retrieval-protocol.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/interaction-conflict-protocol.md`

## 工作流

1. 明确研究问题、时间范围、输出形态和证据边界。
2. 建立研究计划：子问题、候选索引、需要读的 source、可能缺口。
3. 检索 vault：wiki/index、entity/tag/timeline/source indexes、processed extracts、raw evidence。
4. 必要且授权时做外部研究，并保存外部来源引用；关键外部资料应作为 `source_type: web` 捕获，记录 URL、访问时间、标题、快照或摘录。
5. 建立 evidence map：每个关键结论对应证据、反证、置信度。
6. 输出报告：结论先行、证据分级、方案/解释/建议。
7. 用户授权时先用 `record-vault-interaction` 记录研究问题、关键交互、parent sources 和最终报告，再写回研究目录和相关 wiki 页面。

## 写回路径

一次深入研究可以沉淀为：

```text
answers/research/<topic>/
├── research-plan.md
├── evidence-map.md
├── external-sources.md
├── final-report.md
└── citation-ledger.md
```

稳定结论再写入：

- `wiki/reports/<topic>.md`
- `wiki/questions/<question>.md`
- `wiki/concepts/<concept>.md`
- `wiki/projects/<project>.md`

研究目录可以记录中间过程；wiki 只写可长期复用且有引用的结论。

## 研究产物

报告必须包含：

- 核心结论。
- 问题拆解。
- Vault 证据。
- 外部证据（如使用）。
- 推断和不确定性。
- 可执行建议。
- 进一步资料缺口。
- 原始引用表。
- interaction source 和 parent_sources（当研究由一次交互触发或产生用户确认决策时）。
- 外部来源捕获状态：temporary citation、captured web source、blocked/not captured。

## 输出格式

```markdown
**研究结论**

**证据地图**
| 结论 | 证据 | 反证/缺口 | 置信度 |
|---|---|---|---|

**分析**

**建议**

**引用**

**可写回**
- report:
- related pages:
```
