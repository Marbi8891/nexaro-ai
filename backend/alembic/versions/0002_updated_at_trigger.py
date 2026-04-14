"""add updated_at trigger for leads

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-02 00:00:00
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Función que actualiza updated_at automáticamente en cualquier UPDATE
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER leads_updated_at
        BEFORE UPDATE ON leads
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS leads_updated_at ON leads;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
