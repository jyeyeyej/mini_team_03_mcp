"""Spot Tool의 입력 검증과 응답 조립을 담당합니다."""

from core.spot.repository import find_spots_by_city
from core.spot.schemas import SpotItem, SpotSearchResponse


SUPPORTED_CITIES = {"부산", "서울"}


async def search_spots(city: str) -> dict:
    """부산 또는 서울의 관광지 목록을 반환합니다."""
    normalized_city = city.strip() if isinstance(city, str) else ""
    if normalized_city not in SUPPORTED_CITIES:
        raise ValueError("city는 '부산' 또는 '서울'만 입력할 수 있습니다.")

    rows = await find_spots_by_city(normalized_city)
    response = SpotSearchResponse(
        items=[SpotItem(**row) for row in rows],
        count=len(rows),
    )
    return response.model_dump()
