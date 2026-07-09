"""
FSM states module for the currency rate retrieval conversation.
"""

from aiogram.fsm.state import State, StatesGroup


class CurrencyStates(StatesGroup):
    """States for the user conversation when requesting a currency rate."""

    waiting_for_code = State()
