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
    CONF_TICKER_SPEED,
    DEFAULT_TICKER_SPEED,
    CONF_TICKER_THEME,
    DEFAULT_TICKER_THEME,
    TICKER_THEME_LIGHT,
    TICKER_THEME_DARK,
)

DEFAULT_LEAGUES = ["mlb", "nfl"]


def _normalize_leagues(value) -> list[str]:
    """Normalize into list[str] of known league keys."""
    if value is None:
        return []
    if isinstance(value, dict):
        # support {"mlb": True, "nfl": True} style too
        value = [k for k, v in value.items() if v]
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        value = list(value)

    out: list[str] = []
    for v in value:
        k = str(v).strip().lower()
        if k in LEAGUES and k not in out:
            out.append(k)
    return out


def _normalize_theme(value: str | None) -> str:
    t = str(value or DEFAULT_TICKER_THEME).strip().lower()
    return t if t in (TICKER_THEME_LIGHT, TICKER_THEME_DARK) else DEFAULT_TICKER_THEME


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            leagues = _normalize_leagues(user_input.get(CONF_LEAGUES, DEFAULT_LEAGUES))
            poll = int(user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
            speed = int(user_input.get(CONF_TICKER_SPEED, DEFAULT_TICKER_SPEED))
            theme = _normalize_theme(user_input.get(CONF_TICKER_THEME, DEFAULT_TICKER_THEME))

            return self.async_create_entry(
                title="Sports Ticker",
                data={
                    CONF_LEAGUES: leagues,
                    CONF_POLL_INTERVAL: poll,
                    CONF_TICKER_SPEED: speed,
                    CONF_TICKER_THEME: theme,
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
                vol.Optional(CONF_TICKER_SPEED, default=DEFAULT_TICKER_SPEED): vol.All(
                    vol.Coerce(int), vol.Range(min=6, max=30)  # 6 slow, 30 fast
                ),
                vol.Optional(CONF_TICKER_THEME, default=DEFAULT_TICKER_THEME): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[TICKER_THEME_LIGHT, TICKER_THEME_DARK],
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SportsTickerOptionsFlow(config_entry)


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            leagues = _normalize_leagues(user_input.get(CONF_LEAGUES, DEFAULT_LEAGUES))
            poll = int(user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
            speed = int(user_input.get(CONF_TICKER_SPEED, DEFAULT_TICKER_SPEED))
            theme = _normalize_theme(user_input.get(CONF_TICKER_THEME, DEFAULT_TICKER_THEME))

            return self.async_create_entry(
                title="",
                data={
                    CONF_LEAGUES: leagues,
                    CONF_POLL_INTERVAL: poll,
                    CONF_TICKER_SPEED: speed,
                    CONF_TICKER_THEME: theme,
                },
            )

        current = {**self._entry.data, **self._entry.options}
        current_leagues = _normalize_leagues(current.get(CONF_LEAGUES, DEFAULT_LEAGUES))
        current_poll = int(current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        current_speed = int(current.get(CONF_TICKER_SPEED, DEFAULT_TICKER_SPEED))
        current_theme = _normalize_theme(current.get(CONF_TICKER_THEME, DEFAULT_TICKER_THEME))

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
                vol.Optional(CONF_TICKER_SPEED, default=current_speed): vol.All(
                    vol.Coerce(int), vol.Range(min=6, max=30)
                ),
                vol.Optional(CONF_TICKER_THEME, default=current_theme): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[TICKER_THEME_LIGHT, TICKER_THEME_DARK],
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)