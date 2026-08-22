<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# 🏈 College Football Example Layouts

Copy/paste Home Assistant dashboard examples for the **Sports Ticker** College Football integration.

```yaml
sensor.espn_college_football_rankings
sensor.espn_cfb_scoreboard_raw
sensor.espn_cfb_next_game
```

## Requirements

| Requirement | Purpose |
| --- | --- |
| `sports_ticker` integration | Provides ESPN College Football data |
| `sensor.espn_college_football_rankings` | Normalized College Football rankings |
| `custom:button-card` | Required for the custom cards |
| `card-mod` | Required for advanced styling |

## 🧭 College Football Layout Options

| Layout | Best For | Sensor Used |
| --- | --- | --- |
| 1. College Football Rankings | Full Top 25 with logos, records, points, movement, and poll status | `sensor.espn_college_football_rankings` |

---

## 1. College Football Rankings

A full Top 25 card built from the dedicated rankings sensor. It follows `primary_poll` automatically, uses AP early in the season, and can move to CFP rankings when they become available.

> Leave `variables.poll` blank to follow `primary_poll`. Set it to `ap_top_25` or `cfp` to force a specific available poll.
>
> ESPN reports `previous_rank: 0` for preseason rankings. This card shows no movement during preseason instead of treating every team as newly ranked.

<details>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
entity: sensor.espn_college_football_rankings
show_name: false
show_icon: false
show_state: false
tap_action:
  action: more-info
hold_action:
  action: none
triggers_update:
  - sensor.espn_college_football_rankings
grid_options:
  columns: 12
  rows: auto
variables:
  src: sensor.espn_college_football_rankings
  poll: ""
  max_teams: 25
styles:
  card:
    - padding: 0
    - overflow: hidden
    - border-radius: 22px
    - background: var(--ha-card-background, var(--card-background-color))
    - border: 1px solid var(--divider-color)
    - container-type: inline-size
  grid:
    - grid-template-areas: '"content"'
    - grid-template-columns: 1fr
    - grid-template-rows: auto
  custom_fields:
    content:
      - width: 100%
      - min-width: 0
custom_fields:
  content: |
    [[[
      const st = states[variables.src];
      const esc = v => String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

      if (!st) return `
        <div class="empty">
          <div class="empty-title">COLLEGE FOOTBALL RANKINGS</div>
          <div class="empty-sub">Rankings sensor unavailable</div>
        </div>`;

      const a = st.attributes || {};
      const polls = a.polls && typeof a.polls === "object" ? a.polls : {};
      let pollKey = String(variables.poll || "").trim() || a.primary_poll || "ap_top_25";
      let poll = polls[pollKey] || {};
      let rankings = Array.isArray(poll.ranks) ? poll.ranks : [];

      if (!rankings.length) {
        pollKey = "ap_top_25";
        poll = polls.ap_top_25 || {};
        rankings = Array.isArray(poll.ranks)
          ? poll.ranks
          : (Array.isArray(a.ap_top_25) ? a.ap_top_25 : []);
      }

      if (!rankings.length) return `
        <div class="empty">
          <div class="empty-title">COLLEGE FOOTBALL RANKINGS</div>
          <div class="empty-sub">No rankings available</div>
        </div>`;

      const maxTeams = Math.max(1, Math.min(25, Number(variables.max_teams || 25)));
      const teams = rankings.slice(0, maxTeams);
      const pollName = poll.short_name || poll.name || (pollKey === "cfp" ? "CFP Rankings" : "AP Poll");
      const preseason = String(poll.headline || "").toLowerCase().includes("preseason");

      const movement = row => {
        const current = Number(row?.rank);
        const previous = Number(row?.previous_rank);
        if (preseason) return { cls: "same", icon: "—", amount: "" };
        if (!Number.isFinite(previous) || previous <= 0) return { cls: "new", icon: "NEW", amount: "" };
        if (!Number.isFinite(current)) return { cls: "same", icon: "—", amount: "" };
        const diff = previous - current;
        if (diff > 0) return { cls: "up", icon: "▲", amount: diff };
        if (diff < 0) return { cls: "down", icon: "▼", amount: Math.abs(diff) };
        return { cls: "same", icon: "—", amount: "" };
      };

      const teamColor = row => {
        const color = String(row?.color || "").replace("#", "");
        return /^[0-9a-f]{6}$/i.test(color) ? `#${color}` : "var(--primary-color)";
      };

      const teamName = row =>
        row?.nickname || row?.location || row?.display_name || row?.abbreviation || "Team";

      const logo = row => row?.logo
        ? `<img class="team-logo" src="${esc(row.logo)}" alt="${esc(teamName(row))}" loading="lazy">`
        : `<div class="logo-fallback">${esc(row?.abbreviation || "CFB")}</div>`;

      const rowHtml = row => {
        const move = movement(row);
        return `
          <div class="ranking-row" style="--team-color:${teamColor(row)};">
            <div class="rank-number">${esc(row?.rank ?? "—")}</div>
            <div class="logo-shell">${logo(row)}</div>
            <div class="team-info">
              <div class="team-name">${esc(teamName(row))}</div>
              <div class="team-meta">
                <span class="record">${esc(row?.record || "0-0")}</span>
                ${row?.abbreviation ? `<span class="dot">•</span><span>${esc(row.abbreviation)}</span>` : ""}
              </div>
            </div>
            <div class="points">
              <strong>${esc(row?.points ?? "—")}</strong>
              <span>PTS</span>
            </div>
            <div class="move ${move.cls}">
              <span>${move.icon}</span>
              ${move.amount ? `<strong>${esc(move.amount)}</strong>` : ""}
            </div>
          </div>`;
      };

      const topFive = teams.slice(0, 5);

      return `
        <div class="rankings-shell">
          <div class="header">
            <div class="header-main">
              <div class="eyebrow">NCAA FOOTBALL</div>
              <div class="title">COLLEGE FOOTBALL RANKINGS</div>
              <div class="subtitle">
                <span class="poll">${esc(pollName)}</span>
                ${a.season ? `<span class="dot">•</span><span>${esc(a.season)}</span>` : ""}
                ${preseason
                  ? `<span class="dot">•</span><span>PRESEASON</span>`
                  : (a.week ? `<span class="dot">•</span><span>WEEK ${esc(a.week)}</span>` : "")}
              </div>
            </div>
            <div class="header-badges">
              <span class="status ${a.stale === true ? "cached" : "current"}">${a.stale === true ? "CACHED" : "CURRENT"}</span>
              <span class="top25">TOP 25</span>
            </div>
          </div>
          <div class="top-strip">
            ${topFive.map(team => `
              <div class="top-team">
                <span class="top-rank">${esc(team.rank)}</span>
                ${team.logo ? `<img src="${esc(team.logo)}" alt="${esc(teamName(team))}" loading="lazy">` : ""}
                <span class="top-name">${esc(teamName(team))}</span>
              </div>`).join("")}
          </div>
          <div class="rankings-list">${teams.map(rowHtml).join("")}</div>
          <div class="footer">
            <span>${esc(poll.headline || pollName)}</span>
            <span>SPORTS TICKER</span>
          </div>
        </div>`;
    ]]]
card_mod:
  style: |
    .rankings-shell {
      width: 100%;
      min-width: 0;
      color: var(--primary-text-color);
      background: var(--ha-card-background, var(--card-background-color));
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 20px 15px;
      border-bottom: 1px solid var(--divider-color);
    }
    .header-main { min-width: 0; }
    .eyebrow {
      margin-bottom: 5px;
      color: var(--secondary-text-color);
      font-size: 9px;
      font-weight: 900;
      letter-spacing: 1.7px;
    }
    .title {
      overflow: hidden;
      color: var(--primary-text-color);
      font-size: clamp(18px, 3.1cqw, 25px);
      font-weight: 950;
      line-height: 1.08;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .subtitle {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 7px;
      color: var(--secondary-text-color);
      font-size: 10px;
      font-weight: 800;
    }
    .poll { color: var(--primary-color); font-weight: 950; }
    .dot { opacity: .4; }
    .header-badges {
      flex: 0 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 7px;
    }
    .status, .top25 {
      min-width: 76px;
      padding: 7px 10px;
      box-sizing: border-box;
      border-radius: 999px;
      text-align: center;
      font-size: 9px;
      font-weight: 950;
      letter-spacing: .5px;
      border: 1px solid var(--divider-color);
    }
    .current {
      color: var(--success-color);
      background: color-mix(in srgb, var(--success-color) 8%, transparent);
    }
    .cached {
      color: var(--warning-color);
      background: color-mix(in srgb, var(--warning-color) 8%, transparent);
    }
    .top25 {
      color: var(--primary-text-color);
      background: color-mix(in srgb, var(--primary-text-color) 4%, transparent);
    }
    .top-strip {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 1px;
      background: var(--divider-color);
      border-bottom: 1px solid var(--divider-color);
    }
    .top-team {
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 9px 5px;
      text-align: center;
      background: var(--ha-card-background, var(--card-background-color));
    }
    .top-rank { color: var(--primary-text-color); font-size: 14px; font-weight: 950; }
    .top-team img { width: 28px; height: 28px; object-fit: contain; }
    .top-name {
      width: 100%;
      overflow: hidden;
      color: var(--secondary-text-color);
      font-size: 9px;
      font-weight: 850;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .ranking-row {
      position: relative;
      min-width: 0;
      display: grid;
      grid-template-columns: 48px 52px minmax(0, 1fr) 72px 42px;
      align-items: center;
      gap: 10px;
      min-height: 72px;
      padding: 8px 16px;
      box-sizing: border-box;
      border-bottom: 1px solid var(--divider-color);
    }
    .ranking-row::before {
      content: "";
      position: absolute;
      left: 0;
      top: 10px;
      bottom: 10px;
      width: 4px;
      border-radius: 0 4px 4px 0;
      background: var(--team-color);
      opacity: .85;
    }
    .ranking-row:hover {
      background: color-mix(in srgb, var(--team-color) 5%, transparent);
    }
    .rank-number {
      text-align: center;
      color: var(--primary-text-color);
      font-size: 24px;
      font-weight: 950;
      font-variant-numeric: tabular-nums;
    }
    .logo-shell {
      width: 46px;
      height: 46px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4px;
      box-sizing: border-box;
      border-radius: 13px;
      background: color-mix(in srgb, var(--primary-text-color) 4%, transparent);
      border: 1px solid var(--divider-color);
    }
    .team-logo { width: 36px; height: 36px; object-fit: contain; }
    .logo-fallback { color: var(--secondary-text-color); font-size: 9px; font-weight: 900; }
    .team-info { min-width: 0; }
    .team-name {
      overflow: hidden;
      color: var(--primary-text-color);
      font-size: 15px;
      font-weight: 950;
      line-height: 1.15;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .team-meta {
      display: flex;
      align-items: center;
      gap: 5px;
      margin-top: 6px;
      color: var(--secondary-text-color);
      font-size: 10px;
      font-weight: 750;
    }
    .record { font-weight: 850; }
    .points {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
    }
    .points strong {
      color: var(--primary-text-color);
      font-size: 14px;
      font-weight: 950;
      font-variant-numeric: tabular-nums;
    }
    .points span {
      color: var(--secondary-text-color);
      font-size: 7px;
      font-weight: 900;
      letter-spacing: .7px;
    }
    .move {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 2px;
      font-size: 10px;
      font-weight: 950;
      font-variant-numeric: tabular-nums;
    }
    .move.up { color: var(--success-color); }
    .move.down { color: var(--error-color); }
    .move.same { color: var(--secondary-text-color); }
    .move.new { color: var(--primary-color); font-size: 8px; letter-spacing: .3px; }
    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 16px;
      color: var(--secondary-text-color);
      font-size: 8px;
      font-weight: 750;
    }
    .empty {
      min-height: 120px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 20px;
    }
    .empty-title { color: var(--primary-text-color); font-size: 15px; font-weight: 900; }
    .empty-sub { color: var(--secondary-text-color); font-size: 10px; }
    @container (max-width: 520px) {
      .header { padding: 15px 13px 12px; }
      .title { font-size: 16px; }
      .header-badges { gap: 5px; }
      .status, .top25 { min-width: 66px; padding: 6px 8px; font-size: 8px; }
      .top-team { padding: 7px 2px; }
      .top-team img { width: 23px; height: 23px; }
      .top-rank { font-size: 12px; }
      .top-name { font-size: 7px; }
      .ranking-row {
        grid-template-columns: 34px 40px minmax(0,1fr) 56px 30px;
        gap: 6px;
        min-height: 61px;
        padding: 6px 9px;
      }
      .rank-number { font-size: 19px; }
      .logo-shell { width: 38px; height: 38px; border-radius: 11px; }
      .team-logo { width: 30px; height: 30px; }
      .team-name { font-size: 12px; }
      .team-meta { margin-top: 4px; font-size: 8px; }
      .points strong { font-size: 11px; }
      .points span { font-size: 6px; }
      .move { font-size: 9px; }
      .footer { flex-direction: column; align-items: flex-start; gap: 3px; }
    }
```

</details>

### Card behavior

- Uses `sensor.espn_college_football_rankings` directly.
- Follows `primary_poll` by default and falls back to AP if the selected poll is empty.
- Shows `PRESEASON` when the poll headline identifies a preseason ranking.
- Shows up/down/new movement once previous rankings exist.
- Uses ESPN team logos and normalized team colors.
- Uses Home Assistant theme variables instead of forcing a light or dark theme.
- Shows `CACHED` when Sports Ticker is serving the last successful rankings response.

---

More College Football examples will be added here as the CFB card set is built out.
