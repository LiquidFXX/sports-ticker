<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏟️ Home Assistant Sports Ticker

> A Home Assistant integration that pulls live sports data from ESPN scoreboards and exposes it as sensors for Lovelace tickers, scoreboards, game cards, and dashboards.

---

## 📣 What's new in v0.0.18.2

- 🎚️ **Improved ticker speed controls**
  - Ticker speed now supports values from **4 to 60 seconds**
  - The options screen now explains that **lower values scroll faster** and **higher values scroll slower**
  - The configured value is exposed through each scoreboard sensor as `ticker_speed`

- 🏈 **College Football ticker example**
  - Added a complete scrolling College Football ticker card
  - Reads `ticker_speed` directly from `sensor.espn_cfb_scoreboard_raw`
  - Reads the configured favorite team from the sensor attributes

- 🗂️ **Reorganized examples**
  - All Lovelace example cards now live in one top-level `examples/` folder
  - Example filenames were standardized and renamed for clarity

- 🧹 **Cleaner configuration flow**
  - Shared setup and options schemas reduce duplicated code
  - Speed values now display in seconds

---

## ✨ What this integration does

- Creates live ESPN scoreboard sensors for selected leagues
- Exposes raw ESPN scoreboard data for Lovelace cards
- Lets you select a favorite team for each league
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

Current version: **v0.0.18.2**

---

## ❤️ Support

If this project helps you build better Home Assistant dashboards, support is appreciated:

[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
