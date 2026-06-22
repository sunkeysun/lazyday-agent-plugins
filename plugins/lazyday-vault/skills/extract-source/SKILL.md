---
name: extract-source
description: 中文 Lazyday Vault 抽取技能。用于对已捕获 raw source 进行文本抽取、OCR 结果整理、音视频转写整理、PDF/电子书章节页码抽取、压缩包清单、日志时间线初提取、chunk 和 source map 建立；只产出可再生成的 processed/extracts、chunks、media、source-maps，不负责长期标签、PARA 分类、wiki 综合或研究结论。
---

# 抽取资料

## 目标

把 raw source 转换为可读、可切片、可定位的加工层，同时保持每个片段都能回到原始资料。抽取层解决“能不能读、能不能定位、能不能引用”的问题。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/source-types.md`

## 工作流

1. 读取 source manifest，确认 raw path、source_type、privacy、status。
2. 校验 raw source 存在；必要时计算或核对 hash。
3. 按类型抽取：
   - text/file：保留原文结构、行号或段落号。
   - PDF/ebook：抽取目录、章节、页码、标题、正文和图片说明。
   - image：记录尺寸、EXIF、OCR、可见文本、视觉描述和区域定位。
   - audio/video：记录时长、转写、时间戳、说话人线索、关键帧或片段。
   - archive：记录内部文件清单、路径、大小、hash、可疑项和解压状态。
   - log：保留行号、时间戳、错误边界、请求 ID 和堆栈片段。
4. 写入或更新：
   - `processed/extracts/<source_id>.md`
   - `processed/chunks/<source_id>.jsonl`（需要时）
   - `processed/source-maps/<source_id>.md`
   - `processed/media/<source_id>/`（需要时）
5. 更新 manifest 的 `processed_outputs` 和 `status`。
6. 追加 `logs/process-log.md` 和 `logs/event-ledger.jsonl`。
7. 输出下一步 `integrate-knowledge` 的交接摘要。

## 边界

允许：

- 生成可再处理的 extract、chunk、source map、media derivative。
- 标记明显的技术元数据和低风险结构标签。

禁止：

- 删除、移动或改写 raw source。
- 生成长期结论、项目复盘或情绪判断。
- 把 OCR/转写不确定内容当作事实。
- 调用外部 OCR/转写服务处理敏感资料，除非用户明确授权。

## iCloud 同步注意

- 抽取前确认 raw 文件已完整可读；如果文件未下载或正在同步，标记 `partial` 或 `blocked`。
- source map 使用相对路径和 locator，不依赖本机绝对路径。
- 大型媒体的缩略图、关键帧和临时转码文件必须标记为可重建。
- 不要把本地-only 向量库或临时索引当作抽取结果的唯一副本。

## 输出格式

```markdown
**抽取结果**
- source_id:
- source_type:
- extract:
- chunks:
- source_map:
- media:
- status:

**定位能力**
- 支持的 locator:
- 引用样例:

**下一步**
- 推荐 skill:
- 可交给整合层的摘要:
- 未处理/需确认:
```
