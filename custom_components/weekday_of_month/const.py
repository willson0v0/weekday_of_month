"""Add constants for the integration."""
from __future__ import annotations

import logging

from homeassistant.const import WEEKDAYS, Platform

LOGGER = logging.getLogger(__package__)

DOMAIN = "weekday_of_month"
PLATFORMS = [Platform.BINARY_SENSOR]

CONF_WEEKDAYS = "weekdays"
CONF_NTH_WEEKDAY = "nth_weekday"

DEFAULT_NAME = "Weekday Sensor"

ALLOWED_DAYS = WEEKDAYS
ALLOWED_NTH_WEEKDAY = ["-5", "-4", "-3", "-2", "-1", "1", "2", "3", "4", "5"]