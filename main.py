import logging
import os
import sys

from weather import get_tomorrow_forecast, is_nice_weather
from notifier import send_notification

def configure_logging():
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )

def main():
    configure_logging()
    log = logging.getLogger(__name__)

    log.info("Weather alert service starting")

    try:
        forecast = get_tomorrow_forecast()
    except Exception as e:
        log.error(f"Failed to fetch forecast: {e}")
        sys.exit(1)

    log.info(
        f"Tomorrow: {forecast['temp_f']:.1f}F, "
        f"rain={forecast['rain_prob']:.0%}, "
        f"sky='{forecast['condition']}'"
    )

    nice, reasons = is_nice_weather(forecast)

    if not nice:
        log.info(f"Weather not nice enough. Reasons: {reasons}")
        sys.exit(0)

    log.info("Nice weather detected!")

    try: 
        send_notification(forecast)
    except Exception as e:
        log.error(f"Failed to send notification: {e}")
        sys.exit(1)

    log.info("Notification sent.")
    sys.exit(0)

if __name__ == "__main__":
    main()