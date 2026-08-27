"""PostgreSQL에 저장된 날씨를 제공하는 stdio MCP Server입니다."""

from mcp.server.fastmcp import FastMCP

from core.weather.service import WeatherService


mcp = FastMCP(
    "weather",
    instructions="PostgreSQL에 저장된 도시별 현재 날씨와 단기 예보를 제공합니다.",
)
weather_service = WeatherService()


@mcp.tool()
def get_current_weather(city: str) -> dict:
    """DB에 저장된 도시의 가장 최근 현재 날씨를 조회합니다."""
    return weather_service.get_current_weather(city)


@mcp.tool()
def get_weather_forecast(city: str, days: int = 1) -> dict:
    """DB에 저장된 도시의 향후 일별 날씨 예보를 조회합니다 (최대 7일)."""
    return weather_service.get_weather_forecast(city, days)


if __name__ == "__main__":
    mcp.run(transport="stdio")
