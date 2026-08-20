<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏟️ Home Assistant Sports Ticker

> A Home Assistant integration that pulls live sports data from ESPN scoreboards and exposes it as sensors for Lovelace tickers, scoreboards, game cards, and dashboards.

---

## 📣 What's new in v0.0.19

- 🏈 **Favorite-team NFL next game sensor**
  - Added `sensor.espn_nfl_next_game` when NFL is enabled
  - Uses the NFL favorite selected in Sports Ticker options
  - Reads that team's ESPN schedule and selects the earliest future scheduled game
  - Avoids depending only on the current-week league scoreboard

- 📅 **Automation-friendly next-game details**
  - The sensor state is a compact matchup such as `KC @ BUF`
  - Attributes include kickoff date/time, opponent, home/away, venue, broadcast networks, week/season, team logos, and the raw ESPN event
  - Explicit states are returned when no NFL favorite is selected or no future game is available

- 🛡️ **Resilient schedule updates**
  - Keeps the last successful next-game result in memory if ESPN temporarily fails
  - Exposes freshness and error metadata for dashboards and automations

---

## 🚧 Next: v0.0.20 — Football Season

The next release is focused on getting Sports Ticker ready for football season.

Planned work:

- 🏈 Add a favorite-team College Football next-game sensor
- 🏈 Standardize NFL and College Football next-game attributes
- 📅 Improve preseason, regular-season, postseason, bye-week, neutral-site, and schedule-change handling
- 🏆 Improve College Football rankings, conference, bowl, and playoff context where ESPN provides it
- 🧩 Update NFL and College Football dashboard examples to use native Sports Ticker sensors where possible
- 📦 Add HACS-compatible release ZIP packaging so GitHub/HACS release downloads can be counted
- ✅ Keep HACS and Hassfest validation in the release workflow

The published integration remains **v0.0.19** until the v0.0.20 work is complete and released.

---

## ✨ What this integration does

- Creates live ESPN scoreboard sensors for selected leagues
- Exposes raw ESPN scoreboard data for Lovelace cards
- Lets you select a favorite team for each league
- Creates a favorite-team NFL next-game sensor when NFL is enabled
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

| Version | Target release | Sport / focus | Seasonal goal |
| :--- | :--- | :--- | :--- |
| **v0.0.20** | Aug–Sep 2026 | 🏈 NFL + College Football | Football-season foundation; improve existing football support before kickoff |
| **v0.0.21** | Oct 2026 | 🏀 College Basketball | Land before the November college basketball season |
| **v0.0.22** | Dec 2026 | 🎾 Tennis | Land before the January 2027 Australian Open; begin with ATP/WTA and major tournaments |
| **v0.0.23** | Jan 2027 | 🏉 Rugby Union | Land before the 2027 Six Nations begins in early February |
| **v0.0.24** | Early Feb 2027 | 🏉 Rugby League | Land before the 2027 NRL season begins in late February |
| **v0.0.25** | Feb 2027* | 🏎️ Formula 1 | Land before the 2027 F1 season; establish the motorsport event model |
| **v0.0.26** | Feb–Mar 2027* | 🦘 Australian Rules Football | Land before the 2027 AFL season |
| **v0.0.27** | Mar 2027 | 🏏 Cricket | Target the major spring T20 / IPL window while building a year-round cricket model |
| **v0.0.28** | Pre-season target | 🏍️ MotoGP | Reuse the motorsport architecture established for Formula 1 |
| **v0.0.29** | Pre-season target | 🏎️ IndyCar | Add before a future IndyCar season begins |
| **v0.0.30** | Jan 2028 | ⚾🥎 College Baseball + Softball | Land before the NCAA spring schedules begin |
| **v0.0.31** | Pre-season target | 🏒 College Hockey | Land before an NCAA hockey season begins |

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

The selected NFL favorite also drives `sensor.espn_nfl_next_game`.

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

### NFL favorite next game

When NFL is enabled, Sports Ticker also creates:

```text
sensor.espn_nfl_next_game
```

The sensor follows the NFL favorite selected in the integration options. Its state is the next matchup, for example:

```text
KC @ BUF
```

Useful attributes include:

```yaml
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

If no NFL favorite is configured, the state is `No favorite team`. If ESPN returns no future scheduled event for that favorite, the state is `No upcoming game`.

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

All example cards are now stored in the top-level [`examples`](examples/) folder.

| Example | Description |
| :--- | :--- |
| [`NFL.md`](examples/NFL.md) | NFL ticker, schedule, gamecast, featured matchup, and next-game entity examples |
| [`college_football_ticker_card.yaml`](examples/college_football_ticker_card.yaml) | Scrolling College Football ticker that uses the configured favorite team and ticker speed |
| [`multi_league_ticker_card.yaml`](examples/multi_league_ticker_card.yaml) | Reusable ticker card template for supported leagues |
| [`mlb_example_cards.md`](examples/mlb_example_cards.md) | MLB ticker, schedule, gamecast, standings, and stats layouts |
| [`nba_example_cards.md`](examples/nba_example_cards.md) | NBA schedule, ticker, and dashboard card examples |

The College Football ticker reads the integration options directly from the scoreboard sensor:

```javascript
const speed = Number(
  states['sensor.espn_cfb_scoreboard_raw']?.attributes?.ticker_speed
);

const favorite =
  states['sensor.espn_cfb_scoreboard_raw']?.attributes?.favorite_team;
```

This means changing the Sports Ticker options updates the card after the integration reloads. No separate `input_number` helper is required.

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

or the equivalent scoreboard entity state attribute. A hard-coded CSS value such as `36s` will ignore the integration setting, because CSS remains unmoved by good intentions.

### My sensor says cached

ESPN was unavailable, timed out, or returned invalid data. Sports Ticker is intentionally keeping the last valid scoreboard instead of blanking the card.

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

Current version: **v0.0.19**

---

## ❤️ Support

If this project helps you build better Home Assistant dashboards, support is appreciated:

[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
