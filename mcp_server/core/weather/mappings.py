"""Open-Meteo와 기상청 날씨 코드를 공통 상태로 변환합니다."""

from collections import Counter
from typing import Iterable


WMO_CONDITIONS = {
    0: ("맑음", "clear"),
    1: ("대체로 맑음", "clear"),
    2: ("부분적으로 흐림", "partly_cloudy"),
    3: ("흐림", "cloudy"),
    45: ("안개", "fog"),
    48: ("서리 안개", "fog"),
    51: ("약한 이슬비", "drizzle"),
    53: ("이슬비", "drizzle"),
    55: ("강한 이슬비", "drizzle"),
    56: ("약한 어는 이슬비", "drizzle"),
    57: ("강한 어는 이슬비", "drizzle"),
    61: ("약한 비", "rain"),
    63: ("비", "rain"),
    65: ("강한 비", "rain"),
    66: ("약한 어는 비", "rain"),
    67: ("강한 어는 비", "rain"),
    71: ("약한 눈", "snow"),
    73: ("눈", "snow"),
    75: ("강한 눈", "snow"),
    77: ("싸락눈", "snow"),
    80: ("약한 소나기", "shower"),
    81: ("소나기", "shower"),
    82: ("강한 소나기", "shower"),
    85: ("약한 눈보라", "snow"),
    86: ("강한 눈보라", "snow"),
    95: ("뇌우", "thunderstorm"),
    96: ("약한 우박을 동반한 뇌우", "thunderstorm"),
    99: ("강한 우박을 동반한 뇌우", "thunderstorm"),
}

KMA_SKY = {
    "1": ("맑음", "clear"),
    "3": ("구름많음", "partly_cloudy"),
    "4": ("흐림", "cloudy"),
}

KMA_PTY = {
    "0": (None, None),
    "1": ("비", "rain"),
    "2": ("비/눈", "sleet"),
    "3": ("눈", "snow"),
    "4": ("소나기", "shower"),
    "5": ("빗방울", "drizzle"),
    "6": ("빗방울/눈날림", "sleet"),
    "7": ("눈날림", "snow"),
}

KMA_TEXT_CONDITIONS = {
    "맑음": "clear",
    "구름많음": "partly_cloudy",
    "구름많고 비": "rain",
    "구름많고 눈": "snow",
    "구름많고 비/눈": "sleet",
    "구름많고 소나기": "shower",
    "흐림": "cloudy",
    "흐리고 비": "rain",
    "흐리고 눈": "snow",
    "흐리고 비/눈": "sleet",
    "흐리고 소나기": "shower",
}


def wmo_condition(code: int | str | None) -> tuple[str | None, str | None]:
    if code is None:
        return None, None
    return WMO_CONDITIONS.get(int(code), (f"알 수 없음({code})", "unknown"))


def kma_condition(
    sky: str | int | None,
    pty: str | int | None,
) -> tuple[str | None, str | None]:
    if pty is not None:
        precipitation = KMA_PTY.get(str(pty), (None, None))
        if precipitation[0] is not None:
            return precipitation
    if sky is None:
        return None, None
    return KMA_SKY.get(str(sky), (f"알 수 없음({sky})", "unknown"))


def kma_text_condition(text: str | None) -> tuple[str | None, str | None]:
    if not text:
        return None, None
    return text, KMA_TEXT_CONDITIONS.get(text, "unknown")


def representative_value(values: Iterable[str | None]) -> str | None:
    filtered = [value for value in values if value]
    if not filtered:
        return None
    return Counter(filtered).most_common(1)[0][0]
