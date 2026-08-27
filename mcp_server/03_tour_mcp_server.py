"""Hotel과 Spot Tool을 제공하는 Streamable HTTP Tour MCP Server입니다."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp_server.tools.hotel_tool import register_hotel_tool
from mcp_server.tools.spot_tool import register_spot_tool


load_dotenv(PROJECT_ROOT / ".env")

tour_mcp = FastMCP(
    "tour",
    instructions="부산 숙소와 부산·서울 관광지를 PostgreSQL에서 조회합니다.",
    host=os.getenv("TOUR_MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("TOUR_MCP_PORT", "8033")),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)

register_hotel_tool(tour_mcp)
register_spot_tool(tour_mcp)


if __name__ == "__main__":
    tour_mcp.run(transport="streamable-http")
