# premarketstockalerts
Real-time premarket and daily stock alerts highlighting top gainers, volatile stocks under $10, and high-momentum opportunities to help you stay ahead in the market.

## Features

- Fetches **top gainers** filtered by:
  - Minimum % price increase (default 5%)
  - Minimum trading volume (default 500,000)
  - Stock price range ($1 - $50)
- Separately fetches **volatile premarket stocks under $10** filtered by:
  - Premarket % change ≥ 3%
- Automatically fetches the latest news headline per stock symbol
- Formats output with clickable stock symbols linking to Yahoo Finance
- Sends notifications as **Markdown messages** via Telegram Bot API
- Fully contained in a **single Python script** for easy deployment

---

## Tech Stack

- Python 3
- `requests` for API calls
- `pandas` for data manipulation
- Telegram Bot API for alerts
- Yahoo Finance unofficial APIs for stock data and news

---

## Setup & Usage

1. Clone or download this repo

2. Create your Telegram bot
   
Talk to @BotFather on Telegram

Create a new bot, get the bot token

Get your chat ID via @userinfobot or by messaging your bot

4. Update the script with your credentials
   
Replace these lines:

TELEGRAM_BOT_TOKEN = "your_bot_token_here"

TELEGRAM_CHAT_ID = "your_chat_id_here"

5. Run the script
   
python main.py

You should receive the stock alert in your Telegram chat!

 Automate daily runs

Use cron (Linux/macOS) or Task Scheduler (Windows) to schedule the script to run daily at market open (e.g., 8:30 AM).
