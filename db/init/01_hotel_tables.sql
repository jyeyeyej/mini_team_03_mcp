CREATE TABLE IF NOT EXISTS hotels (
    hotel_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    district TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price > 0),
    near_spot TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hotels_city_price
ON hotels (city, price);
