<!-- support_badges_start -->
[![PayPal](https://img.shields.io/badge/PayPal-Support%20Me-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/KevinHughesPhoto)
<!-- support_badges_end -->


# 🏟️ Home Assistant Sports Ticker

> A Home Assistant integration that pulls live sports data (scores, status, schedules, standings, and more) and exposes it as sensors — perfect for building ESPN-style dashboard cards and tickers in Lovelace.

---

## ✨ What this integration does

- **Live scoreboard sensors** per league (JSON “raw” + derived summary sensors)
- **Game day helpers** (what’s on tonight / next game)
- **Team-focused views** (favorite team filters, opponent, record, etc.)
- Works great with:
  - `custom:button-card`
  - `card-mod`
  - Mushroom cards / sections dashboards

---

## 📌 Quick Links

| 📂 Category | 📝 Description | 🔗 Link |
| :--- | :--- | :---: |
| **🏠 Home** | This README | **You are here** |
| **⚙️ Installation** | HACS / manual setup | [Jump](#-installation) |
| **🧠 Sensors** | What entities you get | [Jump](#-entities--sensors) |
| **🧩 Examples** | Copy/paste cards | [Jump](#-lovelace-examples) |
| **🛠️ Troubleshooting** | Common issues | [Jump](#-troubleshooting) |

---

> [!NOTE]
> If you’re using **Sections** view type, some cards may look “compressed.”
> Try setting `rows: 1.5` on the card’s `grid_options` if needed.
>
> ```yaml
> grid_options:
>   rows: 1.5
> ```

> [!TIP]
> Want to force a custom card background / text colors (light-mode friendly)?
> Add the following to your `ha-card` styles:
>
> ```yaml
> background: #1C1C1C !important;
> --card-primary-color: white !important;
> --card-secondary-color: white !important;
> ```

---

## ✅ Supported leagues

This integration is designed around **ESPN-style** endpoints and supports multiple leagues.

Common setups include:
- **MLB**
- **NFL**
- **NBA**
- **NHL**
- **PGA Tour**
- **NASCAR**

> If your fork/build supports additional leagues, add them here.

---

## 📦 Installation

### Option A — HACS (recommended)

1. Open **HACS** → **Integrations**
2. Click **⋮** → **Custom repositories**
3. Add your repo URL, category **Integration**
4. Install **Sports Ticker**
5. Restart Home Assistant

### Option B — Manual

1. Copy the `custom_components/sports_ticker/` folder into:
   - `config/custom_components/sports_ticker/`
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & services → Add integration**

---

## ⚙️ Configuration

After installing:

1. Go to **Settings → Devices & services**
2. Click **Add Integration**
3. Search for **Sports Ticker**
4. Choose:
   - leagues you want enabled
   - poll interval
   - ticker speed/theme (if provided by your version)

---

## 🧠 Entities / Sensors

> Names vary slightly depending on your config flow options.
> Below is the typical pattern used by this integration.

### Scoreboard “raw” sensors (JSON)

These are the “source of truth” sensors used by Lovelace templates:

- `sensor.espn_mlb_scoreboard_raw`
- `sensor.espn_nfl_scoreboard_raw`
- `sensor.espn_nba_scoreboard_raw`
- `sensor.espn_nhl_scoreboard_raw`
- `sensor.espn_pga_scoreboard_raw`
- `sensor.espn_nascar_scoreboard_raw`

They contain JSON attributes like:
- events list (games)
- status (pre / in / final)
- competitors/teams
- scores
- time/period/inning
- broadcast / venue (when available)

### Helper / derived sensors (optional)

Depending on your version, you may also see things like:
- `sensor.sports_ticker_<league>_whats_on_tonight`
- `sensor.sports_ticker_<league>_next_game`
- `sensor.sports_ticker_<league>_standings_*`
- `sensor.sports_ticker_<league>_team_stats_*`

> If you don’t see these, you can still build everything from the `*_raw` sensors.

---

## 🧩 Lovelace examples

### 1) ESPN-style Ticker card (button-card)
![mlbticker](https://github.com/user-attachments/assets/a2450782-197d-4783-b777-bc5007df095f)

<details>
  
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

      // ---- logo helpers (prefer feed logo; fallback ESPN CDN for NBA/MLB/NFL/MLB/...) ----
      const leagueFromSport = (s) => {
        const map = { NBA:'nba', WNBA:'wnba', MLB:'mlb', NFL:'nfl', MLB:'nba' };
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



## 🛠️ Troubleshooting

### “No games found” but you know games exist
- Check the league is enabled in the integration options
- Confirm the sensor has updated recently
- Open the raw sensor in **Developer Tools → States** and verify `attributes.events` exists

### `ButtonCardJSTemplateError: Identifier 'html' has already been declared`
If you copy/paste multiple button-card templates, avoid re-declaring `const html = ...` in the same scope.  
Use unique variable names or inline returns.

### Preseason vs regular season
Some leagues use a `season.type` value in the payload. If your cards need preseason,
read from the event’s `season.type` / `season.slug` and prefer the latest event where appropriate.

---

## 🗺️ Roadmap

- [ ] More derived sensors (standings, team stats, leaderboards)
- [ ] Built-in “ticker” card templates
- [ ] Better caching & rate limiting
- [ ] League expansion

---


## 🧾 Credits

- Data powered by public sports endpoints used by ESPN-style scoreboards
- Home Assistant community for the ecosystem & inspiration

---
