import re
import html


# Caracteres no permitidos en campos de texto libre
_DANGEROUS = re.compile(r"[<>{}\[\]\\;]")
# Detecta patrones de inyección SQL básicos
_SQL_PATTERNS = re.compile(
    r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(|xp_cmdshell)",
    re.IGNORECASE,
)


def sanitize_text(value: str, max_length: int = 500) -> str:
    """Limpia texto libre: escapa HTML, elimina chars peligrosos, trunca."""
    if not value:
        return value
    value = value.strip()[:max_length]
    value = html.escape(value)
    value = _DANGEROUS.sub("", value)
    return value


def looks_like_injection(value: str) -> bool:
    """Detecta posibles intentos de inyección SQL."""
    return bool(_SQL_PATTERNS.search(value or ""))


def sanitize_lead(data: dict) -> dict:
    """Aplica sanitización a todos los campos de texto de un lead."""
    text_fields = ["name", "company", "message", "notes"]
    sanitized = dict(data)
    for field in text_fields:
        if field in sanitized and sanitized[field]:
            sanitized[field] = sanitize_text(str(sanitized[field]))
    return sanitized
