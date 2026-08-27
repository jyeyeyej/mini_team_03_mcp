BEGIN;

INSERT INTO weather_locations (city_name, latitude, longitude, timezone)
VALUES
    ('서울', 37.5665, 126.9780, 'Asia/Seoul'),
    ('부산', 35.1796, 129.0756, 'Asia/Seoul')
ON CONFLICT (city_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    timezone = EXCLUDED.timezone;

COMMIT;
