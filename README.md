<div align="center">

# 🏟️ Sports Ticker for Home Assistant

### Turn ESPN sports data into live Home Assistant scoreboards, tickers, game cards, rankings, standings, highlights, and team-focused dashboards.

[![Latest Release](https://img.shields.io/github/v/release/LiquidFXX/sports-ticker?label=Latest%20Release)](https://github.com/LiquidFXX/sports-ticker/releases/latest)
[![Total Downloads](https://img.shields.io/github/downloads/LiquidFXX/sports-ticker/total?label=Downloads)](https://github.com/LiquidFXX/sports-ticker/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)](#installation)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/LiquidFXX/sports-ticker)](LICENSE)

**Stable release:** `v0.20.4`

</div>

---

## See it in action

Sports Ticker gives Home Assistant a reusable ESPN-powered sports data layer plus native dashboard cards for live games, highlights, and scrolling scoreboards. The existing Lovelace examples remain available for users who want fully custom layouts.

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
| 🧩 **Built-in Game card** | Standard and compact matchup layouts using Sports Ticker scoreboard entities |
| 🎬 **Built-in Game Highlights card** | Playable ESPN game highlights with favorite-team-only and prefer-favorite selection options |
| 📺 **Built-in Multi-Sport Ticker** | Responsive scrolling scoreboard across supported leagues with configurable speed, game count, logos, and pause behavior |
| ⭐ **Favorite teams** | Select a favorite team per league and expose it directly to cards and automations |
| 📅 **Next-game sensors** | Dedicated NFL and College Football next-game entities that follow your configured favorite team |
| 🏆 **College Football rankings** | AP Top 25, Coaches Poll, CFP rankings, previous rank, trend, records, votes, points, logos, and dropped-out teams |
| 🏈 **NFL standings & playoff picture** | Normalized AFC/NFC standings, divisions, playoff seeds, wild cards, cut-line helpers, clinch data, favorite-team highlighting, and flat team lists |
| 📊 **Player / team leaders** | MLB player leader sensors plus NFL per-team game leaders for passing, rushing, receiving, sacks, and tackles |
| 💾 **Failure-resistant data** | Last-good caching keeps cards populated when ESPN temporarily times out or returns bad data |

Sports Ticker remains a reusable sports-data layer. Built-in cards are additive; existing sensors, entity IDs, YAML examples, `custom:button-card`, `card-mod`, Mushroom, and custom dashboards remain supported.

---

## Built-in Sports Ticker cards

Sports Ticker bundles its own Home Assistant dashboard frontend. The integration serves and loads the card JavaScript automatically, so users do not need to manually add Lovelace resources.

### Game

Use the main Sports Ticker card for a single matchup. The visual editor includes **Standard** and **Compact** layouts with options for league label, team logos, records, venue, and broadcast information.

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game
```

### Game Highlights

The Highlights card reads playable ESPN video metadata directly from the selected raw scoreboard sensor.

It supports:

- **Favorite teams only** — never falls back to another team's highlight.
- **Prefer favorite team** — chooses a favorite-team highlight first when one is available, then falls back to another playable game.
- Optional recap text.
- Optional ESPN link.
- Large centered play control for touch-friendly dashboards.

The favorite team comes from the selected league's Sports Ticker integration settings; it does not need to be configured again on the card.

```yaml
type: custom:sports-ticker-highlights-card
entity: sensor.espn_nfl_scoreboard_raw
favorite_only: true
prefer_favorite: true
show_recap: true
show_espn_link: true
```

### Multi-Sport Ticker

The scrolling ticker can combine multiple supported leagues in one responsive scoreboard and includes per-card options for ticker speed, maximum games, logos, records, and pause-on-hover behavior.

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: ticker
sports:
  - nfl
  - cfb
  - mlb
```

Built-in cards inherit Home Assistant theme variables instead of forcing their own dashboard color theme.

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

The `examples/` folder contains complete dashboard examples in addition to the built-in cards.

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

The current stable release is **v0.20.4**.

`v0.20.4` promotes the tested alpha.10 code to stable and includes the built-in Game, Game Highlights, and Multi-Sport Ticker experiences while preserving the existing Sports Ticker entity model and YAML dashboards.

### Planned soccer expansion

- 🇳🇱 **Dutch Eredivisie** (`NED.1`) — planned for an upcoming soccer-focused feature line, beginning with scoreboard/events, favorite-team support, and ticker/card compatibility.

Future feature lines are planned around seasonal timing, with additional soccer competitions, College Basketball, Tennis, Rugby, Formula 1, AFL, Cricket, MotoGP, IndyCar, college baseball/softball, and other sports under consideration.

---

## Troubleshooting

### A sensor is missing

Confirm that its league is enabled under **Sports Ticker → Configure**, then reload or restart Home Assistant after an integration update.

### A built-in card is missing

Confirm Sports Ticker is updated to `v0.20.4` or newer, restart Home Assistant, and reload the Home Assistant frontend after the integration update.

### A card is blank

Check that the selected entity exists and exposes the data expected by the selected card. Raw scoreboard cards require an entity with an `events` attribute.

### A Highlights card has no playable video

ESPN does not publish a playable highlight for every event. With **Favorite teams only** enabled, the card intentionally stays on the favorite team and displays an empty state instead of falling back to another game.

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
