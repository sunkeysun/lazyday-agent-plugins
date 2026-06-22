---
name: process-source
description: 中文 Lazyday Vault 资料处理协调技能。用于用户泛泛要求“处理/加工/入库后继续处理这份资料”但未区分抽取与整合阶段时，先检查 source 状态，再按需串联 extract-source 和 integrate-knowledge；确保 raw source、extract、source map、tags、indexes、wiki 和 logs 的处理顺序正确。不要把它当作单一大而全加工层；具体抽取交给 extract-source，知识整合交给 integrate-knowledge。
---

# 处理资料

## 目标

协调 source 从 raw 到可检索知识层的阶段推进。该 skill 是调度层，不直接替代 `extract-source` 或 `integrate-knowledge` 的职责。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/source-types.md`

## 工作流

1. 先判断输入是否已经有 source manifest：
   - 如果用户给的是新文字、文件、图片、视频、压缩包、电子书、日志或 URL，先交给 `capture-source`，不要跳过 raw 层直接抽取。
   - 如果已有 `source_id` 或 manifest，再继续本工作流。
2. 读取 source manifest、raw path、processed outputs、wiki_pages 和 status。
3. 判断当前阶段：
   - 只有 raw，没有 extract/source map：下一步是 `extract-source`。
   - 已有 extract/source map，但缺 tags/index/wiki：下一步是 `integrate-knowledge`。
   - 两层都已有但状态 partial/blocked：先列出阻塞原因和最小补救动作。
4. 检查确认门：外部 OCR/转写、解压、敏感数据、超大文件、批量处理。
5. 只执行用户授权且当前阶段允许的最小写入。
6. 每阶段完成后更新 manifest status、processed_outputs、wiki_pages、logs 和 `event-ledger.jsonl`。
7. 输出阶段状态、下一步 skill 和未处理缺口。

## 分层要求

- raw source 是事实层。
- extract/chunk/source map 是 L2/L3 加工定位层。
- indexes 是 L4 导航层。
- wiki 是 L5 综合层，必须区分事实、推断和待确认。
- answers/reports 是 L6 输出沉淀层。

## 打标维度

整合阶段至少考虑：

- 时间：日期、时间段、周期。
- 行动：做了什么、决定了什么、后续动作。
- 项目：参与项目、客户、产品、代码库、任务。
- 人和组织：人物、团队、公司。
- 情绪和感想：只在证据足够时低调标注。
- 主题：技术、产品、生活、健康、财务、学习。
- 资料类型：log、meeting、note、screenshot、book、article、video。
- 证据强度：direct、derived、synthesized、inferred、unsupported。

## 输出格式

```markdown
**处理状态**
- source_id:
- 当前阶段：
- 已完成层级：
- 缺失层级：
- 下一步 skill：

**本次动作**
- 已执行：
- 已写入：
- 未执行：

**证据与缺口**
- 引用样例：
- 待确认：
- 未处理内容：
```
