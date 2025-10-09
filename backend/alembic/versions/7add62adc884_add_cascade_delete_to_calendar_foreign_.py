"""Add CASCADE delete to calendar foreign keys

Revision ID: 7add62adc884
Revises: 21630ea43773
Create Date: 2025-10-09 09:36:07.517041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7add62adc884'
down_revision: Union[str, None] = '21630ea43773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('events_calendar_id_fkey', 'events', type_='foreignkey')
    op.drop_constraint('filters_calendar_id_fkey', 'filters', type_='foreignkey')

    # Recreate with CASCADE delete
    op.create_foreign_key(
        'events_calendar_id_fkey',
        'events', 'calendars',
        ['calendar_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'filters_calendar_id_fkey',
        'filters', 'calendars',
        ['calendar_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop CASCADE constraints
    op.drop_constraint('events_calendar_id_fkey', 'events', type_='foreignkey')
    op.drop_constraint('filters_calendar_id_fkey', 'filters', type_='foreignkey')

    # Recreate without CASCADE
    op.create_foreign_key(
        'events_calendar_id_fkey',
        'events', 'calendars',
        ['calendar_id'], ['id']
    )
    op.create_foreign_key(
        'filters_calendar_id_fkey',
        'filters', 'calendars',
        ['calendar_id'], ['id']
    )
