"""The Cambridge CXA Network integration.

Original implementation by @lievencoghe
Network support added by @jlxq0
"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# We only have media_player platform
PLATFORMS = [Platform.MEDIA_PLAYER]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Cambridge CXA Network component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cambridge CXA from a config entry."""
    # Store config where media_player.py can access it
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Tell HA to set up our media_player platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for config updates (when user changes options)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload the media_player platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove config from memory
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)