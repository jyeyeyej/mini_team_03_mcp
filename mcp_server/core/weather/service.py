"""Open-Meteo와 기상청 날씨를 조회·정규화·비교합니다."""

import time
from datetime import datetime, timedelta
from typing import Callable
from zoneinfo import ZoneInfo

from client.kma_client import fetch_current, fetch_mid_forecast, fetch_short_forecast
from client.open_meteo_client import fetch_weather
from core.weather.comparator import compare_current, compare_daily
from core.weather.locations import get_location
from core.weather.normalizer import (
    normalize_kma_current,
    normalize_kma_mid_daily,
    normalize_kma_short_daily,
    normalize_open_meteo_current,
    normalize_open_meteo_daily,
)


KST = ZoneInfo("Asia/Seoul")
_CACHE: dict[tuple, tuple[float, object]] = {}


def _cached(key: tuple, loader: Callable[[], object], ttl: int = 600):
    now = time.monotonic()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1]
    value = loader()
    _CACHE[key] = (now, value)
    return value


def _status(success_count: int, expected_count: int) -> str:
    if success_count == expected_count:
        return "complete"
    return "partial" if success_count else "error"


def compare_current_weather(city: str) -> dict:
    """두 공급자의 현재 날씨와 수치 차이를 반환합니다."""
    location = get_location(city)
    errors: dict[str, str] = {}
    open_current = None
    kma_current = None

    try:
        open_payload = _cached(
            ("open_meteo", city),
            lambda: fetch_weather(location),
        )
        open_current = normalize_open_meteo_current(open_payload)
    except Exception as error:
        errors["open_meteo"] = str(error)

    try:
        kma_items, base = _cached(
            ("kma_current", city, datetime.now(KST).strftime("%Y%m%d%H")),
            lambda: fetch_current(location),
        )
        kma_current = normalize_kma_current(kma_items, base)
    except Exception as error:
        errors["kma"] = str(error)

    success_count = sum(item is not None for item in (open_current, kma_current))
    return {
        "city": city,
        "status": _status(success_count, 2),
        "generated_at": datetime.now(KST).isoformat(),
        "providers": {
            "open_meteo": open_current.to_dict() if open_current else None,
            "kma": kma_current.to_dict() if kma_current else None,
        },
        "difference": compare_current(open_current, kma_current),
        "errors": errors,
    }


def compare_weekly_forecast(city: str, days: int = 7) -> dict:
    """오늘 다음 날부터 요청 일수까지 두 공급자의 일별 예보를 비교합니다."""
    if not 1 <= days <= 7:
        raise ValueError("days는 1에서 7 사이여야 합니다.")

    location = get_location(city)
    start_date = datetime.now(KST).date() + timedelta(days=1)
    errors: dict[str, str] = {}
    open_daily = []
    kma_short = []
    kma_mid = []

    try:
        open_payload = _cached(
            ("open_meteo", city),
            lambda: fetch_weather(location),
        )
        open_daily = normalize_open_meteo_daily(open_payload, start_date, days)
    except Exception as error:
        errors["open_meteo"] = str(error)

    try:
        short_items, _ = _cached(
            ("kma_short", city, datetime.now(KST).strftime("%Y%m%d%H")),
            lambda: fetch_short_forecast(location),
            ttl=1800,
        )
        kma_short = normalize_kma_short_daily(short_items, start_date, days)
    except Exception as error:
        errors["kma_short"] = str(error)

    try:
        land, temperature, base = _cached(
            ("kma_mid", city, datetime.now(KST).strftime("%Y%m%d%H")),
            lambda: fetch_mid_forecast(location),
            ttl=3600,
        )
        kma_mid = normalize_kma_mid_daily(
            land,
            temperature,
            base,
            start_date,
            days,
        )
    except Exception as error:
        errors["kma_mid"] = str(error)

    open_by_date = {item.forecast_date: item for item in open_daily}
    kma_by_date = {item.forecast_date: item for item in kma_mid}
    kma_by_date.update({item.forecast_date: item for item in kma_short})

    forecasts = []
    compared_days = 0
    for offset in range(days):
        forecast_date = start_date + timedelta(days=offset)
        open_item = open_by_date.get(forecast_date)
        kma_item = kma_by_date.get(forecast_date)
        if open_item and kma_item:
            compared_days += 1
        forecasts.append({
            "date": forecast_date.isoformat(),
            "open_meteo": open_item.to_dict() if open_item else None,
            "kma": kma_item.to_dict() if kma_item else None,
            "difference": compare_daily(open_item, kma_item),
        })

    available_count = int(bool(open_daily)) + int(bool(kma_short or kma_mid))
    if len(open_daily) >= days and compared_days == days:
        result_status = "complete"
    elif available_count:
        result_status = "partial"
    else:
        result_status = "error"
    return {
        "city": city,
        "status": result_status,
        "generated_at": datetime.now(KST).isoformat(),
        "period": {
            "start_date": start_date.isoformat(),
            "days": days,
        },
        "summary": {
            "open_meteo_days": len(open_daily),
            "kma_days": len(kma_by_date),
            "compared_days": compared_days,
        },
        "forecasts": forecasts,
        "errors": errors,
    }
