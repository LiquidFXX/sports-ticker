const CARD_VERSION = "0.2.0";

const htmlEscape = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const asArray = (value) => Array.isArray(value) ? value : [];

const PRESETS = {
  game: {
    label: "Game — Standard",
    description: "Full matchup card with team logos, status, records and game details.",
    defaults: {
      show_league: true,
      show_records: true,
      show_venue: true,
      show_broadcast: true,
      show_logos: true,
    },
  },
  game_compact: {
    label: "Game — Compact",
    description: "Smaller matchup card for denser dashboards and mobile layouts.",
    defaults: {
      show_league: false,
      show_records: true,
      show_venue: false,
      show_broadcast: false,
      show_logos: true,
    },
  },
};

const isSportsTickerScoreboardEntity = (hass, entityId) => {
  const state = hass?.states?.[entityId];
  return Boolean(
    entityId?.startsWith("sensor.espn_") &&
    Array.isArray(state?.attributes?.events)
  );
};

class SportsTickerCard extends HTMLElement {
  static getStubConfig(hass) {
    const entity = Object.keys(hass?.states ?? {}).find((entityId) =>
      isSportsTickerScoreboardEntity(hass, entityId)
    );
    return entity ? { entity, preset: "game" } : { preset: "game" };
  }

  static getConfigForm() {
    const presetOptions = Object.entries(PRESETS).map(([value, preset]) => ({
      value,
      label: preset.label,
    }));

    return {
      schema: [
        {
          name: "preset",
          required: true,
          selector: { select: { mode: "dropdown", options: presetOptions } },
        },
        {
          name: "entity",
          required: true,
          selector: { entity: { domain: "sensor" } },
        },
        {
          type: "expandable",
          name: "display",
          title: "Display options",
          flatten: true,
          schema: [
            { name: "show_league", selector: { boolean: {} } },
            { name: "show_logos", selector: { boolean: {} } },
            { name: "show_records", selector: { boolean: {} } },
            { name: "show_venue", selector: { boolean: {} } },
            { name: "show_broadcast", selector: { boolean: {} } },
          ],
        },
        {
          type: "expandable",
          name: "advanced",
          title: "Advanced",
          flatten: true,
          schema: [
            {
              name: "event_id",
              selector: { text: {} },
            },
          ],
        },
      ],
      computeLabel: (schema) => ({
        preset: "Card style",
        entity: "Sports Ticker entity",
        show_league: "Show league",
        show_logos: "Show team logos",
        show_records: "Show team records",
        show_venue: "Show venue",
        show_broadcast: "Show broadcast",
        event_id: "Event ID",
      }[schema.name]),
      computeHelper: (schema) => ({
        preset: "Choose a pre-made Sports Ticker layout. More card families will appear here as they are added.",
        entity: "Choose a Sports Ticker raw scoreboard sensor containing ESPN events.",
        event_id: "Optional. Pin this card to a specific ESPN event instead of automatically choosing the favorite, live, or next game.",
      }[schema.name]),
      assertConfig: (config) => {
        if (config.preset && !PRESETS[config.preset]) {
          throw new Error(`Unknown Sports Ticker preset: ${config.preset}`);
        }
      },
    };
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("Sports Ticker card requires an entity");
    }

    const presetName = PRESETS[config.preset] ? config.preset : "game";
    const preset = PRESETS[presetName];
    this._config = {
      preset: presetName,
      ...preset.defaults,
      ...config,
    };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return this._config?.preset === "game_compact" ? 3 : 4;
  }

  getGridOptions() {
    if (this._config?.preset === "game_compact") {
      return { columns: 12, rows: 3, min_columns: 6, min_rows: 2 };
    }
    return { columns: 12, rows: 4, min_columns: 6, min_rows: 3 };
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;

    const stateObj = this._hass.states[this._config.entity];
    if (!stateObj) {
      this.shadowRoot.innerHTML = this._styles() + this._message(`Entity not found: ${this._config.entity}`);
      return;
    }

    const attrs = stateObj.attributes ?? {};
    const events = asArray(attrs.events);
    if (!events.length) {
      this.shadowRoot.innerHTML = this._styles() + this._message("No games are currently available.");
      return;
    }

    const event = this._selectEvent(events, attrs.favorite_team, this._config.event_id);
    const game = this._normalizeEvent(event);
    if (!game) {
      this.shadowRoot.innerHTML = this._styles() + this._message("Game data is not available.");
      return;
    }

    const league = attrs.league_name || attrs.league || "Sports Ticker";
    const stale = Boolean(attrs.stale);
    const stateClass = game.completed ? "final" : game.live ? "live" : "scheduled";
    const compact = this._config.preset === "game_compact";

    this.shadowRoot.innerHTML = `${this._styles()}
      <ha-card>
        <div class="card ${stateClass} ${compact ? "compact" : "standard"}">
          <div class="header">
            <div class="header-left">
              ${this._config.show_league ? `<span class="league">${htmlEscape(String(league).toUpperCase())}</span>` : ""}
              ${stale ? '<span class="badge stale">CACHED</span>' : ""}
            </div>
            <div class="status-wrap">
              ${game.live ? '<span class="live-dot" aria-hidden="true"></span>' : ""}
              <span class="status">${htmlEscape(game.status)}</span>
            </div>
          </div>

          <div class="matchup">
            ${this._team(game.away, game.completed || game.live)}
            <div class="center">
              ${game.live || game.completed
                ? `<div class="scoreline"><span>${htmlEscape(game.away.score)}</span><span class="score-separator">–</span><span>${htmlEscape(game.home.score)}</span></div>`
                : `<div class="versus">@</div>`}
              <div class="detail">${htmlEscape(game.detail)}</div>
            </div>
            ${this._team(game.home, game.completed || game.live)}
          </div>

          ${this._config.show_records ? `
            <div class="records">
              <span>${htmlEscape(game.away.record || "")}</span>
              <span>${htmlEscape(game.home.record || "")}</span>
            </div>` : ""}

          ${(this._config.show_venue && game.venue) || (this._config.show_broadcast && game.broadcast) ? `
            <div class="footer">
              ${this._config.show_venue && game.venue ? `<span class="meta"><ha-icon icon="mdi:map-marker-outline"></ha-icon>${htmlEscape(game.venue)}</span>` : ""}
              ${this._config.show_broadcast && game.broadcast ? `<span class="meta"><ha-icon icon="mdi:television"></ha-icon>${htmlEscape(game.broadcast)}</span>` : ""}
            </div>` : ""}
        </div>
      </ha-card>`;
  }

  _selectEvent(events, favoriteTeam, eventId) {
    if (eventId) {
      const configured = events.find((event) => String(event?.id) === String(eventId));
      if (configured) return configured;
    }

    if (favoriteTeam) {
      const favorite = String(favoriteTeam).toUpperCase();
      const match = events.find((event) => {
        const competitors = asArray(event?.competitions?.[0]?.competitors);
        return competitors.some((competitor) => {
          const team = competitor?.team ?? {};
          return [team.abbreviation, team.shortDisplayName, team.displayName]
            .filter(Boolean)
            .some((value) => String(value).toUpperCase() === favorite);
        });
      });
      if (match) return match;
    }

    const live = events.find((event) => this._statusType(event)?.state === "in");
    if (live) return live;

    const upcoming = events.find((event) => this._statusType(event)?.state === "pre");
    return upcoming || events[0];
  }

  _statusType(event) {
    return event?.status?.type ?? event?.competitions?.[0]?.status?.type ?? {};
  }

  _normalizeEvent(event) {
    const competition = event?.competitions?.[0] ?? {};
    const competitors = asArray(competition.competitors);
    const home = competitors.find((team) => team?.homeAway === "home") ?? competitors[0];
    const away = competitors.find((team) => team?.homeAway === "away") ?? competitors[1];
    if (!home || !away) return null;

    const statusType = this._statusType(event);
    const state = statusType?.state;
    const live = state === "in";
    const completed = state === "post" || Boolean(statusType?.completed);
    const status = statusType?.shortDetail || statusType?.detail || statusType?.description || (completed ? "Final" : live ? "Live" : "Scheduled");
    const date = competition.date || event?.date;
    const detail = live || completed ? status : this._formatDate(date);

    const broadcasts = asArray(competition.broadcasts)
      .flatMap((broadcast) => asArray(broadcast?.names))
      .filter(Boolean);
    const venue = competition?.venue?.fullName || competition?.venue?.address?.city || "";

    return {
      live,
      completed,
      status,
      detail,
      venue,
      broadcast: [...new Set(broadcasts)].join(", "),
      home: this._normalizeTeam(home),
      away: this._normalizeTeam(away),
    };
  }

  _normalizeTeam(competitor) {
    const team = competitor?.team ?? {};
    const records = asArray(competitor?.records);
    const overall = records.find((record) => record?.type === "total") || records.find((record) => record?.name === "overall") || records[0];
    const rank = competitor?.curatedRank?.current || competitor?.rank;
    const name = team.shortDisplayName || team.displayName || team.name || team.abbreviation || "Team";
    return {
      name: rank && Number(rank) > 0 && Number(rank) <= 25 ? `#${rank} ${name}` : name,
      abbreviation: team.abbreviation || "",
      logo: team.logo || asArray(team.logos)[0]?.href || "",
      score: competitor?.score ?? "0",
      record: overall?.summary || "",
      winner: Boolean(competitor?.winner),
    };
  }

  _formatDate(value) {
    if (!value) return "Scheduled";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    try {
      return new Intl.DateTimeFormat(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      }).format(date);
    } catch (_err) {
      return date.toLocaleString();
    }
  }

  _team(team, showScoreState) {
    const logo = this._config.show_logos
      ? `<div class="logo-wrap">${team.logo
          ? `<img class="logo" src="${htmlEscape(team.logo)}" alt="${htmlEscape(team.name)} logo" loading="lazy">`
          : `<div class="logo fallback">${htmlEscape(team.abbreviation.slice(0, 3))}</div>`}</div>`
      : "";

    return `<div class="team ${showScoreState && team.winner ? "winner" : ""}">
      ${logo}
      <div class="team-name" title="${htmlEscape(team.name)}">${htmlEscape(team.name)}</div>
    </div>`;
  }

  _message(message) {
    return `<ha-card><div class="message">${htmlEscape(message)}</div></ha-card>`;
  }

  _styles() {
    return `<style>
      :host { display: block; --st-gap: 16px; }
      ha-card { overflow: hidden; }
      .card {
        padding: 16px 18px;
        color: var(--primary-text-color);
        background: var(--ha-card-background, var(--card-background-color));
      }
      .header, .footer, .records {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .header { min-height: 24px; margin-bottom: 12px; }
      .header-left, .status-wrap, .meta { display: inline-flex; align-items: center; gap: 6px; }
      .league {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .08em;
        color: var(--secondary-text-color);
      }
      .badge {
        padding: 2px 6px;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .06em;
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }
      .status { font-size: 12px; font-weight: 650; }
      .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--error-color);
        box-shadow: 0 0 0 3px color-mix(in srgb, var(--error-color) 18%, transparent);
      }
      .matchup {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
        align-items: center;
        gap: var(--st-gap);
      }
      .team { min-width: 0; text-align: center; opacity: .86; }
      .team.winner { opacity: 1; }
      .logo-wrap { display: grid; place-items: center; height: 72px; margin-bottom: 7px; }
      .logo { max-width: 68px; max-height: 68px; object-fit: contain; }
      .logo.fallback {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
        font-weight: 700;
      }
      .team-name {
        font-size: 14px;
        font-weight: 650;
        line-height: 1.25;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .center { min-width: 92px; text-align: center; }
      .scoreline {
        display: flex;
        justify-content: center;
        align-items: baseline;
        gap: 8px;
        font-size: clamp(24px, 6vw, 38px);
        font-weight: 750;
        font-variant-numeric: tabular-nums;
        line-height: 1;
      }
      .score-separator { color: var(--disabled-text-color); font-weight: 400; }
      .versus { font-size: 20px; font-weight: 700; color: var(--secondary-text-color); }
      .detail {
        margin-top: 6px;
        max-width: 145px;
        font-size: 11px;
        line-height: 1.3;
        color: var(--secondary-text-color);
      }
      .records {
        margin-top: 8px;
        padding: 0 max(8px, 7%);
        font-size: 11px;
        color: var(--secondary-text-color);
      }
      .footer {
        margin-top: 14px;
        padding-top: 11px;
        border-top: 1px solid var(--divider-color);
        flex-wrap: wrap;
        justify-content: center;
        color: var(--secondary-text-color);
        font-size: 11px;
      }
      .meta ha-icon { --mdc-icon-size: 15px; }
      .message { padding: 20px; color: var(--secondary-text-color); }

      .card.compact { padding: 12px 14px; }
      .card.compact .header { margin-bottom: 7px; min-height: 20px; }
      .card.compact .logo-wrap { height: 48px; margin-bottom: 3px; }
      .card.compact .logo { max-width: 44px; max-height: 44px; }
      .card.compact .logo.fallback { width: 42px; height: 42px; font-size: 11px; }
      .card.compact .team-name { font-size: 12px; }
      .card.compact .center { min-width: 72px; }
      .card.compact .scoreline { font-size: clamp(22px, 5vw, 30px); gap: 5px; }
      .card.compact .detail { margin-top: 3px; font-size: 10px; max-width: 110px; }
      .card.compact .records { margin-top: 5px; font-size: 10px; }
      .card.compact .footer { margin-top: 8px; padding-top: 7px; }

      @media (max-width: 420px) {
        :host { --st-gap: 8px; }
        .card { padding: 14px 12px; }
        .logo-wrap { height: 58px; }
        .logo { max-width: 54px; max-height: 54px; }
        .team-name { font-size: 12px; }
        .center { min-width: 78px; }
        .detail { max-width: 105px; font-size: 10px; }
        .footer { gap: 8px; }
        .card.compact { padding: 10px; }
        .card.compact .logo-wrap { height: 42px; }
        .card.compact .logo { max-width: 38px; max-height: 38px; }
        .card.compact .center { min-width: 62px; }
      }
    </style>`;
  }
}

if (!customElements.get("sports-ticker-card")) {
  customElements.define("sports-ticker-card", SportsTickerCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "sports-ticker-card")) {
  window.customCards.push({
    type: "sports-ticker-card",
    name: "Sports Ticker",
    description: "Sports Ticker dashboard cards with selectable pre-made layouts and per-card options.",
    preview: true,
    documentationURL: "https://github.com/LiquidFXX/sports-ticker",
    getEntitySuggestion: (hass, entityId) => {
      if (!isSportsTickerScoreboardEntity(hass, entityId)) return null;
      return {
        config: {
          type: "custom:sports-ticker-card",
          entity: entityId,
          preset: "game",
        },
      };
    },
  });
}

console.info(
  `%c SPORTS-TICKER-CARD %c v${CARD_VERSION} `,
  "background:#444;color:#fff;font-weight:700",
  "background:#eee;color:#444"
);
