"""
Admin Password Reset Token Model

Stores temporary tokens for admin password reset functionality.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..core.database import Base


class AdminPasswordResetToken(Base):
    """
    Model for admin password reset tokens.

    Tokens expire after 1 hour and can only be used once.
    """
    __tablename__ = "admin_password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    used = Column(Integer, default=0, nullable=False)  # 0 = not used, 1 = used
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<AdminPasswordResetToken(token='{self.token[:8]}...', used={self.used})>"

    @property
    def is_expired(self):
        """Check if token has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.used and not self.is_expired

    @classmethod
    def create_token(cls):
        """Generate a new secure token with 1-hour expiry."""
        import secrets
        token = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        return cls(token=token, expires_at=expires_at)
