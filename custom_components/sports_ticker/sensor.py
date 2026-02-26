from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_SPORTS, LEAGUES
from .coordinator import SportsTickerCoordinator


@dataclass(frozen=True)
class SportsTickerSensorDescription(SensorEntityDescription):
    sport: str | None = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    sports = entry.options.get(CONF_SPORTS, entry.data.get(CONF_SPORTS, ["mlb"]))
    if isinstance(sports, str):
        sports = [s.strip() for s in sports.split(",") if s.strip()]

    entities: list[SensorEntity] = []
    for sport in sports:
        if sport not in LEAGUES:
            continue
        entities.append(SportsTickerNextEventSensor(coordinator, sport))

    async_add_entities(entities)


class SportsTickerNextEventSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SportsTickerCoordinator, sport: str) -> None:
        self.coordinator = coordinator
        self.sport = sport
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{sport}_next"
        self._attr_name = f"{sport.upper()} Next Game"

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self.sport, {})
        return bool(data) and "error" not in data

    @property
    def state(self) -> str | None:
        data = self.coordinator.data.get(self.sport, {})
        nxt = data.get("next") or {}
        return nxt.get("shortName") or nxt.get("name")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.get(self.sport, {})
        nxt = data.get("next") or {}

        # Pass through useful ESPN fields for cards/templates
        return {
            "sport": self.sport,
            "fetched_at": data.get("fetched_at"),
            "id": nxt.get("id"),
            "uid": nxt.get("uid"),
            "date": nxt.get("date"),
            "name": nxt.get("name"),
            "shortName": nxt.get("shortName"),
            "season": nxt.get("season"),
            "competitions": nxt.get("competitions"),
        }

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))