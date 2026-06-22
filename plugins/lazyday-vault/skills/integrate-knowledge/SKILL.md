---
name: integrate-knowledge
description: 中文 Lazyday Vault 知识整合技能。用于把 extract/chunk/source map 整合进长期知识库：打标签、识别实体、项目、人物、组织、产品、代码库、主题、情绪线索、时间线事件、PARA 视图，更新 indexes、wiki 页面、citation ledger，并记录矛盾、过期结论和待确认问题；禁止修改 raw source 或把无引用推断写成事实。
---

# 整合知识

## 目标

把可读加工层变成可召回、可复盘、可研究的长期知识层。整合层解决“这份资料和我已有知识有什么关系”的问题。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/retrieval-protocol.md`
- `../route-vault-task/references/interaction-conflict-protocol.md`（当资料涉及修正、决策、旧 answer 或冲突）

## 工作流

1. 读取 source manifest、extract、source map、已有 wiki_pages 和 indexes。
2. 抽取或确认：
   - 时间事件。
   - 项目、area、resource、archive 候选。
   - 人物、组织、产品、代码库、地点、概念。
   - 任务、决策、问题、风险、结果。
   - 情绪和感想线索。
   - 资料类型和资产类型。
3. 为每个重要事实绑定 `source_id + locator`；关键事实、推断、决策和纠错创建或更新 claim。
4. 更新 indexes：
   - `source-index.md`
   - `tag-index.md`
   - `entity-index.md`
   - `timeline-index.md`
   - `asset-index.md`
   - `claim-index.md`
   - `conflict-index.md`（如有 open/disputed/resolved claim）
   - `citation-ledger.md`
5. 更新 wiki：
   - `wiki/projects/`
   - `wiki/areas/`
   - `wiki/resources/`
   - `wiki/entities/`
   - `wiki/concepts/`
   - `wiki/timelines/`
   - `wiki/questions/` 或 `wiki/reports/`（仅当资料直接产生可沉淀问题或报告）
6. 如果新证据挑战旧结论，优先标记 claim 级 conflict 或 superseded，不直接静默覆盖。
7. 更新 manifest 的 `para`、`projects`、`areas`、`resources`、`entities`、`tags`、`wiki_pages` 和 status。
8. 追加处理日志和 `event-ledger.jsonl`。

## 情绪和个人事实

- 用户原文直接表达的心情是 `direct` 证据。
- 从行为、语气、事件密度推断的心情是 `inferred`，必须标低置信度。
- 不做心理诊断，不写人格判断。
- “我参与了什么项目”“今年做了什么”必须进入 timeline/project 页，并绑定 source。

## Wiki 更新规则

页面结构推荐：

```markdown
# Title

---
type:
tags:
source_count:
sources:
updated_at:
confidence:
---

## 事实

## 综合

## 推断

## 待确认

## 相关链接

## 来源
```

## 输出格式

```markdown
**整合结果**
- source_id:
- indexes:
- wiki pages:
- manifest updates:

**新增知识**
- 事实：
- 时间线：
- 项目/领域：
- 实体/概念：
- 标签：

**质量控制**
- 引用覆盖：
- claim 覆盖：
- 冲突/过期：
- 待确认：
```

## iCloud 同步注意

- 更新 wiki/index/log 前先读最新文件内容，避免覆盖其他设备刚同步的更新。
- 发现 iCloud 冲突副本时先记录到 `logs/maintenance-log.md` 或输出维护建议，不要把冲突内容自动合并成事实。
- 内部链接优先使用相对 Markdown 链接；Obsidian block reference 只能作为增强，不作为唯一引用。
- 批量重写 wiki 或 indexes 前必须确认；默认做小范围增量更新。
