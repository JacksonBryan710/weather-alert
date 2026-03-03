import os
import logging
import requests
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

CLEAR_CONDITION_IDS = {800, 801}

def get_tomorrow_forecast() -> dict:
    api_key = os.environ["OPENWEATHER_API_KEY"]
    city = os.environ.get("CITY_NAME", "NYC,US")

    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",
        "cnt": 16,
    }

    response = requests.get(OWM_BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    return _parse_tomorrow_daytime(response.json())

def _parse_tomorrow_daytime(data: dict) -> dict:
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
    daytime_slots = []

    for item in data.get("list", []):
        slot_dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        if slot_dt.date() == tomorrow and 10 <= slot_dt.hour <= 16:
            daytime_slots.append(item)

    if not daytime_slots:
        raise ValueError(f'No daytime forecast slots found for {tomorrow}')
    
    max_rain_prob = max(slot.get("pop", 0) for slot in daytime_slots)
    min_temp_f = min(slot["main"]["temp"] for slot in daytime_slots)
    mid_slot = daytime_slots[len(daytime_slots) // 2]
    condition_id = mid_slot["weather"][0]["id"]
    condition_desc = mid_slot["weather"][0]["description"]

    return {
        "temp_f": min_temp_f,
        "rain_prob": max_rain_prob,
        "condition": condition_desc,
        "condition_id": condition_id,
        "date": str(tomorrow),
    }


def is_nice_weather(forecast: dict) -> tuple[bool, list[str]]:
    temp_threshold = float(os.environ.get("TEMP_THRESHOLD_F", 65))
    rain_max = float(os.environ.get("RAIN_PROBABILITY_MAX", 0.20))

    failures = []

    if forecast["temp_f"] < temp_threshold:
        failures.append(f"Too cold: {forecast['temp_f']:.1f}F < {temp_threshold}F")

    if forecast["rain_prob"] > rain_max:
        failures.append(f"Too rainy: {forecast['rain_prob']:.0%} > {rain_max:.0%}")

    if forecast["condition_id"] not in CLEAR_CONDITION_IDS:
        failures.append(f"Not clear: '{forecast['condition']}' (id={forecast['condition_id']})")

    return (len(failures) == 0, failures)