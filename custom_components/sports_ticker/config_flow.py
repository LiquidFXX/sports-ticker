from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    LEAGUES,
)

DEFAULT_LEAGUES = ["mlb", "nhl", "nba", "nfl"]


def _league_labels() -> dict[str, str]:
    # Display labels in the UI while values stay lowercase keys
    return {k: k.upper() for k in LEAGUES.keys()}


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            leagues = user_input.get(CONF_LEAGUES) or []
            if isinstance(leagues, str):
                leagues = [leagues]
            user_input[CONF_LEAGUES] = leagues
            return self.async_create_entry(title="Sports Ticker", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_LEAGUES, default=DEFAULT_LEAGUES): cv.multi_select(_league_labels()),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return SportsTickerOptionsFlow(config_entry)


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            leagues = user_input.get(CONF_LEAGUES) or []
            if isinstance(leagues, str):
                leagues = [leagues]
            user_input[CONF_LEAGUES] = leagues
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LEAGUES,
                    default=current.get(CONF_LEAGUES, DEFAULT_LEAGUES),
                ): cv.multi_select(_league_labels()),
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=15, max=600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)