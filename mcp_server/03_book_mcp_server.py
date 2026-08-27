"""특정 지역 호텔 예약 처리하는 교육용 stdio MCP Server입니다."""

from typing import Literal

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "book",
    instructions="특정 지역의 호텔 정보를 제공하고 예약을 처리합니다.",
)



@mcp.tool()
def bool_hotels(
    hotel_id: Literal["hotel-seoul-001", "hotel-busan-001"],
    date: str,
    nights: int,
) -> dict:
    """호텔 예약 가능 여부를 확인합니다."""
    print(f"Checking availability for hotel_id={hotel_id}, date={date}, nights={nights}")
    # 실제 예약 가능 여부를 확인하는 로직을 구현해야 합니다.        
    return {
        "status": "ok",
        "hotel_id": hotel_id,
        "date": date,
        "nights": nights,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
