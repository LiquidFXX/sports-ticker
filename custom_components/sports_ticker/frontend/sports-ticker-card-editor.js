const SPORTS_TICKER_EDITOR_VERSION = "0.2.0";

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
    this._advancedOpen = false;
  }

  set hass(hass) { this._hass = hass; this._render(); }
  setConfig(config) { this._config = { ...(config || {}) }; this._render(); }

  _availableSports() {
    if (!this._hass) return [];
    return Object.entries(ST_SPORTS).filter(([, sport]) => {
      const state = this._hass.states?.[sport.entity];
      return Boolean(state && Array.isArray(state.attributes?.events));
    });
  }

  _cardType() { return this._config.preset === "ticker" ? "ticker" : "game"; }
  _layout() { return this._config.preset === "game_compact" ? "compact" : "standard"; }

  _sportKey(available) {
    const configured = stSportForEntity(this._config.entity);
    if (configured && available.some(([key]) => key === configured)) return configured;
    return available[0]?.[0] || null;
  }

  _emit(next) {
    this._config = next;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: next }, bubbles: true, composed: true }));
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._hass) return;
    const available = this._availableSports();
    const availableKeys = available.map(([key]) => key);
    const cardType = this._cardType();
    const isTicker = cardType === "ticker";
    const sportKey = this._sportKey(available);
    const layout = this._layout();
    const selectedSports = Array.isArray(this._config.sports)
      ? this._config.sports.filter((key) => availableKeys.includes(key))
      : availableKeys.slice(0, 1);

    const sportOptions = available.map(([key, sport]) => `<option value="${key}">${sport.label}</option>`).join("");
    const sportChecks = available.map(([key, sport]) => `<label class="check"><input type="checkbox" data-sport="${key}" ${selectedSports.includes(key) ? "checked" : ""}><span>${sport.label}</span></label>`).join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,inherit)}
        .editor{display:grid;gap:22px;padding:4px 2px 18px}.section{display:grid;gap:13px}.section+.section{padding-top:20px;border-top:1px solid var(--divider-color)}
        .eyebrow{font-size:11px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--secondary-text-color)}
        .field{display:grid;gap:7px}.label{font-size:13px;font-weight:650}.helper{font-size:12px;line-height:1.45;color:var(--secondary-text-color)}
        select,input[type="number"],input[type="text"]{width:100%;box-sizing:border-box;min-height:48px;padding:10px 13px;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color,var(--ha-card-background));color:var(--primary-text-color);font:inherit}
        .options{display:grid}.toggle{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:48px;border-bottom:1px solid color-mix(in srgb,var(--divider-color) 70%,transparent);font-size:14px}.toggle:last-child{border-bottom:0}.toggle input,.check input{width:19px;height:19px;margin:0;accent-color:var(--primary-color)}
        .checks{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}.check{display:flex;align-items:center;gap:9px;min-height:38px;padding:0 4px;font-size:13px}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.advanced{border:1px solid var(--divider-color);border-radius:11px;overflow:hidden}.advanced-button{width:100%;min-height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border:0;background:transparent;color:var(--primary-text-color);font:inherit;font-weight:650;cursor:pointer}.advanced-body{display:grid;gap:13px;padding:14px;border-top:1px solid var(--divider-color)}
        .empty{padding:13px;border:1px dashed var(--divider-color);border-radius:10px;color:var(--secondary-text-color);font-size:13px}.auto{display:flex;align-items:flex-start;gap:8px;font-size:12px;line-height:1.45;color:var(--secondary-text-color)}.auto ha-icon{--mdc-icon-size:17px;margin-top:1px;color:var(--primary-color)}
        @media(max-width:520px){.row{grid-template-columns:1fr}}
      </style>
      <div class="editor">
        <section class="section">
          <div class="eyebrow">Basic setup</div>
          <div class="field"><div class="label">Card type</div><select id="card-type"><option value="game">Game</option><option value="ticker">Multi-Sport Ticker</option></select></div>
          ${available.length ? "" : '<div class="empty">No enabled Sports Ticker scoreboard sensors were found. Enable at least one sport in the integration options.</div>'}
          ${isTicker ? `
            <div class="field"><div class="label">Sports / Leagues</div><div class="checks">${sportChecks}</div><div class="helper">Only leagues enabled in the Sports Ticker integration are shown.</div></div>
          ` : `
            <div class="field"><div class="label">Sport / League</div><select id="sport">${sportOptions}</select></div>
            <div class="field"><div class="label">Layout</div><select id="layout"><option value="standard">Standard</option><option value="compact">Compact</option></select></div>
            <div class="auto"><ha-icon icon="mdi:information-outline"></ha-icon><span>The card automatically uses the selected league's Sports Ticker scoreboard data.</span></div>
          `}
        </section>

        ${isTicker ? `
          <section class="section"><div class="eyebrow">Ticker options</div><div class="options">
            ${this._toggle("show-logos", "Show team logos", this._config.show_logos !== false)}
            ${this._toggle("pause-hover", "Pause on hover", this._config.ticker_pause_on_hover !== false)}
          </div><div class="row">
            <div class="field"><div class="label">Seconds per game</div><input id="speed" type="number" min="3" max="20" step="1" value="${Number(this._config.ticker_seconds_per_game) || 8}"><div class="helper">Higher values scroll more slowly.</div></div>
            <div class="field"><div class="label">Maximum games per sport</div><input id="max-games" type="number" min="1" max="30" step="1" value="${Number(this._config.ticker_max_games_per_sport) || 20}"></div>
          </div></section>
        ` : `
          <section class="section"><div class="eyebrow">Game options</div><div class="options">
            ${this._toggle("show-league", "Show league", this._config.show_league !== false)}
            ${this._toggle("show-records", "Show team records", this._config.show_records !== false)}
            ${this._toggle("show-venue", "Show venue", this._config.show_venue !== false)}
            ${this._toggle("show-broadcast", "Show broadcast", this._config.show_broadcast !== false)}
            ${this._toggle("show-logos", "Show team logos", this._config.show_logos !== false)}
          </div></section>
        `}

        <div class="advanced"><button id="advanced-button" class="advanced-button" type="button"><span>Advanced options</span><ha-icon icon="mdi:chevron-${this._advancedOpen ? "up" : "down"}"></ha-icon></button>
          ${this._advancedOpen ? `<div class="advanced-body">${isTicker ? '<div class="helper">No advanced ticker options are required right now.</div>' : `<div class="field"><div class="label">Event ID</div><input id="event-id" type="text" value="${this._escapeAttr(this._config.event_id || "")}" placeholder="Optional ESPN event ID"><div class="helper">Pin this card to one ESPN event instead of automatic game selection.</div></div><div class="field"><div class="label">Entity override</div><input id="entity-override" type="text" value="${this._escapeAttr(this._config.entity || "")}" placeholder="sensor.espn_..."><div class="helper">Normally managed automatically. Change only for advanced/custom configurations.</div></div>`}</div>` : ""}
        </div>
      </div>`;

    const cardTypeEl = this.shadowRoot.getElementById("card-type");
    cardTypeEl.value = cardType;
    cardTypeEl.addEventListener("change", () => this._changeType(cardTypeEl.value, available));

    const advanced = this.shadowRoot.getElementById("advanced-button");
    advanced?.addEventListener("click", () => { this._advancedOpen = !this._advancedOpen; this._render(); });

    if (isTicker) this._wireTicker(selectedSports);
    else this._wireGame(sportKey, layout);
  }

  _toggle(id, label, checked) { return `<label class="toggle"><span>${label}</span><input id="${id}" type="checkbox" ${checked ? "checked" : ""}></label>`; }

  _changeType(type, available) {
    if (type === "ticker") {
      const enabled = available.map(([key]) => key);
      const sports = (Array.isArray(this._config.sports) ? this._config.sports : []).filter((key) => enabled.includes(key));
      this._emit({ ...this._config, preset: "ticker", sports: sports.length ? sports : enabled.slice(0, 1), show_logos: this._config.show_logos !== false, ticker_seconds_per_game: Number(this._config.ticker_seconds_per_game) || 8, ticker_max_games_per_sport: Number(this._config.ticker_max_games_per_sport) || 20, ticker_pause_on_hover: this._config.ticker_pause_on_hover !== false });
      return;
    }
    const [key, sport] = available[0] || [];
    if (!sport) return;
    this._emit({ ...this._config, preset: "game", entity: sport.entity, show_logos: true, show_league: true, show_records: true, show_venue: true, show_broadcast: true });
  }

  _wireTicker() {
    this.shadowRoot.querySelectorAll("[data-sport]").forEach((input) => input.addEventListener("change", () => {
      const sports = [...this.shadowRoot.querySelectorAll("[data-sport]:checked")].map((item) => item.dataset.sport);
      if (!sports.length) { input.checked = true; return; }
      this._emit({ ...this._config, preset: "ticker", sports });
    }));
    this._wireBool("show-logos", "show_logos"); this._wireBool("pause-hover", "ticker_pause_on_hover");
    this._wireNumber("speed", "ticker_seconds_per_game", 3, 20); this._wireNumber("max-games", "ticker_max_games_per_sport", 1, 30);
  }

  _wireGame(sportKey, layoutValue) {
    const sport = this.shadowRoot.getElementById("sport");
    if (sport) {
      sport.value = sportKey || "";
      sport.addEventListener("change", () => {
        const def = ST_SPORTS[sport.value]; if (!def) return;
        this._emit({ ...this._config, entity: def.entity });
      });
    }
    const layout = this.shadowRoot.getElementById("layout");
    if (layout) {
      layout.value = layoutValue;
      layout.addEventListener("change", () => {
        const compact = layout.value === "compact";
        this._emit({ ...this._config, preset: compact ? "game_compact" : "game", ...(compact ? { show_league: false, show_venue: false, show_broadcast: false } : {}) });
      });
    }
    this._wireBool("show-logos", "show_logos"); this._wireBool("show-league", "show_league"); this._wireBool("show-records", "show_records"); this._wireBool("show-venue", "show_venue"); this._wireBool("show-broadcast", "show_broadcast");
    const eventId = this.shadowRoot.getElementById("event-id"); eventId?.addEventListener("change", () => this._emit({ ...this._config, event_id: eventId.value.trim() || undefined }));
    const override = this.shadowRoot.getElementById("entity-override"); override?.addEventListener("change", () => this._emit({ ...this._config, entity: override.value.trim() || this._config.entity }));
  }

  _wireBool(id, key) { const input = this.shadowRoot.getElementById(id); input?.addEventListener("change", () => this._emit({ ...this._config, [key]: input.checked })); }
  _wireNumber(id, key, min, max) { const input = this.shadowRoot.getElementById(id); input?.addEventListener("change", () => { const value = Math.max(min, Math.min(max, Number(input.value) || min)); this._emit({ ...this._config, [key]: value }); }); }
  _escapeAttr(value) { return String(value).replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
}

if (!customElements.get("sports-ticker-card-editor")) customElements.define("sports-ticker-card-editor", SportsTickerCardEditor);
const SportsTickerCardClass = customElements.get("sports-ticker-card");
if (SportsTickerCardClass) SportsTickerCardClass.getConfigElement = async () => document.createElement("sports-ticker-card-editor");
console.info(`%c SPORTS-TICKER-EDITOR %c v${SPORTS_TICKER_EDITOR_VERSION} `, "background:#444;color:#fff;font-weight:700", "background:#eee;color:#444");
