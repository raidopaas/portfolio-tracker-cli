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
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        dividend = Decimal(data["DividendPerShare"])
        date = data["DividendDate"]

        if not date or date == "None":
            date = None
        else:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        
        return dividend, date

    except Exception as e:
        raise RuntimeError("Failed to fetch stock dividend data.") from e