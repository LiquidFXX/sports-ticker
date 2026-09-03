const SPORTS_TICKER_SPLIT_VERSION = "0.1.0";

const ST_SPLIT_SPORTS = {
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

const stSplitAvailable = (hass, key) => {
  const def = ST_SPLIT_SPORTS[key];
  const state = def ? hass?.states?.[def.entity] : null;
  return Boolean(state && Array.isArray(state.attributes?.events));
};

class SportsTickerSplitEditorBase extends HTMLElement {
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

  _emit(patch) {
    const next = { ...this._config, ...patch };
    this._config = next;
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config: next },
      bubbles: true,
      composed: true,
    }));
    this._render();
  }

  _styles() {
    return `<style>
      :host{display:block;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,inherit)}
      .editor{display:grid;gap:16px}.panel{display:grid;gap:12px;padding:14px;border:1px solid var(--divider-color);border-radius:12px}.title{font-size:14px;font-weight:700}.helper{font-size:12px;line-height:1.4;color:var(--secondary-text-color)}
      .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.field{display:grid;gap:7px}.label{font-size:13px;font-weight:600}.toggle,.sport-option{display:flex;align-items:center;gap:9px;min-height:34px;font-size:13px}
      select,input[type="number"],input[type="text"]{width:100%;box-sizing:border-box;min-height:44px;padding:9px 12px;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color,var(--ha-card-background));color:var(--primary-text-color);font:inherit}
      input[type="checkbox"]{width:18px;height:18px;margin:0}.sports{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}.warning{padding:12px;border:1px dashed var(--warning-color,var(--divider-color));border-radius:10px;color:var(--secondary-text-color);font-size:13px}
      @media(max-width:520px){.row{grid-template-columns:1fr}}
    </style>`;
  }

  _wireBool(id, key) {
    const el = this.shadowRoot.getElementById(id);
    el?.addEventListener("change", () => this._emit({ [key]: el.checked }));
  }

  _wireNumber(id, key, min, max) {
    const el = this.shadowRoot.getElementById(id);
    el?.addEventListener("change", () => {
      const value = Math.max(min, Math.min(max, Number(el.value) || min));
      this._emit({ [key]: value });
    });
  }

  _escape(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }
}

class SportsTickerSportCardEditor extends SportsTickerSplitEditorBase {
  set sportKey(value) {
    this._sportKey = value;
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._sportKey) return;
    const def = ST_SPLIT_SPORTS[this._sportKey];
    const enabled = stSplitAvailable(this._hass, this._sportKey);
    const compact = this._config.preset === "game_compact";

    this.shadowRoot.innerHTML = `${this._styles()}<div class="editor">
      ${enabled ? "" : `<div class="warning">${def.label} is not currently enabled in the Sports Ticker integration. Enable it in the integration options before using this card.</div>`}
      <div class="panel">
        <div class="title">${def.label} card</div>
        <div class="field"><div class="label">Layout</div><select id="layout"><option value="game">Standard</option><option value="game_compact">Compact</option></select></div>
      </div>
      <div class="panel">
        <div class="title">Display options</div>
        <label class="toggle"><input id="show-logos" type="checkbox" ${this._config.show_logos !== false ? "checked" : ""}>Show team logos</label>
        <label class="toggle"><input id="show-league" type="checkbox" ${this._config.show_league !== false ? "checked" : ""}>Show league</label>
        <label class="toggle"><input id="show-records" type="checkbox" ${this._config.show_records !== false ? "checked" : ""}>Show team records</label>
        <label class="toggle"><input id="show-venue" type="checkbox" ${this._config.show_venue !== false ? "checked" : ""}>Show venue</label>
        <label class="toggle"><input id="show-broadcast" type="checkbox" ${this._config.show_broadcast !== false ? "checked" : ""}>Show broadcast</label>
        <div class="field"><div class="label">Event ID</div><input id="event-id" type="text" value="${this._escape(this._config.event_id)}" placeholder="Optional ESPN event ID"></div>
      </div>
    </div>`;

    const layout = this.shadowRoot.getElementById("layout");
    layout.value = compact ? "game_compact" : "game";
    layout.addEventListener("change", () => this._emit({
      preset: layout.value,
      entity: def.entity,
      ...(layout.value === "game_compact" ? { show_league: false, show_venue: false, show_broadcast: false } : {}),
    }));
    this._wireBool("show-logos", "show_logos");
    this._wireBool("show-league", "show_league");
    this._wireBool("show-records", "show_records");
    this._wireBool("show-venue", "show_venue");
    this._wireBool("show-broadcast", "show_broadcast");
    const eventId = this.shadowRoot.getElementById("event-id");
    eventId?.addEventListener("change", () => this._emit({ event_id: eventId.value.trim() || undefined }));
  }
}

class SportsTickerTickerCardEditor extends SportsTickerSplitEditorBase {
  _availableSports() {
    if (!this._hass) return [];
    return Object.entries(ST_SPLIT_SPORTS).filter(([key]) => stSplitAvailable(this._hass, key));
  }

  _render() {
    if (!this.shadowRoot) return;
    const available = this._availableSports();
    const keys = available.map(([key]) => key);
    const selected = Array.isArray(this._config.sports)
      ? this._config.sports.filter((key) => keys.includes(key))
      : keys.slice(0, 1);
    const checks = available.map(([key, def]) => `<label class="sport-option"><input type="checkbox" data-sport="${key}" ${selected.includes(key) ? "checked" : ""}><span>${def.label}</span></label>`).join("");

    this.shadowRoot.innerHTML = `${this._styles()}<div class="editor">
      ${available.length ? "" : '<div class="warning">No enabled Sports Ticker scoreboard sensors were found. Enable at least one sport in the integration options.</div>'}
      <div class="panel"><div class="title">Ticker sports</div><div class="helper">Only sports enabled in the Sports Ticker integration are shown here.</div><div class="sports">${checks}</div></div>
      <div class="panel">
        <div class="title">Ticker options</div>
        <label class="toggle"><input id="show-logos" type="checkbox" ${this._config.show_logos !== false ? "checked" : ""}>Show team logos</label>
        <label class="toggle"><input id="pause-hover" type="checkbox" ${this._config.ticker_pause_on_hover !== false ? "checked" : ""}>Pause on hover</label>
        <div class="row">
          <div class="field"><div class="label">Seconds per game</div><input id="speed" type="number" min="3" max="20" step="1" value="${Number(this._config.ticker_seconds_per_game) || 8}"></div>
          <div class="field"><div class="label">Max games per sport</div><input id="max-games" type="number" min="1" max="30" step="1" value="${Number(this._config.ticker_max_games_per_sport) || 20}"></div>
        </div>
      </div>
    </div>`;

    this.shadowRoot.querySelectorAll("[data-sport]").forEach((input) => input.addEventListener("change", () => {
      const sports = [...this.shadowRoot.querySelectorAll("[data-sport]:checked")].map((item) => item.dataset.sport);
      if (!sports.length) { input.checked = true; return; }
      this._emit({ preset: "ticker", sports });
    }));
    this._wireBool("show-logos", "show_logos");
    this._wireBool("pause-hover", "ticker_pause_on_hover");
    this._wireNumber("speed", "ticker_seconds_per_game", 3, 20);
    this._wireNumber("max-games", "ticker_max_games_per_sport", 1, 30);
  }
}

if (!customElements.get("sports-ticker-sport-card-editor")) customElements.define("sports-ticker-sport-card-editor", SportsTickerSportCardEditor);
if (!customElements.get("sports-ticker-ticker-card-editor")) customElements.define("sports-ticker-ticker-card-editor", SportsTickerTickerCardEditor);

const STBaseCard = customElements.get("sports-ticker-card");

if (STBaseCard) {
  class SportsTickerTickerCard extends STBaseCard {
    static getStubConfig(hass) {
      const sports = Object.keys(ST_SPLIT_SPORTS).filter((key) => stSplitAvailable(hass, key));
      return { preset: "ticker", sports: sports.slice(0, 1), show_logos: true, ticker_seconds_per_game: 8, ticker_max_games_per_sport: 20, ticker_pause_on_hover: true };
    }
    static async getConfigElement() { return document.createElement("sports-ticker-ticker-card-editor"); }
    setConfig(config) { super.setConfig({ ...config, preset: "ticker" }); }
  }
  if (!customElements.get("sports-ticker-ticker-card")) customElements.define("sports-ticker-ticker-card", SportsTickerTickerCard);

  for (const [key, def] of Object.entries(ST_SPLIT_SPORTS)) {
    const tag = `sports-ticker-${key}-card`;
    if (!customElements.get(tag)) {
      class SportsTickerSportCard extends STBaseCard {
        static sportKey = key;
        static getStubConfig() { return { entity: def.entity, preset: "game", show_logos: true, show_league: true, show_records: true, show_venue: true, show_broadcast: true }; }
        static async getConfigElement() {
          const editor = document.createElement("sports-ticker-sport-card-editor");
          editor.sportKey = key;
          return editor;
        }
        setConfig(config) {
          const preset = config?.preset === "game_compact" ? "game_compact" : "game";
          super.setConfig({ ...config, entity: def.entity, preset });
        }
      }
      customElements.define(tag, SportsTickerSportCard);
    }
  }

  window.customCards = (window.customCards || []).filter((card) => card.type !== "sports-ticker-card");
  const registrations = [
    {
      type: "sports-ticker-ticker-card",
      name: "Sports Ticker — Multi-Sport Ticker",
      description: "Scrolling ESPN-style ticker using the Sports Ticker leagues enabled in Home Assistant.",
      preview: true,
    },
    ...Object.entries(ST_SPLIT_SPORTS).map(([key, def]) => ({
      type: `sports-ticker-${key}-card`,
      name: `Sports Ticker — ${def.label}`,
      description: `${def.label} game card powered by the Sports Ticker integration.`,
      preview: true,
      getEntitySuggestion: (hass, entityId) => entityId === def.entity && stSplitAvailable(hass, key)
        ? { config: { type: `custom:sports-ticker-${key}-card`, entity: def.entity, preset: "game" } }
        : null,
    })),
  ];

  for (const registration of registrations) {
    if (!window.customCards.some((card) => card.type === registration.type)) {
      window.customCards.push({ ...registration, documentationURL: "https://github.com/LiquidFXX/sports-ticker" });
    }
  }
}

console.info(`%c SPORTS-TICKER-SPLIT %c v${SPORTS_TICKER_SPLIT_VERSION} `, "background:#444;color:#fff;font-weight:700", "background:#eee;color:#444");
