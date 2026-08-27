"""PostgreSQL 연결 풀을 한 번 만들고 재사용합니다."""

import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    """환경변수 설정으로 PostgreSQL 연결 풀을 반환합니다."""
    global _pool

    if _pool is None:
        async with _pool_lock:
            if _pool is None:
                _pool = await asyncpg.create_pool(
                    host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
                    port=int(os.getenv("POSTGRES_PORT", "5432")),
                    database=os.getenv("POSTGRES_DB", "travel_mcp"),
                    user=os.getenv("POSTGRES_USER", "postgres"),
                    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                    min_size=1,
                    max_size=5,
                )

    return _pool
