"""Weather MCP의 입력 검증과 응답 조립을 담당합니다."""

from typing import Any

from core.weather.exceptions import WeatherValidationError
from core.weather.repository import WeatherRepository

MAX_FORECAST_DAYS = 7


class WeatherService:
    def __init__(self, repository: WeatherRepository | None = None) -> None:
        self._repository = repository or WeatherRepository()

    def get_current_weather(self, city: str) -> dict[str, Any]:
        return self._repository.get_latest_current_weather(self._validate_city(city))

    def get_weather_forecast(self, city: str, days: int = 1) -> dict[str, Any]:
        normalized_city = self._validate_city(city)
        self._validate_days(days)
        forecast = self._repository.get_weather_forecast(normalized_city, days)
        return {"city": normalized_city, "forecast": forecast, "source": "postgresql"}

    @staticmethod
    def _validate_city(city: str) -> str:
        if not isinstance(city, str):
            raise WeatherValidationError("city는 문자열이어야 합니다.")
        normalized_city = city.strip()
        if not normalized_city:
            raise WeatherValidationError("city는 비어 있을 수 없습니다.")
        return normalized_city

    @staticmethod
    def _validate_days(days: int) -> None:
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= MAX_FORECAST_DAYS:
            raise WeatherValidationError(f"days는 1에서 {MAX_FORECAST_DAYS} 사이의 정수여야 합니다.")
