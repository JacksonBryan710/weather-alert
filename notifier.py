import os
import logging
import requests

log = logging.getLogger(__name__)

def send_notification(forecast: dict) -> None:
    url = os.environ['NTFY_URL']
    topic = os.environ['NTFY_TOPIC']

    body = (
        f"Nice weather tomorrow ({forecast['date']})! "
        f"High: {forecast['temp_f']:.0f}F, "
        f"Rain chance: {forecast['rain_prob']:.0%}, "
        f"Sky: {forecast['condition'].capitalize()}. "
        f"Get outside!"
    )

    response = requests.post(f"{url}/{topic}", data=body, timeout=10)
    response.raise_for_status()

    log.info(f"Notification sent to {url}/{topic}")

