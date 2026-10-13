import requests
from decimal import Decimal
from config.settings import API_KEY, BASE_URL
from datetime import datetime

def get_latest_us_stock_price(symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        time_series = data["Time Series (Daily)"]
        latest_date = next(iter(time_series)) # first key (most recent day)
        latest_close = Decimal(time_series[latest_date]["4. close"])

        return latest_close

    except Exception:
        raise RuntimeError("Failed to fetch stock data.")

def get_latest_us_stock_dividend(symbol):
    params = {
        "function": "DIVIDENDS",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        dividends = data["data"]

        if not dividends:
            return Decimal("0.00"), None

        latest = max(dividends, key=lambda item: item["payment_date"])
        dividend = Decimal(latest["amount"])
        date = datetime.strptime(latest["payment_date"], "%Y-%m-%d").date()
        
        return dividend, date

    except Exception as e:
        raise RuntimeError("Failed to fetch stock dividend data.") from e