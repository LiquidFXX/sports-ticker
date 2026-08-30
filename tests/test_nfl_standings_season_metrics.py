from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "sports_ticker"
    / "nfl_standings_parser.py"
)
spec = importlib.util.spec_from_file_location("nfl_standings_parser_metrics", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def stat(name: str, *, value=None, display=None) -> dict:
    result = {"name": name}
    if value is not None:
        result["value"] = value
    if display is not None:
        result["displayValue"] = display
    return result


def team_entry(abbr: str, team_id: str) -> dict:
    return {
        "team": {
            "id": team_id,
            "abbreviation": abbr,
            "displayName": "Atlanta Falcons" if abbr == "ATL" else "Tampa Bay Buccaneers",
            "shortDisplayName": "Falcons" if abbr == "ATL" else "Buccaneers",
        },
        "stats": [
            stat("wins", value=10, display="10"),
            stat("losses", value=6, display="6"),
            stat("ties", value=0, display="0"),
            stat("overall", display="10-6"),
            stat("playoffSeed", value=6, display="6"),
            stat("pointsFor", value=410, display="410"),
            stat("pointsAgainst", value=350, display="350"),
            stat("home", display="6-2"),
            stat("road", display="4-4"),
            stat("division", display="4-2"),
            stat("conference", display="8-4"),
        ],
    }


def payload() -> dict:
    atl = team_entry("ATL", "1")
    tb = team_entry("TB", "27")
    return {
        "season": {"year": 2026, "type": 2, "typeName": "Regular Season"},
        "week": {"number": 17},
        "children": [
            {
                "name": "American Football Conference",
                "abbreviation": "AFC",
                "standings": {"entries": []},
                "children": [],
            },
            {
                "name": "National Football Conference",
                "abbreviation": "NFC",
                "standings": {"entries": [atl, tb]},
                "children": [
                    {
                        "name": "NFC South",
                        "abbreviation": "NFC SOUTH",
                        "standings": {"entries": [atl, tb]},
                    }
                ],
            },
        ],
    }


class NFLStandingsSeasonMetricTests(unittest.TestCase):
    def test_exposes_card_friendly_season_metrics(self):
        data = module.normalize_nfl_standings(payload(), favorite_team="ATL")
        atl = next(row for row in data["teams"] if row["abbreviation"] == "ATL")

        self.assertEqual(atl["games_played"], 16)
        self.assertEqual(atl["points_for"], 410.0)
        self.assertEqual(atl["points_against"], 350.0)
        self.assertEqual(atl["point_differential"], 60.0)
        self.assertEqual(atl["points_per_game"], 25.6)
        self.assertEqual(atl["points_allowed_per_game"], 21.9)
        self.assertEqual(atl["home_record"], "6-2")
        self.assertEqual(atl["away_record"], "4-4")
        self.assertEqual(atl["division_record"], "4-2")
        self.assertEqual(atl["conference_record"], "8-4")
        self.assertEqual(atl["sources"]["point_differential"], "derived_from_espn_points")

    def test_missing_optional_metrics_remain_null(self):
        data = payload()
        atl = data["children"][1]["standings"]["entries"][0]
        atl["stats"] = [item for item in atl["stats"] if item["name"] in {"wins", "losses", "ties", "overall", "playoffSeed"}]
        data["children"][1]["children"][0]["standings"]["entries"][0] = atl

        normalized = module.normalize_nfl_standings(data)
        row = next(item for item in normalized["teams"] if item["abbreviation"] == "ATL")

        self.assertIsNone(row["points_for"])
        self.assertIsNone(row["points_against"])
        self.assertIsNone(row["point_differential"])
        self.assertIsNone(row["points_per_game"])
        self.assertIsNone(row["home_record"])
        self.assertIsNone(row["division_record"])


if __name__ == "__main__":
    unittest.main()
