import requests
from django.conf import settings

YCLOUD_BASE_URL = "https://api.ycloud.com/v2"


def _headers():
    return {
        "Content-Type": "application/json",
        "X-API-Key": settings.YCLOUD_API_KEY,
    }


def send_whatsapp_text(to: str, message: str) -> dict:
    """Envía mensaje de texto libre (dentro de ventana 24h)."""
    payload = {
        "from": settings.YCLOUD_WHATSAPP_NUMBER,
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(
        f"{YCLOUD_BASE_URL}/whatsapp/messages/sendDirectly",
        headers=_headers(),
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()