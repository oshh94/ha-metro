"""API client for Copenhagen Metro operational data."""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp

from .const import API_URL, LOGGER, PLANNED_MAINTENANCE_URL


class CopenhagenMetroApiClientError(Exception):
    """Exception to indicate a general API error."""


class CopenhagenMetroApiClientCommunicationError(CopenhagenMetroApiClientError):
    """Exception to indicate a communication error."""


class CopenhagenMetroApiClientAuthenticationError(CopenhagenMetroApiClientError):
    """Exception to indicate an authentication error."""


class CopenhagenMetroApiClient:
    """API client for the Copenhagen Metro operations data endpoint."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch operational data from the API."""
        LOGGER.debug("Fetching operational data from %s", API_URL)
        return await self._api_wrapper(method="get", url=API_URL)

    async def async_get_planned_maintenance(
        self, date: str, culture: str
    ) -> list[dict[str, Any]]:
        """Fetch planned maintenance for a given date (YYYYMMDD) and culture (en/da)."""
        url = (
            f"{PLANNED_MAINTENANCE_URL}?date={date}&culture={culture}&lines=m1,m2,m3,m4"
        )
        LOGGER.debug(
            "Fetching planned maintenance for date=%s culture=%s", date, culture
        )
        result = await self._api_wrapper(method="get", url=url)
        return result if isinstance(result, list) else []

    async def _api_wrapper(self, method: str, url: str) -> Any:
        """Wrap an API request with error handling."""
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(method, url)
                LOGGER.debug("Response from %s: status=%s", url, response.status)
                response.raise_for_status()
                return await response.json()  # type: ignore[no-any-return]
        except TimeoutError as exception:
            LOGGER.debug("Timeout fetching %s", url)
            msg = "Timeout error fetching information"
            raise CopenhagenMetroApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            LOGGER.debug("Communication error fetching %s: %s", url, exception)
            msg = "Error fetching information"
            raise CopenhagenMetroApiClientCommunicationError(msg) from exception
        except Exception as exception:
            LOGGER.debug("Unexpected error fetching %s: %s", url, exception)
            msg = "Something really wrong happened!"
            raise CopenhagenMetroApiClientError(msg) from exception
