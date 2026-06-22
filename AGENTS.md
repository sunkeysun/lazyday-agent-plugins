# AGENTS.md - Lazyday Agent Plugins 项目级规则

本文件是 `lazyday-agent-plugins` 仓库的项目级规则。它沉淀本仓库长期稳定的结构、插件契约、验证方式和 AI 协作边界。

本仓库不是业务应用仓库，而是面向 Codex 和 Claude Code 的本地优先插件市场与插件包仓库。工作重点是维护可安装、可验证、可复用的 agent workflows、skills、manifest、marketplace 和规则模板。

---

## 0. 规则定位

优先级：

1. 系统级安全与平台规则
2. 用户当前任务中的明确指令
3. 本仓库根目录 `AGENTS.md`
4. 被编辑文件所属运行时的官方 schema、校验器和已有文件约定
5. 通用工程经验

默认使用简体中文回复。JSON key、manifest 字段、命令、路径、代码、日志和第三方原文保持原始文本。

`rules/AGENTS.md` 是要复制到其他仓库的模板资产，不是本仓库 `rules/` 目录的项目级覆盖规则。编辑 `rules/` 下模板时，要把它们当作被维护内容来理解，不要误以为模板里的跨项目规则就是本仓库当前执行规则。

---

## 1. 项目地图

核心路径：

- `.agents/plugins/marketplace.json`：Codex 本地 plugin marketplace 目录。
- `.claude-plugin/marketplace.json`：Claude Code 本地 plugin marketplace 目录。
- `plugins/<plugin-name>/`：每个插件的实际包目录。
- `plugins/lazyday-coding/`：当前核心插件，提供中文代码开发 workflow skills。
- `plugins/lazyday-vault/`：当前核心插件，提供个人知识库、资料入库、检索、深研和复盘 workflow skills。
- `plugins/lazyday-worldcup/`：当前核心插件，提供世界杯赛果、体彩、爆冷风险、2 串 1 组合和冠亚军预测 workflow skill。
- `rules/`：可复制到其他项目的模板资产，包括 `AGENTS.md`、`CLAUDE.md`、`SKILL.md`、`mcp.json`、`README.plugin.md` 和 `plugin-checklist.md`。
- `scripts/validate.sh`：本地插件结构校验入口，默认校验 `plugins/lazyday-coding`，也可传入具体插件目录。
- `README.md`：仓库定位、安装、使用、设计原则、开发流程和路线图。
- `LICENSE`：仓库许可证文件。

当前项目设计要点：

- 本地优先，先服务个人和团队私有分发。
- 双运行时兼容，但 Codex 和 Claude Code manifest 分开维护。
- skills 尽量共享且运行时无关。
- 插件包按问题域拆分，不把 coding、vault、worldcup 等能力塞进单个插件。
- 规则模板是资产，skills 是可安装工作流，二者边界要清楚。

---

## 2. 工作模式

用户要求“分析、看看、评估、review、出方案、先设计、不要改代码”时，保持只读。只读模式允许阅读文件、搜索、运行只读检查和输出方案，不得写文件、安装依赖、提交或推送。

用户明确要求“生成、修改、实现、修复、落地、按方案执行”时，可以修改文件；修改前必须完成：

1. 确认目标文件路径和任务边界。
2. 运行 `git status --short --branch` 建立 dirty worktree 基线。
3. 对将要修改的已跟踪文件读取当前内容和相关 diff。
4. 对将要新增的文件确认路径不存在。
5. 搜索已有约定，优先复用当前结构。

当前工作区可能存在用户或其他 agent 的未提交改动。未跟踪目录、已修改 manifest、README、skill 和 marketplace 都视为用户已有工作，除非本轮明确创建。不得回滚、覆盖、格式化、重排或删除这些改动。

---

## 3. 双运行时契约

### 3.1 Marketplace

Codex marketplace：

- 文件：`.agents/plugins/marketplace.json`
- 插件条目使用 `plugins[].name` 标识插件名。
- 本地源使用 `source.source: "local"` 和 `source.path: "./plugins/<plugin-name>"`。
- `policy.installation` 和 `policy.authentication` 保持显式。
- `category` 使用稳定的大类，例如 `Coding`、`Productivity`。

Claude Code marketplace：

- 文件：`.claude-plugin/marketplace.json`
- 插件条目使用 `plugins[].name` 标识插件名。
- `source` 是相对 marketplace 根目录的字符串路径，例如 `./plugins/lazyday-coding`。
- `description`、`version`、`author` 要能独立说明安装对象。

新增插件时，除非明确只支持某一个运行时，否则同时更新两个 marketplace。若只支持单运行时，必须在 README 或插件说明中写明原因和当前状态。

### 3.2 Plugin Manifests

每个双运行时插件目录应包含：

```text
plugins/<plugin-name>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/
└── README.md
```

Codex manifest：

- 路径：`plugins/<plugin-name>/.codex-plugin/plugin.json`
- 可包含 `interface` 展示信息。
- `skills` 通常指向 `"./skills/"`。
- `name` 使用稳定 kebab-case，必须和插件目录、marketplace 条目一致。

Claude manifest：

- 路径：`plugins/<plugin-name>/.claude-plugin/plugin.json`
- 只写 Claude Code 校验器接受的字段。
- 不要把 Codex 的 `interface` 结构原样复制到 Claude manifest。
- 若要新增展示字段，先查当前 Claude plugin schema 或运行验证；历史上不支持的 root 字段会导致校验失败。

跨运行时同步要求：

- `name`、`version`、`description`、`author`、`homepage`、`repository`、`license`、`keywords` 应尽量保持语义一致。
- 运行时差异放在对应 manifest，不做一份“通用 manifest”强行兼容。
- JSON 文件不得包含注释，不做无关排序或格式化。

---

## 4. Skill 约定

标准目录：

```text
plugins/<plugin-name>/skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
└── references/
```

`SKILL.md` 要求：

- 使用 frontmatter，至少包含 `name` 和 `description`。
- `name` 必须与目录名一致，使用 kebab-case。
- `description` 必须明确触发场景、默认模式、适用请求和禁止误触发的边界。
- 正文用中文描述 workflow，字段名、文件名、命令和 API 保持原文。
- skill 内容应运行时无关，避免引用宿主特有 UI 或不可移植绝对路径。
- 需要长篇评分细则、协议或 rubric 时放到 `references/`，由 `SKILL.md` 明确何时读取。

`agents/openai.yaml` 约定：

- 使用 `interface.display_name`、`interface.short_description`、`interface.default_prompt` 提供展示和默认提示。
- 使用 `policy.allow_implicit_invocation` 控制是否允许隐式触发。
- 当前只有 `route-coding-task` 允许隐式触发；其他业务 skill 默认 `false`，避免误进入写入、提交或高风险流程。

新增或修改 skill 时，同时检查：

- 插件 README 的 skill 列表是否需要更新。
- 对应 reference 文件是否仍被正确引用。
- `agents/openai.yaml` 是否与 `SKILL.md` 的触发语义一致。
- 运行 `./scripts/validate.sh plugins/<plugin-name>` 是否通过。

---

## 5. Lazyday Coding 固定设计

`lazyday-coding` 是中文代码开发 workflow 插件。当前技能边界：

- `route-coding-task`：入口路由，判断当前请求使用哪个 skill，不强制固定流程。
- `clarify-task`：补全任务契约、成功标准、风险等级和确认门。
- `manage-artifacts`：管理 `.lazyday/coding/requirements/` 下的跨会话需求产物。
- `resume-context`：从已有产物恢复上下文并匹配候选需求。
- `explore-repo`：建立项目结构、调用链、可复用实现和验证入口地图。
- `research-approach`：只读方案调研、方案对比、工作量评估和推荐决策。
- `break-down-task`：将已确认方案拆成任务图、依赖关系、冲突矩阵和验证矩阵。
- `implement-change`：在明确授权下进行最小精准实现。
- `diagnose-problem`：只读问题定位、根因分析、证据强度和候选根因排序。
- `review-code`：只读代码 Review，问题优先，按严重度输出。
- `verify-change`：只读验证当前改动、失败路径和剩余风险。
- `commit-changes`：提交信息、提交范围、commit 和 push handoff。

重要原则：

- `route-coding-task` 是入口判断层，不是强制流水线控制器。
- 用户可以直接跳到实现、验证、review 或提交；目标 skill 必须自己补齐安全门和最小上下文。
- 完整需求场景才建议使用 `.lazyday/coding/requirements/`；单点工具请求不要强制创建产物。
- 写代码、提交、推送、删除、依赖、MCP、hook、发布相关动作必须有明确授权。

---

## 5.1 Lazyday Vault 固定设计

`lazyday-vault` 是个人知识库和资料复盘 workflow 插件。当前技能边界：

- `route-vault-task`：入口路由，判断入库、抽取、整合、问答、深研、复盘或维护。
- `initialize-vault`：初始化或修复当前 vault 项目的基础目录、索引和日志。
- `capture-source`：保存原始资料，生成 `source_id`、raw path、manifest 和 source index。
- `extract-source`：从 raw source 抽取文本、OCR、转写、chunk 和 source map。
- `integrate-knowledge`：打标、更新 wiki、indexes、实体、项目、时间线和待确认项。
- `process-source`：协调资料处理的抽取和整合阶段。
- `record-vault-interaction`：记录用户问答、反馈、修正、确认和决策。
- `answer-vault-question`：基于 vault 资料回答问题，保留证据和不确定性。
- `vault-deep-research`：基于个人资料做深入研究和报告。
- `review-life-log`：生成日报、周报、年报、项目回顾、心情与感想复盘。
- `maintain-vault`：检查断链、孤儿页、重复 source、引用覆盖和未处理资料。

重要原则：

- vault 主数据目录默认在运行插件的当前 vault 项目根目录，例如 `raw/`、`processed/`、`wiki/`、`indexes/`、`answers/` 和 `logs/`。
- 跨会话需求协作产物使用 `.lazyday/vault/requirements/`，不要和 `lazyday-coding` 的 `.lazyday/coding/requirements/` 混用。
- 写入 raw、processed、wiki、indexes、answers 或 logs 前，必须确认用户已授权对当前 vault 项目写入。

---

## 5.2 Lazyday Worldcup 固定设计

`lazyday-worldcup` 打包 `forecasting-world-cup-matches` skill，用于世界杯比赛预测、体彩可售方案、爆冷风险、2 串 1 组合和冠亚军预测。

重要原则：

- 默认使用中文输出、北京时间和明确数据截点。
- 涉及最新赛程、赔率、体彩可售状态、伤停、阵容、赛果或规则时，必须联网或使用权威来源确认。
- 预测输出必须区分事实、推断、概率判断和投注建议，不得使用保证性表述。
- skill 内 scripts/tests 只在用户明确触发或验证需要时运行；不得在没有授权时假设自动联网、下注、上传或发布。

---

## 6. 插件产物协议

Lazyday skills 使用目标仓库中的 `.lazyday/<plugin-artifact-namespace>/requirements/` 保存跨会话协作产物。二级目录必须是插件产物命名空间，用来隔离不同插件的产物，避免多个插件共享 `.lazyday/requirements/` 造成上下文混淆。

命名空间规范：

- 每个插件必须定义稳定的 `artifact namespace`。
- 命名空间使用小写字母、数字和连字符，优先使用插件名去掉 `lazyday-` 前缀后的短名。
- `lazyday-coding` 的命名空间固定为 `coding`。
- 后续插件示例：`lazyday-vault` 使用 `vault`，对应 `.lazyday/vault/requirements/`。
- 不要把所有插件产物直接写到 `.lazyday/requirements/`。

`lazyday-coding` 的当前产物根路径是 `.lazyday/coding/requirements/`。这个目录是 agent 协作状态，不是业务源码。

标准结构：

```text
.lazyday/
└── coding/
    └── requirements/
        ├── index.md
        ├── CURRENT
        └── <requirement-id>/
            ├── manifest.md
            ├── brief.md
            ├── repo-context.md
            ├── research.md
            ├── plan.md
            ├── diagnosis.md
            ├── implementation.md
            ├── verification.md
            ├── review.md
            ├── commit.md
            ├── decisions.md
            ├── open-questions.md
            └── handoff.md
```

约定：

- 需求 ID 使用 `YYYYMMDD-HHMM-short-name`。
- 只有用户要求跨会话记录、后续继续、完整需求管理或明确允许落盘时，才写入对应插件命名空间下的 `.lazyday/<namespace>/requirements/`。
- 每个 skill 只读取自己需要的产物，避免加载整个需求目录。
- 每次写阶段产物时同步更新一页以内的 `handoff.md`。
- 写入前重新读取目标文件、`manifest.md` 和 `handoff.md`，检查是否有其他会话更新。
- `.lazyday/` 默认不提交；只有用户明确要求提交协作产物时才纳入提交范围。

---

## 7. `rules/` 模板资产

`rules/` 保存可复制到其他项目的模板，不是运行时自动加载配置。

- `rules/AGENTS.md`：跨项目 AI 编程规则模板。
- `rules/CLAUDE.md`：Claude Code 项目规则模板。
- `rules/SKILL.md`：skill 模板。
- `rules/mcp.json`：MCP 配置模板。
- `rules/README.plugin.md`：插件 README 模板。
- `rules/plugin-checklist.md`：新增或发布插件时的检查清单。

维护模板时：

- 保持模板通用，不写本仓库当前临时任务、私有路径、账号、token 或一次性结论。
- 不把模板内容和本仓库根 `AGENTS.md` 混在一起。
- 修改规则模板时优先保持结构清晰和可复制性，必要时同步 README 中的使用说明。

---

## 8. 验证协议

首选验证入口：

```bash
./scripts/validate.sh
./scripts/validate.sh plugins/<plugin-name>
```

当前脚本行为：

- 默认校验 `plugins/lazyday-coding`。
- 使用 Codex plugin creator validator。
- 如果当前 `python3` 没有 PyYAML，会创建临时 YAML shim。
- 如果本机存在 `claude` 命令，会运行 `claude plugin validate <plugin-dir>`；否则打印 skip 信息。

运行前提：

- 如果 `scripts/validate.sh` 本身被修改过，先重新阅读脚本再执行。
- 不安装依赖、不升级工具、不改系统环境来通过验证，除非用户明确确认。

按改动类型选择验证：

- 修改 JSON manifest 或 marketplace：运行 `python3 -m json.tool <file> >/dev/null`，再运行对应插件校验。
- 新增或修改 skill：检查 frontmatter、`agents/openai.yaml` 和插件 README，再运行插件校验。
- 新增插件：校验 manifest、marketplace、README、skills 和运行时差异说明。
- 仅修改文档或模板：至少做文件读回和结构检查；如果影响安装、manifest 或 skill 触发语，仍运行插件校验。

没有验证证据时，不要说“已完成无风险”。说明未验证原因、替代证据和剩余风险。

---

## 9. 安全与信任边界

插件和 marketplace 是高信任组件。任何会让插件获得更强能力的改动都按高风险处理。

必须先让用户确认的情况：

- 新增 MCP server、hooks、commands、自动化脚本或外部服务连接。
- 新增、删除或升级依赖，或改动 lockfile、安装脚本、CI、发布脚本。
- 改变 marketplace 安装策略、认证策略或默认启用能力。
- 引入网络访问、文件系统写入、命令执行、浏览器自动化或凭据读取能力。
- 发布、上传、推送、打 tag、创建 release 或修改许可证。

禁止写入：

- token、密钥、cookie、账号、私有 payload、生产环境数据。
- 未脱敏日志、用户隐私、完整敏感路径。
- 会在安装缓存中失效的插件内部绝对路径。

开发脚本可以引用本机工具路径，但不要把本机私有路径写进可分发 skill、manifest、README 示例或模板，除非这是明确的本地开发说明。

---

## 10. 编辑纪律

优先使用 `rg`、`rg --files`、`sed`、`git diff`、`git status` 理解仓库。

修改原则：

- 最小精准改动，一次只服务当前任务。
- 不做顺手重构、顺手格式化、顺手同步版本、顺手扩展 roadmap。
- 不删除 `.DS_Store`、未跟踪目录、用户草稿或实验插件，除非用户明确要求。
- 不使用 `git add .`、`git reset --hard`、强制 checkout、清理 untracked、全仓格式化或自动修复命令。
- 写入前重新读取目标片段；写入后检查 diff，确认只包含本次意图。

JSON 修改：

- 保持合法 JSON。
- 不加注释。
- 不引入尾逗号。
- 不跨运行时复制不兼容字段。

Markdown 修改：

- 保持可扫描结构。
- 不重复粘贴大段通用规则。
- 项目 README 说明用户价值、安装和使用；插件 README 说明插件能力和运行时 manifest；skill 文件说明触发、流程和交付。
- 修改项目内容后必须同步检查文档影响，不能只改代码、manifest、marketplace 或 skill 而不更新对应说明。

---

## 11. 文档同步强制规则

修改本仓库任何项目内容后，必须在同一轮检查并更新对应文档。文档同步是交付的一部分，不是可选收尾。

触发规则：

- 新增、删除或改变可发现插件、skill、manifest、marketplace、安装方式、验证方式或许可证时，必须更新根 `README.md`。
- 改变单个插件的能力、skill 边界、运行时差异、数据目录、安全边界或使用示例时，必须更新对应 `plugins/<plugin-name>/README.md`。
- 改变本仓库长期协作规则、目录职责、验证协议、确认门、编辑纪律或发布边界时，必须更新根 `AGENTS.md`。
- 改变可复制模板的行为时，必须更新 `rules/` 下对应模板和说明。
- 改变 `scripts/validate.sh` 或验证前提时，必须同步更新根 `README.md` 和本文件的验证协议。

执行要求：

- 文档更新要和功能、配置或规则改动同轮完成。
- 写文档前先读取目标文档当前内容和相关 diff，保护用户已有改动。
- 如果判断某次改动不需要文档更新，最终交付必须明确说明已检查哪些文档，以及为什么无需更新。
- 验证时至少做文档读回和相关链接 / 路径 / 命令的静态检查；影响 manifest、marketplace 或 skill 触发语时，仍按验证协议运行插件校验。

---

## 12. 新增插件检查

新增 `plugins/<plugin-name>/` 时，最小完成标准：

1. 插件名使用稳定 kebab-case。
2. 创建 `.codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json`，除非明确单运行时。
3. 创建 `README.md`，说明能力、安装、skills 和边界。
4. 创建至少一个 `skills/<skill-name>/SKILL.md`。
5. 为每个 skill 创建或有意省略 `agents/openai.yaml`，并说明原因。
6. 更新 `.agents/plugins/marketplace.json`。
7. 更新 `.claude-plugin/marketplace.json`，或说明为什么暂不支持 Claude Code。
8. 运行 `./scripts/validate.sh plugins/<plugin-name>`。
9. 更新根 README 的插件列表、安装说明、验证说明或 roadmap，仅在该插件进入用户可发现状态时进行。
10. 检查并更新根 `AGENTS.md` 中的项目地图、固定设计、验证协议和文档同步规则。

如果插件只是 scaffold 或实验状态，必须在 manifest/README/最终回复中明确“未完成范围”，不要把它描述为 release-ready。

---

## 13. 提交与发布

提交前必须区分：

- 本次任务相关改动。
- 用户或其他 agent 的并行改动。
- 实验 scaffold、临时文件、生成文件和本地协作产物。

没有用户明确要求，不执行 commit 或 push。

如果用户要求提交：

- 先读取最近提交风格。
- 基于真实 diff 生成提交信息。
- staged 内容不等于授权提交。
- 不使用 `git add .`，除非用户明确确认全部改动都要提交。
- `.lazyday/` 默认不提交。

发布、打 tag、上传 marketplace、公开远程分发、修改许可证或切换 `UNLICENSED` 状态，必须先给影响范围、目标版本、验证证据和回滚方式，并等待确认。

---

## 14. 最终交付

最终回复至少说明：

- 实际完成了什么。
- 修改了哪些文件。
- 运行了哪些验证及结果。
- 未验证内容和剩余风险。
- 是否保留了用户已有改动。
- 文档同步情况：更新了哪些文档，或已检查且无需更新的理由。

如果只做分析或 review，问题和结论优先；如果做实现，改动和验证优先；如果做插件/manifest 变更，运行时兼容性和校验结果优先。
