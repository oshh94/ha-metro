"""Constants for the Copenhagen Metro integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "copenhagen_metro"
API_URL = "https://m.dk/api/operationsdata/"
PLANNED_MAINTENANCE_URL = "https://m.dk/api/operationalChanges/getDay/"
SCAN_INTERVAL_SECONDS = 300
PLANNED_MAINTENANCE_SCAN_INTERVAL_SECONDS = 3600
PLANNED_MAINTENANCE_DAYS_AHEAD = 7
ATTRIBUTION = "Data provided by Metroselskabet (m.dk)"
