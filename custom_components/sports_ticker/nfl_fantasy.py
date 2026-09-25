from __future__ import annotations

import json
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity, UpdateFailed
from homeassistant.util import dt as dt_util

FANTASY_PLAYERS_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/players"
NFL_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"
POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "D/ST"}
INJURY_STATUS = {0: "Active", 1: "Questionable", 2: "Doubtful", 3: "Out", 4: "Injured Reserve", 5: "PUP", 6: "Suspended"}


class NFLFantasyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch ESPN's public NFL fantasy player data and NFL injury report."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.session = async_get_clientsession(hass)
        self.entry = entry
        super().__init__(hass, __import__("logging").getLogger(__name__), name="sports_ticker_nfl_fantasy", update_interval=__import__("datetime").timedelta(minutes=15))

    async def _async_update_data(self) -> dict[str, Any]:
        now = dt_util.now()
        season = now.year
        week = self._week_from_nfl_sensor()
        try:
            players = await self._fetch_players(season, week)
            injuries = await self._fetch_injuries()
        except Exception as err:
            raise UpdateFailed(f"Unable to update ESPN NFL fantasy data: {err}") from err

        injured_ids = {str(item.get("athlete_id")): item for item in injuries if item.get("athlete_id")}
        for player in players:
            injury = injured_ids.get(str(player.get("athlete_id")))
            if injury:
                player["injury"] = injury

        leaders: dict[str, list[dict[str, Any]]] = {"overall": players[:25]}
        for position in ("QB", "RB", "WR", "TE", "K", "D/ST"):
            leaders[position.lower().replace("/", "")]=[p for p in players if p.get("position") == position][:25]

        return {"season": season, "week": week, "scoring": "espn_default", "leaders": leaders, "players": players[:300], "injuries": injuries, "updated_at": dt_util.utcnow().isoformat()}

    def _week_from_nfl_sensor(self) -> int:
        state = self.hass.states.get("sensor.espn_nfl_scoreboard_raw")
        if state:
            week = state.attributes.get("week")
            if isinstance(week, int) and 1 <= week <= 22:
                return week
            if isinstance(week, dict):
                number = week.get("number")
                if isinstance(number, int) and 1 <= number <= 22:
                    return number

            events = state.attributes.get("events")
            if isinstance(events, list):
                for event in events:
                    if not isinstance(event, dict):
                        continue
                    event_week = event.get("week")
                    if isinstance(event_week, dict):
                        number = event_week.get("number")
                        if isinstance(number, int) and 1 <= number <= 22:
                            return number
                    if isinstance(event_week, int) and 1 <= event_week <= 22:
                        return event_week
        return 1

    async def _fetch_players(self, season: int, week: int) -> list[dict[str, Any]]:
        url = FANTASY_PLAYERS_URL.format(season=season)
        params = {"scoringPeriodId": str(week), "view": "kona_player_info"}
        fantasy_filter = {"players": {"limit": 500, "sortPercOwned": {"sortPriority": 1, "sortAsc": False}}}
        headers = {"x-fantasy-filter": json.dumps(fantasy_filter), "x-fantasy-platform": "kona-PROD-1dc40132dc207d89781581d6a4c8100b3cc2458f", "x-fantasy-source": "kona"}
        async with async_timeout.timeout(20):
            response = await self.session.get(url, params=params, headers=headers)
            if response.status != 200:
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message="ESPN fantasy players request failed", headers=response.headers)
            payload = await response.json()
        items = payload if isinstance(payload, list) else payload.get("players", []) if isinstance(payload, dict) else []
        players = [self._normalize_player(item, week) for item in items if isinstance(item, dict)]
        players = [p for p in players if p.get("name") and p.get("position")]
        players.sort(key=lambda p: self._number(p.get("fantasy_points")), reverse=True)
        return players

    @staticmethod
    def _normalize_player(item: dict[str, Any], week: int) -> dict[str, Any]:
        player = item.get("player", item)
        athlete_id = player.get("id")
        stats = player.get("stats") if isinstance(player.get("stats"), list) else []
        weekly = next((s for s in stats if isinstance(s, dict) and s.get("scoringPeriodId") == week and s.get("statSourceId") == 0), None)
        projected = next((s for s in stats if isinstance(s, dict) and s.get("scoringPeriodId") == week and s.get("statSourceId") == 1), None)
        ownership = player.get("ownership") if isinstance(player.get("ownership"), dict) else {}
        injury_id = player.get("injuryStatus")
        return {"athlete_id": athlete_id, "name": player.get("fullName") or player.get("displayName"), "short_name": player.get("shortName"), "team_id": player.get("proTeamId"), "position": POSITIONS.get(player.get("defaultPositionId")), "fantasy_points": weekly.get("appliedTotal") if weekly else None, "projected_points": projected.get("appliedTotal") if projected else None, "rostered_pct": ownership.get("percentOwned"), "start_pct": ownership.get("percentStarted"), "roster_change": ownership.get("percentChange"), "injury_status": INJURY_STATUS.get(injury_id, injury_id), "active": player.get("active"), "stats": weekly.get("stats", {}) if weekly else {}}

    async def _fetch_injuries(self) -> list[dict[str, Any]]:
        async with async_timeout.timeout(20):
            response = await self.session.get(NFL_INJURIES_URL)
            if response.status != 200:
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message="ESPN NFL injuries request failed", headers=response.headers)
            payload = await response.json()
        injuries: list[dict[str, Any]] = []
        for team in payload.get("injuries", []) if isinstance(payload, dict) else []:
            if not isinstance(team, dict): continue
            team_info = team.get("team", {}) if isinstance(team.get("team"), dict) else {}
            for item in team.get("injuries", []) if isinstance(team.get("injuries"), list) else []:
                if not isinstance(item, dict): continue
                athlete = item.get("athlete", {}) if isinstance(item.get("athlete"), dict) else {}
                position = athlete.get("position", {}) if isinstance(athlete.get("position"), dict) else {}
                pos = position.get("abbreviation")
                if pos not in {"QB", "RB", "WR", "TE", "K"}: continue
                injuries.append({"athlete_id": athlete.get("id"), "name": athlete.get("displayName") or athlete.get("fullName"), "short_name": athlete.get("shortName"), "team": team_info.get("abbreviation"), "team_name": team_info.get("displayName"), "position": pos, "status": item.get("status"), "type": item.get("type", {}).get("description") if isinstance(item.get("type"), dict) else item.get("type"), "detail": item.get("details"), "date": item.get("date"), "headshot": athlete.get("headshot", {}).get("href") if isinstance(athlete.get("headshot"), dict) else None})
        return injuries

    @staticmethod
    def _number(value: Any) -> float:
        try: return float(value or 0)
        except (TypeError, ValueError): return 0.0


class ESPNNFLFantasyRaw(CoordinatorEntity[NFLFantasyCoordinator], SensorEntity):
    _attr_icon = "mdi:football"
    _attr_unique_id = "espn_nfl_fantasy_raw"
    _attr_name = "ESPN NFL Fantasy Raw"

    def __init__(self, coordinator: NFLFantasyCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def native_value(self) -> str:
        data = self.coordinator.data or {}
        return f"Week {data.get('week')} - {len(data.get('players', []))} players"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {"league": "nfl", "data_type": "fantasy", **data}
