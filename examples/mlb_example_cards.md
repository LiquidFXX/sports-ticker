<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->

# ⚾ MLB Example Layouts

Copy/paste Home Assistant dashboard examples for the **Sports Ticker** integration using the MLB raw scoreboard sensor.

These examples are built around:

```yaml
sensor.espn_mlb_scoreboard_raw
```

Use this page when you want a quick MLB dashboard section, a full gamecast-style view, or a starter card for standings and team stats.

---

## ✅ Requirements

| Requirement | Purpose |
| :--- | :--- |
| `sports_ticker` integration | Provides the ESPN-style MLB scoreboard sensor |
| `sensor.espn_mlb_scoreboard_raw` | Main source used by every MLB example below |
| `custom:button-card` | Required for the ticker, tonight guide, and gamecast cards |
| `card-mod` | Required for the CSS styling in the ticker and guide cards |

> Entity names can vary depending on your setup. If your MLB raw sensor has a different name, update the `sensor`, `src`, or `entity` value in the YAML.

---

## 🧭 MLB Layout Options

| Layout | Best For | Sensor Used |
| :--- | :--- | :--- |
| [1. ESPN-style MLB ticker](#1-espn-style-mlb-ticker) | A compact scrolling scoreboard | `sensor.espn_mlb_scoreboard_raw` |
| [2. What’s on tonight](#2-whats-on-tonight-guide) | A clean schedule/game list | `sensor.espn_mlb_scoreboard_raw` |
| [3. MLB Gamecast](#3-mlb-gamecast-card) | Full scoreboard with inning linescore | `sensor.espn_mlb_scoreboard_raw` |
| [4. MLB old school poster](#4-mlb-old-school-poster) | Basic standings text output | `sensor.espn_mlb_standings` |
| [5. Game/team stats starter](#5-game--team-stats-starter) | Raw entity and next-game quick view | `sensor.espn_mlb_scoreboard_raw` |

---

## 1. ESPN-style MLB ticker

A compact scrolling ticker designed for the top or bottom of a dashboard. It shows team abbreviations, logos, scores, live/final/upcoming status, and highlights the leading team.

![MLB ticker example](https://github.com/user-attachments/assets/5f63fdf8-9eaf-4400-a3b2-fd7f04b7ea17)

<details open>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
show_name: false
show_state: false
variables:
  sport: MLB
  sensor: sensor.espn_mlb_scoreboard_raw
styles:
  card:
    - border-radius: 14px
    - overflow: hidden
    - padding: 0px
    - background: rgba(255,255,255,0.92)
    - border: 1px solid rgba(0,0,0,0.10)
    - box-shadow: 0 10px 22px rgba(0,0,0,0.18)
  custom_fields:
    ticker:
      - padding: 0px
custom_fields:
  ticker: |
    [[[
      const sport = (variables.sport || 'MLB').toUpperCase();
      const sensorId = variables.sensor || 'sensor.espn_mlb_scoreboard_raw';

      const raw = states[sensorId];
      const ev = raw?.attributes?.events || [];

      // ✅ Theme + speed come from integration options exposed as sensor attributes
      const theme = String(raw?.attributes?.ticker_theme ?? 'light').toLowerCase();
      const div = Number(raw?.attributes?.ticker_speed ?? 12);
      const safeDiv = Number.isFinite(div) ? Math.max(6, Math.min(30, div)) : 12;

      // ---- logo helpers (prefer feed logo; fallback ESPN CDN) ----
      const leagueFromSport = (s) => {
        const map = { NBA:'nba', WNBA:'wnba', MLB:'mlb', NFL:'nfl', NHL:'nhl' };
        return map[s] || null;
      };

      const nbaSlug = (abbr) => {
        const map = { NYK:'ny', NOP:'no', SAS:'sa', GSW:'gs', UTA:'utah' };
        return (map[abbr] || abbr || '').toLowerCase();
      };

      const mlbSlug = (abbr) => {
        const map = { ARI:'ari', KCR:'kc', CHW:'cws', SFG:'sf', SDP:'sd', TBR:'tb' };
        return (map[abbr] || abbr || '').toLowerCase();
      };

      const simpleSlug = (abbr) => (abbr || '').toLowerCase();

      const slugFor = (abbr) => {
        if (sport === 'NBA') return nbaSlug(abbr);
        if (sport === 'MLB') return mlbSlug(abbr);
        return simpleSlug(abbr);
      };

      const logoUrl = (teamObj, abbr) => {
        const direct = teamObj?.logo || teamObj?.logos?.[0]?.href || teamObj?.logos?.[0]?.url;
        if (direct) return direct;

        const league = leagueFromSport(sport);
        if (!league) return '';
        const slug = slugFor(abbr);
        return slug ? `https://a.espncdn.com/i/teamlogos/${league}/500/${slug}.png` : '';
      };

      // ---- status chips ----
      const parseMLBHalf = (shortDetail) => {
        const s = (shortDetail || '').trim();
        const m = s.match(/^(Top|Bot|Bottom|Mid|End)\s+(\d+)(?:st|nd|rd|th)?/i);
        if (!m) return null;
        let half = m[1].toLowerCase();
        const inning = m[2];
        if (half === 'bottom') half = 'bot';
        const isTop = half === 'top';
        return { label: isTop ? `▲ Top ${inning}` : `▼ Bot ${inning}` };
      };

      const chips = (stState, stShort, when) => {
        if (stState === 'in') {
          if (sport === 'MLB') {
            const inn = parseMLBHalf(stShort);
            return `<span class="pill live">LIVE</span><span class="pill meta">${inn ? inn.label : (stShort || 'In Progress')}</span>`;
          }
          return `<span class="pill live">LIVE</span><span class="pill meta">${stShort || 'In Progress'}</span>`;
        }
        if (stState === 'post') {
          const txt = /final/i.test(stShort) ? stShort : 'FINAL';
          return `<span class="pill final">${txt}</span>`;
        }
        return `<span class="pill upcoming">UPCOMING</span><span class="pill meta">${when}</span>`;
      };

      const num = (v) => {
        const n = Number.parseFloat(v);
        return Number.isFinite(n) ? n : null;
      };

      if (!ev.length) {
        return `
          <div class="bar ${theme}" style="--dur:45s">
            <div class="wrap">
              <div class="marquee">
                <div class="tile">
                  <div class="top">
                    <span class="pill upcoming">NO GAMES</span>
                    <span class="pill meta">${sport}</span>
                  </div>
                  <div class="teams one">
                    <div class="row"><span class="abbr">No ${sport} games today</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>`;
      }

      const tiles = [];
      const speedTextParts = [];

      ev.forEach(e => {
        const comp = e?.competitions?.[0];
        const teams = comp?.competitors || [];
        const away = teams.find(t => t.homeAway === 'away');
        const home = teams.find(t => t.homeAway === 'home');

        const aAbbr = away?.team?.abbreviation ?? (away?.team?.shortDisplayName ?? 'AWY');
        const hAbbr = home?.team?.abbreviation ?? (home?.team?.shortDisplayName ?? 'HOM');

        const aScoreRaw = away?.score ?? '';
        const hScoreRaw = home?.score ?? '';
        const aScore = num(aScoreRaw);
        const hScore = num(hScoreRaw);

        const stState = e?.status?.type?.state ?? '';
        const stShort = e?.status?.type?.shortDetail ?? '';
        const when = new Date(e.date).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });

        const aLogo = logoUrl(away?.team, aAbbr);
        const hLogo = logoUrl(home?.team, hAbbr);

        const showScores = (stState !== 'pre');

        let awayWin = false, homeWin = false;
        if (showScores && aScore != null && hScore != null && aScore !== hScore) {
          awayWin = aScore > hScore;
          homeWin = hScore > aScore;
        }

        speedTextParts.push(`${aAbbr} ${aScoreRaw} ${hAbbr} ${hScoreRaw} ${stShort}`);

        tiles.push(`
          <div class="tile">
            <div class="top">${chips(stState, stShort, when)}</div>
            <div class="teams">
              <div class="row">
                <span class="wdot ${awayWin ? 'on' : ''}"></span>
                <img class="tlogo" src="${aLogo}" alt="${aAbbr}" onerror="this.style.display='none'">
                <span class="abbr">${aAbbr}</span>
                <span class="score">${showScores ? aScoreRaw : ''}</span>
              </div>
              <div class="row">
                <span class="wdot ${homeWin ? 'on' : ''}"></span>
                <img class="tlogo" src="${hLogo}" alt="${hAbbr}" onerror="this.style.display='none'">
                <span class="abbr">${hAbbr}</span>
                <span class="score">${showScores ? hScoreRaw : ''}</span>
              </div>
            </div>
          </div>
        `);
      });

      const textForSpeed = speedTextParts.join(' • ');
      const seconds = Math.round(textForSpeed.length / safeDiv);
      const dur = Math.max(22, Math.min(90, seconds)) + 's';

      return `
        <div class="bar ${theme}" style="--dur:${dur}">
          <div class="wrap">
            <div class="marquee">${tiles.join(`<div class="sep"></div>`)}</div>
          </div>
        </div>`;
    ]]]
card_mod:
  style: |
    .bar{
      min-height: 60px;
      display:flex;
      align-items:center;
    }

    .bar.light{
      background: rgba(245,245,245,0.98);
      --pill-bg: rgba(255,255,255,0.92);
      --pill-border: rgba(0,0,0,0.12);
      --pill-text: rgba(0,0,0,0.78);
      --meta-text: rgba(0,0,0,0.58);
      --row-text: rgba(0,0,0,0.82);
      --sep: rgba(0,0,0,0.10);
      --wdot: rgba(0,0,0,0.10);
      --wdot-border: rgba(0,0,0,0.12);
    }

    .bar.dark{
      background: rgba(20,20,20,0.92);
      --pill-bg: rgba(0,0,0,0.35);
      --pill-border: rgba(255,255,255,0.14);
      --pill-text: rgba(255,255,255,0.88);
      --meta-text: rgba(255,255,255,0.60);
      --row-text: rgba(255,255,255,0.90);
      --sep: rgba(255,255,255,0.10);
      --wdot: rgba(255,255,255,0.14);
      --wdot-border: rgba(255,255,255,0.14);
    }

    .wrap{
      overflow:hidden;
      width:100%;
      -webkit-mask-image: linear-gradient(90deg, transparent 0%, black 7%, black 93%, transparent 100%);
              mask-image: linear-gradient(90deg, transparent 0%, black 7%, black 93%, transparent 100%);
    }

    .marquee{
      display:inline-flex;
      align-items:center;
      white-space:nowrap;
      padding-left:100%;
      animation: espn-marquee var(--dur, 34s) linear infinite;
      will-change: transform;
    }
    ha-card:hover .marquee{ animation-play-state: paused; }

    @keyframes espn-marquee{
      0%{ transform: translateX(0%); }
      100%{ transform: translateX(-100%); }
    }

    .tile{
      min-width:190px;
      padding:6px 10px;
      display:flex;
      flex-direction:column;
      gap:4px;
    }
    .sep{
      height:44px;
      border-right:1px solid var(--sep);
      margin:0 2px;
    }
    .top{ display:flex; gap:6px; align-items:center; }

    .pill{
      font-size:10px;
      font-weight:900;
      padding:2px 7px;
      border-radius:999px;
      border:1px solid var(--pill-border);
      color: var(--pill-text);
      background: var(--pill-bg);
      letter-spacing:.4px;
    }
    .pill.live{
      background: rgba(208,0,0,0.92);
      border-color: rgba(208,0,0,0.92);
      color:#fff;
    }
    .pill.final{
      background: rgba(0,0,0,0.08);
    }
    .bar.dark .pill.final{
      background: rgba(255,255,255,0.10);
    }
    .pill.meta{ color: var(--meta-text); }

    .teams{ display:flex; flex-direction:column; gap:3px; }
    .row{ display:flex; align-items:center; gap:8px; line-height:1.05; }

    .wdot{
      width:8px;
      height:8px;
      border-radius:50%;
      background: var(--wdot);
      border: 1px solid var(--wdot-border);
    }
    .wdot.on{
      background:#2ecc71;
      border-color: rgba(46,204,113,0.65);
      box-shadow: 0 0 10px rgba(46,204,113,0.35);
    }

    .tlogo{
      width:18px;
      height:18px;
      object-fit:contain;
      border-radius:4px;
      filter: drop-shadow(0 1px 1px rgba(0,0,0,0.18));
    }
    .abbr{
      font-size:12px;
      font-weight:900;
      color: var(--row-text);
      min-width:36px;
      letter-spacing:.3px;
    }
    .score{
      margin-left:auto;
      font-size:12px;
      font-weight:1000;
      color: var(--row-text);
    }
```

</details>

---

## 2. What’s on tonight guide

A polished MLB schedule card that sorts favorite-team games first, then live games, upcoming games, and finals. Set your favorite team with `fav: ATL`.

<img width="592" height="561" alt="MLB what's on tonight example" src="https://github.com/user-attachments/assets/70082f86-3dc1-4a42-a6d6-d01cb126863f" />

<details>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
entity: sensor.espn_mlb_scoreboard_raw
show_icon: false
show_name: false
show_state: false
variables:
  src: sensor.espn_mlb_scoreboard_raw
  fav: ATL
  max_games: 5
styles:
  card:
    - border-radius: 20px
    - padding: 0px
    - overflow: hidden
    - background: rgba(20,20,24,0.70)
    - backdrop-filter: blur(10px)
    - border: 1px solid rgba(255,255,255,0.10)
  grid:
    - grid-template-areas: "\"main\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
  custom_fields:
    main:
      - width: 100%
custom_fields:
  main: |
    [[[
      const ent = variables.src;
      const fav = variables.fav;
      const MAX = Number(variables.max_games ?? 10);

      const st = states[ent];
      if (!st) return `Entity not found: ${ent}`;

      const events = st.attributes?.events || [];
      if (!events.length) return 'No games found';

      const rows = events.map(e => {
        const c = e.competitions?.[0];
        const comps = c?.competitors || [];
        const home = comps.find(x => x.homeAway === 'home');
        const away = comps.find(x => x.homeAway === 'away');

        const hA = home?.team?.abbreviation ?? 'HOME';
        const aA = away?.team?.abbreviation ?? 'AWAY';
        const hN = home?.team?.shortDisplayName ?? home?.team?.displayName ?? hA;
        const aN = away?.team?.shortDisplayName ?? away?.team?.displayName ?? aA;

        const hL = home?.team?.logo || '';
        const aL = away?.team?.logo || '';

        const hS = home?.score ?? '';
        const aS = away?.score ?? '';

        const type = c?.status?.type || {};
        const state = type?.state; // pre / in / post
        const status = type?.shortDetail || type?.detail || type?.description || '';

        // TV networks
        const nets = (c?.broadcasts || []).flatMap(b => b?.names || []).filter(Boolean);
        const net = nets.slice(0,2).join(' • ');

        // MLB extras: inning / outs / count / base runners if present
        const sit = c?.situation || {};
        const balls = sit?.balls;
        const strikes = sit?.strikes;
        const outs = sit?.outs;

        const on1 = (sit?.onFirst === true) ? '●' : (sit?.onFirst === false ? '○' : '');
        const on2 = (sit?.onSecond === true) ? '●' : (sit?.onSecond === false ? '○' : '');
        const on3 = (sit?.onThird === true) ? '●' : (sit?.onThird === false ? '○' : '');

        const countStr = (Number.isFinite(balls) && Number.isFinite(strikes)) ? `${balls}-${strikes}` : '';
        const outsStr  = Number.isFinite(outs) ? `${outs} out${outs===1?'':'s'}` : '';
        const basesStr = (on1 || on2 || on3) ? `Bases ${on3}${on2}${on1}` : '';

        const detail2 = [countStr ? `Count ${countStr}` : '', outsStr, basesStr].filter(Boolean).join(' • ');

        const hasFav = (hA === fav) || (aA === fav);
        const liveRank = (state === 'in') ? 0 : (state === 'pre') ? 1 : 2;

        return {
          hasFav,
          liveRank,
          start: c?.date || e?.date || '',
          html: `
            <div class="game ${hasFav ? 'fav' : ''}">
              <div class="side">
                ${aL ? `<img class="logo" src="${aL}">` : `<div class="logo ph"></div>`}
                <div class="abbr">${aA}</div>
              </div>

              <div class="mid">
                <div class="match">
                  <span class="team">${aN}</span>
                  <span class="at">@</span>
                  <span class="team">${hN}</span>
                </div>
                <div class="meta">
                  <span class="st">${status}</span>
                  ${net ? `<span class="dot">•</span><span class="tv">${net}</span>` : ``}
                </div>
                ${detail2 ? `<div class="meta2">${detail2}</div>` : ``}
              </div>

              <div class="right">
                ${
                  (state === 'in' || state === 'post')
                  ? `<div class="score">${aS}<span class="dash">-</span>${hS}</div>`
                  : `<div class="pill">UP NEXT</div>`
                }
                ${hL ? `<img class="logo" src="${hL}">` : `<div class="logo ph"></div>`}
              </div>
            </div>
          `
        };
      });

      rows.sort((A, B) => {
        if (A.hasFav !== B.hasFav) return A.hasFav ? -1 : 1;
        if (A.liveRank !== B.liveRank) return A.liveRank - B.liveRank;
        return String(A.start).localeCompare(String(B.start));
      });

      const list = rows.slice(0, MAX).map(r => r.html).join('');

      return `
        <div class="wrap">
          <div class="hdr">
            <div class="title">WHAT’S ON TONIGHT</div>
            <div class="sub">MLB • ${events.length} games</div>
          </div>
          <div class="body">
            ${list}
          </div>
        </div>
      `;
    ]]]
card_mod:
  style: |
    .hdr{
      padding: 14px 16px 12px;
      border-bottom: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.04);
    }
    .title{
      color: #fff;
      font-size: 22px;
      font-weight: 900;
      letter-spacing: 0.6px;
    }
    .sub{
      margin-top: 4px;
      color: rgba(255,255,255,0.65);
      font-size: 13px;
      font-weight: 700;
    }

    .body{ padding: 10px 10px 12px; }

    .game{
      display:grid;
      grid-template-columns: 84px 1fr 140px;
      align-items:center;
      gap: 10px;
      padding: 10px 10px;
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.04);
      margin-bottom: 10px;
    }

    .game.fav{
      border-color: rgba(255,60,60,0.35);
      box-shadow: 0 0 0 1px rgba(255,60,60,0.18) inset;
      background: rgba(255,60,60,0.06);
    }

    .side{
      display:flex;
      align-items:center;
      gap: 8px;
      min-width: 0;
    }

    .abbr{
      color: rgba(255,255,255,0.80);
      font-weight: 900;
      letter-spacing: 0.6px;
    }

    .logo{
      width: 34px;
      height: 34px;
      object-fit: contain;
      border-radius: 10px;
      background: rgba(255,255,255,0.06);
    }

    .mid{ min-width: 0; }

    .match{
      color: #fff;
      font-size: 16px;
      font-weight: 900;
      letter-spacing: 0.2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .at{ opacity: .5; margin: 0 6px; }

    .meta{
      margin-top: 4px;
      color: rgba(255,255,255,0.62);
      font-size: 12px;
      font-weight: 700;
      display:flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items:center;
    }
    .meta2{
      margin-top: 4px;
      color: rgba(255,255,255,0.55);
      font-size: 12px;
      font-weight: 700;
    }
    .dot{ opacity: .4; }

    .right{
      display:flex;
      align-items:center;
      justify-content:flex-end;
      gap: 10px;
      min-width: 0;
    }

    .score{
      color: #fff;
      font-size: 18px;
      font-weight: 900;
      letter-spacing: 0.2px;
      white-space: nowrap;
    }
    .dash{ opacity: .5; padding: 0 6px; }

    .pill{
      color: rgba(255,255,255,0.90);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 1px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(255,255,255,0.06);
      white-space: nowrap;
    }

    @media (max-width: 520px){
      .game{ grid-template-columns: 72px 1fr 120px; }
      .match{ font-size: 14px; }
      .score{ font-size: 16px; }
    }
```

</details>

---

## 3. MLB Gamecast card

A larger MLB scoreboard layout with live status, team logos, scores, base runners, outs, venue info, and a 9-inning linescore table.

Set your favorite team here:

```yaml
variables:
  favorite: ATL
```

<img width="475" height="1227" alt="MLB gamecast example" src="https://github.com/user-attachments/assets/56be2ed7-7f1e-4f3d-8794-a5ef4189ab4e" />

<details>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
entity: sensor.espn_mlb_scoreboard_raw
show_name: false
show_icon: false
show_state: false
triggers_update:
  - sensor.espn_mlb_scoreboard_raw
variables:
  src: sensor.espn_mlb_scoreboard_raw
  favorite: ATL
  max_games: 8
styles:
  card:
    - padding: 0
    - border-radius: 24px
    - overflow: hidden
    - background: linear-gradient(180deg, rgba(8,12,20,0.98), rgba(14,20,32,0.96))
    - border: 1px solid rgba(255,255,255,0.08)
    - box-shadow: 0 12px 30px rgba(0,0,0,0.35)
  grid:
    - grid-template-areas: "\"main\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
  custom_fields:
    main:
      - width: 100%
custom_fields:
  main: |
    [[[
      const st = states[variables.src];
      if (!st) return `<div style="padding:18px;color:#fff;">Entity not found: ${variables.src}</div>`;

      const events = st.attributes?.events || [];
      if (!events.length) {
        return `
          <div style="padding:18px 20px;color:#fff;">
            <div style="font-size:13px;opacity:.7;letter-spacing:.12em;text-transform:uppercase;">MLB Scoreboard</div>
            <div style="margin-top:8px;font-size:18px;font-weight:700;">No games found</div>
          </div>
        `;
      }

      const fav = (variables.favorite || '').toUpperCase();
      const maxGames = Number(variables.max_games || 8);

      const getComp = (ev) => ev?.competitions?.[0] || {};
      const getStatus = (ev) => getComp(ev)?.status || ev?.status || {};
      const getStatusType = (ev) => getStatus(ev)?.type || {};
      const getDetail = (ev) => getStatusType(ev)?.shortDetail || getStatusType(ev)?.detail || 'Scheduled';
      const getState = (ev) => getStatusType(ev)?.state || 'pre';

      const teamBySide = (comp, side) =>
        (comp?.competitors || []).find(t => t.homeAway === side) || null;

      const statVal = (team, key) => {
        const s = (team?.statistics || []).find(x => x.name === key || x.abbreviation === key);
        return s?.displayValue ?? '0';
      };

      const bases = (sit) => {
        if (!sit) return '';
        const on1 = sit.onFirst;
        const on2 = sit.onSecond;
        const on3 = sit.onThird;

        const baseStyle = (on) => `
          width:11px;height:11px;transform:rotate(45deg);
          border-radius:2px;
          background:${on ? '#ffd54a' : 'rgba(255,255,255,0.14)'};
          border:1px solid ${on ? 'rgba(255,213,74,.9)' : 'rgba(255,255,255,.15)'};
          box-shadow:${on ? '0 0 8px rgba(255,213,74,.35)' : 'none'};
        `;

        return `
          <div style="display:grid;grid-template-columns:12px 12px 12px;grid-template-rows:12px 12px 12px;gap:2px;justify-content:center;align-items:center;">
            <div></div>
            <div style="${baseStyle(on2)}"></div>
            <div></div>
            <div style="${baseStyle(on3)}"></div>
            <div></div>
            <div style="${baseStyle(on1)}"></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
        `;
      };

      const outsDots = (outs) => {
        const n = Number(outs ?? 0);
        return `
          <div style="display:flex;gap:4px;align-items:center;">
            ${[0,1,2].map(i => `
              <span style="
                width:7px;height:7px;border-radius:50%;
                background:${i < n ? '#ff5d5d' : 'rgba(255,255,255,0.18)'};
                box-shadow:${i < n ? '0 0 8px rgba(255,93,93,.35)' : 'none'};
                display:inline-block;"></span>
            `).join('')}
          </div>
        `;
      };

      const inningVals = (team) => {
        const arr = new Array(9).fill('-');
        (team?.linescores || []).forEach(ls => {
          const idx = Number(ls.period) - 1;
          if (idx >= 0 && idx < 9) arr[idx] = ls.displayValue ?? ls.value ?? '-';
        });
        return arr;
      };

      const sortGames = [...events].sort((a,b) => {
        const aFav = JSON.stringify(a).includes(`"abbreviation":"${fav}"`) ? 1 : 0;
        const bFav = JSON.stringify(b).includes(`"abbreviation":"${fav}"`) ? 1 : 0;
        if (aFav !== bFav) return bFav - aFav;

        const aState = getState(a);
        const bState = getState(b);
        const rank = { in: 0, pre: 1, post: 2 };
        const ar = rank[aState] ?? 9;
        const br = rank[bState] ?? 9;
        if (ar !== br) return ar - br;

        return new Date(a.date).getTime() - new Date(b.date).getTime();
      }).slice(0, maxGames);

      const rows = sortGames.map((ev) => {
        const comp = getComp(ev);
        const state = getState(ev);
        const detail = getDetail(ev);
        const sit = comp?.situation || {};
        const away = teamBySide(comp, 'away');
        const home = teamBySide(comp, 'home');

        if (!away || !home) return '';

        const awayAbbr = away.team?.abbreviation || 'AWY';
        const homeAbbr = home.team?.abbreviation || 'HME';

        const awayName = away.team?.shortDisplayName || away.team?.name || awayAbbr;
        const homeName = home.team?.shortDisplayName || home.team?.name || homeAbbr;

        const awayLogo = away.team?.logo || '';
        const homeLogo = home.team?.logo || '';

        const awayScore = away.score ?? '-';
        const homeScore = home.score ?? '-';

        const awayHits = statVal(away, 'hits');
        const homeHits = statVal(home, 'hits');
        const awayErr = statVal(away, 'errors');
        const homeErr = statVal(home, 'errors');

        const awayColor = away.team?.color ? `#${away.team.color}` : '#9fb3c8';
        const homeColor = home.team?.color ? `#${home.team.color}` : '#9fb3c8';

        const awayLeading = Number(awayScore) > Number(homeScore);
        const homeLeading = Number(homeScore) > Number(awayScore);
        const isFav = [awayAbbr, homeAbbr].includes(fav);

        const awayInnings = inningVals(away);
        const homeInnings = inningVals(home);

        const live = state === 'in';
        const scheduled = state === 'pre';

        const badgeBg =
          live ? 'linear-gradient(90deg,#00c853,#00e676)' :
          scheduled ? 'linear-gradient(90deg,#31445f,#425a78)' :
          'linear-gradient(90deg,#6b7280,#9ca3af)';

        const badgeText = live ? detail : scheduled ? detail : 'Final';

        const networks = (comp?.broadcasts || [])
          .flatMap(b => b?.names || [])
          .filter(Boolean)
          .slice(0, 2)
          .join(' • ');

        const lsCell = (val, strong = false) => `
          <div style="
            text-align:center;
            font-size:${strong ? '13px' : '11px'};
            font-weight:${strong ? '800' : '600'};
            color:${val === '-' ? 'rgba(255,255,255,0.30)' : 'rgba(255,255,255,0.88)'};
            line-height:1;
          ">${val}</div>
        `;

        return `
          <div style="
            padding:14px 16px;
            border-top:1px solid rgba(255,255,255,0.06);
            background:${isFav ? 'linear-gradient(90deg, rgba(186,12,47,0.12), rgba(12,35,64,0.08))' : 'transparent'};
          ">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
              <div style="
                display:inline-flex;align-items:center;gap:8px;
                font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                color:#fff;padding:4px 10px;border-radius:999px;background:${badgeBg};
                box-shadow:0 0 12px rgba(0,0,0,.18);
              ">
                ${live ? '<span style="width:7px;height:7px;border-radius:50%;background:#fff;display:inline-block;"></span>' : ''}
                ${badgeText}
              </div>

              <div style="font-size:11px;color:rgba(255,255,255,0.65);text-transform:uppercase;letter-spacing:.08em;">
                ${networks}
              </div>
            </div>

            <div style="margin-top:12px;display:grid;grid-template-columns:1fr auto;gap:14px;align-items:center;">
              <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;">
                  <img src="${awayLogo}" style="width:24px;height:24px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.25));">
                  <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                    <span style="font-size:15px;font-weight:700;color:${awayLeading ? '#ffffff' : 'rgba(255,255,255,0.88)'};">${awayAbbr}</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.58);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${awayName}</span>
                  </div>
                  <div style="
                    font-size:30px;font-weight:800;line-height:1;
                    color:${awayLeading ? awayColor : 'rgba(255,255,255,0.9)'};
                    min-width:22px;text-align:right;
                  ">${awayScore}</div>
                </div>

                <div style="display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;">
                  <img src="${homeLogo}" style="width:24px;height:24px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.25));">
                  <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                    <span style="font-size:15px;font-weight:700;color:${homeLeading ? '#ffffff' : 'rgba(255,255,255,0.88)'};">${homeAbbr}</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.58);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${homeName}</span>
                  </div>
                  <div style="
                    font-size:30px;font-weight:800;line-height:1;
                    color:${homeLeading ? homeColor : 'rgba(255,255,255,0.9)'};
                    min-width:22px;text-align:right;
                  ">${homeScore}</div>
                </div>
              </div>

              <div style="
                min-width:88px;
                padding:8px 10px;
                border-radius:16px;
                background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.06);
                display:flex;
                flex-direction:column;
                gap:8px;
                align-items:center;
                justify-content:center;
              ">
                ${
                  live
                    ? `
                      ${bases(sit)}
                      ${outsDots(sit.outs)}
                      <div style="font-size:11px;color:rgba(255,255,255,0.65);">${comp?.outsText || ''}</div>
                    `
                    : `
                      <div style="font-size:11px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:.08em;">Venue</div>
                      <div style="font-size:11px;color:#fff;text-align:center;line-height:1.25;">
                        ${comp?.venue?.fullName || ''}
                      </div>
                    `
                }
              </div>
            </div>

            <div style="
              margin-top:12px;
              padding:10px 10px;
              border-radius:18px;
              background:linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
              border:1px solid rgba(255,255,255,0.06);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            ">
              <div style="
                display:grid;
                grid-template-columns: 72px repeat(9, minmax(0, 1fr)) 28px 28px 28px;
                gap:4px;
                align-items:center;
                width:100%;
              ">
                <div></div>
                ${[1,2,3,4,5,6,7,8,9].map(i => `
                  <div style="
                    text-align:center;
                    font-size:10px;
                    font-weight:600;
                    color:rgba(255,255,255,0.42);
                    line-height:1;
                  ">${i}</div>
                `).join('')}
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">R</div>
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">H</div>
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">E</div>

                <div style="
                  display:flex;
                  align-items:center;
                  gap:6px;
                  min-width:0;
                  padding:4px 2px;
                ">
                  <img src="${awayLogo}" style="width:18px;height:18px;object-fit:contain;flex:0 0 auto;">
                  <span style="
                    font-size:12px;
                    font-weight:800;
                    color:${awayLeading ? '#ffffff' : 'rgba(255,255,255,0.9)'};
                    letter-spacing:.01em;
                    white-space:nowrap;
                  ">${awayAbbr}</span>
                </div>
                ${awayInnings.map(v => lsCell(v)).join('')}
                ${lsCell(awayScore, true)}
                ${lsCell(awayHits, true)}
                ${lsCell(awayErr, true)}

                <div style="
                  display:flex;
                  align-items:center;
                  gap:6px;
                  min-width:0;
                  padding:4px 2px;
                ">
                  <img src="${homeLogo}" style="width:18px;height:18px;object-fit:contain;flex:0 0 auto;">
                  <span style="
                    font-size:12px;
                    font-weight:800;
                    color:${homeLeading ? '#ffffff' : 'rgba(255,255,255,0.9)'};
                    letter-spacing:.01em;
                    white-space:nowrap;
                  ">${homeAbbr}</span>
                </div>
                ${homeInnings.map(v => lsCell(v)).join('')}
                ${lsCell(homeScore, true)}
                ${lsCell(homeHits, true)}
                ${lsCell(homeErr, true)}
              </div>
            </div>
          </div>
        `;
      }).join('');

      return `
        <div style="width:100%;color:#fff;">
          <div style="
            padding:16px 18px 14px 18px;
            background:linear-gradient(90deg, rgba(8,18,36,0.98), rgba(18,34,58,0.94));
            border-bottom:1px solid rgba(255,255,255,0.06);
          ">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="
                  width:42px;height:42px;border-radius:14px;
                  display:flex;align-items:center;justify-content:center;
                  background:linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
                  border:1px solid rgba(255,255,255,0.08);
                  font-size:22px;
                ">⚾</div>
                <div>
                  <div style="font-size:12px;opacity:.62;letter-spacing:.14em;text-transform:uppercase;">Spring Training</div>
                  <div style="font-size:22px;font-weight:800;line-height:1.1;">MLB Scoreboard</div>
                </div>
              </div>

              <div style="
                padding:6px 10px;border-radius:999px;
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(255,255,255,0.08);
                font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
              ">
                ${events.length} Games
              </div>
            </div>
          </div>

          <div>
            ${rows}
          </div>
        </div>
      `;
    ]]]
```

</details>

---

## 4. MLB Old School Poster

A vintage baseball poster-style scoreboard designed to look like a classic printed game-day graphic. It highlights one matchup with oversized team abbreviations, team logos, big center scores, a 9-inning linescore, and win/loss result boxes when the game is final.
This card is best used as a featured MLB card for your favorite team or the main game you want displayed on a dashboard. It reads from the MLB raw scoreboard sensor and automatically picks your favorite team when available.


Set your favorite team here:

```yaml
variables:
  favorite: ATL
```

<img  width="340" alt="image" src="https://github.com/user-attachments/assets/22a61506-a14b-4f44-bb3f-9fc2f93cc60d" />


<details>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card
entity: sensor.espn_mlb_scoreboard_raw
show_name: false
show_icon: false
show_state: false
triggers_update:
  - sensor.espn_mlb_scoreboard_raw
variables:
  src: sensor.espn_mlb_scoreboard_raw
  favorite: ATL
  max_games: 8
styles:
  card:
    - padding: 0
    - border-radius: 24px
    - overflow: hidden
    - background: linear-gradient(180deg, rgba(8,12,20,0.98), rgba(14,20,32,0.96))
    - border: 1px solid rgba(255,255,255,0.08)
    - box-shadow: 0 12px 30px rgba(0,0,0,0.35)
  grid:
    - grid-template-areas: "\"main\""
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
  custom_fields:
    main:
      - width: 100%
custom_fields:
  main: |
    [[[
      const st = states[variables.src];
      if (!st) return `<div style="padding:18px;color:#fff;">Entity not found: ${variables.src}</div>`;

      const events = st.attributes?.events || [];
      if (!events.length) {
        return `
          <div style="padding:18px 20px;color:#fff;">
            <div style="font-size:13px;opacity:.7;letter-spacing:.12em;text-transform:uppercase;">MLB Scoreboard</div>
            <div style="margin-top:8px;font-size:18px;font-weight:700;">No games found</div>
          </div>
        `;
      }

      const fav = (variables.favorite || '').toUpperCase();
      const maxGames = Number(variables.max_games || 8);

      const getComp = (ev) => ev?.competitions?.[0] || {};
      const getStatus = (ev) => getComp(ev)?.status || ev?.status || {};
      const getStatusType = (ev) => getStatus(ev)?.type || {};
      const getDetail = (ev) => getStatusType(ev)?.shortDetail || getStatusType(ev)?.detail || 'Scheduled';
      const getState = (ev) => getStatusType(ev)?.state || 'pre';

      const teamBySide = (comp, side) =>
        (comp?.competitors || []).find(t => t.homeAway === side) || null;

      const statVal = (team, key) => {
        const s = (team?.statistics || []).find(x => x.name === key || x.abbreviation === key);
        return s?.displayValue ?? '0';
      };

      const bases = (sit) => {
        if (!sit) return '';
        const on1 = sit.onFirst;
        const on2 = sit.onSecond;
        const on3 = sit.onThird;

        const baseStyle = (on) => `
          width:11px;height:11px;transform:rotate(45deg);
          border-radius:2px;
          background:${on ? '#ffd54a' : 'rgba(255,255,255,0.14)'};
          border:1px solid ${on ? 'rgba(255,213,74,.9)' : 'rgba(255,255,255,.15)'};
          box-shadow:${on ? '0 0 8px rgba(255,213,74,.35)' : 'none'};
        `;

        return `
          <div style="display:grid;grid-template-columns:12px 12px 12px;grid-template-rows:12px 12px 12px;gap:2px;justify-content:center;align-items:center;">
            <div></div>
            <div style="${baseStyle(on2)}"></div>
            <div></div>
            <div style="${baseStyle(on3)}"></div>
            <div></div>
            <div style="${baseStyle(on1)}"></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
        `;
      };

      const outsDots = (outs) => {
        const n = Number(outs ?? 0);
        return `
          <div style="display:flex;gap:4px;align-items:center;">
            ${[0,1,2].map(i => `
              <span style="
                width:7px;height:7px;border-radius:50%;
                background:${i < n ? '#ff5d5d' : 'rgba(255,255,255,0.18)'};
                box-shadow:${i < n ? '0 0 8px rgba(255,93,93,.35)' : 'none'};
                display:inline-block;"></span>
            `).join('')}
          </div>
        `;
      };

      const inningVals = (team) => {
        const arr = new Array(9).fill('-');
        (team?.linescores || []).forEach(ls => {
          const idx = Number(ls.period) - 1;
          if (idx >= 0 && idx < 9) arr[idx] = ls.displayValue ?? ls.value ?? '-';
        });
        return arr;
      };

      const sortGames = [...events].sort((a,b) => {
        const aFav = JSON.stringify(a).includes(`"abbreviation":"${fav}"`) ? 1 : 0;
        const bFav = JSON.stringify(b).includes(`"abbreviation":"${fav}"`) ? 1 : 0;
        if (aFav !== bFav) return bFav - aFav;

        const aState = getState(a);
        const bState = getState(b);
        const rank = { in: 0, pre: 1, post: 2 };
        const ar = rank[aState] ?? 9;
        const br = rank[bState] ?? 9;
        if (ar !== br) return ar - br;

        return new Date(a.date).getTime() - new Date(b.date).getTime();
      }).slice(0, maxGames);

      const rows = sortGames.map((ev) => {
        const comp = getComp(ev);
        const state = getState(ev);
        const detail = getDetail(ev);
        const sit = comp?.situation || {};
        const away = teamBySide(comp, 'away');
        const home = teamBySide(comp, 'home');

        if (!away || !home) return '';

        const awayAbbr = away.team?.abbreviation || 'AWY';
        const homeAbbr = home.team?.abbreviation || 'HME';

        const awayName = away.team?.shortDisplayName || away.team?.name || awayAbbr;
        const homeName = home.team?.shortDisplayName || home.team?.name || homeAbbr;

        const awayLogo = away.team?.logo || '';
        const homeLogo = home.team?.logo || '';

        const awayScore = away.score ?? '-';
        const homeScore = home.score ?? '-';

        const awayHits = statVal(away, 'hits');
        const homeHits = statVal(home, 'hits');
        const awayErr = statVal(away, 'errors');
        const homeErr = statVal(home, 'errors');

        const awayColor = away.team?.color ? `#${away.team.color}` : '#9fb3c8';
        const homeColor = home.team?.color ? `#${home.team.color}` : '#9fb3c8';

        const awayLeading = Number(awayScore) > Number(homeScore);
        const homeLeading = Number(homeScore) > Number(awayScore);
        const isFav = [awayAbbr, homeAbbr].includes(fav);

        const awayInnings = inningVals(away);
        const homeInnings = inningVals(home);

        const live = state === 'in';
        const scheduled = state === 'pre';

        const badgeBg =
          live ? 'linear-gradient(90deg,#00c853,#00e676)' :
          scheduled ? 'linear-gradient(90deg,#31445f,#425a78)' :
          'linear-gradient(90deg,#6b7280,#9ca3af)';

        const badgeText = live ? detail : scheduled ? detail : 'Final';

        const networks = (comp?.broadcasts || [])
          .flatMap(b => b?.names || [])
          .filter(Boolean)
          .slice(0, 2)
          .join(' • ');

        const lsCell = (val, strong = false) => `
          <div style="
            text-align:center;
            font-size:${strong ? '13px' : '11px'};
            font-weight:${strong ? '800' : '600'};
            color:${val === '-' ? 'rgba(255,255,255,0.30)' : 'rgba(255,255,255,0.88)'};
            line-height:1;
          ">${val}</div>
        `;

        return `
          <div style="
            padding:14px 16px;
            border-top:1px solid rgba(255,255,255,0.06);
            background:${isFav ? 'linear-gradient(90deg, rgba(186,12,47,0.12), rgba(12,35,64,0.08))' : 'transparent'};
          ">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
              <div style="
                display:inline-flex;align-items:center;gap:8px;
                font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                color:#fff;padding:4px 10px;border-radius:999px;background:${badgeBg};
                box-shadow:0 0 12px rgba(0,0,0,.18);
              ">
                ${live ? '<span style="width:7px;height:7px;border-radius:50%;background:#fff;display:inline-block;"></span>' : ''}
                ${badgeText}
              </div>

              <div style="font-size:11px;color:rgba(255,255,255,0.65);text-transform:uppercase;letter-spacing:.08em;">
                ${networks}
              </div>
            </div>

            <div style="margin-top:12px;display:grid;grid-template-columns:1fr auto;gap:14px;align-items:center;">
              <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;">
                  <img src="${awayLogo}" style="width:24px;height:24px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.25));">
                  <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                    <span style="font-size:15px;font-weight:700;color:${awayLeading ? '#ffffff' : 'rgba(255,255,255,0.88)'};">${awayAbbr}</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.58);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${awayName}</span>
                  </div>
                  <div style="
                    font-size:30px;font-weight:800;line-height:1;
                    color:${awayLeading ? awayColor : 'rgba(255,255,255,0.9)'};
                    min-width:22px;text-align:right;
                  ">${awayScore}</div>
                </div>

                <div style="display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;">
                  <img src="${homeLogo}" style="width:24px;height:24px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.25));">
                  <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                    <span style="font-size:15px;font-weight:700;color:${homeLeading ? '#ffffff' : 'rgba(255,255,255,0.88)'};">${homeAbbr}</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.58);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${homeName}</span>
                  </div>
                  <div style="
                    font-size:30px;font-weight:800;line-height:1;
                    color:${homeLeading ? homeColor : 'rgba(255,255,255,0.9)'};
                    min-width:22px;text-align:right;
                  ">${homeScore}</div>
                </div>
              </div>

              <div style="
                min-width:88px;
                padding:8px 10px;
                border-radius:16px;
                background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.06);
                display:flex;
                flex-direction:column;
                gap:8px;
                align-items:center;
                justify-content:center;
              ">
                ${
                  live
                    ? `
                      ${bases(sit)}
                      ${outsDots(sit.outs)}
                      <div style="font-size:11px;color:rgba(255,255,255,0.65);">${comp?.outsText || ''}</div>
                    `
                    : `
                      <div style="font-size:11px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:.08em;">Venue</div>
                      <div style="font-size:11px;color:#fff;text-align:center;line-height:1.25;">
                        ${comp?.venue?.fullName || ''}
                      </div>
                    `
                }
              </div>
            </div>

            <div style="
              margin-top:12px;
              padding:10px 10px;
              border-radius:18px;
              background:linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
              border:1px solid rgba(255,255,255,0.06);
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            ">
              <div style="
                display:grid;
                grid-template-columns: 72px repeat(9, minmax(0, 1fr)) 28px 28px 28px;
                gap:4px;
                align-items:center;
                width:100%;
              ">
                <div></div>
                ${[1,2,3,4,5,6,7,8,9].map(i => `
                  <div style="
                    text-align:center;
                    font-size:10px;
                    font-weight:600;
                    color:rgba(255,255,255,0.42);
                    line-height:1;
                  ">${i}</div>
                `).join('')}
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">R</div>
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">H</div>
                <div style="text-align:center;font-size:10px;font-weight:800;color:rgba(255,255,255,0.65);line-height:1;">E</div>

                <div style="
                  display:flex;
                  align-items:center;
                  gap:6px;
                  min-width:0;
                  padding:4px 2px;
                ">
                  <img src="${awayLogo}" style="width:18px;height:18px;object-fit:contain;flex:0 0 auto;">
                  <span style="
                    font-size:12px;
                    font-weight:800;
                    color:${awayLeading ? '#ffffff' : 'rgba(255,255,255,0.9)'};
                    letter-spacing:.01em;
                    white-space:nowrap;
                  ">${awayAbbr}</span>
                </div>
                ${awayInnings.map(v => lsCell(v)).join('')}
                ${lsCell(awayScore, true)}
                ${lsCell(awayHits, true)}
                ${lsCell(awayErr, true)}

                <div style="
                  display:flex;
                  align-items:center;
                  gap:6px;
                  min-width:0;
                  padding:4px 2px;
                ">
                  <img src="${homeLogo}" style="width:18px;height:18px;object-fit:contain;flex:0 0 auto;">
                  <span style="
                    font-size:12px;
                    font-weight:800;
                    color:${homeLeading ? '#ffffff' : 'rgba(255,255,255,0.9)'};
                    letter-spacing:.01em;
                    white-space:nowrap;
                  ">${homeAbbr}</span>
                </div>
                ${homeInnings.map(v => lsCell(v)).join('')}
                ${lsCell(homeScore, true)}
                ${lsCell(homeHits, true)}
                ${lsCell(homeErr, true)}
              </div>
            </div>
          </div>
        `;
      }).join('');

      return `
        <div style="width:100%;color:#fff;">
          <div style="
            padding:16px 18px 14px 18px;
            background:linear-gradient(90deg, rgba(8,18,36,0.98), rgba(18,34,58,0.94));
            border-bottom:1px solid rgba(255,255,255,0.06);
          ">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="
                  width:42px;height:42px;border-radius:14px;
                  display:flex;align-items:center;justify-content:center;
                  background:linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
                  border:1px solid rgba(255,255,255,0.08);
                  font-size:22px;
                ">⚾</div>
                <div>
                  <div style="font-size:12px;opacity:.62;letter-spacing:.14em;text-transform:uppercase;">Spring Training</div>
                  <div style="font-size:22px;font-weight:800;line-height:1.1;">MLB Scoreboard</div>
                </div>
              </div>

              <div style="
                padding:6px 10px;border-radius:999px;
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(255,255,255,0.08);
                font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
              ">
                ${events.length} Games
              </div>
            </div>
          </div>

          <div>
            ${rows}
          </div>
        </div>
      `;
    ]]]
```

</details>

---

## 5. Game / team stats starter

A quick entity card for testing raw scoreboard data and next-game helper sensors.

<details>
<summary>Copy YAML</summary>

```yaml
type: entities
title: Game / Team Stats (example)
entities:
  - entity: sensor.espn_mlb_scoreboard_raw
    name: Raw scoreboard
  - entity: sensor.espn_mlb_next_game
    name: Next game
```

</details>

---

## 🛠️ Quick Troubleshooting

### No games found

Check that MLB is enabled in the Sports Ticker integration, then open **Developer Tools → States** and confirm this sensor has an `attributes.events` list:

```yaml
sensor.espn_mlb_scoreboard_raw
```

### Logos do not show

The examples prefer the logo URL from the scoreboard feed. If a logo is missing, the ticker falls back to ESPN CDN team-logo URLs for common MLB abbreviations.

### Favorite team is not highlighted

Make sure the favorite abbreviation matches the ESPN abbreviation exactly. For the Atlanta Braves, use:

```yaml
fav: ATL
```

or, in the gamecast card:

```yaml
favorite: ATL
```

### ButtonCardJSTemplateError: Identifier has already been declared

Do not paste multiple JavaScript templates into the same button-card field unless each variable name is unique. Each example above is meant to be used as its own card.

---

## Suggested dashboard stack

For a full MLB page, stack the examples like this:

1. **ESPN-style MLB ticker** at the top
2. **What’s on tonight guide** below it
3. **MLB Gamecast card** for deeper live-game detail
4. **Standings/stats starters** while you build out richer data cards

