"""환경변수 기반 PostgreSQL 연결 생성기입니다."""

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv


def get_database_url() -> str:
    """DATABASE_URL을 읽어 반환합니다. 실제 비밀값은 .env에만 둡니다."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    return database_url


@contextmanager
def get_connection() -> Iterator[object]:
    """PostgreSQL 연결을 열고 사용 후 안전하게 닫습니다."""
    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError("psycopg가 없습니다. requirements.txt 의존성을 설치하세요.") from error

    with psycopg.connect(get_database_url()) as connection:
        yield connection
