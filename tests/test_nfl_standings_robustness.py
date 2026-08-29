from __future__ import annotations

import unittest

from test_nfl_standings_parser import conference, division, entry, module, stat


class NFLStandingsRobustnessTests(unittest.TestCase):
    def test_numeric_streak_is_normalized_to_win_loss_form(self) -> None:
        buf = entry("2", "BUF", "Buffalo Bills", seed=1, wins=4, losses=0, pct=1.0)
        buf["stats"] = [item for item in buf["stats"] if item["name"] != "streak"]
        buf["stats"].append(stat("streak", 4))
        mia = entry("15", "MIA", "Miami Dolphins", seed=8, wins=1, losses=3, pct=.250)
        mia["stats"] = [item for item in mia["stats"] if item["name"] != "streak"]
        mia["stats"].append(stat("streak", -2))
        payload = {
            "season": {"year": 2026, "type": 2},
            "children": [
                conference(
                    "American Football Conference",
                    "AFC",
                    [buf, mia],
                    [division("AFC East", "AFC EAST", [buf, mia])],
                ),
                conference("National Football Conference", "NFC", [], []),
            ],
        }
        data = module.normalize_nfl_standings(payload)
        by_abbr = {row["abbreviation"]: row for row in data["teams"]}
        self.assertEqual(by_abbr["BUF"]["streak"], "W4")
        self.assertEqual(by_abbr["MIA"]["streak"], "L2")

    def test_numeric_zero_clincher_is_not_exposed_as_fake_code(self) -> None:
        buf = entry("2", "BUF", "Buffalo Bills", seed=8, wins=8, losses=7, pct=.533)
        buf["stats"].append(stat("clincher", 0))
        payload = {
            "season": {"year": 2026, "type": 2},
            "children": [
                conference(
                    "American Football Conference",
                    "AFC",
                    [buf],
                    [division("AFC East", "AFC EAST", [buf])],
                ),
                conference("National Football Conference", "NFC", [], []),
            ],
        }
        row = module.normalize_nfl_standings(payload)["conferences"]["AFC"][0]
        self.assertIsNone(row["espn_clincher"])
        self.assertFalse(row["clinched_playoff"])
        self.assertFalse(row["eliminated"])
        self.assertTrue(row["in_the_hunt"])

    def test_nested_conference_groups_are_supported(self) -> None:
        buf = entry("2", "BUF", "Buffalo Bills", seed=1, wins=1, losses=0, pct=1.0)
        payload = {
            "season": {"year": 2026, "type": 2},
            "children": [
                {
                    "name": "NFL",
                    "children": [
                        conference(
                            "American Football Conference",
                            "AFC",
                            [buf],
                            [division("AFC East", "AFC EAST", [buf])],
                        ),
                        conference("National Football Conference", "NFC", [], []),
                    ],
                }
            ],
        }
        data = module.normalize_nfl_standings(payload)
        self.assertEqual(data["conferences"]["AFC"][0]["abbreviation"], "BUF")


if __name__ == "__main__":
    unittest.main()
