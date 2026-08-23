from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "sports_ticker"
    / "nfl_team_leaders.py"
)
spec = importlib.util.spec_from_file_location("nfl_team_leaders", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def athlete(
    player_id: str,
    name: str,
    short_name: str,
    position: str,
    stats: list[str],
) -> dict:
    return {
        "athlete": {
            "id": player_id,
            "displayName": name,
            "shortName": short_name,
            "position": {"abbreviation": position},
            "headshot": {"href": f"https://example.test/{player_id}.png"},
        },
        "stats": stats,
    }


def team_box(team_id: str, abbreviation: str, offset: int = 0) -> dict:
    return {
        "team": {"id": team_id, "abbreviation": abbreviation},
        "statistics": [
            {
                "name": "passing",
                "keys": [
                    "completions/passingAttempts",
                    "passingYards",
                    "passingTouchdowns",
                ],
                "athletes": [
                    athlete(
                        f"{team_id}-qb1",
                        f"{abbreviation} Quarterback One",
                        f"Q. One",
                        "QB",
                        ["18/25", str(240 + offset), "2"],
                    ),
                    athlete(
                        f"{team_id}-qb2",
                        f"{abbreviation} Quarterback Two",
                        f"Q. Two",
                        "QB",
                        ["3/5", "35", "0"],
                    ),
                ],
            },
            {
                "name": "rushing",
                "keys": ["rushingAttempts", "rushingYards", "rushingTouchdowns"],
                "athletes": [
                    athlete(
                        f"{team_id}-rb",
                        f"{abbreviation} Running Back",
                        "R. Back",
                        "RB",
                        ["14", str(88 + offset), "1"],
                    )
                ],
            },
            {
                "name": "receiving",
                "keys": ["receptions", "receivingYards", "receivingTargets"],
                "athletes": [
                    athlete(
                        f"{team_id}-wr",
                        f"{abbreviation} Receiver",
                        "W. Receiver",
                        "WR",
                        ["7", str(112 + offset), "9"],
                    )
                ],
            },
            {
                "name": "defensive",
                "keys": ["totalTackles", "soloTackles", "sacks", "interceptions"],
                "athletes": [
                    athlete(
                        f"{team_id}-lb",
                        f"{abbreviation} Linebacker",
                        "L. Backer",
                        "LB",
                        [str(10 + offset), "7", "1", "0"],
                    ),
                    athlete(
                        f"{team_id}-de",
                        f"{abbreviation} Edge",
                        "E. Rusher",
                        "DE",
                        ["5", "4", "2.5", "0"],
                    ),
                ],
            },
        ],
    }


def competition() -> dict:
    return {
        "leaders": [{"name": "passingYards", "leaders": [{"value": 999}]}],
        "competitors": [
            {
                "id": "2",
                "homeAway": "home",
                "team": {"id": "2", "abbreviation": "HOM"},
            },
            {
                "id": "1",
                "homeAway": "away",
                "team": {"id": "1", "abbreviation": "AWY"},
            },
        ],
    }


class NFLTeamLeadersTests(unittest.TestCase):
    def test_extracts_both_teams_and_all_required_categories(self) -> None:
        comp = competition()
        summary = {
            "boxscore": {
                "players": [team_box("2", "HOM", 5), team_box("1", "AWY")]
            }
        }

        leaders = module.extract_nfl_team_leaders(summary, comp)

        self.assertEqual(leaders["away"]["passing"]["name"], "AWY Quarterback One")
        self.assertEqual(leaders["away"]["passing"]["value"], 240)
        self.assertEqual(leaders["away"]["passing"]["detail"], "18/25 CMP/ATT")
        self.assertEqual(leaders["away"]["rushing"]["value"], 88)
        self.assertEqual(leaders["away"]["rushing"]["detail"], "14 CAR")
        self.assertEqual(leaders["away"]["receiving"]["value"], 112)
        self.assertEqual(leaders["away"]["receiving"]["detail"], "7 REC")
        self.assertEqual(leaders["away"]["sacks"]["name"], "AWY Edge")
        self.assertEqual(leaders["away"]["sacks"]["value"], 2.5)
        self.assertEqual(leaders["away"]["tackles"]["name"], "AWY Linebacker")
        self.assertEqual(leaders["away"]["tackles"]["value"], 10)
        self.assertEqual(leaders["away"]["tackles"]["detail"], "7 SOLO")

        self.assertEqual(leaders["home"]["passing"]["team_id"], "2")
        self.assertEqual(leaders["home"]["passing"]["team_abbreviation"], "HOM")
        self.assertEqual(leaders["home"]["passing"]["value"], 245)
        self.assertEqual(leaders["home"]["tackles"]["value"], 15)
        self.assertEqual(
            leaders["home"]["receiving"]["headshot"],
            "https://example.test/2-wr.png",
        )
        self.assertEqual(leaders["home"]["receiving"]["position"], "WR")

    def test_unknown_summary_team_is_not_assigned_to_a_side(self) -> None:
        comp = competition()
        summary = {"boxscore": {"players": [team_box("999", "BAD")]}}

        leaders = module.extract_nfl_team_leaders(summary, comp)

        self.assertFalse(module.team_leaders_have_data(leaders))
        for side in ("away", "home"):
            for category in module.LEADER_CATEGORIES:
                self.assertIsNone(leaders[side][category])

    def test_merge_preserves_existing_overall_leaders(self) -> None:
        comp = competition()
        original_leaders = list(comp["leaders"])
        event = {"competitions": [comp], "season": {"type": 2}}
        summary = {"boxscore": {"players": [team_box("1", "AWY"), team_box("2", "HOM")]}}

        module.merge_nfl_team_leaders(event, summary)

        self.assertEqual(event["competitions"][0]["leaders"], original_leaders)
        self.assertIn("team_leaders", event["competitions"][0])
        self.assertTrue(
            module.team_leaders_have_data(event["competitions"][0]["team_leaders"])
        )

    def test_missing_boxscore_returns_predictable_empty_structure(self) -> None:
        leaders = module.extract_nfl_team_leaders({}, competition())

        self.assertEqual(set(leaders), {"away", "home"})
        self.assertEqual(set(leaders["away"]), set(module.LEADER_CATEGORIES))
        self.assertTrue(all(value is None for value in leaders["away"].values()))
        self.assertTrue(all(value is None for value in leaders["home"].values()))

    def test_parser_is_season_type_agnostic(self) -> None:
        summary = {"boxscore": {"players": [team_box("1", "AWY"), team_box("2", "HOM")]}}

        for season_type in (1, 2, 3):  # preseason, regular season, postseason
            with self.subTest(season_type=season_type):
                event = {
                    "season": {"type": season_type},
                    "competitions": [competition()],
                }
                module.merge_nfl_team_leaders(event, summary)
                leaders = event["competitions"][0]["team_leaders"]
                self.assertEqual(leaders["away"]["passing"]["value"], 240)
                self.assertEqual(leaders["home"]["sacks"]["value"], 2.5)


if __name__ == "__main__":
    unittest.main()
