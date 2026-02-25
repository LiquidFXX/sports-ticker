### \### Ticker sensors created

### \- sensor.espn\_nfl\_ticker (attribute: ticker)

### \- sensor.espn\_mlb\_ticker (attribute: ticker)

### ...

### ---

### 

### \## Lovelace ticker card example (Button Card)

### 

### This is the dashboard card style used in my setup. It renders a scrolling “tile” ticker using the raw scoreboard sensor’s `events` attribute.

### 

### \### MLB example

### 

### ```yaml

### type: custom:button-card

### show\_name: false

### show\_state: false

### variables:

### &nbsp; sport: MLB

### &nbsp; sensor: sensor.espn\_mlb\_scoreboard\_raw

### styles:

### &nbsp; card:

### &nbsp;   - border-radius: 14px

### &nbsp;   - overflow: hidden

### &nbsp;   - padding: 0px

### &nbsp;   - background: rgba(255,255,255,0.92)

### &nbsp;   - border: 1px solid rgba(0,0,0,0.10)

### &nbsp;   - box-shadow: 0 10px 22px rgba(0,0,0,0.18)

### &nbsp; custom\_fields:

### &nbsp;   ticker:

### &nbsp;     - padding: 0px

### custom\_fields:

### &nbsp; ticker: |

### &nbsp;   \[\[\[

### &nbsp;     const sport = variables.sport || 'MLB';

### &nbsp;     const sensorId = variables.sensor || 'sensor.espn\_mlb\_scoreboard\_raw';

### 

### &nbsp;     const raw = states\[sensorId];

### &nbsp;     const evRaw = raw?.attributes?.events || \[];

### 

### &nbsp;     // ✅ Sort: LIVE first, then UPCOMING, then FINAL (stable within each group by start time)

### &nbsp;     const rankState = (st) => (st === 'in' ? 0 : (st === 'pre' ? 1 : 2));

### &nbsp;     const ev = \[...evRaw].sort((a,b) => {

### &nbsp;       const ra = rankState(a?.status?.type?.state ?? '');

### &nbsp;       const rb = rankState(b?.status?.type?.state ?? '');

### &nbsp;       if (ra !== rb) return ra - rb;

### 

### &nbsp;       const ta = Date.parse(a?.date ?? '') || 0;

### &nbsp;       const tb = Date.parse(b?.date ?? '') || 0;

### &nbsp;       return ta - tb;

### &nbsp;     });

### 

### &nbsp;     // ---- logo helpers (prefer feed logo; fallback ESPN CDN for NBA/MLB/NFL/NHL/...) ----

### &nbsp;     const leagueFromSport = (s) => {

### &nbsp;       const map = { NBA:'nba', WNBA:'wnba', MLB:'mlb', NFL:'nfl', NHL:'nhl' };

### &nbsp;       return map\[s] || null;

### &nbsp;     };

### 

### &nbsp;     const mlbSlug = (abbr) => {

### &nbsp;       const map = { ARI:'ari', KCR:'kc', CHW:'cws', SFG:'sf', SDP:'sd', TBR:'tb' };

### &nbsp;       return (map\[abbr] || abbr || '').toLowerCase();

### &nbsp;     };

### &nbsp;     const simpleSlug = (abbr) => (abbr || '').toLowerCase();

### 

### &nbsp;     const slugFor = (abbr) => {

### &nbsp;       if (sport === 'MLB') return mlbSlug(abbr);

### &nbsp;       return simpleSlug(abbr);

### &nbsp;     };

### 

### &nbsp;     const logoUrl = (teamObj, abbr) => {

### &nbsp;       const direct = teamObj?.logo || teamObj?.logos?.\[0]?.href || teamObj?.logos?.\[0]?.url;

### &nbsp;       if (direct) return direct;

### 

### &nbsp;       const league = leagueFromSport(sport);

### &nbsp;       if (!league) return '';

### &nbsp;       const slug = slugFor(abbr);

### &nbsp;       return slug ? `https://a.espncdn.com/i/teamlogos/${league}/500/${slug}.png` : '';

### &nbsp;     };

### 

### &nbsp;     // ---- status chips ----

### &nbsp;     const parseMLBHalf = (shortDetail) => {

### &nbsp;       const s = (shortDetail || '').trim();

### &nbsp;       const m = s.match(/^(Top|Bot|Bottom|Mid|End)\\s+(\\d+)(?:st|nd|rd|th)?/i);

### &nbsp;       if (!m) return null;

### &nbsp;       let half = m\[1].toLowerCase();

### &nbsp;       const inning = m\[2];

### &nbsp;       if (half === 'bottom') half = 'bot';

### &nbsp;       const isTop = half === 'top';

### &nbsp;       return { label: isTop ? `▲ Top ${inning}` : `▼ Bot ${inning}` };

### &nbsp;     };

### 

### &nbsp;     const chips = (stState, stShort, when) => {

### &nbsp;       if (stState === 'in') {

### &nbsp;         const inn = parseMLBHalf(stShort);

### &nbsp;         return `<span class="pill live">LIVE</span><span class="pill meta">${inn ? inn.label : (stShort || 'In Progress')}</span>`;

### &nbsp;       }

### &nbsp;       if (stState === 'post') {

### &nbsp;         const txt = /final/i.test(stShort) ? stShort : 'FINAL';

### &nbsp;         return `<span class="pill final">${txt}</span>`;

### &nbsp;       }

### &nbsp;       return `<span class="pill upcoming">UPCOMING</span><span class="pill meta">${when}</span>`;

### &nbsp;     };

### 

### &nbsp;     const num = (v) => {

### &nbsp;       const n = Number.parseFloat(v);

### &nbsp;       return Number.isFinite(n) ? n : null;

### &nbsp;     };

### 

### &nbsp;     if (!ev.length) {

### &nbsp;       return `

### &nbsp;         <div class="bar" style="--dur:45s">

### &nbsp;           <div class="wrap">

### &nbsp;             <div class="marquee">

### &nbsp;               <div class="tile">

### &nbsp;                 <div class="top"><span class="pill upcoming">NO GAMES</span><span class="pill meta">${sport}</span></div>

### &nbsp;                 <div class="teams one"><div class="row"><span class="abbr">No ${sport} games today</span></div></div>

### &nbsp;               </div>

### &nbsp;             </div>

### &nbsp;           </div>

### &nbsp;         </div>`;

### &nbsp;     }

### 

### &nbsp;     // Build tiles + a plain-text string for duration calculation

### &nbsp;     const tiles = \[];

### &nbsp;     const speedTextParts = \[];

### 

### &nbsp;     ev.forEach(e => {

### &nbsp;       const comp = e?.competitions?.\[0];

### &nbsp;       const teams = comp?.competitors || \[];

### &nbsp;       const away = teams.find(t => t.homeAway === 'away');

### &nbsp;       const home = teams.find(t => t.homeAway === 'home');

### 

### &nbsp;       const aAbbr = away?.team?.abbreviation ?? (away?.team?.shortDisplayName ?? 'AWY');

### &nbsp;       const hAbbr = home?.team?.abbreviation ?? (home?.team?.shortDisplayName ?? 'HOM');

### 

### &nbsp;       const aScoreRaw = away?.score ?? '';

### &nbsp;       const hScoreRaw = home?.score ?? '';

### &nbsp;       const aScore = num(aScoreRaw);

### &nbsp;       const hScore = num(hScoreRaw);

### 

### &nbsp;       const stState = e?.status?.type?.state ?? '';

### &nbsp;       const stShort = e?.status?.type?.shortDetail ?? '';

### &nbsp;       const when = new Date(e.date).toLocaleTimeString(\[], { hour: 'numeric', minute: '2-digit' });

### 

### &nbsp;       const aLogo = logoUrl(away?.team, aAbbr);

### &nbsp;       const hLogo = logoUrl(home?.team, hAbbr);

### 

### &nbsp;       const showScores = (stState !== 'pre');

### 

### &nbsp;       // winner dot (leader for live; winner for final)

### &nbsp;       let awayWin = false, homeWin = false;

### &nbsp;       if (showScores \&\& aScore != null \&\& hScore != null \&\& aScore !== hScore) {

### &nbsp;         awayWin = aScore > hScore;

### &nbsp;         homeWin = hScore > aScore;

### &nbsp;       }

### 

### &nbsp;       speedTextParts.push(`${aAbbr} ${aScoreRaw} ${hAbbr} ${hScoreRaw} ${stShort}`);

### 

### &nbsp;       tiles.push(`

### &nbsp;         <div class="tile">

### &nbsp;           <div class="top">${chips(stState, stShort, when)}</div>

### &nbsp;           <div class="teams">

### &nbsp;             <div class="row">

### &nbsp;               <span class="wdot ${awayWin ? 'on' : ''}"></span>

### &nbsp;               <img class="tlogo" src="${aLogo}" alt="${aAbbr}" onerror="this.style.display='none'">

### &nbsp;               <span class="abbr">${aAbbr}</span>

### &nbsp;               <span class="score">${showScores ? aScoreRaw : ''}</span>

### &nbsp;             </div>

### &nbsp;             <div class="row">

### &nbsp;               <span class="wdot ${homeWin ? 'on' : ''}"></span>

### &nbsp;               <img class="tlogo" src="${hLogo}" alt="${hAbbr}" onerror="this.style.display='none'">

### &nbsp;               <span class="abbr">${hAbbr}</span>

### &nbsp;               <span class="score">${showScores ? hScoreRaw : ''}</span>

### &nbsp;             </div>

### &nbsp;           </div>

### &nbsp;         </div>

### &nbsp;       `);

### &nbsp;     });

### 

### &nbsp;     // duration scales with content length (keeps speed consistent)

### &nbsp;     const textForSpeed = speedTextParts.join(' • ');

### &nbsp;     const seconds = Math.round(textForSpeed.length / 12); // tweak divisor: smaller=slower, larger=faster

### &nbsp;     const dur = Math.max(22, Math.min(90, seconds)) + 's';

### 

### &nbsp;     return `

### &nbsp;       <div class="bar" style="--dur:${dur}">

### &nbsp;         <div class="wrap">

### &nbsp;           <div class="marquee">${tiles.join(`<div class="sep"></div>`)}</div>

### &nbsp;         </div>

### &nbsp;       </div>`;

### &nbsp;   ]]]

### card\_mod:

### &nbsp; style: |

### &nbsp;   .bar{

### &nbsp;     min-height: 60px;

### &nbsp;     background: rgba(245,245,245,0.98);

### &nbsp;     display:flex;

### &nbsp;     align-items:center;

### &nbsp;   }

### &nbsp;   .wrap{

### &nbsp;     overflow:hidden;

### &nbsp;     width:100%;

### &nbsp;     -webkit-mask-image: linear-gradient(90deg, transparent 0%, black 7%, black 93%, transparent 100%);

### &nbsp;             mask-image: linear-gradient(90deg, transparent 0%, black 7%, black 93%, transparent 100%);

### &nbsp;   }

### &nbsp;   .marquee{

### &nbsp;     display:inline-flex;

### &nbsp;     align-items:center;

### &nbsp;     white-space:nowrap;

### &nbsp;     padding-left:100%;

### &nbsp;     animation: espn-marquee var(--dur, 34s) linear infinite;

### &nbsp;     will-change: transform;

### &nbsp;   }

### &nbsp;   ha-card:hover .marquee{ animation-play-state: paused; }

### 

### &nbsp;   @keyframes espn-marquee{

### &nbsp;     0%{ transform: translateX(0%); }

### &nbsp;     100%{ transform: translateX(-100%); }

### &nbsp;   }

### 

### &nbsp;   .tile{

### &nbsp;     min-width:190px;

### &nbsp;     padding:6px 10px;

### &nbsp;     display:flex;

### &nbsp;     flex-direction:column;

### &nbsp;     gap:4px;

### &nbsp;   }

### &nbsp;   .sep{

### &nbsp;     height:44px;

### &nbsp;     border-right:1px solid rgba(0,0,0,0.10);

### &nbsp;     margin:0 2px;

### &nbsp;   }

### &nbsp;   .top{ display:flex; gap:6px; align-items:center; }

### 

### &nbsp;   .pill{

### &nbsp;     font-size:10px;

### &nbsp;     font-weight:900;

### &nbsp;     padding:2px 7px;

### &nbsp;     border-radius:999px;

### &nbsp;     border:1px solid rgba(0,0,0,0.12);

### &nbsp;     color: rgba(0,0,0,0.78);

### &nbsp;     background: rgba(255,255,255,0.92);

### &nbsp;     letter-spacing:.4px;

### &nbsp;   }

### &nbsp;   .pill.live{

### &nbsp;     background: rgba(208,0,0,0.92);

### &nbsp;     border-color: rgba(208,0,0,0.92);

### &nbsp;     color:#fff;

### &nbsp;   }

### &nbsp;   .pill.meta{ color: rgba(0,0,0,0.58); }

### 

### &nbsp;   .teams{ display:flex; flex-direction:column; gap:3px; }

### &nbsp;   .row{ display:flex; align-items:center; gap:8px; line-height:1.05; }

### 

### &nbsp;   .wdot{

### &nbsp;     width:8px;

### &nbsp;     height:8px;

### &nbsp;     border-radius:50%;

### &nbsp;     background: rgba(0,0,0,0.10);

### &nbsp;     border: 1px solid rgba(0,0,0,0.12);

### &nbsp;   }

### &nbsp;   .wdot.on{

### &nbsp;     background:#2ecc71;

### &nbsp;     border-color: rgba(46,204,113,0.65);

### &nbsp;     box-shadow: 0 0 10px rgba(46,204,113,0.35);

### &nbsp;   }

### 

### &nbsp;   .tlogo{

### &nbsp;     width:18px;

### &nbsp;     height:18px;

### &nbsp;     object-fit:contain;

### &nbsp;     border-radius:4px;

### &nbsp;     filter: drop-shadow(0 1px 1px rgba(0,0,0,0.18));

### &nbsp;   }

### &nbsp;   .abbr{

### &nbsp;     font-size:12px;

### &nbsp;     font-weight:900;

### &nbsp;     color: rgba(0,0,0,0.82);

### &nbsp;     min-width:36px;

### &nbsp;     letter-spacing:.3px;

### &nbsp;   }

### &nbsp;   .score{

### &nbsp;     margin-left:auto;

### &nbsp;     font-size:12px;

### &nbsp;     font-weight:1000;

### &nbsp;     color: rgba(0,0,0,0.82);

### &nbsp;   }

### ```

### 

### > To use a different league, change `variables.sport` and `variables.sensor` (e.g. `NFL` + `sensor.espn\_nfl\_scoreboard\_raw`).

### 

### ---

### 

### \## Troubleshooting note (development)

### 

### If you see an error like:

### 

### \- `AttributeError: 'NoneType' object has no attribute 'isEnabledFor'`

### 

### It means the coordinator was created with `logger=None`. Ensure the `DataUpdateCoordinator` is initialized with a real logger (e.g. `logger=LOGGER`).

### 

### ```python

### import logging

### LOGGER = logging.getLogger(\_\_name\_\_)

### 

### super().\_\_init\_\_(

### &nbsp; hass=hass,

### &nbsp; logger=LOGGER,

### &nbsp; name=DOMAIN,

### &nbsp; update\_interval=timedelta(seconds=poll),

### )

### ```



