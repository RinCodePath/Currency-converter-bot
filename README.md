# Currency Rates Telegram Bot

A lightweight and efficient asynchronous Telegram bot built with **Aiogram 3** that fetches current currency exchange rates against the Russian Ruble (RUB) using the official Central Bank of Russia (CBR) API data.

---

## Features

* **Asynchronous Architecture:** Built using `asyncio` and `aiohttp` for non-blocking network I/O.
* **Finite State Machine (FSM):** Secure state management to handle user input sequentially.
* **Robust Error Handling:** Validates API responses, JSON structures, network timeouts, and incorrect user inputs without crashing.
* **Clean Code:** Strictly separated configuration, business logic, states, and message constants.

---

## Project Structure

```text
├── bot.py         # Bot entry point, initialization, and conversation handlers.
├── exchange.py    # CBR API integration module (fetching and parsing data).
├── states.py      # FSM (Finite State Machine) state definitions.
└── README.md      # Project documentation.