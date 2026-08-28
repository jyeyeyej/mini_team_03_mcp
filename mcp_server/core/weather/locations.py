"""지원 도시와 공급자별 위치 식별자를 관리합니다."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherLocation:
    city: str
    latitude: float
    longitude: float
    nx: int
    ny: int
    mid_land_reg_id: str
    mid_temp_reg_id: str


LOCATIONS = {
    "서울": WeatherLocation(
        city="서울",
        latitude=37.5665,
        longitude=126.9780,
        nx=60,
        ny=127,
        mid_land_reg_id="11B00000",
        mid_temp_reg_id="11B10101",
    ),
    "부산": WeatherLocation(
        city="부산",
        latitude=35.1796,
        longitude=129.0756,
        nx=98,
        ny=76,
        mid_land_reg_id="11H20000",
        mid_temp_reg_id="11H20201",
    ),
}


def get_location(city: str) -> WeatherLocation:
    """지원 도시의 위치 정보를 반환합니다."""
    try:
        return LOCATIONS[city]
    except KeyError as error:
        supported = ", ".join(LOCATIONS)
        raise ValueError(f"지원하지 않는 도시입니다: {city}. 지원 도시: {supported}") from error
