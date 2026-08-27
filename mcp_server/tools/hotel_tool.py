from mcp.server.fastmcp import FastMCP

from core.hotel.service import search_hotels


def register_hotel_tool(mcp: FastMCP) -> None:
    @mcp.tool(name="hotel")
    async def hotel(city: str = "부산", max_price: int = 150_000) -> dict:
        """부산 호텔을 1박 최대 가격으로 검색합니다."""
        return await search_hotels(city, max_price)
