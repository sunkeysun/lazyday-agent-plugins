---
name: maintain-vault
description: 中文 Lazyday Vault 维护技能。用于检查、整理、修复或重建个人知识库的目录结构、source manifest、索引、wiki 链接、引用覆盖、孤儿页、重复 source、断链、过期结论、矛盾内容、未处理资料和日志；默认只做安全增量修复，高风险批量改写、删除或移动 raw source 前必须确认。
---

# Vault 维护

## 目标

保持 vault 可检索、可追溯、可持续增长。维护不是美化目录，而是降低未来召回和引用失败的概率。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/interaction-conflict-protocol.md`

## 检查项

- raw source 是否都有 manifest。
- manifest 是否包含 source_id、raw_path、sha256、source_type、status。
- processed outputs 是否能追溯 raw source。
- wiki 页面是否有 sources、updated_at、confidence。
- indexes 是否覆盖新增 source、tag、entity、timeline、asset。
- citation-ledger 是否覆盖关键报告和问答。
- interaction-index 是否覆盖被保存的问答、修正、反馈和决策。
- conflict-index 是否列出 open conflict、superseded answer、被用户修正的旧结论。
- claim-index 是否覆盖关键事实、推断、纠错、决策和过期 claim。
- event-ledger.jsonl 是否为合法 JSONL，事件是否能对应 source/log/wiki/index 变更。
- 是否有孤儿 wiki 页、断链、重复 source、矛盾事实、过期页面。
- 是否有 captured 但未 processed 的资料。
- 是否有敏感资料被写入不该公开的摘要或日志。
- iCloud 冲突副本、未下载占位文件、部分同步文件是否被误标为完整资料。

## 工作流

1. 读取 vault 协议、交互冲突协议和当前目录。
2. 生成 health report。
3. 区分可自动修复和需确认修复：
   - 可自动：补 index、补日志、标记待处理、修复明显断链、把无索引的 interaction source 加入 interaction-index。
   - 需确认：删除、移动 raw、批量重命名、批量重写 wiki、外部同步、清理 iCloud 冲突副本。
4. 执行已授权的最小修复。
5. 更新 `logs/maintenance-log.md` 和 `logs/event-ledger.jsonl`。
6. 输出修复清单、未修复问题和下一步建议。

## 重建索引

用户要求“重建索引/修复索引/校验 vault”时，按 `vault-protocol.md` 的 Rebuild Protocol 执行：

1. 从 `raw/**/manifest.md` 建立 source inventory。
2. 校验 raw path、availability、hash、status。
3. 扫描 processed outputs 和 source maps。
4. 重建 source、asset、interaction、claim 索引。
5. 从 source/claim/source map 重建 tag、entity、timeline 索引。
6. 检查 wiki/report/answer 引用覆盖。
7. 标记无 parent_sources 的旧 answer、open conflict、iCloud 冲突副本。

未经确认不要大规模重写 wiki 正文；先输出 diff 级计划或修复清单。

## Obsidian 和 iCloud

- `.obsidian/` 只当工具配置，不作为事实源。
- 发现冲突副本时作为独立 source 或 conflict 线程处理，不删除、不静默合并。
- 未下载占位文件应标记 `availability: cloud-placeholder`。
- 本地向量库、缩略图缓存和临时转码文件可清理或重建，但不能替代 raw/source map。

## 输出格式

```markdown
**健康状态**
- 总体：
- raw:
- processed:
- wiki:
- indexes:
- citations:

**已修复**

**需要确认**

**剩余风险**

**下一步**
```
