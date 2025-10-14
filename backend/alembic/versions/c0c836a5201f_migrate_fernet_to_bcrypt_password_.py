"""migrate_fernet_to_bcrypt_password_hashing

Revision ID: c0c836a5201f
Revises: cc5b28851942
Create Date: 2025-10-14 14:14:10.199403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0c836a5201f'
down_revision: Union[str, None] = 'cc5b28851942'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migrate from Fernet (AES) encryption to bcrypt hashing for passwords.

    BREAKING CHANGE: All existing passwords are cleared and must be reset.
    - Admin passwords: Force password reset on next login
    - User passwords: Force password reset on next login

    Rationale:
    - Fernet (AES) is encryption: reversible, requires key management
    - bcrypt is hashing: one-way, no key needed, industry standard for passwords
    - Reduces attack surface (no encryption key to leak)
    - Simpler configuration (no PASSWORD_ENCRYPTION_KEY env var)
    """
    # Clear all admin password hashes (force password reset)
    op.execute("UPDATE domains SET admin_password_hash = NULL WHERE admin_password_hash IS NOT NULL")

    # Clear all user password hashes (force password reset)
    op.execute("UPDATE domains SET user_password_hash = NULL WHERE user_password_hash IS NOT NULL")


def downgrade() -> None:
    """
    Downgrade not supported: cannot convert bcrypt hashes back to Fernet encryption.

    If you need to rollback, you must:
    1. Restore from database backup (before this migration)
    2. OR: Accept that all users must reset passwords again
    """
    raise NotImplementedError(
        "Cannot downgrade from bcrypt to Fernet: password hashes are one-way. "
        "Restore from backup or accept password resets."
    )
