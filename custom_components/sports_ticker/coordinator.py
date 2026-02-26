from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_SPORTS, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, LEAGUES


ESPN_SCOREBOARD = "https://site.web.api.espn.com/apis/v2/sports/{league}/scoreboard"


def _parse_dt(dt_str: str) -> datetime | None:
    # ESPN returns ISO8601 like "2026-02-23T18:05Z"
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


class SportsTickerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self._session = aiohttp.ClientSession()

        poll = entry.options.get(CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        super().__init__(
            hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(seconds=int(poll)),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        sports = self.entry.options.get(CONF_SPORTS, self.entry.data.get(CONF_SPORTS, ["mlb"]))
        # If config_flow ended up giving a string like "mlb,nfl", normalize:
        if isinstance(sports, str):
            sports = [s.strip() for s in sports.split(",") if s.strip()]

        async def fetch_one(sport_key: str) -> tuple[str, Any]:
            league = LEAGUES.get(sport_key)
            if not league:
                return sport_key, {"error": "unknown_league"}

            url = ESPN_SCOREBOARD.format(league=league)
            try:
                async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"ESPN HTTP {resp.status}")
                    data = await resp.json()
            except Exception as e:
                return sport_key, {"error": str(e)}

            events = data.get("events") or []
            # Sort by date, pick next upcoming or most recent
            def key_fn(ev):
                dt = _parse_dt(ev.get("date", ""))
                return dt or datetime.max.replace(tzinfo=None)

            events_sorted = sorted(events, key=key_fn)

            next_event = None
            now = datetime.now(tz=datetime.now().astimezone().tzinfo)

            for ev in events_sorted:
                dt = _parse_dt(ev.get("date", ""))
                if dt and dt >= now:
                    next_event = ev
                    break

            # fallback to first event if nothing upcoming
            if not next_event and events_sorted:
                next_event = events_sorted[0]

            return sport_key, {
                "events": events_sorted[:25],
                "next": next_event,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
            }

        results = await asyncio.gather(*(fetch_one(s) for s in sports))
        return {k: v for k, v in results}

    async def async_shutdown(self):
        await self._session.close()