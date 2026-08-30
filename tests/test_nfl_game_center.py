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


def test_extracts_live_situation_last_play_win_probability_and_drive():
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

    assert result["available"] is True
    assert result["state"] == "in"
    assert result["situation"]["possession_team_id"] == "1"
    assert result["situation"]["possession_team_abbreviation"] == "ATL"
    assert result["situation"]["possession_side"] == "away"
    assert result["situation"]["down"] == 3
    assert result["situation"]["distance"] == 4
    assert result["situation"]["possession_text"] == "MIA 38"
    assert result["situation"]["home_timeouts"] == 2
    assert result["situation"]["away_timeouts"] == 1
    assert result["last_play"]["text"] == "B. Robinson left tackle for 7 yards"
    assert result["last_play"]["period"] == 4
    assert result["last_play"]["clock"] == "6:42"
    assert result["win_probability"]["home"] == 0.28
    assert result["win_probability"]["away"] == 0.72
    assert result["win_probability"]["play_id"] == "2"
    assert result["current_drive"]["team_abbreviation"] == "ATL"
    assert result["current_drive"]["yards"] == 52
    assert result["current_drive"]["offensive_plays"] == 8
    assert result["current_drive"]["time_elapsed"] == "4:03"


def test_uses_header_situation_when_scoreboard_situation_is_missing():
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

    assert result["situation"]["possession_team_abbreviation"] == "MIA"
    assert result["situation"]["possession_side"] == "home"
    assert result["situation"]["is_red_zone"] is True


def test_uses_last_play_end_state_as_situation_fallback():
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

    assert result["situation"]["down"] == 2
    assert result["situation"]["distance"] == 5
    assert result["situation"]["yards_to_endzone"] == 15
    assert result["situation"]["is_red_zone"] is True
    assert result["situation"]["possession_team_abbreviation"] == "ATL"


def test_empty_structure_is_predictable():
    result = empty_game_center()

    assert result["available"] is False
    assert result["situation"]["possession_team_id"] is None
    assert result["last_play"]["text"] is None
    assert result["win_probability"]["home"] is None
    assert result["current_drive"]["team_id"] is None
    assert game_center_have_data(result) is False


def test_cached_values_only_fill_missing_current_fields():
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

    assert merged["situation"]["down"] == 2
    assert merged["situation"]["distance"] == 7
    assert merged["win_probability"]["home"] == 0.61
    assert merged["win_probability"]["away"] == 0.39
    assert merged["available"] is True
