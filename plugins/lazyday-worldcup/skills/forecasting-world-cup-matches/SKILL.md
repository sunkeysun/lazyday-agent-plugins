---
name: forecasting-world-cup-matches
description: 用于研究或预测 FIFA 世界杯比赛、排序未开赛场次、分析完赛过程表现、评估爆冷风险、构建体彩 2 串 1 组合、估算概率，或基于当前证据预测冠亚军。默认只读研究和预测；除非用户明确要求写报告到文件，不创建或修改文件；不用于非世界杯赛事、无当前来源核验的实时预测，或保证式投注建议。
---

# 世界杯比赛预测

产出可审计的预测，不产出保证。所有事实必须验证；概率是估计，战术判断是推断。

## 执行约定

默认只读。除非用户明确要求写入指定文件，不创建、修改或删除文件。

运行本 skill 自带脚本前，先把工作目录切到本 skill 根目录，也就是包含 `SKILL.md`、`references/` 和 `scripts/` 的目录；下文所有 `python3 scripts/...` 命令都以该目录为当前工作目录。若宿主环境不能切换目录，必须使用等价的绝对脚本路径。

## 必需流程

1. 设定绝对数据截止时间和用户时区。所有进行中的赛事预测都必须浏览当前来源。
2. 阅读 [data-and-evidence.md](references/data-and-evidence.md)。用官方赛程和一个独立来源核对赛程；排除已开赛或已失效比赛。
3. 面向中国体彩的报告必须阅读 [china-sporttery.md](references/china-sporttery.md)。获取当前官方体彩比赛、冠军、冠亚军固定奖金。国内足球计算器优先使用 `python3 scripts/fetch_sporttery_calculator.py --extract-options --pretty`。把官方 JSON 获取和投注执行资格分开判断：`count: 0`、`sellStatus != 1`、`bettingSingle != 1` 或 `bettingAllUp != 1` 表示当前没有可执行体彩推荐，即使官方获取成功。不得用第三方报价替代缺失的官方数据。
4. 阅读 [methodology.md](references/methodology.md)。收集强弱先验、过程表现、阵容/语境、战术、国际去水市场和官方体彩概率。缺失组件设为零权重并重归一；同时降低置信度。
5. 分析完赛比赛时必须看过程和特殊事件。区分 11v11、红牌/人数不等阶段；单独隔离点球、乌龙、比赛状态进球、门将方差和可重复机会创造。
6. 输入存在时使用 `python3 scripts/forecast_math.py --home-xg X --away-xg Y --odds H D A`。完整体彩市场可用 `python3 scripts/forecast_math.py --fixed-bonus ...`。必须区分：
   - 90 分钟胜平负概率；
   - 精确比分概率；
   - 淘汰赛晋级概率；
   - 弱方 90 分钟直接取胜概率；
   - 强方不胜概率，包含平局；
   - 爆冷脆弱度分，是审计分数，不是事件概率；
   - 置信度分，是审计分数，不是事件概率。
7. 每个候选都必须建立爆冷风险画像。从混合 1X2 概率开始，再评估低事件概率、强方过程弱点、弱方转换/定位球威胁、强方可用性风险、轮换/动机风险、市场分歧和纪律方差。可使用：
   `python3 scripts/forecast_math.py --outcome-probabilities H D A --low-event-probability U25 --favorite-process-weakness X --underdog-transition-set-piece-threat X --favorite-availability-risk X --rotation-incentive-risk X --market-disagreement X --discipline-variance X`。
8. 将返回的 0-1 `upset_vulnerability` 输入 `confidence_score()`，不要使用 0-100 展示分。按该惩罚后的置信度排序，最多返回十场。高热门概率本身不足以入选。
9. 面向中国体彩的单关推荐必须先区分推荐模式：
   - `strict_value`：长期价值保护；要求当前官方可执行，且模型概率高于盈亏平衡并达到安全边际。
   - `controlled_participation`：稳健偏成长的每日参与档；当用户需要有推荐价值的日常出票方案时使用。即使价值门失败，也必须通过官方可执行、方向合理、置信度、爆冷风险和最低模型返还指数门槛，并清楚标注期望值为负或不确定。
   - `backtest_observation`：只用于非推荐回测对照。
   计算 `break_even_probability = 1 / fixed_bonus` 和 `model_return_index = model_probability * fixed_bonus`。输入存在时使用 `python3 scripts/forecast_math.py --single-ticket-probability P --single-ticket-fixed-bonus B --single-ticket-confidence C --single-ticket-upset-vulnerability U`。每日下注报告中，`strict_value` 保留为长期账本，但默认可执行推荐应选择通过稳健偏成长门槛的 `controlled_participation`。如果 strict 和 controlled 两档都失败，才发布不下注。
10. 用户请求 2 串 1 时，重新获取官方计算器数据：`python3 scripts/fetch_sporttery_calculator.py --extract-options --pretty`。若 `count` 为 `0`，停止构建组合，并说明官方 API 可达但当前没有 HAD/HHAD 过关资格。若同一次新鲜获取已保存 raw response，运行 `python3 scripts/forecast_math.py --sporttery-api-json response.json` 提取 eligible HAD/HHAD。把模型字段 join 到候选上，再运行 `python3 scripts/forecast_math.py --portfolio-json selections.json`，最多发布一个 `steady`、`growth`、`aggressive` 组合；没有合格组合时明确说明。
11. 冠军/冠亚军预测必须模拟或近似剩余赛程。报告路径相关爆冷敏感性、夺冠概率、进决赛概率、精确冠亚军组合概率、决赛条件胜率，以及可用时的官方体彩 CHP/FNL 固定奖金。
12. 改权重或投注策略前，先用 Brier score、log loss、可靠性分箱、热门强度/爆冷分箱、value-gate 结果、controlled-participation 结果和用户实际出票记录评分。不要用小样本或选择性样本调参。
13. 发布前立即复核开球/状态、计算器资格和引用奖金。报告最终官方获取状态与最终执行资格状态。对所有可执行层移除已开赛、已停止或不合格选项；对 `strict_value` 移除价值门失败选项。价值门失败选项只可在 `controlled_participation` 或 `backtest_observation` 中出现，并必须展示预期净值、最大亏损和非长期正期望身份。
14. 使用 [output-template.md](references/output-template.md)，包含直接链接、证据等级、风险、赔率/奖金、时间戳、明确爆冷路径、价值门结果和分层组合。

## 硬性禁区

- 不得把预测称为事实、确定、保证、稳胆、锁定或无风险。
- 不得从传闻推断伤停或禁赛已确认。
- 不得只用 FIFA 排名作为强弱模型。
- 没有赛前 rating、预期结果、K-factor、结果编码和事件调整时，不得发布 rating 分数变化；只能做定性更新。
- 不得把控球率或原始射门数当作 xG。
- 不得因一场赛事大幅更新球队强弱。
- 不得用精确比分概率当作赛果置信度。
- 不得把 `favorite fail-to-win` 等同于弱方直接赢。
- 不得把爆冷脆弱度分当作概率。
- 不得因叙事精彩就抬高爆冷概率；只有记录到 xG、阵容、rating 或场景输入时，才能改变事件概率。
- 不得说爆冷不可能；强热门也有非零尾部风险。
- 不得把体彩固定奖金当作校准概率，必须对完整互斥市场归一化。
- 不得把让球体彩价格当作普通 1X2 概率。
- 不得静默使用过期、停止、暂停或第三方体彩价格。
- 不得说计算器资格保证门店出票。
- 不得在一个串关中组合同一场的 HAD 和 HHAD。
- 不得把不满足概率、置信度、爆冷、分歧、新鲜度和 HAD-only 门槛的组合标成 `steady`。
- 不得只按固定奖金排序组合。必须发布联合命中概率、至少一腿失手概率和模型返还指数。
- 不得暗示正模型边际、低固定奖金或 `单` 图标意味着盈利或安全。
- 不得仅因为某选择大概率命中就推荐下注。长期 `strict_value` 推荐必须高于固定奖金盈亏平衡概率并达到安全边际。`controlled_participation` 必须明确不是正期望推荐。
- 面向中国的每日下注报告不得保守到 strict value 失败就默认不出单；必须先评估稳健偏成长参与门，并在通过时发布有金额上限的方案。
- 不浏览当前信息时，不得发布当前预测；只能说明方法。
- 证据质量不足时，不得强行凑满十场。

## 最终审计

回复前确认：

- 概率分布在四舍五入误差内归一到 100%；
- 每个数字都有输入或来源；
- rating 更新可复现；
- 事实、估计和推断分开；
- 阵容、赔率/奖金和状态时间戳足够新；
- 展示体彩销售状态、固定奖金、场次编号和获取时间；
- 展示推荐模式：`strict_value`、`controlled_participation` 或 `backtest_observation`；
- 披露国际市场和体彩市场分歧；
- 每场都有强弱、过程/战术、语境、最大风险和具体爆冷路径；
- 分别展示弱方赢和强方不胜概率；
- 置信排序已纳入爆冷脆弱度，且不把它误标为概率；
- 每个组合腿都在售、可过关、新鲜且来自不同比赛；
- `steady`/`growth`/`aggressive` 标签符合 methodology 门槛；
- 展示组合奖金、联合概率、失手概率和计算器获取时间；
- 每日回测分开记录正式 strict-value 推荐、controlled-participation 选项、backtest-only 选项和用户实际出票；
- 精确比分显示其低基准率概率；
- 淘汰赛选择区分 90 分钟、加时和点球。
