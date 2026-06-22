---
name: route-vault-task
description: 中文 Lazyday Vault 入口路由技能。用于个人知识库、资料库、笔记、复盘、日志、图片/视频/文件/压缩包/电子书等任意资料的接收、预处理、打标、关联、分层、检索问答、NotebookLM 式资料研究、日报周报年报、心情/感想/项目回顾、原始资料引用和 vault 健康维护。当用户说“保存到知识库”“处理这份资料”“基于我的资料回答”“召回某个图片/日志/文件”“生成日报/周报/复盘/年度总结”“做深入研究”或泛泛提到 lazyday-vault 时使用。
---

# Vault 路由

## 目标

判断当前请求属于 Lazyday Vault 的哪个工作流，并把任务交给最小合适的 skill。不要把所有任务都走完整流水线；一句话快记、文件入库、日志追踪、研究报告和年度复盘需要不同深度。

## 默认约定

- 默认输出简体中文。
- 默认当前项目根目录就是 vault 数据根；该项目可以放在 iCloud Drive 中同步。
- 如需跨会话需求协作产物，使用 `.lazyday/vault/requirements/`，不要和 `raw/`、`processed/`、`wiki/`、`indexes/` 等知识库主数据混放。
- 原始资料层必须全量保留；加工层、wiki 层和答案层必须能追溯到原始资料。
- 对用户个人数据采取本地优先、最小暴露原则；不要主动上传、发布、分享或打印敏感内容。
- 若用户只让“设计方案/分析想法”，默认只读；若用户明确要求“创建/保存/处理/入库/更新 vault”，允许写入当前 vault 项目根下的知识库目录。

详细协议见 `references/vault-protocol.md`。处理特殊资料类型时读 `references/source-types.md`。回答和召回时读 `references/retrieval-protocol.md`。交互、纠错和冲突处理读 `references/interaction-conflict-protocol.md`。需要理论和产品依据时读 `references/industry-patterns.md`。
数据层级、身份模型和反模式见 `references/architecture.md`。

## 路由规则

- 初始化、创建 vault 目录、准备 iCloud 同步项目、修复缺失基础目录：使用 `initialize-vault`。
- 新内容入库、保存一句话、接收文件/图片/视频/压缩包/电子书：使用 `capture-source`。
- 已有 raw source 需要抽取文本、OCR、转录、chunk 或 source map：使用 `extract-source`。
- 已有 extract/chunk 需要打标、分类、关联、更新 wiki 和 indexes：使用 `integrate-knowledge`。
- 用户泛泛说“处理这份资料”，且输入是新内容或文件：先使用 `capture-source`；如果资料已捕获但未说明阶段，使用 `process-source` 协调 `extract-source` 与 `integrate-knowledge`。
- 用户提出问题、要召回图片/文本/日志/项目证据、要基于资料回答：使用 `answer-vault-question`。
- 用户要求“深入研究”“像 NotebookLM 一样研究”“综合多份资料形成报告”：使用 `vault-deep-research`。
- 用户问“我今天/本周/今年做了啥”“心情如何”“关键事件和感悟”“项目参与情况”：使用 `review-life-log`。
- 用户要求“记住这次问答/把这次交互入库/以后以这个修正为准/记录我的反馈”：使用 `record-vault-interaction`。
- 用户要求检查、整理、修复、重建索引、找孤儿页/断链/重复/矛盾：使用 `maintain-vault`。

如果推荐 skill 明确、风险低、用户已经要求执行而不是只要路由建议，应在同一轮继续执行目标 skill 的工作流，不要只输出路由表后停止。只有触发澄清门、确认门或用户明确要求“只判断/先设计”时才停在路由结果。

## 澄清门

低风险时可以采用默认 vault 路径继续。以下情况先问 1-3 个问题：

- 用户要处理非常大的目录、压缩包或视频集合，但未说明是否允许复制原始文件。
- 用户要求联网补充资料、调用外部转写/OCR/云模型，可能暴露私人数据。
- 用户要求删除、重命名、移动 raw source 或批量重写 wiki。
- 用户想默认记录所有交互全文，但未确认隐私范围、保存粒度和关闭方式。
- 用户希望把 vault 与 Obsidian、Notion、Readwise、Google Drive 等外部系统同步，但未确认方向和权限。

## 输出格式

```markdown
**路由判断**
- 请求类型：
- 推荐 skill：
- vault 路径：
- 是否需要写入：

**关键边界**
- 原始资料保留：
- 隐私/外部调用：
- 需要确认：

**交接输入**
- 给下一个 skill 的最小任务说明：
```
