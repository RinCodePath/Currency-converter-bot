"""
Integration module with the external API of the Central Bank of the Russian Federation.

Contains an asynchronous function to retrieve current currency exchange rates
from the public service https://www.cbr-xml-daily.ru/
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
REQUEST_TIMEOUT_SECONDS = 10


async def get_currency_data() -> Optional[Dict[str, Any]]:
    """
    Retrieves currency exchange rate data from the CBR API.

    Performs an asynchronous GET request to the cbr-xml-daily.ru service and
    returns the 'Valute' dictionary from the response (key is the currency code,
    value is a dictionary containing fields like Name, Value, Previous, etc.).

    Returns:
        Optional[Dict[str, Any]]: A dictionary structured as {"USD": {...}, "EUR": {...}}
        on a successful request, or None in case of any error
        (network failure, timeout, invalid JSON, or missing required key).
    """
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

    return valute