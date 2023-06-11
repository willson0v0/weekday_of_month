from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_WEEKDAYS,
    CONF_NTH_WEEKDAY,
    DOMAIN,
    LOGGER,
    PLATFORMS,
    DEFAULT_NAME,
    ALLOWED_DAYS,
    ALLOWED_NTH_WEEKDAY
)

NONE_SENTINEL = "none"

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(),
        vol.Required(CONF_WEEKDAYS, default=["sat"]): SelectSelector(
            SelectSelectorConfig(
                options=ALLOWED_DAYS,
                multiple=True,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="days",
            )
        ),
        vol.Required(CONF_NTH_WEEKDAY, default=["-1"]): SelectSelector(
            SelectSelectorConfig(
                options=ALLOWED_NTH_WEEKDAY,
                multiple=True,
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    },
)

async def validate_input(data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short hostname
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.
    if len(data[CONF_NTH_WEEKDAY]) != len(set(data[CONF_NTH_WEEKDAY])):
        raise DuplicateNthWeekday

    # Return info that you want to store in the config entry.
    # "Title" is what is displayed to the user for this hub device
    # It is stored internally in HA as part of the device config.
    # See `async_step_user` below for how this is used
    return {
        CONF_NAME: data[CONF_NAME]
    }


class WeekdayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Workday integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(user_input)

                return self.async_create_entry(title=info[CONF_NAME], data=user_input)
            except DuplicateNthWeekday:
                errors["base"] = "duplicate_nth_weekday"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class DuplicateNthWeekday(HomeAssistantError):
    """Exception for specifing multiple nth-weekday"""