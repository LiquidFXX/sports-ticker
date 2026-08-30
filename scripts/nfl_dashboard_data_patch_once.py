from pathlib import Path


def patch_standings() -> None:
    path = Path("custom_components/sports_ticker/nfl_standings_parser.py")
    text = path.read_text(encoding="utf-8")

    marker = '''    wins = _stat_int(_get(stats, "wins"))
    losses = _stat_int(_get(stats, "losses"))
    ties = _stat_int(_get(stats, "ties"))
    win_percentage = _stat_float(_get(stats, "winpercent", "winpercentage"))

    record_stat = _get(stats, "overall", "overallrecord", "record")
'''
    replacement = '''    wins = _stat_int(_get(stats, "wins"))
    losses = _stat_int(_get(stats, "losses"))
    ties = _stat_int(_get(stats, "ties"))
    win_percentage = _stat_float(_get(stats, "winpercent", "winpercentage"))

    games_played = (
        wins + losses + (ties or 0)
        if wins is not None and losses is not None
        else None
    )
    points_for = _stat_float(_get(stats, "pointsfor", "points", "pf"))
    points_against = _stat_float(_get(stats, "pointsagainst", "pa"))
    differential_stat = _get(stats, "pointdifferential", "differential", "pointdiff")
    point_differential = _stat_float(differential_stat)
    point_differential_source = "espn_stat" if point_differential is not None else None
    if point_differential is None and points_for is not None and points_against is not None:
        point_differential = points_for - points_against
        point_differential_source = "derived_from_espn_points"

    points_per_game = (
        round(points_for / games_played, 1)
        if points_for is not None and games_played
        else None
    )
    points_allowed_per_game = (
        round(points_against / games_played, 1)
        if points_against is not None and games_played
        else None
    )

    home_record = _display(_get(stats, "home", "homerecord"))
    away_record = _display(_get(stats, "road", "away", "roadrecord", "awayrecord"))
    division_record = _display(_get(stats, "division", "divisionrecord", "divrecord", "vsdivision"))
    conference_record = _display(_get(stats, "conference", "conferencerecord", "confrecord", "vsconference"))

    record_stat = _get(stats, "overall", "overallrecord", "record")
'''
    if "points_allowed_per_game = (" not in text:
        if marker not in text:
            raise SystemExit("standings W/L marker not found")
        text = text.replace(marker, replacement, 1)

    return_marker = '''        "record": record,
        "win_percentage": win_percentage,
        "conference": conference,
'''
    return_replacement = '''        "record": record,
        "win_percentage": win_percentage,
        "games_played": games_played,
        "points_for": points_for,
        "points_against": points_against,
        "point_differential": point_differential,
        "points_per_game": points_per_game,
        "points_allowed_per_game": points_allowed_per_game,
        "home_record": home_record,
        "away_record": away_record,
        "division_record": division_record,
        "conference_record": conference_record,
        "conference": conference,
'''
    if '"points_for": points_for' not in text:
        if return_marker not in text:
            raise SystemExit("standings return marker not found")
        text = text.replace(return_marker, return_replacement, 1)

    source_marker = '''            "record": record_source,
            "division_rank": division_rank_source,
'''
    source_replacement = '''            "record": record_source,
            "points_for": "espn_stat" if points_for is not None else None,
            "points_against": "espn_stat" if points_against is not None else None,
            "point_differential": point_differential_source,
            "points_per_game": "derived_from_espn_points_and_wlt" if points_per_game is not None else None,
            "points_allowed_per_game": "derived_from_espn_points_and_wlt" if points_allowed_per_game is not None else None,
            "home_record": "espn_stat" if home_record else None,
            "away_record": "espn_stat" if away_record else None,
            "division_record": "espn_stat" if division_record else None,
            "conference_record": "espn_stat" if conference_record else None,
            "division_rank": division_rank_source,
'''
    if '"points_per_game": "derived_from_espn_points_and_wlt"' not in text:
        if source_marker not in text:
            raise SystemExit("standings source marker not found")
        text = text.replace(source_marker, source_replacement, 1)

    path.write_text(text, encoding="utf-8")


def patch_next_game() -> None:
    path = Path("custom_components/sports_ticker/next_game.py")
    text = path.read_text(encoding="utf-8")

    const_marker = '''from .const import (
    CONF_FAVORITE_TEAMS,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    TEAM_OPTIONS,
)
'''
    helper_import = '''from .football_schedule import normalize_recent_games, recent_form

'''
    if "from .football_schedule import" not in text:
        if const_marker not in text:
            raise SystemExit("next game const import marker not found")
        text = text.replace(const_marker, const_marker + "\n" + helper_import, 1)

    no_favorite_marker = '''            return {
                "favorite_team": None,
                "event": None,
                "_sports_ticker_meta": {
'''
    no_favorite_replacement = '''            return {
                "favorite_team": None,
                "event": None,
                "recent_games": [],
                "recent_form": None,
                "_sports_ticker_meta": {
'''
    if '"recent_games": []' not in text.split('url = TEAM_SCHEDULE_URL', 1)[0]:
        if no_favorite_marker not in text:
            raise SystemExit("next game no-favorite marker not found")
        text = text.replace(no_favorite_marker, no_favorite_replacement, 1)

    event_marker = '''            event = self._find_next_event(events, favorite)
            data = {
                "favorite_team": favorite,
                "event": event,
                "_sports_ticker_meta": {
'''
    event_replacement = '''            event = self._find_next_event(events, favorite)
            recent_games = normalize_recent_games(events, favorite, limit=5)
            data = {
                "favorite_team": favorite,
                "event": event,
                "recent_games": recent_games,
                "recent_form": recent_form(recent_games),
                "_sports_ticker_meta": {
'''
    if "recent_games = normalize_recent_games" not in text:
        if event_marker not in text:
            raise SystemExit("next game data marker not found")
        text = text.replace(event_marker, event_replacement, 1)

    failure_marker = '''            return {
                "favorite_team": favorite,
                "event": None,
                "_sports_ticker_meta": {
'''
    failure_replacement = '''            return {
                "favorite_team": favorite,
                "event": None,
                "recent_games": [],
                "recent_form": None,
                "_sports_ticker_meta": {
'''
    # Replace only the error-path occurrence remaining after the no-favorite patch.
    if failure_marker in text:
        text = text.replace(failure_marker, failure_replacement, 1)

    attrs_marker = '''            "has_upcoming_game": isinstance(event, dict),
            "stale": bool(meta.get("stale", False)),
'''
    attrs_replacement = '''            "has_upcoming_game": isinstance(event, dict),
            "recent_games": data.get("recent_games", []),
            "last_five": data.get("recent_games", []),
            "recent_form": data.get("recent_form"),
            "stale": bool(meta.get("stale", False)),
'''
    if '"last_five": data.get("recent_games", [])' not in text:
        if attrs_marker not in text:
            raise SystemExit("next game attrs marker not found")
        text = text.replace(attrs_marker, attrs_replacement, 1)

    path.write_text(text, encoding="utf-8")


patch_standings()
patch_next_game()
