from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_SPORTS, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, LEAGUES


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Sports Ticker", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_SPORTS, default=["mlb"]): vol.All(
                    vol.Coerce(list),
                ),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.Coerce(int),
            }
        )

        # Simple checkbox-style selection in UI
        schema = vol.Schema(
            {
                vol.Required(CONF_SPORTS, default=["mlb"]): vol.In(list(LEAGUES.keys())),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.Coerce(int),
            }
        )
        # NOTE: HA's basic flow widgets for multi-select vary; to keep it working everywhere,
        # we’ll accept a comma-separated list in README and parse in coordinator if needed.

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SportsTickerOptionsFlow(config_entry)


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        options = self.config_entry.options

        sports_default = options.get(CONF_SPORTS, data.get(CONF_SPORTS, ["mlb"]))
        poll_default = options.get(CONF_POLL_INTERVAL, data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))

        schema = vol.Schema(
            {
                vol.Required(CONF_SPORTS, default=sports_default): vol.In(list(LEAGUES.keys())),
                vol.Optional(CONF_POLL_INTERVAL, default=poll_default): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)