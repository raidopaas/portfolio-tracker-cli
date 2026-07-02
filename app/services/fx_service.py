from decimal import Decimal, ROUND_HALF_UP
import api.fx_api as fx_api
from datetime import datetime, timezone, timedelta

_cached_rate = None
_cached_time = None
_CACHE_TTL = timedelta(minutes=20)

def usd_to_eur(amount, rate):
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def eur_to_usd(amount, rate):
    return (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_usd_to_eur_rate():
    global _cached_rate, _cached_time

    now = datetime.now(timezone.utc)
    
    if _cached_rate is not None and _cached_time is not None:
        if now - _cached_time < _CACHE_TTL:
            return _cached_rate
    
    try:
        rate = fx_api.get_usdeur()
        _cached_rate = rate
        _cached_time = now
        return rate
    except Exception:
        return _cached_rate