"""공급자 응답을 비교하기 위한 내부 공통 모델입니다."""

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any


@dataclass
class CurrentWeather:
    provider: str
    observed_at: datetime
    temperature_c: float | None
    humidity_pct: float | None
    precipitation_mm: float | None
    precipitation_type: str | None
    wind_speed_ms: float | None
    condition: str | None
    condition_code: str | None
    source: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["observed_at"] = self.observed_at.isoformat()
        return result


@dataclass
class DailyForecast:
    provider: str
    forecast_date: date
    forecast_type: str
    granularity: str
    min_temperature_c: float | None
    max_temperature_c: float | None
    precipitation_probability_pct: float | None
    condition: str | None
    condition_code: str | None
    condition_am: str | None = None
    condition_pm: str | None = None
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["date"] = result.pop("forecast_date").isoformat()
        return result
