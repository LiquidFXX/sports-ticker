from __future__ import annotations

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    CONF_CREATE_RAW,
    CONF_CREATE_NEXT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_CREATE_RAW,
    DEFAULT_CREATE_NEXT,
    LEAGUES,
)


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Sports Ticker", data=user_input)

        data_schema = {
            CONF_LEAGUES: selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=sorted(list(LEAGUES.keys())),
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            CONF_POLL_INTERVAL: selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=15, max=600, step=5, mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="sec"
                )
            ),
            CONF_CREATE_RAW: selector.BooleanSelector(),
            CONF_CREATE_NEXT: selector.BooleanSelector(),
        }

        defaults = {
            CONF_LEAGUES: ["mlb", "nfl"],
            CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL,
            CONF_CREATE_RAW: DEFAULT_CREATE_RAW,
            CONF_CREATE_NEXT: DEFAULT_CREATE_NEXT,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=selector.schema(data_schema),
            description_placeholders={},
            last_step=True,
        )


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        data_schema = {
            CONF_LEAGUES: selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=sorted(list(LEAGUES.keys())),
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            CONF_POLL_INTERVAL: selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=15, max=600, step=5, mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="sec"
                )
            ),
            CONF_CREATE_RAW: selector.BooleanSelector(),
            CONF_CREATE_NEXT: selector.BooleanSelector(),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=selector.schema(data_schema),
        )


@config_entries.HANDLERS.register(DOMAIN)
def _create_options_flow(config_entry):
    return SportsTickerOptionsFlow(config_entry)