"""create leads table

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(200), nullable=False, index=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("company", sa.String(150), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "source",
            sa.Enum("web", "instagram", "google", "referral", "whatsapp", "other", name="leadsource"),
            nullable=False,
            server_default="web",
        ),
        sa.Column(
            "status",
            sa.Enum("new", "contacted", "qualified", "closed", "lost", name="leadstatus"),
            nullable=False,
            server_default="new",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("leads")
    op.execute("DROP TYPE IF EXISTS leadstatus")
    op.execute("DROP TYPE IF EXISTS leadsource")
