from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_TICKER_SPEED,
    CONF_TICKER_THEME,
    DEFAULT_TICKER_SPEED,
    DEFAULT_TICKER_THEME,
    LEAGUES,
)
from .coordinator import SportsTickerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    leagues = entry.options.get(CONF_LEAGUES, entry.data.get(CONF_LEAGUES, ["mlb", "nfl"]))
    if not isinstance(leagues, list):
        leagues = [leagues]
    leagues = [str(x).strip().lower() for x in leagues]

    entities: list[SensorEntity] = []
    for lg in leagues:
        meta = LEAGUES.get(lg)
        if not meta:
            continue
        entities.append(ESPNRawScoreboardSensor(coordinator, entry, lg, str(meta["name"])))

    async_add_entities(entities, update_before_add=True)


class ESPNRawScoreboardSensor(SensorEntity):
    _attr_icon = "mdi:scoreboard-outline"
    _attr_has_entity_name = True

    def __init__(self, coordinator: SportsTickerCoordinator, entry: ConfigEntry, league_key: str, league_name: str) -> None:
        self.coordinator = coordinator
        self.entry = entry
        self.league_key = league_key
        self.league_name = league_name

        # Unique per config entry + league
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{league_key}_scoreboard_raw"
        self._attr_name = f"ESPN {league_name} Scoreboard Raw"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self.league_key, {})
        return bool(data) and "error" not in data

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get(self.league_key, {}).get("fetched_at", "")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data.get(self.league_key, {})
        # expose UI options so the card can optionally read them
        speed = self.entry.options.get(CONF_TICKER_SPEED, DEFAULT_TICKER_SPEED)
        theme = self.entry.options.get(CONF_TICKER_THEME, DEFAULT_TICKER_THEME)

        return {
            "events": d.get("events", []),
            "leagues": d.get("leagues"),
            "day": d.get("day"),
            "season": d.get("season"),
            "ticker_speed": speed,
            "ticker_theme": theme,
        }