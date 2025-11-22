#!/usr/bin/env python3
"""
Demo script for notification system.

This script demonstrates the notification features including:
- Creating notifications
- UI notifications
- Browser alerts (via API)
- Phone subscriptions
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notifications.notification_manager import (
    NotificationManager,
    NotificationSeverity
)


def main():
    """Run notification demo."""
    print("=" * 70)
    print("VUTS NOTIFICATION SYSTEM - DEMO")
    print("=" * 70)
    print()
    
    # Initialize notification manager (uses default output directory)
    data_dir = Path(__file__).parent / "demo_output"
    data_dir.mkdir(exist_ok=True)
    
    manager = NotificationManager(data_dir)
    
    print("📢 Creating sample notifications...")
    print()
    
    # Create various types of notifications
    notifications = [
        {
            'message': "Welcome to VUTS notification system!",
            'severity': NotificationSeverity.INFO,
            'topic': None,
            'score': None
        },
        {
            'message': "Strong positive sentiment detected for TSLA",
            'severity': NotificationSeverity.SUCCESS,
            'topic': "TSLA",
            'score': 8.5
        },
        {
            'message': "Negative trend detected for MSFT",
            'severity': NotificationSeverity.WARNING,
            'topic': "MSFT",
            'score': -3.5
        },
        {
            'message': "Critical negative sentiment for NVDA - potential selloff",
            'severity': NotificationSeverity.CRITICAL,
            'topic': "NVDA",
            'score': -8.5
        },
        {
            'message': "New article analyzed for AMD",
            'severity': NotificationSeverity.INFO,
            'topic': "AMD",
            'score': 2.5
        }
    ]
    
    for notif_data in notifications:
        n = manager.add_notification(
            message=notif_data['message'],
            severity=notif_data['severity'],
            topic=notif_data['topic'],
            score=notif_data['score']
        )
        
        severity_icon = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'critical': '🚨'
        }
        
        icon = severity_icon.get(n.severity.value, '📢')
        print(f"{icon} [{n.severity.value.upper()}] {n.message}")
        if n.topic:
            print(f"   Topic: {n.topic}, Score: {n.score}")
        print()
        time.sleep(0.5)
    
    print(f"✓ Created {len(notifications)} notifications")
    print()
    
    # Show notification summary
    print("=" * 70)
    print("NOTIFICATION SUMMARY")
    print("=" * 70)
    
    all_notifications = manager.get_notifications()
    unread_count = manager.get_unread_count()
    
    print(f"Total notifications: {len(all_notifications)}")
    print(f"Unread notifications: {unread_count}")
    print()
    
    # Show unread notifications
    print("=" * 70)
    print("UNREAD NOTIFICATIONS")
    print("=" * 70)
    print()
    
    unread = manager.get_notifications(unread_only=True, limit=10)
    for n in unread:
        severity_icon = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'critical': '🚨'
        }
        icon = severity_icon.get(n.severity.value, '📢')
        print(f"{icon} {n.message}")
        if n.topic:
            print(f"   Topic: {n.topic}, Score: {n.score}")
        print(f"   Time: {n.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # Demonstrate phone subscriptions
    print("=" * 70)
    print("PHONE SUBSCRIPTIONS")
    print("=" * 70)
    print()
    
    print("📱 Adding phone subscriptions...")
    
    # Add subscriptions for different users
    sub1 = manager.add_subscription(
        phone_number="+1234567890",
        topics=["TSLA", "MSFT"],
        min_severity="warning"
    )
    print(f"✓ Subscribed: {sub1['phone_number']}")
    print(f"  Topics: {', '.join(sub1['topics']) if sub1['topics'] else 'All'}")
    print(f"  Min Severity: {sub1['min_severity']}")
    print()
    
    sub2 = manager.add_subscription(
        phone_number="+9876543210",
        topics=[],  # All topics
        min_severity="critical"
    )
    print(f"✓ Subscribed: {sub2['phone_number']}")
    print(f"  Topics: {', '.join(sub2['topics']) if sub2['topics'] else 'All'}")
    print(f"  Min Severity: {sub2['min_severity']}")
    print()
    
    subscriptions = manager.get_subscriptions()
    print(f"Total subscriptions: {len(subscriptions)}")
    print()
    
    # Demonstrate score threshold checking
    print("=" * 70)
    print("AUTOMATIC THRESHOLD NOTIFICATIONS")
    print("=" * 70)
    print()
    
    print("📊 Checking score thresholds...")
    print()
    
    # Simulate high positive score
    print("Analyzing AAPL: Score = +8.5")
    manager.check_score_threshold(topic="AAPL", score=8.5)
    print("✓ Notification created for extremely positive sentiment")
    print()
    
    # Simulate high negative score
    print("Analyzing GOOGL: Score = -7.5")
    manager.check_score_threshold(topic="GOOGL", score=-7.5)
    print("✓ Notification created for extremely negative sentiment")
    print()
    
    # Summary
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print(f"✓ Notifications saved to: {data_dir / 'notifications.json'}")
    print(f"✓ Subscriptions saved to: {data_dir / 'notification_subscriptions.json'}")
    print()
    print("To view notifications in the UI:")
    print("  1. Start the web server: ./vuts ui")
    print("  2. Open browser to: http://localhost:5000")
    print("  3. Click the 🔔 icon in the top navigation bar")
    print()
    print("To access notifications via API:")
    print("  - GET  /api/notifications          - Get all notifications")
    print("  - GET  /api/notifications/unread   - Get unread notifications")
    print("  - POST /api/notifications/<id>/mark-read - Mark as read")
    print("  - GET  /api/notifications/subscriptions  - Get subscriptions")
    print()
    print("Browser notifications will be requested when you open the UI.")
    print("Allow notifications in your browser to receive audible alerts!")
    print()


if __name__ == '__main__':
    main()
