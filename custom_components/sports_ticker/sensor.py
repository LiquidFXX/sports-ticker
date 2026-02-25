from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_CREATE_RAW,
    CONF_CREATE_NEXT,
    DEFAULT_CREATE_RAW,
    DEFAULT_CREATE_NEXT,
)
from .coordinator import SportsTickerCoordinator


# Map league key -> labels + "no games" message to match your templates
LEAGUE_META = {
    "nfl":   {"label": "NFL",   "none": "No NFL games today"},
    "cfb":   {"label": "CFB",   "none": "No CFB games today"},
    "mlb":   {"label": "MLB",   "none": "No MLB games today"},
    "nba":   {"label": "NBA",   "none": "No NBA games today"},
    "nhl":   {"label": "NHL",   "none": "No NHL games today"},
    "wnba":  {"label": "WNBA",  "none": "No WNBA games today"},
    "ncaam": {"label": "NCAAM", "none": "No NCAAM games today"},
    "ncaaw": {"label": "NCAAW", "none": "No NCAAW games today"},
    "epl":   {"label": "EPL",   "none": "No EPL matches today"},
    "mls":   {"label": "MLS",   "none": "No MLS matches today"},
    "laliga": {"label": "LaLiga", "none": "No LaLiga matches today"},
    "bundesliga": {"label": "Bundesliga", "none": "No Bundesliga matches today"},
    "seriea": {"label": "Serie A", "none": "No Serie A matches today"},
    "ligue1": {"label": "Ligue 1", "none": "No Ligue 1 matches today"},
    "ucl":   {"label": "UCL",   "none": "No UCL matches today"},
    "uecl":  {"label": "UECL",  "none": "No UECL matches today"},
    "f1":    {"label": "F1",    "none": "No F1 events today"},
    "nascar": {"label": "NASCAR", "none": "No NASCAR events today"},
}


def _safe_get(d: Any, *path, default=None):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


def _fmt_local_time(iso_z: str) -> str:
    # input like "2026-02-23T18:05Z"
    try:
        dt = datetime.fromisoformat(iso_z.replace("Z", "+00:00")).astimezone()
        # match your template: %-I:%M%p  (Windows strftime may not support %-I)
        # Use a portable format and strip leading zero.
        s = dt.strftime("%I:%M%p")
        return s.lstrip("0")
    except Exception:
        return ""


def _format_ticker(events: list[dict[str, Any]], none_msg: str) -> str:
    if not events:
        return none_msg

    out: list[str] = []
    for e in events:
        comp0 = _safe_get(e, "competitions", 0)
        if not isinstance(comp0, dict):
            continue

        competitors = comp0.get("competitors") or []
        if not isinstance(competitors, list) or len(competitors) < 2:
            continue

        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        if not away or not home:
            continue

        a = _safe_get(away, "team", "abbreviation", default="AWAY")
        h = _safe_get(home, "team", "abbreviation", default="HOME")
        a_score = away.get("score", "0") or "0"
        h_score = home.get("score", "0") or "0"

        st_state = _safe_get(e, "status", "type", "state", default="")
        st_short = _safe_get(e, "status", "type", "shortDetail", default="")

        if st_state == "pre":
            when = _fmt_local_time(e.get("date", ""))
            out.append(f"{a} @ {h} ({when})" if when else f"{a} @ {h}")
        else:
            # Matches your template: "A as @ H hs (st)"
            out.append(f"{a} {a_score} @ {h} {h_score} ({st_short})" if st_short else f"{a} {a_score} @ {h} {h_score}")

    return "  •  ".join(out) if out else none_msg


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    leagues = entry.options.get(CONF_LEAGUES, entry.data.get(CONF_LEAGUES, ["mlb", "nfl"]))
    create_raw = entry.options.get(CONF_CREATE_RAW, entry.data.get(CONF_CREATE_RAW, DEFAULT_CREATE_RAW))
    create_next = entry.options.get(CONF_CREATE_NEXT, entry.data.get(CONF_CREATE_NEXT, DEFAULT_CREATE_NEXT))

    entities: list[SensorEntity] = []
    for lg in leagues:
        meta = LEAGUE_META.get(lg, {"label": lg.upper(), "none": f"No {lg.upper()} games today"})
        label = meta["label"]

        if create_raw:
            entities.append(ESPNScoreboardRawSensor(coordinator, lg, label))

        # create_next toggles “ticker-style” sensors too (keeps the UI simple)
        if create_next:
            entities.append(ESPNTickerSensor(coordinator, lg, label, meta["none"]))

    async_add_entities(entities)


class _Base(SensorEntity):
    def __init__(self, coordinator: SportsTickerCoordinator, league: str) -> None:
        self.coordinator = coordinator
        self.league = league

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self.league, {})
        return bool(data) and "error" not in data


class ESPNScoreboardRawSensor(_Base):
    _attr_icon = "mdi:database-outline"

    def __init__(self, coordinator: SportsTickerCoordinator, league: str, label: str) -> None:
        super().__init__(coordinator, league)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.entry.entry_id}_{league}_scoreboard_raw"
        self._attr_name = f"ESPN {label} Scoreboard Raw"

    @property
    def native_value(self) -> str:
        # Mimics your REST sensor "now().isoformat()" behavior as an update marker
        return self.coordinator.data.get(self.league, {}).get("fetched_at", "")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.get(self.league, {}).get("raw", {}) or {}
        return {
            "events": raw.get("events"),
            "leagues": raw.get("leagues"),
            "day": raw.get("day"),
            "season": raw.get("season"),
        }


class ESPNTickerSensor(_Base):
    _attr_icon = "mdi:scoreboard"

    def __init__(self, coordinator: SportsTickerCoordinator, league: str, label: str, none_msg: str) -> None:
        super().__init__(coordinator, league)
        self.none_msg = none_msg
        self._attr_unique_id = f"{DOMAIN}_{coordinator.entry.entry_id}_{league}_ticker"
        self._attr_name = f"ESPN {label} Ticker"

    @property
    def native_value(self) -> int:
        events = self.coordinator.data.get(self.league, {}).get("events") or []
        return len(events) if isinstance(events, list) else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        events = self.coordinator.data.get(self.league, {}).get("events") or []
        if not isinstance(events, list):
            events = []

        return {
            "ticker": _format_ticker(events, self.none_msg)
        }
