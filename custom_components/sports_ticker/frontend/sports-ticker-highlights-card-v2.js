const SPORTS_TICKER_HIGHLIGHTS_VERSION = "0.1.0";

const HIGHLIGHT_SPORTS = {
  nfl: { label: "NFL", entity: "sensor.espn_nfl_scoreboard_raw" },
  cfb: { label: "CFB", entity: "sensor.espn_cfb_scoreboard_raw" },
  mlb: { label: "MLB", entity: "sensor.espn_mlb_scoreboard_raw" },
  nba: { label: "NBA", entity: "sensor.espn_nba_scoreboard_raw" },
  wnba: { label: "WNBA", entity: "sensor.espn_wnba_scoreboard_raw" },
  nhl: { label: "NHL", entity: "sensor.espn_nhl_scoreboard_raw" },
  mls: { label: "MLS", entity: "sensor.espn_mls_scoreboard_raw" },
  epl: { label: "Premier League", entity: "sensor.espn_epl_scoreboard_raw" },
  laliga: { label: "LaLiga", entity: "sensor.espn_laliga_scoreboard_raw" },
  bundesliga: { label: "Bundesliga", entity: "sensor.espn_bundesliga_scoreboard_raw" },
  seriea: { label: "Serie A", entity: "sensor.espn_seriea_scoreboard_raw" },
  ligue1: { label: "Ligue 1", entity: "sensor.espn_ligue1_scoreboard_raw" },
  ucl: { label: "Champions League", entity: "sensor.espn_ucl_scoreboard_raw" },
};

const hEsc = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");
const hArr = (value) => Array.isArray(value) ? value : [];

class SportsTickerHighlightsCard extends HTMLElement {
  static getStubConfig(hass) {
    const entity = Object.values(HIGHLIGHT_SPORTS).find((sport) => hass?.states?.[sport.entity])?.entity;
    return { entity, favorite_only: false, prefer_favorite: true, show_recap: true, show_espn_link: true };
  }

  static async getConfigElement() {
    await customElements.whenDefined("sports-ticker-highlights-card-editor");
    return document.createElement("sports-ticker-highlights-card-editor");
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._signature = "";
  }

  setConfig(config) {
    if (!config?.entity) throw new Error("Sports Ticker Highlights requires a scoreboard entity");
    this._config = {
      favorite_only: false,
      prefer_favorite: true,
      show_recap: true,
      show_espn_link: true,
      ...config,
    };
    this._signature = "";
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const state = this._config?.entity ? hass?.states?.[this._config.entity] : null;
    const signature = `${this._config?.entity || ""}:${state?.last_updated || "missing"}:${state?.state || ""}`;
    if (signature === this._signature) return;
    this._signature = signature;
    this._render();
  }

  getCardSize() { return 5; }
  getGridOptions() { return { columns: 12, rows: 5, min_columns: 6, min_rows: 4 }; }

  _competitors(comp) { return hArr(comp?.competitors); }
  _away(comp) { return this._competitors(comp).find((x) => x?.homeAway === "away") || {}; }
  _home(comp) { return this._competitors(comp).find((x) => x?.homeAway === "home") || {}; }
  _abbr(competitor) { return competitor?.team?.abbreviation || competitor?.team?.shortDisplayName || "TEAM"; }
  _logo(team) { return team?.logo || hArr(team?.logos)[0]?.href || hArr(team?.logos)[0]?.url || ""; }
  _score(competitor) { return competitor?.score ?? "—"; }

  _headlineObjects(event, comp) {
    return [...hArr(comp?.headlines), ...hArr(event?.headlines)];
  }

  _videos(event, comp) {
    const videos = [...hArr(comp?.highlights), ...hArr(event?.highlights)];
    this._headlineObjects(event, comp).forEach((headline) => videos.push(...hArr(headline?.video)));
    const seen = new Set();
    return videos.filter((video) => {
      const key = String(video?.id || video?.headline || video?.thumbnail || "");
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return Boolean(this._directVideo(video));
    });
  }

  _directVideo(video) {
    const links = video?.links || {};
    return links?.source?.HD?.href || links?.source?.href || links?.source?.mezzanine?.href || links?.HD?.href || links?.mezzanine?.href || "";
  }

  _espnPage(video) { return video?.links?.web?.href || video?.links?.self?.href || ""; }

  _duration(raw) {
    const total = Number(raw || 0);
    if (!Number.isFinite(total) || total <= 0) return "";
    const minutes = Math.floor(total / 60);
    const seconds = Math.floor(total % 60);
    return `${minutes}:${String(seconds).padStart(2, "0")}`;
  }

  _isFavoriteGame(game, favorite) {
    if (!favorite) return false;
    const wanted = String(favorite).trim().toUpperCase();
    const values = [game.away, game.home].flatMap((competitor) => {
      const team = competitor?.team || {};
      return [team.abbreviation, team.shortDisplayName, team.displayName, team.name].filter(Boolean).map((v) => String(v).toUpperCase());
    });
    return values.includes(wanted);
  }

  _playableGames(events, favorite) {
    return events.map((event) => {
      const comp = event?.competitions?.[0] || {};
      const videos = this._videos(event, comp);
      if (!videos.length) return null;
      const away = this._away(comp);
      const home = this._home(comp);
      const status = comp?.status || event?.status || {};
      const state = String(status?.type?.state || "").toLowerCase();
      const game = { event, comp, away, home, videos, state, date: comp?.date || event?.date || "" };
      game.favorite = this._isFavoriteGame(game, favorite);
      return game;
    }).filter(Boolean).sort((a, b) => {
      const aRank = a.state === "post" ? 0 : 1;
      const bRank = b.state === "post" ? 0 : 1;
      if (aRank !== bRank) return aRank - bRank;
      return new Date(b.date || 0) - new Date(a.date || 0);
    });
  }

  _selectGame(games, favorite) {
    if (this._config.favorite_only) {
      if (!favorite) return { error: "No favorite team is configured for this league." };
      const favoriteGame = games.find((game) => game.favorite);
      return favoriteGame ? { game: favoriteGame } : { error: `No playable highlights are available for ${favorite}.` };
    }
    if (this._config.prefer_favorite && favorite) {
      const favoriteGame = games.find((game) => game.favorite);
      if (favoriteGame) return { game: favoriteGame };
    }
    return games[0] ? { game: games[0] } : { error: "No playable highlights are available." };
  }

  _logoMarkup(url, abbreviation) {
    if (!url) return `<div class="logo-plate"><span class="logo-fallback">${hEsc(abbreviation)}</span></div>`;
    return `<div class="logo-plate"><img class="team-logo" src="${hEsc(url)}" alt="${hEsc(abbreviation)}"></div>`;
  }

  _message(title, subtitle) {
    this.shadowRoot.innerHTML = `${this._styles()}<ha-card><div class="empty"><div class="empty-title">${hEsc(title)}</div><div class="empty-sub">${hEsc(subtitle)}</div></div></ha-card>`;
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;
    const st = this._hass.states[this._config.entity];
    if (!st) return this._message("GAME HIGHLIGHTS", `Entity not found: ${this._config.entity}`);
    const attrs = st.attributes || {};
    const events = hArr(attrs.events);
    const favorite = String(attrs.favorite_team || "").trim().toUpperCase();
    const games = this._playableGames(events, favorite);
    const selected = this._selectGame(games, favorite);
    if (!selected.game) return this._message("GAME HIGHLIGHTS", selected.error);

    const game = selected.game;
    const video = game.videos[0];
    const directVideo = this._directVideo(video);
    const espnPage = this._espnPage(video);
    const duration = this._duration(video?.duration);
    const away = game.away;
    const home = game.home;
    const awayAbbr = this._abbr(away);
    const homeAbbr = this._abbr(home);
    const headlines = this._headlineObjects(game.event, game.comp);
    const recap = headlines.find((item) => String(item?.type || "").toLowerCase() === "recap") || headlines[0] || {};
    const videoTitle = video?.headline || video?.description || recap?.shortLinkText || `${awayAbbr} vs. ${homeAbbr} Highlights`;
    const recapText = recap?.shortLinkText || recap?.description || "";

    this.shadowRoot.innerHTML = `${this._styles()}
      <ha-card class="highlight-card">
        <div class="highlight-shell">
          <div class="video-panel">
            <video class="highlight-video" controls playsinline preload="metadata" ${video?.thumbnail ? `poster="${hEsc(video.thumbnail)}"` : ""}>
              <source src="${hEsc(directVideo)}" type="video/mp4">
            </video>
            <button class="big-play" type="button" aria-label="Play highlight"><span>▶</span></button>
            <div class="hero-overlay">
              <div class="hero-meta"><span>HIGHLIGHTS</span>${game.state === "post" ? '<b>FINAL</b>' : ""}${game.favorite ? '<b>FAVORITE</b>' : ""}</div>
              <div class="hero-title">${hEsc(videoTitle)}</div>
            </div>
            ${duration ? `<div class="duration">${hEsc(duration)}</div>` : ""}
          </div>
          <div class="info-bar">
            <div class="matchup">
              <div class="team">${this._logoMarkup(this._logo(away?.team || {}), awayAbbr)}<span class="team-name">${hEsc(awayAbbr)}</span><span class="team-score">${hEsc(this._score(away))}</span></div>
              <span class="score-separator">–</span>
              <div class="team">${this._logoMarkup(this._logo(home?.team || {}), homeAbbr)}<span class="team-name">${hEsc(homeAbbr)}</span><span class="team-score">${hEsc(this._score(home))}</span></div>
            </div>
            <div class="details"><div class="recap">${hEsc(this._config.show_recap && recapText ? recapText : videoTitle)}</div></div>
            ${this._config.show_espn_link && espnPage ? `<a class="espn-button" href="${hEsc(espnPage)}" target="_blank" rel="noopener noreferrer">ESPN ↗</a>` : ""}
          </div>
        </div>
      </ha-card>`;

    const panel = this.shadowRoot.querySelector(".video-panel");
    const player = this.shadowRoot.querySelector(".highlight-video");
    const play = this.shadowRoot.querySelector(".big-play");
    const updatePlay = () => panel?.classList.toggle("is-playing", !player?.paused && !player?.ended);
    play?.addEventListener("click", () => player?.play());
    player?.addEventListener("play", updatePlay);
    player?.addEventListener("pause", updatePlay);
    player?.addEventListener("ended", updatePlay);
  }

  _styles() {
    return `<style>
      :host{display:block;container-type:inline-size}.highlight-card{overflow:hidden}.highlight-shell{width:100%;min-width:0;overflow:hidden;background:var(--ha-card-background,var(--card-background-color));color:var(--primary-text-color)}
      .video-panel{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;background:#000}.highlight-video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000}
      .big-play{position:absolute;z-index:12;left:50%;top:50%;transform:translate(-50%,-50%);width:88px;height:88px;border-radius:50%;display:grid;place-items:center;border:3px solid rgba(255,255,255,.94);background:rgba(5,10,18,.72);color:#fff;font-size:40px;cursor:pointer;box-shadow:0 8px 30px rgba(0,0,0,.45);backdrop-filter:blur(12px);transition:opacity .18s ease,transform .18s ease}.big-play span{margin-left:6px}.video-panel.is-playing .big-play{opacity:0;pointer-events:none;transform:translate(-50%,-50%) scale(.88)}
      .hero-overlay{position:absolute;z-index:5;left:0;right:0;bottom:0;padding:64px 18px 15px;pointer-events:none;background:linear-gradient(180deg,transparent 0%,rgba(3,7,13,.08) 18%,rgba(3,7,13,.7) 65%,rgba(3,7,13,.93) 100%);color:#fff}.hero-meta{display:flex;align-items:center;gap:7px;margin-bottom:6px;font-size:10px;font-weight:900;letter-spacing:1.3px;color:rgba(255,255,255,.74)}.hero-meta b{padding:3px 7px;border:1px solid rgba(255,255,255,.15);border-radius:999px;background:rgba(255,255,255,.1);font-size:9px}.hero-title{width:min(82%,760px);display:-webkit-box;overflow:hidden;font-size:clamp(17px,2.35cqw,24px);font-weight:900;line-height:1.15;-webkit-line-clamp:2;-webkit-box-orient:vertical;text-shadow:0 2px 9px rgba(0,0,0,.72)}
      .duration{position:absolute;z-index:14;top:12px;right:12px;padding:5px 9px;border-radius:10px;color:#fff;background:rgba(3,7,13,.76);border:1px solid rgba(255,255,255,.16);font-size:12px;font-weight:900}
      .info-bar{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:14px;padding:11px 14px;border-top:1px solid var(--divider-color);background:var(--ha-card-background,var(--card-background-color))}.matchup{display:flex;align-items:center;gap:6px;padding:6px 8px;border-radius:13px;background:var(--secondary-background-color);white-space:nowrap}.team{display:flex;align-items:center;gap:5px}.logo-plate{width:32px;height:32px;display:grid;place-items:center;padding:3px;border-radius:9px;background:var(--card-background-color);border:1px solid var(--divider-color)}.team-logo{width:24px;height:24px;object-fit:contain}.logo-fallback{font-size:8px;font-weight:900}.team-name{color:var(--secondary-text-color);font-size:10px;font-weight:800}.team-score{font-size:20px;font-weight:900;font-variant-numeric:tabular-nums}.score-separator{color:var(--disabled-text-color);font-size:11px}.details{min-width:0}.recap{display:-webkit-box;overflow:hidden;color:var(--secondary-text-color);font-size:11px;font-weight:650;line-height:1.35;-webkit-line-clamp:2;-webkit-box-orient:vertical}.espn-button{display:inline-flex;align-items:center;justify-content:center;padding:7px 9px;border-radius:9px;color:var(--primary-text-color);background:var(--secondary-background-color);border:1px solid var(--divider-color);text-decoration:none;font-size:9px;font-weight:900}.empty{min-height:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;padding:20px}.empty-title{font-size:15px;font-weight:900}.empty-sub{color:var(--secondary-text-color);font-size:11px;text-align:center}
      @container(max-width:760px){.hero-title{width:90%}.info-bar{grid-template-columns:auto minmax(0,1fr)}.espn-button{grid-column:2;justify-self:end}.details{padding-right:0}}
      @container(max-width:500px){.big-play{width:72px;height:72px;font-size:32px}.hero-overlay{padding:48px 12px 10px}.hero-title{width:94%;font-size:15px}.duration{top:8px;right:8px;font-size:10px}.info-bar{grid-template-columns:1fr auto;gap:8px;padding:9px 10px}.details{grid-column:1/-1;grid-row:2}.espn-button{grid-column:2;grid-row:1}.logo-plate{width:28px;height:28px}.team-logo{width:21px;height:21px}.team-score{font-size:17px}}
    </style>`;
  }
}

class SportsTickerHighlightsCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
    this._availabilitySignature = "";
  }

  set hass(hass) {
    this._hass = hass;
    const signature = this._availableSports().map(([key]) => key).join("|");
    if (!this.shadowRoot.childNodes.length || signature !== this._availabilitySignature) {
      this._availabilitySignature = signature;
      this._render();
    }
  }

  setConfig(config) {
    this._config = { ...(config || {}) };
    this._render();
  }

  _availableSports() {
    if (!this._hass) return [];
    return Object.entries(HIGHLIGHT_SPORTS).filter(([, sport]) => {
      const state = this._hass.states?.[sport.entity];
      return Boolean(state && Array.isArray(state.attributes?.events));
    });
  }

  _emit(next) {
    this._config = next;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: next }, bubbles: true, composed: true }));
    this._render();
  }

  _toggle(id, label, icon, checked, helper = "") {
    return `<label class="toggle"><span class="toggle-copy"><span class="toggle-title"><ha-icon icon="${icon}"></ha-icon>${label}</span>${helper ? `<small>${helper}</small>` : ""}</span><span class="switch"><input id="${id}" type="checkbox" ${checked ? "checked" : ""}><span class="slider"></span></span></label>`;
  }

  _render() {
    if (!this.shadowRoot || !this._hass) return;
    const available = this._availableSports();
    const currentEntity = this._config.entity || available[0]?.[1]?.entity || "";
    this.shadowRoot.innerHTML = `<style>
      :host{display:block;color:var(--primary-text-color)}*{box-sizing:border-box}.editor{display:grid;gap:0;padding:4px 10px 22px}.section{display:grid;gap:16px;padding:20px 0}.section+.section{border-top:1px solid var(--divider-color)}.eyebrow{font-size:12px;font-weight:800;letter-spacing:.105em;text-transform:uppercase;color:var(--secondary-text-color)}.helper{font-size:12px;line-height:1.45;color:var(--secondary-text-color)}
      .league-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:9px}.league{min-height:43px;padding:0 10px;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color,var(--ha-card-background));color:var(--primary-text-color);font:inherit;font-size:13px;font-weight:700;cursor:pointer}.league.selected{border-color:var(--primary-color);background:color-mix(in srgb,var(--primary-color) 10%,var(--card-background-color,var(--ha-card-background)));color:var(--primary-color)}
      .options{display:grid}.toggle{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:58px;border-bottom:1px solid color-mix(in srgb,var(--divider-color) 75%,transparent)}.toggle:last-child{border-bottom:0}.toggle-copy{display:grid;gap:3px}.toggle-title{display:flex;align-items:center;gap:9px;font-size:14px;font-weight:650}.toggle-title ha-icon{--mdc-icon-size:19px;color:var(--secondary-text-color)}.toggle small{font-size:11px;line-height:1.35;color:var(--secondary-text-color)}.switch{position:relative;width:48px;height:28px;flex:0 0 48px}.switch input{position:absolute;opacity:0}.slider{position:absolute;inset:0;border-radius:999px;background:var(--disabled-color,#9e9e9e);cursor:pointer;transition:.18s}.slider:before{content:"";position:absolute;width:22px;height:22px;left:3px;top:3px;border-radius:50%;background:var(--card-background-color,#fff);box-shadow:0 1px 3px rgba(0,0,0,.35);transition:.18s}.switch input:checked+.slider{background:var(--primary-color)}.switch input:checked+.slider:before{transform:translateX(20px)}
      .favorite-note{display:flex;align-items:flex-start;gap:8px;padding:11px 12px;border-radius:10px;background:var(--secondary-background-color);font-size:12px;line-height:1.4;color:var(--secondary-text-color)}.favorite-note ha-icon{--mdc-icon-size:18px;color:var(--primary-color)}
    </style><div class="editor">
      <section class="section"><div class="eyebrow">Highlights source</div><div class="league-grid">${available.map(([key, sport]) => `<button type="button" class="league ${sport.entity === currentEntity ? "selected" : ""}" data-entity="${sport.entity}">${sport.label}</button>`).join("")}</div><div class="helper">Only leagues enabled in Sports Ticker are shown.</div></section>
      <section class="section"><div class="eyebrow">Highlight options</div><div class="options">
        ${this._toggle("favorite-only", "Favorite teams only", "mdi:star", this._config.favorite_only === true, "Never fall back to another team's highlight.")}
        ${this._toggle("prefer-favorite", "Prefer favorite team", "mdi:star-outline", this._config.prefer_favorite !== false, "When favorite-only is off, choose a favorite-team highlight first when available.")}
        ${this._toggle("show-recap", "Show recap text", "mdi:text-box-outline", this._config.show_recap !== false)}
        ${this._toggle("show-espn", "Show ESPN link", "mdi:open-in-new", this._config.show_espn_link !== false)}
      </div><div class="favorite-note"><ha-icon icon="mdi:information-outline"></ha-icon><span>The favorite team comes from the selected league's Sports Ticker integration settings. You do not need to configure it again on this card.</span></div></section>
    </div>`;

    this.shadowRoot.querySelectorAll("[data-entity]").forEach((button) => button.addEventListener("click", () => this._emit({ ...this._config, entity: button.dataset.entity })));
    [["favorite-only","favorite_only"],["prefer-favorite","prefer_favorite"],["show-recap","show_recap"],["show-espn","show_espn_link"]].forEach(([id,key]) => {
      this.shadowRoot.getElementById(id)?.addEventListener("change", (event) => this._emit({ ...this._config, [key]: event.target.checked }));
    });
  }
}

customElements.define("sports-ticker-highlights-card", SportsTickerHighlightsCard);
customElements.define("sports-ticker-highlights-card-editor", SportsTickerHighlightsCardEditor);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "sports-ticker-highlights-card")) {
  window.customCards.push({
    type: "sports-ticker-highlights-card",
    name: "Sports Ticker — Game Highlights",
    description: "Playable ESPN game highlights with optional favorite-team-only filtering.",
    preview: true,
  });
}
console.info(`%c SPORTS-TICKER-HIGHLIGHTS %c v${SPORTS_TICKER_HIGHLIGHTS_VERSION} `,"background:#444;color:#fff;font-weight:700","background:#eee;color:#444");
