"""
Unit tests for the Currency Bot.

Uses unittest.mock to mock external API calls and FSM state management.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, Chat

from Bot import process_currency_code, cmd_rates
from config import MESSAGE_INVALID_FORMAT, MESSAGE_CURRENCY_NOT_FOUND
from exchange import get_currency_data, clear_cache
from states import CurrencyStates


class TestExchangeModule(unittest.TestCase):
    """Tests for the exchange module."""

    def setUp(self):
        """Clear cache before each test."""
        clear_cache()

    def test_cache_validity(self):
        """Test that cache is returned within TTL."""

        async def run_test():
            # Mock aiohttp to return sample data
            sample_data = {
                "Valute": {
                    "USD": {"Name": "US Dollar", "Value": 90.5, "Previous": 89.5}
                }
            }

            with patch("aiohttp.ClientSession") as mock_session:
                mock_response = AsyncMock()
                mock_response.text = AsyncMock(
                    return_value=__import__("json").dumps(sample_data)
                )
                mock_response.raise_for_status = MagicMock()

                mock_session.return_value.__aenter__ = AsyncMock(
                    return_value=MagicMock(
                        get=MagicMock(
                            return_value=MagicMock(
                                __aenter__=AsyncMock(return_value=mock_response),
                                __aexit__=AsyncMock(return_value=None),
                            )
                        )
                    )
                )
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                # First call should hit the API
                result1 = await get_currency_data()
                self.assertIsNotNone(result1)
                self.assertIn("USD", result1)

        asyncio.run(run_test())

    def test_invalid_json_response(self):
        """Test handling of invalid JSON from API."""

        async def run_test():
            with patch("aiohttp.ClientSession") as mock_session:
                mock_response = AsyncMock()
                mock_response.text = AsyncMock(return_value="{invalid json}")
                mock_response.raise_for_status = MagicMock()

                mock_session.return_value.__aenter__ = AsyncMock(
                    return_value=MagicMock(
                        get=MagicMock(
                            return_value=MagicMock(
                                __aenter__=AsyncMock(return_value=mock_response),
                                __aexit__=AsyncMock(return_value=None),
                            )
                        )
                    )
                )
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await get_currency_data()
                self.assertIsNone(result)

        asyncio.run(run_test())


class TestBotHandlers(unittest.TestCase):
    """Tests for bot message handlers."""

    def setUp(self):
        """Clear cache before each test."""
        clear_cache()

    def _create_message(self, text):
        """Helper to create a mock Message object."""
        message = MagicMock(spec=Message)
        message.text = text
        message.answer = AsyncMock()
        return message

    def test_invalid_currency_code_format(self):
        """Test rejection of invalid currency code format."""

        async def run_test():
            message = self._create_message("US")  # Too short
            state = AsyncMock(spec=FSMContext)
            state.clear = AsyncMock()

            await process_currency_code(message, state)
            message.answer.assert_called()
            call_args = message.answer.call_args[0][0]
            self.assertIn("Invalid format", call_args)

        asyncio.run(run_test())

    def test_currency_not_found(self):
        """Test handling when currency code is not found."""

        async def run_test():
            message = self._create_message("XYZ")  # Valid format, non-existent
            state = AsyncMock(spec=FSMContext)
            state.clear = AsyncMock()

            # Mock get_currency_data to return data without XYZ
            with patch("Bot.get_currency_data") as mock_get:
                mock_get.return_value = {
                    "USD": {"Name": "US Dollar", "Value": 90.5, "Previous": 89.5}
                }

                await process_currency_code(message, state)
                message.answer.assert_called()
                call_args = message.answer.call_args[0][0]
                self.assertIn("not found", call_args)

        asyncio.run(run_test())

    def test_valid_currency_code(self):
        """Test successful currency rate retrieval."""

        async def run_test():
            message = self._create_message("USD")
            state = AsyncMock(spec=FSMContext)
            state.clear = AsyncMock()

            with patch("Bot.get_currency_data") as mock_get:
                mock_get.return_value = {
                    "USD": {"Name": "US Dollar", "Value": 90.5, "Previous": 89.5}
                }

                await process_currency_code(message, state)
                message.answer.assert_called()
                call_args = message.answer.call_args[0][0]
                self.assertIn("90.50", call_args)
                self.assertIn("US Dollar", call_args)
                state.clear.assert_called_once()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
