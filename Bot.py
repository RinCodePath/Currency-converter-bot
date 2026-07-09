"""
Main module of the Telegram bot: initialization and handlers.

The bot requests a three-letter currency code from the user and returns
the current exchange rate of this currency to the Russian Ruble (RUB)
based on the Central Bank of Russia data.

Before running, set the BOT_TOKEN environment variable, for example:
    export BOT_TOKEN="your_bot_token"
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from exchange import get_currency_data
from states import CurrencyStates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Message Constants (avoiding "magic strings" in the handler bodies) ---
REQUEST_CODE_MESSAGE = "Please enter a three-letter currency code (e.g., USD, EUR, KGS):"
SERVER_ERROR_MESSAGE = (
    "Server error. Failed to retrieve currency rates. Please try again later."
)
CURRENCY_NOT_FOUND_MESSAGE = "❌ Currency not found, please try again."
NON_TEXT_INPUT_MESSAGE = "Please send the currency code as text."

# Retrieve the token strictly from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "The BOT_TOKEN environment variable is not set. "
        "Set it before running, for example: export BOT_TOKEN='your_token'"
    )

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("rates"))
async def cmd_rates(message: Message, state: FSMContext) -> None:
    """
    Handler for the /rates command.

    Requests a currency code from the user and switches the conversation
    into the waiting state.
    """
    await message.answer(REQUEST_CODE_MESSAGE)
    await state.set_state(CurrencyStates.waiting_for_code)


@dp.message(CurrencyStates.waiting_for_code)
async def process_currency_code(message: Message, state: FSMContext) -> None:
    """
    Handler for the currency code waiting state.

    Receives the currency code from the user, requests current rates
    via exchange.get_currency_data(), and sends a formatted response
    or an appropriate error message.
    """
    if message.text is None:
        await message.answer(NON_TEXT_INPUT_MESSAGE)
        return

    currency_code = message.text.strip().upper()
    valute_data = await get_currency_data()

    # Case 1: API is unavailable
    if valute_data is None:
        await message.answer(SERVER_ERROR_MESSAGE)
        await state.clear()
        return

    currency_info = valute_data.get(currency_code)

    # Case 2: Currency code not found — remain in the current state
    if currency_info is None:
        await message.answer(CURRENCY_NOT_FOUND_MESSAGE)
        return

    # Case 3: Currency found — extract the required fields
    try:
        name = currency_info["Name"]
        current_value = currency_info["Value"]
        previous_value = currency_info["Previous"]
    except KeyError as error:
        logger.error("Expected key is missing in currency data: %s", error)
        await message.answer(SERVER_ERROR_MESSAGE)
        await state.clear()
        return

    response_text = (
        f"Currency: {name} ({currency_code})\n"
        f"Current rate: {current_value:.2f} RUB\n"
        f"Previous rate: {previous_value:.2f} RUB"
    )

    await message.answer(response_text)
    await state.clear()


async def main() -> None:
    """Entry point: start long polling."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())