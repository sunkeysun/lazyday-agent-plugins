# 中国体彩证据规范

中国体彩层只使用官方 Sporttery 域名：

- 比赛 HAD/HHAD：`https://www.sporttery.cn/jc/jsq/zqspf/`
- 冠军 CHP 和冠亚军 FNL：
  `https://www.sporttery.cn/jc/jsq/jcmc/?poolCode=CHP&sportsCode=FB&tCode=WCC`
- 页面暴露的官方 API 系列：
  - `/gateway/uniform/football/getMatchCalculatorV1.qry`
  - `/gateway/jc/tournament/getTournCalculatorV1.qry`

## 获取

1. 官方 Web API 返回 JSON 时优先使用 API。
2. 若 API 被 WAF 阻断，使用浏览器打开官方计算器页，检查渲染表格或同源网络响应。
3. 捕获页面可见更新时间，并同时获取 CHP 和 FNL 标签。
4. 临近开球比赛在发布前 10 分钟内复核。
5. 不绕过访问控制；不把第三方报价当作官方数据。

## 状态分层

官方体彩层必须拆成两个状态：

| 层 | 成功含义 | 不代表 |
|---|---|---|
| 获取 | 官方域名返回 JSON，且获取时间新鲜 | 当前可售、可单关、可过关或值得推荐 |
| 执行资格 | 所选结果在同一次新鲜 API 响应中通过销售和资格门 | 门店一定出票 |

不得用“体彩数据可用”代指“可以买这张票”。使用明确字段：

- `official_fetch_status: success_json`
- `execution_eligibility: none`
- `reason: count=0` 或 `reason: sellStatus=2, bettingSingle=0, bettingAllUp=0`

API 获取成功但 `--extract-options` 返回 `count: 0` 时，这是合法的官方市场状态，不是抓取失败。它必须阻断所有已发布的 2 串 1 方案和任何“当前可执行”推荐。若披露销售状态，raw fixed bonus 仍可作为市场观察，但必须标为观察或不下注，直到执行门通过。

## 国内足球计算器获取

足球 HAD/HHAD 计算器优先使用内置 fetcher：

```bash
python3 scripts/fetch_sporttery_calculator.py --extract-options --pretty
```

该命令调用官方 endpoint：

```text
https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry
```

脚本发送移动端 Sporttery referer 和 user-agent：

```text
Referer: https://m.sporttery.cn/
Accept: application/json, text/plain, */*
Accept-Encoding: identity
```

可选玩法池检查：

```bash
python3 scripts/fetch_sporttery_calculator.py --pool-code HAD --extract-options --pretty
python3 scripts/fetch_sporttery_calculator.py --pool-code HHAD --extract-options --pretty
```

默认保持 TLS 校验开启。若本地 Python 因证书链拒绝官方 endpoint，优先修复本机证书。需要在当前诊断会话继续核验官方数据时，优先使用只在证书错误时自动降级一次的命令：

```bash
python3 scripts/fetch_sporttery_calculator.py --extract-options --pretty --retry-insecure-on-cert-error
```

该命令会先走正常 TLS 校验；只有遇到 `CERTIFICATE_VERIFY_FAILED` 时才自动重试一次，并在输出 metadata 中写入 `tls_verified: false` 和 `tls_fallback_reason: certificate_verify_failed`。

若已经确认只是诊断本机证书链问题，也可显式使用：

```bash
python3 scripts/fetch_sporttery_calculator.py --extract-options --pretty --insecure
```

使用 `--retry-insecure-on-cert-error` 发生降级，或使用 `--insecure` 时，报告 `tls_verified: false` 作为获取风险备注，并保留官方 Sporttery 来源 URL。TLS 正常成功只保留在 raw metadata 中，不作为报告标题或决策信号。

若直接 API 返回 HTML、错误页或非 JSON，视为被阻断或不可用。不得把错误页解析成赔率。改用真实浏览器访问官方页面并检查同源网络响应；两者都失败时，标记官方计算器数据不可用。

为审计保留脚本输出 metadata：

- `source_url`;
- `referer`;
- `pool_code`，如有；
- `retrieved_at_utc`;
- 输出 `count`。

`tls_verified` 保留在 raw metadata 中；只有为 `false` 或影响来源可靠性时才在报告正文突出。

## 执行摘要

另行发布执行摘要：

- raw matches 数量；
- eligible all-up options 数量；
- 每个候选的 `sellStatus`、`bettingSingle`、`bettingAllUp`；
- 单关候选的盈亏平衡概率、模型返还指数和 value-gate 动作；
- 最终动作：`executable`、`watch_only` 或 `no_bet`。

执行资格不等于长期下注推荐。单关计算：

```text
break_even_probability = 1 / fixed_bonus
model_return_index = model_probability * fixed_bonus
```

若模型概率未达到 `methodology.md` 的盈亏平衡安全边际，即使该结果在售且可单关，也把 `strict_value` 动作标为 `no_bet_value_gate`。每日下注报告随后评估稳健偏成长的 `controlled_participation`：只有通过方法论文档门槛且清楚标注未满足长期价值门时，才可作为可执行推荐。`backtest_observation` 必须和任何可发给门店的方案分开。

若同一次新鲜获取保存了 raw JSON，提取命令仍为：

```bash
python3 scripts/forecast_math.py --sporttery-api-json response.json
```

两条路径必须产出相同的官方计算器资格字段，才可进入组合构建。

## 比赛记录

存储：

- 官方 match ID 和场次编号；
- 联赛/赛事、球队、开球时间、销售状态；
- HAD 主/平/客固定奖金；
- HHAD 让球线和主/平/客固定奖金；
- 显示时的单关资格；
- 执行动作：executable / watch-only / no-bet；
- 价值动作：positive_value / thin_value / no_bet_value_gate；
- 推荐模式：strict_value / controlled_participation / backtest_observation；
- 任一拟投注项的盈亏平衡概率和模型返还指数；
- controlled-participation 票的每元期望净值和最大亏损；
- controlled-participation 是否通过稳健偏成长门；
- 任一销售或资格标记失败时的明确不可执行原因；
- 官方更新时间和获取时间。

玩法池更新时间是最后一次奖金变更时间，不是当前报价年龄。新鲜度来自成功官方 API 获取时间，同时保留 pool 仍为 `Selling` 的更新时间。

按标准化队名加开球时间匹配比赛。模糊匹配有歧义时拒绝。不得为强行匹配而颠倒主客。

## 计算器方案资格

移动端/桌面端“查看方案”只是根据所选结果计算组合，不是独立专家推荐。

同一次新鲜 API 响应中同时满足以下条件时，才把选项视为当前可用于 2 串 1 计算：

- match `matchStatus` 为 `Selling` 且 `sellStatus` 为 `1`；
- pool `poolStatus` 为 `Selling`；
- 所选 HAD 或 HHAD 固定奖金存在且大于 1；
- `allUp`、`bettingAllup`、`cbtAllUp` 均启用；
- 开球和销售截止未过。

蓝色 `单` 标记对应单关资格，不是 `2串1` 必需条件。串关必须使用两场不同比赛。计算器页面不接受同一场的 HAD 和 HHAD 组合。

称为“官方计算器 eligible”，不要称为“保证可买”。最终出票取决于门店、销售截止、系统状态和票面。

保存 API JSON 后运行：

```bash
python3 scripts/forecast_math.py --sporttery-api-json response.json
```

该命令为每个 eligible HAD/HHAD 结果输出官方场次、玩法池、让球线、固定奖金、单关/过关标记和来源更新时间。

## 冠军/冠亚军记录

存储 pool code、tournament code、selection number、展示名、状态、固定奖金、销售截止、官方更新时间和获取时间。

- `CHP`：每队一个冠军选项。
- `FNL`：冠亚军二元组合，除非官方规则说明有顺序。
- 从活跃概率归一化中排除无效、停止、退款或已淘汰选项，但在证据日志中保留其状态。

## 概率换算

完整活跃市场：

```text
raw_i = 1 / fixed_bonus_i
fair_i = raw_i / sum(raw)
implied_payout_rate = 1 / sum(raw)
```

对市场中每个活跃选项运行 `python3 scripts/forecast_math.py --fixed-bonus ...`。报告 raw 奖金和 fair probabilities。

HAD 与 HHAD 是不同事件，不得合并隐含概率。冠军概率与 FNL 组合概率也是不同对象。

## 失败规则

- API WAF 加渲染页失败：标记官方体彩数据不可用。
- JSON 获取成功但 `count: 0`：标记官方获取可用但执行资格不可用；不发布 all-up 组合。
- TLS metadata 只证明传输检查。正常报告不突出，除非校验失败或被禁用；不得用它证明可售或可执行。
- 缺更新时间：引用获取时间并施加新鲜度惩罚。
- 停止或暂停市场：展示状态，但模型权重为零。
- HAD 不可用但 HHAD 可用：不分配体彩 1X2 权重；HHAD 只做净胜球一致性检查并施加缺失惩罚。
- 国际市场差异大：先核对队名和时间戳，再保留两类信号并增加分歧惩罚。
- 任一资格标记缺失或冲突：排除出分层组合，不假设可组合。
