### Ticker sensors created
- sensor.espn_nfl_ticker (attribute: ticker)
- sensor.espn_mlb_ticker (attribute: ticker)
...
---

## Lovelace ticker card example (Button Card)

This is the dashboard card style used in my setup. It renders a scrolling “tile” ticker using the raw scoreboard sensor’s `events` attribute.

### MLB example

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
      const sport = variables.sport || 'MLB';
      const sensorId = variables.sensor || 'sensor.espn_mlb_scoreboard_raw';

      const raw = states[sensorId];
      const evRaw = raw?.attributes?.events || [];

      // ✅ Sort: LIVE first, then UPCOMING, then FINAL (stable within each group by start time)
      const rankState = (st) => (st === 'in' ? 0 : (st === 'pre' ? 1 : 2));
      const ev = [...evRaw].sort((a,b) => {
        const ra = rankState(a?.status?.type?.state ?? '');
        const rb = rankState(b?.status?.type?.state ?? '');
        if (ra !== rb) return ra - rb;

        const ta = Date.parse(a?.date ?? '') || 0;
        const tb = Date.parse(b?.date ?? '') || 0;
        return ta - tb;
      });

      // ---- logo helpers (prefer feed logo; fallback ESPN CDN for NBA/MLB/NFL/NHL/...) ----
      const leagueFromSport = (s) => {
        const map = { NBA:'nba', WNBA:'wnba', MLB:'mlb', NFL:'nfl', NHL:'nhl' };
        return map[s] || null;
      };

      const mlbSlug = (abbr) => {
        const map = { ARI:'ari', KCR:'kc', CHW:'cws', SFG:'sf', SDP:'sd', TBR:'tb' };
        return (map[abbr] || abbr || '').toLowerCase();
      };
      const simpleSlug = (abbr) => (abbr || '').toLowerCase();

      const slugFor = (abbr) => {
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
          const inn = parseMLBHalf(stShort);
          return `<span class="pill live">LIVE</span><span class="pill meta">${inn ? inn.label : (stShort || 'In Progress')}</span>`;
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
          <div class="bar" style="--dur:45s">
            <div class="wrap">
              <div class="marquee">
                <div class="tile">
                  <div class="top"><span class="pill upcoming">NO GAMES</span><span class="pill meta">${sport}</span></div>
                  <div class="teams one"><div class="row"><span class="abbr">No ${sport} games today</span></div></div>
                </div>
              </div>
            </div>
          </div>`;
      }

      // Build tiles + a plain-text string for duration calculation
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

        // winner dot (leader for live; winner for final)
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

      // duration scales with content length (keeps speed consistent)
      const textForSpeed = speedTextParts.join(' • ');
      const seconds = Math.round(textForSpeed.length / 12); // tweak divisor: smaller=slower, larger=faster
      const dur = Math.max(22, Math.min(90, seconds)) + 's';

      return `
        <div class="bar" style="--dur:${dur}">
          <div class="wrap">
            <div class="marquee">${tiles.join(`<div class="sep"></div>`)}</div>
          </div>
        </div>`;
    ]]]
card_mod:
  style: |
    .bar{
      min-height: 60px;
      background: rgba(245,245,245,0.98);
      display:flex;
      align-items:center;
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
      border-right:1px solid rgba(0,0,0,0.10);
      margin:0 2px;
    }
    .top{ display:flex; gap:6px; align-items:center; }

    .pill{
      font-size:10px;
      font-weight:900;
      padding:2px 7px;
      border-radius:999px;
      border:1px solid rgba(0,0,0,0.12);
      color: rgba(0,0,0,0.78);
      background: rgba(255,255,255,0.92);
      letter-spacing:.4px;
    }
    .pill.live{
      background: rgba(208,0,0,0.92);
      border-color: rgba(208,0,0,0.92);
      color:#fff;
    }
    .pill.meta{ color: rgba(0,0,0,0.58); }

    .teams{ display:flex; flex-direction:column; gap:3px; }
    .row{ display:flex; align-items:center; gap:8px; line-height:1.05; }

    .wdot{
      width:8px;
      height:8px;
      border-radius:50%;
      background: rgba(0,0,0,0.10);
      border: 1px solid rgba(0,0,0,0.12);
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
      color: rgba(0,0,0,0.82);
      min-width:36px;
      letter-spacing:.3px;
    }
    .score{
      margin-left:auto;
      font-size:12px;
      font-weight:1000;
      color: rgba(0,0,0,0.82);
    }
```

> To use a different league, change `variables.sport` and `variables.sensor` (e.g. `NFL` + `sensor.espn_nfl_scoreboard_raw`).

---

## Troubleshooting note (development)

If you see an error like:

- `AttributeError: 'NoneType' object has no attribute 'isEnabledFor'`

It means the coordinator was created with `logger=None`. Ensure the `DataUpdateCoordinator` is initialized with a real logger (e.g. `logger=LOGGER`).

```python
import logging
LOGGER = logging.getLogger(__name__)

super().__init__(
  hass=hass,
  logger=LOGGER,
  name=DOMAIN,
  update_interval=timedelta(seconds=poll),
)
```
