"""Open-Meteo의 현재 날씨와 일별 예보를 PostgreSQL에 적재합니다."""

import argparse
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_DATABASE_URL = (
    "postgresql://weather_app:weather_password@127.0.0.1:5432/weather"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open-Meteo 날씨를 Docker PostgreSQL에 적재합니다."
    )
    parser.add_argument(
        "--forecast-days",
        type=int,
        default=3,
        choices=range(1, 16),
        metavar="1-15",
        help="오늘을 제외하고 저장할 예보 일수(기본값: 3)",
    )
    return parser.parse_args()


def database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def load_locations(connection: psycopg.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, city_name, latitude, longitude, timezone
        FROM weather_locations
        ORDER BY id
        """
    ).fetchall()
    if not rows:
        raise RuntimeError("weather_locations에 적재할 도시가 없습니다.")
    return rows


def fetch_weather(location: dict[str, Any], forecast_days: int) -> dict[str, Any]:
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,apparent_temperature,relative_humidity_2m,"
            "precipitation,weather_code"
        ),
        "daily": (
            "weather_code,temperature_2m_min,temperature_2m_max,"
            "precipitation_probability_max"
        ),
        "timezone": location["timezone"],
        "forecast_days": forecast_days + 1,
    }
    with httpx.Client(timeout=20) as client:
        response = client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    if "current" not in payload or "daily" not in payload:
        raise RuntimeError(
            f"{location['city_name']}의 Open-Meteo 응답 형식이 올바르지 않습니다."
        )
    return payload


def store_weather(
    connection: psycopg.Connection,
    location: dict[str, Any],
    payload: dict[str, Any],
    forecast_days: int,
) -> tuple[int, int]:
    current = payload["current"]
    utc_offset = timezone(
        timedelta(seconds=int(payload.get("utc_offset_seconds", 0)))
    )
    observed_at = datetime.fromisoformat(current["time"]).replace(
        tzinfo=utc_offset
    )

    connection.execute(
        """
        INSERT INTO weather_current (
            location_id,
            observed_at,
            temperature_c,
            apparent_temperature_c,
            humidity_pct,
            precipitation_mm,
            weather_code,
            source,
            raw_payload,
            fetched_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'open-meteo', %s, CURRENT_TIMESTAMP)
        ON CONFLICT (location_id, observed_at)
        DO UPDATE SET
            temperature_c = EXCLUDED.temperature_c,
            apparent_temperature_c = EXCLUDED.apparent_temperature_c,
            humidity_pct = EXCLUDED.humidity_pct,
            precipitation_mm = EXCLUDED.precipitation_mm,
            weather_code = EXCLUDED.weather_code,
            raw_payload = EXCLUDED.raw_payload,
            fetched_at = CURRENT_TIMESTAMP
        """,
        (
            location["id"],
            observed_at,
            current["temperature_2m"],
            current.get("apparent_temperature"),
            current.get("relative_humidity_2m"),
            current.get("precipitation"),
            current["weather_code"],
            Jsonb({
                "current": current,
                "current_units": payload.get("current_units"),
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
                "timezone": payload.get("timezone"),
            }),
        ),
    )

    daily = payload["daily"]
    available_days = len(daily.get("time", [])) - 1
    if available_days < forecast_days:
        raise RuntimeError(
            f"{location['city_name']} 예보가 {forecast_days}일보다 적습니다."
        )

    for index in range(1, forecast_days + 1):
        raw_day = {
            key: values[index]
            for key, values in daily.items()
            if isinstance(values, list) and len(values) > index
        }
        connection.execute(
            """
            INSERT INTO weather_forecast (
                location_id,
                forecast_date,
                min_temperature_c,
                max_temperature_c,
                precipitation_probability_pct,
                weather_code,
                source,
                raw_payload,
                fetched_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'open-meteo', %s, CURRENT_TIMESTAMP)
            ON CONFLICT (location_id, forecast_date)
            DO UPDATE SET
                min_temperature_c = EXCLUDED.min_temperature_c,
                max_temperature_c = EXCLUDED.max_temperature_c,
                precipitation_probability_pct =
                    EXCLUDED.precipitation_probability_pct,
                weather_code = EXCLUDED.weather_code,
                raw_payload = EXCLUDED.raw_payload,
                fetched_at = CURRENT_TIMESTAMP
            """,
            (
                location["id"],
                daily["time"][index],
                daily["temperature_2m_min"][index],
                daily["temperature_2m_max"][index],
                daily["precipitation_probability_max"][index],
                daily["weather_code"][index],
                Jsonb(raw_day),
            ),
        )

    return 1, forecast_days


def main() -> None:
    args = parse_args()
    current_count = 0
    forecast_count = 0

    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        locations = load_locations(connection)
        for location in locations:
            payload = fetch_weather(location, args.forecast_days)
            current_rows, forecast_rows = store_weather(
                connection,
                location,
                payload,
                args.forecast_days,
            )
            current_count += current_rows
            forecast_count += forecast_rows
            print(
                f"{location['city_name']}: 현재 날씨 1건, "
                f"예보 {forecast_rows}건 적재 완료"
            )

    print(
        f"완료: 현재 날씨 {current_count}건, "
        f"일별 예보 {forecast_count}건"
    )


if __name__ == "__main__":
    main()
