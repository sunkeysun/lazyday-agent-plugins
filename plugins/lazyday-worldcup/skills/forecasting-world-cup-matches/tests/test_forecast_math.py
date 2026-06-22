import json
import importlib
import subprocess
import sys
import tempfile
import unittest
import ssl
import urllib.error
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from scripts.forecast_math import (  # noqa: E402
    blend_probabilities,
    brier_score,
    build_two_leg_portfolios,
    confidence_score,
    devig_1x2,
    extract_sporttery_all_up_options,
    implied_probabilities_from_fixed_bonus,
    market_disagreement,
    multiclass_log_loss,
    poisson_forecast,
    qualification_probability,
    single_ticket_value_gate,
    upset_risk_profile,
)


class ForecastMathTests(unittest.TestCase):
    def test_fetcher_is_importable_as_package_module(self):
        module = importlib.import_module("scripts.fetch_sporttery_calculator")

        self.assertTrue(callable(module.fetch_json))

    def test_fetcher_detects_certificate_verification_errors(self):
        module = importlib.import_module("scripts.fetch_sporttery_calculator")
        error = urllib.error.URLError(
            ssl.SSLCertVerificationError("CERTIFICATE_VERIFY_FAILED")
        )

        self.assertTrue(module._is_certificate_verification_error(error))

    def test_devig_probabilities_sum_to_one(self):
        result = devig_1x2([1.50, 4.50, 7.00])

        self.assertAlmostEqual(sum(result), 1.0, places=12)
        self.assertGreater(result[0], result[1])
        self.assertGreater(result[1], result[2])

    def test_fixed_bonus_probabilities_remove_payout_margin(self):
        result = implied_probabilities_from_fixed_bonus([1.42, 4.20, 6.50])

        self.assertAlmostEqual(sum(result["fair_probabilities"]), 1.0, places=12)
        self.assertAlmostEqual(
            result["raw_probability_sum"],
            (1 / 1.42) + (1 / 4.20) + (1 / 6.50),
            places=12,
        )
        self.assertGreater(result["fair_probabilities"][0], 0.60)
        self.assertGreater(result["payout_rate"], 0.0)
        self.assertLess(result["payout_rate"], 1.0)

    def test_single_ticket_value_gate_allows_strict_positive_value(self):
        result = single_ticket_value_gate(
            0.74,
            1.45,
            confidence=72,
            upset_vulnerability=0.22,
        )

        self.assertEqual(result["value_action"], "positive_value")
        self.assertEqual(result["strict_value_action"], "strict_value_stake")
        self.assertEqual(result["suggested_stake_units_from_100"], [40, 70])
        self.assertGreater(result["expected_net_per_yuan"], 0.0)

    def test_single_ticket_value_gate_separates_controlled_participation(self):
        result = single_ticket_value_gate(
            0.625,
            1.39,
            confidence=62,
            upset_vulnerability=0.327,
        )

        self.assertEqual(result["value_action"], "no_bet_value_gate")
        self.assertEqual(result["strict_value_action"], "strict_value_no_bet")
        self.assertEqual(
            result["controlled_participation_action"],
            "steady_growth_participation",
        )
        self.assertEqual(result["suggested_stake_units_from_100"], [30, 50])
        self.assertLess(result["expected_net_per_yuan"], 0.0)

    def test_single_ticket_value_gate_rejects_low_return_participation(self):
        result = single_ticket_value_gate(
            0.56,
            1.25,
            confidence=62,
            upset_vulnerability=0.30,
        )

        self.assertEqual(result["strict_value_action"], "strict_value_no_bet")
        self.assertEqual(
            result["controlled_participation_action"],
            "watch_only_or_no_bet",
        )

    def test_single_ticket_value_gate_blocks_ineligible_selection(self):
        result = single_ticket_value_gate(
            0.80,
            1.60,
            official_eligible=False,
        )

        self.assertEqual(result["value_action"], "not_officially_eligible")
        self.assertEqual(result["strict_value_action"], "no_bet_ineligible")
        self.assertEqual(
            result["controlled_participation_action"],
            "watch_only_ineligible",
        )
        self.assertEqual(result["suggested_stake_units_from_100"], [0, 0])

    def test_market_disagreement_detects_divergent_market(self):
        aligned = market_disagreement(
            [
                [0.70, 0.20, 0.10],
                [0.68, 0.21, 0.11],
            ]
        )
        divergent = market_disagreement(
            [
                [0.70, 0.20, 0.10],
                [0.42, 0.31, 0.27],
            ]
        )

        self.assertLess(aligned, divergent)
        self.assertGreaterEqual(aligned, 0.0)
        self.assertLessEqual(divergent, 1.0)

    def test_poisson_distribution_is_normalized(self):
        result = poisson_forecast(2.0, 0.7, max_goals=12)

        self.assertAlmostEqual(
            result["home_win"] + result["draw"] + result["away_win"],
            1.0,
            places=10,
        )
        self.assertGreater(result["home_win"], result["away_win"])
        self.assertEqual(result["top_scores"][0]["score"], "2-0")
        self.assertGreater(result["entropy"], 0.0)
        self.assertLessEqual(result["entropy"], 1.0)
        self.assertGreaterEqual(result["under_2_5_probability"], 0.0)
        self.assertLessEqual(result["under_2_5_probability"], 1.0)

    def test_low_scoring_match_has_more_under_2_5_risk(self):
        low_scoring = poisson_forecast(0.8, 0.6)
        high_scoring = poisson_forecast(2.1, 1.6)

        self.assertGreater(
            low_scoring["under_2_5_probability"],
            high_scoring["under_2_5_probability"],
        )

    def test_blend_probabilities_normalizes_available_models(self):
        result = blend_probabilities(
            [
                {"probabilities": [0.70, 0.20, 0.10], "weight": 0.6},
                {"probabilities": [0.60, 0.25, 0.15], "weight": 0.4},
            ]
        )

        self.assertAlmostEqual(sum(result), 1.0, places=12)
        self.assertAlmostEqual(result[0], 0.66, places=12)

    def test_confidence_penalizes_uncertainty(self):
        clean = confidence_score(
            selected_probability=0.80,
            evidence_quality=0.90,
            model_disagreement=0.05,
            lineup_uncertainty=0.00,
            rotation_risk=0.00,
            data_missingness=0.00,
        )
        uncertain = confidence_score(
            selected_probability=0.80,
            evidence_quality=0.90,
            model_disagreement=0.20,
            lineup_uncertainty=0.15,
            rotation_risk=0.10,
            data_missingness=0.25,
        )

        self.assertGreater(clean, uncertain)
        self.assertGreaterEqual(uncertain, 0.0)
        self.assertLessEqual(clean, 100.0)

    def test_confidence_penalizes_upset_vulnerability(self):
        stable = confidence_score(
            selected_probability=0.80,
            evidence_quality=0.90,
            model_disagreement=0.05,
            lineup_uncertainty=0.00,
            rotation_risk=0.00,
            data_missingness=0.00,
            upset_vulnerability=0.10,
        )
        vulnerable = confidence_score(
            selected_probability=0.80,
            evidence_quality=0.90,
            model_disagreement=0.05,
            lineup_uncertainty=0.00,
            rotation_risk=0.00,
            data_missingness=0.00,
            upset_vulnerability=0.80,
        )

        self.assertGreater(stable, vulnerable)

    def test_upset_profile_separates_outright_upset_from_favorite_fail(self):
        profile = upset_risk_profile([0.80, 0.13, 0.07])

        self.assertEqual(profile["favorite"], "home")
        self.assertAlmostEqual(profile["underdog_win_probability"], 0.07)
        self.assertAlmostEqual(profile["favorite_fail_probability"], 0.20)
        self.assertNotEqual(
            profile["underdog_win_probability"],
            profile["favorite_fail_probability"],
        )
        self.assertAlmostEqual(
            profile["upset_vulnerability"],
            profile["upset_vulnerability_score"] / 100.0,
        )

    def test_upset_profile_handles_away_favorite(self):
        profile = upset_risk_profile([0.10, 0.20, 0.70])

        self.assertEqual(profile["favorite"], "away")
        self.assertAlmostEqual(profile["underdog_win_probability"], 0.10)
        self.assertAlmostEqual(profile["favorite_fail_probability"], 0.30)

    def test_upset_vulnerability_increases_with_contextual_risks(self):
        stable = upset_risk_profile(
            [0.72, 0.18, 0.10],
            low_event_probability=0.20,
        )
        exposed = upset_risk_profile(
            [0.72, 0.18, 0.10],
            low_event_probability=0.80,
            favorite_process_weakness=0.80,
            underdog_transition_set_piece_threat=0.80,
            favorite_availability_risk=0.80,
            rotation_incentive_risk=0.80,
            market_disagreement=0.80,
            discipline_variance=0.80,
        )

        self.assertGreater(
            exposed["upset_vulnerability_score"],
            stable["upset_vulnerability_score"],
        )

    def test_two_leg_portfolios_exclude_unavailable_and_same_match_selections(self):
        selections = [
            self._selection("A-HAD", "A", 0.78, 1.25, 72, 0.20),
            self._selection("A-HHAD", "A", 0.52, 2.00, 55, 0.42, pool="HHAD"),
            self._selection("B-HAD", "B", 0.72, 1.35, 68, 0.25),
            self._selection(
                "C-HAD",
                "C",
                0.70,
                1.40,
                65,
                0.25,
                pool_status="Stopped",
            ),
            self._selection(
                "D-HAD",
                "D",
                0.68,
                1.45,
                64,
                0.27,
                all_up=False,
            ),
        ]

        result = build_two_leg_portfolios(selections)

        self.assertEqual(
            [leg["selection_id"] for leg in result["steady"]["legs"]],
            ["A-HAD", "B-HAD"],
        )
        for portfolio in result.values():
            if portfolio is None:
                continue
            match_ids = [leg["match_id"] for leg in portfolio["legs"]]
            self.assertEqual(len(match_ids), len(set(match_ids)))
            self.assertNotIn("C", match_ids)
            self.assertNotIn("D", match_ids)

    def test_two_leg_portfolios_have_ordered_risk_and_return_profiles(self):
        selections = [
            self._selection("A", "A", 0.80, 1.20, 78, 0.15),
            self._selection("B", "B", 0.75, 1.30, 72, 0.20),
            self._selection("C", "C", 0.64, 1.75, 63, 0.32),
            self._selection("D", "D", 0.58, 2.05, 58, 0.40),
            self._selection("E", "E", 0.45, 3.10, 50, 0.52),
        ]

        result = build_two_leg_portfolios(selections)

        self.assertGreater(
            result["steady"]["joint_probability"],
            result["growth"]["joint_probability"],
        )
        self.assertGreater(
            result["growth"]["joint_probability"],
            result["aggressive"]["joint_probability"],
        )
        self.assertLess(
            result["steady"]["combined_bonus"],
            result["growth"]["combined_bonus"],
        )
        self.assertLess(
            result["growth"]["combined_bonus"],
            result["aggressive"]["combined_bonus"],
        )

    def test_two_leg_portfolio_reports_probability_and_return_without_guarantee(self):
        selections = [
            self._selection("A", "A", 0.80, 1.20, 78, 0.15),
            self._selection("B", "B", 0.75, 1.30, 72, 0.20),
        ]

        steady = build_two_leg_portfolios(selections)["steady"]

        self.assertAlmostEqual(steady["joint_probability"], 0.60)
        self.assertAlmostEqual(steady["combined_bonus"], 1.56)
        self.assertAlmostEqual(steady["loss_probability"], 0.40)
        self.assertAlmostEqual(steady["model_return_index"], 0.936)
        self.assertFalse(steady["guaranteed"])

    def test_source_update_age_does_not_replace_fresh_retrieval_age(self):
        selections = [
            self._selection("A", "A", 0.80, 1.20, 78, 0.15),
            self._selection("B", "B", 0.75, 1.30, 72, 0.20),
        ]
        for selection in selections:
            selection["source_update_age_minutes"] = 10_000

        result = build_two_leg_portfolios(selections)

        self.assertIsNotNone(result["steady"])

    def test_string_zero_availability_flags_are_not_treated_as_enabled(self):
        selections = [
            self._selection("A", "A", 0.80, 1.20, 78, 0.15),
            self._selection("B", "B", 0.75, 1.30, 72, 0.20),
            self._selection("blocked", "C", 0.95, 5.00, 90, 0.05),
        ]
        selections[-1]["all_up"] = "0"
        selections[-1]["cbt_all_up"] = "0"

        result = build_two_leg_portfolios(selections)

        for portfolio in result.values():
            if portfolio is None:
                continue
            self.assertNotIn(
                "blocked",
                [leg["selection_id"] for leg in portfolio["legs"]],
            )

    def test_portfolios_reject_extremely_poor_model_return(self):
        selections = [
            self._selection("A", "A", 0.66, 1.05, 65, 0.25),
            self._selection("B", "B", 0.66, 1.05, 65, 0.25),
        ]

        result = build_two_leg_portfolios(selections)

        self.assertIsNone(result["steady"])

    def test_extract_sporttery_options_keeps_only_current_all_up_pools(self):
        payload = {
            "success": True,
            "value": {
                "matchInfoList": [
                    {
                        "subMatchList": [
                            {
                                "matchId": 101,
                                "matchNumStr": "周一001",
                                "matchDate": "2026-06-15",
                                "matchTime": "03:00:00",
                                "homeTeamAbbName": "主队",
                                "awayTeamAbbName": "客队",
                                "matchStatus": "Selling",
                                "sellStatus": 1,
                                "had": {
                                    "h": "1.50",
                                    "d": "3.50",
                                    "a": "5.00",
                                    "updateDate": "2026-06-14",
                                    "updateTime": "10:00:00",
                                },
                                "hhad": {
                                    "goalLine": "-1",
                                    "h": "2.50",
                                    "d": "3.30",
                                    "a": "2.20",
                                },
                                "poolList": [
                                    {
                                        "poolCode": "HAD",
                                        "poolStatus": "Selling",
                                        "single": 1,
                                        "allUp": 1,
                                        "bettingAllup": 1,
                                        "cbtAllUp": 1,
                                    },
                                    {
                                        "poolCode": "HHAD",
                                        "poolStatus": "Selling",
                                        "single": 0,
                                        "allUp": 1,
                                        "bettingAllup": 0,
                                        "cbtAllUp": 1,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        options = extract_sporttery_all_up_options(payload)

        self.assertEqual(len(options), 3)
        self.assertEqual({option["pool"] for option in options}, {"HAD"})
        self.assertTrue(all(option["single"] for option in options))
        self.assertEqual(
            {option["outcome"] for option in options},
            {"H", "D", "A"},
        )
        self.assertEqual(options[0]["source_update_at"], "2026-06-14 10:00:00")

    @staticmethod
    def _selection(
        selection_id,
        match_id,
        probability,
        fixed_bonus,
        confidence,
        upset_vulnerability,
        *,
        pool="HAD",
        pool_status="Selling",
        all_up=True,
    ):
        return {
            "selection_id": selection_id,
            "match_id": match_id,
            "pool": pool,
            "outcome": "H",
            "probability": probability,
            "fixed_bonus": fixed_bonus,
            "confidence": confidence,
            "upset_vulnerability": upset_vulnerability,
            "market_disagreement": 0.05,
            "match_status": "Selling",
            "sell_status": 1,
            "pool_status": pool_status,
            "all_up": all_up,
            "betting_all_up": all_up,
            "cbt_all_up": all_up,
            "retrieval_age_minutes": 5,
        }

    def test_qualification_probability_separates_90_minute_draw(self):
        result = qualification_probability(
            home_win_90=0.38,
            draw_90=0.31,
            away_win_90=0.31,
            home_advance_given_draw=0.54,
        )

        self.assertAlmostEqual(result["home_qualify"], 0.5474, places=4)
        self.assertAlmostEqual(
            result["home_qualify"] + result["away_qualify"],
            1.0,
            places=12,
        )

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            devig_1x2([1.5, 0, 4.0])
        with self.assertRaises(ValueError):
            poisson_forecast(-1.0, 1.0)
        with self.assertRaises(ValueError):
            blend_probabilities([])

    def test_forecast_scoring_rewards_calibrated_probability(self):
        strong = [0.80, 0.15, 0.05]
        weak = [0.40, 0.35, 0.25]

        self.assertLess(brier_score(strong, 0), brier_score(weak, 0))
        self.assertLess(multiclass_log_loss(strong, 0), multiclass_log_loss(weak, 0))

    def test_cli_returns_json(self):
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "forecast_math.py"),
            "--home-xg",
            "2.0",
            "--away-xg",
            "0.7",
            "--odds",
            "1.50",
            "4.50",
            "7.00",
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertIn("poisson", result)
        self.assertIn("market_probabilities", result)
        self.assertAlmostEqual(sum(result["market_probabilities"]), 1.0, places=12)

    def test_cli_converts_fixed_bonus_without_xg(self):
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "forecast_math.py"),
            "--fixed-bonus",
            "4.75",
            "5.00",
            "5.55",
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertNotIn("poisson", result)
        self.assertIn("fixed_bonus_market", result)
        self.assertAlmostEqual(
            sum(result["fixed_bonus_market"]["fair_probabilities"]),
            1.0,
            places=12,
        )

    def test_cli_returns_upset_risk_profile(self):
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "forecast_math.py"),
            "--outcome-probabilities",
            "0.72",
            "0.18",
            "0.10",
            "--low-event-probability",
            "0.65",
            "--underdog-transition-set-piece-threat",
            "0.70",
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["upset_profile"]["favorite"], "home")
        self.assertAlmostEqual(
            result["upset_profile"]["underdog_win_probability"],
            0.10,
        )
        self.assertGreater(
            result["upset_profile"]["upset_vulnerability_score"],
            0.0,
        )

    def test_cli_returns_single_ticket_value_gate(self):
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "forecast_math.py"),
            "--single-ticket-probability",
            "0.625",
            "--single-ticket-fixed-bonus",
            "1.39",
            "--single-ticket-confidence",
            "62",
            "--single-ticket-upset-vulnerability",
            "0.327",
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)["single_ticket_value_gate"]

        self.assertEqual(result["strict_value_action"], "strict_value_no_bet")
        self.assertEqual(
            result["controlled_participation_action"],
            "steady_growth_participation",
        )

    def test_cli_builds_two_leg_portfolios_from_json(self):
        selections = [
            self._selection("A", "A", 0.80, 1.20, 78, 0.15),
            self._selection("B", "B", 0.75, 1.30, 72, 0.20),
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(selections, handle)
            handle.flush()
            command = [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "forecast_math.py"),
                "--portfolio-json",
                handle.name,
            ]

            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

        result = json.loads(completed.stdout)
        self.assertAlmostEqual(
            result["two_leg_portfolios"]["steady"]["joint_probability"],
            0.60,
        )

    def test_cli_extracts_official_all_up_options(self):
        payload = {
            "success": True,
            "value": {
                "matchInfoList": [
                    {
                        "subMatchList": [
                            {
                                "matchId": 101,
                                "matchStatus": "Selling",
                                "sellStatus": 1,
                                "had": {"h": "1.5", "d": "3.5", "a": "5.0"},
                                "poolList": [
                                    {
                                        "poolCode": "HAD",
                                        "poolStatus": "Selling",
                                        "single": 1,
                                        "allUp": 1,
                                        "bettingAllup": 1,
                                        "cbtAllUp": 1,
                                    }
                                ],
                            }
                        ]
                    }
                ]
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            command = [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "forecast_math.py"),
                "--sporttery-api-json",
                handle.name,
            ]

            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

        result = json.loads(completed.stdout)
        self.assertEqual(len(result["sporttery_all_up_options"]), 3)

    def test_fetch_sporttery_calculator_cli_extracts_options_from_url(self):
        payload = {
            "success": True,
            "value": {
                "matchInfoList": [
                    {
                        "subMatchList": [
                            {
                                "matchId": 202,
                                "matchNumStr": "周四025",
                                "matchDate": "2026-06-19",
                                "matchTime": "00:00:00",
                                "homeTeamAbbName": "捷克",
                                "awayTeamAbbName": "南非",
                                "matchStatus": "Selling",
                                "sellStatus": 1,
                                "had": {
                                    "h": "1.66",
                                    "d": "3.36",
                                    "a": "4.35",
                                    "updateDate": "2026-06-18",
                                    "updateTime": "20:00:00",
                                },
                                "poolList": [
                                    {
                                        "poolCode": "HAD",
                                        "poolStatus": "Selling",
                                        "single": 1,
                                        "allUp": 1,
                                        "bettingAllup": 1,
                                        "cbtAllUp": 1,
                                    }
                                ],
                            }
                        ]
                    }
                ]
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            command = [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "fetch_sporttery_calculator.py"),
                "--url",
                Path(handle.name).as_uri(),
                "--extract-options",
            ]

            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

        result = json.loads(completed.stdout)
        self.assertEqual(result["retrieval"]["source_url"], Path(handle.name).as_uri())
        self.assertEqual(len(result["sporttery_all_up_options"]), 3)
        self.assertEqual(
            result["sporttery_all_up_options"][0]["match_num"],
            "周四025",
        )

    def test_fetch_sporttery_calculator_cli_documents_insecure_tls_escape_hatch(self):
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "fetch_sporttery_calculator.py"),
            "--help",
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("--insecure", completed.stdout)
        self.assertIn("--retry-insecure-on-cert-error", completed.stdout)


if __name__ == "__main__":
    unittest.main()
