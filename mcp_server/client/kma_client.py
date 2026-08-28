"""기상청 초단기실황·단기예보·중기예보를 조회합니다."""

import os
from datetime import datetime, timedelta
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from client.connection import get_json
from core.weather.exceptions import WeatherProviderError
from core.weather.locations import WeatherLocation


KST = ZoneInfo("Asia/Seoul")
KMA_SHORT_BASE_URL = os.getenv(
    "KMA_SHORT_BASE_URL",
    "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0",
).rstrip("/")
KMA_MID_BASE_URL = os.getenv(
    "KMA_MID_BASE_URL",
    "https://apis.data.go.kr/1360000/MidFcstInfoService",
).rstrip("/")
SHORT_FORECAST_TIMES = (2, 5, 8, 11, 14, 17, 20, 23)


def service_key() -> str:
    """URL 인코딩 키와 Decoding 키를 모두 안전하게 params에 사용할 수 있게 합니다."""
    raw = os.getenv("KMA_SERVICE_KEY", "").strip()
    if not raw:
        raise WeatherProviderError("kma", "KMA_SERVICE_KEY가 필요합니다.")
    return unquote(raw)


def _latest_hourly_base(now: datetime | None = None) -> datetime:
    current = (now or datetime.now(KST)).astimezone(KST) - timedelta(minutes=40)
    return current.replace(minute=0, second=0, microsecond=0)


def _latest_short_base(now: datetime | None = None) -> datetime:
    current = (now or datetime.now(KST)).astimezone(KST) - timedelta(minutes=20)
    candidates = [hour for hour in SHORT_FORECAST_TIMES if hour <= current.hour]
    if candidates:
        return current.replace(
            hour=max(candidates), minute=0, second=0, microsecond=0
        )
    previous = current - timedelta(days=1)
    return previous.replace(hour=23, minute=0, second=0, microsecond=0)


def _latest_mid_base(now: datetime | None = None) -> datetime:
    current = (now or datetime.now(KST)).astimezone(KST) - timedelta(minutes=20)
    if current.hour >= 18:
        hour = 18
    elif current.hour >= 6:
        hour = 6
    else:
        current -= timedelta(days=1)
        hour = 18
    return current.replace(hour=hour, minute=0, second=0, microsecond=0)


def _items(endpoint: str, params: dict) -> list[dict]:
    common = {
        "serviceKey": service_key(),
        "pageNo": 1,
        "numOfRows": 2000,
        "dataType": "JSON",
    }
    try:
        payload = get_json("kma", endpoint, {**common, **params})
        response = payload.get("response", {})
        header = response.get("header", {})
        result_code = str(header.get("resultCode", ""))
        if result_code != "00":
            message = header.get("resultMsg", "알 수 없는 기상청 오류")
            raise WeatherProviderError("kma", f"{result_code}: {message}")
        raw_items = response.get("body", {}).get("items", {})
        if not raw_items:
            return []
        items = raw_items.get("item", [])
        return items if isinstance(items, list) else [items]
    except WeatherProviderError:
        raise
    except (RuntimeError, AttributeError, TypeError) as error:
        raise WeatherProviderError("kma", str(error)) from error


def fetch_current(
    location: WeatherLocation,
    now: datetime | None = None,
) -> tuple[list[dict], datetime]:
    base = _latest_hourly_base(now)
    items = _items(
        f"{KMA_SHORT_BASE_URL}/getUltraSrtNcst",
        {
            "base_date": base.strftime("%Y%m%d"),
            "base_time": base.strftime("%H%M"),
            "nx": location.nx,
            "ny": location.ny,
        },
    )
    if not items:
        raise WeatherProviderError("kma", "초단기실황 데이터가 없습니다.")
    return items, base


def fetch_short_forecast(
    location: WeatherLocation,
    now: datetime | None = None,
) -> tuple[list[dict], datetime]:
    base = _latest_short_base(now)
    items = _items(
        f"{KMA_SHORT_BASE_URL}/getVilageFcst",
        {
            "base_date": base.strftime("%Y%m%d"),
            "base_time": base.strftime("%H%M"),
            "nx": location.nx,
            "ny": location.ny,
        },
    )
    if not items:
        raise WeatherProviderError("kma", "단기예보 데이터가 없습니다.")
    return items, base


def fetch_mid_forecast(
    location: WeatherLocation,
    now: datetime | None = None,
) -> tuple[dict, dict, datetime]:
    base = _latest_mid_base(now)
    tm_fc = base.strftime("%Y%m%d%H%M")
    land_items = _items(
        f"{KMA_MID_BASE_URL}/getMidLandFcst",
        {"regId": location.mid_land_reg_id, "tmFc": tm_fc},
    )
    temperature_items = _items(
        f"{KMA_MID_BASE_URL}/getMidTa",
        {"regId": location.mid_temp_reg_id, "tmFc": tm_fc},
    )
    if not land_items or not temperature_items:
        raise WeatherProviderError("kma", "중기예보 데이터가 없습니다.")
    return land_items[0], temperature_items[0], base
