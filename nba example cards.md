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

Shows tonight’s games with logos, status/time, TV network, and score if live/final. Puts **ATL** game at the top.

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
