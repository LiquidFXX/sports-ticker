from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    LEAGUES,
)

TIMEOUT = aiohttp.ClientTimeout(total=20)


def _parse_dt(dt_str: str) -> datetime | None:
    try:
        # ESPN gives "2026-02-23T18:05Z"
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def _pick_next_event(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc)
    dated = []
    for ev in events:
        dt = _parse_dt(ev.get("date", ""))
        if dt:
            dated.append((dt, ev))

    if not dated:
        return events[0] if events else None

    dated.sort(key=lambda x: x[0])

    for dt, ev in dated:
        if dt >= now:
            return ev

    # fallback to soonest
    return dated[0][1]


class SportsTickerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        self.session = aiohttp.ClientSession(timeout=TIMEOUT)

        poll = int(
            entry.options.get(CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        )

        super().__init__(
            hass=hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll),
        )

    async def _fetch(self, url: str) -> dict[str, Any]:
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"ESPN HTTP {resp.status} for {url}")
                return await resp.json()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    async def _async_update_data(self) -> dict[str, Any]:
        leagues = self.entry.options.get(CONF_LEAGUES, self.entry.data.get(CONF_LEAGUES, ["mlb", "nfl"]))
        if not isinstance(leagues, list):
            leagues = [str(leagues)]

        result: dict[str, Any] = {}
        fetched_at = datetime.now(timezone.utc).isoformat()

        # Fetch all selected leagues
        for key in leagues:
            url = LEAGUES.get(key)
            if not url:
                result[key] = {"error": "unknown_league", "fetched_at": fetched_at}
                continue

            try:
                raw = await self._fetch(url)
                events = raw.get("events") or []
                nxt = _pick_next_event(events)

                result[key] = {
                    "fetched_at": fetched_at,
                    "raw": raw,
                    "events": events,
                    "next": nxt,
                }
            except Exception as e:
                result[key] = {"error": str(e), "fetched_at": fetched_at}

        return result

    async def async_shutdown(self) -> None:
        await self.session.close()
