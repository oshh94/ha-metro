"""API client for Danish Metro operational data."""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp

from .const import API_URL


class DanishMetroApiClientError(Exception):
    """Exception to indicate a general API error."""


class DanishMetroApiClientCommunicationError(DanishMetroApiClientError):
    """Exception to indicate a communication error."""


class DanishMetroApiClientAuthenticationError(DanishMetroApiClientError):
    """Exception to indicate an authentication error."""


class DanishMetroApiClient:
    """API client for the Danish Metro operations data endpoint."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch operational data from the API."""
        return await self._api_wrapper(method="get", url=API_URL)

    async def _api_wrapper(self, method: str, url: str) -> dict[str, Any]:
        """Wrap an API request with error handling."""
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(method, url)
                response.raise_for_status()
                return await response.json()  # type: ignore[no-any-return]
        except asyncio.TimeoutError as exception:
            raise DanishMetroApiClientCommunicationError(
                "Timeout error fetching information"
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise DanishMetroApiClientCommunicationError(
                "Error fetching information"
            ) from exception
        except Exception as exception:
            raise DanishMetroApiClientError(
                "Something really wrong happened!"
            ) from exception
