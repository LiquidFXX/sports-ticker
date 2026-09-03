const SPORTS_TICKER_EDITOR_VERSION = "0.1.0";

const ST_SPORTS = {
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

const stSportForEntity = (entityId) => Object.entries(ST_SPORTS).find(([, sport]) => sport.entity === entityId)?.[0] || null;

class SportsTickerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    this._config = { ...(config || {}) };
    this._render();
  }

  _availableSports() {
    if (!this._hass) return [];
    return Object.entries(ST_SPORTS).filter(([, sport]) => {
      const state = this._hass.states?.[sport.entity];
      return Boolean(state && Array.isArray(state.attributes?.events));
    });
  }

  _cardChoice() {
    if (this._config.preset === "ticker") return "ticker";
    const sport = stSportForEntity(this._config.entity);
    if (!sport) return "ticker";
    return `${sport}:${this._config.preset === "game_compact" ? "game_compact" : "game"}`;
  }

  _emit(next) {
    this._config = next;
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config: next },
      bubbles: true,
      composed: true,
    }));
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._hass) return;
    const available = this._availableSports();
    const availableKeys = available.map(([key]) => key);
    const selectedSports = Array.isArray(this._config.sports)
      ? this._config.sports.filter((key) => availableKeys.includes(key))
      : availableKeys.slice(0, 1);
    const choice = this._cardChoice();
    const isTicker = choice === "ticker";

    const cardOptions = [
      '<option value="ticker">Multi-Sport Ticker</option>',
      ...available.flatMap(([key, sport]) => [
        `<option value="${key}:game">${sport.label} — Game</option>`,
        `<option value="${key}:game_compact">${sport.label} — Game Compact</option>`,
      ]),
    ].join("");

    const sportChecks = available.map(([key, sport]) => `
      <label class="sport-option">
        <input type="checkbox" data-sport="${key}" ${selectedSports.includes(key) ? "checked" : ""}>
        <span>${sport.label}</span>
      </label>`).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,inherit)}
        .editor{display:grid;gap:16px}.field{display:grid;gap:7px}.label{font-size:13px;font-weight:600}.helper{font-size:12px;line-height:1.4;color:var(--secondary-text-color)}
        select,input[type="number"],input[type="text"]{width:100%;box-sizing:border-box;min-height:44px;padding:9px 12px;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color,var(--ha-card-background));color:var(--primary-text-color);font:inherit}
        .panel{display:grid;gap:12px;padding:14px;border:1px solid var(--divider-color);border-radius:12px}.panel-title{font-size:14px;font-weight:700}.sports{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:8px}.sport-option,.toggle{display:flex;align-items:center;gap:9px;min-height:34px;font-size:13px}.sport-option input,.toggle input{width:18px;height:18px;margin:0}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.empty{padding:12px;border:1px dashed var(--divider-color);border-radius:10px;color:var(--secondary-text-color);font-size:13px}
        @media(max-width:520px){.row{grid-template-columns:1fr}}
      </style>
      <div class="editor">
        <div class="field">
          <div class="label">Card</div>
          <select id="card-choice">${cardOptions}</select>
          <div class="helper">Only cards for sports currently enabled in the Sports Ticker integration are shown.</div>
        </div>
        ${available.length ? "" : '<div class="empty">No enabled Sports Ticker scoreboard sensors were found. Enable at least one sport in the integration options.</div>'}
        ${isTicker ? `
          <div class="panel">
            <div class="panel-title">Ticker sports</div>
            <div class="helper">Only enabled sports are available. Select one or more leagues to include.</div>
            <div class="sports">${sportChecks}</div>
          </div>
          <div class="panel">
            <div class="panel-title">Ticker options</div>
            <label class="toggle"><input id="show-logos" type="checkbox" ${this._config.show_logos !== false ? "checked" : ""}>Show team logos</label>
            <label class="toggle"><input id="pause-hover" type="checkbox" ${this._config.ticker_pause_on_hover !== false ? "checked" : ""}>Pause on hover</label>
            <div class="row">
              <div class="field"><div class="label">Seconds per game</div><input id="speed" type="number" min="3" max="20" step="1" value="${Number(this._config.ticker_seconds_per_game) || 8}"></div>
              <div class="field"><div class="label">Max games per sport</div><input id="max-games" type="number" min="1" max="30" step="1" value="${Number(this._config.ticker_max_games_per_sport) || 20}"></div>
            </div>
          </div>` : `
          <div class="panel">
            <div class="panel-title">Game options</div>
            <label class="toggle"><input id="show-logos" type="checkbox" ${this._config.show_logos !== false ? "checked" : ""}>Show team logos</label>
            <label class="toggle"><input id="show-league" type="checkbox" ${this._config.show_league !== false ? "checked" : ""}>Show league</label>
            <label class="toggle"><input id="show-records" type="checkbox" ${this._config.show_records !== false ? "checked" : ""}>Show team records</label>
            <label class="toggle"><input id="show-venue" type="checkbox" ${this._config.show_venue !== false ? "checked" : ""}>Show venue</label>
            <label class="toggle"><input id="show-broadcast" type="checkbox" ${this._config.show_broadcast !== false ? "checked" : ""}>Show broadcast</label>
            <div class="field"><div class="label">Event ID</div><input id="event-id" type="text" value="${this._escapeAttr(this._config.event_id || "")}" placeholder="Optional ESPN event ID"></div>
          </div>`}
      </div>`;

    const choiceEl = this.shadowRoot.getElementById("card-choice");
    choiceEl.value = available.length || choice === "ticker" ? choice : "ticker";
    if (![...choiceEl.options].some((option) => option.value === choiceEl.value)) choiceEl.value = "ticker";
    choiceEl.addEventListener("change", () => this._changeCard(choiceEl.value, available));

    if (isTicker) this._wireTicker(selectedSports);
    else this._wireGame();
  }

  _changeCard(value, available) {
    if (value === "ticker") {
      const enabled = available.map(([key]) => key);
      const sports = (Array.isArray(this._config.sports) ? this._config.sports : []).filter((key) => enabled.includes(key));
      this._emit({
        ...this._config,
        preset: "ticker",
        sports: sports.length ? sports : enabled.slice(0, 1),
        show_logos: this._config.show_logos !== false,
        ticker_seconds_per_game: Number(this._config.ticker_seconds_per_game) || 8,
        ticker_max_games_per_sport: Number(this._config.ticker_max_games_per_sport) || 20,
        ticker_pause_on_hover: this._config.ticker_pause_on_hover !== false,
      });
      return;
    }
    const [sportKey, preset] = value.split(":");
    const sport = ST_SPORTS[sportKey];
    if (!sport) return;
    this._emit({
      ...this._config,
      preset,
      entity: sport.entity,
      show_logos: this._config.show_logos !== false,
      show_league: preset === "game_compact" ? false : this._config.show_league !== false,
      show_records: this._config.show_records !== false,
      show_venue: preset === "game_compact" ? false : this._config.show_venue !== false,
      show_broadcast: preset === "game_compact" ? false : this._config.show_broadcast !== false,
    });
  }

  _wireTicker(selectedSports) {
    this.shadowRoot.querySelectorAll("[data-sport]").forEach((input) => input.addEventListener("change", () => {
      const sports = [...this.shadowRoot.querySelectorAll("[data-sport]:checked")].map((item) => item.dataset.sport);
      if (!sports.length) {
        input.checked = true;
        return;
      }
      this._emit({ ...this._config, preset: "ticker", sports });
    }));
    this._wireBool("show-logos", "show_logos");
    this._wireBool("pause-hover", "ticker_pause_on_hover");
    this._wireNumber("speed", "ticker_seconds_per_game", 3, 20);
    this._wireNumber("max-games", "ticker_max_games_per_sport", 1, 30);
  }

  _wireGame() {
    this._wireBool("show-logos", "show_logos");
    this._wireBool("show-league", "show_league");
    this._wireBool("show-records", "show_records");
    this._wireBool("show-venue", "show_venue");
    this._wireBool("show-broadcast", "show_broadcast");
    const eventId = this.shadowRoot.getElementById("event-id");
    eventId?.addEventListener("change", () => this._emit({ ...this._config, event_id: eventId.value.trim() || undefined }));
  }

  _wireBool(id, key) {
    const input = this.shadowRoot.getElementById(id);
    input?.addEventListener("change", () => this._emit({ ...this._config, [key]: input.checked }));
  }

  _wireNumber(id, key, min, max) {
    const input = this.shadowRoot.getElementById(id);
    input?.addEventListener("change", () => {
      const value = Math.max(min, Math.min(max, Number(input.value) || min));
      this._emit({ ...this._config, [key]: value });
    });
  }

  _escapeAttr(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }
}

if (!customElements.get("sports-ticker-card-editor")) customElements.define("sports-ticker-card-editor", SportsTickerCardEditor);

const SportsTickerCardClass = customElements.get("sports-ticker-card");
if (SportsTickerCardClass) {
  SportsTickerCardClass.getConfigElement = async () => document.createElement("sports-ticker-card-editor");
}

console.info(`%c SPORTS-TICKER-EDITOR %c v${SPORTS_TICKER_EDITOR_VERSION} `, "background:#444;color:#fff;font-weight:700", "background:#eee;color:#444");
