"""정규화된 두 공급자의 날씨 수치와 상태를 비교합니다."""

from core.weather.schemas import CurrentWeather, DailyForecast


def _difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(left - right, 2)


def _condition_match(left: str | None, right: str | None) -> bool | None:
    if left is None or right is None:
        return None
    return left == right


def compare_current(
    open_meteo: CurrentWeather | None,
    kma: CurrentWeather | None,
) -> dict:
    if open_meteo is None or kma is None:
        return {}
    return {
        "basis": "open_meteo_minus_kma",
        "temperature_c": _difference(open_meteo.temperature_c, kma.temperature_c),
        "humidity_pct": _difference(open_meteo.humidity_pct, kma.humidity_pct),
        "precipitation_mm": _difference(open_meteo.precipitation_mm, kma.precipitation_mm),
        "wind_speed_ms": _difference(open_meteo.wind_speed_ms, kma.wind_speed_ms),
        "condition_match": _condition_match(open_meteo.condition_code, kma.condition_code),
        "observation_time_gap_minutes": round(
            abs((open_meteo.observed_at - kma.observed_at).total_seconds()) / 60,
            1,
        ),
    }


def compare_daily(
    open_meteo: DailyForecast | None,
    kma: DailyForecast | None,
) -> dict:
    if open_meteo is None or kma is None:
        return {}
    return {
        "basis": "open_meteo_minus_kma",
        "min_temperature_c": _difference(
            open_meteo.min_temperature_c,
            kma.min_temperature_c,
        ),
        "max_temperature_c": _difference(
            open_meteo.max_temperature_c,
            kma.max_temperature_c,
        ),
        "precipitation_probability_pct": _difference(
            open_meteo.precipitation_probability_pct,
            kma.precipitation_probability_pct,
        ),
        "condition_match": _condition_match(
            open_meteo.condition_code,
            kma.condition_code,
        ),
    }
