from pathlib import Path

path = Path("custom_components/sports_ticker/coordinator.py")
text = path.read_text(encoding="utf-8")

import_marker = '''from .nfl_team_leaders import (
    NFL_SUMMARY_URL,
    empty_team_leaders,
    get_event_team_leaders,
    merge_nfl_team_leaders,
    team_leaders_have_data,
)
'''
import_block = '''
from .nfl_game_center import (
    empty_game_center,
    game_center_have_data,
    get_event_game_center,
    merge_game_center_fallback,
    merge_nfl_game_center,
)
'''
if "from .nfl_game_center import (" not in text:
    if import_marker not in text:
        raise SystemExit("NFL team leader import block not found")
    text = text.replace(import_marker, import_marker + import_block, 1)

old_call = "await self._enrich_nfl_team_leaders(payload, previous)"
new_call = "await self._enrich_nfl_event_details(payload, previous)"
if old_call in text:
    text = text.replace(old_call, new_call, 1)
elif new_call not in text:
    raise SystemExit("NFL enrichment call not found")

old_method = "async def _enrich_nfl_team_leaders("
new_method = "async def _enrich_nfl_event_details("
if old_method in text:
    text = text.replace(old_method, new_method, 1)
elif new_method not in text:
    raise SystemExit("NFL enrichment method not found")

text = text.replace(
    '"""Enrich NFL scoreboard events with away/home box-score leaders."""',
    '"""Enrich NFL scoreboard events with leaders and live game-center data."""',
    1,
)

leader_init = '''            # Always expose a predictable structure, including scheduled games.
            competition["team_leaders"] = empty_team_leaders()
'''
game_init = '''            # Always expose predictable structures, including scheduled games.
            competition["team_leaders"] = empty_team_leaders()
            competition["game_center"] = empty_game_center()
            # Normalize any live situation already present on the scoreboard.
            # The summary response below adds win probability and drive detail.
            merge_nfl_game_center(event, {})
'''
if 'competition["game_center"] = empty_game_center()' not in text:
    if leader_init not in text:
        raise SystemExit("NFL enrichment initialization block not found")
    text = text.replace(leader_init, game_init, 1)

cached_marker = '''            cached_event = previous_events.get(event_id)
            cached = get_event_team_leaders(cached_event)
'''
cached_block = '''            cached_event = previous_events.get(event_id)
            cached = get_event_team_leaders(cached_event)
            cached_game_center = get_event_game_center(cached_event)
'''
if "cached_game_center = get_event_game_center(cached_event)" not in text:
    if cached_marker not in text:
        raise SystemExit("NFL cached leader block not found")
    text = text.replace(cached_marker, cached_block, 1)

# Upcoming games retain the predictable empty structure and need no summary call.
# Final games can reuse both normalized structures when the cached snapshot was final.
final_marker = '''            if (
                state == "post"
                and cached_state == "post"
                and team_leaders_have_data(cached)
            ):
                competition["team_leaders"] = cached
                continue
'''
final_block = '''            if (
                state == "post"
                and cached_state == "post"
                and team_leaders_have_data(cached)
                and game_center_have_data(cached_game_center)
            ):
                competition["team_leaders"] = cached
                competition["game_center"] = cached_game_center
                continue
'''
if "and game_center_have_data(cached_game_center)" not in text:
    if final_marker not in text:
        raise SystemExit("NFL final cache reuse block not found")
    text = text.replace(final_marker, final_block, 1)

merge_marker = '''                merge_nfl_team_leaders(event, summary)
            except Exception as err:
'''
merge_block = '''                merge_nfl_team_leaders(event, summary)
                merge_nfl_game_center(event, summary)
            except Exception as err:
'''
if "merge_nfl_game_center(event, summary)" not in text:
    if merge_marker not in text:
        raise SystemExit("NFL summary merge block not found")
    text = text.replace(merge_marker, merge_block, 1)

except_marker = '''                if team_leaders_have_data(cached):
                    competition["team_leaders"] = cached
                _LOGGER.warning(
'''
except_block = '''                if team_leaders_have_data(cached):
                    competition["team_leaders"] = cached
                current_game_center = get_event_game_center(event)
                if game_center_have_data(cached_game_center):
                    competition["game_center"] = merge_game_center_fallback(
                        current_game_center,
                        cached_game_center,
                    )
                _LOGGER.warning(
'''
if "current_game_center = get_event_game_center(event)" not in text:
    if except_marker not in text:
        raise SystemExit("NFL summary failure block not found")
    text = text.replace(except_marker, except_block, 1)

path.write_text(text, encoding="utf-8")
