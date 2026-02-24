from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_SPORTS, LEAGUES
from .coordinator import SportsTickerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    sports = entry.options.get(CONF_SPORTS, entry.data.get(CONF_SPORTS, ["mlb"]))
    if isinstance(sports, str):
        sports = [s.strip() for s in sports.split(",") if s.strip()]

    entities: list[SensorEntity] = []
    for sport in sports:
        if sport in LEAGUES:
            entities.append(SportsTickerNextSensor(coordinator, sport))

    async_add_entities(entities)


class SportsTickerNextSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SportsTickerCoordinator, sport: str) -> None:
        self.coordinator = coordinator
        self.sport = sport

        # Stable and predictable IDs
        self._attr_unique_id = f"{DOMAIN}_{coordinator.entry.entry_id}_{sport}_next"
        self._attr_name = f"{sport.upper()} Ticker"
        self._attr_icon = "mdi:scoreboard-outline"

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self.sport, {})
        return bool(data) and "error" not in data

    @property
    def native_value(self) -> str:
        data = self.coordinator.data.get(self.sport, {})
        nxt = data.get("next") or {}
        return nxt.get("shortName") or nxt.get("name") or "No games found"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.get(self.sport, {})
        nxt = data.get("next") or {}
        events = data.get("events") or []

        return {
            "league": self.sport,
            "fetched_at": data.get("fetched_at"),
            "next": {
                "id": nxt.get("id"),
                "uid": nxt.get("uid"),
                "date": nxt.get("date"),
                "name": nxt.get("name"),
                "shortName": nxt.get("shortName"),
                "competitions": nxt.get("competitions"),
            },
            # Card-friendly list (keep it reasonably small)
            "events": [
                {
                    "id": ev.get("id"),
                    "date": ev.get("date"),
                    "name": ev.get("name"),
                    "shortName": ev.get("shortName"),
                }
                for ev in events[:25]
            ],
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))