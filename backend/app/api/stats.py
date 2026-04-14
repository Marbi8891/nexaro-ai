from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.core.security import require_admin
from app.utils.rate_limit import limiter
from app.core.config import settings

router = APIRouter()


def _is_sqlite(db: Session) -> bool:
    return db.bind.dialect.name == "sqlite"


@router.get("/stats")
@limiter.limit("60/minute")
def get_stats(
    request: Request,
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

    # Leads últimos 7 días — query compatible con SQLite y PostgreSQL
    seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)

    if _is_sqlite(db):
        # SQLite: usar strftime para truncar a fecha
        daily = (
            db.query(
                func.strftime("%Y-%m-%d", Lead.created_at).label("day"),
                func.count(Lead.id).label("count"),
            )
            .filter(Lead.created_at >= seven_days_ago)
            .group_by(text("day"))
            .order_by(text("day"))
            .all()
        )
    else:
        # PostgreSQL: usar DATE_TRUNC para truncar a día
        from sqlalchemy import cast, Date
        daily = (
            db.query(
                cast(Lead.created_at, Date).label("day"),
                func.count(Lead.id).label("count"),
            )
            .filter(Lead.created_at >= seven_days_ago)
            .group_by(text("day"))
            .order_by(text("day"))
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
