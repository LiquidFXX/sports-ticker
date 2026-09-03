import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1] / "custom_components" / "sports_ticker"

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

standings = load("standings_parser")
schedule = load("team_schedule")
postseason = load("postseason_parser")


def stat(name, value, display=None): return {"name": name, "value": value, "displayValue": str(value) if display is None else display}
def entry(team_id, abbr, name, stats): return {"team": {"id": str(team_id), "abbreviation": abbr, "displayName": name, "logo": f"https://logo/{abbr}.png"}, "stats": stats}
def sched_event(event_id, date, state, favorite_score=None, opponent_score=None):
    favorite = {"homeAway": "away", "team": {"abbreviation": "ATL", "displayName": "Atlanta"}}; opponent = {"homeAway": "home", "team": {"abbreviation": "BOS", "displayName": "Boston"}}
    if favorite_score is not None: favorite["score"] = str(favorite_score)
    if opponent_score is not None: opponent["score"] = str(opponent_score)
    return {"id": str(event_id), "date": date, "competitions": [{"date": date, "competitors": [favorite, opponent], "status": {"type": {"state": state}}}]}
def playoff_game(event_id, *, series_id=None, note="Conference Semifinals"):
    series = {"id": series_id, "title": "Conference Semifinals", "summary": "BOS leads 2-1", "totalCompetitions": 7} if series_id else {}
    return {"id": str(event_id), "date": "2026-05-01T00:00:00Z", "competitions": [{"date": "2026-05-01T00:00:00Z", "competitors": [{"homeAway": "away", "team": {"id": "1", "abbreviation": "ATL"}, "score": "100"}, {"homeAway": "home", "team": {"id": "2", "abbreviation": "BOS"}, "score": "105", "winner": True}], "series": series, "notes": [{"headline": note}], "status": {"type": {"state": "post", "shortDetail": "Final"}}}]}


class MultiSportPlatformTests(unittest.TestCase):
    def test_nba_conference_division_play_in_and_favorite(self):
        atl = entry(1, "ATL", "Atlanta Hawks", [stat("wins", 40), stat("losses", 32), stat("conferenceRank", 8), stat("streak", -2, "L2"), stat("clincher", 0, "PB")]); bos = entry(2, "BOS", "Boston Celtics", [stat("conferenceRank", 1), stat("clincher", 0, "x")])
        payload = {"season": {"year": 2026, "type": 2}, "children": [{"name": "Eastern Conference", "standings": {"entries": [bos, atl]}, "children": [{"name": "Atlantic Division", "standings": {"entries": [bos]}}, {"name": "Southeast Division", "standings": {"entries": [atl]}}]}]}
        data = standings.normalize_league_standings(payload, league="nba", profile="nba", favorite_team="ATL"); by = {row["abbreviation"]: row for row in data["teams"]}
        self.assertEqual(data["season"], 2026); self.assertTrue(by["ATL"]["favorite"]); self.assertEqual(by["ATL"]["division"], "Southeast Division"); self.assertTrue(by["ATL"]["play_in"]); self.assertTrue(by["ATL"]["clinched_play_in"]); self.assertEqual(by["ATL"]["streak"], "L2"); self.assertTrue(by["BOS"]["clinched_playoff"])

    def test_wnba_top_eight_cut_line(self):
        entries = [entry(pos, f"T{pos}", f"Team {pos}", [stat("rank", pos)]) for pos in range(1, 11)]; payload = {"season": {"year": 2026, "type": 2}, "children": [{"name": "WNBA", "standings": {"entries": entries}}]}
        data = standings.normalize_league_standings(payload, league="wnba", profile="wnba", favorite_team="T9"); by = {row["abbreviation"]: row for row in data["teams"]}
        self.assertTrue(by["T8"]["in_playoffs"]); self.assertFalse(by["T9"]["in_playoffs"]); self.assertTrue(by["T9"]["in_the_hunt"]); self.assertEqual(data["playoff"]["cut_line"], 8)

    def test_nhl_wildcard_clinch_and_otl(self):
        car = entry(1, "CAR", "Carolina", [stat("overtimeLosses", 8), stat("points", 108), stat("playoffSeed", 5), stat("wildCardRank", 1), stat("clincher", 0, "x")]); payload = {"season": {"year": 2026, "type": 2}, "children": [{"name": "Eastern Conference", "children": [{"name": "Metropolitan Division", "standings": {"entries": [car]}}]}]}
        row = standings.normalize_league_standings(payload, league="nhl", profile="nhl")["teams"][0]
        self.assertEqual(row["overtime_losses"], 8); self.assertEqual(row["points"], 108.0); self.assertTrue(row["wildcard"]); self.assertTrue(row["clinched_playoff"])

    def test_soccer_table_and_form_no_fake_playoff(self):
        ars = entry(1, "ARS", "Arsenal", [stat("wins", 20), stat("draws", 5), stat("losses", 3), stat("points", 65), stat("goalsFor", 60), stat("goalsAgainst", 25), stat("rank", 1), stat("form", 0, "WWDLW")]); payload = {"season": {"year": 2026, "type": 2}, "children": [{"name": "Premier League", "standings": {"entries": [ars]}}]}
        data = standings.normalize_league_standings(payload, league="epl", profile="soccer", favorite_team="ARS"); row = data["teams"][0]
        self.assertEqual(row["position"], 1); self.assertEqual(row["draws"], 5); self.assertEqual(row["differential"], 35.0); self.assertEqual(row["form"], "WWDLW"); self.assertIsNone(row["in_playoffs"]); self.assertIsNone(data["playoff"]["cut_line"])

    def test_mlb_clincher_codes_profile_specific(self):
        nyy = entry(1, "NYY", "Yankees", [stat("playoffSeed", 1), stat("clincher", 0, "x*")]); payload = {"season": {"year": 2026, "type": 2}, "children": [{"name": "American League", "children": [{"name": "AL East", "standings": {"entries": [nyy]}}]}]}
        row = standings.normalize_league_standings(payload, league="mlb", profile="mlb")["teams"][0]
        self.assertTrue(row["clinched_division"]); self.assertTrue(row["clinched_best_record"]); self.assertTrue(row["in_playoffs"])

    def test_missing_standings_fields_are_none(self):
        row = standings.normalize_league_standings({"children": [{"name": "League", "standings": {"entries": [entry(1, "ABC", "ABC", [])]}}]}, league="epl", profile="soccer")["teams"][0]
        self.assertIsNone(row["wins"]); self.assertIsNone(row["streak"]); self.assertIsNone(row["espn_clincher"])

    def test_malformed_standings_raises(self):
        with self.assertRaises(ValueError): standings.normalize_league_standings({}, league="nba", profile="nba")

    def test_schedule_recent_form_record_streak(self):
        events = [sched_event(1, "2026-08-30T00:00:00Z", "post", 5, 2), sched_event(2, "2026-08-29T00:00:00Z", "post", 4, 1), sched_event(3, "2026-08-28T00:00:00Z", "post", 1, 3)]; games = schedule.normalize_recent_games(events, "ATL", limit=5)
        self.assertEqual(schedule.recent_form(games), "WWL"); self.assertEqual(schedule.recent_record(games), "2-1"); self.assertEqual(schedule.current_streak(games), "W2")

    def test_schedule_upcoming_sorted(self):
        games = schedule.normalize_upcoming_games([sched_event(1, "2099-09-03T00:00:00Z", "pre"), sched_event(2, "2099-09-02T00:00:00Z", "pre")], "ATL", limit=5)
        self.assertEqual([game["event_id"] for game in games], ["2", "1"])

    def test_schedule_tie_supported(self):
        games = schedule.normalize_recent_games([sched_event(1, "2026-08-30T00:00:00Z", "post", 2, 2)], "ATL")
        self.assertEqual(games[0]["result"], "T"); self.assertEqual(schedule.recent_record(games), "0-0-1")

    def test_postseason_series_grouping(self):
        data = postseason.normalize_postseason({"events": [playoff_game(1, series_id="s1"), playoff_game(2, series_id="s1")]}, league="nba", season=2026); series = data["rounds"][0]["series"][0]
        self.assertEqual(series["key"], "s1"); self.assertEqual(len(series["games"]), 2); self.assertEqual(series["source"], "espn_series")

    def test_postseason_fallback_does_not_infer_bracket_links(self):
        data = postseason.normalize_postseason({"events": [playoff_game(1, note="Wild Card"), playoff_game(2, note="Wild Card")]}, league="mlb", season=2026)
        self.assertEqual(len(data["rounds"][0]["series"]), 1); self.assertFalse(data["normalization"]["bracket_links_inferred"])

    def test_malformed_postseason_raises(self):
        with self.assertRaises(ValueError): postseason.normalize_postseason({}, league="nfl", season=2026)


if __name__ == "__main__": unittest.main()
