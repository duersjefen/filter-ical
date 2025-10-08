"""migrate_data_to_domains_table

Revision ID: 21630ea43773
Revises: 9a8a8689fab6
Create Date: 2025-10-08 16:51:56.903119

"""
from typing import Sequence, Union
from pathlib import Path
import yaml

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '21630ea43773'
down_revision: Union[str, None] = '9a8a8689fab6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate data from domains.yaml and domain_auth table to new domains table."""

    # Create table references for raw SQL operations
    domains = table('domains',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('name', sa.String),
        column('calendar_url', sa.Text),
        column('calendar_id', sa.Integer),
        column('admin_password_hash', sa.String),
        column('user_password_hash', sa.String),
        column('status', sa.String)
    )

    domain_auth = table('domain_auth',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('calendar_id', sa.Integer),
        column('admin_password_hash', sa.String),
        column('user_password_hash', sa.String)
    )

    groups = table('groups',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('domain_id', sa.Integer)
    )

    recurring_event_groups = table('recurring_event_groups',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('domain_id', sa.Integer)
    )

    assignment_rules = table('assignment_rules',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('domain_id', sa.Integer)
    )

    filters = table('filters',
        column('id', sa.Integer),
        column('domain_key', sa.String),
        column('domain_id', sa.Integer)
    )

    # Get database connection
    conn = op.get_bind()

    # 1. Load and migrate domains from YAML file
    domains_yaml_path = Path(__file__).parent.parent.parent / 'domains' / 'domains.yaml'

    if domains_yaml_path.exists():
        with open(domains_yaml_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        if yaml_config and 'domains' in yaml_config:
            for domain_key, config in yaml_config['domains'].items():
                # Insert domain from YAML
                conn.execute(
                    domains.insert().values(
                        domain_key=domain_key,
                        name=config.get('name', domain_key),
                        calendar_url=config.get('calendar_url', ''),
                        status='active'
                    )
                )

                # Get the domain_id we just inserted
                domain_result = conn.execute(
                    sa.select(domains).where(domains.c.domain_key == domain_key)
                ).fetchone()
                domain_id = domain_result[0]

                # Update groups, recurring_event_groups, assignment_rules, filters
                conn.execute(
                    groups.update().
                    where(groups.c.domain_key == domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    recurring_event_groups.update().
                    where(recurring_event_groups.c.domain_key == domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    assignment_rules.update().
                    where(assignment_rules.c.domain_key == domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    filters.update().
                    where(filters.c.domain_key == domain_key).
                    values(domain_id=domain_id)
                )

    # 2. Migrate data from domain_auth table
    domain_auth_rows = conn.execute(sa.select(domain_auth)).fetchall()

    for row in domain_auth_rows:
        # Check if domain already exists (from YAML migration)
        existing = conn.execute(
            sa.select(domains).where(domains.c.domain_key == row.domain_key)
        ).fetchone()

        if existing:
            # Update existing domain with auth data and calendar_id
            conn.execute(
                domains.update().
                where(domains.c.domain_key == row.domain_key).
                values(
                    calendar_id=row.calendar_id,
                    admin_password_hash=row.admin_password_hash,
                    user_password_hash=row.user_password_hash
                )
            )
        else:
            # Create new domain from domain_auth (domains not in YAML)
            # Get calendar info for name
            calendar_result = conn.execute(
                sa.text("SELECT name, source_url FROM calendars WHERE id = :calendar_id"),
                {"calendar_id": row.calendar_id}
            ).fetchone()

            if calendar_result:
                conn.execute(
                    domains.insert().values(
                        domain_key=row.domain_key,
                        name=calendar_result[0],
                        calendar_url=calendar_result[1],
                        calendar_id=row.calendar_id,
                        admin_password_hash=row.admin_password_hash,
                        user_password_hash=row.user_password_hash,
                        status='active'
                    )
                )

                # Get the domain_id we just inserted
                domain_result = conn.execute(
                    sa.select(domains).where(domains.c.domain_key == row.domain_key)
                ).fetchone()
                domain_id = domain_result[0]

                # Update related tables
                conn.execute(
                    groups.update().
                    where(groups.c.domain_key == row.domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    recurring_event_groups.update().
                    where(recurring_event_groups.c.domain_key == row.domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    assignment_rules.update().
                    where(assignment_rules.c.domain_key == row.domain_key).
                    values(domain_id=domain_id)
                )

                conn.execute(
                    filters.update().
                    where(filters.c.domain_key == row.domain_key).
                    values(domain_id=domain_id)
                )


def downgrade() -> None:
    """No downgrade - data migration is one-way."""
    pass
