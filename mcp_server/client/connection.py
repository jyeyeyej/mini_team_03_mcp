"""날씨 공급자 HTTP와 기존 PostgreSQL 연결 설정입니다."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


MCP_SERVER_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = MCP_SERVER_ROOT.parent
load_dotenv(MCP_SERVER_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_DATABASE_URL = (
    "postgresql://weather_app:weather_password@127.0.0.1:5432/weather"
)


def database_url() -> str:
    """환경변수 또는 로컬 Docker 기본값에서 PostgreSQL URL을 반환합니다."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def connect_database():
    """기존 DB 실습 코드와의 호환을 위한 지연 PostgreSQL 연결입니다."""
    import psycopg
    from psycopg.rows import dict_row

    return psycopg.connect(
        database_url(),
        row_factory=dict_row,
        connect_timeout=5,
    )


def get_json(
    provider: str,
    url: str,
    params: dict,
) -> dict:
    """외부 날씨 API를 호출하고 JSON Object를 반환합니다."""
    timeout = float(os.getenv("WEATHER_HTTP_TIMEOUT", "10"))
    last_error = "알 수 없는 오류"
    for _ in range(2):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("JSON Object가 아닌 응답입니다.")
                return payload
        except httpx.HTTPStatusError as error:
            last_error = f"HTTP {error.response.status_code}"
        except httpx.TimeoutException:
            last_error = "timeout"
        except httpx.HTTPError:
            last_error = "network error"
        except ValueError:
            last_error = "invalid JSON"
    raise RuntimeError(f"{provider} API 요청 실패: {last_error}")
