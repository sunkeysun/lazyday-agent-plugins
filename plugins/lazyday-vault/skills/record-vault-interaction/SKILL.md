---
name: record-vault-interaction
description: 中文 Lazyday Vault 交互记录技能。用于把用户与知识库的问答、反馈、修正、确认、研究过程、复盘结论和“以后记住/把这次入库”等交互作为新的 source 写入 vault；必须区分 user_assertion、assistant_answer、tool_observation、decision、correction，记录 parent_sources、derived_from、supersedes、conflicts_with，避免把 assistant 旧回答当作外部事实源造成自我强化循环。
---

# 记录交互

## 目标

把有价值的 vault 交互保存为一等 source，让后续可以追踪“用户问过什么、当时怎么回答、引用了哪些资料、用户后来如何纠正、最终确认了什么”。该 skill 解决的是交互记忆和冲突处理，不替代 `answer-vault-question`、`vault-deep-research` 或 `integrate-knowledge`。

## 读取协议

先读取：

- `../route-vault-task/references/architecture.md`
- `../route-vault-task/references/vault-protocol.md`
- `../route-vault-task/references/retrieval-protocol.md`
- `../route-vault-task/references/interaction-conflict-protocol.md`

## 何时记录

默认不要偷偷记录所有对话全文。以下情况应记录：

- 用户明确说“记住这个”“把这次问答入库”“以后以这个为准”“这次修正保存下来”。
- 用户纠正了旧答案、旧标签、旧项目归属、旧时间线或旧 wiki 结论。
- 一次问答产生可复用结论、项目决策、故障案例、年度复盘、研究报告。
- 用户开启了“vault 交互默认入库”的工作方式。

## Source 角色

每个 interaction source 必须标注角色：

- `user_assertion`：用户原话、偏好、经历、确认。
- `assistant_answer`：assistant 基于资料组织的回答。
- `tool_observation`：工具读到的文件、日志、命令输出、验证结果。
- `decision`：用户确认的结论、分类、行动或规则。
- `correction`：用户对旧回答、wiki、标签、项目归属或事实解释的纠错。

## 工作流

1. 明确记录范围：本轮、某段对话、某个回答、某条用户修正或某个决策。
2. 生成 `source_id`，`source_type: interaction`。
3. 写入 `raw/YYYY/MM/<source_id>/original/interaction.md`，保留原话、回答、引用和上下文摘要。
4. 创建 manifest，至少记录：
   - `interaction_kind`
   - `source_role`
   - `parent_sources`
   - `derived_from`
   - `supersedes`
   - `superseded_by`
   - `conflicts_with`
   - `conflict_status`
   - `writes_to`
5. 如果交互包含重要事实、修正或决策，创建 claim，并记录 `claim_ids`、`supersedes_claims`、`conflicts_with_claims`。
6. 如果用户一句话同时纠错和设规则，拆分 correction claim 和 decision claim。
7. 更新 `indexes/interaction-index.md` 和 `indexes/claim-index.md`。
8. 如果存在冲突或修正，更新 `indexes/conflict-index.md`。
9. 追加 `logs/event-ledger.jsonl`。
10. 如有高价值结论，交给 `integrate-knowledge` 更新相关 wiki 页面。

## 冲突规则

- 用户 correction 不删除旧 answer；它创建新 source，并让旧 answer 进入 superseded 或 conflict 状态。
- assistant answer 不能单独作为外部事实证据；必须回到 `parent_sources`。
- `parent_sources` 只放证据 source；`derived_from` 才记录问答链、研究链和处理链。
- 对用户偏好、意图、个人经历，用户后续明确修正优先级最高。
- 对文件、日志、测试、命令结果，tool_observation 优先级高于 assistant 推断。
- 无法判定的冲突进入 `conflict-index.md` 的 open 状态。

## 防递归规则

- 记录本次交互后，不要自动再次把“记录动作本身”记录成新 source。
- interaction source 可以被检索，但引用外部事实时应优先跳转到 parent sources。
- answer 的总结可以写入 `answers/questions/`，但 wiki 事实段必须引用原始 source 或用户 correction。

## 输出格式

```markdown
**交互记录**
- source_id:
- interaction_kind:
- source_role:
- raw path:
- parent_sources:

**冲突处理**
- supersedes:
- conflicts_with:
- supersedes_claims:
- conflicts_with_claims:
- conflict_status:

**已更新**
- interaction-index:
- claim-index:
- conflict-index:
- wiki/index:

**下一步**
- 推荐 skill:
- 待确认：
```
