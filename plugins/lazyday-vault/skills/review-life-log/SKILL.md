---
name: review-life-log
description: 中文 Lazyday Vault 个人复盘技能。用于从 vault 时间线和原始证据生成日报、周报、月报、年报、项目回顾、关键事件、心情变化、感想总结、参与项目清单、习惯/健康/学习/工作复盘；必须基于 timeline/source 证据，区分用户明确表达、行为事实和低置信情绪推断。
---

# 个人复盘

## 目标

把分散的记录变成可靠的生活和工作回顾。重点是证据、时间线、变化和洞察，不是编造漂亮总结。

## 读取协议

先读取：

- `../route-vault-task/references/retrieval-protocol.md`
- `../route-vault-task/references/interaction-conflict-protocol.md`
- `../route-vault-task/references/vault-protocol.md`

## 工作流

1. 确定时间范围：今天、本周、本月、今年、某项目周期或用户指定范围。
2. 读取 timeline-index、相关 timelines、source-index、project pages、interaction-index、claim-index、conflict-index 和最近 ingest/process logs。
3. 按类别整理：
   - 做了什么。
   - 参与了什么项目。
   - 遇到什么问题。
   - 做了哪些决策。
   - 与谁互动。
   - 心情/感想/压力/成就感线索。
   - 可复用经验和待办。
4. 回到 source 证据校验关键事件，并排除 superseded/disputed 旧 answer。
5. 输出总结、证据、不确定性和覆盖范围。
6. 用户授权时写回 `wiki/reports/` 或 `wiki/timelines/`。

## 情绪和感想规则

- 用户直接写“开心/焦虑/烦/有成就感”等，才作为事实。
- 从行为推断心情时必须标注“推断”，并给依据。
- 不做心理诊断，不把短期记录过度解释成人格结论。

## 输出格式

```markdown
**时间范围**

**覆盖范围**
- 已检索：
- 命中 source：
- source 类型：
- 缺失区间：
- open conflicts / superseded:

**做了什么**

**关键事件**

**项目参与**

**心情与感想**
- 明确表达：
- 推断：
- 证据：

**可复用经验**

**待确认/缺失记录**

**引用**
```
