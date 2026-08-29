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
spec = importlib.util.spec_from_file_location("nfl_standings_parser", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def stat(name: str, value=None, display=None) -> dict:
    item = {"name": name}
    if value is not None:
        item["value"] = value
    if display is not None:
        item["displayValue"] = display
    return item


def entry(
    team_id: str,
    abbr: str,
    name: str,
    *,
    seed: int | None,
    wins: int,
    losses: int,
    ties: int = 0,
    pct: float = 0.0,
    streak: str | None = None,
    clincher: str | None = None,
    games_back: float | None = None,
    include_optional: bool = True,
) -> dict:
    stats = [
        stat("wins", wins, str(wins)),
        stat("losses", losses, str(losses)),
        stat("ties", ties, str(ties)),
        stat("winPercent", pct, f"{pct:.3f}"),
        stat("overall", display=f"{wins}-{losses}" + (f"-{ties}" if ties else "")),
    ]
    if seed is not None:
        stats.append(stat("playoffSeed", seed, str(seed)))
    if include_optional and streak is not None:
        stats.append(stat("streak", display=streak))
    if include_optional and clincher is not None:
        stats.append(stat("clincher", display=clincher))
    if include_optional and games_back is not None:
        stats.append(stat("gamesBehind", games_back, str(games_back)))

    return {
        "team": {
            "id": team_id,
            "abbreviation": abbr,
            "displayName": name,
            "shortDisplayName": name.split()[-1],
            "logos": [{"href": f"https://example.test/{abbr}.png"}],
        },
        "stats": stats,
    }


def division(name: str, abbreviation: str, entries: list[dict]) -> dict:
    return {
        "name": name,
        "abbreviation": abbreviation,
        "standings": {"entries": entries},
    }


def conference(name: str, abbreviation: str, entries: list[dict], divisions: list[dict]) -> dict:
    return {
        "name": name,
        "abbreviation": abbreviation,
        "standings": {
            "season": 2026,
            "seasonType": 2,
            "seasonTypeName": "Regular Season",
            "entries": entries,
        },
        "children": divisions,
    }


def sample_payload() -> dict:
    buf = entry("2", "BUF", "Buffalo Bills", seed=1, wins=13, losses=2, pct=.867, streak="W5", clincher="*", games_back=0)
    mia = entry("15", "MIA", "Miami Dolphins", seed=8, wins=9, losses=6, pct=.600, streak="W2", clincher="", games_back=4)
    bal = entry("33", "BAL", "Baltimore Ravens", seed=3, wins=11, losses=4, pct=.733, streak="W3", clincher="z", games_back=2)
    cin = entry("4", "CIN", "Cincinnati Bengals", seed=7, wins=10, losses=5, pct=.667, streak="L1", clincher="x", games_back=3)

    phi = entry("21", "PHI", "Philadelphia Eagles", seed=2, wins=12, losses=3, pct=.800, streak="W4", clincher="z", games_back=1)
    atl = entry("1", "ATL", "Atlanta Falcons", seed=6, wins=10, losses=5, pct=.667, streak="W1", clincher="y", games_back=3)
    tb = entry("27", "TB", "Tampa Bay Buccaneers", seed=8, wins=8, losses=7, pct=.533, streak="L2", clincher="e", games_back=5)
    gb = entry("9", "GB", "Green Bay Packers", seed=5, wins=10, losses=5, pct=.667, streak="W2", games_back=3)

    return {
        "season": {"year": 2026, "type": 2, "typeName": "Regular Season"},
        "week": {"number": 16},
        "children": [
            conference(
                "American Football Conference",
                "AFC",
                [buf, bal, cin, mia],
                [
                    division("AFC East", "AFC EAST", [buf, mia]),
                    division("AFC North", "AFC NORTH", [bal, cin]),
                ],
            ),
            conference(
                "National Football Conference",
                "NFC",
                [phi, gb, atl, tb],
                [
                    division("NFC East", "NFC EAST", [phi]),
                    division("NFC North", "NFC NORTH", [gb]),
                    division("NFC South", "NFC SOUTH", [atl, tb]),
                ],
            ),
        ],
    }


class NFLStandingsParserTests(unittest.TestCase):
    def test_normalizes_afc_and_nfc_standings(self) -> None:
        data = module.normalize_nfl_standings(sample_payload(), favorite_team="ATL", updated_at="2026-12-20T12:00:00+00:00")

        self.assertEqual(data["season"], 2026)
        self.assertEqual(data["week"], 16)
        self.assertEqual(data["season_type"], 2)
        self.assertEqual(len(data["conferences"]["AFC"]), 4)
        self.assertEqual(len(data["conferences"]["NFC"]), 4)
        self.assertEqual(len(data["teams"]), 8)
        self.assertEqual(data["favorite_team"], "ATL")

    def test_division_leaders_and_division_metadata(self) -> None:
        data = module.normalize_nfl_standings(sample_payload())
        by_abbr = {row["abbreviation"]: row for row in data["teams"]}

        self.assertTrue(by_abbr["BUF"]["division_leader"])
        self.assertTrue(by_abbr["BAL"]["division_leader"])
        self.assertTrue(by_abbr["ATL"]["division_leader"])
        self.assertFalse(by_abbr["MIA"]["division_leader"])
        self.assertEqual(data["divisions"]["AFC East"]["leader"], "BUF")
        self.assertEqual(data["divisions"]["NFC South"]["teams"], ["ATL", "TB"])

    def test_seeds_playoff_positions_and_cut_line_helpers(self) -> None:
        data = module.normalize_nfl_standings(sample_payload())
        by_abbr = {row["abbreviation"]: row for row in data["teams"]}

        self.assertEqual(by_abbr["BUF"]["seed"], 1)
        self.assertEqual(by_abbr["CIN"]["playoff_position"], 7)
        self.assertTrue(by_abbr["CIN"]["wildcard"])
        self.assertTrue(by_abbr["CIN"]["in_playoffs"])
        self.assertTrue(by_abbr["MIA"]["in_the_hunt"])
        self.assertEqual(data["playoff"]["cut_line_seed"], 7)
        self.assertEqual(by_abbr["CIN"]["sources"]["wildcard"], "derived_from_regular_season_seed")

    def test_streak_games_back_and_favorite_team(self) -> None:
        data = module.normalize_nfl_standings(sample_payload(), favorite_team="atl")
        by_abbr = {row["abbreviation"]: row for row in data["teams"]}

        self.assertEqual(by_abbr["BUF"]["streak"], "W5")
        self.assertEqual(by_abbr["ATL"]["streak"], "W1")
        self.assertEqual(by_abbr["ATL"]["games_back"], 3.0)
        self.assertTrue(by_abbr["ATL"]["favorite"])
        self.assertFalse(by_abbr["TB"]["favorite"])

    def test_clinch_and_elimination_flags_preserve_espn_clincher(self) -> None:
        data = module.normalize_nfl_standings(sample_payload())
        by_abbr = {row["abbreviation"]: row for row in data["teams"]}

        self.assertEqual(by_abbr["BUF"]["espn_clincher"], "*")
        self.assertTrue(by_abbr["BUF"]["clinched_playoff"])
        self.assertTrue(by_abbr["BUF"]["clinched_division"])
        self.assertTrue(by_abbr["BUF"]["clinched_first_seed"])
        self.assertIsNone(by_abbr["BUF"]["clinched_conference"])
        self.assertTrue(by_abbr["ATL"]["clinched_wildcard"])
        self.assertTrue(by_abbr["TB"]["eliminated"])
        self.assertFalse(by_abbr["TB"]["in_the_hunt"])
        self.assertEqual(by_abbr["TB"]["sources"]["eliminated"], "espn_clincher")

    def test_missing_optional_espn_fields_remain_null(self) -> None:
        minimal = entry("17", "NE", "New England Patriots", seed=None, wins=0, losses=0, include_optional=False)
        payload = {
            "season": {"year": 2026, "type": 1, "typeName": "Preseason"},
            "children": [
                conference(
                    "American Football Conference",
                    "AFC",
                    [minimal],
                    [division("AFC East", "AFC EAST", [minimal])],
                ),
                conference("National Football Conference", "NFC", [], []),
            ],
        }
        data = module.normalize_nfl_standings(payload)
        row = data["conferences"]["AFC"][0]

        self.assertIsNone(row["seed"])
        self.assertIsNone(row["streak"])
        self.assertIsNone(row["games_back"])
        self.assertIsNone(row["clinched_playoff"])
        self.assertIsNone(row["eliminated"])
        self.assertIsNone(row["wildcard"])
        self.assertIsNone(row["in_the_hunt"])

    def test_partial_response_can_fall_back_to_division_entries(self) -> None:
        buf = entry("2", "BUF", "Buffalo Bills", seed=1, wins=1, losses=0, pct=1.0)
        payload = {
            "season": {"year": 2026, "type": 2},
            "children": [
                {
                    "name": "American Football Conference",
                    "abbreviation": "AFC",
                    "standings": {},
                    "children": [division("AFC East", "AFC EAST", [buf])],
                },
                {
                    "name": "National Football Conference",
                    "abbreviation": "NFC",
                    "standings": {"entries": []},
                    "children": [],
                },
            ],
        }
        data = module.normalize_nfl_standings(payload)
        self.assertEqual(data["conferences"]["AFC"][0]["abbreviation"], "BUF")

    def test_malformed_response_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "conference groups"):
            module.normalize_nfl_standings({"children": None})

        with self.assertRaisesRegex(ValueError, "AFC/NFC"):
            module.normalize_nfl_standings({"children": [{"name": "Other"}]})


if __name__ == "__main__":
    unittest.main()
