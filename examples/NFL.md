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


<details open>
<summary>Copy YAML</summary>

```yaml
type: custom:button-card

entity: sensor.espn_nfl_scoreboard_raw

show_icon: false
show_name: false
show_state: false

variables:
  src: sensor.espn_nfl_scoreboard_raw
  fav: ATL
  max_games: 16

styles:
  card:
    - border-radius: 20px
    - padding: 0px
    - overflow: hidden
    - background: rgba(20,20,24,0.70)
    - backdrop-filter: blur(10px)
    - border: 1px solid rgba(255,255,255,0.10)
    - container-type: inline-size

  grid:
    - grid-template-areas: '"main"'
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
      const MAX = Number(variables.max_games ?? 16);

      const st = states[ent];

      if (!st) {
        return `
          <div class="empty">
            ESPN NFL scoreboard unavailable
          </div>
        `;
      }

      const events = st.attributes?.events || [];

      if (!events.length) {
        return `
          <div class="empty">
            No NFL games scheduled
          </div>
        `;
      }


      const rows = events.map(e => {

        const c = e.competitions?.[0];

        const comps = c?.competitors || [];

        const home = comps.find(x => x.homeAway === "home");
        const away = comps.find(x => x.homeAway === "away");


        const hA = home?.team?.abbreviation ?? "HOME";
        const aA = away?.team?.abbreviation ?? "AWAY";

        const hN =
          home?.team?.shortDisplayName ??
          home?.team?.displayName ??
          hA;

        const aN =
          away?.team?.shortDisplayName ??
          away?.team?.displayName ??
          aA;


        const hL = home?.team?.logo || "";
        const aL = away?.team?.logo || "";


        const hS = home?.score ?? "";
        const aS = away?.score ?? "";


        const type = c?.status?.type || {};

        const state = type.state;

        const detail =
          type.shortDetail ||
          type.detail ||
          type.description ||
          "";


        const clock =
          c?.status?.displayClock || "";


        const period =
          c?.status?.period || "";


        const broadcasts =
          (c?.broadcasts || [])
            .flatMap(x => x.names || [])
            .filter(Boolean);


        const network =
          broadcasts.slice(0,2).join(" • ");


        const hasFav =
          hA === fav ||
          aA === fav;


        const liveRank =
          state === "in" ? 0 :
          state === "pre" ? 1 :
          2;


        let badge = "UP NEXT";

        if (state === "in")
          badge = "LIVE";

        if (state === "post")
          badge = "FINAL";


        const statusLine =
          state === "in"
            ? `${period ? "Q" + period : ""} ${clock}`
            : detail;


        return {

          hasFav,

          liveRank,

          start:
            c?.date ||
            e?.date ||
            "",


          html: `

          <div class="game ${hasFav ? "fav" : ""}">

            <div class="side">

              ${
                aL
                ? `<img class="logo" src="${aL}">`
                : `<div class="logo ph"></div>`
              }

              <div class="abbr">
                ${aA}
              </div>

            </div>



            <div class="mid">

              <div class="match">

                <span>
                  ${aN}
                </span>

                <span class="at">
                  @
                </span>

                <span>
                  ${hN}
                </span>

              </div>



              <div class="meta">

                <span class="pill">
                  ${badge}
                </span>


                ${
                  statusLine
                  ? `<span>${statusLine}</span>`
                  : ""
                }


                ${
                  network
                  ? `<span class="dot">•</span>
                     <span class="tv">${network}</span>`
                  : ""
                }

              </div>

            </div>



            <div class="right">

              ${
                state === "in" ||
                state === "post"

                ?

                `
                <div class="score">
                  ${aS}
                  <span class="dash">-</span>
                  ${hS}
                </div>
                `

                :

                `
                <div class="pill2">
                  KICKOFF
                </div>
                `
              }



              ${
                hL
                ? `<img class="logo" src="${hL}">`
                : `<div class="logo ph"></div>`
              }


            </div>


          </div>

          `
        };

      });



      rows.sort((a,b)=>{

        if (a.hasFav !== b.hasFav)
          return a.hasFav ? -1 : 1;

        if (a.liveRank !== b.liveRank)
          return a.liveRank - b.liveRank;


        return String(a.start)
          .localeCompare(String(b.start));

      });



      const list =
        rows
          .slice(0,MAX)
          .map(x=>x.html)
          .join("");



      return `

      <div class="wrap">


        <div class="hdr">

          <div class="title">
            NFL SCOREBOARD
          </div>

          <div class="sub">
            ${events.length} games
          </div>

        </div>


        <div class="body">

          ${list}

        </div>


      </div>

      `;

    ]]]

card_mod:
  style: |

    .wrap{
      width:100%;
    }


    .hdr{

      padding:
        clamp(10px,2vw,16px);

      border-bottom:
        1px solid rgba(255,255,255,.10);

      background:
        rgba(255,255,255,.04);

    }


    .title{

      color:white;

      font-size:
        clamp(18px,3cqw,26px);

      font-weight:900;

      letter-spacing:.6px;

    }


    .sub{

      margin-top:4px;

      color:
        rgba(255,255,255,.65);

      font-size:
        clamp(11px,1.5cqw,14px);

      font-weight:700;

    }



    .body{

      padding:
        clamp(8px,1.5vw,14px);

    }



    .game{

      display:grid;

      grid-template-columns:

        clamp(50px,14%,90px)

        minmax(0,1fr)

        clamp(75px,20%,150px);


      align-items:center;

      gap:
        clamp(5px,1vw,12px);


      padding:
        clamp(8px,1.2vw,12px);


      border-radius:
        clamp(10px,2vw,16px);


      border:
        1px solid rgba(255,255,255,.08);


      background:
        rgba(255,255,255,.04);


      margin-bottom:
        clamp(6px,1vw,10px);

    }



    .game.fav{

      border-color:
        rgba(255,60,60,.35);

      background:
        rgba(255,60,60,.06);

    }



    .side,
    .right{

      display:flex;

      align-items:center;

      gap:8px;

      min-width:0;

    }


    .right{

      justify-content:flex-end;

    }



    .abbr{

      color:
        rgba(255,255,255,.8);

      font-weight:900;

    }



    .logo{

      width:
        clamp(24px,4cqw,40px);

      height:
        clamp(24px,4cqw,40px);

      object-fit:contain;

      border-radius:10px;

      background:
        rgba(255,255,255,.06);

    }



    .match{

      color:white;

      font-size:
        clamp(12px,2cqw,17px);

      font-weight:900;

      white-space:nowrap;

      overflow:hidden;

      text-overflow:ellipsis;

    }



    .at{

      opacity:.5;

      margin:
        0 5px;

    }



    .meta{

      margin-top:5px;

      display:flex;

      flex-wrap:wrap;

      gap:5px;

      align-items:center;

      color:
        rgba(255,255,255,.65);

      font-size:
        clamp(10px,1.5cqw,13px);

      font-weight:700;

    }



    .pill,
    .pill2{

      border-radius:999px;

      padding:
        4px 9px;

      font-size:
        10px;

      font-weight:900;

      letter-spacing:1px;

      border:
        1px solid rgba(255,255,255,.14);

      background:
        rgba(255,255,255,.08);

      white-space:nowrap;

    }



    .score{

      color:white;

      font-size:
        clamp(14px,2.5cqw,22px);

      font-weight:900;

      white-space:nowrap;

    }



    .dash{

      opacity:.5;

      padding:
        0 5px;

    }



    .empty{

      padding:20px;

      color:white;

      text-align:center;

      font-weight:800;

    }



    @container (max-width:500px){

      .abbr{
        display:none;
      }


      .tv{
        display:none;
      }

    }


    @container (max-width:350px){

      .game{

        grid-template-columns:

          42px

          minmax(0,1fr)

          65px;

      }


      .pill2{

        padding:
          3px 6px;

      }

    }
```

</details>

---

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
