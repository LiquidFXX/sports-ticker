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

DEFAULT_LEAGUES = ["mlb", "nfl"]


def _normalize_leagues(value) -> list[str]:
    """Normalize user input into a lowercase list of known league keys."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        value = list(value)

    out: list[str] = []
    for v in value:
        key = str(v).strip().lower()
        if key in LEAGUES and key not in out:
            out.append(key)
    return out


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            leagues = _normalize_leagues(user_input.get(CONF_LEAGUES, DEFAULT_LEAGUES))
            poll = int(user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
            return self.async_create_entry(
                title="Sports Ticker",
                data={
                    CONF_LEAGUES: leagues,
                    CONF_POLL_INTERVAL: poll,
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_LEAGUES, default=DEFAULT_LEAGUES): selector.SelectSelector(
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
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SportsTickerOptionsFlow(config_entry)


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        # NOTE: do NOT assign self.config_entry (HA manages that)
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            leagues = _normalize_leagues(user_input.get(CONF_LEAGUES))
            poll = int(user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
            return self.async_create_entry(
                title="",
                data={
                    CONF_LEAGUES: leagues,
                    CONF_POLL_INTERVAL: poll,
                },
            )

        current = {**self._entry.data, **self._entry.options}
        current_leagues = _normalize_leagues(current.get(CONF_LEAGUES, DEFAULT_LEAGUES))
        current_poll = int(current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))

        data_schema = vol.Schema(
            {
                vol.Required(CONF_LEAGUES, default=current_leagues): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=sorted(list(LEAGUES.keys())),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_POLL_INTERVAL, default=current_poll): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)