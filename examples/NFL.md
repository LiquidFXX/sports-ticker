<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏈 NFL Example Layouts

Copy/paste Home Assistant dashboard examples for the **Sports Ticker** integration.

The NFL examples use the raw scoreboard sensor and the favorite-team next-game sensor:

```yaml
sensor.espn_nfl_scoreboard_raw
sensor.espn_nfl_next_game
```

## Requirements

| Requirement | Purpose |
| --- | --- |
| `sports_ticker` integration | Provides ESPN-style NFL data |
| `sensor.espn_nfl_next_game` | Favorite team's next scheduled game |
| `sensor.espn_nfl_scoreboard_raw` | Full NFL scoreboard source |
| `custom:button-card` | Required for the custom cards |
| `card-mod` | Required for advanced styling |

## 🧭 NFL Layout Options

| Layout | Best For | Sensor Used |
| --- | --- | --- |
| 1. Favorite Team Next Game | A polished featured card for the configured favorite team | `sensor.espn_nfl_next_game` |
| 2. What's on this week | Schedule and matchup guide | `sensor.espn_nfl_scoreboard_raw` |
| 3. NFL Gamecast | Live game details | `sensor.espn_nfl_scoreboard_raw` |
| 4. NFL Old School Poster | Featured matchup poster | `sensor.espn_nfl_next_game` |
| 5. Game / team stats starter | Entity testing and quick access | Both |

---

## 1. Favorite Team Next Game

A featured next-game card that automatically follows the NFL favorite selected in Sports Ticker. It shows the favorite team, opponent, kickoff date and time, venue, broadcast, week, and whether the game is home or away.

<img src="images/nfl_next_game_card.jpg" alt="NFL Next Game card example" width="520">

> No team abbreviation needs to be hard-coded. The card reads the configured favorite directly from `sensor.espn_nfl_next_game`.

<details open>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
entity: sensor.espn_nfl_next_game

show_icon: false
show_name: false
show_state: false

tap_action:
  action: more-info

variables:
  src: sensor.espn_nfl_next_game

styles:
  card:
    - padding: 0
    - border-radius: 22px
    - overflow: hidden
    - background: rgba(8, 19, 36, 0.96)
    - border: 1px solid rgba(255, 255, 255, 0.10)
    - box-shadow: 0 18px 45px rgba(0, 0, 0, 0.30)
    - container-type: inline-size
  grid:
    - grid-template-areas: '"main"'
    - grid-template-columns: 1fr
    - grid-template-rows: auto
  custom_fields:
    main:
      - width: 100%

custom_fields:
  main: |
    [[[
      const entityId = variables.src;
      const st = states[entityId];

      const esc = (value) =>
        String(value ?? "")
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");

      if (!st) {
        return `
          <div class="empty">
            <div class="empty-icon">🏈</div>
            <div class="empty-title">NFL NEXT GAME</div>
            <div class="empty-sub">${esc(entityId)} is unavailable</div>
          </div>
        `;
      }

      const a = st.attributes || {};
      const favorite = String(a.favorite_team || "").trim().toUpperCase();
      const favoriteName = a.favorite_team_name || favorite || "Favorite Team";

      if (!favorite) {
        return `
          <div class="empty">
            <div class="empty-icon">⭐</div>
            <div class="empty-title">SELECT AN NFL FAVORITE</div>
            <div class="empty-sub">Choose your favorite NFL team in Sports Ticker options.</div>
          </div>
        `;
      }

      if (!a.has_upcoming_game || !a.date) {
        return `
          <div class="empty">
            <div class="empty-icon">🏈</div>
            <div class="empty-title">${esc(favoriteName)}</div>
            <div class="empty-sub">No upcoming game found</div>
            ${a.stale ? `<div class="cache-pill">CACHED DATA</div>` : ""}
          </div>
        `;
      }

      const opponent = String(a.opponent || "OPP").toUpperCase();
      const opponentName = a.opponent_name || opponent;
      const side = String(a.home_away || "").toLowerCase();

      const date = new Date(a.date);
      const validDate = !Number.isNaN(date.getTime());

      const dateText = validDate
        ? date.toLocaleDateString(undefined, {
            weekday: "short",
            month: "short",
            day: "numeric"
          })
        : "";

      const timeText = validDate
        ? date.toLocaleTimeString(undefined, {
            hour: "numeric",
            minute: "2-digit"
          })
        : "";

      const kickoff = [dateText, timeText].filter(Boolean).join(" • ");
      const venue = a.venue || "Venue TBD";
      const location = [a.venue_city, a.venue_state].filter(Boolean).join(", ");

      const broadcasts = Array.isArray(a.broadcasts)
        ? a.broadcasts.filter(Boolean)
        : [];

      const broadcast = broadcasts.length
        ? broadcasts.slice(0, 3).join(" • ")
        : "Broadcast TBD";

      const week = a.week ? `Week ${a.week}` : "NFL";
      const gameType = side === "home"
        ? "Home game"
        : side === "away"
          ? "Away game"
          : "Scheduled game";

      const centerWord = side === "away" ? "AT" : "VS";
      const status = String(a.status || "pre").toLowerCase();

      let badge = "UPCOMING";
      let badgeClass = "upcoming";

      if (status === "in") {
        badge = "LIVE";
        badgeClass = "live";
      } else if (status === "post") {
        badge = "FINAL";
        badgeClass = "final";
      }

      return `
        <div class="wrap">

          <div class="header">
            <div class="header-left">
              <div class="header-icon">🏈</div>
              <div class="title">NEXT GAME</div>
            </div>

            <div class="header-right">
              ${a.stale ? `<span class="status cached">CACHED</span>` : ""}
              <span class="status ${badgeClass}">${badge}</span>
            </div>
          </div>

          <div class="matchup">
            <div class="team favorite-team">
              <div class="team-mark">${esc(favorite)}</div>
              <div class="team-abbr">${esc(favorite)}</div>
              <div class="favorite-pill">★ FAVORITE</div>
            </div>

            <div class="versus">
              <div class="vs-line"></div>
              <div class="vs-circle">${centerWord}</div>
              <div class="vs-line"></div>
            </div>

            <div class="team opponent-team">
              <div class="team-mark">${esc(opponent)}</div>
              <div class="team-abbr opponent">${esc(opponent)}</div>
              <div class="opponent-name">${esc(opponentName)}</div>
            </div>
          </div>

          <div class="game-info">
            <div class="info-row primary">
              <span class="info-icon">📅</span>
              <span>${esc(kickoff)}</span>
            </div>

            <div class="info-row">
              <span class="info-icon">📍</span>
              <span>${esc(venue)}</span>
            </div>

            <div class="info-row">
              <span class="info-icon">📺</span>
              <span>${esc(broadcast)}</span>
            </div>
          </div>

          <div class="footer">
            <div class="footer-item">${esc(week)}</div>
            <div class="footer-divider"></div>
            <div class="footer-item">${esc(gameType)}</div>
            ${location ? `
              <div class="footer-divider"></div>
              <div class="footer-item">${esc(location)}</div>
            ` : ""}
          </div>

        </div>
      `;
    ]]]

card_mod:
  style: |
    .wrap {
      width: 100%;
      color: white;
      box-sizing: border-box;
      font-family: var(--paper-font-body1_-_font-family);
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: clamp(20px, 4cqw, 34px);
      min-height: clamp(82px, 14cqw, 120px);
      box-sizing: border-box;
      border-bottom: 1px solid rgba(255,255,255,.11);
      background: linear-gradient(180deg, rgba(255,255,255,.025), transparent);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: clamp(14px, 2.5cqw, 22px);
      min-width: 0;
    }

    .header-icon {
      width: clamp(54px, 9cqw, 78px);
      height: clamp(54px, 9cqw, 78px);
      display: flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 auto;
      border-radius: 20px;
      font-size: clamp(26px, 4.5cqw, 38px);
      background: rgba(38,91,160,.15);
      border: 1px solid rgba(80,145,235,.32);
    }

    .title {
      color: white;
      font-size: clamp(23px, 5cqw, 40px);
      font-weight: 900;
      letter-spacing: 2px;
      line-height: 1;
      white-space: nowrap;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 7px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .status {
      padding: 8px 17px;
      border-radius: 999px;
      font-size: clamp(10px, 1.8cqw, 14px);
      font-weight: 900;
      letter-spacing: 1px;
      border: 1px solid rgba(255,255,255,.12);
    }

    .status.upcoming {
      color: #94bcff;
      background: rgba(35,92,180,.14);
      border-color: rgba(64,132,235,.45);
    }

    .status.live {
      color: white;
      background: rgba(225,40,52,.92);
      border-color: rgba(255,85,95,.45);
      box-shadow: 0 0 18px rgba(225,40,52,.24);
    }

    .status.final {
      color: rgba(255,255,255,.78);
      background: rgba(255,255,255,.08);
    }

    .status.cached {
      color: #ffd17a;
      background: rgba(255,175,25,.10);
      border-color: rgba(255,195,65,.28);
    }

    .matchup {
      display: grid;
      grid-template-columns: minmax(0,1fr) clamp(58px, 9cqw, 82px) minmax(0,1fr);
      align-items: stretch;
      gap: clamp(10px, 2cqw, 18px);
      padding: clamp(26px, 5cqw, 40px) clamp(18px, 4cqw, 30px) 18px;
    }

    .team {
      min-width: 0;
      min-height: clamp(230px, 38cqw, 330px);
      padding: clamp(18px, 3.5cqw, 28px);
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border-radius: 28px;
      border: 1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.025);
    }

    .favorite-team {
      background: radial-gradient(circle at top left, rgba(206,40,55,.16), transparent 65%), rgba(255,255,255,.02);
      border-color: rgba(221,51,64,.46);
    }

    .opponent-team {
      background: radial-gradient(circle at top right, rgba(66,105,170,.14), transparent 62%), rgba(255,255,255,.02);
    }

    .team-mark {
      width: clamp(66px, 11cqw, 90px);
      height: clamp(66px, 11cqw, 90px);
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      color: white;
      background: rgba(255,255,255,.065);
      border: 1px solid rgba(255,255,255,.16);
      font-size: clamp(18px, 3.5cqw, 28px);
      font-weight: 900;
    }

    .team-abbr {
      margin-top: clamp(20px, 3.5cqw, 30px);
      color: white;
      font-size: clamp(38px, 8cqw, 66px);
      font-weight: 900;
      line-height: 1;
      letter-spacing: 1px;
    }

    .team-abbr.opponent {
      color: rgba(240,243,250,.94);
    }

    .favorite-pill {
      margin-top: clamp(20px, 3cqw, 26px);
      padding: 6px 12px;
      border-radius: 999px;
      color: white;
      background: linear-gradient(180deg, #ef3f4e, #c92232);
      font-size: clamp(9px, 1.6cqw, 12px);
      font-weight: 900;
      letter-spacing: .6px;
    }

    .opponent-name {
      margin-top: 9px;
      max-width: 100%;
      color: rgba(200,214,238,.50);
      font-size: clamp(9px, 1.5cqw, 12px);
      font-weight: 650;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .versus {
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
    }

    .vs-line {
      width: 1px;
      flex: 1;
      min-height: 35px;
      background: linear-gradient(transparent, rgba(255,255,255,.13), transparent);
    }

    .vs-circle {
      width: clamp(52px, 8cqw, 72px);
      height: clamp(52px, 8cqw, 72px);
      flex: 0 0 auto;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      color: #9cb3db;
      background: rgba(4,15,30,.76);
      border: 1px solid rgba(95,145,220,.22);
      font-size: clamp(12px, 2.4cqw, 18px);
      font-weight: 900;
      letter-spacing: 1px;
    }

    .game-info {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      padding: 10px clamp(18px, 4cqw, 32px) clamp(26px, 4cqw, 38px);
    }

    .info-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      max-width: 100%;
      color: #728bb5;
      font-size: clamp(12px, 2.1cqw, 17px);
      font-weight: 700;
      text-align: center;
    }

    .info-row.primary {
      color: white;
      font-size: clamp(19px, 4cqw, 30px);
      font-weight: 900;
    }

    .info-icon {
      flex: 0 0 auto;
      opacity: .75;
    }

    .footer {
      display: flex;
      align-items: center;
      justify-content: space-around;
      gap: clamp(10px, 2cqw, 22px);
      padding: clamp(19px, 3cqw, 26px) clamp(14px, 3cqw, 26px);
      border-top: 1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.018);
    }

    .footer-item {
      min-width: 0;
      color: #7f9bc7;
      font-size: clamp(11px, 2cqw, 15px);
      font-weight: 800;
      text-align: center;
      white-space: nowrap;
    }

    .footer-divider {
      width: 1px;
      height: 30px;
      flex: 0 0 auto;
      background: rgba(255,255,255,.08);
    }

    .empty {
      min-height: 240px;
      padding: 35px 20px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }

    .empty-icon {
      font-size: 38px;
    }

    .empty-title {
      margin-top: 12px;
      color: white;
      font-size: clamp(18px, 4cqw, 28px);
      font-weight: 900;
      letter-spacing: 1px;
    }

    .empty-sub {
      margin-top: 7px;
      color: rgba(200,215,238,.60);
      font-size: 13px;
      font-weight: 600;
    }

    .cache-pill {
      margin-top: 15px;
      padding: 5px 10px;
      border-radius: 999px;
      color: #ffce73;
      background: rgba(255,170,20,.10);
      border: 1px solid rgba(255,190,60,.24);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .8px;
    }

    @container (max-width: 520px) {
      .header {
        padding: 16px;
        min-height: 82px;
      }

      .header-icon {
        width: 46px;
        height: 46px;
        border-radius: 15px;
      }

      .title {
        font-size: 22px;
      }

      .status {
        padding: 6px 11px;
      }

      .matchup {
        padding: 20px 10px 12px;
        grid-template-columns: minmax(0,1fr) 46px minmax(0,1fr);
        gap: 6px;
      }

      .team {
        min-height: 190px;
        padding: 14px 7px;
        border-radius: 20px;
      }

      .team-mark {
        width: 56px;
        height: 56px;
      }

      .team-abbr {
        margin-top: 18px;
        font-size: 38px;
      }

      .favorite-pill {
        margin-top: 16px;
        padding: 5px 8px;
        font-size: 8px;
      }

      .opponent-name {
        display: none;
      }

      .vs-circle {
        width: 42px;
        height: 42px;
        font-size: 11px;
      }

      .game-info {
        padding: 12px 12px 24px;
      }

      .footer {
        padding: 16px 8px;
      }

      .footer-divider {
        display: none;
      }
    }
```

</details>

---

## 2. What's on this week

Uses `sensor.espn_nfl_scoreboard_raw` for a weekly matchup list with favorite-team priority, kickoff times, live/final status, scores, and broadcast networks.

```yaml
entity: sensor.espn_nfl_scoreboard_raw
```

---

## 3. NFL Gamecast

Uses `sensor.espn_nfl_scoreboard_raw` for a featured game view with NFL-specific fields such as quarter, clock, possession, down and distance, drives, venue, and team totals.

```yaml
variables:
  src: sensor.espn_nfl_scoreboard_raw
```

---

## 4. NFL Old School Poster

A featured matchup card designed around the configured favorite team's next game.

```yaml
entity: sensor.espn_nfl_next_game
```

---

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

### Next Game card shows no favorite

Choose an NFL favorite team in the Sports Ticker integration options. `sensor.espn_nfl_next_game` follows that configured favorite automatically.

### No upcoming game found

Confirm that `sensor.espn_nfl_next_game` exists and that its `has_upcoming_game` attribute is `true`.

### No scoreboard games found

Confirm that `sensor.espn_nfl_scoreboard_raw` exists and contains an `attributes.events` list.

### Template errors

Keep each `button-card` JavaScript template isolated and avoid duplicate variable declarations.
