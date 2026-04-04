from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadUpdate, LeadOut, LeadListOut
from app.core.security import require_admin
from app.core.logging import get_logger
from app.utils.rate_limit import limiter
from app.utils.sanitize import sanitize_lead, looks_like_injection, sanitize_text
from app.services.email_service import send_confirmation_email, send_internal_notification
from app.services.whatsapp_service import send_whatsapp_notification

router = APIRouter()
logger = get_logger(__name__)


@router.post("/leads", response_model=LeadOut, status_code=201)
@limiter.limit("5/minute")
def create_lead(
    request: Request,
    payload: LeadCreate,
    honeypot: Optional[str] = Query(None, alias="website"),
    db: Session = Depends(get_db),
):
    # 1. Honeypot anti-bot
    if honeypot:
        logger.warning("Bot detectado | IP=%s", request.client.host)
        raise HTTPException(status_code=422, detail="Formulario inválido")

    # 2. Detección de inyección
    for field in ["name", "company", "message"]:
        val = getattr(payload, field, "") or ""
        if looks_like_injection(val):
            logger.warning("Posible inyección | IP=%s | field=%s", request.client.host, field)
            raise HTTPException(status_code=400, detail="Datos no válidos")

    # 3. Sanitizar
    clean_data = sanitize_lead(payload.model_dump())

    # 4. Deduplicar
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    if db.query(Lead).filter(Lead.email == payload.email, Lead.created_at >= cutoff).first():
        logger.info("Lead duplicado | email=%s", payload.email)
        raise HTTPException(status_code=409, detail="Ya hemos recibido tu solicitud. Te contactaremos pronto.")

    # 5. Persistir
    lead = Lead(**clean_data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    logger.info("Lead creado | id=%d | email=%s", lead.id, lead.email)

    # 6. Automatizaciones (nunca bloquean la respuesta)
    try:
        send_confirmation_email(lead.name, lead.email, lead.message or "")
        send_internal_notification(lead.name, lead.email, lead.phone or "", lead.company or "", lead.message or "", lead.source.value)
        send_whatsapp_notification(lead.name, lead.phone or "", f"Hola {lead.name}, hemos recibido tu solicitud en NexaroAI. Te contactamos pronto.")
    except Exception as e:
        logger.error("Error automatizaciones | id=%d | %s", lead.id, str(e))

    return lead


@router.get("/leads", response_model=LeadListOut)
@limiter.limit("60/minute")
def list_leads(
    request: Request,
    status: Optional[LeadStatus] = Query(None),
    search: Optional[str] = Query(None, min_length=2, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = db.query(Lead)
    if status:
        q = q.filter(Lead.status == status)
    if search:
        term = f"%{search}%"
        q = q.filter(or_(Lead.name.ilike(term), Lead.email.ilike(term), Lead.company.ilike(term)))
    total = q.count()
    items = q.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/leads/{lead_id}", response_model=LeadOut)
@limiter.limit("60/minute")
def get_lead(request: Request, lead_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadOut)
@limiter.limit("30/minute")
def update_lead(request: Request, lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if payload.status is not None:
        lead.status = payload.status
    if payload.notes is not None:
        lead.notes = sanitize_text(payload.notes, max_length=1000)
    db.commit()
    db.refresh(lead)
    logger.info("Lead actualizado | id=%d | status=%s", lead.id, lead.status)
    return lead
