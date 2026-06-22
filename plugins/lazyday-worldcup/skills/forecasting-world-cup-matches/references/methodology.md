# 足球预测方法论

## 目录

1. 预测对象
2. 集成架构
3. 球队强弱先验
4. 进球与比分模型
5. 过程表现更新
6. 战术与语境调整
7. 爆冷与尾部风险评估
8. 市场信息
9. 单关投注门槛
10. 分层 2 串 1 组合
11. 置信度与校准
12. 淘汰赛与赛事模拟
13. 术语

## 1. 预测对象

不要把不同问题压缩成一个数字。

| 对象 | 含义 |
|---|---|
| 1X2 probability | 90 分钟加补时后的主胜、平、客胜概率 |
| Exact-score probability | 常规时间某个精确比分的概率 |
| Qualification probability | 晋级概率，包含加时和点球 |
| Title probability | 剩余路径中的夺冠概率 |
| Underdog win probability | 较弱一方 90 分钟取胜概率 |
| Favorite fail probability | 强方不胜概率，即平局加弱方胜 |
| Upset vulnerability score | 爆冷结构暴露审计分，不是事件概率 |
| Confidence score | 证据覆盖、模型一致性和不确定性的审计分，不是预测“正确率” |

概率语言必须校准：70% 表示类似预测中大约十次发生七次，不代表单场确定。

## 2. 集成架构

优先使用集成模型，因为单一模型无法同时覆盖球队质量、进球生成、阵容变化和赛事语境。

默认赛前首发未确认权重：

| 层 | 权重 | 主要输入 |
|---|---:|---|
| 国际去水市场 | 27% | 当前流动性 1X2/亚盘价格 |
| 中国体彩市场 | 8% | 官方当前 HAD 固定奖金 |
| Rating 先验 | 25% | Elo 类 rating、正式比赛强度 |
| 进球模型 | 20% | 对手调整后的攻防率 |
| 阵容与语境 | 10% | 可用性、休息、旅行、场地、气候 |
| 过程与战术 | 10% | xG profile、压迫、转换、定位球 |

这些是起始权重，不是固定真理。组件不可用时权重设为零，剩余权重重归一。不得用编造值替代缺失数据；缺失会降低置信度。

体彩层权重较小，因为固定奖金的返奖结构、更新节奏、流动性和参与者构成可能不同于国际市场共识。它是独立信号，不是整个市场层的第二份复制。

模型分歧用可用模型对所选结果概率的离散度衡量。大分歧是信息，不要静默平均成虚假的确定性。

## 3. 球队强弱先验

先验来自：

- Elo 或其他经对手和场地调整的 rating；
- 正式比赛权重大于友谊赛；
- 近期衰减，但不丢弃长期强弱；
- 阵容质量和深度，尤其是门将、中锋、中卫和推进核心；
- 洲际环境和预选赛路径强度；
- 主办地/场地效应，而非泛化 home flag。

FIFA 排名只能作为次级背景，因为其积分体系不直接优化比赛概率。不得把排名差直接换算为胜率。

赛事早期至少保留 70-80% 赛前长期先验，除非确认的阵容变化具有结构性影响。单场比赛噪声很大。

不得从叙事证据发布 Elo 点数更新。数字 rating 更新必须具备：

- 已识别赛前 rating；
- 模型预期结果；
- K-factor 和主场/场地处理；
- 结果编码和净胜球规则；
- 明确事件扭曲乘数。

缺少这些时，只发布 `upgrade`、`neutral` 或 `downgrade`，并用 `negligible`、`small`、`material` 之类定性幅度，不要伪造精度。

## 4. 进球与比分模型

估计双方常规时间 expected goals。一个透明概念式为：

```text
log(lambda_home) =
  competition_baseline
  + home_attack
  - away_defence
  + venue
  + squad
  + tactical_context

log(lambda_away) =
  competition_baseline
  + away_attack
  - home_defence
  + squad
  + tactical_context
```

用这些 rate 输入独立 Poisson 模型作为透明基线。可靠工具和样本足够时，低比分相关性应优先考虑 Dixon-Coles 或 bivariate-Poisson 修正。

用 `scripts/forecast_math.py` 生成可复现基线。阵容或战术不确定时，对每方 expected-goal rate 做约 0.15-0.25 的敏感性移动。

精确比分只是宽分布中的众数。即便强热门，最可能比分通常也只有 10-18% 左右概率。必须单独展示该概率。

## 5. 过程表现更新

评估机会和领地如何产生。

高价值指标：

- **xG：** 射门结果前的机会质量期望；
- **npxG：** 去点球 xG，更适合评估开放战可重复创造；
- **PSxG / xGOT：** 射正后质量，用于门将扑救和射门落点；
- **xThreat / possession value：** 推进价值；
- **field tilt：** 进攻三区控球或触球份额；
- **PPDA：** 每次防守动作允许对手传球数，压迫强度 proxy；
- 禁区进入、deep completions、big chances、倒三角、转换射门；
- 定位球 xG 和第一点率；
- 高位夺回和压迫后射门；
- 射门距离、角度、部位、助攻类型和防守压力。

孤立时低价值的指标：

- 没有领地或机会质量的控球率；
- 没有位置的原始射门数；
- 没有压力和推进语境的传球成功率；
- 没有事件语境的比分。

### 收缩

把赛事过程向先验收缩：

```text
updated_signal =
  prior_signal * (1 - w)
  + tournament_signal * w

w = reliable_equivalent_minutes / (reliable_equivalent_minutes + 720)
```

赛事早期过程权重上限约 20-25%。可靠等效分钟数要排除或折扣事件扭曲阶段。

### 特殊事件调整

- 区分红牌前 11v11、红牌后人数不等和恢复阶段。
- 不把点球 xG 当作普通机会创造；单独报告。
- 从终结评价中移除乌龙，同时保留相关进攻组织语境。
- 落后一方打开阵型后的进球下调权重。
- 标记改变净胜球但不代表过程优势的补时进球。
- 可用时用 PSxG - goals conceded 比较门将 goals prevented。
- 纪律问题只有多场模式时才当作球队特征。

## 6. 战术与语境调整

评估交互，而不是泛化风格标签：

- 高压对出球抗压；
- 防线高度对速度和直塞冲击；
- rest defence 对反击质量；
- 边后卫站位对边路一对一；
- 空中优势和二点球；
- 定位球传中对盯防和门将控制；
- 中路 overload 对中场间距；
- 低位防守破密集和传中依赖；
- 逆足限制、压迫陷阱、转换防守。

语境变量：

- 休息天数和加时负荷；
- 旅行距离、时差、海拔、温度、湿度；
- 已确认轮换和出线动机；
- 裁判牌/点球倾向，仅在样本和任命可靠时使用；
- 场地和天气；
- 小组积分形势导致的可能比赛状态。

调整幅度要小且有记录。避免重复计算已经嵌入市场价格或 rating 的信息。

## 7. 爆冷与尾部风险评估

每个候选预测都需要明确爆冷画像。不能选完热门后只加一句“足球什么都可能发生”。先从最终混合 1X2 分布量化两个事件：

```text
P(underdog wins) = 较弱一方 90 分钟胜率
P(favorite fails) = P(draw) + P(underdog wins)
```

然后用 `upset_risk_profile()` 计算单独的脆弱度审计分。每个语境因子按 0 到 1 评分，并记录证据：

- **Low-event probability：** 优先用模型 `P(total goals <= 2)`。事件越少，平局和一球爆冷路径越强。
- **Favorite process weakness：** 比分高于 npxG/领地表现、禁区进入差、出球脆弱或依赖不可持续终结。
- **Underdog transition/set-piece threat：** 速度冲击高防线、反击通道、空中错位、传中质量或第一点率。
- **Favorite availability risk：** 门将、中卫、推进核心或终结者不确定；替补深度弱。
- **Rotation/incentive risk：** 已出线、赛程拥挤、加时负荷或小组动机不对称。
- **Market disagreement：** 模型、国际市场和官方体彩 fair probability 的实质分歧。
- **Discipline variance：** 有证据的牌/点球暴露，加可靠裁判/样本语境；不得用单一轶事。

解释分数：

| 分数 | 标签 | 动作 |
|---:|---|---|
| 低于 20 | Low | 正常置信处理 |
| 20-34.9 | Guarded | 点名主要爆冷路径 |
| 35-49.9 | Elevated | 施加实质置信惩罚并做场景测试 |
| 50+ | High | 通常排除出高置信 top ten |

该分数不得覆盖模型事件概率。战术爆冷叙事只有被转换为记录的 xG、可用性、rating 或场景输入时，才改变 1X2 分布。避免同一伤病或市场移动被多个因子重复计算。使用返回的 0-1 `upset_vulnerability` 作为 confidence penalty 输入；0-100 `upset_vulnerability_score` 只用于展示。

证据允许时，每个热门至少跑三个场景：

1. 基准首发和比赛计划；
2. 热门不利场景，如轮换或中轴缺人；
3. 弱方成功场景，如先进球、定位球领先或持续转换进入。

报告哪个场景对热门胜率影响最大。淘汰赛和冠军预测要把这些爆冷分支传导到小组名次和签表路径，不要用一个全局折扣。

## 8. 市场信息

使用当前市场共识，优先流动性市场。记录获取时间和覆盖 bookmaker/exchange。

小数赔率转隐含概率并去水：

```text
raw_i = 1 / odds_i
fair_i = raw_i / sum(raw)
```

比较开盘和即时价格。盘口移动只有在确认是否反映首发新闻、流动性或过期异常后才作为证据。不得把单一过期 bookmaker 当作共识。

官方体彩固定奖金同样用完整互斥选项做倒数归一化。记录 raw probability sum 和 implied payout rate。1X2 HAD 必须只用主、平、客。HHAD 单独处理，因为它结算的是让球事件。

冠军 CHP 和冠亚军 FNL 必须在每个活跃市场内归一化。除非官方规则另有说明，FNL 组合按无序冠亚军对处理。不得把组合概率直接和单队夺冠概率比较。

用 total-variation distance 衡量国际市场与体彩的差异。距离超过 0.08 视为明显，超过 0.15 视为重大；使用前先检查新鲜度、首发新闻、队名匹配和销售状态。增加置信分歧惩罚，而不是强行平均成确定性。

## 9. 单关投注门槛

中国体彩单关推荐必须区分方向质量、下注价值和用户参与偏好。一个选择可以是最可能结果，但因为固定奖金太低而不是长期好投注。

使用三种明确推荐模式：

| 模式 | 目的 | 是否可下注 | 必需措辞 |
|---|---|---|---|
| `strict_value` | 长期正期望保护 | 只有通过 positive-value 门时 | 主价值推荐 |
| `controlled_participation` | 用户需要有推荐价值的稳健偏成长日常参与 | 可以，但有上限且明确 discretionary | 不是正期望推荐 |
| `backtest_observation` | 策略对照和校准 | 不推荐下注 | 仅回测/不推荐 |

不要把这些模式压成一个 "recommended" 标记。每日下注报告中，`strict_value` 是账本；除非用户明确要求“只按严格正期望出单”，否则 `controlled_participation` 是默认可执行模式。一天可以 `strict_value = no-bet`，但只要官方资格、方向质量、置信度、模型返还指数和爆冷风险门槛通过，就仍可发布稳健偏成长单关。

每个候选计算：

```text
break_even_probability = 1 / fixed_bonus
model_return_index = model_probability * fixed_bonus
probability_edge = model_probability - break_even_probability
expected_net_per_yuan = model_return_index - 1
```

输入存在时使用 helper：

```bash
python3 scripts/forecast_math.py \
  --single-ticket-probability P \
  --single-ticket-fixed-bonus B \
  --single-ticket-confidence C \
  --single-ticket-upset-vulnerability U
```

strict-value 门：

| 结果 | 条件 | 动作 |
|---|---|---|
| Positive value | 官方可执行；model_probability >= break_even_probability + 0.03；confidence >=60；upset vulnerability 低于 35，除非降 stake | 可作为 `strict_value` 投注 |
| Thin value | 官方可执行；model_return_index 在 0.97 到 1.03，或 probability edge 在 +/-3 pct 内 | `strict_value` 不下注；可发布低金额 `controlled_participation` |
| Negative value | model_return_index <0.97，或概率低于盈亏平衡超过 3 pct | `strict_value` 不下注/保留本金 |

controlled participation 必须同时满足：

- 官方单关资格来自最终 fresh fetch；
- 所选结果概率至少 55%；
- model return index 至少 0.80，防止把低质量赌注包装成参与；
- confidence 至少 55；
- upset vulnerability 至多 45%；
- 票旁边展示主要风险和每元期望净值；
- 100 单位本金中 stake 上限 30-50；
- 除非用户明确要求更高风险，否则不串关。

任一 controlled-participation 门失败时，保持 watch-only 或 backtest-only。不得用 controlled participation 掩盖弱方向或不合格票。

默认 stake：

| 模式 / 价值带 | 100 单位本金建议 stake |
|---|---:|
| `strict_value`，没有正价值选择 | 0 |
| `controlled_participation`，稳健偏成长但价值门失败单关 | 30-50 |
| `strict_value`，正常不确定性的正价值 | 40-70 |
| `strict_value`，低不确定性强价值 | 70-100 |

不得因为上一天盈利而加仓，除非有足够校准样本支持。前一日盈利只能支持保护本金，不能放宽价值门。

## 10. 分层 2 串 1 组合

只有在单场概率、置信度、爆冷画像和官方计算器资格都最终确定后，才构建组合。两场不同比赛：

```text
joint hit probability = P(leg 1) * P(leg 2)
at-least-one-loss probability = 1 - joint hit probability
combined fixed bonus = bonus 1 * bonus 2
model return index = joint probability * combined fixed bonus
```

乘法是独立性近似。若共享首发新闻或小组动机等相关信息，必须披露。模型返还指数不是保证收益，也继承概率估计误差。

用 `build_two_leg_portfolios()` 或 `scripts/forecast_math.py --portfolio-json selections.json`。每个 selection 必须包含 match/pool/outcome identifier、model probability、fixed bonus、confidence、upset vulnerability、market disagreement、retrieval age 和官方可用性字段。`retrieval_age_minutes` 是距最近一次成功 API 请求的时间，不是距奖金最后变化的时间。

| 层 | 必需门槛 | 选择目标 |
|---|---|---|
| Steady | 仅 HAD；每腿 probability >=65%；confidence >=60；upset <=35%；disagreement <=12%；retrieval age <=30 分钟；return index >=0.75 | 最高联合命中概率 |
| Growth | 每腿 probability >=55%；confidence >=55；upset <=45%；disagreement <=18%；combined bonus >=2.00；return index >=0.75；最多一腿 HHAD | 通过 return floor 后最高联合命中概率 |
| Aggressive | 每腿 probability >=35%；confidence >=45；upset <=60%；disagreement <=25%；combined bonus >=3.00；return index >=0.70 | 仍有支撑的最高组合奖金 |

这些标签是相对风险层，不是安全声明。没有组合过门时写 `no qualifying portfolio`。不得为凑满三层放宽门槛。优先 `2串1`；更多腿会放大失败概率，不属于这些定义。由于这些层使用命中率和风险门，它们不自动等于正期望推荐。`model_return_index < 1` 时，标为 controlled participation 或 backtest observation，不标 strict value。

## 11. 置信度与校准

置信排序应同时反映事件概率和预测完整性。

用脚本中的 `confidence_score()`，输入按 0-1：

- 所选结果概率；
- 证据质量；
- 模型分歧；
- 首发不确定性；
- 轮换风险；
- 数据缺失度；
- 爆冷脆弱度。

该分数用于报告排序，不是预测正确概率。必须同时发布所选结果概率和 confidence score。

高直接胜率不自动代表高置信。由低事件条件和可信弱方得分路线驱动的高爆冷脆弱度，必须降低排序。

建议标签：

| 分数 | 标签 |
|---:|---|
| 80-100 | 证据一致性很强 |
| 70-79.9 | 强 |
| 60-69.9 | 中等 |
| 低于 60 | 不纳入高置信榜，除非用户要求全覆盖 |

长期跟踪 Brier score、log loss、可靠性分箱和 sharpness。准确率本身会奖励过于保守或类别不均衡的预测。

维护 append-only 预测记录：

- forecast/model version；
- cutoff 和 publication timestamps；
- fixture identifier 和 status；
- 开赛前 1X2 概率；
- 精确比分分布或 top modes；
- 有效组件权重和缺失标记；
- underdog-win probability、favorite-fail probability 和爆冷因子；
- 最终 90 分钟结果；
- Brier score 和 log loss；
- 每个 ticket-like 输出的推荐模式；
- strict-value stake 和结算；
- controlled-participation stake 和结算；
- backtest-only stake 和结算；
- 与报告不同的用户实际出票。

赛果确定后用 `scripts/forecast_math.py` 的 `brier_score()` 和 `multiclass_log_loss()`。按概率分箱、赛事阶段、热门强度、爆冷脆弱度、首发确认状态和数据覆盖度复盘。爆冷路径是否发生可作为叙事审计，但校准必须基于发布时概率。只有有足够样本和 out-of-sample 理由时才调权。不得在手选成功样本上优化。

每日体彩复盘至少分四本账：

| 账本 | 含义 |
|---|---|
| Formal strict-value recommendation | 长期价值政策实际推荐 |
| Controlled-participation option | 有上限的每日参与选项 |
| Backtest-only option | 非推荐对照选择 |
| Actual issued ticket | 用户报告的打印/实际出票；提供时作为结算真相 |

不得把 no-bet strict tier 解释成模型没有方向意见。也不得用盈利的 controlled-participation 或 backtest-only 小样本直接宣称 strict value gate 错了。

## 12. 淘汰赛与赛事模拟

淘汰赛：

```text
P(home qualifies) =
  P(home wins in 90)
  + P(draw in 90) * P(home advances | draw after 90)
```

根据加时进球率和点球能力估计平局后的条件结果。点球大战高方差；门将和主罚手证据只能支持适度调整。

冠军/决赛模拟：

1. 从常规时间比分分布抽样剩余小组赛。
2. 应用官方排名规则。
3. 根据抽样小组名次生成真实签表。
4. 抽样淘汰赛常规时间、加时和点球。
5. 至少 20,000 次；需要稳定小概率时用 100,000 次。
6. 报告 Monte Carlo 不确定性，以及对阵容或小组名次假设的敏感性。

不得不检查签表半区就假设两个热门能在决赛相遇。

## 13. 术语

| 术语 | 用法 |
|---|---|
| xG differential | 机会质量差；评估可重复性时优先 npxG differential |
| xGOT / PSxG | 射正后质量，用于终结和门将 |
| PPDA | 压迫强度 proxy，通常越低越积极 |
| Field tilt | 进攻区域领地控制 |
| OPPDA | 球队面对的压迫环境，不同提供方定义可能不同 |
| Rest defence | 进攻后留在球后阻止转换的结构 |
| Game state | 当前比分导致的战术和风险变化 |
| De-vig | 移除 bookmaker margin |
| CLV | Closing-line value，用于评估预测信息质量 |
| Favorite fail | 热门 90 分钟不胜：平局加弱方胜 |
| Outright upset | 较弱一方直接赢，比 favorite fail 更窄 |
| Tail risk | 低概率但影响大的路径 |
| Joint hit probability | 所有串关腿都中的乘积近似 |
| Model return index | 联合概率乘组合奖金，不保证收益 |
| Brier score | 多分类平方概率误差，越低越好 |
| Log loss | 对自信错误惩罚强 |
