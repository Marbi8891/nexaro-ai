"""
Google Calendar Service — NexaroAI
====================================
Placeholder para agendar reuniones automáticamente.
Conecta con google-api-python-client cuando estés listo.

Pasos para activar:
  1. Crea un proyecto en Google Cloud Console
  2. Activa Calendar API
  3. Descarga credentials.json
  4. pip install google-api-python-client google-auth-oauthlib
"""
import logging

logger = logging.getLogger(__name__)


def schedule_intro_call(name: str, email: str, phone: str) -> dict | None:
    """
    Agenda llamada introductoria con el lead.
    Retorna evento creado o None si falla.
    """
    logger.info(
        "[CALENDAR MOCK] Agendar llamada con %s <%s> | Tel: %s",
        name,
        email,
        phone or "—",
    )

    # ── Google Calendar (descomentar para activar) ─────────────────
    # from googleapiclient.discovery import build
    # from google.oauth2.service_account import Credentials
    # creds = Credentials.from_service_account_file("credentials.json",
    #     scopes=["https://www.googleapis.com/auth/calendar"])
    # service = build("calendar", "v3", credentials=creds)
    # event = service.events().insert(calendarId="primary", body={...}).execute()
    # return event
    # ───────────────────────────────────────────────────────────────

    return {"mock": True, "lead": name, "status": "pending_schedule"}
