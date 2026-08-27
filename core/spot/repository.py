"""PostgreSQL의 spots 테이블을 조회합니다."""

from client.connection import get_pool


async def find_spots_by_city(city: str) -> list[dict]:
    """도시에 속한 관광지를 spot_id 순서대로 조회합니다."""
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT spot_id, name, city, district, category, description
        FROM spots
        WHERE city = $1
        ORDER BY spot_id;
        """,
        city,
    )
    return [dict(row) for row in rows]
