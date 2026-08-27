"""날씨 MCP에서 사용하는 예외입니다."""


class WeatherValidationError(ValueError):
    """MCP 도구 입력값이 올바르지 않을 때 발생합니다."""


class WeatherSchemaNotReadyError(RuntimeError):
    """DB 테이블 명세가 아직 연결되지 않았을 때 발생합니다."""
