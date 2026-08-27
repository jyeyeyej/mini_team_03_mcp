BEGIN;

CREATE TABLE IF NOT EXISTS weather_locations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Seoul',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_weather_locations_city UNIQUE (city_name),
    CONSTRAINT ck_weather_locations_latitude
        CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_weather_locations_longitude
        CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE IF NOT EXISTS weather_current (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_id BIGINT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    temperature_c DOUBLE PRECISION NOT NULL,
    apparent_temperature_c DOUBLE PRECISION,
    humidity_pct SMALLINT,
    precipitation_mm DOUBLE PRECISION,
    weather_code SMALLINT NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'open-meteo',
    raw_payload JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weather_current_location
        FOREIGN KEY (location_id)
        REFERENCES weather_locations(id)
        ON DELETE RESTRICT,
    CONSTRAINT uq_weather_current_observation
        UNIQUE (location_id, observed_at),
    CONSTRAINT ck_weather_current_humidity
        CHECK (humidity_pct IS NULL OR humidity_pct BETWEEN 0 AND 100),
    CONSTRAINT ck_weather_current_precipitation
        CHECK (precipitation_mm IS NULL OR precipitation_mm >= 0)
);

CREATE TABLE IF NOT EXISTS weather_forecast (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_id BIGINT NOT NULL,
    forecast_date DATE NOT NULL,
    min_temperature_c DOUBLE PRECISION NOT NULL,
    max_temperature_c DOUBLE PRECISION NOT NULL,
    precipitation_probability_pct SMALLINT,
    weather_code SMALLINT NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'open-meteo',
    raw_payload JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weather_forecast_location
        FOREIGN KEY (location_id)
        REFERENCES weather_locations(id)
        ON DELETE RESTRICT,
    CONSTRAINT uq_weather_forecast_date
        UNIQUE (location_id, forecast_date),
    CONSTRAINT ck_weather_forecast_temperature
        CHECK (min_temperature_c <= max_temperature_c),
    CONSTRAINT ck_weather_forecast_probability
        CHECK (
            precipitation_probability_pct IS NULL
            OR precipitation_probability_pct BETWEEN 0 AND 100
        )
);

CREATE INDEX IF NOT EXISTS idx_weather_current_latest
    ON weather_current (location_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_weather_forecast_date
    ON weather_forecast (location_id, forecast_date);

CREATE INDEX IF NOT EXISTS idx_weather_current_fetched
    ON weather_current (fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_weather_forecast_fetched
    ON weather_forecast (fetched_at DESC);

COMMIT;
