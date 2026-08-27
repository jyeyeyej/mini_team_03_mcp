"""공용 PostgreSQL 연결 설정입니다."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_DATABASE_URL = (
    "postgresql://weather_app:weather_password@127.0.0.1:5432/weather"
)


def database_url() -> str:
    """환경변수 또는 로컬 Docker 기본값에서 PostgreSQL URL을 반환합니다."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def connect_database() -> psycopg.Connection[dict[str, Any]]:
    """dict 형태의 행을 반환하는 PostgreSQL 연결을 생성합니다."""
    return psycopg.connect(
        database_url(),
        row_factory=dict_row,
        connect_timeout=5,
    )
