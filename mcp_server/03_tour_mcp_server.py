"""서울과 부산의 관광지 정보를 제공하는 교육용 stdio MCP Server입니다."""

from typing import Literal

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "tour",
    instructions="서울과 부산의 대표 관광지 정보를 제공합니다.",
)


ATTRACTIONS = {
    "서울": [
        {
            "attraction_id": "seoul-gyeongbokgung",
            "name": "경복궁",
            "area": "종로구",
            "description": "조선 왕조의 대표 궁궐로, 고궁의 건축과 경관을 둘러볼 수 있습니다.",
            "recommended_for": "한국의 역사와 전통 건축에 관심 있는 여행자",
        },
        {
            "attraction_id": "seoul-namsan-tower",
            "name": "N서울타워",
            "area": "용산구",
            "description": "남산 정상에서 서울 도심의 전경을 감상할 수 있는 전망 명소입니다.",
            "recommended_for": "도시 전망과 야경을 즐기고 싶은 여행자",
        },
        {
            "attraction_id": "seoul-bukchon",
            "name": "북촌한옥마을",
            "area": "종로구",
            "description": "전통 한옥이 모여 있는 골목을 걸으며 서울의 옛 모습을 만날 수 있습니다.",
            "recommended_for": "산책과 전통적인 분위기를 좋아하는 여행자",
        },
    ],
    "부산": [
        {
            "attraction_id": "busan-haeundae",
            "name": "해운대해수욕장",
            "area": "해운대구",
            "description": "넓은 백사장과 바다 풍경으로 유명한 부산의 대표 해변입니다.",
            "recommended_for": "바다와 해변 산책을 즐기고 싶은 여행자",
        },
        {
            "attraction_id": "busan-gamcheon",
            "name": "감천문화마을",
            "area": "사하구",
            "description": "알록달록한 건물과 골목길, 예술 작품을 만날 수 있는 산동네 마을입니다.",
            "recommended_for": "사진 촬영과 골목 여행을 좋아하는 여행자",
        },
        {
            "attraction_id": "busan-jagalchi",
            "name": "자갈치시장",
            "area": "중구",
            "description": "신선한 해산물과 부산 항구의 활기찬 분위기를 경험할 수 있는 시장입니다.",
            "recommended_for": "지역 음식과 시장 구경을 좋아하는 여행자",
        },
    ],
}


@mcp.tool()
def search_attractions(city: Literal["부산", "서울"]) -> dict:
    """도시의 대표 관광지 목록을 조회합니다."""
    return {
        "city": city,
        "items": ATTRACTIONS[city],
        "source": "lab-tour-attractions-catalog",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
