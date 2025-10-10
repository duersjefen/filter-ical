"""store_admin_password_in_database

Revision ID: cc5b28851942
Revises: 9c9fe9735b5a
Create Date: 2025-10-10 16:48:30.110075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5b28851942'
down_revision: Union[str, None] = '9c9fe9735b5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create admin_settings table for database-stored admin password.
    This removes the need to update .env after password resets.

    Password will be seeded from ADMIN_PASSWORD env var on first login
    if the table is empty.
    """
    # Create admin_settings table (initially empty)
    op.create_table(
        'admin_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Remove admin_settings table and revert to .env password."""
    op.drop_table('admin_settings')
