"""
WhatsApp Service — NexaroAI
===========================
Placeholder listo para conectar con:
  - Twilio WhatsApp API
  - WhatsApp Business API (Meta)
  - Wassenger / ChatAPI

Para activar, instala twilio y configura las variables en .env:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM
"""
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_whatsapp_notification(name: str, phone: str, message: str) -> bool:
    """
    Envía notificación WhatsApp al lead.
    Actualmente en modo mock — conecta un proveedor real para activar.
    """
    if not phone:
        logger.info("[WA MOCK] Sin teléfono, omitiendo WhatsApp para %s", name)
        return False

    logger.info(
        "[WA MOCK] Mensaje WA → %s (%s): '%s'",
        name,
        phone,
        message[:80],
    )

    # ── Twilio (descomentar para activar) ──────────────────────────
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(
    #     from_=f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}",
    #     to=f"whatsapp:{phone}",
    #     body=message,
    # )
    # ───────────────────────────────────────────────────────────────

    return True
