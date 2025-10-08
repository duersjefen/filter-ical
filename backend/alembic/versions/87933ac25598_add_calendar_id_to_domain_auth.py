"""add_calendar_id_to_domain_auth

Revision ID: 87933ac25598
Revises: a1b2c3d4e5f6
Create Date: 2025-10-08 11:43:13.952940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87933ac25598'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add calendar_id column to domain_auth and link existing domain calendars."""
    from sqlalchemy import text

    # Add calendar_id column to domain_auth
    op.add_column('domain_auth', sa.Column('calendar_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_domain_auth_calendar_id', 'domain_auth', 'calendars', ['calendar_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_domain_auth_calendar_id', 'domain_auth', ['calendar_id'])

    # Link existing domain calendars to domain_auth entries
    # For any domain calendar without a domain_auth entry, create one
    connection = op.get_bind()

    # Get all domain calendars
    result = connection.execute(text("""
        SELECT c.id, c.name
        FROM calendars c
        WHERE c.type = 'domain'
        AND NOT EXISTS (
            SELECT 1 FROM domain_auth da WHERE da.calendar_id = c.id
        )
    """))

    orphan_calendars = result.fetchall()

    # For each orphaned domain calendar, create domain_auth entry
    # We'll derive domain_key from calendar name (lowercase, replace spaces with hyphens)
    for calendar_id, calendar_name in orphan_calendars:
        # Derive domain_key from name: "Exter Kalendar" -> "exter"
        domain_key = calendar_name.lower().split()[0] if calendar_name else f"domain_{calendar_id}"

        connection.execute(text("""
            INSERT INTO domain_auth (domain_key, calendar_id, created_at, updated_at)
            VALUES (:domain_key, :calendar_id, NOW(), NOW())
        """), {"domain_key": domain_key, "calendar_id": calendar_id})

    # Now make calendar_id NOT NULL
    op.alter_column('domain_auth', 'calendar_id', nullable=False)

    # Make it unique (one domain_auth per calendar)
    op.create_unique_constraint('uq_domain_auth_calendar_id', 'domain_auth', ['calendar_id'])


def downgrade() -> None:
    """Remove calendar_id from domain_auth."""
    op.drop_constraint('uq_domain_auth_calendar_id', 'domain_auth', type_='unique')
    op.drop_index('ix_domain_auth_calendar_id', 'domain_auth')
    op.drop_constraint('fk_domain_auth_calendar_id', 'domain_auth', type_='foreignkey')
    op.drop_column('domain_auth', 'calendar_id')
