from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_LEAGUES,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    CONF_TICKER_SPEED,
    DEFAULT_TICKER_SPEED,
    CONF_TICKER_THEME,
    DEFAULT_TICKER_THEME,
    TICKER_THEME_LIGHT,
    TICKER_THEME_DARK,
    LEAGUES,
)


def _league_options() -> list[selector.SelectOptionDict]:
    # Nice labels in UI, values stay lowercase keys
    opts: list[selector.SelectOptionDict] = []
    for k, meta in LEAGUES.items():
        label = str(meta.get("name", k.upper()))
        opts.append({"value": k, "label": label})
    return sorted(opts, key=lambda x: x["label"])


class SportsTickerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            leagues = user_input.get(CONF_LEAGUES) or []
            if isinstance(leagues, str):
                leagues = [leagues]
            user_input[CONF_LEAGUES] = [str(x).strip().lower() for x in leagues]
            return self.async_create_entry(title="Sports Ticker", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_LEAGUES, default=["mlb", "nfl"]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_league_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=15, max=600)),
                vol.Optional(CONF_TICKER_SPEED, default=DEFAULT_TICKER_SPEED): vol.All(vol.Coerce(int), vol.Range(min=6, max=30)),
                vol.Optional(CONF_TICKER_THEME, default=DEFAULT_TICKER_THEME): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": TICKER_THEME_LIGHT, "label": "Light"},
                            {"value": TICKER_THEME_DARK, "label": "Dark"},
                        ],
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return SportsTickerOptionsFlow(config_entry)


class SportsTickerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        # ✅ DO NOT assign self.config_entry (read-only in newer HA)
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            leagues = user_input.get(CONF_LEAGUES) or []
            if isinstance(leagues, str):
                leagues = [leagues]
            user_input[CONF_LEAGUES] = [str(x).strip().lower() for x in leagues]
            return self.async_create_entry(title="", data=user_input)

        current = {**self._entry.data, **self._entry.options}

        schema = vol.Schema(
            {
                vol.Required(CONF_LEAGUES, default=current.get(CONF_LEAGUES, ["mlb", "nfl"])): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_league_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_POLL_INTERVAL, default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=600)
                ),
                vol.Optional(CONF_TICKER_SPEED, default=current.get(CONF_TICKER_SPEED, DEFAULT_TICKER_SPEED)): vol.All(
                    vol.Coerce(int), vol.Range(min=6, max=30)
                ),
                vol.Optional(CONF_TICKER_THEME, default=current.get(CONF_TICKER_THEME, DEFAULT_TICKER_THEME)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": TICKER_THEME_LIGHT, "label": "Light"},
                            {"value": TICKER_THEME_DARK, "label": "Dark"},
                        ],
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)