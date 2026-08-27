"""Spot Tool의 입출력 형식입니다."""

from pydantic import BaseModel, Field


class SpotItem(BaseModel):
    """관광지 한 건의 정보입니다."""

    spot_id: int
    name: str
    city: str
    district: str
    category: str
    description: str


class SpotSearchResponse(BaseModel):
    """spot Tool이 반환하는 응답입니다."""

    items: list[SpotItem] = Field(default_factory=list)
    count: int
    source: str = "postgresql"
