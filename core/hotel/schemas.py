from typing import Literal

from pydantic import BaseModel


class Hotel(BaseModel):
    hotel_id: int
    name: str
    city: str
    district: str
    price: int
    near_spot: str


class HotelResponse(BaseModel):
    items: list[Hotel]
    count: int
    source: Literal["postgresql"] = "postgresql"
