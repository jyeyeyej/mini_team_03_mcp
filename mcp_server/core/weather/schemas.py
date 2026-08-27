"""날씨 Tool의 응답 모델입니다."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


WeatherCity = Literal["부산", "서울"]


class CurrentWeatherResponse(BaseModel):
    city: WeatherCity
    condition: str
    temperature_c: float
    apparent_temperature_c: float | None
    humidity_pct: int | None
    precipitation_mm: float | None
    weather_code: int
    observed_at: datetime
    fetched_at: datetime
    source: str


class ForecastItem(BaseModel):
    date: date
    day: str
    condition: str
    min_c: float
    max_c: float
    precipitation_probability_pct: int | None
    weather_code: int
    fetched_at: datetime


class WeatherForecastResponse(BaseModel):
    city: WeatherCity
    forecast: list[ForecastItem]
    source: str
