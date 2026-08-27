"""Tour MCP 서버에 spot Tool을 등록합니다."""

from mcp.server.fastmcp import FastMCP

from core.spot.service import search_spots


def register_spot_tool(mcp: FastMCP) -> None:
    """공용 Tour MCP 객체에 관광지 검색 Tool을 등록합니다."""

    @mcp.tool(name="spot")
    async def spot(city: str) -> dict:
        """부산 또는 서울의 관광지 목록을 PostgreSQL에서 조회합니다."""
        return await search_spots(city)
