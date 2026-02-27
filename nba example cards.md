# NBA Cards (ESPN Scoreboard Raw) — `card.md`

This doc contains copy/paste **Home Assistant Lovelace** examples for NBA using your ESPN-style sensor:

- `sensor.espn_nba_scoreboard_raw`

Most examples use:
- `custom:button-card`
- `card-mod` (for CSS)

> **Important:** In button-card JS templates, `config` may not exist and `entity` may be undefined depending on context.  
> These cards use `variables.src` and read from `states[variables.src]` for reliability.

---

## Requirements

- HACS: **button-card** (`custom:button-card`)
- HACS: **card-mod**
- ESPN NBA sensor with `attributes.events[]` (like your dump)

---

## 1) What’s On Tonight (NBA list)
<img width="206" height="1257" alt="image" src="https://github.com/user-attachments/assets/e1038d01-cb04-4b77-80c5-452352539189" />

Shows tonight’s games with logos, status/time, TV network, and score if live/final. Puts **ATL** game at the top.

<details>
<summary><b>Click to expand the full What’s On Tonight (NBA list)</b></summary>

```yaml
type: custom:button-card
entity: sensor.espn_nba_scoreboard_raw
show_icon: false
show_name: false
show_state: false

variables:
  src: sensor.espn_nba_scoreboard_raw
  fav: ATL
  max_games: 8

styles:
  card:
    - border-radius: 20px
    - padding: 0px
    - overflow: hidden
    - background: rgba(20,20,24,0.70)
    - backdrop-filter: blur(10px)
    - border: 1px solid rgba(255,255,255,0.10)
  grid:
    - grid-template-areas: '"main"'
    - grid-template-columns: 1fr
    - grid-template-rows: 1fr
  custom_fields:
    main:
      - width: 100%

custom_fields:
  main: >
    [[[
      const ent = variables.src;
      const fav = variables.fav;
      const MAX = Number(variables.max_games ?? 8);

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

        const nets = (c?.broadcasts || []).flatMap(b => b?.names || []).filter(Boolean);
        const net = nets.slice(0,2).join(' • ');

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
            <div class="sub">NBA • ${events.length} games</div>
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
2) ESPN Scoreboard Strip (wide “TV ticker” look)
<img width="1101" height="297" alt="image" src="https://github.com/user-attachments/assets/9596d262-f43c-48a4-b593-ec1895cbf387" />


Away on left, home on right, big scores, center quarter/clock + linescore.

<details> <summary><b>Click to expand the full ESPN Scoreboard Strip</b></summary>

```yaml

type: custom:button-card
entity: sensor.espn_nba_scoreboard_raw
show_icon: false
show_name: false
show_state: false

variables:
  src: sensor.espn_nba_scoreboard_raw
  fav: ATL

styles:
  card:
    - border-radius: 18px
    - padding: 14px 16px
    - background: rgba(255,255,255,0.96)
    - border: 1px solid rgba(0,0,0,0.08)
    - overflow: hidden
  custom_fields:
    main:
      - width: 100%

custom_fields:
  main: >
    [[[
      const ent = variables.src;
      const fav = variables.fav;
      const st = states[ent];
      if (!st) return `Entity not found: ${ent}`;

      const events = st.attributes?.events || [];
      if (!events.length) return 'No games';

      const ev = events.find(e => (e.competitions?.[0]?.competitors || []).some(x => x.team?.abbreviation === fav)) || events[0];
      const c = ev.competitions?.[0];
      const comps = c?.competitors || [];
      const away = comps.find(x => x.homeAway === 'away');
      const home = comps.find(x => x.homeAway === 'home');

      const an = away?.team?.abbreviation ?? 'AWY';
      const hn = home?.team?.abbreviation ?? 'HME';
      const as = away?.score ?? '0';
      const hs = home?.score ?? '0';

      const awayName = away?.team?.displayName ?? an;
      const homeName = home?.team?.displayName ?? hn;

      const awayLogo = away?.team?.logo || '';
      const homeLogo = home?.team?.logo || '';

      const period = c?.status?.period;
      const clock  = c?.status?.displayClock;
      const type   = c?.status?.type || {};
      const state  = type?.state;

      let header = '';
      if (state === 'post') header = 'FINAL';
      else if (state === 'pre') header = (type?.shortDetail || 'UP NEXT');
      else header = `${clock || ''} - Q${period || ''}`.trim() || (type?.shortDetail || 'LIVE');

      const aLS = away?.linescores || [];
      const hLS = home?.linescores || [];
      const qCount = Math.max(aLS.length, hLS.length, 4);

      const qHead = Array.from({length:qCount},(_,i)=>`<div class="q">${i+1}</div>`).join('');
      const aRow  = Array.from({length:qCount},(_,i)=>`<div class="qv">${aLS[i]?.displayValue ?? aLS[i]?.value ?? ''}</div>`).join('');
      const hRow  = Array.from({length:qCount},(_,i)=>`<div class="qv">${hLS[i]?.displayValue ?? hLS[i]?.value ?? ''}</div>`).join('');

      return `
        <div class="strip">
          <div class="team left">
            <div class="logo">${awayLogo ? `<img src="${awayLogo}">` : ''}</div>
            <div class="meta">
              <div class="name">${awayName}</div>
              <div class="rec">${away?.records?.[0]?.summary || ''}</div>
            </div>
            <div class="score">${as}</div>
          </div>

          <div class="center">
            <div class="header">${header}</div>
            <div class="linescore">
              <div class="row head">
                <div class="abbr"></div>
                ${qHead}<div class="qt">T</div>
              </div>
              <div class="row">
                <div class="abbr">${an}</div>
                ${aRow}<div class="qtv">${as}</div>
              </div>
              <div class="row">
                <div class="abbr">${hn}</div>
                ${hRow}<div class="qtv">${hs}</div>
              </div>
            </div>
          </div>

          <div class="team right">
            <div class="score">${hs}</div>
            <div class="meta">
              <div class="name">${homeName}</div>
              <div class="rec">${home?.records?.[0]?.summary || ''}</div>
            </div>
            <div class="logo">${homeLogo ? `<img src="${homeLogo}">` : ''}</div>
          </div>
        </div>
      `;
    ]]]

card_mod:
  style: |
    ha-card { position: relative; }
    ha-card:before{
      content:"";
      position:absolute;
      top:0; left:0; right:0;
      height:4px;
      background: rgba(255,0,0,0.85);
    }

    .strip{ display:flex; align-items:center; justify-content:space-between; gap:14px; color:#111; }
    .team{ flex: 1 1 36%; display:flex; align-items:center; gap:12px; min-width:0; }
    .team.left{ justify-content:flex-start; }
    .team.right{ justify-content:flex-end; }

    .logo{ width:56px; height:56px; display:flex; align-items:center; justify-content:center; border-radius:14px; background: rgba(0,0,0,0.02); }
    .logo img{ width:52px; height:52px; object-fit:contain; }

    .meta{ min-width:0; display:flex; flex-direction:column; gap:2px; }
    .name{ font-size:18px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .rec{ font-size:12px; opacity:.55; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

    .score{ font-size:42px; font-weight:900; line-height:1; min-width:48px; text-align:center; }

    .center{ flex:0 0 32%; display:flex; flex-direction:column; align-items:center; gap:8px; min-width:240px; }
    .header{ font-size:16px; font-weight:700; opacity:.85; }

    .linescore{ width:100%; display:flex; flex-direction:column; gap:4px; opacity:.88; }
    .row{ display:grid; grid-template-columns: 44px repeat(4, 22px) 22px; gap:6px; align-items:center; justify-content:center; }
    .row.head{ opacity:.55; font-size:12px; font-weight:700; }
    .abbr{ text-align:left; font-size:12px; font-weight:800; opacity:.85; }
    .q, .qt, .qv, .qtv{ text-align:center; font-size:12px; font-weight:700; }

    @media (max-width: 520px){
      .logo{ display:none; }
      .center{ min-width:200px; }
      .score{ font-size:34px; }
      .name{ font-size:15px; }
    }
  ```
</details>
3) POSSESSION (Last Play + Win% + Leaders)
<img width="1083" height="717" alt="image" src="https://github.com/user-attachments/assets/6a783502-2a53-4e07-9597-8b7fc2edee0d" />


Uses your real payload paths:

competitions[0].situation.lastPlay.text

lastPlay.probability.homeWinPercentage / awayWinPercentage

competitor.leaders[]

<details> <summary><b>Click to expand the full POSSESSION card</b></summary>

```yaml
type: custom:button-card
entity: sensor.espn_nba_scoreboard_raw
show_icon: false
show_name: false
show_state: false

variables:
  src: sensor.espn_nba_scoreboard_raw
  fav: ATL

styles:
  card:
    - border-radius: 22px
    - padding: 0px
    - overflow: hidden
    - background: rgba(255,255,255,0.98)
    - border: 1px solid rgba(0,0,0,0.08)
  custom_fields:
    main:
      - width: 100%

custom_fields:
  main: >
    [[[
      const fav = variables.fav;
      const ent = variables.src;
      const stObj = states[ent];
      if (!stObj) return `Entity not found: ${ent}`;

      const events = stObj.attributes?.events || [];
      if (!events.length) return `${fav}: no games found`;

      const ev = events.find(e => (e.competitions?.[0]?.competitors || []).some(x => x.team?.abbreviation === fav));
      if (!ev) return `${fav}: no game found`;

      const c = ev.competitions?.[0];
      const comps = c?.competitors || [];
      const home = comps.find(x => x.homeAway === 'home');
      const away = comps.find(x => x.homeAway === 'away');

      const hAbbr = home?.team?.abbreviation ?? 'HOME';
      const aAbbr = away?.team?.abbreviation ?? 'AWAY';
      const hLogo = home?.team?.logo ?? '';
      const aLogo = away?.team?.logo ?? '';

      const hScore = home?.score ?? '';
      const aScore = away?.score ?? '';

      const status = c?.status?.type?.shortDetail || c?.status?.type?.detail || '';

      const lp = c?.situation?.lastPlay;
      const playType = lp?.type?.text || 'Possession';
      const playText = lp?.text || '—';

      const p = lp?.probability || {};
      const hWin = (typeof p.homeWinPercentage === 'number') ? (p.homeWinPercentage * 100) : null;
      const aWin = (typeof p.awayWinPercentage === 'number') ? (p.awayWinPercentage * 100) : null;

      let favWin = null;
      if (fav === hAbbr) favWin = hWin;
      if (fav === aAbbr) favWin = aWin;

      const winStr = (favWin != null) ? `Win %: ${fav}, ${favWin.toFixed(1)}%` : '';

      const b = (c?.broadcasts || []).flatMap(x => x?.names || []).filter(Boolean);
      const badges = b.slice(0, 3).map(x => `<span class="pill">${x}</span>`).join('');

      const getLeader = (teamObj, key) => {
        const L = (teamObj?.leaders || []).find(l => l?.name === key);
        const top = L?.leaders?.[0];
        if (!top) return '';
        const nm = top?.athlete?.shortName || top?.athlete?.displayName || '';
        const val = top?.displayValue || '';
        return (nm && val) ? `${L.shortDisplayName || L.displayName || key}: ${nm} ${val}` : '';
      };

      const favTeamObj = (fav === hAbbr) ? home : away;
      const leaders = [
        getLeader(favTeamObj, 'points'),
        getLeader(favTeamObj, 'rebounds'),
        getLeader(favTeamObj, 'assists'),
      ].filter(Boolean).join(' • ');

      return `
        <div class="wrap">
          <div class="hdr">
            <div class="side">
              ${aLogo ? `<img class="logo" src="${aLogo}">` : ``}
              <div class="abbr">${aAbbr}</div>
              <div class="score">${aScore}</div>
            </div>

            <div class="mid">
              <div class="title">POSSESSION</div>
              <div class="sub">${status}</div>
              <div class="badges">${badges}</div>
            </div>

            <div class="side">
              <div class="score">${hScore}</div>
              <div class="abbr">${hAbbr}</div>
              ${hLogo ? `<img class="logo" src="${hLogo}">` : ``}
            </div>
          </div>

          <div class="court"></div>

          <div class="body">
            <div class="row">
              <div class="rail">
                <div class="dot live"></div>
                <div class="line"></div>
              </div>
              <div class="content">
                <div class="topline">
                  <div class="ptype">${playType}</div>
                  <div class="wstr">${winStr}</div>
                </div>
                <div class="ptext">${playText}</div>
                <div class="leaders">${leaders || '&nbsp;'}</div>
              </div>
            </div>
          </div>
        </div>
      `;
    ]]]

card_mod:
  style: |
    .hdr{
      height: 78px;
      background: linear-gradient(180deg, rgba(70,70,70,0.95), rgba(55,55,55,0.95));
      color: #fff;
      display:grid;
      grid-template-columns: 1fr 1.4fr 1fr;
      align-items:center;
      padding: 10px 12px;
      gap: 10px;
    }
    .side{ display:flex; align-items:center; justify-content:center; gap:10px; min-width:0; }
    .logo{ width:40px; height:40px; object-fit:contain; }
    .abbr{ font-size:14px; font-weight:800; opacity:.85; letter-spacing:.8px; }
    .score{ font-size:28px; font-weight:900; line-height:1; }

    .mid{ display:flex; flex-direction:column; align-items:center; gap:6px; text-align:center; min-width:0; }
    .title{ font-size:34px; font-weight:900; letter-spacing:2px; line-height:1; }
    .sub{ font-size:13px; opacity:.8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%; }

    .badges{ display:flex; gap:6px; flex-wrap:wrap; justify-content:center; }
    .pill{ font-size:11px; font-weight:800; padding:3px 8px; border-radius:999px; background: rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.18); }

    .court{
      height: 92px;
      background:
        radial-gradient(circle at 50% 50%, rgba(200,120,40,0.18), rgba(0,0,0,0) 55%),
        linear-gradient(180deg, rgba(240,240,240,0.95), rgba(255,255,255,1));
      border-bottom: 1px solid rgba(0,0,0,0.08);
    }
    .body{ padding: 14px 16px 16px; background:#fff; }
    .row{ display:grid; grid-template-columns: 18px 1fr; gap:12px; align-items:flex-start; }

    .rail{ position:relative; display:flex; justify-content:center; }
    .dot{ width:8px; height:8px; border-radius:999px; background: rgba(200,0,0,0.55); margin-top:6px; }
    .dot.live{ background: rgba(200,0,0,1); box-shadow: 0 0 0 4px rgba(200,0,0,0.18); }
    .line{ position:absolute; top:18px; bottom:-6px; width:4px; border-radius:999px; background: rgba(200,0,0,0.12); }

    .topline{ display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
    .ptype{ font-size:22px; font-weight:900; color:#111; }
    .wstr{ font-size:14px; font-weight:800; color: rgba(0,0,0,0.55); white-space:nowrap; }
    .ptext{ margin-top:6px; font-size:16px; color: rgba(0,0,0,0.85); line-height:1.25; }
    .leaders{ margin-top:10px; font-size:13px; color: rgba(0,0,0,0.55); font-weight:700; }

    @media (max-width: 520px){
      .title{ font-size:26px; }
      .score{ font-size:24px; }
      .logo{ width:34px; height:34px; }
      .ptype{ font-size:18px; }
      .wstr{ font-size:12px; }
    }
  ```
</details>
