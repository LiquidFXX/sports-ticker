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

FANTASY_PLAYERS_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leaguedefaults/3"
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

        leaders = self._build_leaders(players, "fantasy_points")
        season_leaders = self._build_leaders(players, "season_fantasy_points")

        return {
            "season": season,
            "week": week,
            "scoring": "espn_default",
            "leaders": leaders,
            "season_leaders": season_leaders,
            "players": players[:300],
            "injuries": injuries,
            "updated_at": dt_util.utcnow().isoformat(),
        }

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
        fantasy_filter = {
            "players": {
                "filterSlotIds": {"value": [0, 2, 4, 6, 17, 16]},
                "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
                "limit": 500,
                "offset": 0,
            }
        }
        headers = {
            "x-fantasy-filter": json.dumps(fantasy_filter),
            "x-fantasy-platform": "kona-PROD-1dc40132dc207d89781581d6a4c8100b3cc2458f",
            "x-fantasy-source": "kona",
        }
        async with async_timeout.timeout(20):
            response = await self.session.get(url, params=params, headers=headers)
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    response.request_info,
                    response.history,
                    status=response.status,
                    message="ESPN fantasy players request failed",
                    headers=response.headers,
                )
            payload = await response.json()

        items = payload.get("players", []) if isinstance(payload, dict) else []
        player_ids = []
        for item in items:
            if not isinstance(item, dict):
                continue
            player = item.get("player", item)
            player_id = player.get("id") or item.get("id")
            if player_id is not None:
                player_ids.append(player_id)

        # kona_player_info is reliable for ownership/status, but ESPN does not
        # consistently include weekly stat splits there. Fetch player cards by
        # id and merge their stats back into the player pool.
        try:
            cards = await self._fetch_player_cards(season, week, player_ids)
        except Exception:
            # Keep fantasy data non-fatal if the deeper player-card request is
            # temporarily unavailable. Ownership/injury data can still update.
            cards = {}

        players = [
            self._normalize_player(
                item,
                week,
                season,
                cards.get(str((item.get("player", item)).get("id") or item.get("id"))),
            )
            for item in items
            if isinstance(item, dict)
        ]
        players = [
            player
            for player in players
            if player.get("name")
            and player.get("position")
            and player.get("active") is not False
        ]
        players.sort(
            key=lambda player: (
                self._number(player.get("fantasy_points")),
                self._number(player.get("rostered_pct")),
            ),
            reverse=True,
        )
        return players

    async def _fetch_player_cards(
        self, season: int, week: int, player_ids: list[Any]
    ) -> dict[str, dict[str, Any]]:
        url = FANTASY_PLAYERS_URL.format(season=season)
        cards: dict[str, dict[str, Any]] = {}

        # Keep the filter header reasonably small. ESPN accepts batched filterIds
        # on the league-default player-card view.
        for offset in range(0, len(player_ids), 100):
            batch = player_ids[offset : offset + 100]
            if not batch:
                continue
            params = {"scoringPeriodId": str(week), "view": "kona_playercard"}
            fantasy_filter = {
                "players": {
                    "filterIds": {"value": batch},
                    "filterStatsForTopScoringPeriodIds": {
                        "value": week,
                        "additionalValue": [f"00{season}", f"10{season}"],
                    },
                    "filterStatsForSourceIds": {"value": [0, 1]},
                }
            }
            headers = {
                "x-fantasy-filter": json.dumps(fantasy_filter),
                "x-fantasy-platform": "kona-PROD-1dc40132dc207d89781581d6a4c8100b3cc2458f",
                "x-fantasy-source": "kona",
            }
            async with async_timeout.timeout(20):
                response = await self.session.get(url, params=params, headers=headers)
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message="ESPN fantasy player-card request failed",
                        headers=response.headers,
                    )
                payload = await response.json()

            for item in payload.get("players", []) if isinstance(payload, dict) else []:
                if not isinstance(item, dict):
                    continue
                player = item.get("player", item)
                player_id = player.get("id") or item.get("id")
                if player_id is not None:
                    cards[str(player_id)] = player

        return cards

    @staticmethod
    def _normalize_player(
        item: dict[str, Any],
        week: int,
        season: int,
        card_player: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        player = item.get("player", item)
        stats_player = card_player if isinstance(card_player, dict) else player
        stats = stats_player.get("stats") if isinstance(stats_player.get("stats"), list) else []

        weekly = NFLFantasyCoordinator._find_stat(
            stats, season=season, week=week, source=0
        )
        projected = NFLFantasyCoordinator._find_stat(
            stats, season=season, week=week, source=1
        )
        season_actual = NFLFantasyCoordinator._find_season_stat(
            stats, season=season, source=0
        )
        season_projected = NFLFantasyCoordinator._find_season_stat(
            stats, season=season, source=1
        )

        fantasy_points = weekly.get("appliedTotal") if weekly else None
        projected_points = projected.get("appliedTotal") if projected else None
        season_fantasy_points = (
            season_actual.get("appliedTotal") if season_actual else None
        )
        season_projected_points = (
            season_projected.get("appliedTotal") if season_projected else None
        )

        ownership = player.get("ownership") if isinstance(player.get("ownership"), dict) else {}
        injury_id = player.get("injuryStatus")

        weekly_stats = {}
        if weekly:
            if isinstance(weekly.get("stats"), dict):
                weekly_stats = weekly.get("stats")
            elif isinstance(weekly.get("appliedStats"), dict):
                weekly_stats = weekly.get("appliedStats")

        season_stats = {}
        if season_actual:
            if isinstance(season_actual.get("stats"), dict):
                season_stats = season_actual.get("stats")
            elif isinstance(season_actual.get("appliedStats"), dict):
                season_stats = season_actual.get("appliedStats")

        return {
            "athlete_id": player.get("id") or item.get("id"),
            "name": player.get("fullName") or player.get("displayName"),
            "short_name": player.get("shortName"),
            "team_id": player.get("proTeamId"),
            "position": POSITIONS.get(player.get("defaultPositionId")),
            "fantasy_points": fantasy_points,
            "projected_points": projected_points,
            "season_fantasy_points": season_fantasy_points,
            "season_projected_points": season_projected_points,
            "rostered_pct": ownership.get("percentOwned"),
            "start_pct": ownership.get("percentStarted"),
            "roster_change": ownership.get("percentChange"),
            "injury_status": INJURY_STATUS.get(injury_id, injury_id),
            "active": player.get("active"),
            "stats": weekly_stats,
            "season_stats": season_stats,
        }

    @staticmethod
    def _build_leaders(
        players: list[dict[str, Any]], points_key: str
    ) -> dict[str, list[dict[str, Any]]]:
        scored_players = [
            player for player in players if player.get(points_key) is not None
        ]
        scored_players.sort(
            key=lambda player: (
                NFLFantasyCoordinator._number(player.get(points_key)),
                NFLFantasyCoordinator._number(player.get("rostered_pct")),
            ),
            reverse=True,
        )
        leaders: dict[str, list[dict[str, Any]]] = {
            "overall": scored_players[:25]
        }
        for position in ("QB", "RB", "WR", "TE", "K", "D/ST"):
            leaders[position.lower().replace("/", "")] = [
                player
                for player in scored_players
                if player.get("position") == position
            ][:25]
        return leaders

    @staticmethod
    def _find_stat(
        stats: list[dict[str, Any]], *, season: int, week: int, source: int
    ) -> dict[str, Any] | None:
        for stat in stats:
            if not isinstance(stat, dict):
                continue
            if stat.get("seasonId") not in (None, season):
                continue
            if stat.get("scoringPeriodId") != week:
                continue
            if stat.get("statSourceId") != source:
                continue
            split_type = stat.get("statSplitTypeId")
            if split_type not in (None, 1):
                continue
            return stat
        return None

    @staticmethod
    def _find_season_stat(
        stats: list[dict[str, Any]], *, season: int, source: int
    ) -> dict[str, Any] | None:
        for stat in stats:
            if not isinstance(stat, dict):
                continue
            if stat.get("seasonId") not in (None, season):
                continue
            if stat.get("scoringPeriodId") not in (None, 0):
                continue
            if stat.get("statSourceId") != source:
                continue
            split_type = stat.get("statSplitTypeId")
            if split_type not in (None, 0):
                continue
            return stat
        return None

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
