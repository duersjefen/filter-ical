"""populate_group_domain_ids

Revision ID: 9c9fe9735b5a
Revises: 67a59792c235
Create Date: 2025-10-10 16:01:53.782680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c9fe9735b5a'
down_revision: Union[str, None] = '67a59792c235'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Populate domain_id for all groups based on their domain_key.
    This fixes the relationship between groups and domains.
    """
    # Get database connection
    connection = op.get_bind()

    # SQL to update groups.domain_id based on domain_key
    connection.execute(sa.text("""
        UPDATE groups
        SET domain_id = (
            SELECT id
            FROM domains
            WHERE domains.domain_key = groups.domain_key
        )
        WHERE domain_id IS NULL
        AND domain_key IS NOT NULL
    """))

    # After populating, make domain_id NOT NULL (future groups must have it)
    op.alter_column('groups', 'domain_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)


def downgrade() -> None:
    """
    Revert domain_id to nullable and clear values.
    """
    # Make domain_id nullable again
    op.alter_column('groups', 'domain_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)

    # Optionally clear domain_id values (keeps legacy domain_key)
    # connection = op.get_bind()
    # connection.execute(sa.text("UPDATE groups SET domain_id = NULL"))
