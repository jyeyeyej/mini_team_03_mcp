"""시간 선택, 정규화, 비교 로직의 단위 테스트입니다."""

import sys
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import httpx

MCP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MCP_ROOT))

from client.kma_client import (  # noqa: E402
    _latest_hourly_base,
    _latest_mid_base,
    _latest_short_base,
)
from client.connection import get_json  # noqa: E402
from core.weather.comparator import compare_daily  # noqa: E402
from core.weather.locations import get_location  # noqa: E402
from core.weather.mappings import kma_condition, wmo_condition  # noqa: E402
from core.weather.normalizer import (  # noqa: E402
    normalize_kma_mid_daily,
    normalize_kma_short_daily,
)
from core.weather.schemas import DailyForecast  # noqa: E402


KST = ZoneInfo("Asia/Seoul")


class BaseTimeTests(unittest.TestCase):
    def test_hourly_base_uses_publication_buffer(self):
        now = datetime(2026, 8, 28, 9, 20, tzinfo=KST)
        self.assertEqual(_latest_hourly_base(now).strftime("%Y%m%d%H%M"), "202608280800")

    def test_short_base_crosses_midnight(self):
        now = datetime(2026, 8, 28, 0, 10, tzinfo=KST)
        self.assertEqual(_latest_short_base(now).strftime("%Y%m%d%H%M"), "202608272300")

    def test_mid_base_crosses_midnight(self):
        now = datetime(2026, 8, 28, 5, 30, tzinfo=KST)
        self.assertEqual(_latest_mid_base(now).strftime("%Y%m%d%H%M"), "202608271800")


class MappingTests(unittest.TestCase):
    def test_precipitation_overrides_sky(self):
        self.assertEqual(kma_condition("1", "1"), ("비", "rain"))

    def test_wmo_mapping(self):
        self.assertEqual(wmo_condition(3), ("흐림", "cloudy"))

    def test_city_coordinates(self):
        self.assertEqual((get_location("부산").nx, get_location("부산").ny), (98, 76))


class NormalizationTests(unittest.TestCase):
    def test_short_forecast_aggregates_daily_values(self):
        items = [
            {"fcstDate": "20260829", "category": "TMP", "fcstValue": "24"},
            {"fcstDate": "20260829", "category": "TMP", "fcstValue": "30"},
            {"fcstDate": "20260829", "category": "POP", "fcstValue": "20"},
            {"fcstDate": "20260829", "category": "POP", "fcstValue": "60"},
            {"fcstDate": "20260829", "category": "SKY", "fcstValue": "3"},
            {"fcstDate": "20260829", "category": "PTY", "fcstValue": "0"},
        ]
        result = normalize_kma_short_daily(items, date(2026, 8, 29), 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].min_temperature_c, 24)
        self.assertEqual(result[0].max_temperature_c, 30)
        self.assertEqual(result[0].precipitation_probability_pct, 60)
        self.assertEqual(result[0].condition_code, "partly_cloudy")

    def test_mid_forecast_maps_offset_to_date(self):
        base = datetime(2026, 8, 28, 6, tzinfo=KST)
        land = {
            "wf4Am": "구름많음",
            "wf4Pm": "흐리고 비",
            "rnSt4Am": 30,
            "rnSt4Pm": 70,
        }
        temperature = {"taMin4": 22, "taMax4": 29}
        result = normalize_kma_mid_daily(
            land,
            temperature,
            base,
            date(2026, 9, 1),
            1,
        )
        self.assertEqual(result[0].forecast_date, date(2026, 9, 1))
        self.assertEqual(result[0].precipitation_probability_pct, 70)
        self.assertEqual(result[0].condition_code, "rain")

    def test_daily_difference_is_signed(self):
        left = DailyForecast(
            "open_meteo", date(2026, 8, 29), "daily", "daily",
            24, 31, 40, "비", "rain",
        )
        right = DailyForecast(
            "kma", date(2026, 8, 29), "short_term", "hourly_to_daily",
            23, 30, 60, "비", "rain",
        )
        difference = compare_daily(left, right)
        self.assertEqual(difference["min_temperature_c"], 1)
        self.assertEqual(difference["precipitation_probability_pct"], -20)
        self.assertTrue(difference["condition_match"])


class SecurityTests(unittest.TestCase):
    def test_http_error_does_not_expose_service_key(self):
        secret = "do-not-leak-this-key"
        request = httpx.Request(
            "GET",
            "https://example.test/weather",
            params={"serviceKey": secret},
        )
        response = httpx.Response(403, request=request)
        error = httpx.HTTPStatusError("forbidden", request=request, response=response)
        mocked_client = MagicMock()
        mocked_client.__enter__.return_value.get.side_effect = error
        with patch("client.connection.httpx.Client", return_value=mocked_client):
            with self.assertRaises(RuntimeError) as caught:
                get_json("kma", "https://example.test/weather", {"serviceKey": secret})
        self.assertNotIn(secret, str(caught.exception))
        self.assertIn("HTTP 403", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
