from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    LEAGUES,
)


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
                vol.Required(CONF_LEAGUES, default=["mlb", "nfl"]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=sorted(list(LEAGUES.keys())),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
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
                vol.Required(CONF_LEAGUES, default=current.get(CONF_LEAGUES, ["mlb", "nfl"])): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=sorted(list(LEAGUES.keys())),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=15, max=600)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)