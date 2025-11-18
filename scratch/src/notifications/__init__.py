"""
Notification module for VUTS.

Provides notification management, storage, and delivery capabilities
for UI alerts, browser notifications, and phone subscriptions.
"""

from .notification_manager import (
    NotificationManager,
    Notification,
    NotificationSeverity,
    create_notification
)

__all__ = [
    'NotificationManager',
    'Notification',
    'NotificationSeverity',
    'create_notification'
]
