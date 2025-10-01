"""add_domain_backups_table

Revision ID: ed716677d1fb
Revises: ad420dcd7f39
Create Date: 2025-10-01 09:02:28.903867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed716677d1fb'
down_revision: Union[str, None] = 'ad420dcd7f39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create domain_backups table for configuration snapshot system."""
    op.create_table(
        'domain_backups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_key', sa.String(length=100), nullable=False),
        sa.Column('config_snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('backup_type', sa.String(length=50), server_default='manual', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient querying
    op.create_index('ix_domain_backups_id', 'domain_backups', ['id'], unique=False)
    op.create_index('ix_domain_backups_domain_key', 'domain_backups', ['domain_key'], unique=False)
    op.create_index('ix_domain_backups_created_at', 'domain_backups', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop domain_backups table."""
    op.drop_index('ix_domain_backups_created_at', table_name='domain_backups')
    op.drop_index('ix_domain_backups_domain_key', table_name='domain_backups')
    op.drop_index('ix_domain_backups_id', table_name='domain_backups')
    op.drop_table('domain_backups')
