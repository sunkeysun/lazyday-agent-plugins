# 中文预测报告模板

## 页眉

```markdown
# 2026 世界杯未开赛比赛专业预测

数据截止：YYYY-MM-DD HH:MM:SS 时区（UTC offset）
最终状态复核：YYYY-MM-DD HH:MM:SS
符合条件的未开赛比赛：N 场
```

声明概率是模型估计，不是事实或保证。

包含稳定预测 ID 和模型版本，便于赛后评分。

## 模型摘要

| 层 | 有效权重 | 输入时间戳 | 覆盖范围 |
|---|---:|---|---|
| 国际去水市场 | | | |
| 中国体彩市场 | | | |
| 强弱 rating 先验 | | | |
| 进球模型 | | | |
| 阵容/语境 | | | |
| 过程/战术 | | | |

解释因缺失输入导致的权重重归一。

面向中国体彩报告时，必须单独展示状态分层，不得把官方获取成功和购买资格混在一起：

```markdown
## 官方体彩状态分层

| 层 | 状态 | 证据 | 动作 |
|---|---|---|---|
| Official fetch | success / failed | source_url, retrieved_at_utc, raw match count | 只可观察 fixed bonus |
| Execution eligibility | executable / none / partial | count, sellStatus, bettingSingle, bettingAllUp, all-up flags | 出票 / 观察 / 不下注 |
```

若官方获取成功但执行资格为 `none`，100 元方案必须为不下注或保留本金，不得把观察票写成推荐购买。

每日中国体彩下注报告必须显示推荐模式，避免一个“推荐”字段承载所有含义：

```markdown
## 推荐策略模式

| Mode | Action | Stake | Why |
|---|---|---:|---|
| strict_value | no-bet / stake | | |
| controlled_participation | no-bet / steady-growth capped single | | |
| backtest_observation | comparison only | | |
```

`strict_value` 是长期价值账本。每日下注报告中，`controlled_participation` 是通过稳健偏成长门槛后的默认可执行推荐；若未通过正期望门，必须明确标注。`backtest_observation` 绝不是购买建议。

## 单关价值门槛

```markdown
## 单关价值门槛

| Candidate | Fixed bonus | Model probability | Break-even probability | Model return index | Value action |
|---|---:|---:|---:|---:|---|
```

若没有候选高于盈亏平衡概率加安全边际，`strict_value` 的 100 元账本必须为不下注/保留本金。随后评估稳健偏成长 `controlled_participation` 门；通过时，把该有上限的票作为每日可执行推荐；失败时才发布不下注。controlled-participation 票必须包含预期亏损、最大亏损、官方资格，以及为什么方向仍合理。

100 元购买方案按以下顺序：

```markdown
## 100 元本金购买方案

### 方案A：strict_value
- 是否推荐执行：
- 总金额：
- 价值门结果：
- 预期净值：

### 方案B：controlled_participation
- 是否推荐执行：
- 总金额：
- 单关/过关：
- 最高返还：
- 最大亏损：
- 模型返还指数：
- 为什么不是 strict_value：

### 方案C：backtest_observation / higher-risk comparison
- 是否推荐执行：否
- 用途：回测对照
```

## 完赛过程复盘

| 比赛 | 赛果 | 11v11 过程 | 特殊事件 | 可重复性 | 预测更新 |
|---|---:|---|---|---|---|

可用时使用 xG/npxG、射门、禁区进入、field tilt、PPDA、定位球、门将表现、比赛状态、红牌、点球、乌龙和尾段进球语境。不得强行填不可用指标。

## 预测排序

按 confidence score 降序排序。

| 排名 | 比赛与开球 | 选择 | 1X2 概率 | 体彩 HAD/HHAD | xG | 精确比分 | 比分概率 | 爆冷脆弱度 | 置信度 |
|---:|---|---|---|---|---|---:|---:|---:|---:|

每场附：

```markdown
### N. Team A v Team B

- **已验证事实：** 强弱、可用性、场地/休息、当前状态。
- **过程/战术推断：** 可重复赛事表现和对位。
- **模型估计：** 1X2、预期进球、精确比分分布。
- **体彩：** 场次编号、HAD 奖金和 fair probabilities、HHAD 让球线和奖金、更新时间、销售状态、国际市场差异。
- **价值门：** 盈亏平衡概率、模型返还指数、每元期望净值，以及 positive value / thin value / no-bet。
- **爆冷画像：** 弱方直接赢概率、强方不胜概率、脆弱度分/标签、最可信爆冷路径。
- **爆冷证据：** 低事件概率、强方过程弱点、弱方转换/定位球路线、可用性、轮换/动机、纪律方差和市场分歧；只列有证据因子。
- **入选理由：** 独立层证据一致性。
- **最大风险：** 最能降低所选结果概率的场景，并尽量量化敏感性。
- **来源：** 带证据等级的直接链接。
```

精确比分必须同时给出概率。

## 分层 2 串 1 组合

仅在用户请求组合时使用。

| Tier | Leg 1 | Leg 2 | 官方玩法池 | 组合奖金 | 联合命中 | 至少一腿失手 | 模型返还指数 | 资格时间 |
|---|---|---|---|---:|---:|---:|---:|---|
| Steady | | | | | | | | |
| Growth | | | | | | | | |
| Aggressive | | | | | | | | |

每层附：

- 两腿各自概率、置信度和爆冷脆弱度；
- HAD/HHAD 让球线和结果解释；
- 比赛/玩法池销售状态、过关资格、固定奖金更新时间和获取时间；
- 明确说明 raw JSON 成功不是资格信号；
- 主要失败路线，以及两腿是否共享信息；
- 不满足门槛时写 `no qualifying portfolio`。

说明 `2串1` 需要两腿都中。蓝色 `单` 标记针对单场投注，不是 all-up 必需条件。不得使用“稳胆”“保本”“稳赢”。

## 淘汰赛补充

```markdown
- 90 分钟赛果概率：
- 90 分钟比分估计：
- 加时条件概率：
- 点球条件概率：
- 晋级概率：
```

不得把常规时间平局写成最终胜者。

## 冠军与冠亚军

| 球队 | 夺冠概率 | 进决赛概率 | 主要路径假设 | 主要风险 |
|---|---:|---:|---|---|

然后报告：

- 预测冠军；
- 预测亚军；
- 官方体彩 CHP 奖金和归一化概率；
- 官方体彩 FNL 组合奖金和归一化组合概率；
- 精确冠亚军组合概率；
- 决赛条件胜率；
- 使用的模拟和晋级规则；
- 对小组名次、阵容和重大伤病的敏感性；
- 每个预计决赛队伍的路径相关爆冷敏感性，包括最危险的早轮对手和不利场景。

## 校准说明

使用类似措辞：

> “高置信度”表示在当前信息和模型校准下，相对其他比赛具有更高的方向概率与证据一致性，不代表结果已经确定。比分预测是低基准率事件，其概率显著低于胜平负方向概率。

## 来源

只列实际使用的来源，包含直接链接和获取日期。区分已验证事实和分析推断。

## 赛后校准记录

赛果确定后追加：

```markdown
预测 ID:
90-minute outcome:
Published 1X2 probabilities:
Brier score:
Log loss:
Special-event review:
Published underdog-win probability:
Published favorite-fail probability:
Upset vulnerability band:
Did the identified upset path occur:
Strict-value settlement:
Controlled-participation settlement:
Backtest-only settlement:
Actual issued-ticket settlement:
Calibration action: none / investigate / change after sufficient sample
```

用户报告实际出票时，优先结算实际出票账本，并与报告中的正式推荐账本分开。不得赛后改写原预测。
