INSERT INTO hotels (hotel_id, name, city, district, price, near_spot) VALUES
    (1, '해운대 오션 스테이', '부산', '해운대구', 89000, '해운대해수욕장'),
    (2, '광안리 비치 호텔', '부산', '수영구', 120000, '광안리해수욕장'),
    (3, '남포 도시 스테이', '부산', '중구', 145000, '자갈치시장'),
    (4, '기장 오션 리조트', '부산', '기장군', 180000, '해동용궁사')
ON CONFLICT (hotel_id) DO UPDATE SET
    name = EXCLUDED.name,
    city = EXCLUDED.city,
    district = EXCLUDED.district,
    price = EXCLUDED.price,
    near_spot = EXCLUDED.near_spot;

SELECT setval(pg_get_serial_sequence('hotels', 'hotel_id'), MAX(hotel_id))
FROM hotels;
