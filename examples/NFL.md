<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏈 NFL Example Layouts

Copy/paste Home Assistant dashboard examples for the **Sports Ticker** integration using the NFL raw scoreboard sensor.

These examples use:

```yaml
sensor.espn_nfl_scoreboard_raw
```

## Requirements

| Requirement | Purpose |
| --- | --- |
| `sports_ticker` integration | Provides ESPN-style NFL scoreboard data |
| `sensor.espn_nfl_scoreboard_raw` | Main NFL scoreboard source |
| `custom:button-card` | Required for custom scoreboard cards |
| `card-mod` | Required for advanced styling |

## 🧭 NFL Layout Options

| Layout | Best For |
| --- | --- |
| 1. ESPN-style NFL ticker | Compact scrolling scores |
| 2. What's on tonight | Schedule and matchup guide |
| 3. NFL Gamecast | Live game details |
| 4. NFL old school poster | Featured matchup card |
| 5. Team stats starter | Entity testing and quick access |

> This NFL edition follows the MLB examples but replaces baseball-specific logic with football fields: quarters, clocks, possession, drives, downs, distance, red-zone state, and TV/network information.

## 1. ESPN-style NFL ticker

Use the same ticker pattern with:

```yaml
variables:
  sport: NFL
  sensor: sensor.espn_nfl_scoreboard_raw
```

NFL status handling:
- LIVE: quarter and game clock
- FINAL: completed games
- UPCOMING: kickoff time

## 2. What's on tonight guide

Use:

```yaml
entity: sensor.espn_nfl_scoreboard_raw
variables:
  fav: KC
  max_games: 5
```

Displays:
- favorite team priority
- matchup
- score
- kickoff/live status
- broadcast networks

## 3. NFL Gamecast

Recommended variables:

```yaml
variables:
  src: sensor.espn_nfl_scoreboard_raw
  favorite: KC
```

NFL-specific data:
- quarter
- clock
- possession indicator
- down and distance
- drive information
- venue
- team totals

## 4. NFL Old School Poster

Featured matchup card using:

```yaml
variables:
  favorite: KC
```

Designed for a primary dashboard view with:
- large team logos
- scores
- game status
- matchup presentation

## 5. Game / team stats starter

```yaml
type: entities
title: Game / Team Stats (example)
entities:
  - entity: sensor.espn_nfl_scoreboard_raw
    name: Raw scoreboard
  - entity: sensor.espn_nfl_next_game
    name: Next game
```

## 🛠️ Troubleshooting

### No games found

Confirm the sensor exists and contains:

```yaml
sensor.espn_nfl_scoreboard_raw
```

with an `attributes.events` list.

### Favorite team highlight missing

Use the ESPN abbreviation, for example:

```yaml
favorite: KC
```

### Template errors

Keep each `button-card` JavaScript template isolated and avoid duplicate variable declarations.
