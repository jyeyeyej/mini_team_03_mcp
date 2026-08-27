"""Docker PostgreSQL의 날씨 Tool을 공개하는 stdio MCP Server입니다."""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from core.weather.service import (
    get_current_weather as get_current_weather_service,
    get_weather_forecast as get_weather_forecast_service,
)


mcp = FastMCP(
    "weather",
    instructions="Docker PostgreSQL에 저장된 부산과 서울의 날씨를 제공합니다.",
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
    mcp.run(transport="stdio")
