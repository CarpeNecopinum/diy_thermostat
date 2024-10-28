from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_TEMPERATURE_ENTITY,
    CONF_MIRROR_ACTION_FROM,
    CONF_ATTACH_TO_DEVICE,
    CONF_NAME,
)
import voluptuous as vol
from homeassistant.config import cv
from homeassistant.helpers import selector
from uuid import uuid4

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_TEMPERATURE_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["sensor", "number", "input_number"],
                device_class="temperature",
                multiple=False,
            )
        ),
        vol.Optional(CONF_MIRROR_ACTION_FROM): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate", multiple=False)
        ),
        vol.Optional(CONF_ATTACH_TO_DEVICE): selector.DeviceSelector(),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 1
    MINOR_VERSION = 0

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, info):
        if info is not None:
            await self.async_set_unique_id(f"diy_thermostat_{uuid4()}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="DIY Thermostat",
                data=info,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
        )

    async def async_step_reconfigure(self, info):
        if info is not None:
            unique_id = self._get_reconfigure_entry().unique_id
            self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=info,
            )

        pre_filled = self.add_suggested_values_to_schema(
            DATA_SCHEMA, self._get_reconfigure_entry().data
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=pre_filled,
        )
