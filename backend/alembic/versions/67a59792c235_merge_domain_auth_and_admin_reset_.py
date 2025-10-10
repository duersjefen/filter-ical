"""merge domain_auth and admin_reset_tokens migrations

Revision ID: 67a59792c235
Revises: 893472e90cd9, c5d6e7f8g9h0
Create Date: 2025-10-10 15:19:55.421063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67a59792c235'
down_revision: Union[str, None] = ('893472e90cd9', 'c5d6e7f8g9h0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
