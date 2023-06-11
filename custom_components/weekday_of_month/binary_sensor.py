"""Sensor to indicate whether the current day is a workday."""
from __future__ import annotations

from datetime import date, timedelta
import calendar
from typing import Any

import holidays
from holidays import DateLike, HolidayBase
import voluptuous as vol

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util

from .const import (
    CONF_WEEKDAYS,
    CONF_NTH_WEEKDAY,
    DEFAULT_NAME,
    DOMAIN,
    LOGGER,
    PLATFORMS,
    ALLOWED_DAYS,
    ALLOWED_NTH_WEEKDAY
)

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_WEEKDAYS, default=["sat"]): vol.All(
            cv.ensure_list, [vol.In(ALLOWED_DAYS)]
        ),
        vol.Required(CONF_NTH_WEEKDAY, default=["-1"]): vol.All(
            cv.ensure_list, [vol.In(ALLOWED_NTH_WEEKDAY)]
        ),
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Workday sensor."""
    async_create_issue(
        hass,
        DOMAIN,
        "deprecated_yaml",
        breaks_in_ha_version="2023.7.0",
        is_fixable=False,
        severity=IssueSeverity.WARNING,
        translation_key="deprecated_yaml",
    )

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Workday sensor."""
    sensor_name: str = entry.data[CONF_NAME]
    weekdays: list[str] = entry.data[CONF_WEEKDAYS]
    nth_weekday: list[str] = entry.data[CONF_NTH_WEEKDAY]

    async_add_entities(
        [
            NthWeekdayOfMonthSensor(
                weekdays,
                nth_weekday,
                sensor_name,
                entry.entry_id,
            )
        ],
        True,
    )


class NthWeekdayOfMonthSensor(BinarySensorEntity):
    """Implementation of a Workday sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        weekdays: list[str],
        nth_weekday: list[str],
        name: str,
        entry_id: str,
    ) -> None:
        """Initialize the Workday sensor."""
        self._weekdays = weekdays
        self._nth_weekday = nth_weekday
        self._attr_extra_state_attributes = {
            CONF_WEEKDAYS: weekdays,
            CONF_NTH_WEEKDAY: nth_weekday,
        }
        self._attr_unique_id = entry_id
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="willson0v0",
            model="N/A",
            name=name,
        )
        self._attr_is_on = True

    def is_specified_weekday_of_month(self, weekday: str, nth: int):
        current_date = dt_util.now()
        current_weekday = current_date.isoweekday() - 1
        if ALLOWED_DAYS[current_weekday] != weekday:
            return False
        month = calendar.monthcalendar(current_date.year, current_date.month)
        if nth > 0 or not month[nth][current_weekday]:
            return month[nth - 1][current_weekday] == current_date.day
        else:
            return month[nth][current_weekday] == current_date.day

    async def async_update(self) -> None:
        """Get date and check about it."""
        self._attr_is_on = False
        for weekday in self._weekdays:
            for nth in self._nth_weekday:
                if self.is_specified_weekday_of_month(weekday, int(nth)):
                    self._attr_is_on = True
                    return
