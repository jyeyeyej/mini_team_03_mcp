"""날씨 입력을 검증하고 DB 결과를 MCP 응답으로 바꿉니다."""

from core.weather.repository import (
    find_future_forecasts,
    find_latest_current_weather,
)
SUPPORTED_CITIES = {"부산", "서울"}

WEATHER_CONDITIONS = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "약한 어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "약한 어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈보라",
    86: "강한 눈보라",
    95: "뇌우",
    96: "약한 우박을 동반한 뇌우",
    99: "강한 우박을 동반한 뇌우",
}


def validate_city(city: str) -> str:
    """Weather 도메인이 지원하는 도시인지 확인합니다."""
    if city not in SUPPORTED_CITIES:
        raise ValueError("city는 '부산' 또는 '서울'이어야 합니다.")
    return city


def weather_condition(weather_code: int) -> str:
    """Open-Meteo WMO 날씨 코드를 한국어 상태로 변환합니다."""
    return WEATHER_CONDITIONS.get(weather_code, f"알 수 없음({weather_code})")


def day_label(days_from_today: int) -> str:
    """오늘과의 날짜 차이를 사람이 읽기 쉬운 표현으로 변환합니다."""
    if days_from_today == 1:
        return "내일"
    if days_from_today == 2:
        return "모레"
    return f"{days_from_today}일 후"


def get_current_weather(city: str) -> dict:
    """최신 현재 날씨를 일반 딕셔너리로 반환합니다."""
    city = validate_city(city)
    weather = find_latest_current_weather(city)
    if weather is None:
        raise ValueError(
            f"{city}의 현재 날씨가 없습니다. "
            "scripts/seed_open_meteo.py를 먼저 실행해 주세요."
        )

    return {
        "city": city,
        "condition": weather_condition(weather["weather_code"]),
        "temperature_c": weather["temperature_c"],
        "humidity_pct": weather["humidity_pct"],
        "observed_at": weather["observed_at"].isoformat(),
        "source": weather["source"],
    }


def get_weather_forecast(city: str, days: int = 1) -> dict:
    """향후 날씨 예보를 일반 딕셔너리로 반환합니다."""
    city = validate_city(city)
    if not 1 <= days <= 3:
        raise ValueError("days는 1에서 3 사이여야 합니다.")

    forecasts = find_future_forecasts(city, days)
    if len(forecasts) < days:
        raise ValueError(
            f"{city}의 향후 {days}일 예보가 충분하지 않습니다. "
            "scripts/seed_open_meteo.py를 다시 실행해 주세요."
        )

    return {
        "city": city,
        "forecast": [
            {
                "date": forecast["forecast_date"].isoformat(),
                "day": day_label(forecast["days_from_today"]),
                "condition": weather_condition(forecast["weather_code"]),
                "min_c": forecast["min_temperature_c"],
                "max_c": forecast["max_temperature_c"],
            }
            for forecast in forecasts
        ],
        "source": forecasts[0]["source"],
    }
