import requests
from flask import current_app


def send_sms(to: str, message: str) -> bool:
    """Send outbound SMS via Africa's Talking API."""
    username = current_app.config.get("AFRICASTALKING_USERNAME")
    api_key = current_app.config.get("AFRICASTALKING_API_KEY")
    if not username or not api_key:
        current_app.logger.warning("SMS credentials not configured; skipping send to %s", to)
        return False

    if len(message) > 160:
        message = message[:157] + "..."

    try:
        data = {
            "username": username,
            "to": to,
            "message": message,
        }
        shortcode = current_app.config.get("AFRICASTALKING_SHORTCODE")
        if shortcode:
            data["from"] = shortcode

        response = requests.post(
            "https://api.africastalking.com/version1/messaging",
            headers={"apiKey": api_key, "Accept": "application/json"},
            data=data,
            timeout=15,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        current_app.logger.error("SMS send failed: %s", exc)
        return False
