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

FANTASY_DEFAULTS_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leaguedefaults/3"
NFL_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"
POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "D/ST"}
NFL_TEAMS = {1:"ATL",2:"BUF",3:"CHI",4:"CIN",5:"CLE",6:"DAL",7:"DEN",8:"DET",9:"GB",10:"TEN",11:"IND",12:"KC",13:"LV",14:"LAR",15:"MIA",16:"MIN",17:"NE",18:"NO",19:"NYG",20:"NYJ",21:"PHI",22:"ARI",23:"PIT",24:"LAC",25:"SF",26:"SEA",27:"TB",28:"WSH",29:"CAR",30:"JAX",33:"BAL",34:"HOU"}
STAT_NAMES = {0:"passing_attempts",1:"passing_completions",3:"passing_yards",4:"passing_tds",20:"passing_interceptions",23:"rushing_attempts",24:"rushing_yards",25:"rushing_tds",41:"receptions",42:"receiving_yards",43:"receiving_tds",53:"receiving_targets",72:"fumbles",74:"fumbles_lost"}


class NFLFantasyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch ESPN public NFL fantasy player data and NFL injury report."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.session = async_get_clientsession(hass)
        self.entry = entry
        super().__init__(hass, __import__("logging").getLogger(__name__), name="sports_ticker_nfl_fantasy", update_interval=__import__("datetime").timedelta(minutes=15))

    async def _async_update_data(self) -> dict[str, Any]:
        season = dt_util.now().year
        week = self._week_from_nfl_sensor()
        try:
            players = await self._fetch_players(season, week)
            injuries = await self._fetch_injuries()
        except Exception as err:
            raise UpdateFailed(f"Unable to update ESPN NFL fantasy data: {err}") from err

        injured_ids = {str(i.get("athlete_id")): i for i in injuries if i.get("athlete_id")}
        for player in players:
            injury = injured_ids.get(str(player.get("athlete_id")))
            if injury:
                player["injury"] = injury
                player["injury_status"] = injury.get("status") or player.get("injury_status")

        leaders = {"overall": players[:25]}
        for position in ("QB", "RB", "WR", "TE", "K", "D/ST"):
            leaders[position.lower().replace("/", "")] = [p for p in players if p.get("position") == position][:25]

        return {"season": season, "week": week, "scoring": "espn_ppr_default", "leaders": leaders, "players": players[:300], "injuries": injuries, "updated_at": dt_util.utcnow().isoformat()}

    def _week_from_nfl_sensor(self) -> int:
        state = self.hass.states.get("sensor.espn_nfl_scoreboard_raw")
        if state:
            week = state.attributes.get("week")
            if isinstance(week, int) and 1 <= week <= 22:
                return week
            events = state.attributes.get("events")
            if isinstance(events, list):
                for event in events:
                    if not isinstance(event, dict):
                        continue
                    event_week = event.get("week")
                    if isinstance(event_week, dict):
                        value = event_week.get("number")
                        if isinstance(value, int) and 1 <= value <= 22:
                            return value
        return 1

    async def _fetch_players(self, season: int, week: int) -> list[dict[str, Any]]:
        url = FANTASY_DEFAULTS_URL.format(season=season)
        params = {"scoringPeriodId": str(week), "view": "kona_player_info"}
        fantasy_filter = {"players": {"filterActive": {"value": True}, "limit": 500, "sortAppliedStatTotal": {"sortAsc": False, "sortPriority": 1}, "sortPercOwned": {"sortAsc": False, "sortPriority": 2}}}
        headers = {"x-fantasy-filter": json.dumps(fantasy_filter), "x-fantasy-source": "kona"}
        async with async_timeout.timeout(20):
            response = await self.session.get(url, params=params, headers=headers)
            if response.status != 200:
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message="ESPN fantasy defaults request failed", headers=response.headers)
            payload = await response.json()
        items = payload.get("players", []) if isinstance(payload, dict) else []
        players = [self._normalize_player(item, week) for item in items if isinstance(item, dict)]
        players = [p for p in players if p.get("name") and p.get("position") and p.get("active")]
        players.sort(key=lambda p: self._number(p.get("fantasy_points")), reverse=True)
        return players

    @staticmethod
    def _normalize_player(item: dict[str, Any], week: int) -> dict[str, Any]:
        player = item.get("player", item)
        stats = player.get("stats") if isinstance(player.get("stats"), list) else []
        weekly = next((s for s in stats if isinstance(s, dict) and s.get("scoringPeriodId") == week and s.get("statSourceId") == 0), None)
        projected = next((s for s in stats if isinstance(s, dict) and s.get("scoringPeriodId") == week and s.get("statSourceId") == 1), None)
        ownership = player.get("ownership") if isinstance(player.get("ownership"), dict) else {}
        raw_stats = weekly.get("stats", {}) if weekly else {}
        readable_stats = {STAT_NAMES.get(int(k), str(k)): v for k, v in raw_stats.items() if str(k).isdigit() and (int(k) in STAT_NAMES)} if isinstance(raw_stats, dict) else {}
        fantasy_points = item.get("appliedStatTotal")
        if fantasy_points is None and weekly:
            fantasy_points = weekly.get("appliedTotal")
        projected_points = projected.get("appliedTotal") if projected else None
        team_id = player.get("proTeamId")
        return {"athlete_id": player.get("id"), "name": player.get("fullName") or player.get("displayName"), "short_name": player.get("shortName"), "team_id": team_id, "team": NFL_TEAMS.get(team_id), "position": POSITIONS.get(player.get("defaultPositionId")), "fantasy_points": fantasy_points, "projected_points": projected_points, "rostered_pct": ownership.get("percentOwned"), "start_pct": ownership.get("percentStarted"), "roster_change": ownership.get("percentChange"), "injury_status": player.get("injuryStatus"), "active": bool(player.get("active")), "stats": readable_stats, "raw_stats": raw_stats}

    async def _fetch_injuries(self) -> list[dict[str, Any]]:
        async with async_timeout.timeout(20):
            response = await self.session.get(NFL_INJURIES_URL)
            if response.status != 200:
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message="ESPN NFL injuries request failed", headers=response.headers)
            payload = await response.json()
        injuries = []
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
