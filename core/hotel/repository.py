from client.connection import get_pool


SQL = """
SELECT hotel_id, name, city, district, price, near_spot
FROM hotels
WHERE city = $1
  AND price <= $2
ORDER BY price, hotel_id;
"""


async def find_hotels(city: str, max_price: int) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(SQL, city, max_price)
    return [dict(row) for row in rows]
