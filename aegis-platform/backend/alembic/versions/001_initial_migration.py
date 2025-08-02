"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-07-09 02:22:48.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This will be auto-generated when you run alembic revision --autogenerate
    # For now, we'll let SQLAlchemy create the tables directly
    pass


def downgrade() -> None:
    # Drop all tables in reverse order
    pass