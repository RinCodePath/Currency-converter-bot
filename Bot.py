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
import re

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import (
    BOT_TOKEN,
    LOGGING_LEVEL,
    CURRENCY_CODE_PATTERN,
    MESSAGE_START,
    MESSAGE_HELP,
    MESSAGE_REQUEST_CODE,
    MESSAGE_SERVER_ERROR,
    MESSAGE_CURRENCY_NOT_FOUND,
    MESSAGE_NON_TEXT_INPUT,
    MESSAGE_INVALID_FORMAT,
)
from exchange import get_currency_data
from states import CurrencyStates

logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Handler for the /start command.

    Sends a welcome message.
    """
    await message.answer(MESSAGE_START)


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Handler for the /help command.

    Sends available commands.
    """
    await message.answer(MESSAGE_HELP)


@dp.message(Command("rates"))
async def cmd_rates(message: Message, state: FSMContext) -> None:
    """
    Handler for the /rates command.

    Requests a currency code from the user and switches the conversation
    into the waiting state.
    """
    await message.answer(MESSAGE_REQUEST_CODE)
    await state.set_state(CurrencyStates.waiting_for_code)


@dp.message(CurrencyStates.waiting_for_code)
async def process_currency_code(message: Message, state: FSMContext) -> None:
    """
    Handler for the currency code waiting state.

    Receives the currency code from the user, validates the format,
    requests current rates via exchange.get_currency_data(), and sends
    a formatted response or an appropriate error message.
    """
    if message.text is None:
        await message.answer(MESSAGE_NON_TEXT_INPUT)
        return

    currency_code = message.text.strip().upper()

    # Validate currency code format
    if not re.match(CURRENCY_CODE_PATTERN, currency_code):
        await message.answer(MESSAGE_INVALID_FORMAT)
        return

    valute_data = await get_currency_data()

    # Case 1: API is unavailable
    if valute_data is None:
        await message.answer(MESSAGE_SERVER_ERROR)
        await state.clear()
        return

    currency_info = valute_data.get(currency_code)

    # Case 2: Currency code not found — remain in the current state
    if currency_info is None:
        await message.answer(MESSAGE_CURRENCY_NOT_FOUND)
        return

    # Case 3: Currency found — extract the required fields
    try:
        name = currency_info["Name"]
        current_value = currency_info["Value"]
        previous_value = currency_info["Previous"]
    except KeyError as error:
        logger.error("Expected key is missing in currency data: %s", error)
        await message.answer(MESSAGE_SERVER_ERROR)
        await state.clear()
        return

    change = current_value - previous_value
    change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"

    response_text = (
        f"💱 {name} ({currency_code})\n\n"
        f"Current rate: {current_value:.2f} RUB\n"
        f"Previous rate: {previous_value:.2f} RUB\n"
        f"Change: {change_symbol} {change:+.2f} RUB"
    )

    await message.answer(response_text)
    await state.clear()


async def main() -> None:
    """Entry point: start long polling."""
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
