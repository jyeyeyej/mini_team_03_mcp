"""PostgreSQL에서 날씨 데이터를 조회하고 연결 불가 시 데모 데이터를 제공합니다."""

from datetime import date, datetime, timedelta, timezone

from psycopg import OperationalError

from client.connection import connect_database


DEMO_CURRENT = {
    "부산": {"temperature_c": 24.0, "humidity_pct": 70, "weather_code": 2},
    "서울": {"temperature_c": 26.0, "humidity_pct": 62, "weather_code": 1},
}


def _demo_current(city: str):
    values = DEMO_CURRENT.get(city)
    if values is None:
        return None
    return {
        **values,
        "city_name": city,
        "observed_at": datetime.now(timezone.utc),
        "source": "built-in-demo (PostgreSQL unavailable)",
    }


def _demo_forecasts(city: str, days: int):
    if city not in DEMO_CURRENT:
        return []
    today = date.today()
    base = DEMO_CURRENT[city]["temperature_c"]
    return [
        {
            "forecast_date": today + timedelta(days=offset),
            "min_temperature_c": base - 3 + offset,
            "max_temperature_c": base + 2 + offset,
            "precipitation_probability_pct": 20,
            "weather_code": 2,
            "source": "built-in-demo (PostgreSQL unavailable)",
            "days_from_today": offset,
        }
        for offset in range(1, days + 1)
    ]


def find_latest_current_weather(city: str):
    """도시의 가장 최근 현재 날씨 한 건을 반환합니다."""
    try:
        with connect_database() as connection:
            return connection.execute(
            """
            SELECT
                locations.city_name,
                current_weather.observed_at,
                current_weather.temperature_c,
                current_weather.apparent_temperature_c,
                current_weather.humidity_pct,
                current_weather.precipitation_mm,
                current_weather.weather_code,
                current_weather.source,
                current_weather.fetched_at
            FROM weather_current AS current_weather
            JOIN weather_locations AS locations
                ON locations.id = current_weather.location_id
            WHERE locations.city_name = %s
            ORDER BY current_weather.observed_at DESC
            LIMIT 1
            """,
            (city,),
            ).fetchone()
    except OperationalError:
        return _demo_current(city)


def find_future_forecasts(city: str, days: int):
    """도시 현지 날짜를 기준으로 향후 예보를 요청 일수만큼 반환합니다."""
    try:
        with connect_database() as connection:
            return connection.execute(
            """
            SELECT
                forecast.forecast_date,
                forecast.min_temperature_c,
                forecast.max_temperature_c,
                forecast.precipitation_probability_pct,
                forecast.weather_code,
                forecast.source,
                forecast.fetched_at,
                forecast.forecast_date
                    - (CURRENT_TIMESTAMP AT TIME ZONE locations.timezone)::date
                    AS days_from_today
            FROM weather_forecast AS forecast
            JOIN weather_locations AS locations
                ON locations.id = forecast.location_id
            WHERE locations.city_name = %s
              AND forecast.forecast_date
                    > (CURRENT_TIMESTAMP AT TIME ZONE locations.timezone)::date
            ORDER BY forecast.forecast_date
            LIMIT %s
            """,
            (city, days),
            ).fetchall()
    except OperationalError:
        return _demo_forecasts(city, days)
