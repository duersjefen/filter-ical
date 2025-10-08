"""create_domains_table_and_add_domain_id_fks

Revision ID: 9a8a8689fab6
Revises: 8d2c8836f283
Create Date: 2025-10-08 16:51:18.743158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a8a8689fab6'
down_revision: Union[str, None] = '8d2c8836f283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create domains table
    op.create_table(
        'domains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('calendar_url', sa.Text(), nullable=False),
        sa.Column('calendar_id', sa.Integer(), nullable=True),
        sa.Column('admin_password_hash', sa.String(length=255), nullable=True),
        sa.Column('user_password_hash', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain_key'),
        sa.UniqueConstraint('calendar_id')
    )
    op.create_index('ix_domains_id', 'domains', ['id'])
    op.create_index('ix_domains_domain_key', 'domains', ['domain_key'])
    op.create_index('ix_domains_calendar_id', 'domains', ['calendar_id'])

    # Add domain_id column to groups table
    op.add_column('groups', sa.Column('domain_id', sa.Integer(), nullable=True))
    op.create_index('ix_groups_domain_id', 'groups', ['domain_id'])
    op.create_foreign_key('fk_groups_domain_id', 'groups', 'domains', ['domain_id'], ['id'], ondelete='CASCADE')

    # Make domain_key nullable in groups
    op.alter_column('groups', 'domain_key', nullable=True)

    # Add domain_id column to recurring_event_groups table
    op.add_column('recurring_event_groups', sa.Column('domain_id', sa.Integer(), nullable=True))
    op.create_index('ix_recurring_event_groups_domain_id', 'recurring_event_groups', ['domain_id'])
    op.create_foreign_key('fk_recurring_event_groups_domain_id', 'recurring_event_groups', 'domains', ['domain_id'], ['id'], ondelete='CASCADE')

    # Make domain_key nullable in recurring_event_groups
    op.alter_column('recurring_event_groups', 'domain_key', nullable=True)

    # Add domain_id column to assignment_rules table
    op.add_column('assignment_rules', sa.Column('domain_id', sa.Integer(), nullable=True))
    op.create_index('ix_assignment_rules_domain_id', 'assignment_rules', ['domain_id'])
    op.create_foreign_key('fk_assignment_rules_domain_id', 'assignment_rules', 'domains', ['domain_id'], ['id'], ondelete='CASCADE')

    # Make domain_key nullable in assignment_rules
    op.alter_column('assignment_rules', 'domain_key', nullable=True)

    # Add domain_id column to filters table
    op.add_column('filters', sa.Column('domain_id', sa.Integer(), nullable=True))
    op.create_index('ix_filters_domain_id', 'filters', ['domain_id'])
    op.create_foreign_key('fk_filters_domain_id', 'filters', 'domains', ['domain_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Remove domain_id foreign keys and columns
    op.drop_constraint('fk_filters_domain_id', 'filters', type_='foreignkey')
    op.drop_index('ix_filters_domain_id', 'filters')
    op.drop_column('filters', 'domain_id')

    op.alter_column('assignment_rules', 'domain_key', nullable=False)
    op.drop_constraint('fk_assignment_rules_domain_id', 'assignment_rules', type_='foreignkey')
    op.drop_index('ix_assignment_rules_domain_id', 'assignment_rules')
    op.drop_column('assignment_rules', 'domain_id')

    op.alter_column('recurring_event_groups', 'domain_key', nullable=False)
    op.drop_constraint('fk_recurring_event_groups_domain_id', 'recurring_event_groups', type_='foreignkey')
    op.drop_index('ix_recurring_event_groups_domain_id', 'recurring_event_groups')
    op.drop_column('recurring_event_groups', 'domain_id')

    op.alter_column('groups', 'domain_key', nullable=False)
    op.drop_constraint('fk_groups_domain_id', 'groups', type_='foreignkey')
    op.drop_index('ix_groups_domain_id', 'groups')
    op.drop_column('groups', 'domain_id')

    # Drop domains table
    op.drop_index('ix_domains_calendar_id', 'domains')
    op.drop_index('ix_domains_domain_key', 'domains')
    op.drop_index('ix_domains_id', 'domains')
    op.drop_table('domains')
