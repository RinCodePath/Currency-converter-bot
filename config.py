"""
Configuration and constants for the Currency Bot.

Centralizes all settings, timeouts, messages, and API endpoints.
"""

import os
from logging import INFO

# --- Telegram Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "The BOT_TOKEN environment variable is not set. "
        "Set it before running, for example: export BOT_TOKEN='your_token'"
    )

# --- Logging Configuration ---
LOGGING_LEVEL = INFO

# --- API Configuration ---
CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
REQUEST_TIMEOUT_SECONDS = 10
CACHE_TTL_SECONDS = 86400  # 24 hours (CBR updates once per day)

# --- Validation ---
CURRENCY_CODE_LENGTH = 3
CURRENCY_CODE_PATTERN = r"^[A-Z]{3}$"  # Only uppercase letters, exactly 3

# --- User Messages ---
MESSAGE_START = (
    "Welcome to Currency Rates Bot! 🌍\n\n"
    "I provide current exchange rates from the Central Bank of Russia.\n\n"
    "Use /rates to get started."
)
MESSAGE_HELP = (
    "Commands:\n"
    "/rates - Get exchange rate for a currency\n"
    "/help - Show this help message"
)
MESSAGE_REQUEST_CODE = "Please enter a three-letter currency code (e.g., USD, EUR, GBP, KGS):"
MESSAGE_SERVER_ERROR = (
    "🔴 Server error. Failed to retrieve currency rates. Please try again later."
)
MESSAGE_CURRENCY_NOT_FOUND = (
    "❌ Currency not found. Please check the code and try again.\n"
    "Example: USD, EUR, GBP, JPY, CNY, KGS"
)
MESSAGE_NON_TEXT_INPUT = "Please send the currency code as text."
MESSAGE_INVALID_FORMAT = (
    "❌ Invalid format. Please enter exactly 3 uppercase letters.\n"
    "Example: USD, EUR, GBP"
)
