<div align="center">

# 🏟️ Sports Ticker for Home Assistant

### Turn ESPN sports data into live Home Assistant scoreboards, tickers, game cards, rankings, standings, highlights, and team-focused dashboards.

[![Latest Release](https://img.shields.io/github/v/release/LiquidFXX/sports-ticker?label=Latest%20Release)](https://github.com/LiquidFXX/sports-ticker/releases/latest)
[![Total Downloads](https://img.shields.io/github/downloads/LiquidFXX/sports-ticker/total?label=Downloads)](https://github.com/LiquidFXX/sports-ticker/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)](#installation)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/LiquidFXX/sports-ticker)](LICENSE)

**Stable release:** `v0.20.1`  •  **Current prerelease:** `v0.20.3-alpha.5`

</div>

---

## See it in action

Sports Ticker gives Home Assistant the sports data and now includes the beginning of a native dashboard-card system. The existing Lovelace examples remain available for users who want fully custom layouts.

<a href="examples/NFL.md#2-scrolling-sports-ticker">
  <img src="examples/images/NFL/nfl_multi_sport_ticker.gif" alt="Sports Ticker scrolling multi-sport Home Assistant card" width="100%">
</a>

<p align="center">
  <a href="examples/NFL.md#1-favorite-team-next-game">
    <img src="examples/images/NFL/nfl_next_game_card.svg" alt="NFL favorite team next game card" width="31%">
  </a>
  &nbsp;
  <a href="examples/NFL.md">
    <img src="examples/images/NFL/nfl_this_week_card.svg" alt="NFL weekly card example" width="31%">
  </a>
  &nbsp;
  <a href="examples/CFB.md">
    <img src="examples/images/CFB/cfb_rankings_card.webp" alt="College Football rankings card" width="31%">
  </a>
</p>

---

## What Sports Ticker can do

| Feature | What you get |
| :--- | :--- |
| 🏟️ **Live scoreboards** | ESPN scoreboard data for enabled leagues, including events, teams, scores, status, venue, broadcasts, and game metadata where available |
| 🧩 **Built-in dashboard card** | One Sports Ticker card in the Home Assistant picker with selectable pre-made layouts and per-card options |
| 📺 **Built-in ticker preset** | Responsive scrolling scoreboard using the same Sports Ticker raw scoreboard entities |
| ⭐ **Favorite teams** | Select a favorite team per league and expose it directly to cards and automations |
| 📅 **Next-game sensors** | Dedicated NFL and College Football next-game entities that follow your configured favorite team |
| 🏆 **College Football rankings** | AP Top 25, Coaches Poll, CFP rankings, previous rank, trend, records, votes, points, logos, and dropped-out teams |
| 🏈 **NFL standings & playoff picture** | Normalized AFC/NFC standings, divisions, playoff seeds, wild cards, cut-line helpers, clinch data, favorite-team highlighting, and flat team lists |
| 📊 **Player / team leaders** | MLB player leader sensors plus NFL per-team game leaders for passing, rushing, receiving, sacks, and tackles |
| 🎬 **Highlights** | ESPN highlight/video metadata that can power playable game recap cards |
| 💾 **Failure-resistant data** | Last-good caching keeps cards populated when ESPN temporarily times out or returns bad data |

Sports Ticker remains a reusable sports-data layer. Built-in cards are additive; existing sensors, entity IDs, YAML examples, `custom:button-card`, `card-mod`, Mushroom, and custom dashboards remain supported.

---

## Built-in Sports Ticker cards

Starting with `v0.20.3-alpha.5`, Sports Ticker bundles its own Home Assistant dashboard card frontend. The integration serves and loads the card automatically, so users do not need to manually add a Lovelace JavaScript resource.

Add **Sports Ticker** from the Home Assistant card picker, then choose a pre-made layout in the graphical editor.

Current presets:

- **Game — Standard** — full matchup presentation with logos, score/status, records, venue, and broadcast options.
- **Game — Compact** — a denser matchup layout for smaller dashboard areas.
- **Scoreboard — Ticker** — horizontally scrolling league scoreboard with configurable logos, records, game count, scroll duration, and pause-on-hover behavior.

The built-in cards inherit Home Assistant theme variables instead of forcing their own dashboard color theme. More presets will be added to the same Sports Ticker card selector rather than registering a long list of separate card types.

Basic YAML remains available when desired:

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game
```

Ticker example:

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: ticker
```

---

## Supported sports and leagues

| Category | Leagues |
| :--- | :--- |
| ⚾ Baseball | MLB |
| 🏈 Football | NFL, College Football |
| 🏀 Basketball | NBA, WNBA |
| 🏒 Hockey | NHL |
| ⚽ Soccer | MLS, Premier League, LaLiga, Bundesliga, Serie A, Ligue 1, UEFA Champions League |
| ⛳ Golf | PGA Tour |
| 🏁 Racing | NASCAR |

More sports are planned around their seasonal calendars so support can land before each season or major competition begins.

---

## Core entities

### League scoreboards

Each selected league gets a raw scoreboard sensor:

```text
sensor.espn_<league>_scoreboard_raw
```

Examples:

```text
sensor.espn_nfl_scoreboard_raw
sensor.espn_cfb_scoreboard_raw
sensor.espn_mlb_scoreboard_raw
sensor.espn_nba_scoreboard_raw
sensor.espn_nhl_scoreboard_raw
sensor.espn_epl_scoreboard_raw
```

Typical attributes include `events`, season/day metadata, favorite-team information, ticker settings, and data-freshness metadata.

### Favorite-team next game

When NFL or College Football is enabled:

```text
sensor.espn_nfl_next_game
sensor.espn_cfb_next_game
```

These sensors automatically follow the favorite team selected in Sports Ticker settings.

### NFL standings and playoff picture

When NFL is enabled:

```text
sensor.espn_nfl_standings_raw
```

This sensor uses ESPN's standings hierarchy and exposes normalized conference/division standings, playoff seeds, wild-card helpers, cut-line data, favorite-team highlighting, and clinch information where ESPN provides it.

See **[NFL Standings & Playoff Picture example](examples/NFL.md#7-standings--playoff-picture)**.

### College Football rankings

```text
sensor.espn_cfb_rankings
```

Card-friendly ranking groups include AP Top 25, Coaches Poll, and CFP rankings when ESPN publishes them.

### MLB player leaders

```text
sensor.espn_mlb_player_leaders_raw
```

Includes normalized leader groups such as home runs, RBI, hits, stolen bases, wins, ERA, strikeouts, and saves when ESPN provides them.

---

## Installation

### HACS

Sports Ticker is installed as a **custom HACS integration**.

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/LiquidFXX/sports-ticker`.
4. Select **Integration** as the category.
5. Install **Sports Ticker**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration → Sports Ticker**.

Release builds include a `sports_ticker.zip` asset for HACS installation.

### Manual installation

Copy `custom_components/sports_ticker/` to `config/custom_components/sports_ticker/`, restart Home Assistant, then add **Sports Ticker** from **Settings → Devices & services**.

---

## Configuration

Open:

```text
Settings → Devices & services → Sports Ticker → Configure
```

Choose the leagues you want, then configure favorite teams, poll interval, ticker speed, and other available league settings.

---

## Lovelace examples

The `examples/` folder contains complete dashboard examples in addition to the new built-in card.

| Sport | Examples |
| :--- | :--- |
| 🏈 NFL | [Next game, scrolling ticker, highlights, leaders, standings, playoff picture, and more](examples/NFL.md) |
| 🏈 College Football | [Rankings and College Football cards](examples/CFB.md) |
| ⚾ MLB | [Ticker, schedule, standings-style layouts, stats, and game cards](examples/MLB.md) |
| 🏀 NBA | [Schedule, ticker, and dashboard cards](examples/NBA.md) |
| 🌐 Multi-sport | [`multi_league_ticker_card.yaml`](examples/multi_league_ticker_card.yaml) |

Community frontend cards remain optional and are only required by examples that reference them.

---

## Reliability and caching

ESPN endpoints occasionally timeout, return incomplete data, or temporarily fail. Sports Ticker preserves the last known good result whenever possible instead of blanking dashboards.

Fresh data reports `stale: false`; cached fallback data reports `stale: true` with source/error metadata so cards and automations can react appropriately.

---

## Current development

The stable release is **v0.20.1**. The current prerelease is **v0.20.3-alpha.5**.

This prerelease line includes normalized NFL standings/playoff-picture data, College Football rankings work, and the first bundled Sports Ticker dashboard-card framework. The card framework is intentionally additive and keeps existing sensors and YAML dashboards backward-compatible.

### Planned soccer expansion

- 🇳🇱 **Dutch Eredivisie** (`NED.1`) — planned for an upcoming soccer-focused feature line, beginning with scoreboard/events, favorite-team support, and ticker/card compatibility.

Future feature lines are planned around seasonal timing, with additional soccer competitions, College Basketball, Tennis, Rugby, Formula 1, AFL, Cricket, MotoGP, IndyCar, college baseball/softball, and other sports under consideration.

---

## Troubleshooting

### A sensor is missing

Confirm that its league is enabled under **Sports Ticker → Configure**, then reload or restart Home Assistant after an integration update.

### A built-in card is missing

Confirm Sports Ticker is updated to a prerelease that contains built-in cards, restart Home Assistant, and hard-refresh/reload the browser frontend after the integration update.

### A card is blank

Check that the selected entity exists and exposes the data expected by the selected preset. Raw scoreboard presets require an entity with an `events` attribute.

### The sensor says `Cached`

Sports Ticker could not retrieve a valid fresh response and is intentionally preserving the last good data instead of clearing the sensor.

---

## Project goals

- **Useful Home Assistant entities first** — not just raw API dumps.
- **Backward compatibility** — new sports, sensors, and cards should be additive whenever possible.
- **No fabricated sports data** — if ESPN does not provide something reliably, it should remain unavailable rather than be guessed.
- **Dashboard-friendly normalization** — expose predictable data that is practical to use in Lovelace.
- **Theme-friendly cards** — built-in cards should follow Home Assistant themes by default.
- **Graceful failures** — preserve last-good data whenever possible.

---

## Support

If Sports Ticker helps build your Home Assistant sports dashboard, starring the repository helps other users find it.

Issues, feature requests, card ideas, and tested ESPN data improvements are welcome through the repository issue tracker.

---

<div align="center">

**Built for Home Assistant dashboards that should feel like a real sports screen.**

</div>
