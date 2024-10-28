import logging

import voluptuous as vol

from homeassistant.components.climate import (
    PLATFORM_SCHEMA as CLIMATE_PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config import cv
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import Event, EventStateChangedData, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_MIRROR_ACTION_FROM,
    CONF_TEMPERATURE_ENTITY,
    CONF_ATTACH_TO_DEVICE,
    CONF_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = CLIMATE_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): str,
        vol.Required(CONF_TEMPERATURE_ENTITY): cv.entity_id,
        vol.Optional(CONF_MIRROR_ACTION_FROM): cv.entity_id,
        vol.Optional(CONF_ATTACH_TO_DEVICE): cv.isdevice,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    # Add devices
    _LOGGER.info(config)
    add_entities([DIYThermostat(hass, config, None)])


async def async_setup_entry(hass: HomeAssistant, config_entry, add_entities):
    add_entities([DIYThermostat(hass, config_entry.data, config_entry.entry_id)])


def clean_id(source: str) -> str:
    return source.lower().replace(" ", "_").replace(".", "_")


class DIYThermostat(ClimateEntity):
    """Representation of a DIY Thermostat."""

    def __init__(self, hass: HomeAssistant, config: ConfigType, unique_id: str) -> None:
        """Initialize a DIY Thermostat."""
        self.name = config.get(CONF_NAME, "DIY Thermostat")
        self.hass = hass
        self.hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self.temperature_unit = "°C"
        self.hvac_mode = HVACMode.OFF
        self.current_temperature = 20.0
        self.target_temperature = 20.0
        self.max_temp = 35.0
        self.min_temp = 5.0
        self.hvac_action = HVACAction.IDLE
        self.supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self.unique_id = unique_id
        async_track_state_change_event(
            hass, config[CONF_TEMPERATURE_ENTITY], self._async_temperature_changed
        )

        if mirrored := config.get(CONF_MIRROR_ACTION_FROM):
            async_track_state_change_event(hass, mirrored, self._async_action_changed)

        if attach_to_id := config.get(CONF_ATTACH_TO_DEVICE):
            device_registry = dr.async_get(hass)
            device = device_registry.async_get(attach_to_id)
            self.device_info = {
                "identifiers": device.identifiers,
                "name": device.name,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "sw_version": device.sw_version,
            }

    def _async_action_changed(self, event: Event[EventStateChangedData]):
        new_state = event.data["new_state"]
        if new_action := new_state.attributes.get("hvac_action"):
            self.hvac_action = new_action
            self.schedule_update_ha_state()

    def _async_temperature_changed(self, event: Event[EventStateChangedData]):
        new_state = event.data["new_state"]

        try:
            self.current_temperature = float(new_state.state)
            self.schedule_update_ha_state()
        except ValueError:
            pass

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self.hvac_mode = hvac_mode
        self.schedule_update_ha_state()

    def set_temperature(self, temperature=None, hvac_mode=None, **_) -> None:
        if temperature is not None:
            self.target_temperature = temperature
        if hvac_mode is not None:
            self.hvac_mode = hvac_mode
        self.schedule_update_ha_state()

    def turn_on(self) -> None:
        self.set_hvac_mode(HVACMode.HEAT)

    def turn_off(self) -> None:
        self.set_hvac_mode(HVACMode.OFF)
