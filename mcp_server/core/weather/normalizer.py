"""공급자별 원본 응답을 공통 날씨 모델로 변환합니다."""

import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from core.weather.mappings import (
    KMA_PTY,
    kma_condition,
    kma_text_condition,
    representative_value,
    wmo_condition,
)
from core.weather.schemas import CurrentWeather, DailyForecast


KST = ZoneInfo("Asia/Seoul")


def _float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        match = re.search(r"-?\d+(?:\.\d+)?", str(value))
        return float(match.group()) if match else None


def _precipitation(value) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    if "없음" in text:
        return 0.0
    parsed = _float(text)
    if parsed is None:
        return None
    return parsed / 2 if "미만" in text else parsed


def _parse_open_meteo_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=KST) if parsed.tzinfo is None else parsed


def normalize_open_meteo_current(payload: dict) -> CurrentWeather:
    current = payload["current"]
    condition, condition_code = wmo_condition(current.get("weather_code"))
    precipitation_codes = {
        "drizzle", "rain", "sleet", "snow", "shower", "thunderstorm"
    }
    return CurrentWeather(
        provider="open_meteo",
        observed_at=_parse_open_meteo_time(current["time"]),
        temperature_c=_float(current.get("temperature_2m")),
        humidity_pct=_float(current.get("relative_humidity_2m")),
        precipitation_mm=_float(current.get("precipitation")),
        precipitation_type=condition if condition_code in precipitation_codes else "강수 없음",
        wind_speed_ms=_float(current.get("wind_speed_10m")),
        condition=condition,
        condition_code=condition_code,
        source="Open-Meteo",
    )


def normalize_open_meteo_daily(
    payload: dict,
    start_date: date,
    days: int,
) -> list[DailyForecast]:
    daily = payload["daily"]
    dates = daily.get("time", [])
    result: list[DailyForecast] = []
    for index, raw_date in enumerate(dates):
        forecast_date = date.fromisoformat(raw_date)
        if not start_date <= forecast_date < start_date + timedelta(days=days):
            continue
        condition, condition_code = wmo_condition(daily["weather_code"][index])
        result.append(DailyForecast(
            provider="open_meteo",
            forecast_date=forecast_date,
            forecast_type="daily",
            granularity="daily",
            min_temperature_c=_float(daily["temperature_2m_min"][index]),
            max_temperature_c=_float(daily["temperature_2m_max"][index]),
            precipitation_probability_pct=_float(
                daily["precipitation_probability_max"][index]
            ),
            condition=condition,
            condition_code=condition_code,
            source="Open-Meteo",
        ))
    return result


def normalize_kma_current(items: list[dict], base: datetime) -> CurrentWeather:
    values = {item.get("category"): item.get("obsrValue") for item in items}
    pty = str(values.get("PTY", "0"))
    precipitation_type = KMA_PTY.get(pty, (None, None))[0] or "강수 없음"
    condition, condition_code = kma_condition(None, pty)
    return CurrentWeather(
        provider="kma",
        observed_at=base,
        temperature_c=_float(values.get("T1H")),
        humidity_pct=_float(values.get("REH")),
        precipitation_mm=_precipitation(values.get("RN1")),
        precipitation_type=precipitation_type,
        wind_speed_ms=_float(values.get("WSD")),
        condition=condition,
        condition_code=condition_code,
        source="기상청 초단기실황",
    )


def normalize_kma_short_daily(
    items: list[dict],
    start_date: date,
    days: int,
) -> list[DailyForecast]:
    grouped: dict[date, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    end_date = start_date + timedelta(days=days)
    for item in items:
        raw_date = item.get("fcstDate")
        if not raw_date:
            continue
        forecast_date = datetime.strptime(raw_date, "%Y%m%d").date()
        if start_date <= forecast_date < end_date:
            grouped[forecast_date][item.get("category")].append(item.get("fcstValue"))

    result: list[DailyForecast] = []
    for forecast_date in sorted(grouped):
        categories = grouped[forecast_date]
        temperatures = [_float(value) for value in categories.get("TMP", [])]
        temperatures = [value for value in temperatures if value is not None]
        minimums = [_float(value) for value in categories.get("TMN", [])]
        maximums = [_float(value) for value in categories.get("TMX", [])]
        pops = [_float(value) for value in categories.get("POP", [])]
        precipitation_conditions = [
            kma_condition(None, value)
            for value in categories.get("PTY", [])
            if str(value) != "0"
        ]
        if precipitation_conditions:
            condition = representative_value(value[0] for value in precipitation_conditions)
            condition_code = representative_value(value[1] for value in precipitation_conditions)
        else:
            sky_conditions = [kma_condition(value, 0) for value in categories.get("SKY", [])]
            condition = representative_value(value[0] for value in sky_conditions)
            condition_code = representative_value(value[1] for value in sky_conditions)
        result.append(DailyForecast(
            provider="kma",
            forecast_date=forecast_date,
            forecast_type="short_term",
            granularity="hourly_to_daily",
            min_temperature_c=next(
                (value for value in minimums if value is not None),
                min(temperatures) if temperatures else None,
            ),
            max_temperature_c=next(
                (value for value in maximums if value is not None),
                max(temperatures) if temperatures else None,
            ),
            precipitation_probability_pct=max(
                (value for value in pops if value is not None),
                default=None,
            ),
            condition=condition,
            condition_code=condition_code,
            source="기상청 단기예보",
        ))
    return result


def normalize_kma_mid_daily(
    land: dict,
    temperature: dict,
    base: datetime,
    start_date: date,
    days: int,
) -> list[DailyForecast]:
    end_date = start_date + timedelta(days=days)
    result: list[DailyForecast] = []
    for offset in range(3, 11):
        forecast_date = base.date() + timedelta(days=offset)
        if not start_date <= forecast_date < end_date:
            continue
        condition_am = land.get(f"wf{offset}Am") or land.get(f"wf{offset}")
        condition_pm = land.get(f"wf{offset}Pm") or land.get(f"wf{offset}")
        rain_am = _float(land.get(f"rnSt{offset}Am") or land.get(f"rnSt{offset}"))
        rain_pm = _float(land.get(f"rnSt{offset}Pm") or land.get(f"rnSt{offset}"))
        rain_values = [value for value in (rain_am, rain_pm) if value is not None]
        representative = condition_pm or condition_am
        condition, condition_code = kma_text_condition(representative)
        result.append(DailyForecast(
            provider="kma",
            forecast_date=forecast_date,
            forecast_type="mid_term",
            granularity="am_pm",
            min_temperature_c=_float(temperature.get(f"taMin{offset}")),
            max_temperature_c=_float(temperature.get(f"taMax{offset}")),
            precipitation_probability_pct=max(rain_values, default=None),
            condition=condition,
            condition_code=condition_code,
            condition_am=condition_am,
            condition_pm=condition_pm,
            source="기상청 중기예보",
        ))
    return result
