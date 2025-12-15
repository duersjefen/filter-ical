"""
Lambda sync handler for scheduled calendar syncing.

This handler is invoked by EventBridge on a schedule to sync calendars.
"""

from backend.app.lambda_sync import handler

__all__ = ['handler']
