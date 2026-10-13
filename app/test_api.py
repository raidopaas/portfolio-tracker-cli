import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("ALPHAVANTAGE_API_KEY")

print("API key loaded:", bool(api_key))

response = requests.get(
    "https://www.alphavantage.co/query",
    params={
        "function": "DIVIDENDS",
        "symbol": "VZ",
        "apikey": api_key
    },
    timeout=15
)

print("HTTP status:", response.status_code)
print("Response:", response.text[:1500])