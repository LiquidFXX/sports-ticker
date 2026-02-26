from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_LEAGUES, LEAGUES
from .coordinator import SportsTickerCoordinator


def _normalize_leagues(value) -> list[str]:
    """Normalize stored leagues into list[str] of known league keys."""
    if value is None:
        return []
    # Sometimes multi-select style storage ends up as dict: {"mlb": True, "nfl": True}
    if isinstance(value, dict):
        value = [k for k, v in value.items() if v]
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        value = list(value)

    out: list[str] = []
    for v in value:
        k = str(v).strip().lower()
        if k in LEAGUES and k not in out:
            out.append(k)
    return out


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    stored = entry.options.get(CONF_LEAGUES, entry.data.get(CONF_LEAGUES, ["mlb", "nfl"]))
    leagues = _normalize_leagues(stored)

    async_add_entities(
        [ESPNRawScoreboard(coordinator, lg) for lg in leagues],
        update_before_add=True,
    )


class ESPNRawScoreboard(SensorEntity):
    _attr_icon = "mdi:scoreboard-outline"

    def __init__(self, coordinator: SportsTickerCoordinator, league: str) -> None:
        self.coordinator = coordinator
        self.league = league

        # Ensures entity_id is sensor.espn_<league>_scoreboard_raw
        self._attr_unique_id = f"espn_{league}_scoreboard_raw"
        self._attr_name = f"ESPN {league.upper()} Scoreboard Raw"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        d = self.coordinator.data.get(self.league, {})
        return bool(d) and "error" not in d

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get(self.league, {}).get("fetched_at", "")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data.get(self.league, {})
        return {
            "events": d.get("events", []),
            "leagues": d.get("leagues"),
            "day": d.get("day"),
            "season": d.get("season"),
        }