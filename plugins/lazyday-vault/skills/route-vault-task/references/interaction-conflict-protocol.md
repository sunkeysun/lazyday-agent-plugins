# Interaction And Conflict Protocol

## 目标

Vault 会把问答、修正、反馈和决策也作为 source。这个能力必须防止两类问题：

- 把 assistant 旧回答当作外部事实，形成自我强化。
- 只做 source 级冲突，导致一个 source 中的无关内容被过度失效。

## 证据角色

`source_role` 决定证据优先级：

- `user_assertion`：用户原话、偏好、经历、确认。
- `assistant_answer`：assistant 当时如何回答；不能单独证明外部事实。
- `tool_observation`：工具读取文件、日志、命令、测试或系统状态的结果。
- `decision`：用户确认的规则、分类、行动或项目归属。
- `correction`：用户对旧 answer、wiki、标签、时间线或事实解释的纠错。

用户关于自己经历、偏好、意图的明确修正，优先于旧 assistant 推断。工具观测关于文件、日志和验证结果，优先于 assistant 推断和无来源总结。

## parent_sources 与 derived_from

- `parent_sources` 只记录支持事实断言的证据 source。
- `derived_from` 记录交互链、研究链或处理链。
- 一个 answer 的 `parent_sources` 是它引用的 raw、extract、tool_observation、user_assertion 或 correction。
- 旧 answer 只有在问题是“当时怎么回答过”时作为 direct evidence；如果问题是“事实到底是什么”，必须跳回旧 answer 的 `parent_sources`。
- 缺少 `parent_sources` 或 parent 已失效的 answer，只能标为 historical answer，不能作为事实证据。

## Claim 级冲突

优先创建 claim 关系，而不是只写 source 关系。

```markdown
- claim_id:
- source_id:
- locator:
- applies_to_locator:
- claim_type: fact | inference | decision | correction | preference | tool-observation
- statement:
- evidence_strength: direct | derived | synthesized | inferred | unsupported
- status: active | superseded | disputed | resolved | retracted
- parent_sources:
- supersedes_claims:
- conflicts_with_claims:
```

当用户纠正旧结论时：

1. 为用户纠正创建 `source_role: correction` 的 interaction source。
2. 为具体纠正内容创建 correction claim。
3. 将旧 claim 标记为 `superseded` 或 `disputed`。
4. 在 `claim-index.md` 和 `conflict-index.md` 写明 locator，不要让整个旧 source 失效。

## correction 与 decision 拆分

如果用户一句话同时包含纠错和新规则，拆成两个 source 或两个 claim：

- correction claim：指出旧内容哪里错。
- decision claim：确认以后如何归类、命名、执行或解释。

decision 可以 `derived_from` correction，但不要把 decision 写成“证明旧事实错误”的唯一证据。

示例：

```text
用户：不是 A 项目，是 B 项目；以后这类客户日志都归到 B 项目。
```

应建模为：

- correction：旧 claim 的项目归属从 A 更正为 B。
- decision：后续类似客户日志默认归入 B 项目，除非 source 显示其他项目。

## 冲突状态

- `open`：存在矛盾，尚未确认。
- `disputed`：有反证，但证据强度或适用范围未定。
- `resolved`：用户确认、raw evidence 或 tool_observation 足以判断。
- `superseded`：旧 claim 被新 claim 替代，但旧 source 保留。
- `retracted`：用户撤回自己之前的断言或确认。

能直接关闭冲突的情况：

- 用户明确确认自己偏好、个人经历、项目归属或决策。
- raw source 或 tool_observation 直接证明日志、文件、时间戳、测试结果。
- OCR/转写错误经原图、音视频或人工校对确认。

必须保持 open 的情况：

- 两个 raw source 对同一事件互相矛盾且无更高优先级证据。
- 用户修正只覆盖部分内容，旧 source 还有其他 claim。
- iCloud conflict 副本内容不同，无法判断哪个版本是最终版本。

## iCloud 冲突文件

iCloud 冲突副本不是可静默合并的普通重复文件。处理方式：

1. 为每个冲突副本建立独立 source，记录文件名、mtime、size、hash、device_hint、raw path。
2. 在原 source 或相关 source 的 manifest 写 `sync_conflict: detected`。
3. 在 `conflict-index.md` 写入冲突线程。
4. 如果内容差异只在日志追加尾部，可建议合并，但需先展示差异和推荐方案。
5. 无用户确认时，不删除任一副本，不把任一副本作为唯一最终事实。

## 查询旧交互

回答“我上次问了什么”“你当时怎么答”“后来我纠正过什么”时，必须查：

- `indexes/interaction-index.md`
- `indexes/conflict-index.md`
- `indexes/claim-index.md`
- 相关 interaction manifests
- 旧 answer 的 `parent_sources`

输出时明确：

- 当时回答是什么。
- 当时引用了哪些 parent sources。
- 后续是否被 correction、decision、conflict 或 superseded claim 影响。
- 当前应以哪个 active claim 为准。
