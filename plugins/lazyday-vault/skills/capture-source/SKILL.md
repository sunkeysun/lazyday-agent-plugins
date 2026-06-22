---
name: capture-source
description: 中文 Lazyday Vault 原始资料捕获技能。用于把一句话、聊天片段、文件、图片、音频、视频、压缩包、电子书、日志、网页链接、项目资料等任意输入保存到个人 vault；必须全量保留 raw source，创建 source manifest，计算或记录原始路径/hash/类型/隐私/时间，并为后续预处理、打标、关联、检索和引用建立稳定 source_id。
---

# 捕获资料

## 目标

把任意输入安全保存为可追溯 source。捕获阶段只做最小必要处理：保留原始资料、记录元数据、建立索引入口、安排后续加工。不要在捕获阶段用摘要替代原文。

## 读取协议

先读取 `../route-vault-task/references/vault-protocol.md`。涉及图片、视频、压缩包、电子书、日志或敏感资料时，再读取 `../route-vault-task/references/source-types.md`。

## 工作流

1. 确定 vault 根目录，默认当前项目根目录；该目录可以位于 iCloud Drive。
2. 判断输入类型和隐私级别。
3. 生成 `source_id`。
4. 判断多文件关系：独立 source、共享 `batch_id` 的 child sources、容器 source、或 `part001` 分片。
5. 创建 `raw/YYYY/MM/<source_id>/original/`。
6. 保留原始资料：
   - 用户直接输入文本：写入 `original/input.md`，保持原文。
   - 本地文件：复制到 `original/`，不要修改原文件。
   - 多文件或压缩包：保留容器文件或文件清单，必要时先问是否复制/解压。
   - URL：先记录 URL；只有用户允许时抓取内容。
7. 创建 `manifest.md`，记录 raw path、来源、hash、类型、隐私、availability、batch_id、初步 PARA、标签和状态。
8. 更新 `indexes/source-index.md`、必要时更新 `indexes/asset-index.md`，追加 `logs/ingest-log.md` 和 `logs/event-ledger.jsonl`。
9. 输出 source_id、raw path、后续建议 skill。

## iCloud 同步注意

- durable path 使用相对 vault 根目录的路径，例如 `raw/2026/06/...`。
- `original_location` 可以记录用户提供的原始位置，但不要把本机绝对路径当成唯一引用。
- 复制大文件前确认文件已完整下载，不要对 iCloud 占位文件生成完成状态。
- 发现 iCloud 冲突副本时，把冲突文件作为独立 source 或标记 `blocked`，不要静默覆盖。
- 同一 source 目录写入前先确认目录不存在；若存在，读取 manifest 后再决定追加或停止。
- markdown 日志用于人读，`event-ledger.jsonl` 用于重建和冲突恢复；两者都追加，不覆盖。

## 最小打标

捕获阶段只做低风险初步标签：

- 时间：captured_at、created_or_observed_at。
- 类型：text、file、image、audio、video、archive、ebook、web、log、mixed。
- 领域：work、life、project、learning、health、finance、relationship、engineering、unknown。
- PARA 候选：project、area、resource、archive、unknown。
- 隐私：private、sensitive、public、unknown。

复杂实体、主题、情绪、时间线和交叉链接交给 `integrate-knowledge`；如果用户只说“继续处理”，交给 `process-source` 协调。

## 确认门

先问用户：

- 是否允许复制超大文件、目录或压缩包。
- 是否允许解压归档。
- 是否允许调用外部 OCR、转写、网页抓取或云模型。
- 是否处理疑似敏感资料。

## 输出格式

```markdown
**捕获结果**
- source_id:
- raw path:
- manifest:
- source type:
- privacy:

**已更新**
- source-index:
- ingest-log:

**下一步**
- 推荐 skill:
- 加工建议:
- 需要确认:
```
