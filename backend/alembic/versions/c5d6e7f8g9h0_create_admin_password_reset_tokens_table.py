"""create_admin_password_reset_tokens_table

Revision ID: c5d6e7f8g9h0
Revises: b4c9e444b42e
Create Date: 2025-10-10 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8g9h0'
down_revision: Union[str, None] = 'b4c9e444b42e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create admin_password_reset_tokens table."""
    op.create_table(
        'admin_password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('token', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('used', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False)
    )


def downgrade() -> None:
    """Drop admin_password_reset_tokens table."""
    op.drop_table('admin_password_reset_tokens')
