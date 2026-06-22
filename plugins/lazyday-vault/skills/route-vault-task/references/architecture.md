# Lazyday Vault 架构设计

## 设计目标

Lazyday Vault 不是普通笔记目录，也不是只在查询时检索 chunk 的临时 RAG。它是一个本地优先、可追溯、可长期维护的个人知识系统。它必须同时满足：

- 任意资料低摩擦进入。
- 原始资料全量保留。
- 加工结果可以重建。
- 每个回答都有原始引用。
- 用户与 vault 的问答、修正、决策和反馈也可以成为新的可追溯 source。
- 个人时间线、项目、心情、复盘和研究报告能长期累积。
- 普通 markdown 文件可读、可版本化、可被不同 agent 维护。
- 当前项目根目录可以直接作为 vault 数据根，放到 iCloud Drive 同步。
- 知识冲突要能定位到 claim，而不是只能粗粒度否定整份 source。

## 核心判断

主架构必须以 `source_id` 为中心，而不是以文件夹分类为中心。

原因：

- 一份资料经常同时属于项目、时间线、人物、主题、PARA 和资产类型。
- 文件夹只能表达一个主位置，无法表达多维关联。
- 后续问答需要精确引用原始资料，而不是引用某个被移动过的分类路径。
- LLM 维护 wiki 时会不断重组概念，不能让概念页面成为事实源。

因此：

- `raw/` 和 `manifest.md` 是 source of truth。
- `processed/`、`indexes/`、`wiki/`、`answers/` 都是派生视图。
- 任何派生视图都必须能追溯到 `source_id + locator + raw_path`。

## 层级模型

默认当前项目根目录就是 vault 数据根。如果同一项目还需要跨会话需求协作产物，放在 `.lazyday/vault/requirements/`，不要与知识库主数据混放。

| 层级 | 目录 | 职责 | 可变性 | 失败后果 |
|---|---|---|---|---|
| L0 Inbox | `inbox/` | 暂存用户刚丢进来的材料 | 可清理 | 未入库资料可能漏处理 |
| L1 Raw Source | `raw/` | 原始资料和 source manifest | 追加为主，不直接改写 | 事实源丢失，不可接受 |
| L2 Extract | `processed/extracts/` | OCR、转写、文本抽取、结构化摘录 | 可重建 | 检索质量下降 |
| L3 Source Map | `processed/source-maps/` | extract/chunk 到 raw 的定位映射 | 可重建但必须严谨 | 引用无法校验 |
| L4 Indexes | `indexes/` | source、tag、entity、timeline、asset、claim、citation 导航 | 可重建 | 召回变慢、漏召回或引用到过期结论 |
| L5 Wiki | `wiki/` | LLM 维护的项目、领域、概念、实体、时间线和报告 | 可编辑，需引用 | 长期知识退化或矛盾 |
| L6 Answers | `answers/` 或 `wiki/questions/` | 高价值问答和研究结果沉淀 | 可编辑，需引用 | 聊天成果无法复利 |
| L7 Logs | `logs/` | ingest、process、query、research、maintenance 摘要和 JSONL 事件账本 | 追加为主 | 无法恢复操作历史或处理同步冲突 |

## 交互也是 Source

用户与 vault 的任何有价值交互都可以作为 `source_type: interaction` 进入 raw source 层，例如：

- 用户提问和上下文补充。
- assistant 的有引用回答。
- 用户对回答的修正、否定、补充和确认。
- 深入研究过程中的中间结论、取舍和最终决策。
- 用户要求“以后记住”“这次结论入库”“把这次复盘保存下来”的内容。

交互 source 必须区分角色：

- `user_assertion`：用户原话、偏好、经历、确认或修正。
- `assistant_answer`：assistant 基于资料组织的回答。
- `tool_observation`：工具读到的文件、日志、命令输出或验证结果。
- `decision`：用户确认的结论、分类、项目归属或后续动作。
- `correction`：用户对既有 wiki、answer 或 source interpretation 的纠错。

重要规则：

- 用户原话可以作为关于“用户意图、偏好、经历陈述”的直接证据。
- assistant 回答不是外部事实源；它只能作为“当时如何回答”的记录，外部事实仍必须引用其 parent sources。
- 用户修正优先级高于旧的 assistant 推断，但不能删除旧 source；应建立 supersedes/conflicts 关系。
- 交互 source 默认可以进入 `answers/`、`indexes/interaction-index.md` 和相关 wiki 页面，但不能无限递归处理自己生成的二次摘要。
- 事实关系优先写到 claim 级别；source 级关系只表示整份资料的处理状态或批次关系。

## iCloud 同步约束

vault 项目可以放进 iCloud Drive，但必须按文件同步系统设计：

- durable data 使用普通文件：markdown、JSONL、原始媒体、PDF、压缩包。
- 所有内部引用使用相对路径，不写本机绝对路径作为长期引用。
- `raw/` 追加为主，避免多设备同时改同一个原始 source 目录。
- `logs/*.md` 追加前先读最新内容，避免覆盖其他设备刚同步的内容。
- `logs/event-ledger.jsonl` 是机器可读事件账本；多设备并发时优先用 event_id/source_id/device_hint/hash 对齐，而不是只看 markdown 日志。
- 任何本地向量库、全文索引缓存、缩略图缓存都必须可重建；不要把它们当事实源。
- 处理 iCloud 冲突副本、未下载占位文件、部分同步文件时，先标记 `partial` 或 `blocked`，不要静默生成结论。
- 大视频、电子书、压缩包可以保留在 raw，但 extract/source map 必须足够说明处理状态和缺口。

## 数据身份

每个 source 必须有稳定 ID：

```text
src-YYYYMMDD-HHMMSS-short-slug
```

每个可引用片段必须包含定位符：

```text
src-20260622-210301-app-log#L120-L155
src-20260622-210455-demo-video#t00:03:12-t00:04:08
src-20260622-210522-product-screenshot#image:original/app-error.png
src-20260622-211000-book#p42
src-20260622-211500-archive#path:logs/client/app.log#L9-L40
```

关键断言还应拥有 claim_id：

```text
clm-20260622-211500-archive-1
```

claim_id 连接 source locator、证据强度、状态和冲突关系。它是“这个断言是否仍有效”的最小单位。

## 写入边界

### Capture 阶段

只做：

- 原始资料保存。
- manifest 创建。
- source-index 和 ingest-log 更新。

不做：

- 深度摘要。
- 大规模标签推断。
- wiki 改写。

### Extract 阶段

只做：

- OCR、转写、文本抽取。
- chunk。
- source map。
- 媒体关键帧或缩略图登记。

不做：

- 长期知识综合。
- 项目结论。
- 年度总结。

### Integrate 阶段

只做：

- 标签、实体、项目、时间线、PARA、多维索引。
- wiki 页面增量更新。
- 矛盾、缺口和待确认项记录。

不做：

- 改写 raw。
- 把推断写成事实。
- 删除旧结论；旧结论被新证据挑战时标记 superseded 或 conflict。

### Query / Research / Review 阶段

只做：

- 基于 indexes/wiki/extract/raw 召回。
- 回到 raw 或 source map 校验关键断言。
- 输出引用和不确定性。
- 经用户授权把高价值答案写回 wiki。

## Wiki 不是事实源

wiki 页面必须把内容分成：

- `事实`：可引用到 source。
- `综合`：基于多个事实的整理。
- `推断`：有置信度和依据。
- `待确认`：缺数据或需要用户判断。

禁止：

- 用 wiki 页面替代 raw source。
- 在没有 source 的情况下写入“用户做过/参与过/感受到”这类个人事实。
- 把模型通识混入个人记录而不标注。

## 多维组织

PARA 是行动视图，不是唯一组织方式。

同一 source 可以同时进入：

- Project：当前正在推进的项目。
- Area：长期责任，例如健康、家庭、财务、工程能力。
- Resource：可复用主题，例如设计模式、知识管理、AI agent。
- Archive：完成、暂停或暂不活跃内容。
- Timeline：日、周、月、年、项目周期。
- Entity：人物、团队、公司、产品、代码库。
- Asset：图片、视频、音频、PDF、日志、压缩包、电子书。
- Question：被问过的问题和答案。

## 证据强度

每条重要结论标记证据强度：

- `direct`：原文、原日志、原截图、用户直接表达。
- `derived`：从 OCR、转写、extract 得出，有 source map。
- `synthesized`：多个 source 共同支持。
- `inferred`：合理推断，但证据间接。
- `unsupported`：暂无证据，只能作为问题或假设。

## 冲突处理

冲突不是覆盖旧数据，而是新增关系。

常见冲突：

- 用户更正了 assistant 的旧回答。
- 新日志推翻了旧故障判断。
- OCR/转写与原图/音视频不一致。
- 两个 source 对同一事件时间、人物、项目归属或结论不一致。
- iCloud 冲突副本导致同一 source 出现多个版本。

处理规则：

- raw source 永不删除；冲突通过 `conflicts_with`、`supersedes`、`superseded_by` 记录。
- direct evidence 优先于 inferred evidence。
- 用户 correction 对用户偏好、意图和个人记录有高优先级。
- tool_observation 对文件、日志、测试、命令结果有高优先级。
- assistant_answer 只能引用其 parent sources，不能单独推翻 raw source。
- 缺少 parent_sources 的旧 answer 只能作为 historical answer，不得作为 direct/derived/synthesized 证据。
- correction 与 decision 要拆分；一句话同时纠错和设规则时，用独立 claim 表达。
- 无法判定时写入 `indexes/conflict-index.md` 和相关 wiki 的 `待确认`，不要静默合并。

## 设计依据

- LLM Wiki：采用 raw sources、LLM-maintained markdown wiki、schema/workflow 三层思想；避免每次查询都从 raw chunks 重新拼答案。
- PARA：采用 Projects、Areas、Resources、Archives 作为行动导向视图，但不把 PARA 当成唯一分类。
- NotebookLM：借鉴 source-grounded QA、source discovery、citations、Deep Research 和 Audio/Video Overview 等以 source 为中心的体验；但保留本地 raw、长期 wiki、跨年度 timeline 和自定义 schema。
- Obsidian：借鉴 plain markdown、internal links、block/heading anchors 和 vault graph 的可移植链接思路。
- Zotero：借鉴 item metadata、collections/tags、attachments、snapshots、citation 和 bibliography 的研究资料严谨性。
- Readwise/Reader：借鉴低摩擦捕获、阅读材料汇聚、高亮和回顾，但不把 highlight 当成完整事实源。

## 反模式

- 只保存摘要，不保存原始资料。
- 只有向量库，没有可读 source map。
- 只按 PARA 文件夹搬运资料，缺少 source_id 和多维索引。
- 每次问答临时检索 raw chunks，答案不写回长期 wiki。
- 把 assistant 以前的回答当作外部事实，再次用于支持同一个结论，形成自我强化循环。
- 自动生成年度复盘但没有 timeline 覆盖范围和引用。
- 对图片、视频、压缩包只记录文件名，不记录可定位 locator。
- 对个人心情做强判断，却没有用户原文或明确行为证据。
