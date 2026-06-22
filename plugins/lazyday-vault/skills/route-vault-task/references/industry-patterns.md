# Industry Patterns

本文件记录 Lazyday Vault 的外部方法论依据。需要最新产品限制或能力时重新联网核对。架构如何落地见 `architecture.md`。

## LLM Wiki

Karpathy 的 LLM Wiki 模式强调：不要只在查询时对 raw documents 做一次性 RAG，而是让 LLM 增量维护一个持久、互链、会复利的 markdown wiki。raw sources 是不可变事实源，wiki 是 LLM 维护层，schema/AGENTS 指导工作流。该模式适合 Lazyday Vault 的核心：资料进入后要编译进长期结构，而不是每次问题都从零检索。

参考：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## PARA

PARA 的价值不在复杂分类，而在行动导向：Projects、Areas、Resources、Archives 四层足够简单，适合个人生活和工作的当前关注、长期责任、主题资源和归档内容。Lazyday Vault 使用 PARA 做顶层组织，但不把它作为唯一分类；同一 source 可以同时进入时间线、人物、项目、主题和问题索引。

参考：https://fortelabs.com/blog/para/

## NotebookLM

NotebookLM 的优势是以 sources 为中心做总结、问答、自动标签、web/Drive source discovery 和 Deep Research 导入。它的限制也提示 Lazyday Vault 的差异化：本地原始资料全量保留、wiki 持久累积、跨源长期时间线、可自定义 schema、可把答案写回知识库，并避免被固定 notebook/source quota 约束。

参考：https://support.google.com/notebooklm/answer/16215270

## Obsidian

Obsidian 的链接、反向链接和图谱证明了 plain markdown + local files + explicit links 的长期价值。Lazyday Vault 应当把 wiki 设计成普通 markdown 文件，以便人类能浏览、git 能版本化、agent 能维护。

参考：https://obsidian.md/help/links

## Readwise / Reader

Readwise/Reader 的重点是捕获阅读高亮、跨来源同步和定期回顾。Lazyday Vault 可借鉴“重点片段复现”和 spaced review，但不应只保存 highlights；必须保留完整原文、上下文和 source map。

## Zotero

Zotero 的强项是研究资料的 collect、organize、annotate、cite、share。Lazyday Vault 在论文、电子书和资料研究场景中要借鉴 source metadata、引用可靠性和原文定位，而不是只做聊天式总结。

参考：https://www.zotero.org/support/quick_start_guide

## Mem / Notion AI

Mem 和 Notion AI 强调低摩擦捕获、自动组织、自然语言召回和工作区问答。Lazyday Vault 应该借鉴“随手丢资料”的体验，但把可验证引用、raw 保留、可移植 markdown 和本地隐私作为更高优先级。
