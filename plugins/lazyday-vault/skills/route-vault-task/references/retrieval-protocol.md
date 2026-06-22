# Retrieval And Citation Protocol

## 检索顺序

1. 明确用户意图：事实问答、时间线、资产召回、项目回顾、心情复盘、故障追踪、概念研究、输出生成。
2. 读 `wiki/index.md`、相关 `indexes/*.md` 和最近日志。
3. 读候选 wiki 页面，收集已编译知识。
4. 读对应 source manifests 和 processed extracts。
5. 对关键断言回到 raw source 或 source map 校验。
6. 检查 `claim-index.md`、`conflict-index.md`、`interaction-index.md`，确认候选结论是否被纠正、取代或仍 open。
7. 组织答案，标注事实、推断、置信度、缺口和引用。
8. 如果用户要求记录本次交互，或本次回答会改变长期 wiki，使用 `record-vault-interaction` 写入交互 source。

## 召回策略

按问题类型选择入口：

- “今天/本周/今年做了什么”：`timeline-index.md` -> `wiki/timelines/` -> source manifests -> extracts。
- “某项目发生了什么”：`wiki/projects/` -> entity/project tags -> timeline -> raw evidence。
- “找一张图片/视频/文件”：`asset-index.md` -> source manifest -> raw path -> media preview/source map。
- “用户打不开应用/日志是什么”：`tag-index.md` 或 `entity-index.md` 中的故障/产品/用户线索 -> log sources -> raw log lines -> `asset-index.md` 中同时间/同 batch 的截图、录屏、压缩包和用户描述。
- “某个概念/设计模式”：`wiki/concepts/` 和 `resources/`，必要时区分 vault 资料和模型通识。
- “我上次怎么问/你当时怎么回答/我后来纠正过什么”：`indexes/interaction-index.md` -> `indexes/conflict-index.md` -> `indexes/claim-index.md` -> interaction source -> parent sources。

## 组合召回

故障、项目复盘和研究问题经常跨多个 source。不要只返回第一个命中文本。

故障类组合策略：

1. 用产品名、用户名、错误码、时间段、项目名查 `tag-index.md`、`entity-index.md`、`timeline-index.md`。
2. 查 log source，优先 raw log locator 和 request/session id。
3. 用相同时间段、batch_id、entity、tag 查 `asset-index.md`，补截图、录屏、压缩包、用户文字描述。
4. 查 `interaction-index.md`，确认用户是否后来补充或纠正了故障背景。
5. 查 `conflict-index.md` 和 `claim-index.md`，避免引用已推翻根因。
6. 输出证据表时列出为什么每个 source 匹配。

## 引用格式

回答中的证据使用短引用，答案末尾列出来源表：

```markdown
这次应用打不开集中发生在 6 月 21 日晚的 Electron 启动阶段，核心错误是网关进程未正常退出。[S1]

**来源**
- [S1] `src-20260621-231510-openclaw-log#L88-L143` raw: `raw/2026/06/src-.../original/app.log` evidence: direct reason: gateway error lines
```

图片、视频和音频必须给原始路径和定位：

```markdown
- [S2] `src-20260622-101200-screenshot#error-dialog` raw: `.../original/screenshot.png`
- [S3] `src-20260622-140000-demo-video#t00:03:12-t00:03:45` raw: `.../original/demo.mov`
```

## 不确定性

- 找不到证据时说“当前 vault 未找到证据”，不要补造。
- 只有间接线索时写“推断”，并说明依据和缺口。
- 情绪、感想、动机等心理状态必须低调推断，除非用户原文直接表达。
- 年度总结这类大跨度输出必须列出覆盖范围和缺失月份/来源类型。

## 覆盖范围

长周期问题必须报告覆盖范围：

- 时间范围。
- 已检索的 timeline/wiki/index。
- 命中的 source 数量和类型。
- 缺失区间。
- 低证据结论。
- open conflicts、superseded claims 和被排除的旧 answer。

## 答案可沉淀

当用户的问题产生了可复用产物，例如设计模式总结、项目复盘、年度回顾、故障案例库：

1. 先回答用户问题。
2. 询问或按用户授权把本次问答记录为 interaction source。
3. 再把高价值答案写回 `wiki/questions/`、`wiki/reports/` 或相关 concept/project 页面。
4. 写回页面时保留所有引用，不把聊天结论当成原始事实。

## 防自我强化

- assistant 旧回答只能证明“当时这样回答过”，不能单独证明回答内容是真的。
- answer source 必须记录 `parent_sources`；后续引用外部事实时应回到 parent sources。
- answer source 如果缺少 `parent_sources`，或 parent sources 不可读/已失效，只能标记为 historical answer。
- 用户 correction 可以推翻旧 answer 的推断，但应保留旧 answer 并记录 superseded/conflict。
- 不要把 `answers/` 中无来源的文字再次当作 direct evidence。

## 召回资产

召回图片、文件、日志、视频片段时，不只给文字摘要，还要给：

- source_id
- raw path
- 预览/缩略图路径（如存在）
- 相关 processed extract
- 为什么匹配该查询
- 关联项目、人物、时间和标签

来源表至少包含：

```markdown
| ref | source_id | locator | raw path | evidence_strength | reason |
|---|---|---|---|---|---|
| S1 | src-... | #L88-L143 | raw/.../app.log | direct | exact error line |
```
