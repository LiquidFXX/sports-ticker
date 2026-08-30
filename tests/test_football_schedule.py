from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "sports_ticker"
    / "football_schedule.py"
)
spec = importlib.util.spec_from_file_location("football_schedule", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def game(event_id: str, date: str, favorite_score: int, opponent_score: int, opponent: str, *, home_away: str = "home") -> dict:
    favorite = {
        "homeAway": home_away,
        "score": str(favorite_score),
        "team": {
            "abbreviation": "ATL",
            "displayName": "Atlanta Falcons",
            "logo": "https://example.test/ATL.png",
        },
    }
    other_side = "away" if home_away == "home" else "home"
    other = {
        "homeAway": other_side,
        "score": str(opponent_score),
        "team": {
            "abbreviation": opponent,
            "displayName": f"{opponent} Team",
            "logo": f"https://example.test/{opponent}.png",
        },
    }
    return {
        "id": event_id,
        "date": date,
        "week": {"number": int(event_id)},
        "season": {"year": 2026, "type": 2},
        "competitions": [
            {
                "date": date,
                "status": {"type": {"state": "post", "shortDetail": "Final"}},
                "competitors": [favorite, other],
                "venue": {"fullName": "Test Stadium"},
                "broadcasts": [{"names": ["FOX"]}],
            }
        ],
    }


class FootballScheduleTests(unittest.TestCase):
    def test_recent_games_are_sorted_newest_first_and_limited(self):
        events = [
            game("1", "2026-09-01T17:00:00Z", 24, 20, "TB"),
            game("2", "2026-09-08T17:00:00Z", 17, 27, "CAR", home_away="away"),
            game("3", "2026-09-15T17:00:00Z", 31, 31, "NO"),
        ]

        recent = module.normalize_recent_games(events, "ATL", limit=2)

        self.assertEqual([item["event_id"] for item in recent], ["3", "2"])
        self.assertEqual(recent[0]["result"], "T")
        self.assertEqual(recent[1]["result"], "L")
        self.assertEqual(recent[1]["opponent"], "CAR")
        self.assertEqual(recent[1]["home_away"], "away")
        self.assertEqual(recent[1]["broadcasts"], ["FOX"])

    def test_recent_form_uses_normalized_results(self):
        recent = module.normalize_recent_games(
            [
                game("1", "2026-09-01T17:00:00Z", 24, 20, "TB"),
                game("2", "2026-09-08T17:00:00Z", 17, 27, "CAR"),
                game("3", "2026-09-15T17:00:00Z", 31, 31, "NO"),
            ],
            "ATL",
            limit=5,
        )
        self.assertEqual(module.recent_form(recent), "TLW")

    def test_pre_and_unrelated_games_are_ignored(self):
        completed = game("1", "2026-09-01T17:00:00Z", 24, 20, "TB")
        upcoming = game("2", "2026-09-08T17:00:00Z", 0, 0, "CAR")
        upcoming["competitions"][0]["status"]["type"]["state"] = "pre"
        unrelated = game("3", "2026-09-15T17:00:00Z", 10, 7, "NO")
        unrelated["competitions"][0]["competitors"][0]["team"]["abbreviation"] = "DAL"

        recent = module.normalize_recent_games([completed, upcoming, unrelated], "ATL")

        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["event_id"], "1")
        self.assertEqual(recent[0]["score"], "24-20")
        self.assertEqual(recent[0]["margin"], 4)


if __name__ == "__main__":
    unittest.main()
