import requests
import pandas as pd

# --- Settings: Customize these thresholds to filter stocks ---
MIN_PERCENT_GAIN = 5         # Minimum % price increase to qualify as a gainer
MIN_VOLUME = 500000          # Minimum trading volume
MIN_PRICE = 1                # Minimum stock price
MAX_PRICE = 50               # Maximum stock price

# --- Telegram credentials ---
# Replace these with your Telegram bot token and your chat ID
TELEGRAM_BOT_TOKEN = "8079888447:AAFuXlpSzfqRD-_6wmgvp-lnMbKbd_fQ7F8"
TELEGRAM_CHAT_ID = "8271650437"
# Volatile premarket filter (under $10 stocks)
VOLATILE_MAX_PRICE = 10
VOLATILE_PREMARKET_CHANGE = 3  # % premarket change threshold

# --- Helper: Get latest news for a symbol ---
def get_latest_news(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers).json()
        news_items = response.get("news", [])
        if news_items:
            title = news_items[0]["title"]
            link = news_items[0]["link"]
            return f"[📰 {title}]({link})"
        else:
            return "No news found"
    except:
        return "Error fetching news"

# --- Get top daily gainers from Yahoo Finance ---
def get_top_gainers():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers).json()

    try:
        items = response['finance']['result'][0]['quotes']
        gainers = []
        for item in items:
            if 'regularMarketPrice' not in item or 'regularMarketChangePercent' not in item:
                continue

            price = item['regularMarketPrice']
            percent_change = item['regularMarketChangePercent']
            volume = item.get('regularMarketVolume', 0)

            if price and percent_change and volume:
                if (percent_change >= MIN_PERCENT_GAIN and
                    volume >= MIN_VOLUME and
                    MIN_PRICE <= price <= MAX_PRICE):
                    gainers.append({
                        'Symbol': item['symbol'],
                        'Name': item.get('shortName', ''),
                        'Price': price,
                        'Change %': round(percent_change, 2),
                        'Volume': volume
                    })

        return pd.DataFrame(gainers)

    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

# --- Get volatile stocks under $10 in premarket ---
def get_volatile_premarket_stocks():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=most_actives"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers).json()

    try:
        items = response['finance']['result'][0]['quotes']
        volatile = []
        for item in items:
            price = item.get('regularMarketPrice')
            change_percent = item.get('preMarketChangePercent')
            volume = item.get('regularMarketVolume', 0)

            if price and change_percent and price <= VOLATILE_MAX_PRICE and abs(change_percent) >= VOLATILE_PREMARKET_CHANGE:
                volatile.append({
                    'Symbol': item['symbol'],
                    'Name': item.get('shortName', ''),
                    'Price': price,
                    'Premarket Change %': round(change_percent, 2),
                    'Volume': volume
                })

        return pd.DataFrame(volatile)

    except Exception as e:
        print("Error fetching premarket:", e)
        return pd.DataFrame()

# --- Format stock lists into Telegram-friendly Markdown message ---
def format_stock_message(df, title, include_news=True, is_premarket=False):
    if df.empty:
        return f"*{title}*\n_No stocks found._\n\n"

    message = f"*{title}*\n\n"
    for _, row in df.iterrows():
        symbol = row['Symbol']
        name = row['Name'][:25].replace('_', '\\_').replace('*', '\\*')
        price = f"${row['Price']:.2f}"
        volume = f"{row['Volume']:,}"
        percent = f"{row['Change %']}%" if not is_premarket else f"{row['Premarket Change %']}%"

        link = f"[{symbol}](https://finance.yahoo.com/quote/{symbol})"
        news = get_latest_news(symbol) if include_news else ""

        message += f"{link} | {name}\n"
        message += f"💵 Price: {price} | 📊 Volume: {volume} | 🔺 Change: {percent}\n"
        if news:
            message += f"{news}\n"
        message += "\n"

    return message

# --- Send message to Telegram ---
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)
    try:
        response.raise_for_status()
        print("✅ Telegram message sent!")
    except requests.exceptions.HTTPError as err:
        print(f"❌ Failed to send Telegram message: {err}")
        print("Response content:", response.text)

# --- Main execution ---
if __name__ == "__main__":
    # Get daily top gainers
    df_gainers = get_top_gainers()

    # Get volatile premarket stocks under $10
    df_volatile = get_volatile_premarket_stocks()

    # Format both messages
    message = format_stock_message(df_gainers, "📈 Top Gainers Today")
    message += format_stock_message(df_volatile, "🔥 Volatile Premarket Stocks Under $10", is_premarket=True)

    # Send the combined message
    send_telegram_message(message)
