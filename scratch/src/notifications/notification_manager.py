"""
Notification Manager for VUTS.

Manages notifications including creation, storage, retrieval,
and user subscriptions for alerts via UI, browser, and phone.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class NotificationSeverity(Enum):
    """Notification severity levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"


class Notification:
    """Represents a single notification."""
    
    def __init__(
        self,
        message: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        topic: Optional[str] = None,
        score: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        notification_id: Optional[str] = None,
        read: bool = False
    ):
        self.message = message
        self.severity = severity
        self.topic = topic
        self.score = score
        self.timestamp = timestamp or datetime.now()
        self.notification_id = notification_id or self._generate_id()
        self.read = read
    
    def _generate_id(self) -> str:
        """Generate a unique notification ID."""
        return f"notif_{int(self.timestamp.timestamp() * 1000)}"
    
    def to_dict(self) -> Dict:
        """Convert notification to dictionary."""
        return {
            'id': self.notification_id,
            'message': self.message,
            'severity': self.severity.value,
            'topic': self.topic,
            'score': self.score,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Notification':
        """Create notification from dictionary."""
        return cls(
            message=data['message'],
            severity=NotificationSeverity(data['severity']),
            topic=data.get('topic'),
            score=data.get('score'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            notification_id=data['id'],
            read=data.get('read', False)
        )


class NotificationManager:
    """Manages notifications for the VUTS system."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize notification manager.
        
        Args:
            data_dir: Directory for storing notification data
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "output"
        
        self.data_dir = Path(data_dir)
        self.notifications_file = self.data_dir / "notifications.json"
        self.subscriptions_file = self.data_dir / "notification_subscriptions.json"
        
        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing notifications and subscriptions
        self.notifications: List[Notification] = self._load_notifications()
        self.subscriptions: List[Dict] = self._load_subscriptions()
    
    def _load_notifications(self) -> List[Notification]:
        """Load notifications from storage."""
        if not self.notifications_file.exists():
            return []
        
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Notification.from_dict(n) for n in data]
        except Exception as e:
            print(f"Error loading notifications: {e}")
            return []
    
    def _save_notifications(self):
        """Save notifications to storage."""
        try:
            data = [n.to_dict() for n in self.notifications]
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving notifications: {e}")
    
    def _load_subscriptions(self) -> List[Dict]:
        """Load phone subscriptions from storage."""
        if not self.subscriptions_file.exists():
            return []
        
        try:
            with open(self.subscriptions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading subscriptions: {e}")
            return []
    
    def _save_subscriptions(self):
        """Save subscriptions to storage."""
        try:
            with open(self.subscriptions_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscriptions, f, indent=2)
        except Exception as e:
            print(f"Error saving subscriptions: {e}")
    
    def add_notification(
        self,
        message: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        topic: Optional[str] = None,
        score: Optional[float] = None
    ) -> Notification:
        """
        Add a new notification.
        
        Args:
            message: Notification message
            severity: Notification severity level
            topic: Related topic/stock symbol
            score: Related sentiment score
        
        Returns:
            Created notification
        """
        notification = Notification(
            message=message,
            severity=severity,
            topic=topic,
            score=score
        )
        
        self.notifications.append(notification)
        self._save_notifications()
        
        return notification
    
    def get_notifications(
        self,
        unread_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Notification]:
        """
        Get notifications.
        
        Args:
            unread_only: Return only unread notifications
            limit: Maximum number of notifications to return
        
        Returns:
            List of notifications (newest first)
        """
        notifications = self.notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        # Sort by timestamp (newest first)
        notifications = sorted(notifications, key=lambda n: n.timestamp, reverse=True)
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of notification to mark
        
        Returns:
            True if notification was found and marked, False otherwise
        """
        for notification in self.notifications:
            if notification.notification_id == notification_id:
                notification.read = True
                self._save_notifications()
                return True
        
        return False
    
    def mark_all_as_read(self) -> int:
        """
        Mark all notifications as read.
        
        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification in self.notifications:
            if not notification.read:
                notification.read = True
                count += 1
        
        if count > 0:
            self._save_notifications()
        
        return count
    
    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of notification to delete
        
        Returns:
            True if notification was found and deleted, False otherwise
        """
        for i, notification in enumerate(self.notifications):
            if notification.notification_id == notification_id:
                del self.notifications[i]
                self._save_notifications()
                return True
        
        return False
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        return sum(1 for n in self.notifications if not n.read)
    
    def add_subscription(
        self,
        phone_number: str,
        topics: Optional[List[str]] = None,
        min_severity: str = "warning"
    ) -> Dict:
        """
        Add a phone subscription for notifications.
        
        Args:
            phone_number: Phone number to subscribe
            topics: List of topics to monitor (None = all topics)
            min_severity: Minimum severity level for notifications
        
        Returns:
            Subscription details
        """
        subscription = {
            'phone_number': phone_number,
            'topics': topics or [],
            'min_severity': min_severity,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        # Check if subscription already exists
        for i, sub in enumerate(self.subscriptions):
            if sub['phone_number'] == phone_number:
                self.subscriptions[i] = subscription
                self._save_subscriptions()
                return subscription
        
        self.subscriptions.append(subscription)
        self._save_subscriptions()
        
        return subscription
    
    def remove_subscription(self, phone_number: str) -> bool:
        """
        Remove a phone subscription.
        
        Args:
            phone_number: Phone number to unsubscribe
        
        Returns:
            True if subscription was found and removed, False otherwise
        """
        for i, sub in enumerate(self.subscriptions):
            if sub['phone_number'] == phone_number:
                del self.subscriptions[i]
                self._save_subscriptions()
                return True
        
        return False
    
    def get_subscriptions(self) -> List[Dict]:
        """Get all active subscriptions."""
        return [s for s in self.subscriptions if s.get('active', True)]
    
    def check_score_threshold(
        self,
        topic: str,
        score: float,
        threshold_positive: float = 7.0,
        threshold_negative: float = -7.0
    ):
        """
        Check if a score crosses threshold and create notification.
        
        Args:
            topic: Stock symbol/topic
            score: Sentiment score
            threshold_positive: Threshold for positive alerts
            threshold_negative: Threshold for negative alerts
        """
        if score >= threshold_positive:
            self.add_notification(
                message=f"Extremely positive sentiment detected for {topic}",
                severity=NotificationSeverity.SUCCESS,
                topic=topic,
                score=score
            )
        elif score <= threshold_negative:
            self.add_notification(
                message=f"Extremely negative sentiment detected for {topic}",
                severity=NotificationSeverity.CRITICAL,
                topic=topic,
                score=score
            )


def create_notification(
    message: str,
    severity: str = "info",
    topic: Optional[str] = None,
    score: Optional[float] = None,
    data_dir: Optional[Path] = None
) -> Notification:
    """
    Helper function to create a notification.
    
    Args:
        message: Notification message
        severity: Severity level (info, success, warning, critical)
        topic: Related topic/stock symbol
        score: Related sentiment score
        data_dir: Data directory for notification storage
    
    Returns:
        Created notification
    """
    manager = NotificationManager(data_dir)
    severity_enum = NotificationSeverity(severity)
    return manager.add_notification(message, severity_enum, topic, score)
