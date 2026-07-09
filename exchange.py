"""
Integration module with the external API of the Central Bank of the Russian Federation.

Contains an asynchronous function to retrieve current currency exchange rates
from the public service https://www.cbr-xml-daily.ru/ with simple in-memory caching.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional

import aiohttp

from config import CBR_API_URL, REQUEST_TIMEOUT_SECONDS, CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache: Dict[str, Any] = {"data": None, "timestamp": 0}


def _is_cache_valid() -> bool:
    """Check if cached data is still fresh."""
    if _cache["data"] is None:
        return False
    elapsed = time.time() - _cache["timestamp"]
    return elapsed < CACHE_TTL_SECONDS


async def get_currency_data() -> Optional[Dict[str, Any]]:
    """
    Retrieves currency exchange rate data from the CBR API.

    Uses in-memory caching with a TTL of 24 hours (CBR updates once daily).
    Performs an asynchronous GET request to the cbr-xml-daily.ru service and
    returns the 'Valute' dictionary from the response (key is the currency code,
    value is a dictionary containing fields like Name, Value, Previous, etc.).

    Returns:
        Optional[Dict[str, Any]]: A dictionary structured as {"USD": {...}, "EUR": {...}}
        on a successful request, or None in case of any error
        (network failure, timeout, invalid JSON, or missing required key).
    """
    # Return cached data if it's still fresh
    if _is_cache_valid():
        logger.info("Returning cached currency data")
        return _cache["data"]

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(CBR_API_URL) as response:
                response.raise_for_status()
                raw_text = await response.text()

    except asyncio.TimeoutError:
        logger.error("Timeout exceeded while waiting for response from CBR API")
        return None
    except aiohttp.ClientError as error:
        logger.error("Network error during request to CBR API: %s", error)
        return None

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        logger.error("Failed to parse JSON response from CBR API: %s", error)
        return None

    valute = data.get("Valute")
    if not isinstance(valute, dict):
        logger.error("API response does not contain a valid 'Valute' key")
        return None

    # Cache the data
    _cache["data"] = valute
    _cache["timestamp"] = time.time()
    logger.info("Currency data cached successfully")

    return valute


def clear_cache() -> None:
    """Clear the in-memory cache (useful for testing)."""
    _cache["data"] = None
    _cache["timestamp"] = 0
    logger.debug("Cache cleared")
