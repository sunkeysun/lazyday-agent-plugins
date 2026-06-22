# Lazyday Worldcup

`lazyday-worldcup` packages the `forecasting-world-cup-matches` skill as a local Lazyday plugin for Codex and Claude Code.

It is intended for World Cup forecasting work where the agent must separate current facts, model estimates, and tactical inference. The workflow covers live fixture checks, official Sporttery data retrieval, de-vigged probabilities, upset-risk auditing, 2-leg portfolio construction, and champion or finalist forecasts.

## Skills

| Skill | When to use | Output |
| --- | --- | --- |
| `forecasting-world-cup-matches` | 预测世界杯比赛、排序未开赛场次、复盘已完赛表现、评估爆冷风险、构建体彩 2 串 1、预测冠亚军 | 带时间截点、来源分级、概率估计、风险路径、体彩可售状态和验证提醒的预测报告 |

## Included Files

- `skills/forecasting-world-cup-matches/SKILL.md`
- `skills/forecasting-world-cup-matches/agents/openai.yaml`
- `skills/forecasting-world-cup-matches/references/`
- `skills/forecasting-world-cup-matches/scripts/`
- `skills/forecasting-world-cup-matches/tests/`

## Boundaries

- Forecasts are estimates, not guarantees.
- Live tournament requests must browse or otherwise verify current official sources before publishing.
- Sporttery prices must come from official data when used for China-facing recommendations.
- Generated cache files and local macOS metadata are intentionally excluded from the plugin package.
