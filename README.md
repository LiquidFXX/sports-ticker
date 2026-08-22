<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏟️ Home Assistant Sports Ticker

> A Home Assistant integration that pulls live sports data from ESPN scoreboards and exposes it as sensors for Lovelace tickers, scoreboards, game cards, highlights, and dashboards.

---

## 📣 What's new in v0.0.20

- 🏈 **Favorite-team College Football next game sensor**
  - Added `sensor.espn_cfb_next_game` when College Football is enabled
  - Uses the College Football favorite selected in Sports Ticker options
  - Reads that team's ESPN schedule and selects the earliest future scheduled game

- 🏈 **Shared NFL + College Football next-game model**
  - Preserves `sensor.espn_nfl_next_game`
  - Standardizes matchup, opponent, home/away, kickoff, venue, broadcast, season/week, logos, records, rankings, and freshness attributes where ESPN provides them
  - Adds College Football context such as neutral-site and conference-game information when available
  - Keeps the last successful next-game result if ESPN temporarily fails

- 📦 **HACS release ZIP support**
  - Releases now publish `sports_ticker.zip`
  - HACS is configured to install from the release asset
  - GitHub release asset downloads provide the download metric HACS can use without adding installation telemetry

- 🗺️ **Season-based sports roadmap**
  - Planned sport releases are targeted ahead of their seasons or major annual competitions
  - Future targets include College Basketball, Tennis, Rugby, Formula 1, AFL, Cricket, MotoGP, IndyCar, and more

---

## 🚧 In development for v0.20.1

- 🏆 **College Football rankings sensor**
  - Adds `sensor.espn_cfb_rankings` whenever College Football is enabled
  - Exposes all polls ESPN currently provides, including AP Top 25, Coaches Poll, and College Football Playoff rankings when available
  - Normalizes current rank, previous rank, trend, record, first-place votes, points, team colors, logos, and dropped-out teams
  - Provides card-friendly aliases: `ap_top_25`, `coaches_poll`, and `cfp`
  - Preserves the last successful ranking data if ESPN is temporarily unavailable

---

## 🏈 NFL card showcase

The NFL examples are being rebuilt around cards that are useful day-to-day. The current set includes a favorite-team next-game card, a multi-sport scrolling ticker, and a playable ESPN highlights card.

### Favorite Team Next Game

Automatically follows the NFL favorite configured in Sports Ticker and shows the next matchup, kickoff, venue, broadcast, week, and home/away status.

<a href="examples/NFL.md#1-favorite-team-next-game">
  <img src="examples/images/NFL/nfl_next_game_card.svg" alt="NFL Favorite Team Next Game card" width="360">
</a>

### Scrolling Sports Ticker

A glass-style ticker that can show NFL by itself or combine multiple enabled sports in one continuous scrolling display.

<a href="examples/NFL.md#2-scrolling-sports-ticker">
  <img src="examples/images/NFL/nfl_multi_sport_ticker.gif" alt="NFL multi-sport scrolling ticker" width="100%">
</a>

### NFL Game Highlights

Finds playable ESPN highlights from the NFL scoreboard data and combines the video with the final score and recap information.

<a href="examples/NFL.md#3-nfl-game-highlights">
  <img src="https://github.com/user-attachments/assets/44bc4b4e-5866-490e-a4df-73c7ade104b9" alt="NFL Game Highlights card" width="420">
</a>

➡️ **[Open the full NFL examples with copy/paste YAML](examples/NFL.md)**

---

## ✨ What this integration does

- Creates live ESPN scoreboard sensors for selected leagues
- Exposes raw ESPN scoreboard data for Lovelace cards
- Lets you select a favorite team for each league
- Creates favorite-team NFL and College Football next-game sensors when those leagues are enabled
- Creates a normalized College Football rankings sensor when CFB is enabled
- Exposes ticker speed and theme settings as sensor attributes
- Keeps the last good scoreboard data if ESPN is temporarily unavailable
- Adds cache and freshness attributes for dashboard status indicators
- Works well with:
  - `custom:button-card`
  - `card-mod`
  - Mushroom cards
  - Home Assistant sections dashboards

---

## 📌 Quick links

| Category | Description | Link |
| :--- | :--- | :---: |
| Installation | HACS and manual installation | [Jump](#-installation) |
| Configuration | Leagues, favorites, ticker speed, and theme | [Jump](#️-configuration) |
| Sensors | Entity names and available attributes | [Jump](#-entities--sensors) |
| NFL showcase | Preview the newest NFL dashboard cards | [Jump](#-nfl-card-showcase) |
| Examples | Ready-to-use Lovelace cards | [Jump](#-lovelace-examples) |
| Planned sports | Season-based expansion roadmap | [Jump](#️-planned-sports-roadmap) |
| Troubleshooting | Common setup and dashboard issues | [Jump](#️-troubleshooting) |

---

## ✅ Supported leagues

### Major U.S. leagues

- MLB
- NFL
- College Football
- NBA
- WNBA
- NHL

### Golf and racing

- PGA Tour
- NASCAR

### Soccer

- MLS
- Premier League
- LaLiga
- Bundesliga
- Serie A
- Ligue 1
- Champions League

---

## 🗺️ Planned sports roadmap

New sports are targeted for releases **before their seasons or major annual competitions begin**, leaving time for testing, documentation, and dashboard examples. Version targets may move if ESPN data is not reliable enough for production support or if an official season calendar changes.

### Version numbering going forward

Starting with the next update, Sports Ticker will use:

```text
v0.<feature line>.<sub-update>
```

Examples:

- `v0.20.1` — first follow-up update to the Football release line
- `v0.20.2` — another Football fix/card/docs update
- `v0.21.0` — next feature release line
- `v0.21.1` — follow-up update to v0.21

The currently published release remains **v0.0.20** so the existing GitHub/HACS history stays accurate. The **next release will begin the new structure at v0.20.1**.

| Version | Target release | Sport / focus | Seasonal goal |
| :--- | :--- | :--- | :--- |
| **v0.20.1** | Aug–Sep 2026 | 🏈 NFL + College Football | Football sub-update: cards, examples, CFB rankings, CFB/NFL refinements, and season-ready fixes |
| **v0.21.0** | Oct 2026 | 🏀 College Basketball | Land before the November college basketball season |
| **v0.22.0** | Dec 2026 | 🎾 Tennis | Land before the January 2027 Australian Open; begin with ATP/WTA and major tournaments |
| **v0.23.0** | Jan 2027 | 🏉 Rugby Union | Land before the 2027 Six Nations begins in early February |
| **v0.24.0** | Early Feb 2027 | 🏉 Rugby League | Land before the 2027 NRL season begins in late February |
| **v0.25.0** | Feb 2027* | 🏎️ Formula 1 | Land before the 2027 F1 season; establish the motorsport event model |
| **v0.26.0** | Feb–Mar 2027* | 🦘 Australian Rules Football | Land before the 2027 AFL season |
| **v0.27.0** | Mar 2027 | 🏏 Cricket | Target the major spring T20 / IPL window while building a year-round cricket model |
| **v0.28.0** | Pre-season target | 🏍️ MotoGP | Reuse the motorsport architecture established for Formula 1 |
| **v0.29.0** | Pre-season target | 🏎️ IndyCar | Add before a future IndyCar season begins |
| **v0.30.0** | Jan 2028 | ⚾🥎 College Baseball + Softball | Land before the NCAA spring schedules begin |
| **v0.31.0** | Pre-season target | 🏒 College Hockey | Land before an NCAA hockey season begins |

\* Target month is provisional until the relevant official season calendar is published.

### Future event-driven candidates

These sports do not follow a single traditional season, so they can fit between seasonal releases once the common event model is ready:

- 🥋 MMA / UFC
- 🥊 Boxing

### Additional seasonal candidates

- 🏐 Volleyball
- 🤾 Handball
- 🥍 Lacrosse
- 🏑 Field Hockey
- 🏒 International and non-NHL hockey
- 🏈 Canadian Football
- 🏎️ Endurance racing and additional motorsport series

A planned sport becomes an official release target only after its ESPN scoreboard, schedule, competitor, status, and event data are verified as reliable enough for Home Assistant use.

---

## 📦 Installation

### Option A: HACS

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add this repository.
4. Choose **Integration** as the category.
5. Install **Sports Ticker**.
6. Restart Home Assistant.

### Option B: Manual installation

Copy the integration folder to:

```text
config/custom_components/sports_ticker/
```

Then restart Home Assistant and add the integration from:

```text
Settings → Devices & services → Add integration → Sports Ticker
```

---

## ⚙️ Configuration

Open:

```text
Settings → Devices & services → Sports Ticker → Configure
```

### Step 1: Sports, leagues, and display options

Choose the leagues you want to track, then configure:

- **Poll interval**: how often Sports Ticker refreshes ESPN data
- **Ticker speed**: the animation duration in seconds
  - Lower numbers scroll faster
  - Higher numbers scroll slower
  - Supported range: **4 to 60 seconds**
- **Ticker theme**: light or dark

### Step 2: Favorite teams

Choose a favorite team for each selected league. Dashboard cards can use this information to:

- Sort favorite games first
- Highlight favorite teams
- Build team-focused cards

The selected NFL and College Football favorites also drive their next-game sensors.

---

## 🧠 Entities and sensors

Raw scoreboard sensors follow this pattern:

```text
sensor.espn_<league>_scoreboard_raw
```

Examples:

```text
sensor.espn_mlb_scoreboard_raw
sensor.espn_nfl_scoreboard_raw
sensor.espn_cfb_scoreboard_raw
sensor.espn_nba_scoreboard_raw
sensor.espn_wnba_scoreboard_raw
sensor.espn_nhl_scoreboard_raw
sensor.espn_mls_scoreboard_raw
sensor.espn_epl_scoreboard_raw
sensor.espn_laliga_scoreboard_raw
sensor.espn_bundesliga_scoreboard_raw
sensor.espn_seriea_scoreboard_raw
sensor.espn_ligue1_scoreboard_raw
sensor.espn_ucl_scoreboard_raw
```

### Football favorite next game

When NFL or College Football is enabled, Sports Ticker creates the corresponding favorite-team next-game sensor:

```text
sensor.espn_nfl_next_game
sensor.espn_cfb_next_game
```

Each sensor follows the favorite selected for that league. Its state is the next matchup, for example:

```text
KC @ BUF
```

Useful attributes include:

```yaml
league: nfl
favorite_team: KC
favorite_team_name: Kansas City Chiefs
has_upcoming_game: true
date: "2026-09-01T00:00:00Z"
home_team: BUF
away_team: KC
home_away: away
opponent: BUF
opponent_name: Buffalo Bills
venue: Highmark Stadium
broadcasts:
  - CBS
week: 1
stale: false
source: espn
```

College Football exposes the same common model and also includes additional context such as rankings, records, neutral-site status, and conference-game information when ESPN provides it.

If no favorite is configured, the sensor state is `No favorite team`. If ESPN returns no future scheduled event for that favorite, the state is `No upcoming game`.

### College Football rankings

When College Football is enabled, Sports Ticker also creates:

```text
sensor.espn_cfb_rankings
```

The state identifies the preferred current poll and the number of ranked teams, for example:

```text
AP Top 25 - 25 teams
```

The sensor exposes all polls currently returned by ESPN. Card-friendly aliases make the major polls easy to use directly:

```yaml
season: 2026
week: 1
primary_poll: ap_top_25
ap_top_25:
  - rank: 1
    previous_rank: 2
    trend: 1
    abbreviation: TEX
    display_name: Texas Longhorns
    record: 0-0
    first_place_votes: 25
    points: 1525
    logo: https://...
coaches_poll:
  - ...
cfp:
  - ...
polls:
  ap_top_25:
    name: AP Top 25
    headline: ...
    ranks:
      - ...
    dropped_out:
      - ...
stale: false
source: espn
```

The `cfp` list can be empty early in the season before the College Football Playoff committee publishes its first rankings. `ap_top_25` and `coaches_poll` are populated whenever ESPN provides those polls.

### Main scoreboard attributes

```yaml
events:
  - ...
leagues:
day:
season:
next:
```

### Favorite team attributes

```yaml
favorite_team: ATL
favorite_team_name: Atlanta Braves
has_favorite_team: true
```

### Ticker helper attributes

```yaml
ticker_speed: 12
ticker_theme: light
```

`ticker_speed` is the configured animation duration in seconds. A lower value creates a faster scroll; a higher value creates a slower scroll.

### Cache and freshness attributes

```yaml
stale: false
source: espn
last_successful_update: "2026-05-05T23:00:00+00:00"
last_attempted_update: "2026-05-05T23:00:00+00:00"
last_error: null
```

When ESPN is unavailable, Sports Ticker keeps the last valid data and marks it as cached:

```yaml
stale: true
source: cache
last_error: "Unexpected status 503"
```

---

## 🧩 Lovelace examples

All example cards are stored in the top-level [`examples`](examples/) folder.

| Example | Description |
| :--- | :--- |
| [`NFL.md`](examples/NFL.md) | Favorite-team next game, multi-sport scrolling ticker, and playable NFL game highlights |
| [`college_football_ticker_card.yaml`](examples/college_football_ticker_card.yaml) | Scrolling College Football ticker that uses the configured favorite team and ticker speed |
| [`multi_league_ticker_card.yaml`](examples/multi_league_ticker_card.yaml) | Reusable ticker card template for supported leagues |
| [`MLB.md`](examples/MLB.md) | MLB ticker, schedule, gamecast, standings, and stats layouts |
| [`NBA.md`](examples/NBA.md) | NBA schedule, ticker, and dashboard card examples |

The College Football ticker reads integration options directly from the scoreboard sensor:

```javascript
const speed = Number(
  states['sensor.espn_cfb_scoreboard_raw']?.attributes?.ticker_speed
);

const favorite =
  states['sensor.espn_cfb_scoreboard_raw']?.attributes?.favorite_team;
```

This means changing Sports Ticker options updates the card after the integration reloads. No separate `input_number` helper is required.

---

## 🛠️ Troubleshooting

### The new options are not visible

Update the integration, restart Home Assistant, then reopen:

```text
Settings → Devices & services → Sports Ticker → Configure
```

### The ticker speed does not change

Confirm the Lovelace card reads:

```javascript
entity.attributes.ticker_speed
```

or the equivalent scoreboard entity state attribute. A hard-coded CSS value such as `36s` will ignore the integration setting.

### My sensor says cached

ESPN was unavailable, timed out, or returned invalid data. Sports Ticker intentionally keeps the last valid scoreboard instead of blanking the card.

### My favorite team does not show

Reopen the integration options and select a favorite team for that league. Then check the scoreboard sensor attributes for:

```yaml
favorite_team:
favorite_team_name:
has_favorite_team:
```

### My dashboard card is blank

Verify that:

- The correct raw scoreboard sensor is used
- The entity has an `events` attribute
- The selected league is enabled in the integration options
- Required custom cards such as `button-card` and `card-mod` are installed

---

## 📌 Version

Current published version: **v0.0.20**

Next sub-update: **v0.20.1**

Going forward, feature lines use `v0.<feature>.0` and follow-up fixes/improvements increment the final number, for example `v0.20.1`, `v0.20.2`, then `v0.21.0`.

---

## ❤️ Support

If this project helps you build better Home Assistant dashboards, support is appreciated:

[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
