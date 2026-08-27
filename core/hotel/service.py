from core.hotel.repository import find_hotels
from core.hotel.schemas import HotelResponse


async def search_hotels(city: str, max_price: int) -> dict:
    if city != "부산":
        raise ValueError("city는 '부산'만 지원합니다.")
    if max_price < 1:
        raise ValueError("max_price는 1 이상이어야 합니다.")

    items = await find_hotels(city, max_price)
    return HotelResponse(items=items, count=len(items)).model_dump()
