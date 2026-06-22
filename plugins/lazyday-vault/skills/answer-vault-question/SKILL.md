---
name: answer-vault-question
description: 中文 Lazyday Vault 检索问答技能。用于基于个人 vault 回答问题、召回图片/文本/日志/文件/视频片段、解释某个项目或故障、回答“今天做了啥/今年做了啥/某个问题的证据是什么/软件工程有哪些设计模式”等问题；必须从 wiki/index/processed/raw 中检索，给出原始资料引用、证据强度、不确定性和缺口，不得凭空补造个人事实。
---

# Vault 问答

## 目标

从 vault 中准确召回证据并组织答案。答案必须能回到原始资料，而不是只依赖模型记忆或加工层摘要。

## 读取协议

先读取 `../route-vault-task/references/retrieval-protocol.md`。涉及旧问答、纠错、决策或冲突时读取 `../route-vault-task/references/interaction-conflict-protocol.md`。需要目录细节时读取 `../route-vault-task/references/vault-protocol.md`。

## 工作流

1. 识别问题类型：
   - 事实问答。
   - 时间线/复盘。
   - 图片/文件/日志/视频召回。
   - 项目/人物/主题总结。
   - 故障分析。
   - 通用知识解释。
2. 先查 wiki/index，再查 source-index、tag-index、entity-index、timeline-index、asset-index、claim-index。
3. 读取候选 wiki 页和 processed extracts。
4. 对关键结论回到 source manifest、source map 或 raw source 校验。
5. 检查 interaction-index、conflict-index 和 claim-index，排除 superseded/disputed 的旧结论。
6. 对故障、项目、图片、日志类问题执行组合召回：日志 source、截图/录屏 asset、用户说明、同 batch 压缩包和后续 correction 一起查。
7. 输出答案，区分事实、推断、建议和缺口。
8. 给引用表：source_id、定位符、raw path、证据强度、匹配理由。
9. 如果答案本身值得沉淀，建议使用 `record-vault-interaction` 把问答作为 interaction source，再写回 `wiki/questions/` 或 `wiki/reports/`；未获授权不写。

## 回答规则

- 找不到证据时说找不到，并说明查了哪些索引。
- 个人经历、心情、项目参与、年度总结必须基于 timeline/source 证据。
- 故障问题优先给原始日志片段和时间线，再给根因推断。
- 通用知识问题可以结合已有 vault 内容和模型通识，但必须标明哪些来自 vault，哪些是通用解释。
- 召回图片/文件时给路径和 source_id，不只给描述。
- 旧 answer 只能证明“当时这样答过”，不能单独证明回答内容是真的；事实引用必须回到 parent sources。
- 缺少 parent_sources 的旧 answer 只能作为 historical answer，不得作为事实证据。
- 用户后续修正必须作为 correction source 处理，而不是直接覆盖旧 answer。

## 输出格式

```markdown
**答案**

**证据**
- [S1] source:
- [S2] source:

**不确定性**
- 未覆盖：
- 低置信推断：

**可沉淀内容**
- 建议记录交互：
- 建议写回：
- 推荐位置：
```
