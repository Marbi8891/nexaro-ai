from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as PgEnum
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    closed = "closed"
    lost = "lost"


class LeadSource(str, enum.Enum):
    web = "web"
    instagram = "instagram"
    google = "google"
    referral = "referral"
    whatsapp = "whatsapp"
    other = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    company = Column(String(150), nullable=True)
    message = Column(Text, nullable=True)
    source = Column(
        PgEnum(LeadSource, name="leadsource"),
        default=LeadSource.web,
        nullable=False,
    )
    status = Column(
        PgEnum(LeadStatus, name="leadstatus"),
        default=LeadStatus.new,
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
