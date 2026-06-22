# Lazyday Agent Plugins

[![Codex](https://img.shields.io/badge/Codex-compatible-111827)](https://developers.openai.com/codex)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-4f46e5)](https://code.claude.com/docs)
[![Plugin Marketplace](https://img.shields.io/badge/plugin%20marketplace-local%20first-059669)](#installation)
[![Status](https://img.shields.io/badge/status-early%20alpha-f59e0b)](#roadmap)

Lazyday Agent Plugins 是一组面向 Codex 和 Claude Code 的通用 AI
Agent 工具插件集合。

它的目标很直接：把高质量 AI 协作里的通用流程、工程纪律、验证闭环和上下文模板沉淀成可安装、可复用、可分发的插件，让人从重复解释、反复纠偏和低价值执行中解放出来，把注意力留给真正需要判断力和创造力的事情。

> 人人都有 Lazyday：人负责方向、决策和创造，AI 负责可靠执行、证据验证和持续交付。

## Why Lazyday

今天的大模型已经很强，但很多团队使用 AI 编程工具时仍然会遇到相同问题：

- 每次都要重复说明工作方式、只读边界、验证要求和提交规范。
- Agent 容易抢跑、多改、漏改、覆盖用户改动，或者在没有证据时交付。
- Codex、Claude Code、不同项目和不同成员之间缺少统一的协作协议。
- 好的 prompt 和 workflow 难以版本化、复用、评审、安装和迭代。
- 人仍然在做大量低价值操作：拆任务、贴规则、补上下文、提醒跑测试、整理提交。

Lazyday 的方向是把这些内容产品化为插件：

- **工作流即插件**：把调研、拆解、实现、诊断、Review、验证、提交这些流程做成可安装能力。
- **规则即资产**：把 AI 编程黄金法则、项目模板和检查清单沉淀到版本库。
- **双运行时兼容**：同一套能力同时服务 Codex 和 Claude Code，避免团队被单一工具锁死。
- **证据驱动交付**：强调最小改动、保护用户已有改动、验证结果和可回滚边界。
- **本地优先分发**：先支持个人和团队在本地/私有仓库中使用，再逐步走向公开市场。

## What Is Inside

当前仓库包含一个本地插件市场和三个核心插件：`lazyday-coding`、`lazyday-vault` 与 `lazyday-worldcup`。

| Layer | Path | Purpose |
| --- | --- | --- |
| Codex marketplace | `.agents/plugins/marketplace.json` | Codex 可发现的插件目录 |
| Claude Code marketplace | `.claude-plugin/marketplace.json` | Claude Code 可添加的插件市场 |
| Coding plugin | `plugins/lazyday-coding/` | 中文代码开发 workflow skills |
| Vault plugin | `plugins/lazyday-vault/` | 个人知识库、资料入库、检索、深研和复盘 workflow skills |
| World Cup plugin | `plugins/lazyday-worldcup/` | 世界杯赛果、体彩、爆冷风险和冠亚军预测 workflow skill |
| Codex plugin manifests | `plugins/*/.codex-plugin/plugin.json` | Codex 插件描述、技能入口和展示信息 |
| Claude plugin manifests | `plugins/*/.claude-plugin/plugin.json` | Claude Code 插件描述和技能入口 |
| Shared skills | `plugins/*/skills/` | 双运行时共享的 Lazyday 工作流 |
| Rule templates | `rules/` | 深度优化的 AGENTS / CLAUDE / Skill / MCP 模板 |
| Validation | `scripts/validate.sh` | 本地校验 Codex / Claude Code 插件结构 |

## Current Plugin: lazyday-coding

`lazyday-coding` 是面向中文代码开发场景的基础插件，覆盖从想法到提交的主流程。

| Skill | When to use | Output |
| --- | --- | --- |
| `route-coding-task` | 不确定该用哪个 coding skill、要判断完整需求还是单点工具、要支持跳步执行 | 推荐 skill、是否需要产物、是否恢复上下文、交接输入 |
| `clarify-task` | 需求模糊、边界不清、需要选择或创建需求产物 | 任务契约、确认问题、风险等级、下一步 skill |
| `manage-artifacts` | 创建、选择、切换、读取、修复或归档需求产物 | 当前需求、产物状态、handoff 摘要、下一步 skill |
| `resume-context` | 继续上次任务、跨会话恢复上下文、从多个需求中选择当前需求 | 候选需求排序、匹配依据、当前阶段、下一步 skill |
| `explore-repo` | 进入陌生仓库/模块、需要理解入口、调用链和测试 | 仓库上下文地图、相关文件、验证入口、风险边界 |
| `research-approach` | 先调研、出方案、评估设计、比较最佳实践 | 多方案对比、推荐方案、风险边界和实现指导 |
| `break-down-task` | 把已确认方案拆成可执行任务 | 任务图、依赖关系、并发边界、验证矩阵 |
| `implement-change` | 已授权修改代码、修复问题、按方案落地 | 最小精准改动、验证证据、剩余风险 |
| `diagnose-problem` | 分析 bug、日志、测试失败、线上异常 | 时间线、候选根因、影响范围、修复建议 |
| `review-code` | Review 当前 diff、PR、文件或方案 | Findings、严重级别、行号证据、测试缺口 |
| `verify-change` | 跑测试、验证修复、交付前检查 | 验证矩阵、命令结果、未覆盖路径 |
| `commit-changes` | 生成提交信息、提交、按要求推送 | 提交范围判断、commit message、push 结果 |

### Cross-session artifacts

Lazyday Coding 支持把不同 skill 的产物沉淀到目标仓库的隐藏目录。`.lazyday/` 下的二级目录是插件产物命名空间，`lazyday-coding` 固定使用 `coding`：

```text
.lazyday/coding/requirements/<requirement-id>/
```

后续插件也必须使用自己的命名空间，例如 `lazyday-vault` 的跨会话需求协作产物使用 `.lazyday/vault/requirements/`。`lazyday-vault` 的主知识库数据则直接放在 vault 项目根目录，便于作为 iCloud 同步项目使用。不要再把插件产物直接写入 `.lazyday/requirements/`。

每个需求目录统一管理 `manifest.md`、`brief.md`、`repo-context.md`、`research.md`、`plan.md`、`diagnosis.md`、`implementation.md`、`verification.md`、`review.md`、`commit.md`、`decisions.md`、`open-questions.md` 和 `handoff.md`。

使用策略：

1. 不确定要继续哪个需求时，先用 `resume-context` 读取 `index.md`、`CURRENT`、`manifest.md`、`handoff.md` 和 `brief.md`，按当前描述排序候选。
2. 需要创建、切换、归档、修复或整理产物时，用 `manage-artifacts` 维护需求目录、`CURRENT`、`index.md`、`manifest.md` 和 `handoff.md`。
3. 需要补全任务契约时，用 `clarify-task` 更新 `brief.md`、`decisions.md` 和 `open-questions.md`。
4. 每个业务 skill 只读取自己需要的前序产物，避免加载整个目录；单独使用某个 skill 时，产物只是可选输入，不强制走完整流程。
5. 每个业务 skill 产出结果时更新自己的阶段文件和 `handoff.md`。
6. `.lazyday/` 默认是本地协作产物，不纳入业务提交；只有用户明确要求时才提交。

这些技能默认遵守 Lazyday 的核心工程约束：

- 用户要求只读时绝不改代码。
- 修改前先理解项目规则和 dirty worktree。
- 优先复用已有实现，不顺手重构。
- 每一行改动都服务当前任务。
- 高风险决策先让人确认。
- 没有验证证据，不算完成。

## Current Plugin: lazyday-vault

`lazyday-vault` 是面向个人知识库和资料复盘的基础插件。它的核心不是普通分类，而是以 `source_id` 为中心保存原始资料、加工层、索引、LLM wiki、答案和日志。

默认数据位置是运行插件的当前 vault 项目根目录：

```text
<vault-project>/
├── raw/
├── processed/
├── wiki/
├── indexes/
├── answers/
└── logs/
```

跨会话需求协作产物仍使用隐藏命名空间：

```text
.lazyday/vault/requirements/
```

| Skill | When to use | Output |
| --- | --- | --- |
| `route-vault-task` | 不确定该入库、抽取、整合、问答、深研、复盘还是维护 | 推荐 skill、写入边界、交接输入 |
| `initialize-vault` | 初始化或修复当前 iCloud vault 项目的基础目录、索引和日志 | vault 骨架、基础索引、事件账本、初始化报告 |
| `capture-source` | 保存一句话、文件、图片、视频、压缩包、电子书、日志等原始资料 | source_id、raw path、manifest、source-index |
| `extract-source` | 从 raw source 抽取文本、OCR、转写、chunk、source map | extract、chunks、source map、引用样例 |
| `integrate-knowledge` | 打标、识别实体/项目/时间线/情绪线索、更新 wiki 和 indexes | wiki 页面、索引、引用覆盖、待确认项 |
| `process-source` | 用户只说“处理这份资料”，需要协调抽取和整合阶段 | 当前层级状态、下一步 skill、缺口 |
| `record-vault-interaction` | 记录用户问答、反馈、修正、确认和决策 | interaction source、parent sources、claim 级冲突关系 |
| `answer-vault-question` | 基于 vault 回答问题、召回图片/日志/文本/项目证据 | 有引用的答案、证据表、不确定性 |
| `vault-deep-research` | 基于个人资料做 NotebookLM 式深入研究和报告 | 研究结论、证据地图、引用和可写回页面 |
| `review-life-log` | 生成日报、周报、年报、项目回顾、心情与感想复盘 | 时间线总结、项目参与、情绪证据、引用 |
| `maintain-vault` | 检查断链、孤儿页、重复 source、引用覆盖和未处理资料 | 健康报告、已修复项、需确认项 |

## Current Plugin: lazyday-worldcup

`lazyday-worldcup` 打包 `forecasting-world-cup-matches` skill，用于世界杯赛果预测、体彩可售方案、爆冷风险、2 串 1 组合和冠亚军预测。

| Skill | When to use | Output |
| --- | --- | --- |
| `forecasting-world-cup-matches` | 预测世界杯比赛、排序未开赛场次、复盘已完赛表现、评估爆冷风险、构建体彩 2 串 1、预测冠亚军 | 带时间截点、来源分级、概率估计、风险路径、体彩可售状态和验证提醒的预测报告 |

## Rules & AGENTS.md

Lazyday 不只有插件技能，还沉淀了一套可复制到任意仓库的 AI 编程规则模板。这里最有价值的是 `rules/AGENTS.md`：它不是普通 prompt，而是一份跨项目恒定成立的 agent 工作协议。

这份模板解决的是插件无法单独覆盖的问题：当 agent 进入具体代码仓库时，它需要稳定理解工作边界、只读模式、风险分级、dirty worktree、确认门、验证证据、并发协作和最终交付格式。`AGENTS.md` 把这些规则放到仓库内，让 Codex 这类遵循 AGENTS 约定的工具可以在每次任务开始时自动读取。

### What the template enforces

| Area | Rule |
| --- | --- |
| 工作模式 | 先判断只读、实现、Bug 修复、Review、研究决策等模式 |
| 上下文理解 | 修改前先找项目级 / 目录级规则，先理解调用链和现有实现 |
| 用户改动保护 | 修改前检查 dirty worktree，禁止覆盖、回滚或格式化用户已有改动 |
| 最小改动 | 只做当前任务需要的改动，不顺手重构、升级依赖或扩大范围 |
| 风险分级 | S0-S4 区分咨询、小改、多模块、核心链路和破坏性操作 |
| 人工确认门 | 依赖、schema、权限、数据迁移、发布、删除等高风险动作先确认 |
| 证据验证 | 没有测试、构建、lint、smoke、日志或手工证据，不算真正完成 |
| 多 agent 协作 | 明确文件所有权，避免多个 agent 同时写同一文件或 lockfile |

### How to use `rules/AGENTS.md`

把模板复制到目标仓库根目录：

```bash
cp rules/AGENTS.md /path/to/your-repo/AGENTS.md
```

然后按项目补充更近目录的规则。例如：

```text
your-repo/
├── AGENTS.md                  # 全仓通用 AI 协作规则
├── apps/web/AGENTS.md         # 前端目录的构建、测试、UI 规则
├── apps/electron/AGENTS.md    # Electron main/preload/renderer 边界
└── packages/api/AGENTS.md     # API、schema、权限、数据库规则
```

推荐分层方式：

1. 根 `AGENTS.md` 只放全仓稳定规则：工作模式、风险分级、验证要求、提交边界。
2. 子目录 `AGENTS.md` 放局部规则：构建命令、测试命令、架构边界、业务约束。
3. 不把临时需求、一次性任务和具体 issue 写进长期规则。
4. 不把 token、账号、私有路径、生产环境数据写进规则文件。
5. 每次规则升级后，用真实任务或 review 场景验证它是否减少误改和返工。

### Global vs project rules

如果你希望所有仓库都默认遵守 Lazyday 工作协议，可以把 `rules/AGENTS.md` 作为个人级规则维护；如果只想在某个项目生效，则复制到该项目根目录。项目规则应优先承载具体命令和业务约束，个人级规则只放跨项目恒定成立的原则。

### `rules/` vs plugin package

`rules/AGENTS.md` 是完整、深度优化的规则库模板，适合作为项目初始化或团队标准。`lazyday-coding` 插件本体只分发可执行的 skills，不再在插件目录内携带 `templates/`，避免安装包内出现两套规则来源。

- 新项目初始化：优先使用 `rules/AGENTS.md`。
- 插件安装后的日常使用：通过 `lazyday-coding` 的 skills 触发工作流。
- 团队规范沉淀：把 `rules/AGENTS.md` 复制到目标仓库后，再加入项目级构建、测试、架构和业务规则。
- 插件作者开发新插件：参考 `rules/plugin-checklist.md`，确保双运行时 manifest、marketplace、skills 和验证说明齐全。

## Installation

### Prerequisites

- 已安装并登录 [Codex](https://developers.openai.com/codex)。
- 已安装并登录 [Claude Code](https://code.claude.com/docs)。
- 如果使用本地路径安装，先 clone 本仓库：

```bash
git clone https://github.com/sunkeysun/lazyday-agent-plugins.git
cd lazyday-agent-plugins
```

### Install in Codex

Codex 支持通过 marketplace 安装插件。Lazyday 提供的是 repo-scoped marketplace：

```bash
codex plugin marketplace add .
codex plugin marketplace list
```

然后打开 Codex 插件目录：

```text
codex
/plugins
```

在插件目录中选择 `Lazyday Agent Plugins` marketplace，找到并安装 `lazyday-coding`、`lazyday-vault` 或 `lazyday-worldcup`。安装后开启新线程，直接描述任务，或在 prompt 中显式选择 Lazyday Coding / Lazyday Vault / Lazyday Worldcup / 相关技能。

如果后续从 GitHub 分发，可使用同类命令添加远程市场：

```bash
codex plugin marketplace add sunkeysun/lazyday-agent-plugins
```

### Install in Claude Code

在 Claude Code 交互会话中添加本地 marketplace：

```text
/plugin marketplace add .
/plugin install lazyday-coding@lazyday-agent-plugins
/plugin install lazyday-vault@lazyday-agent-plugins
/plugin install lazyday-worldcup@lazyday-agent-plugins
/reload-plugins
```

也可以在仓库公开后通过 GitHub shorthand 添加：

```text
/plugin marketplace add sunkeysun/lazyday-agent-plugins
/plugin install lazyday-coding@lazyday-agent-plugins
/plugin install lazyday-vault@lazyday-agent-plugins
/plugin install lazyday-worldcup@lazyday-agent-plugins
/reload-plugins
```

Claude Code 插件技能会按插件名命名空间化。安装后可以尝试：

```text
/lazyday-coding:research-approach 先调研这个需求应该怎么实现，不要改代码
/lazyday-coding:review-code review 当前 diff，重点看回归风险
/lazyday-coding:verify-change 验证这次改动是否完整
/lazyday-vault:route-vault-task 处理这份资料并保留原始引用
/lazyday-vault:answer-vault-question 基于我的资料回答这个问题，并给出来源
/lazyday-worldcup:forecasting-world-cup-matches 预测今天世界杯比赛，使用官方体彩数据并给出风险
```

### Validate the local package

```bash
./scripts/validate.sh
./scripts/validate.sh plugins/lazyday-vault
./scripts/validate.sh plugins/lazyday-worldcup
```

如果只想直接验证 Claude Code marketplace：

```bash
claude plugin validate .claude-plugin/marketplace.json
```

## Usage Patterns

### 1. 先调研，再落地

```text
使用 Lazyday Coding 先调研这个功能怎么做，不要改代码。
目标：...
约束：...
验收标准：...
```

适合不确定方案、涉及架构取舍、需要查官方文档或比较多个实现路径的任务。

### 2. 选择或创建需求产物

```text
使用 Lazyday Coding 创建这个需求的产物目录，并设为当前需求。
```

适合多天开发、多 skill 协作、多个会话切换或需要让 agent 从已有产物继续工作的场景。

### 3. 探索仓库上下文

```text
使用 Lazyday Coding 探索这个模块，找入口、调用链、相关测试和可复用实现，结果记录到当前需求。
```

适合陌生仓库、跨模块改动、实现前上下文不足或 review 前需要建立变更地图的场景。

### 4. 把方案拆成 Agent 任务

```text
把上面的方案拆成可交给多个 agent 执行的任务，标明哪些可以并行，哪些必须串行。
```

适合较大改动、多人协作、并行子任务或希望减少 agent 互相覆盖的场景。

### 5. 最小实现并验证

```text
按这个方案落地，只解决当前问题，不做额外重构。完成后运行最小验证。
```

适合已经确认方向，需要让 agent 稳定写代码并给出证据的任务。

### 6. 只做 Review

```text
review 当前 diff，只输出真实问题，按严重程度排序，不改代码。
```

适合提交前把关、合并前检查、回归风险评估。

### 7. 提交与推送

```text
整理这次改动，生成提交信息。确认范围后提交并推送。
```

适合把 agent 产出的改动安全收束为 commit，避免把其他会话或用户未完成改动误提交。

## Design Principles

### 1. Human decision, agent execution

Lazyday 不追求让 AI 替代人的判断。它把重复、可验证、可流程化的部分交给 agent，把不可逆决策、产品判断、技术取舍和创造性工作留给人。

### 2. Evidence over vibes

每个工作流都强调证据链：读了哪些规则，为什么这样改，跑了什么验证，哪些路径没覆盖，剩余风险是什么。

### 3. Local first, team ready

本仓库先服务本地和团队私有分发。随着插件成熟，可以接入远程 marketplace、团队托管、版本发布和更严格的 CI。

### 4. Cross-runtime by design

Codex 和 Claude Code 的插件 manifest 分开维护，但技能、模板和方法论尽量共享。这样既尊重不同宿主的约定，也避免重复维护两套工作流。

### 5. Minimal surface area

当前插件先聚焦 coding workflow，不急着塞进所有能力。未来的通用工具、知识管理、项目管理、浏览器自动化、文档处理、数据分析等能力会按独立插件扩展。

## Documentation Sources

本 README 的安装与市场设计参考了以下官方文档和开源 README 实践：

- [Codex Plugins](https://developers.openai.com/codex/plugins)：Codex 插件可包含 skills、apps、MCP servers，并可通过 plugin directory 安装和启用。
- [Codex Build Plugins](https://developers.openai.com/codex/plugins/build)：Codex repo marketplace、personal marketplace、`codex plugin marketplace add` 和本地插件结构。
- [Claude Code: Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)：Claude Code marketplace 添加、插件安装、`/reload-plugins`、安装 scope 和安全提示。
- [Claude Code: Create plugins](https://code.claude.com/docs/en/plugins)：Claude Code 插件可打包 skills、agents、hooks、MCP servers 等能力。
- [Claude Code: Create plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)：Claude Code marketplace 分发模型和市场目录结构。
- [GitHub Docs: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)：README 应说明项目做什么、为什么有用、如何开始、在哪里获得帮助。
- [awesome-readme](https://github.com/matiassingers/awesome-readme) 和 [Best-README-Template](https://github.com/othneildrew/Best-README-Template)：优秀开源 README 通常具备清晰定位、快速开始、安装、使用示例、路线图和贡献入口。

## Project Structure

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── lazyday-coding/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── .codex-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   └── README.md
│   ├── lazyday-vault/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── .codex-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   └── README.md
│   └── lazyday-worldcup/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .codex-plugin/
│       │   └── plugin.json
│       ├── skills/
│       └── README.md
├── rules/
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── README.plugin.md
│   ├── SKILL.md
│   ├── mcp.json
│   └── plugin-checklist.md
├── scripts/
│   └── validate.sh
└── README.md
```

## Development Workflow

### Documentation sync rule

修改本仓库任何项目内容后，必须在同一轮检查并更新对应文档：

- 新增、删除或改变可发现插件、skill、manifest、marketplace、安装方式、验证方式或许可证时，更新根 `README.md`。
- 改变单个插件的能力、skill 边界、运行时差异、数据目录或安全边界时，更新对应 `plugins/<plugin-name>/README.md`。
- 改变本仓库长期协作规则、目录职责、验证协议、确认门或编辑纪律时，更新根 `AGENTS.md`。
- 改变可复制模板的行为时，更新 `rules/` 下对应模板和说明。
- 如果判断某次代码或配置改动不需要文档更新，最终交付必须明确说明“已检查文档，无需更新”的理由。

### Add a new skill

1. 在 `plugins/<plugin>/skills/<skill-name>/SKILL.md` 创建技能。
2. 使用 frontmatter 声明 `name` 和 `description`。
3. 在插件 README 中补充能力说明。
4. 运行 `./scripts/validate.sh`。

### Add a new plugin

1. 在 `plugins/<plugin-name>/` 下创建插件目录。
2. 分别创建 `.codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json`。
3. 将插件加入 `.agents/plugins/marketplace.json`。
4. 将插件加入 `.claude-plugin/marketplace.json`。
5. 为插件补充 `README.md` 和 `skills/`。
6. 运行 `./scripts/validate.sh <plugin-dir>`。

### Compatibility checklist

- 插件名使用稳定的 kebab-case。
- Codex 和 Claude Code manifest 各自只放对应运行时支持的字段。
- skills 内容尽量运行时无关；运行时差异放在安装和使用说明中。
- 插件内引用文件必须在插件目录内，避免安装到缓存后路径失效。
- 不把私有路径、token、账号、生产环境信息写入技能、模板或日志。

## Roadmap

### Near term

- 完善 `lazyday-coding` 的技能边界、触发语和验证闭环。
- 为 `rules/AGENTS.md` 增加更完整的安装说明、场景示例和裁剪指南。
- 为 Codex / Claude Code 增加更完整的本地安装截图或录屏。
- 为每个 skill 增加最小示例和反例。
- 增加 marketplace / plugin manifest 的 CI 校验。
- 增加英文 README 或双语入口，方便公开传播。

### Mid term

- 增加 `lazyday-product`：产品调研、PRD、用户故事、验收标准和发布说明。
- 增加 `lazyday-research`：联网调研、来源分级、证据摘要和决策备忘录。
- 增加 `lazyday-docs`：文档重写、知识库整理、变更说明和团队 SOP。
- 增加 `lazyday-ops`：例行任务、状态检查、告警摘要和运维 runbook。
- 增加更严格的版本发布、变更日志和兼容性矩阵。

### Long term

- 建立 Lazyday 插件生态：个人、团队和社区都可以贡献高质量 agent workflow。
- 提供面向 Codex、Claude Code 和其他 agent runtime 的统一插件生成工具。
- 将常见 AI 工作模式抽象为可组合、可评审、可安装的标准能力。
- 让更多非工程用户也能拥有自己的 Lazyday：用 AI 自动运行创造价值。

## Security and Trust

插件和 marketplace 是高信任组件。安装前请确认来源可信，并理解插件可能包含 skills、hooks、MCP servers、commands 或其他能影响本地环境的能力。

当前 `lazyday-coding`、`lazyday-vault` 和 `lazyday-worldcup` 都只通过插件 manifest 分发 skills，不声明 hooks、MCP servers 或 commands。`lazyday-worldcup` 的 skill 内包含可手动调用的 Python scripts/tests；除用户明确触发脚本或要求联网核验外，插件本身不主动访问外部服务。后续如果引入 hooks、MCP、自动化或外部连接，会在 manifest、README 和版本说明中明确列出权限边界、数据流和关闭方式。

## Contributing

欢迎贡献新的 Lazyday workflow，但请优先遵守这些原则：

- 先描述要解决的真实问题，再新增 skill。
- 每个 skill 都要有清晰触发场景、默认模式、禁止行为和交付形态。
- 尽量复用现有模板和工程纪律，不复制一份略有差异的规则。
- 新能力必须能被验证，至少能通过 manifest 校验和静态审查。
- 面向公开生态的文档要具体、可复制、少空话。

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).

The license covers the source code, plugin manifests, skills, scripts, templates, and documentation in this repository unless a file explicitly states otherwise. Third-party names, trademarks, service marks, APIs, event names, and data sources referenced by the project remain the property of their respective owners and are not licensed under this repository's MIT License.
