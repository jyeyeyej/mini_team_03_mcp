CREATE TABLE IF NOT EXISTS spots (
    spot_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(20) NOT NULL,
    district VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    CONSTRAINT spots_city_name_key UNIQUE (city, name)
);

CREATE INDEX IF NOT EXISTS idx_spots_city ON spots (city);
