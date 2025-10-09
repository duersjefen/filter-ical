"""Drop deprecated domain_auth table

Revision ID: 893472e90cd9
Revises: b4c9e444b42e
Create Date: 2025-10-09 14:17:24.944161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '893472e90cd9'
down_revision: Union[str, None] = 'b4c9e444b42e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop the deprecated domain_auth table.

    Auth fields have been migrated to the unified domains table.
    All services now use the Domain model directly.
    """
    op.drop_table('domain_auth')


def downgrade() -> None:
    """
    Recreate domain_auth table for rollback purposes.

    Note: This only recreates the structure. Data migration from
    domains table back to domain_auth would need to be handled separately.
    """
    op.create_table(
        'domain_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_key', sa.String(length=100), nullable=False),
        sa.Column('calendar_id', sa.Integer(), nullable=True),
        sa.Column('admin_password_hash', sa.String(length=255), nullable=True),
        sa.Column('user_password_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain_key'),
        sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], ondelete='CASCADE')
    )
    op.create_index('ix_domain_auth_domain_key', 'domain_auth', ['domain_key'])
