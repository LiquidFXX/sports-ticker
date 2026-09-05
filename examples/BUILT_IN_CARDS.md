# 🧩 Built-in Sports Ticker Cards

Sports Ticker includes native Home Assistant dashboard cards that are loaded automatically by the integration. You do not need to add a manual Lovelace JavaScript resource.

The graphical card editor currently supports three card modes:

| Card mode | Best for | Main data source |
| :--- | :--- | :--- |
| **Game** | A single matchup / favorite-team game | `sensor.espn_<league>_scoreboard_raw` |
| **Game Highlights** | Playable ESPN highlight video with score and recap | `sensor.espn_<league>_scoreboard_raw` |
| **Multi-Sport Ticker** | A scrolling scoreboard across one or more enabled leagues | Raw scoreboard sensors for each selected league |

> The editor only shows leagues that are enabled in the Sports Ticker integration and currently expose a raw scoreboard sensor.

---

## Add a built-in card

1. Open a Home Assistant dashboard.
2. Choose **Edit dashboard → Add card**.
3. Select **Sports Ticker**.
4. Choose **Game**, **Game Highlights**, or **Multi-Sport Ticker** in the graphical editor.
5. Select the sport / league and configure the available options.

The card automatically selects the corresponding Sports Ticker scoreboard entity. Advanced users can still override the entity in YAML where supported.

---

## 1. Game

The Game card presents one matchup from a selected league. Automatic game selection prioritizes the configured favorite team when one is available, then active/upcoming games.

### Layouts

- **Standard** — full matchup presentation.
- **Compact** — reduced spacing and metadata for smaller dashboard areas.

### Visual editor options

- Show league
- Show team records
- Show venue
- Show broadcast
- Show team logos
- Optional ESPN event ID in advanced configuration
- Optional scoreboard entity override in advanced configuration

### YAML

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game
```

Compact layout:

```yaml
type: custom:sports-ticker-card
entity: sensor.espn_nfl_scoreboard_raw
preset: game_compact
```

---

## 2. Game Highlights

The Game Highlights card plays direct ESPN highlight video when ESPN exposes a playable source for an event. It includes a large center play control, matchup logos, score, recap text, and an optional ESPN link.

The favorite team is read directly from the selected league's Sports Ticker configuration. It does not need to be entered again on the card.

### Favorite-team behavior

**Favorite teams only** is a strict filter. When enabled, the card only considers playable highlights involving the configured favorite team. It does not fall back to another matchup. If the selected league has no favorite team configured, or no playable favorite-team highlight is available, the card displays an explicit empty state.

**Prefer favorite team** is a softer preference. When enabled and **Favorite teams only** is disabled, the card chooses a playable favorite-team highlight first when available and otherwise falls back to the newest playable game.

### Visual editor options

- Favorite teams only
- Prefer favorite team
- Show recap text
- Show ESPN link
- Sport / league selector using enabled Sports Ticker leagues

### YAML

```yaml
type: custom:sports-ticker-highlights-card
entity: sensor.espn_mlb_scoreboard_raw
favorite_only: true
prefer_favorite: true
show_recap: true
show_espn_link: true
```

To allow fallback to another game:

```yaml
type: custom:sports-ticker-highlights-card
entity: sensor.espn_mlb_scoreboard_raw
favorite_only: false
prefer_favorite: true
show_recap: true
show_espn_link: true
```

### Highlight availability

The card only displays events where Sports Ticker receives playable ESPN video metadata. A completed game is not guaranteed to have a playable highlight. Availability varies by league, event, and ESPN feed response.

---

## 3. Multi-Sport Ticker

The Multi-Sport Ticker combines games from one or more enabled leagues into a responsive scrolling scoreboard.

### Visual editor options

- Select one or more enabled leagues
- Show team logos
- Pause on hover
- Seconds per game
- Maximum games per sport

### YAML

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

The `sports` values use Sports Ticker league keys. The visual editor is recommended because it automatically limits choices to enabled leagues.

---

## Supported built-in-card leagues

The visual editor currently maps the built-in scoreboard cards to these enabled Sports Ticker leagues:

| Category | Leagues |
| :--- | :--- |
| Baseball | MLB |
| Football | NFL, College Football |
| Basketball | NBA, WNBA |
| Hockey | NHL |
| Soccer | MLS, Premier League, LaLiga, Bundesliga, Serie A, Ligue 1, UEFA Champions League |

Other Sports Ticker data sources such as PGA Tour and NASCAR remain available to the integration but are not yet mapped into these built-in card selectors.

---

## Favorite teams

Configure favorite teams from:

```text
Settings → Devices & services → Sports Ticker → Configure
```

The raw scoreboard sensor exposes the selected favorite team in attributes such as `favorite_team` and `favorite_team_name`. The Game and Game Highlights cards use that data directly.

---

## Built-in cards vs. YAML examples

The built-in cards are designed to work without `custom:button-card` or `card-mod` and follow Home Assistant theme variables by default.

The larger examples in `NFL.md`, `CFB.md`, `MLB.md`, and `NBA.md` remain available for advanced dashboards. Those examples may use community frontend cards and custom CSS for layouts that go beyond the built-in card set.

Existing YAML dashboards are not replaced by the built-in cards; both approaches are supported.

---

## Troubleshooting

### Game Highlights does not appear as a card mode

Use a Sports Ticker release that includes the unified three-mode editor, restart Home Assistant, and reload the browser frontend after updating the integration.

### No leagues are shown

Enable the desired league under **Sports Ticker → Configure** and confirm its `sensor.espn_<league>_scoreboard_raw` entity exists.

### Favorite teams only shows no highlight

Confirm a favorite team is configured for that league. The strict favorite-only mode intentionally does not fall back to another game.

### Highlight card says no playable highlights are available

ESPN did not provide a direct playable highlight source for the games currently present in the raw scoreboard data.

### Card styling does not match my dashboard

Built-in cards use Home Assistant theme variables. Check the active Home Assistant theme before adding card-specific styling.
