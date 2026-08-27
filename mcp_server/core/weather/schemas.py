"""Weather MCP의 외부 응답 형식입니다."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CurrentWeatherResponse:
    city: str
    condition: str
    temperature_c: float
    observed_at: str
    source: str = "postgresql"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForecastItem:
    forecast_at: str
    condition: str
    min_c: float
    max_c: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
