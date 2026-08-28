"""Open-Meteo와 기상청 날씨를 비교하는 Streamable HTTP MCP Server입니다."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from core.weather.service import (
    compare_current_weather as compare_current_weather_service,
    compare_weekly_forecast as compare_weekly_forecast_service,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / "mcp_server" / ".env")
load_dotenv(PROJECT_ROOT / ".env")

mcp = FastMCP(
    "weather-comparison",
    instructions=(
        "서울과 부산의 현재 날씨 및 향후 7일 예보를 "
        "Open-Meteo와 기상청 데이터로 비교합니다."
    ),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8010")),
)


@mcp.tool()
def compare_current_weather(city: Literal["부산", "서울"]) -> dict:
    """도시의 현재 날씨를 Open-Meteo와 기상청 초단기실황으로 비교합니다."""
    return compare_current_weather_service(city)


@mcp.tool()
def compare_weekly_forecast(
    city: Literal["부산", "서울"],
    days: int = 7,
) -> dict:
    """도시의 향후 1~7일 예보를 Open-Meteo와 기상청 단기·중기예보로 비교합니다."""
    return compare_weekly_forecast_service(city, days)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
