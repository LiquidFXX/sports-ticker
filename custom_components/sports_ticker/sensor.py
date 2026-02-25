from __future__ import annotations

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SportsTickerCoordinator = hass.data[DOMAIN][entry.entry_id]

    leagues = entry.options.get(CONF_LEAGUES, entry.data.get(CONF_LEAGUES, ["mlb", "nfl"]))
    create_raw = entry.options.get(CONF_CREATE_RAW, entry.data.get(CONF_CREATE_RAW, DEFAULT_CREATE_RAW))
    create_next = entry.options.get(CONF_CREATE_NEXT, entry.data.get(CONF_CREATE_NEXT, DEFAULT_CREATE_NEXT))

    entities: list[SensorEntity] = []
    for lg in leagues:
        if create_raw:
            entities.append(ESPNScoreboardRawSensor(coordinator, lg))
        if create_next:
            entities.append(SportsTickerNextSensor(coordinator, lg))

    async_add_entities(entities)


class _BaseTickerSensor(SensorEntity):
    def __init__(self, coordinator: SportsTickerCoordinator, league: str) -> None:
        self.coordinator = coordinator
        self.league = league

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self.league, {})
        return bool(data) and "error" not in data


class ESPNScoreboardRawSensor(_BaseTickerSensor):
    _attr_icon = "mdi:database-outline"

    def __init__(self, coordinator: SportsTickerCoordinator, league: str) -> None:
        super().__init__(coordinator, league)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.entry.entry_id}_{league}_raw"
        self._attr_name = f"ESPN {league.upper()} Scoreboard Raw"

    @property
    def native_value(self) -> str:
        # legacy behavior: store a timestamp-y value (like your now().isoformat())
        return self.coordinator.data.get(self.league, {}).get("fetched_at", "")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.get(self.league, {}).get("raw", {}) or {}
        # mimic your REST json_attributes set
        return {
            "events": raw.get("events"),
            "leagues": raw.get("leagues"),
            "day": raw.get("day"),
            "season": raw.get("season"),
        }


class SportsTickerNextSensor(_BaseTickerSensor):
    _attr_icon = "mdi:scoreboard-outline"

    def __init__(self, coordinator: SportsTickerCoordinator, league: str) -> None:
        super().__init__(coordinator, league)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.entry.entry_id}_{league}_next"
        self._attr_name = f"{league.upper()} Next"

    @property
    def native_value(self) -> str:
        nxt = self.coordinator.data.get(self.league, {}).get("next") or {}
        return nxt.get("shortName") or nxt.get("name") or "No games found"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.get(self.league, {})
        nxt = data.get("next") or {}
        events = data.get("events") or []
        return {
            "league": self.league,
            "fetched_at": data.get("fetched_at"),
            "next": {
                "id": nxt.get("id"),
                "uid": nxt.get("uid"),
                "date": nxt.get("date"),
                "name": nxt.get("name"),
                "shortName": nxt.get("shortName"),
                "competitions": nxt.get("competitions"),
            },
            # card-friendly list
            "events": [
                {"id": ev.get("id"), "date": ev.get("date"), "name": ev.get("name"), "shortName": ev.get("shortName")}
                for ev in events[:25]
            ],
        }
