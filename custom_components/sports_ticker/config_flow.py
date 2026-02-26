from __future__ import annotations

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
)

DEFAULT_LEAGUES = ["mlb", "nfl"]


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="Sports Ticker",
            data={
                CONF_LEAGUES: DEFAULT_LEAGUES,
                CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL,
            },
        )