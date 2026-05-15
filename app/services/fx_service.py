from decimal import Decimal, ROUND_HALF_UP
import api.fx_api as fx_api

def usd_to_eur(amount, rate):
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def eur_to_usd(amount, rate):
    return (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_usd_to_eur_rate():
    try:
        return fx_api.get_usdeur()
    except Exception:
        return None