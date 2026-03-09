"""Constants for the Copenhagen Metro integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "copenhagen_metro"
API_URL = "https://m.dk/api/operationsdata/"
SCAN_INTERVAL_SECONDS = 60
ATTRIBUTION = "Data provided by Metroselskabet (m.dk)"
