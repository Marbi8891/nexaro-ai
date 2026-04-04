import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


CONFIRMATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8" /></head>
<body style="font-family:sans-serif;background:#f4f4f4;padding:32px">
  <div style="max-width:560px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08)">
    <div style="background:#080B12;padding:28px 32px">
      <h1 style="color:#00E5FF;margin:0;font-size:22px">NexaroAI Agency</h1>
      <p style="color:#6B7A99;margin:4px 0 0;font-size:13px">nexaroai.agency</p>
    </div>
    <div style="padding:32px">
      <h2 style="color:#111827;font-size:20px;margin-top:0">¡Solicitud recibida, {name}!</h2>
      <p style="color:#4B5563;line-height:1.7">
        Hemos recibido tu solicitud correctamente.<br/>
        Uno de nuestros especialistas revisará tu caso y te contactará en
        <strong>menos de 24 horas</strong>.
      </p>
      <div style="background:#F9FAFB;border-radius:8px;padding:18px;margin:24px 0">
        <p style="margin:0;color:#6B7A99;font-size:13px;text-transform:uppercase;letter-spacing:.05em">Tu solicitud</p>
        <p style="margin:8px 0 0;color:#111827;font-weight:600">{message_preview}</p>
      </div>
      <p style="color:#4B5563;line-height:1.7">
        Mientras tanto, si tienes alguna duda urgente puedes escribirnos a
        <a href="mailto:hola@nexaroai.agency" style="color:#00E5FF">hola@nexaroai.agency</a>
        o por WhatsApp.
      </p>
      <a href="https://nexaroai.agency" style="display:inline-block;background:#00E5FF;color:#080B12;padding:14px 28px;border-radius:8px;font-weight:700;text-decoration:none;margin-top:8px">
        Volver a la web →
      </a>
    </div>
    <div style="padding:20px 32px;border-top:1px solid #F3F4F6">
      <p style="color:#9CA3AF;font-size:12px;margin:0">
        © 2025 NexaroAI Agency · nexaroai.agency<br/>
        Este email fue enviado porque rellenaste el formulario de contacto.
      </p>
    </div>
  </div>
</body>
</html>
"""

INTERNAL_TEMPLATE = """
<b>Nuevo lead en NexaroAI</b><br/><br/>
<b>Nombre:</b> {name}<br/>
<b>Email:</b> {email}<br/>
<b>Teléfono:</b> {phone}<br/>
<b>Empresa:</b> {company}<br/>
<b>Mensaje:</b> {message}<br/>
<b>Fuente:</b> {source}<br/>
"""


def _send_smtp(to: str, subject: str, html_body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to, msg.as_string())
    return True


def send_confirmation_email(name: str, email: str, message: str) -> bool:
    subject = "Hemos recibido tu solicitud — NexaroAI"
    html = CONFIRMATION_TEMPLATE.format(
        name=name,
        message_preview=message[:120] + "..." if len(message) > 120 else message or "Sin mensaje",
    )

    if settings.EMAIL_MOCK:
        logger.info(
            "[EMAIL MOCK] Confirmación enviada a %s | Subject: %s",
            email,
            subject,
        )
        return True

    try:
        return _send_smtp(email, subject, html)
    except Exception as e:
        logger.error("[EMAIL ERROR] No se pudo enviar a %s: %s", email, str(e))
        return False


def send_internal_notification(name: str, email: str, phone: str, company: str, message: str, source: str) -> bool:
    """Notifica al equipo interno de NexaroAI sobre el nuevo lead."""
    subject = f"🔥 Nuevo lead: {name} ({company or 'sin empresa'})"
    html = INTERNAL_TEMPLATE.format(
        name=name, email=email, phone=phone or "—",
        company=company or "—", message=message or "—", source=source,
    )

    if settings.EMAIL_MOCK:
        logger.info("[EMAIL MOCK] Notificación interna | Lead: %s <%s>", name, email)
        return True

    try:
        return _send_smtp(settings.EMAIL_FROM, subject, html)
    except Exception as e:
        logger.error("[EMAIL ERROR] Notificación interna fallida: %s", str(e))
        return False
