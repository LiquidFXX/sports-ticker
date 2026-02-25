from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_LEAGUES, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, LEAGUES

LOGGER = logging.getLogger(__name__)
TIMEOUT = aiohttp.ClientTimeout(total=30)


class SportsTickerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        self.session = aiohttp.ClientSession(timeout=TIMEOUT)
        self._last_fetch: dict[str, datetime] = {}

        poll = int(entry.options.get(CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)))

        super().__init__(
            hass=hass,
            logger=LOGGER,  # ✅ MUST NOT BE NONE
            name=DOMAIN,
            update_interval=timedelta(seconds=poll),
        )

    async def _fetch_json(self, url: str) -> dict[str, Any]:
        async with self.session.get(url) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"ESPN HTTP {resp.status}")
            return await resp.json()

    async def _async_update_data(self) -> dict[str, Any]:
        leagues = self.entry.options.get(CONF_LEAGUES, self.entry.data.get(CONF_LEAGUES, list(LEAGUES.keys())))
        if not isinstance(leagues, list):
            leagues = [leagues]

        now = datetime.now(timezone.utc)
        out: dict[str, Any] = {}

        for key in leagues:
            meta = LEAGUES.get(key)
            if not meta:
                out[key] = {"error": "unknown_league", "fetched_at": now.isoformat()}
                continue

            min_interval = int(meta.get("min_interval", 60))
            last = self._last_fetch.get(key)
            if last and (now - last).total_seconds() < min_interval:
                # keep previous data if we’re within min interval
                out[key] = self.data.get(key, {})
                continue

            try:
                raw = await self._fetch_json(meta["url"])
                self._last_fetch[key] = now
                out[key] = {
                    "fetched_at": now.isoformat(),
                    "raw": raw,
                    "events": raw.get("events") or [],
                    "leagues": raw.get("leagues"),
                    "day": raw.get("day"),
                    "season": raw.get("season"),
                }
            except Exception as e:
                out[key] = {"error": str(e), "fetched_at": now.isoformat()}

        return out

    async def async_shutdown(self) -> None:
        await self.session.close()