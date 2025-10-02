"""Add app_settings table for global configuration

Revision ID: 0u62nu8zsa7m
Revises: 5204516d67aa
Create Date: 2025-10-02 19:50:38

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0u62nu8zsa7m'
down_revision: Union[str, None] = '5204516d67aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create app_settings table
    op.create_table('app_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('footer_visibility', sa.String(), nullable=False, server_default='everywhere'),
    sa.Column('show_domain_request', sa.Boolean(), nullable=False, server_default='true'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_app_settings_id'), 'app_settings', ['id'], unique=False)

    # Insert default settings row
    op.execute("""
        INSERT INTO app_settings (id, footer_visibility, show_domain_request)
        VALUES (1, 'everywhere', true)
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_app_settings_id'), table_name='app_settings')
    op.drop_table('app_settings')
