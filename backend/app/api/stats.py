from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.core.security import require_admin

router = APIRouter()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """Panel de estadísticas para el admin."""
    total = db.query(func.count(Lead.id)).scalar()

    by_status = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )

    by_source = (
        db.query(Lead.source, func.count(Lead.id))
        .group_by(Lead.source)
        .all()
    )

    # Leads de los últimos 7 días por día
    from sqlalchemy import cast, Date, text
    from datetime import datetime, timedelta

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily = (
        db.query(
            cast(Lead.created_at, Date).label("day"),
            func.count(Lead.id).label("count"),
        )
        .filter(Lead.created_at >= seven_days_ago)
        .group_by("day")
        .order_by("day")
        .all()
    )

    conversion_rate = 0.0
    closed = next((c for s, c in by_status if s == LeadStatus.closed), 0)
    if total > 0:
        conversion_rate = round((closed / total) * 100, 1)

    return {
        "total": total,
        "conversion_rate": conversion_rate,
        "by_status": {s.value: c for s, c in by_status},
        "by_source": {s.value: c for s, c in by_source},
        "daily_last_7d": [
            {"day": str(r.day), "count": r.count} for r in daily
        ],
    }
