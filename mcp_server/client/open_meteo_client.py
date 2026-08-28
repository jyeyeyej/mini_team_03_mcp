"""Open-Meteo의 현재 날씨와 일별 예보를 조회합니다."""

import os

from client.connection import get_json
from core.weather.exceptions import WeatherProviderError
from core.weather.locations import WeatherLocation


OPEN_METEO_BASE_URL = os.getenv(
    "OPEN_METEO_BASE_URL",
    "https://api.open-meteo.com/v1",
).rstrip("/")


def fetch_weather(location: WeatherLocation, forecast_days: int = 8) -> dict:
    """현재 날씨와 오늘을 포함한 일별 예보를 한 번에 조회합니다."""
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "timezone": "Asia/Seoul",
        "wind_speed_unit": "ms",
        "forecast_days": forecast_days,
    }
    try:
        payload = get_json(
            "open_meteo",
            f"{OPEN_METEO_BASE_URL}/forecast",
            params,
        )
    except RuntimeError as error:
        raise WeatherProviderError("open_meteo", str(error)) from error
    if "current" not in payload or "daily" not in payload:
        raise WeatherProviderError("open_meteo", "현재 또는 일별 예보가 없습니다.")
    return payload
