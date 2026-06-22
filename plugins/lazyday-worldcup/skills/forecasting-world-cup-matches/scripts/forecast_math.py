#!/usr/bin/env python3
"""足球比赛预测的确定性概率辅助工具。"""

from __future__ import annotations

import argparse
import json
import math
from itertools import combinations
from typing import Iterable, Sequence


def _validate_probability(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} 必须在 0 和 1 之间")
    return value


def _normalize(values: Sequence[float]) -> list[float]:
    total = sum(values)
    if total <= 0.0:
        raise ValueError("概率总和必须为正")
    return [value / total for value in values]


def _is_enabled(value: object) -> bool:
    return value is True or value == 1 or str(value).strip() == "1"


def devig_1x2(decimal_odds: Sequence[float]) -> list[float]:
    """通过小数赔率倒数归一化移除 bookmaker margin。"""
    if len(decimal_odds) != 3:
        raise ValueError("1X2 odds 必须正好包含三个值")
    odds = [float(value) for value in decimal_odds]
    if any(not math.isfinite(value) or value <= 1.0 for value in odds):
        raise ValueError("decimal odds 必须有限且大于 1")
    return _normalize([1.0 / value for value in odds])


def implied_probabilities_from_fixed_bonus(
    fixed_bonus: Sequence[float],
) -> dict[str, object]:
    """将互斥 fixed bonus 转为 fair probabilities。"""
    if len(fixed_bonus) < 2:
        raise ValueError("fixed bonuses 必须至少包含两个值")
    bonuses = [float(value) for value in fixed_bonus]
    if any(not math.isfinite(value) or value <= 1.0 for value in bonuses):
        raise ValueError("fixed bonuses 必须有限且大于 1")

    raw_probabilities = [1.0 / value for value in bonuses]
    raw_probability_sum = sum(raw_probabilities)
    return {
        "raw_probabilities": raw_probabilities,
        "raw_probability_sum": raw_probability_sum,
        "payout_rate": 1.0 / raw_probability_sum,
        "fair_probabilities": _normalize(raw_probabilities),
    }


def single_ticket_value_gate(
    model_probability: float,
    fixed_bonus: float,
    *,
    confidence: float = 60.0,
    upset_vulnerability: float = 0.0,
    official_eligible: bool = True,
    safety_margin: float = 0.03,
) -> dict[str, object]:
    """为 Sporttery 单关候选分类 strict value 与稳健偏成长参与模式。

    strict value 保护长期期望值。稳健偏成长参与模式是单独标注的日常报告
    出单选项，避免在存在合理方向时长期变成 no-bet。
    """
    model_probability = _validate_probability(
        model_probability, "model_probability"
    )
    upset_vulnerability = _validate_probability(
        upset_vulnerability, "upset_vulnerability"
    )
    safety_margin = _validate_probability(safety_margin, "safety_margin")
    fixed_bonus = float(fixed_bonus)
    confidence = float(confidence)
    if not math.isfinite(fixed_bonus) or fixed_bonus <= 1.0:
        raise ValueError("fixed_bonus 必须有限且大于 1")
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 100.0:
        raise ValueError("confidence 必须在 0 和 100 之间")

    break_even_probability = 1.0 / fixed_bonus
    model_return_index = model_probability * fixed_bonus
    probability_edge = model_probability - break_even_probability
    expected_net_per_yuan = model_return_index - 1.0

    positive_value = (
        official_eligible
        and probability_edge >= safety_margin
        and confidence >= 60.0
        and upset_vulnerability < 0.35
    )
    thin_value = (
        official_eligible
        and not positive_value
        and (0.97 <= model_return_index <= 1.03 or abs(probability_edge) <= 0.03)
    )
    controlled_participation = (
        official_eligible
        and not positive_value
        and model_probability >= 0.55
        and model_return_index >= 0.80
        and confidence >= 55.0
        and upset_vulnerability <= 0.45
    )

    if not official_eligible:
        value_action = "not_officially_eligible"
        strict_action = "no_bet_ineligible"
        participation_action = "watch_only_ineligible"
        stake_units = [0, 0]
    elif positive_value:
        value_action = "positive_value"
        strict_action = "strict_value_stake"
        participation_action = "strict_value_stake"
        stake_units = [40, 70]
    elif thin_value:
        value_action = "thin_value"
        strict_action = "strict_value_no_bet"
        participation_action = "low_stake_discretionary"
        stake_units = [20, 40]
    elif controlled_participation:
        value_action = "no_bet_value_gate"
        strict_action = "strict_value_no_bet"
        participation_action = "steady_growth_participation"
        stake_units = [30, 50]
    else:
        value_action = "no_bet_value_gate"
        strict_action = "strict_value_no_bet"
        participation_action = "watch_only_or_no_bet"
        stake_units = [0, 20]

    return {
        "official_eligible": official_eligible,
        "model_probability": model_probability,
        "fixed_bonus": fixed_bonus,
        "break_even_probability": break_even_probability,
        "model_return_index": model_return_index,
        "probability_edge": probability_edge,
        "expected_net_per_yuan": expected_net_per_yuan,
        "confidence": confidence,
        "upset_vulnerability": upset_vulnerability,
        "safety_margin": safety_margin,
        "value_action": value_action,
        "strict_value_action": strict_action,
        "controlled_participation_action": participation_action,
        "suggested_stake_units_from_100": stake_units,
    }


def market_disagreement(probability_sets: Iterable[Sequence[float]]) -> float:
    """返回 0-1 标尺上的最大两两 total-variation distance。"""
    normalized_sets = []
    for probabilities in probability_sets:
        if len(probabilities) < 2:
            raise ValueError("每组 probability set 必须至少包含两个值")
        normalized_sets.append(
            _normalize(
                [
                    _validate_probability(value, "market probability")
                    for value in probabilities
                ]
            )
        )
    if len(normalized_sets) < 2:
        return 0.0
    if len({len(values) for values in normalized_sets}) != 1:
        raise ValueError("probability sets 长度必须一致")

    return max(
        0.5 * sum(abs(left - right) for left, right in zip(first, second))
        for first_index, first in enumerate(normalized_sets)
        for second in normalized_sets[first_index + 1 :]
    )


def _poisson_probability(rate: float, goals: int) -> float:
    return math.exp(-rate) * (rate**goals) / math.factorial(goals)


def poisson_forecast(
    home_xg: float,
    away_xg: float,
    max_goals: int = 10,
    top_n: int = 5,
) -> dict[str, object]:
    """返回归一化的独立 Poisson 90 分钟比分预测。"""
    home_xg = float(home_xg)
    away_xg = float(away_xg)
    if not math.isfinite(home_xg) or not math.isfinite(away_xg):
        raise ValueError("expected goals 必须有限")
    if home_xg < 0.0 or away_xg < 0.0:
        raise ValueError("expected goals 不能为负")
    if max_goals < 1:
        raise ValueError("max_goals 至少为 1")
    if top_n < 1:
        raise ValueError("top_n 至少为 1")

    home_probs = [_poisson_probability(home_xg, goals) for goals in range(max_goals + 1)]
    away_probs = [_poisson_probability(away_xg, goals) for goals in range(max_goals + 1)]
    raw_scores = [
        (home_goals, away_goals, home_prob * away_prob)
        for home_goals, home_prob in enumerate(home_probs)
        for away_goals, away_prob in enumerate(away_probs)
    ]
    retained_mass = sum(probability for _, _, probability in raw_scores)
    if retained_mass <= 0.0:
        raise ValueError("比分分布没有保留的概率质量")

    scores = [
        (home_goals, away_goals, probability / retained_mass)
        for home_goals, away_goals, probability in raw_scores
    ]
    home_win = sum(probability for home, away, probability in scores if home > away)
    draw = sum(probability for home, away, probability in scores if home == away)
    away_win = sum(probability for home, away, probability in scores if home < away)
    under_2_5_probability = sum(
        probability for home, away, probability in scores if home + away <= 2
    )
    outcomes = _normalize([home_win, draw, away_win])

    # 第二排序键把数学上相等的众数推向更接近 expected-goal 向量的比分，
    # 避免依赖循环顺序。
    ranked_scores = sorted(
        scores,
        key=lambda item: (
            -item[2],
            abs(item[0] - home_xg) + abs(item[1] - away_xg),
            item[0] + item[1],
        ),
    )
    top_scores = [
        {
            "score": f"{home_goals}-{away_goals}",
            "probability": probability,
        }
        for home_goals, away_goals, probability in ranked_scores[:top_n]
    ]

    outcome_entropy = -sum(
        probability * math.log(probability)
        for probability in outcomes
        if probability > 0.0
    ) / math.log(3.0)

    return {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "home_win": outcomes[0],
        "draw": outcomes[1],
        "away_win": outcomes[2],
        "under_2_5_probability": under_2_5_probability,
        "entropy": outcome_entropy,
        "retained_score_mass": retained_mass,
        "top_scores": top_scores,
    }


def blend_probabilities(models: Iterable[dict[str, object]]) -> list[float]:
    """用明确非负权重混合可用 1X2 模型。"""
    weighted = [0.0, 0.0, 0.0]
    total_weight = 0.0

    for model in models:
        probabilities = model.get("probabilities")
        weight = float(model.get("weight", 0.0))
        if not isinstance(probabilities, (list, tuple)) or len(probabilities) != 3:
            raise ValueError("每个模型必须包含三个概率")
        if not math.isfinite(weight) or weight < 0.0:
            raise ValueError("模型权重必须有限且非负")
        normalized = _normalize(
            [_validate_probability(value, "model probability") for value in probabilities]
        )
        for index, probability in enumerate(normalized):
            weighted[index] += weight * probability
        total_weight += weight

    if total_weight <= 0.0:
        raise ValueError("至少需要一个正模型权重")
    return _normalize(weighted)


def confidence_score(
    selected_probability: float,
    evidence_quality: float,
    model_disagreement: float,
    lineup_uncertainty: float,
    rotation_risk: float,
    data_missingness: float,
    upset_vulnerability: float = 0.0,
) -> float:
    """返回有界审计分，不是事件概率。"""
    selected_probability = _validate_probability(
        selected_probability, "selected_probability"
    )
    evidence_quality = _validate_probability(evidence_quality, "evidence_quality")
    model_disagreement = _validate_probability(
        model_disagreement, "model_disagreement"
    )
    lineup_uncertainty = _validate_probability(
        lineup_uncertainty, "lineup_uncertainty"
    )
    rotation_risk = _validate_probability(rotation_risk, "rotation_risk")
    data_missingness = _validate_probability(data_missingness, "data_missingness")
    upset_vulnerability = _validate_probability(
        upset_vulnerability, "upset_vulnerability"
    )

    base = 100.0 * (0.72 * selected_probability + 0.28 * evidence_quality)
    penalty = 100.0 * (
        0.25 * model_disagreement
        + 0.15 * lineup_uncertainty
        + 0.10 * rotation_risk
        + 0.20 * data_missingness
        + 0.10 * upset_vulnerability
    )
    return round(max(0.0, min(100.0, base - penalty)), 1)


def upset_risk_profile(
    outcome_probabilities: Sequence[float],
    *,
    low_event_probability: float = 0.0,
    favorite_process_weakness: float = 0.0,
    underdog_transition_set_piece_threat: float = 0.0,
    favorite_availability_risk: float = 0.0,
    rotation_incentive_risk: float = 0.0,
    market_disagreement: float = 0.0,
    discipline_variance: float = 0.0,
) -> dict[str, object]:
    """返回爆冷概率和单独的语境脆弱度分。

    脆弱度分是审计分，不是事件概率。直接爆冷和强方不胜概率仍以模型概率为准。
    """
    if len(outcome_probabilities) != 3:
        raise ValueError("outcome_probabilities 必须包含 home、draw、away")
    home_win, draw, away_win = _normalize(
        [
            _validate_probability(value, "outcome probability")
            for value in outcome_probabilities
        ]
    )

    factors = {
        "low_event_probability": low_event_probability,
        "favorite_process_weakness": favorite_process_weakness,
        "underdog_transition_set_piece_threat": (
            underdog_transition_set_piece_threat
        ),
        "favorite_availability_risk": favorite_availability_risk,
        "rotation_incentive_risk": rotation_incentive_risk,
        "market_disagreement": market_disagreement,
        "discipline_variance": discipline_variance,
    }
    validated_factors = {
        name: _validate_probability(value, name) for name, value in factors.items()
    }

    if home_win >= away_win:
        favorite = "home"
        favorite_win_probability = home_win
        underdog_win_probability = away_win
    else:
        favorite = "away"
        favorite_win_probability = away_win
        underdog_win_probability = home_win

    favorite_fail_probability = 1.0 - favorite_win_probability
    vulnerability = (
        0.55 * favorite_fail_probability
        + 0.10 * underdog_win_probability
        + 0.08 * validated_factors["low_event_probability"]
        + 0.06 * validated_factors["favorite_process_weakness"]
        + 0.06
        * validated_factors["underdog_transition_set_piece_threat"]
        + 0.05 * validated_factors["favorite_availability_risk"]
        + 0.05 * validated_factors["rotation_incentive_risk"]
        + 0.05 * validated_factors["market_disagreement"]
        + 0.05 * validated_factors["discipline_variance"]
    )
    vulnerability_score = round(100.0 * min(1.0, vulnerability), 1)
    if vulnerability_score < 20.0:
        label = "low"
    elif vulnerability_score < 35.0:
        label = "guarded"
    elif vulnerability_score < 50.0:
        label = "elevated"
    else:
        label = "high"

    return {
        "favorite": favorite,
        "favorite_win_probability": favorite_win_probability,
        "draw_probability": draw,
        "underdog_win_probability": underdog_win_probability,
        "favorite_fail_probability": favorite_fail_probability,
        "upset_vulnerability": vulnerability_score / 100.0,
        "upset_vulnerability_score": vulnerability_score,
        "upset_vulnerability_label": label,
        "risk_factors": validated_factors,
    }


def extract_sporttery_all_up_options(
    payload: dict[str, object],
) -> list[dict[str, object]]:
    """从 API JSON 提取官方启用的 HAD/HHAD 过关选项。"""
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Sporttery payload 必须是成功 API 响应")
    value = payload.get("value")
    if not isinstance(value, dict):
        raise ValueError("Sporttery payload 缺少 value")
    match_groups = value.get("matchInfoList")
    if not isinstance(match_groups, list):
        raise ValueError("Sporttery payload 缺少 matchInfoList")

    options = []
    for group in match_groups:
        if not isinstance(group, dict):
            continue
        matches = group.get("subMatchList")
        if not isinstance(matches, list):
            continue
        for match in matches:
            if not isinstance(match, dict):
                continue
            if (
                str(match.get("matchStatus", "")).lower() != "selling"
                or not _is_enabled(match.get("sellStatus"))
            ):
                continue
            pool_list = match.get("poolList")
            if not isinstance(pool_list, list):
                continue
            for pool_record in pool_list:
                if not isinstance(pool_record, dict):
                    continue
                pool = str(pool_record.get("poolCode", "")).upper()
                if pool not in {"HAD", "HHAD"}:
                    continue
                if not (
                    str(pool_record.get("poolStatus", "")).lower() == "selling"
                    and _is_enabled(pool_record.get("allUp"))
                    and _is_enabled(pool_record.get("bettingAllup"))
                    and _is_enabled(pool_record.get("cbtAllUp"))
                ):
                    continue
                odds_record = match.get(pool.lower())
                if not isinstance(odds_record, dict):
                    continue
                source_update_at = " ".join(
                    part
                    for part in (
                        str(odds_record.get("updateDate", "")).strip(),
                        str(odds_record.get("updateTime", "")).strip(),
                    )
                    if part
                )
                for outcome, odds_key in (("H", "h"), ("D", "d"), ("A", "a")):
                    raw_bonus = odds_record.get(odds_key)
                    try:
                        fixed_bonus = float(raw_bonus)
                    except (TypeError, ValueError):
                        continue
                    if not math.isfinite(fixed_bonus) or fixed_bonus <= 1.0:
                        continue
                    match_id = str(match.get("matchId", ""))
                    options.append(
                        {
                            "selection_id": f"{match_id}-{pool}-{outcome}",
                            "match_id": match_id,
                            "match_num": match.get("matchNumStr", ""),
                            "kickoff": " ".join(
                                [
                                    str(match.get("matchDate", "")).strip(),
                                    str(match.get("matchTime", "")).strip(),
                                ]
                            ).strip(),
                            "home_team": match.get("homeTeamAbbName", ""),
                            "away_team": match.get("awayTeamAbbName", ""),
                            "pool": pool,
                            "goal_line": (
                                str(odds_record.get("goalLine", "0"))
                                if pool == "HHAD"
                                else "0"
                            ),
                            "outcome": outcome,
                            "fixed_bonus": fixed_bonus,
                            "single": _is_enabled(pool_record.get("single")),
                            "all_up": True,
                            "betting_all_up": True,
                            "cbt_all_up": True,
                            "match_status": match.get("matchStatus"),
                            "sell_status": match.get("sellStatus"),
                            "pool_status": pool_record.get("poolStatus"),
                            "source_update_at": source_update_at,
                        }
                    )
    return options


def build_two_leg_portfolios(
    selections: Iterable[dict[str, object]],
) -> dict[str, dict[str, object] | None]:
    """构建可审计的 steady、growth、aggressive 2 串 1 组合。

    可用性标记来自官方 Sporttery 计算器。联合概率假设比赛结果独立，
    仍是模型估计。
    """
    eligible = []
    for raw_selection in selections:
        selection = dict(raw_selection)
        required = (
            "selection_id",
            "match_id",
            "pool",
            "outcome",
            "probability",
            "fixed_bonus",
            "confidence",
            "upset_vulnerability",
            "market_disagreement",
            "match_status",
            "sell_status",
            "pool_status",
            "all_up",
            "betting_all_up",
            "cbt_all_up",
            "retrieval_age_minutes",
        )
        missing = [key for key in required if key not in selection]
        if missing:
            raise ValueError(f"selection 缺少字段: {', '.join(missing)}")

        probability = _validate_probability(
            selection["probability"], "selection probability"
        )
        upset_vulnerability = _validate_probability(
            selection["upset_vulnerability"], "upset_vulnerability"
        )
        disagreement = _validate_probability(
            selection["market_disagreement"], "market_disagreement"
        )
        fixed_bonus = float(selection["fixed_bonus"])
        confidence = float(selection["confidence"])
        retrieval_age_minutes = float(selection["retrieval_age_minutes"])
        pool = str(selection["pool"]).upper()

        if not math.isfinite(fixed_bonus) or fixed_bonus <= 1.0:
            raise ValueError("fixed_bonus 必须有限且大于 1")
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 100.0:
            raise ValueError("confidence 必须在 0 和 100 之间")
        if not math.isfinite(retrieval_age_minutes) or retrieval_age_minutes < 0.0:
            raise ValueError(
                "retrieval_age_minutes 必须有限且非负"
            )
        if pool not in {"HAD", "HHAD"}:
            continue

        available = (
            str(selection["match_status"]).lower() == "selling"
            and int(selection["sell_status"]) == 1
            and str(selection["pool_status"]).lower() == "selling"
            and _is_enabled(selection["all_up"])
            and _is_enabled(selection["betting_all_up"])
            and _is_enabled(selection["cbt_all_up"])
            and retrieval_age_minutes <= 60.0
        )
        if not available:
            continue

        selection.update(
            {
                "pool": pool,
                "probability": probability,
                "fixed_bonus": fixed_bonus,
                "confidence": confidence,
                "upset_vulnerability": upset_vulnerability,
                "market_disagreement": disagreement,
                "retrieval_age_minutes": retrieval_age_minutes,
            }
        )
        eligible.append(selection)

    candidates = []
    for first, second in combinations(eligible, 2):
        if str(first["match_id"]) == str(second["match_id"]):
            continue
        joint_probability = first["probability"] * second["probability"]
        combined_bonus = first["fixed_bonus"] * second["fixed_bonus"]
        candidates.append(
            {
                "legs": [first, second],
                "joint_probability": joint_probability,
                "loss_probability": 1.0 - joint_probability,
                "combined_bonus": combined_bonus,
                "model_return_index": joint_probability * combined_bonus,
                "model_net_return_index": joint_probability * combined_bonus - 1.0,
                "guaranteed": False,
            }
        )

    def qualifies(candidate: dict[str, object], tier: str) -> bool:
        legs = candidate["legs"]
        probabilities = [leg["probability"] for leg in legs]
        confidences = [leg["confidence"] for leg in legs]
        vulnerabilities = [leg["upset_vulnerability"] for leg in legs]
        disagreements = [leg["market_disagreement"] for leg in legs]
        ages = [leg["retrieval_age_minutes"] for leg in legs]
        pools = [leg["pool"] for leg in legs]

        if tier == "steady":
            return (
                min(probabilities) >= 0.65
                and min(confidences) >= 60.0
                and max(vulnerabilities) <= 0.35
                and max(disagreements) <= 0.12
                and max(ages) <= 30.0
                and pools == ["HAD", "HAD"]
                and candidate["model_return_index"] >= 0.75
            )
        if tier == "growth":
            return (
                min(probabilities) >= 0.55
                and min(confidences) >= 55.0
                and max(vulnerabilities) <= 0.45
                and max(disagreements) <= 0.18
                and candidate["combined_bonus"] >= 2.0
                and candidate["model_return_index"] >= 0.75
                and pools.count("HHAD") <= 1
            )
        return (
            min(probabilities) >= 0.35
            and min(confidences) >= 45.0
            and max(vulnerabilities) <= 0.60
            and max(disagreements) <= 0.25
            and candidate["combined_bonus"] >= 3.0
            and candidate["model_return_index"] >= 0.70
        )

    policies = {
        "steady": lambda item: (
            item["joint_probability"],
            -max(leg["upset_vulnerability"] for leg in item["legs"]),
        ),
        "growth": lambda item: (
            item["joint_probability"],
            item["model_return_index"],
        ),
        "aggressive": lambda item: (
            item["combined_bonus"],
            item["model_return_index"],
        ),
    }
    result: dict[str, dict[str, object] | None] = {}
    for tier, key_function in policies.items():
        tier_candidates = [
            candidate for candidate in candidates if qualifies(candidate, tier)
        ]
        result[tier] = (
            max(tier_candidates, key=key_function) if tier_candidates else None
        )
    return result


def qualification_probability(
    home_win_90: float,
    draw_90: float,
    away_win_90: float,
    home_advance_given_draw: float,
) -> dict[str, float]:
    """将 90 分钟 1X2 转为淘汰赛晋级概率。"""
    outcomes = _normalize(
        [
            _validate_probability(home_win_90, "home_win_90"),
            _validate_probability(draw_90, "draw_90"),
            _validate_probability(away_win_90, "away_win_90"),
        ]
    )
    home_advance_given_draw = _validate_probability(
        home_advance_given_draw, "home_advance_given_draw"
    )
    home_qualify = outcomes[0] + outcomes[1] * home_advance_given_draw
    return {
        "home_qualify": home_qualify,
        "away_qualify": 1.0 - home_qualify,
    }


def brier_score(probabilities: Sequence[float], outcome_index: int) -> float:
    """返回多分类 Brier score；越低越好。"""
    if len(probabilities) < 2:
        raise ValueError("至少需要两个 outcome probabilities")
    if not 0 <= outcome_index < len(probabilities):
        raise ValueError("outcome_index 超出概率向量范围")
    normalized = _normalize(
        [_validate_probability(value, "forecast probability") for value in probabilities]
    )
    return sum(
        (probability - (1.0 if index == outcome_index else 0.0)) ** 2
        for index, probability in enumerate(normalized)
    )


def multiclass_log_loss(
    probabilities: Sequence[float],
    outcome_index: int,
    epsilon: float = 1e-15,
) -> float:
    """返回观测结果的 log loss；越低越好。"""
    if len(probabilities) < 2:
        raise ValueError("至少需要两个 outcome probabilities")
    if not 0 <= outcome_index < len(probabilities):
        raise ValueError("outcome_index 超出概率向量范围")
    if not 0.0 < epsilon < 1.0:
        raise ValueError("epsilon 必须在 0 和 1 之间")
    normalized = _normalize(
        [_validate_probability(value, "forecast probability") for value in probabilities]
    )
    return -math.log(max(epsilon, normalized[outcome_index]))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser._optionals.title = "选项"
    parser.add_argument("-h", "--help", action="help", help="显示帮助并退出")
    parser.add_argument("--home-xg", type=float)
    parser.add_argument("--away-xg", type=float)
    parser.add_argument("--max-goals", type=int, default=10)
    parser.add_argument(
        "--odds",
        type=float,
        nargs=3,
        metavar=("HOME", "DRAW", "AWAY"),
    )
    parser.add_argument(
        "--fixed-bonus",
        type=float,
        nargs="+",
        metavar="BONUS",
        help="完整互斥的 Sporttery fixed-bonus 市场",
    )
    parser.add_argument(
        "--outcome-probabilities",
        type=float,
        nargs=3,
        metavar=("HOME", "DRAW", "AWAY"),
        help="用于爆冷风险画像的最终混合 90 分钟概率",
    )
    parser.add_argument(
        "--single-ticket-probability",
        type=float,
        help="Sporttery 单关选择的模型概率",
    )
    parser.add_argument(
        "--single-ticket-fixed-bonus",
        type=float,
        help="单关选择的官方 fixed bonus",
    )
    parser.add_argument(
        "--single-ticket-confidence",
        type=float,
        default=60.0,
        help="单关选择的 confidence score",
    )
    parser.add_argument(
        "--single-ticket-upset-vulnerability",
        type=float,
        default=0.0,
        help="单关选择的 0-1 upset vulnerability",
    )
    parser.add_argument(
        "--single-ticket-ineligible",
        action="store_true",
        help="将单关选择标记为官方当前不可执行",
    )
    parser.add_argument(
        "--single-ticket-safety-margin",
        type=float,
        default=0.03,
        help="strict value 要求高于盈亏平衡的概率安全边际",
    )
    parser.add_argument("--low-event-probability", type=float, default=0.0)
    parser.add_argument("--favorite-process-weakness", type=float, default=0.0)
    parser.add_argument(
        "--underdog-transition-set-piece-threat",
        type=float,
        default=0.0,
    )
    parser.add_argument("--favorite-availability-risk", type=float, default=0.0)
    parser.add_argument("--rotation-incentive-risk", type=float, default=0.0)
    parser.add_argument("--market-disagreement", type=float, default=0.0)
    parser.add_argument("--discipline-variance", type=float, default=0.0)
    parser.add_argument(
        "--portfolio-json",
        help="包含模型化且官方 eligible selections 的 JSON 文件",
    )
    parser.add_argument(
        "--sporttery-api-json",
        help="待提取的已保存官方比赛计算器 API 响应",
    )
    args = parser.parse_args()
    if (args.home_xg is None) != (args.away_xg is None):
        parser.error("--home-xg 和 --away-xg 必须同时提供")
    if (
        args.home_xg is None
        and args.fixed_bonus is None
        and args.outcome_probabilities is None
        and args.single_ticket_probability is None
        and args.portfolio_json is None
        and args.sporttery_api_json is None
    ):
        parser.error(
            "请提供 xG 输入、--fixed-bonus、outcome probabilities、"
            "--portfolio-json、--sporttery-api-json 或它们的组合"
        )
    if args.odds and args.home_xg is None:
        parser.error("--odds 需要同时提供 --home-xg 和 --away-xg")
    if (args.single_ticket_probability is None) != (
        args.single_ticket_fixed_bonus is None
    ):
        parser.error(
            "--single-ticket-probability 和 --single-ticket-fixed-bonus "
            "必须同时提供"
        )
    return args


def main() -> None:
    args = _parse_args()
    result: dict[str, object] = {}
    if args.home_xg is not None:
        result["poisson"] = poisson_forecast(
            args.home_xg,
            args.away_xg,
            max_goals=args.max_goals,
        )
    if args.odds:
        result["market_probabilities"] = devig_1x2(args.odds)
    if args.fixed_bonus:
        result["fixed_bonus_market"] = implied_probabilities_from_fixed_bonus(
            args.fixed_bonus
        )
    if args.outcome_probabilities:
        result["upset_profile"] = upset_risk_profile(
            args.outcome_probabilities,
            low_event_probability=args.low_event_probability,
            favorite_process_weakness=args.favorite_process_weakness,
            underdog_transition_set_piece_threat=(
                args.underdog_transition_set_piece_threat
            ),
            favorite_availability_risk=args.favorite_availability_risk,
            rotation_incentive_risk=args.rotation_incentive_risk,
            market_disagreement=args.market_disagreement,
            discipline_variance=args.discipline_variance,
        )
    if args.single_ticket_probability is not None:
        result["single_ticket_value_gate"] = single_ticket_value_gate(
            args.single_ticket_probability,
            args.single_ticket_fixed_bonus,
            confidence=args.single_ticket_confidence,
            upset_vulnerability=args.single_ticket_upset_vulnerability,
            official_eligible=not args.single_ticket_ineligible,
            safety_margin=args.single_ticket_safety_margin,
        )
    if args.portfolio_json:
        with open(args.portfolio_json, encoding="utf-8") as handle:
            selections = json.load(handle)
        if not isinstance(selections, list):
            raise ValueError("portfolio JSON 必须包含 selections 列表")
        result["two_leg_portfolios"] = build_two_leg_portfolios(selections)
    if args.sporttery_api_json:
        with open(args.sporttery_api_json, encoding="utf-8") as handle:
            payload = json.load(handle)
        result["sporttery_all_up_options"] = extract_sporttery_all_up_options(
            payload
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
