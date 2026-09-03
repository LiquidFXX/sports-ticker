# Multi-Sport Data Sources

Sports Ticker exposes shared, normalized Home Assistant data sources for supported team sports. These sensors are intended to be stable building blocks for Lovelace cards, templates, and automations.

The integration preserves the existing specialized NFL and MLB standings sensors while using a shared normalization layer for the other supported leagues.

## Standings

When the corresponding league is enabled, Sports Ticker can expose:

```text
sensor.espn_nfl_standings_raw
sensor.espn_mlb_standings_raw
sensor.espn_nba_standings_raw
sensor.espn_wnba_standings_raw
sensor.espn_nhl_standings_raw
sensor.espn_mls_standings_raw
sensor.espn_epl_standings_raw
sensor.espn_laliga_standings_raw
sensor.espn_bundesliga_standings_raw
sensor.espn_seriea_standings_raw
sensor.espn_ligue1_standings_raw
sensor.espn_ucl_standings_raw
```

NFL and MLB keep their dedicated parsers because their postseason-race requirements are richer and already backward-compatible. NBA, WNBA, NHL, and soccer leagues share the generic standings coordinator/parser.

Common top-level attributes include:

```yaml
league: nba
data_type: standings
season: 2026
season_type: 2
season_type_name: Regular Season
favorite_team: ATL
updated_at: "..."

groups: {}
conferences: {}
leagues: {}
divisions: {}
table: []
teams: []
playoff: {}
normalization: {}

stale: false
source: espn
```

Not every league uses every alias. For example, NBA/NHL primarily use `conferences`, soccer exposes `table`, and the normalized flat `teams` list is available for card development across the shared parser.

Common team-row fields include:

```yaml
seed:
position:
team_id:
abbreviation:
display_name:
short_name:
logo:
favorite:
group:
conference:
league_group:
division:
division_rank:
group_rank:
conference_rank:
league_rank:
overall_rank:
wildcard_rank:
division_leader:
wins:
losses:
ties:
draws:
overtime_losses:
games_played:
record:
win_percentage:
points:
points_percentage:
games_back:
home_record:
away_record:
division_record:
conference_record:
last_10:
streak:
form:
runs_for:
runs_against:
goals_for:
goals_against:
points_for:
points_against:
differential:
regulation_wins:
regulation_overtime_wins:
shootout_wins:
shootout_losses:
espn_clincher:
clinched_playoff:
clinched_play_in:
clinched_wildcard:
clinched_division:
clinched_conference:
clinched_best_record:
eliminated:
playoff_position:
wildcard:
play_in:
in_playoffs:
in_the_hunt:
sources: {}
espn_stats: {}
```

Optional ESPN fields remain `null` when unavailable. Sports Ticker does not invent clinch or elimination status. Deterministic helpers such as playoff cut lines are identified in `sources`/`normalization` metadata.

### League-specific playoff helpers

- **NFL:** existing dedicated AFC/NFC seeds, division leaders, wild cards, cut line, hunt, and ESPN clincher handling.
- **MLB:** existing dedicated division/wild-card standings remain authoritative.
- **NBA:** conference positions 1–6 are automatic playoff positions; 7–10 are exposed as play-in positions when rank data is available.
- **WNBA:** top-eight cut-line helpers are exposed from league rank.
- **NHL:** playoff helpers are only derived when ESPN provides usable playoff-seed/wild-card ranking data.
- **Soccer:** table data is normalized, but Sports Ticker does not fabricate qualification/relegation zones when ESPN does not expose them reliably.

## Favorite-team schedules, next game, and form

Team leagues use the same next-game entity pattern:

```text
sensor.espn_<league>_next_game
```

Examples:

```text
sensor.espn_mlb_next_game
sensor.espn_nfl_next_game
sensor.espn_cfb_next_game
sensor.espn_nba_next_game
sensor.espn_wnba_next_game
sensor.espn_nhl_next_game
sensor.espn_mls_next_game
sensor.espn_epl_next_game
sensor.espn_laliga_next_game
sensor.espn_bundesliga_next_game
sensor.espn_seriea_next_game
sensor.espn_ligue1_next_game
sensor.espn_ucl_next_game
```

The existing NFL and CFB entity IDs are unchanged.

The sensor follows the favorite team configured in Sports Ticker and includes the next scheduled event plus reusable schedule/form attributes:

```yaml
favorite_team: ATL
has_upcoming_game: true

upcoming_games:
  - ...
next_five:
  - ...

recent_games:
  - result: W
    opponent: BOS
    score: 5-2
    date: "..."
  - ...
last_five:
  - ...

recent_form: WWLWW
record_last_5: 4-1
record_last_10: 7-3
current_streak: W2
```

Existing next-game attributes such as date, opponent, home/away, venue, broadcasts, team logos, records, rankings, week, and raw event data remain available where ESPN supplies them.

## Postseason / playoffs

For supported postseason-based pro leagues:

```text
sensor.espn_mlb_playoffs
sensor.espn_nfl_playoffs
sensor.espn_nba_playoffs
sensor.espn_wnba_playoffs
sensor.espn_nhl_playoffs
```

These sensors normalize ESPN postseason scoreboard/series metadata into:

```yaml
league: nba
data_type: postseason
season: 2026
updated_at: "..."
has_postseason_data: true

rounds:
  - name: Conference Semifinals
    source: espn_note
    series:
      - key: "..."
        title: Conference Semifinals
        summary: BOS leads 2-1
        completed: false
        total_games: 7
        teams:
          - ...
        games:
          - ...

games:
  - event_id: "..."
    date: "..."
    teams:
      - abbreviation: ATL
        seed: 4
        score: 101
        winner: false
      - abbreviation: BOS
        seed: 1
        score: 108
        winner: true

normalization:
  bracket_links_inferred: false
```

Sports Ticker preserves ESPN series IDs, titles, summaries, and round labels when provided. When ESPN does not expose explicit bracket linkage, the integration does **not** guess which series feeds another series.

## Reliability

Standings and postseason data use separate cached coordinators with conservative refresh intervals. If ESPN temporarily fails, the last successful normalized response is retained when available and the sensor reports:

```yaml
stale: true
source: cache
last_error: "..."
```

This keeps dashboard cards populated during short ESPN outages without presenting cached data as fresh.
