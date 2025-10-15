"""add_composite_indexes_for_performance

Revision ID: 3a51e4bcec06
Revises: 1ebb6c1e9f59
Create Date: 2025-10-15 06:42:49.127111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a51e4bcec06'
down_revision: Union[str, None] = '1ebb6c1e9f59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for events by calendar and title
    op.create_index(
        'ix_events_calendar_title',
        'events',
        ['calendar_id', 'title'],
        unique=False
    )

    # Composite index for events by calendar and start time
    op.create_index(
        'ix_events_calendar_start',
        'events',
        ['calendar_id', 'start_time'],
        unique=False
    )

    # Composite index for recurring event groups
    op.create_index(
        'ix_recurring_groups_domain_group',
        'recurring_event_groups',
        ['domain_key', 'group_id'],
        unique=False
    )

    # Composite index for filters
    op.create_index(
        'ix_filters_user_domain',
        'filters',
        ['user_id', 'domain_key'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_events_calendar_title', table_name='events')
    op.drop_index('ix_events_calendar_start', table_name='events')
    op.drop_index('ix_recurring_groups_domain_group', table_name='recurring_event_groups')
    op.drop_index('ix_filters_user_domain', table_name='filters')
