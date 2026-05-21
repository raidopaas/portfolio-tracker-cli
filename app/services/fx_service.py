from decimal import Decimal, ROUND_HALF_UP
import api.fx_api as fx_api

_cached_rate = None

def usd_to_eur(amount, rate):
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def eur_to_usd(amount, rate):
    return (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_usd_to_eur_rate():
    global _cached_rate
    
    if _cached_rate is not None:
        return _cached_rate
    
    try:
        _cached_rate = fx_api.get_usdeur()
        return _cached_rate
    except Exception:
        return None