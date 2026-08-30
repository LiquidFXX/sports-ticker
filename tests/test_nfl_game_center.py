import unittest

from custom_components.sports_ticker.nfl_game_center import (
    empty_game_center,
    extract_nfl_game_center,
    game_center_have_data,
    merge_game_center_fallback,
)


def _competition():
    return {
        "status": {"type": {"state": "in"}},
        "competitors": [
            {
                "id": "1",
                "homeAway": "away",
                "team": {"id": "1", "abbreviation": "ATL"},
            },
            {
                "id": "15",
                "homeAway": "home",
                "team": {"id": "15", "abbreviation": "MIA"},
            },
        ],
        "situation": {
            "possession": "1",
            "down": 3,
            "distance": 4,
            "yardLine": 62,
            "yardsToEndzone": 38,
            "downDistanceText": "3rd & 4 at MIA 38",
            "shortDownDistanceText": "3rd & 4",
            "possessionText": "MIA 38",
            "isRedZone": False,
            "homeTimeouts": 2,
            "awayTimeouts": 1,
            "lastPlay": {
                "id": "4010000001234",
                "text": "B. Robinson left tackle for 7 yards",
                "shortText": "7 yard rush",
                "type": {"text": "Rush", "abbreviation": "RUSH"},
                "scoringPlay": False,
                "period": {"number": 4},
                "clock": {"displayValue": "6:42"},
                "homeScore": 20,
                "awayScore": 24,
                "end": {
                    "down": 3,
                    "distance": 4,
                    "yardLine": 62,
                    "yardsToEndzone": 38,
                    "possessionText": "MIA 38",
                    "team": {"id": "1"},
                },
            },
        },
    }


class NFLGameCenterTests(unittest.TestCase):
    def test_extracts_live_situation_last_play_win_probability_and_drive(self):
        competition = _competition()
        event = {"id": "401000000", "status": {"type": {"state": "in"}}}
        summary = {
            "winprobability": [
                {"playId": "1", "homeWinPercentage": 0.55, "tiePercentage": 0.0},
                {"playId": "2", "homeWinPercentage": 0.28, "tiePercentage": 0.0},
            ],
            "drives": {
                "current": {
                    "id": "drive-1",
                    "team": {"id": "1", "abbreviation": "ATL"},
                    "description": "8 plays, 52 yards, 4:03",
                    "result": "",
                    "yards": 52,
                    "offensivePlays": 8,
                    "timeElapsed": {"displayValue": "4:03"},
                    "start": {
                        "period": {"number": 4},
                        "clock": {"displayValue": "10:45"},
                        "yardLine": 25,
                        "yardsToEndzone": 75,
                        "text": "ATL 25",
                    },
                    "end": {
                        "period": {"number": 4},
                        "clock": {"displayValue": "6:42"},
                        "yardLine": 62,
                        "yardsToEndzone": 38,
                        "text": "MIA 38",
                    },
                }
            },
        }

        result = extract_nfl_game_center(event, competition, summary)

        self.assertTrue(result["available"])
        self.assertEqual(result["state"], "in")
        self.assertEqual(result["situation"]["possession_team_id"], "1")
        self.assertEqual(result["situation"]["possession_team_abbreviation"], "ATL")
        self.assertEqual(result["situation"]["possession_side"], "away")
        self.assertEqual(result["situation"]["down"], 3)
        self.assertEqual(result["situation"]["distance"], 4)
        self.assertEqual(result["situation"]["possession_text"], "MIA 38")
        self.assertEqual(result["situation"]["home_timeouts"], 2)
        self.assertEqual(result["situation"]["away_timeouts"], 1)
        self.assertEqual(result["last_play"]["text"], "B. Robinson left tackle for 7 yards")
        self.assertEqual(result["last_play"]["period"], 4)
        self.assertEqual(result["last_play"]["clock"], "6:42")
        self.assertEqual(result["win_probability"]["home"], 0.28)
        self.assertAlmostEqual(result["win_probability"]["away"], 0.72)
        self.assertEqual(result["win_probability"]["play_id"], "2")
        self.assertEqual(result["current_drive"]["team_abbreviation"], "ATL")
        self.assertEqual(result["current_drive"]["yards"], 52)
        self.assertEqual(result["current_drive"]["offensive_plays"], 8)
        self.assertEqual(result["current_drive"]["time_elapsed"], "4:03")

    def test_uses_header_situation_when_scoreboard_situation_is_missing(self):
        competition = _competition()
        competition.pop("situation")
        event = {"status": {"type": {"state": "in"}}}
        summary = {
            "header": {
                "competitions": [
                    {
                        "situation": {
                            "possession": "15",
                            "down": 1,
                            "distance": 10,
                            "yardLine": 80,
                            "yardsToEndzone": 20,
                            "isRedZone": True,
                            "homeTimeouts": 3,
                            "awayTimeouts": 2,
                        }
                    }
                ]
            }
        }

        result = extract_nfl_game_center(event, competition, summary)

        self.assertEqual(result["situation"]["possession_team_abbreviation"], "MIA")
        self.assertEqual(result["situation"]["possession_side"], "home")
        self.assertTrue(result["situation"]["is_red_zone"])

    def test_uses_last_play_end_state_as_situation_fallback(self):
        competition = _competition()
        competition["situation"] = {
            "lastPlay": {
                "playId": "play-1",
                "text": "Run for 5 yards",
                "end": {
                    "down": 2,
                    "distance": 5,
                    "yardLine": 85,
                    "yardsToEndzone": 15,
                    "downDistanceText": "2nd & 5 at MIA 15",
                    "shortDownDistanceText": "2nd & 5",
                    "possessionText": "MIA 15",
                    "team": {"id": "1"},
                },
            },
            "homeTimeouts": 3,
            "awayTimeouts": 2,
        }

        result = extract_nfl_game_center({}, competition, {})

        self.assertEqual(result["situation"]["down"], 2)
        self.assertEqual(result["situation"]["distance"], 5)
        self.assertEqual(result["situation"]["yards_to_endzone"], 15)
        self.assertTrue(result["situation"]["is_red_zone"])
        self.assertEqual(result["situation"]["possession_team_abbreviation"], "ATL")

    def test_empty_structure_is_predictable(self):
        result = empty_game_center()

        self.assertFalse(result["available"])
        self.assertIsNone(result["situation"]["possession_team_id"])
        self.assertIsNone(result["last_play"]["text"])
        self.assertIsNone(result["win_probability"]["home"])
        self.assertIsNone(result["current_drive"]["team_id"])
        self.assertFalse(game_center_have_data(result))

    def test_cached_values_only_fill_missing_current_fields(self):
        current = empty_game_center()
        current["state"] = "in"
        current["situation"]["down"] = 2
        current["situation"]["distance"] = 7
        cached = empty_game_center()
        cached["available"] = True
        cached["situation"]["down"] = 3
        cached["win_probability"]["home"] = 0.61
        cached["win_probability"]["away"] = 0.39
        cached["win_probability"]["source"] = "espn_summary"

        merged = merge_game_center_fallback(current, cached)

        self.assertEqual(merged["situation"]["down"], 2)
        self.assertEqual(merged["situation"]["distance"], 7)
        self.assertEqual(merged["win_probability"]["home"], 0.61)
        self.assertEqual(merged["win_probability"]["away"], 0.39)
        self.assertTrue(merged["available"])


if __name__ == "__main__":
    unittest.main()
