import requests
from decimal import Decimal
from config.settings import API_KEY, BASE_URL

def get_usdeur():
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": "USD",
        "to_currency": "EUR",
        "apikey": API_KEY
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        rate = Decimal(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

        return rate

    except Exception:
        raise RuntimeError("Failed to fetch FX rate.")