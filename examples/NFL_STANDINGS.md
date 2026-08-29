# NFL Standings & Playoff Data

Sports Ticker exposes normalized league-wide NFL standings through:

```text
sensor.espn_nfl_standings_raw
```

This sensor uses ESPN's NFL standings feed and is separate from the weekly scoreboard sensor. It is intended to provide a stable data source for future standings and playoff-picture Lovelace cards.

## Top-level attributes

```yaml
league: nfl
data_type: standings
season: 2026
season_type: 2
season_type_name: Regular Season
week: 16
favorite_team: ATL
updated_at: "2026-12-20T23:15:00+00:00"

conferences:
  AFC:
    - ...
  NFC:
    - ...

divisions:
  AFC East:
    conference: AFC
    leader: BUF
    teams:
      - BUF
      - MIA
      - NE
      - NYJ

teams:
  - ...

playoff:
  seeds_per_conference: 7
  division_leader_seeds: 4
  cut_line_seed: 7
  source: nfl_rule

stale: false
source: espn
```

`week` is reused from the existing ESPN NFL scoreboard data when the standings response does not provide it directly.

## Normalized team row

Each entry under `conferences.AFC`, `conferences.NFC`, and the flat `teams` list uses the same shape:

```yaml
seed: 6
team_id: "1"
abbreviation: ATL
display_name: Atlanta Falcons
short_name: Falcons
logo: https://...
wins: 10
losses: 5
ties: 0
record: 10-5
win_percentage: 0.667
conference: NFC
division: NFC South
division_rank: 1
conference_rank: 6
division_leader: true
wildcard: true
playoff_position: 6
in_playoffs: true
in_the_hunt: false
streak: W3
games_back: 2.0
games_back_display: "2"
espn_clincher: y
clinched_playoff: true
clinched_wildcard: true
clinched_division: false
clinched_conference: null
clinched_first_seed: false
eliminated: false
favorite: true

derived:
  division_leader: true
  wildcard: true
  in_playoffs: true
  in_the_hunt: false

sources:
  seed: espn_stat
  division_rank: espn_division_order
  conference_rank: espn_playoff_seed
  division_leader: derived_from_division_rank
  wildcard: derived_from_regular_season_seed
  in_playoffs: derived_from_regular_season_seed
  in_the_hunt: derived_from_seed_and_elimination
  clinched_playoff: espn_clincher
  clinched_division: espn_clincher
  clinched_conference: null
  eliminated: espn_clincher
```

The simple top-level helper fields are intentionally duplicated inside `derived` / `sources` so dashboard authors can use convenient values while still knowing which values came directly from ESPN and which were normalized or derived.

## Playoff and clinch handling

For regular-season standings:

- ESPN `playoffSeed` is normalized to `seed` and `playoff_position`.
- Seeds 1-7 are exposed through the `in_playoffs` helper.
- Seeds 5-7 are exposed through the `wildcard` helper.
- `division_leader` is derived from ESPN's division rank or the ordered ESPN division standings.
- `in_the_hunt` is only set when a team is below the cut line and ESPN provides enough elimination information to determine that it has not been eliminated. Otherwise it remains `null`.
- ESPN's original clincher value is preserved as `espn_clincher`.
- `clinched_conference` is **not** inferred from seed or home-field advantage. It remains `null` unless ESPN supplies a direct conference-clinch field.

Known NFL clincher symbols are normalized when ESPN supplies them:

| ESPN/NFL code | Normalized meaning |
| --- | --- |
| `x` | Clinched playoff berth |
| `y` | Clinched wild card |
| `z` | Clinched division |
| `*` | Clinched division and home-field / first seed |
| `e` | Eliminated, when ESPN supplies the code |

## Reading the attributes from Lovelace

No standings card is included yet. A future card can read the normalized data directly:

```javascript
const st = states['sensor.espn_nfl_standings_raw'];
const afc = st?.attributes?.conferences?.AFC || [];
const nfc = st?.attributes?.conferences?.NFC || [];
const favorite = st?.attributes?.favorite_team;
const season = st?.attributes?.season;
const week = st?.attributes?.week;
```

Or in Home Assistant templates:

```jinja2
{{ state_attr('sensor.espn_nfl_standings_raw', 'conferences')['AFC'] }}
{{ state_attr('sensor.espn_nfl_standings_raw', 'conferences')['NFC'] }}
{{ state_attr('sensor.espn_nfl_standings_raw', 'favorite_team') }}
{{ state_attr('sensor.espn_nfl_standings_raw', 'season') }}
{{ state_attr('sensor.espn_nfl_standings_raw', 'week') }}
```

## Refresh and cache behavior

NFL standings use a dedicated coordinator with a minimum polling interval of 15 minutes. This keeps standings requests separate from faster live-score polling.

When ESPN fails or returns malformed data, Sports Ticker keeps the most recent successful normalized standings in Home Assistant storage and marks the sensor as cached:

```yaml
stale: true
source: cache
last_error: "..."
```

The sensor remains additive and does not replace or rename any existing NFL entities.
