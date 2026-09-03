from __future__ import annotations

import logging
from pathlib import Path

import homeassistant.helpers.config_validation as cv
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .coordinator import SportsTickerCoordinator

LOGGER = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_URL = "/sports-ticker/frontend"
CARD_FILENAME = "sports-ticker-card.js"
CARD_VERSION = "0.3.1"
CARD_URL = f"{FRONTEND_URL}/{CARD_FILENAME}?v={CARD_VERSION}"

# ✅ hassfest: integration has async_setup, so define CONFIG_SCHEMA
# This integration is config-entry only (no YAML configuration)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration and bundled dashboard cards."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend(hass)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and load the bundled Sports Ticker dashboard cards."""
    card_path = FRONTEND_DIR / CARD_FILENAME
    if not card_path.exists():
        LOGGER.warning(
            "Bundled Sports Ticker card was not found at %s; dashboard card will not be available",
            card_path,
        )
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_DIR), False)]
    )
    add_extra_js_url(hass, CARD_URL)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sports Ticker from a config entry."""
    coordinator = SportsTickerCoordinator(hass, entry)

    # Load last-good cached data before the first ESPN refresh.
    # This prevents sensors from starting empty if ESPN is unavailable.
    await coordinator.async_load_cached_data()

    # Fetch fresh data. If ESPN fails, the coordinator keeps cached data.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Reload the integration when Options are changed.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Sports Ticker."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: SportsTickerCoordinator | None = hass.data.get(DOMAIN, {}).pop(
            entry.entry_id,
            None,
        )

        if coordinator:
            await coordinator.async_shutdown()

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
