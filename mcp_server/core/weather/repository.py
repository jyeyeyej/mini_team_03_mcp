"""날씨 테이블을 조회하는 저장소 계층입니다.

테이블 명세를 받으면 이 파일에만 테이블명, 컬럼명, SQL을 작성합니다.
"""

from typing import Any

from core.weather.exceptions import WeatherSchemaNotReadyError


class WeatherRepository:
    def get_latest_current_weather(self, city: str) -> dict[str, Any]:
        """도시의 최신 현재 날씨 한 건을 반환합니다."""
        raise WeatherSchemaNotReadyError(
            "날씨 테이블 명세를 받은 뒤 WeatherRepository에 현재 날씨 조회 SQL을 연결해야 합니다."
        )

    def get_weather_forecast(self, city: str, days: int) -> list[dict[str, Any]]:
        """도시의 향후 일별 예보를 최대 days건 반환합니다."""
        raise WeatherSchemaNotReadyError(
            "날씨 테이블 명세를 받은 뒤 WeatherRepository에 예보 조회 SQL을 연결해야 합니다."
        )
