"""PostgreSQL에서 날씨 데이터를 조회합니다."""

from typing import Any

from client.connection import connect_database


def find_latest_current_weather(city: str) -> dict[str, Any] | None:
    """도시의 가장 최근 현재 날씨 한 건을 반환합니다."""
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


def find_future_forecasts(city: str, days: int) -> list[dict[str, Any]]:
    """도시 현지 날짜를 기준으로 향후 예보를 요청 일수만큼 반환합니다."""
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
