"""Docker PostgreSQL의 날씨 Tool을 공개하는 Streamable HTTP MCP Server입니다."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from core.weather.service import (
    get_current_weather as get_current_weather_service,
    get_weather_forecast as get_weather_forecast_service,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

mcp = FastMCP(
    "weather",
    instructions="Docker PostgreSQL에 저장된 부산과 서울의 날씨를 제공합니다.",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8010")),
)


@mcp.tool()
def get_current_weather(city: Literal["부산", "서울"]) -> dict:
    """Docker PostgreSQL에서 도시의 최신 현재 날씨를 조회합니다."""
    return get_current_weather_service(city)


@mcp.tool()
def get_weather_forecast(
    city: Literal["부산", "서울"],
    days: int = 1,
) -> dict:
    """Docker PostgreSQL에서 오늘을 제외한 향후 날씨 예보를 조회합니다."""
    return get_weather_forecast_service(city, days)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
