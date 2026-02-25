## What this creates

For each selected league (mlb, nfl, nba, etc.) it can create:

### Raw sensor
- `sensor.espn_mlb_scoreboard_raw`
Attributes: `events`, `leagues`, `day`, `season`

### Next/Ticker sensor
- `sensor.mlb_next`
State: `shortName` (ex: `ATL @ BAL`)  
Attributes: `next` (full event block), `events` (list), `fetched_at`
