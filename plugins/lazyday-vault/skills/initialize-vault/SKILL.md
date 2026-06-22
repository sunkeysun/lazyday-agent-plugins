---
name: initialize-vault
description: 中文 Lazyday Vault 初始化技能。用于在当前项目根目录幂等创建或修复个人知识库骨架，适合用户说“初始化 vault/创建知识库目录/把这个项目作为我的知识库/准备 iCloud 同步 vault/修复缺失基础目录”；必须建立 raw、processed、wiki、indexes、answers、logs、基础索引、事件账本和 README/导航提示，不处理具体资料，不删除已有内容。
---

# 初始化 Vault

## 目标

把当前项目根目录准备成 Lazyday Vault 数据根。初始化只创建缺失结构和空白索引，不导入资料、不改写已有笔记、不删除内容。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`

## 工作流

1. 确认当前项目根目录就是目标 vault 根；如果用户指定其他路径，先说明将写入的路径。
2. 扫描已有目录和文件，区分已存在、缺失、冲突、疑似非 vault 项目。
3. 幂等创建缺失目录：
   - `inbox/`
   - `raw/`
   - `processed/extracts/`
   - `processed/chunks/`
   - `processed/media/`
   - `processed/source-maps/`
   - `wiki/index.md`
   - `wiki/projects/`
   - `wiki/areas/`
   - `wiki/resources/`
   - `wiki/archives/`
   - `wiki/entities/`
   - `wiki/concepts/`
   - `wiki/timelines/`
   - `wiki/questions/`
   - `wiki/reports/`
   - `answers/questions/`
   - `answers/research/`
   - `indexes/`
   - `logs/`
4. 创建缺失基础索引：
   - `indexes/source-index.md`
   - `indexes/tag-index.md`
   - `indexes/entity-index.md`
   - `indexes/timeline-index.md`
   - `indexes/asset-index.md`
   - `indexes/interaction-index.md`
   - `indexes/conflict-index.md`
   - `indexes/claim-index.md`
   - `indexes/citation-ledger.md`
5. 创建缺失日志：
   - `logs/ingest-log.md`
   - `logs/process-log.md`
   - `logs/query-log.md`
   - `logs/research-log.md`
   - `logs/maintenance-log.md`
   - `logs/event-ledger.jsonl`
6. 追加初始化事件到 `logs/event-ledger.jsonl`，并在 `logs/maintenance-log.md` 记录摘要。
7. 输出初始化报告：已存在、已创建、跳过、冲突、下一步。

## 初始文件内容

`wiki/index.md` 至少包含：

```markdown
# Vault Index

## Projects

## Areas

## Resources

## Archives

## Timelines

## Reports
```

索引文件至少包含标题、用途和空表头。不要写虚假示例数据。

`logs/event-ledger.jsonl` 可以为空；如果写初始化事件，每行必须是合法 JSON。

## iCloud 和 Obsidian

- 所有 durable 文件使用相对路径和普通 Markdown/JSONL。
- `.obsidian/` 如已存在，不读取或改写它；如不存在，不主动创建。
- 如果检测到 iCloud 冲突副本，只记录到初始化报告，不合并、不删除。
- 如果检测到未下载占位文件，把后续处理标为待确认，不生成完整状态。

## 确认门

先问用户：

- 目标路径不像空项目或 vault，且初始化可能混入现有业务仓库。
- 用户要求移动、删除、重命名已有文件。
- 用户要求创建 Obsidian 配置、外部同步配置、向量库或自动化脚本。

## 输出格式

```markdown
**初始化结果**
- vault root:
- 已存在:
- 已创建:
- 已跳过:
- 冲突/异常:

**基础索引**
- source-index:
- claim-index:
- citation-ledger:

**下一步**
- 推荐 skill:
- 建议:
- 需要确认:
```
