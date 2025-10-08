"""create_user_account_system

Revision ID: a1b2c3d4e5f6
Revises: fd1683e51aa9
Create Date: 2025-01-10 00:00:00.000000

Comprehensive migration to implement user account system:
1. Create users table (global admin + regular users)
2. Create user_domain_access table (domain unlocking)
3. Add user_id to calendars and filters
4. Move domain_key from calendars to domain_auth
5. Remove username from calendars and filters
6. Seed global admin from environment variables
"""

import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '291591d9697b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade to user account system."""

    # ===================================================================
    # STEP 1: Create users table
    # ===================================================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('reset_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token_expires', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # ===================================================================
    # STEP 2: Create user_domain_access table
    # ===================================================================
    op.create_table(
        'user_domain_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('calendar_id', sa.Integer(), nullable=False),
        sa.Column('access_level', sa.String(length=20), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'calendar_id', 'access_level', name='uq_user_calendar_access')
    )
    op.create_index('ix_user_domain_access_id', 'user_domain_access', ['id'])
    op.create_index('ix_user_domain_access_user_id', 'user_domain_access', ['user_id'])
    op.create_index('ix_user_domain_access_calendar_id', 'user_domain_access', ['calendar_id'])

    # ===================================================================
    # STEP 3: Add user_id to calendars table
    # ===================================================================
    with op.batch_alter_table('calendars', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_calendars_user_id', 'users', ['user_id'], ['id'])
        batch_op.create_index('ix_calendars_user_id', ['user_id'])

    # ===================================================================
    # STEP 4: Add user_id to filters table
    # ===================================================================
    with op.batch_alter_table('filters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_filters_user_id', 'users', ['user_id'], ['id'])
        batch_op.create_index('ix_filters_user_id', ['user_id'])

    # ===================================================================
    # STEP 5: Move domain_key from calendars to domain_auth
    # ===================================================================
    # Note: domain_auth.domain_key might already exist from previous migration
    # We'll check and only add if it doesn't exist

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    domain_auth_columns = [col['name'] for col in inspector.get_columns('domain_auth')]

    # Add domain_key to domain_auth if it doesn't exist
    if 'domain_key' not in domain_auth_columns:
        with op.batch_alter_table('domain_auth', schema=None) as batch_op:
            batch_op.add_column(sa.Column('domain_key', sa.String(length=100), nullable=True))

        # Copy domain_key from calendars to domain_auth
        connection.execute(text("""
            UPDATE domain_auth
            SET domain_key = (
                SELECT c.domain_key
                FROM calendars c
                WHERE c.id = domain_auth.calendar_id
            )
            WHERE domain_auth.calendar_id IS NOT NULL
        """))

        # Make domain_key NOT NULL after data migration
        with op.batch_alter_table('domain_auth', schema=None) as batch_op:
            batch_op.alter_column('domain_key', nullable=False)
            batch_op.create_index('ix_domain_auth_domain_key', ['domain_key'], unique=True)

    # ===================================================================
    # STEP 6: Remove domain_key from calendars table
    # ===================================================================
    calendar_columns = [col['name'] for col in inspector.get_columns('calendars')]
    if 'domain_key' in calendar_columns:
        # Check if index exists before trying to drop it
        calendars_indexes = [idx['name'] for idx in inspector.get_indexes('calendars')]

        with op.batch_alter_table('calendars', schema=None) as batch_op:
            # Drop index first if it exists
            if 'ix_calendars_domain_key' in calendars_indexes:
                batch_op.drop_index('ix_calendars_domain_key')
            batch_op.drop_column('domain_key')

    # ===================================================================
    # STEP 7: Remove username from calendars table
    # ===================================================================
    if 'username' in calendar_columns:
        with op.batch_alter_table('calendars', schema=None) as batch_op:
            batch_op.drop_column('username')

    # ===================================================================
    # STEP 8: Remove username from filters table
    # ===================================================================
    filter_columns = [col['name'] for col in inspector.get_columns('filters')]
    if 'username' in filter_columns:
        with op.batch_alter_table('filters', schema=None) as batch_op:
            batch_op.drop_column('username')

    # ===================================================================
    # STEP 9: Seed global admin user from environment variables
    # ===================================================================
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@filter-ical.de')
    admin_password = os.getenv('ADMIN_PASSWORD', 'change-me-in-production')

    # Hash password with bcrypt
    import bcrypt
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert global admin user
    connection.execute(text("""
        INSERT INTO users (username, email, password_hash, role, created_at, updated_at)
        VALUES ('admin', :email, :password_hash, 'global_admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """), {"email": admin_email, "password_hash": password_hash})

    print(f"✅ Global admin user created with email: {admin_email}")
    print("⚠️  IMPORTANT: Change admin password after deployment!")


def downgrade() -> None:
    """Downgrade from user account system."""

    # WARNING: This downgrade will lose user account data!
    # Only use in development environments.

    # Re-add username to filters
    with op.batch_alter_table('filters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=100), nullable=True))

    # Re-add username to calendars
    with op.batch_alter_table('calendars', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=100), nullable=True))

    # Re-add domain_key to calendars
    with op.batch_alter_table('calendars', schema=None) as batch_op:
        batch_op.add_column(sa.Column('domain_key', sa.String(length=100), nullable=True))
        batch_op.create_index('ix_calendars_domain_key', ['domain_key'], unique=False)

    # Copy domain_key back from domain_auth to calendars
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE calendars
        SET domain_key = (
            SELECT da.domain_key
            FROM domain_auth da
            WHERE da.calendar_id = calendars.id
        )
        WHERE calendars.id IN (SELECT calendar_id FROM domain_auth)
    """))

    # Remove domain_key from domain_auth
    with op.batch_alter_table('domain_auth', schema=None) as batch_op:
        batch_op.drop_index('ix_domain_auth_domain_key')
        batch_op.drop_column('domain_key')

    # Remove user_id from filters
    with op.batch_alter_table('filters', schema=None) as batch_op:
        batch_op.drop_index('ix_filters_user_id')
        batch_op.drop_constraint('fk_filters_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    # Remove user_id from calendars
    with op.batch_alter_table('calendars', schema=None) as batch_op:
        batch_op.drop_index('ix_calendars_user_id')
        batch_op.drop_constraint('fk_calendars_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    # Drop user_domain_access table
    op.drop_index('ix_user_domain_access_calendar_id', table_name='user_domain_access')
    op.drop_index('ix_user_domain_access_user_id', table_name='user_domain_access')
    op.drop_index('ix_user_domain_access_id', table_name='user_domain_access')
    op.drop_table('user_domain_access')

    # Drop users table
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
