# AGENTS.md - Lazyday Vault 目标知识库规则

本文件应复制到目标 vault 项目根目录，约束所有 AI agent 在该仓库内的知识库操作。

目标：确保个人知识库中的资料捕获、加工、检索、问答、复盘、研究、交互记录和维护任务 100% 进入 Lazyday Vault skill 工作流；任何 agent 都不得绕过 source 协议、证据协议和冲突协议直接写知识库事实。

一句话压缩版：先识别是否是知识库任务；是知识库任务必须先用 `route-vault-task` 或明确的 Lazyday Vault skill；raw 全量保留；加工层可重建；wiki 不是事实源；回答必须有 source 引用；交互也可入库；冲突只追加关系不覆盖；iCloud 冲突不静默合并；不能验证就不能写成事实。

---

## 0. 适用范围

本仓库是 Lazyday Vault 数据仓库，不是普通代码仓库。默认当前项目根目录就是 vault root。

核心目录：

```text
inbox/
raw/
processed/
wiki/
indexes/
answers/
logs/
.lazyday/vault/requirements/
```

目录职责：

- `inbox/`：临时暂存区。
- `raw/`：原始资料和 source manifest，事实源，追加为主。
- `processed/`：extract、chunk、media derivative、source map，可重建。
- `indexes/`：source、tag、entity、timeline、asset、interaction、claim、conflict、citation 导航。
- `wiki/`：LLM 维护的长期知识层，必须带引用，不是事实源。
- `answers/`：高价值问答和研究过程/报告沉淀。
- `logs/`：人类可读日志和 `event-ledger.jsonl` 事件账本。
- `.lazyday/vault/requirements/`：可选 agent 协作产物，不承载知识库事实。

## 1. 规则优先级

1. 系统级安全和平台规则。
2. 用户当前任务中的明确指令。
3. 本仓库内更近目录的 `AGENTS.md`。
4. 本文件。
5. Lazyday Vault skill 和 reference 协议。
6. 模型通用经验。

若用户明确要求“只分析 / 不改 / 先设计 / review”，保持只读，不写入 vault。

若用户明确要求“保存 / 入库 / 处理 / 生成 / 更新 / 记录 / 初始化 / 修复”，可以进入写入流程，但必须满足本文件的 skill 路由和确认门。

## 2. 最高强制规则

### 2.1 知识库任务必须调用 Lazyday Vault skill

只要请求涉及以下任一内容，必须使用 Lazyday Vault skill：

- 保存、入库、捕获、记录任何资料。
- 处理文件、图片、视频、音频、压缩包、电子书、PDF、网页、日志。
- 抽取 OCR、转写、正文、chunk、source map。
- 打标签、分类、PARA、项目、人物、时间线、实体、概念、情绪。
- 更新 `raw/`、`processed/`、`wiki/`、`indexes/`、`answers/`、`logs/`。
- 基于 vault 回答问题、召回图片/文本/日志/文件/视频片段。
- 生成日报、周报、月报、年报、项目回顾、心情和感想复盘。
- 做 NotebookLM 式深入研究、证据地图、专题报告。
- 记录用户问答、反馈、修正、确认、决策。
- 检查、修复、重建、去重、处理 iCloud 冲突。

如果用户没有明确指定 skill，必须先使用 `route-vault-task`。如果用户明确指定子 skill，可以直接进入该 skill，但仍要遵守本文件的确认门和证据协议。

如果当前运行环境无法使用 Lazyday Vault skill，禁止自行模拟写入知识库。必须停止并说明：无法保证 vault 协议准确执行，需要安装或启用 `lazyday-vault` 后继续。

### 2.2 禁止绕过 route

除非用户明确点名某个 Lazyday Vault 子 skill，否则不得直接选择 `capture-source`、`answer-vault-question`、`review-life-log` 等子 skill。

正确入口：

- Codex：使用 `$route-vault-task` 或用户指定的 `$<vault-skill>`。
- Claude Code：使用 `/lazyday-vault:route-vault-task` 或用户指定的 `/lazyday-vault:<skill>`。
- 其他 agent：必须按本文件的路由矩阵等价执行，不能跳过分类判断。

### 2.3 原始资料不可替代

禁止用摘要、OCR、转写、wiki、answer 或向量库替代 raw source。

每个 source 必须有：

- `source_id`
- `raw_path`
- `manifest.md`
- `source_type`
- `status`
- `availability`
- 原始定位或原始文件

### 2.4 没有引用，不得写事实

任何关于用户经历、项目参与、心情、决策、故障、日志、文件内容、图片内容、研究结论的事实性写入，必须绑定：

```text
source_id + locator + raw_path
```

无法定位到 source 时，只能写为 `待确认`、`unsupported` 或问题，不能写入事实段。

### 2.5 旧 answer 不是事实源

assistant 旧回答只能证明“当时这样回答过”。除非问题本身是在问旧回答内容，否则不得把旧 answer 作为事实证据。

引用旧 answer 中的事实时，必须跳回它的 `parent_sources`。缺少 `parent_sources` 的旧 answer 只能标记为 `historical answer`。

## 3. Skill 路由矩阵

| 请求类型 | 必须使用的 skill | 允许写入 | 必读协议 |
|---|---|---|---|
| 初始化 vault、创建目录、准备 iCloud 项目 | `initialize-vault` | 缺失目录、空索引、日志骨架 | `architecture.md`、`vault-protocol.md` |
| 保存一句话、文件、图片、视频、压缩包、电子书、日志、URL | `capture-source` | `raw/`、manifest、source-index、ingest-log、event-ledger | `vault-protocol.md`，特殊类型读 `source-types.md` |
| 已捕获 source 的 OCR、转写、正文、chunk、source map | `extract-source` | `processed/`、manifest outputs、process-log、event-ledger | `architecture.md`、`vault-protocol.md`、`source-types.md` |
| 打标、实体、项目、时间线、PARA、wiki、索引 | `integrate-knowledge` | indexes、wiki、claim、citation、manifest metadata | `architecture.md`、`vault-protocol.md`、`retrieval-protocol.md` |
| 用户泛泛说“处理这份资料” | `process-source`；新资料先 `capture-source` | 按阶段最小写入 | `architecture.md`、`vault-protocol.md`、`source-types.md` |
| 基于资料回答、召回图片/日志/文件/视频 | `answer-vault-question` | 默认不写；用户授权才写 answer/interaction | `retrieval-protocol.md`，冲突场景读 `interaction-conflict-protocol.md` |
| 深入研究、多源报告、NotebookLM 式分析 | `vault-deep-research` | 用户授权后写 `answers/research/`、`wiki/reports/` | `retrieval-protocol.md`、`vault-protocol.md`、`interaction-conflict-protocol.md` |
| 日报、周报、年报、项目回顾、心情复盘 | `review-life-log` | 用户授权后写 reports/timelines | `retrieval-protocol.md`、`interaction-conflict-protocol.md`、`vault-protocol.md` |
| 记录问答、反馈、修正、决策 | `record-vault-interaction` | interaction source、claim、interaction-index、conflict-index | `interaction-conflict-protocol.md`、`vault-protocol.md` |
| 健康检查、索引重建、断链、重复、iCloud 冲突 | `maintain-vault` | 安全增量修复；高风险先确认 | `architecture.md`、`vault-protocol.md`、`interaction-conflict-protocol.md` |

## 4. 执行前检查

每个非纯问答任务开始前必须完成：

1. 判断是否知识库任务；是则进入 Lazyday Vault skill。
2. 判断是否只读；只读时不得写文件。
3. 确认 vault root，默认当前项目根。
4. 读取本 `AGENTS.md`。
5. 如存在 git 仓库，运行或等价检查 `git status --short --branch`，保护用户已有改动。
6. 识别将要触碰的目录层级：raw、processed、wiki、indexes、answers、logs。
7. 读取目标 skill 的 `SKILL.md` 和其要求的 references。
8. 写入前重新读取目标文件当前内容。

## 5. 写入边界

### 5.1 可自动写入

在用户明确要求保存、入库、处理、初始化、回答写回或维护时，可以按 skill 协议写入：

- 新 source 的 `raw/YYYY/MM/<source_id>/`。
- 新 source 的 `manifest.md`。
- 对应 `processed/extracts/`、`processed/chunks/`、`processed/source-maps/`、`processed/media/`。
- 小范围增量更新 `indexes/*.md`。
- 有引用的小范围 wiki 更新。
- `answers/questions/`、`answers/research/` 中的授权沉淀。
- `logs/*.md` 和 `logs/event-ledger.jsonl`。

### 5.2 必须先确认

以下操作必须先让用户确认：

- 删除、移动、重命名、压缩、清理任何 `raw/` source。
- 批量重写 `wiki/`、`indexes/`、`answers/`。
- 合并或删除 iCloud 冲突副本。
- 解压大型压缩包或复制大型目录/视频集合。
- 调用外部 OCR、转写、云模型、网页抓取处理私人或敏感资料。
- 默认记录所有交互全文。
- 把 vault 同步到 Notion、Google Drive、Readwise、远程仓库或其他外部系统。
- 创建向量库、数据库、自动化脚本、hook、MCP server 或后台任务。

### 5.3 禁止操作

禁止：

- 删除 raw source 来“去重”。
- 只保存摘要不保存原文。
- 在没有 source locator 的情况下把推断写成事实。
- 把 wiki、answer、模型记忆当作原始事实源。
- 静默覆盖冲突文件。
- 静默合并 iCloud 冲突副本。
- 打印或写入 token、密钥、凭据、身份证件、未脱敏私人聊天。
- 用本地向量库或临时缓存作为唯一知识副本。
- 用本机绝对路径作为长期唯一引用。

## 6. 数据层级强约束

### 6.1 Raw Layer

`raw/` 是 source of truth。写入 raw 时必须：

- 使用稳定 `source_id`。
- 保留原始输入。
- 创建 manifest。
- 记录 hash、size、mime、privacy、availability、status。
- 多文件输入先建模 batch/source/part 关系。
- iCloud 未下载或缺文件时标记 `partial` 或 `blocked`。

### 6.2 Processed Layer

`processed/` 是可重建加工层。写入 processed 时必须：

- 记录生成时间和方法。
- 保留 source map。
- 每个 chunk 或 extract 片段可回到 raw locator。
- OCR/转写不确定内容不得写成事实。

### 6.3 Index Layer

`indexes/` 是导航层。更新任何 source 或 wiki 后必须考虑同步更新：

- `source-index.md`
- `tag-index.md`
- `entity-index.md`
- `timeline-index.md`
- `asset-index.md`
- `interaction-index.md`
- `claim-index.md`
- `conflict-index.md`
- `citation-ledger.md`

索引可以重建，但不能比 raw/source map 更权威。

### 6.4 Wiki Layer

`wiki/` 是长期知识层。页面必须区分：

- `事实`
- `综合`
- `推断`
- `待确认`
- `来源`

`事实` 必须有 source 引用。`推断` 必须标注证据强度和不确定性。

### 6.5 Answer And Research Layer

`answers/` 是输出沉淀层。answer/report 可以被复用，但不能自动升级为事实源。事实仍必须引用 parent sources。

### 6.6 Log Layer

`logs/*.md` 给人读；`logs/event-ledger.jsonl` 给重建和冲突恢复用。

每次 ingest、process、interaction、research、maintenance 写入都应追加事件。JSONL 每行必须是合法 JSON。

## 7. 证据与引用

证据强度只允许：

- `direct`
- `derived`
- `synthesized`
- `inferred`
- `unsupported`

回答、复盘、研究报告必须给来源表：

```markdown
| ref | source_id | locator | raw path | evidence_strength | reason |
|---|---|---|---|---|---|
| S1 | src-... | #L88-L143 | raw/.../app.log | direct | exact error line |
```

找不到证据时必须说“当前 vault 未找到证据”，并说明查了哪些索引或路径。

## 8. 交互和冲突

用户与 vault 的交互可以成为 source，但必须防自我强化。

必须区分：

- `user_assertion`
- `assistant_answer`
- `tool_observation`
- `decision`
- `correction`

`parent_sources` 只放证据 source。`derived_from` 记录问答链、研究链或处理链。

用户纠正旧内容时：

1. 创建 correction source。
2. 创建或更新 claim。
3. 标记 `supersedes_claims` 或 `conflicts_with_claims`。
4. 更新 `interaction-index.md`、`claim-index.md`、`conflict-index.md`。
5. 不删除旧 answer，不静默覆盖旧 wiki。

如果用户一句话同时纠错和设规则，必须拆成 correction claim 和 decision claim。

## 9. iCloud 同步规则

vault 可以放在 iCloud Drive，但必须按文件同步系统处理：

- 所有长期引用使用相对路径。
- 写入前读取最新文件。
- 不同时大范围重写同一索引或 wiki。
- 发现冲突副本时，作为独立 source 或 open conflict 处理。
- 未下载占位文件不得标记为完整 source。
- hash 不可验证时不得标记为 processed。
- 索引丢失时从 `raw/**/manifest.md` 和 `processed/**` 重建。

## 10. 输出契约

执行 Lazyday Vault 任务后，最终回复必须包含：

- 使用的 skill。
- 是否写入。
- 写入路径。
- source_id 或 affected sources。
- 引用和证据强度。
- 未处理内容和缺口。
- 需要用户确认的事项。
- 如果做了维护或重建，说明验证结果和剩余风险。

只读任务必须明确“未写入 vault”。

## 11. 验证

完成写入后必须做最低验证：

- 新 source：检查 `manifest.md`、raw path、source-index、ingest-log、event-ledger。
- 抽取：检查 extract/source map 可回到 raw。
- 整合：检查 wiki/index 引用覆盖和 claim 状态。
- 问答/复盘/研究：检查来源表、缺失范围和 unsupported 内容。
- 交互记录：检查 parent_sources、derived_from、claim/conflict 更新。
- 维护：检查 health report、修复清单和未修复项。

不能验证时，不得说完成无风险；必须说明未验证原因和剩余风险。
