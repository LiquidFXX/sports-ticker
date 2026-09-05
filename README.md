<div align="center">

# 🏟️ Sports Ticker for Home Assistant

### Turn ESPN sports data into live Home Assistant scoreboards, tickers, game cards, playable highlights, rankings, standings, and team-focused dashboards.

[![Latest Release](https://img.shields.io/github/v/release/LiquidFXX/sports-ticker?label=Latest%20Release)](https://github.com/LiquidFXX/sports-ticker/releases/latest)
[![Total Downloads](https://img.shields.io/github/downloads/LiquidFXX/sports-ticker/total?label=Downloads)](https://github.com/LiquidFXX/sports-ticker/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)](#installation)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/LiquidFXX/sports-ticker)](LICENSE)

**Stable release:** `v0.20.3`  •  **Current prerelease:** `v0.20.4-alpha.2`

</div>

---

## See it in action

Sports Ticker gives Home Assistant a reusable ESPN-backed sports data layer plus native dashboard cards that are loaded automatically by the integration. Existing Lovelace examples remain available for users who want larger custom layouts.

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
| 🧩 **Built-in Game card** | Standard and Compact matchup layouts with automatic favorite-team-aware game selection |
| 🎬 **Built-in Game Highlights card** | Playable ESPN highlights with large play control, score, recap, ESPN link, and strict favorite-team-only filtering |
| 📺 **Built-in Multi-Sport Ticker** | Responsive scrolling scoreboard across one or more enabled Sports Ticker leagues |
| ⭐ **Favorite teams** | Select a favorite team per league and expose it directly to cards and automations |
| 📅 **Next-game sensors** | Dedicated NFL and College Football next-game entities that follow your configured favorite team |
| 🏆 **College Football rankings** | AP Top 25, Coaches Poll, CFP rankings, previous rank, trend, records, votes, points, logos, and dropped-out teams |
| 🏈 **NFL standings & playoff picture** | Normalized AFC/NFC standings, divisions, playoff seeds, wild cards, cut-line helpers, clinch data, favorite-team highlighting, and flat team lists |
| 📊 **Player / team leaders** | MLB player leader sensors plus NFL per-team game leaders for passing, rushing, receiving, sacks, and tackles |
| 💾 **Failure-resistant data** | Last-good caching keeps cards populated when ESPN temporarily times out or returns bad data |

Sports Ticker remains a reusable sports-data layer. Built-in cards are additive; existing sensors, entity IDs, YAML examples, `custom:button-card`, `card-mod`, Mushroom, and custom dashboards remain supported.

---

## Built-in Sports Ticker cards

Sports Ticker includes a graphical Home Assistant card editor. In the current `v0.20.4` prerelease line, the editor exposes three card modes from the same Sports Ticker configuration experience:

| Card mode | What it does |
| :--- | :--- |
| **Game** | Shows one matchup from a selected league, with Standard and Compact layouts |
| **Game Highlights** | Plays ESPN highlight video and can strictly filter to the configured favorite team |
| **Multi-Sport Ticker** | Scrolls games from one or more enabled leagues |

The graphical editor only shows leagues that are enabled in Sports Ticker and have an available raw scoreboard sensor.

### Game

The Game card supports:

- Standard and Compact layouts
- Show/hide league
- Team records
- Venue
- Broadcast
- Team logos
- Optional event ID and entity override for advanced use

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game
```

Compact example:

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game_compact
```

### Game Highlights

The Highlights card reads playable video metadata directly from the selected league's raw scoreboard data. It includes a large center play button, matchup score, recap text, and an optional ESPN link.

The favorite team comes directly from Sports Ticker integration settings.

- **Favorite teams only** — strict mode. Only show a highlight involving the configured favorite team. Never fall back to another game.
- **Prefer favorite team** — soft preference. Use a favorite-team highlight first, then fall back to another playable game when strict mode is off.
- **Show recap text** — display ESPN recap/headline text when available.
- **Show ESPN link** — show an external ESPN link when provided by the feed.

```yaml
type: custom:sports-ticker-highlights-card
entity: sensor.espn_mlb_scoreboard_raw
favorite_only: true
prefer_favorite: true
show_recap: true
show_espn_link: true
```

If strict favorite-only mode is enabled and no favorite team is configured, or ESPN has no playable favorite-team highlight in the current data, the card shows an explicit empty state instead of another team's game.

### Multi-Sport Ticker

The ticker can combine multiple enabled leagues and includes controls for logos, pause-on-hover, seconds per game, and maximum games per sport.

```yaml
type: custom:sports-ticker-card
preset: ticker
sports:
  - nfl
  - cfb
  - mlb
show_logos: true
ticker_pause_on_hover: true
ticker_seconds_per_game: 8
ticker_max_games_per_sport: 20
```

Built-in cards follow Home Assistant theme variables by default instead of forcing a separate dashboard theme.

**Full card documentation:** [Built-in Sports Ticker Cards](examples/BUILT_IN_CARDS.md)

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

The current built-in Game, Highlights, and Ticker selectors map scoreboard-card support to MLB, NFL, College Football, NBA, WNBA, NHL, MLS, Premier League, LaLiga, Bundesliga, Serie A, Ligue 1, and UEFA Champions League. PGA Tour and NASCAR data remain integration features but are not yet mapped into the built-in scoreboard-card selectors.

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

Typical attributes include `events`, season/day metadata, favorite-team information, ticker settings, highlight/video metadata where ESPN provides it, and data-freshness metadata.

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

To test card features from the `v0.20.4` development line, enable prerelease versions for Sports Ticker in HACS and install the current prerelease.

### Manual installation

Copy `custom_components/sports_ticker/` to `config/custom_components/sports_ticker/`, restart Home Assistant, then add **Sports Ticker** from **Settings → Devices & services**.

---

## Configuration

Open:

```text
Settings → Devices & services → Sports Ticker → Configure
```

Choose the leagues you want, then configure favorite teams, poll interval, ticker speed, and other available league settings.

Favorite-team-aware cards use the favorite team configured here; you do not need to enter the favorite team separately on each card.

---

## Lovelace examples

The `examples/` folder contains complete custom dashboard examples in addition to the built-in cards.

| Sport / Guide | Examples |
| :--- | :--- |
| 🧩 Built-in cards | [Game, Game Highlights, Multi-Sport Ticker, favorite-team filtering, and YAML](examples/BUILT_IN_CARDS.md) |
| 🏈 NFL | [Next game, scrolling ticker, highlights, leaders, standings, playoff picture, and more](examples/NFL.md) |
| 🏈 College Football | [Rankings and College Football cards](examples/CFB.md) |
| ⚾ MLB | [Ticker, schedule, standings-style layouts, stats, highlights, and game cards](examples/MLB.md) |
| 🏀 NBA | [Schedule, ticker, and dashboard cards](examples/NBA.md) |
| 🌐 Multi-sport | [`multi_league_ticker_card.yaml`](examples/multi_league_ticker_card.yaml) |

Community frontend cards remain optional and are only required by examples that reference them. The built-in Sports Ticker cards themselves do not require `custom:button-card` or `card-mod`.

---

## Reliability and caching

ESPN endpoints occasionally timeout, return incomplete data, or temporarily fail. Sports Ticker preserves the last known good result whenever possible instead of blanking dashboards.

Fresh data reports `stale: false`; cached fallback data reports `stale: true` with source/error metadata so cards and automations can react appropriately.

---

## Current development

The current stable release is **v0.20.3**. The current feature line is **v0.20.4**, with **v0.20.4-alpha.2** adding the unified three-mode graphical card editor and the built-in Game Highlights card.

The `v0.20.4` card work is additive and keeps existing sensors, entity IDs, and YAML dashboards backward-compatible.

### Planned soccer expansion

- 🇳🇱 **Dutch Eredivisie** (`NED.1`) — planned for an upcoming soccer-focused feature line, beginning with scoreboard/events, favorite-team support, and ticker/card compatibility.

Future feature lines are planned around seasonal timing, with additional soccer competitions, College Basketball, Tennis, Rugby, Formula 1, AFL, Cricket, MotoGP, IndyCar, college baseball/softball, and other sports under consideration.

---

## Troubleshooting

### A sensor is missing

Confirm that its league is enabled under **Sports Ticker → Configure**, then reload or restart Home Assistant after an integration update.

### A built-in card mode is missing

The stable `v0.20.3` line includes the original built-in card framework. **Game Highlights** and the unified three-mode editor are part of the `v0.20.4` prerelease line. Install the current prerelease, restart Home Assistant, and reload the browser frontend.

### No leagues appear in the graphical editor

The editor only lists enabled Sports Ticker leagues with an available raw scoreboard sensor. Enable the league under **Sports Ticker → Configure** and confirm its `sensor.espn_<league>_scoreboard_raw` entity exists.

### Favorite teams only shows no game

This mode is intentionally strict. Confirm a favorite team is configured for the selected league and that ESPN currently provides a playable highlight for a game involving that team.

### A Highlights card says no playable highlights are available

ESPN did not expose a direct playable video source for the games currently present in the raw scoreboard feed. Highlight availability varies by event and league.

### A card is blank

Check that the selected entity exists and exposes the data expected by the selected card. Scoreboard cards require an entity with an `events` attribute.

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
