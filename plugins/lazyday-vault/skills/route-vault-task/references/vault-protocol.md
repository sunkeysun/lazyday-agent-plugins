# Lazyday Vault 协议

本协议定义文件结构和写入规则。架构设计、分层依据和反模式见 `architecture.md`；处理不同资料类型见 `source-types.md`；检索和引用见 `retrieval-protocol.md`。

## 设计原则

1. 原始资料不可变：raw source 是事实来源，不能被摘要、OCR、转写或 wiki 页面替代。
2. 加工层可再生成：extract、chunk、tag、entity、timeline、wiki 都可以重跑，但必须记录生成时间、方法和来源。
3. 引用优先于记忆：任何回答、总结、研究和推断都要能指回 source ID、原始路径和定位符。
4. 行动导向加链接导向：PARA 负责当前行动组织，wiki/link graph 负责长期关联，timeline 负责人生和项目回顾。
5. 增量维护：新资料进入时更新相关 wiki 页面、索引和日志；不要只在查询时临时 RAG。

## 默认目录

```text
<vault-project>/
├── .lazyday/
│   └── vault/
│       └── requirements/
├── inbox/
├── raw/
│   └── YYYY/
│       └── MM/
│           └── <source_id>/
│               ├── original/
│               └── manifest.md
├── processed/
│   ├── extracts/
│   ├── chunks/
│   ├── media/
│   └── source-maps/
├── wiki/
│   ├── index.md
│   ├── projects/
│   ├── areas/
│   ├── resources/
│   ├── archives/
│   ├── entities/
│   ├── concepts/
│   ├── timelines/
│   ├── questions/
│   └── reports/
├── answers/
│   ├── questions/
│   └── research/
├── indexes/
│   ├── source-index.md
│   ├── tag-index.md
│   ├── entity-index.md
│   ├── timeline-index.md
│   ├── asset-index.md
│   ├── interaction-index.md
│   ├── conflict-index.md
│   ├── claim-index.md
│   └── citation-ledger.md
└── logs/
    ├── ingest-log.md
    ├── process-log.md
    ├── query-log.md
    ├── research-log.md
    ├── maintenance-log.md
    └── event-ledger.jsonl
```

当前项目根目录就是个人知识库数据根。`.lazyday/vault/requirements/` 只用于可选的跨会话需求协作产物，不承载知识库事实数据。

`answers/` 用于沉淀高价值问答和研究中间产物；稳定后的内容可以再整合进 `wiki/questions/`、`wiki/reports/` 或相关项目/概念页。

## Source ID

使用稳定、可排序、避免泄露内容的 ID：

```text
src-YYYYMMDD-HHMMSS-<short-slug>
```

同一批资料的多个文件可以使用：

```text
src-YYYYMMDD-HHMMSS-<short-slug>-part001
```

多文件输入先判断关系，不要机械合并：

| 输入关系 | Source 建模 | 示例 |
|---|---|---|
| 同一事件的不同证据 | 一个 `batch_id`，多个独立 child source | 用户同时给截图、日志、录屏，用于同一故障 |
| 一个容器文件 | 容器本身一个 source，内部清单进入 extract/source map | zip、tar、epub |
| 一个逻辑文档被拆成多文件 | `part001`、`part002`，共享 `batch_id` | 扫描件多张图片组成一份合同 |
| 互不相关的一组文件 | 多个独立 source，不共享结论 | 用户拖入一批杂项资料 |
| 混合输入且关系不明 | 创建 batch source 或先询问，避免错误关联 | 视频加压缩包但未说明用途 |

`batch_id` 用于检索关联，不代表这些 source 的结论相互证明。每个 child source 仍必须有自己的 manifest、raw path、hash 和 status。

## Manifest

每个 raw source 必须有 `manifest.md`：

```markdown
# <source_id>

- source_id:
- title:
- captured_at:
- batch_id:
- part_id:
- source_type: text | file | image | audio | video | archive | ebook | web | log | interaction | mixed
- original_location:
- raw_path:
- sha256:
- size:
- mime_type:
- language:
- created_or_observed_at:
- privacy: private | sensitive | public | unknown
- para:
- projects:
- areas:
- resources:
- entities:
- tags:
- status: captured | processed | partial | blocked | archived
- availability: local | cloud-placeholder | missing | external-only | unknown
- raw_downloaded: true | false | unknown
- hash_verified_at:
- sync_conflict: none | detected | resolved | unknown
- rebuild_required: none | extract | indexes | wiki | all
- source_role:
- parent_sources:
- derived_from:
- supersedes:
- superseded_by:
- conflicts_with:
- claim_ids:
- supersedes_claims:
- conflicts_with_claims:
- conflict_status: none | open | resolved | superseded
- processed_outputs:
- wiki_pages:
- citation_examples:
- notes:
```

`raw_path` 必须使用相对 vault 根目录的路径。`original_location` 可记录用户给出的原始位置，但不得作为唯一长期引用；如果它包含本机私有绝对路径，输出时要谨慎展示。

状态含义：

- `captured`：raw source 和 manifest 已建立，但加工层未完成。
- `processed`：extract/source map/index/wiki 达到当前资料类型的可用标准。
- `partial`：已完成部分处理，但存在未下载文件、缺转写、缺 OCR、压缩包未解等明确缺口。
- `blocked`：因权限、缺文件、敏感外部处理未授权、文件损坏或 iCloud 占位导致不能继续。
- `archived`：不再活跃，但 raw 和引用仍可用。

可用性含义：

- `local`：文件已在本机可读，可计算 hash。
- `cloud-placeholder`：iCloud 或同步盘显示占位，不能当作完整 raw。
- `missing`：manifest 指向的 raw path 不存在。
- `external-only`：仅有 URL 或外部系统位置，尚未抓取本地副本。
- `unknown`：尚未验证。

交互类 source 额外建议记录：

```markdown
- interaction_kind: question | answer | correction | feedback | decision | research-session | retrospective
- participants:
- thread_id:
- turn_range:
- user_intent:
- answer_path:
- parent_sources:
- derived_from:
- writes_to:
```

`parent_sources` 与 `derived_from` 不同：

- `parent_sources` 只放支持事实断言的证据 source。assistant answer 不能把自己放进自己的事实父证据。
- `derived_from` 记录处理链或交互链，例如“这个决策由某次问答引出”。
- 旧 answer 只有在回答“当时怎么回答过”时才作为事实证据；回答 answer 内容是否为真时，必须跳回它的 `parent_sources`。

## Claim ID

重要事实、推断、决策和纠错必须尽量 claim 化，避免 source 级冲突过度失效。

```text
clm-YYYYMMDD-HHMMSS-<source-slug>-<n>
```

claim 最小字段：

```markdown
- claim_id:
- source_id:
- locator:
- applies_to_locator:
- claim_type: fact | inference | decision | correction | preference | tool-observation
- statement:
- evidence_strength: direct | derived | synthesized | inferred | unsupported
- status: active | superseded | disputed | resolved | retracted
- parent_sources:
- supersedes_claims:
- conflicts_with_claims:
- confidence: high | medium | low
- updated_at:
```

`indexes/claim-index.md` 是 claim 的导航表，不替代 manifest。`indexes/conflict-index.md` 记录 open/disputed/resolved 的冲突线程。

## 加工产物

- `processed/extracts/<source_id>.md`：文本抽取、OCR、转写或人工输入的可读内容。
- `processed/chunks/<source_id>.jsonl`：可选切片，每行带 chunk_id、locator、text、tags。
- `processed/source-maps/<source_id>.md`：说明 extract/chunk 与原始文件页码、时间戳、帧、路径或行号的对应关系。
- `processed/media/<source_id>/`：缩略图、关键帧、音频转写片段等可再生成资产。

加工层的每个事实必须带引用：

```text
source: src-20260622-210301-app-log#L120-L155
source: src-20260622-210455-demo-video#t00:03:12-t00:04:08
source: src-20260622-210522-product-screenshot#image:original/app-error.png
```

## Wiki 页面

wiki 页面是 LLM 维护层，不是原始事实层。页面 frontmatter 推荐：

```yaml
title:
type: project | area | resource | archive | entity | concept | timeline | report | question
tags:
source_count:
sources:
updated_at:
confidence: high | medium | low
```

正文必须区分：

- `事实`：来自 source 的可引用内容。
- `推断`：基于多个事实的判断，标注置信度。
- `待确认`：需要更多资料或用户确认。
- `相关链接`：其他 wiki 页面。

页面必须优先使用标准 Markdown 链接以保持跨工具可移植；需要 Obsidian 专用 block reference 时，必须同时保留普通 Markdown 可读定位。

## Index 文件职责

- `source-index.md`：source_id、标题、类型、时间、状态、raw path、processed outputs。
- `tag-index.md`：标签到 source/wiki 的映射。
- `entity-index.md`：人物、组织、产品、代码库、地点、概念实体。
- `timeline-index.md`：日/周/月/年/项目周期入口。
- `asset-index.md`：图片、视频、音频、PDF、压缩包、电子书和日志资产。
- `interaction-index.md`：用户问题、回答、反馈、修正、决策和写回记录。
- `conflict-index.md`：未解决冲突、被推翻结论、iCloud 冲突副本和待确认事项。
- `claim-index.md`：关键 claim、证据强度、状态、定位符和 claim 级 supersedes/conflicts。
- `citation-ledger.md`：报告、问答、wiki 关键结论到引用的账本。

## 日志

所有 ingest、process、query、research、interaction、maintenance 都追加到对应日志。日志条目统一前缀：

```markdown
## [YYYY-MM-DD HH:mm] ingest | <source_id> | <title>
```

`logs/*.md` 是给人读的摘要日志。`logs/event-ledger.jsonl` 是可重建和并发恢复用的机器账本，每行一个事件：

```json
{"event_id":"evt-20260623-101500-abc123","event_type":"ingest","source_id":"src-20260623-101455-app-log","device_hint":"macbook","created_at":"2026-06-23T10:15:00+08:00","paths":["raw/2026/06/src-.../manifest.md"],"status":"ok","notes":"captured log source"}
```

追加事件前先读文件尾部，生成唯一 `event_id`。如果发现同一 source 在不同设备产生相互冲突的事件，不覆盖，记录 `sync_conflict: detected` 并写入 `conflict-index.md`。

## 模板

`source-index.md` 条目：

```markdown
| source_id | title | type | observed_at | status | raw path | outputs | tags |
|---|---|---|---|---|---|---|---|
| src-... | App crash log | log | 2026-06-22 21:03 | captured | raw/2026/06/src-.../original/app.log | extract pending | app, crash |
```

`asset-index.md` 条目：

```markdown
| source_id | asset_type | locator | raw path | preview | related sources | reason |
|---|---|---|---|---|---|---|
| src-... | image | #image:original/error.png | raw/.../original/error.png | processed/media/src-.../thumb.png | src-...-log | error dialog screenshot |
```

`ingest-log.md` 条目：

```markdown
## [2026-06-23 10:15] ingest | src-20260623-101455-app-log | App crash log
- status: captured
- raw: raw/2026/06/src-20260623-101455-app-log/original/app.log
- availability: local
- next: extract-source
```

`claim-index.md` 条目：

```markdown
| claim_id | statement | source | locator | evidence | status | related |
|---|---|---|---|---|---|---|
| clm-...-1 | App failed during gateway startup | src-... | #L88-L143 | direct | active | conflicts: clm-... |
```

## Rebuild Protocol

索引和 wiki 可重建，但 raw 不可丢。重建顺序：

1. 扫描 `raw/**/manifest.md`，生成 source inventory。
2. 校验 `raw_path`、availability、hash、status；缺文件先标记，不生成事实。
3. 扫描 `processed/extracts/`、`processed/source-maps/`、`processed/chunks/`，回填 processed outputs。
4. 重建 `source-index.md`、`asset-index.md`、`interaction-index.md`、`claim-index.md`。
5. 从 claim 和 source map 重建 `tag-index.md`、`entity-index.md`、`timeline-index.md`。
6. 检查 wiki frontmatter 的 `sources` 和正文引用，更新缺失索引，但不要无确认大规模重写 wiki 正文。
7. 重建 `citation-ledger.md`，标出无来源答案、无 parent_sources 的旧 answer 和 open conflicts。
8. 追加 `maintenance-log.md` 和 `event-ledger.jsonl`。

通过标准：

- 每个 source 有 manifest、raw path、status 和 availability。
- 每个关键 wiki/report/answer claim 有 source locator。
- `interaction-index.md` 与 `conflict-index.md` 不遗漏 correction、decision、open conflict。
- 无来源 answer 不被升级为事实证据。

## 写入边界

允许自动写入：

- 新 source 的 raw 目录和 manifest。
- 由该 source 派生的 processed 文件。
- 相关 wiki/index/log 的增量更新。
- 用户明确要求记录的交互、回答、修正和决策。

需要确认：

- 删除或移动 raw source。
- 批量重命名 source_id。
- 批量重写 wiki。
- 调用外部服务处理敏感资料。
- 把 vault 同步到外部产品或远程仓库。
- 自动记录所有对话全文，除非用户明确开启该工作方式。

## Obsidian 边界

可以把整个 vault 作为 Obsidian vault 打开，也可以只把 `wiki/` 当作主要阅读入口。不要让 Obsidian 约定破坏 source 协议：

- `.obsidian/` 属于工具配置，不是事实源。
- `raw/` 可被 Obsidian 看到，但不要依赖 Obsidian 链接作为唯一引用。
- 大型媒体、压缩包、临时缓存和向量索引应保持可重建或外部工具可忽略。
- block reference 可以作为增强，必须同时保留普通 Markdown 链接、`source_id` 和 locator。
