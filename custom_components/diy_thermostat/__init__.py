"""Let's try this."""

import logging
from asyncio import Lock
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Config
from homeassistant.config_entries import ConfigEntry
import voluptuous as vol

from .const import DOMAIN

PLATFORMS = [Platform.CLIMATE]

config_entry_update_listener_lock = Lock()


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""

    hass.states.async_set("diy_thermostat.hello", "Running, I guess")
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN] = {}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    async with config_entry_update_listener_lock:
        await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)
