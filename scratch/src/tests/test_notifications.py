#!/usr/bin/env python3
"""
Test script for notification system.

This script validates the notification manager functionality without requiring API calls.
"""

import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path to import the notification module
sys.path.insert(0, str(Path(__file__).parent.parent))

from notifications.notification_manager import (
    NotificationManager,
    Notification,
    NotificationSeverity
)


def test_notification_creation():
    """Test creating notifications."""
    print("=" * 60)
    print("TEST: Notification Creation")
    print("=" * 60)
    
    try:
        # Create notification
        notification = Notification(
            message="Test notification",
            severity=NotificationSeverity.INFO,
            topic="TSLA",
            score=5.5
        )
        
        assert notification.message == "Test notification"
        assert notification.severity == NotificationSeverity.INFO
        assert notification.topic == "TSLA"
        assert notification.score == 5.5
        assert notification.read == False
        assert notification.notification_id is not None
        
        print("✓ Notification created successfully")
        print(f"  ID: {notification.notification_id}")
        print(f"  Message: {notification.message}")
        print(f"  Severity: {notification.severity.value}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_notification_serialization():
    """Test notification to/from dict conversion."""
    print("=" * 60)
    print("TEST: Notification Serialization")
    print("=" * 60)
    
    try:
        # Create notification
        notification = Notification(
            message="Test notification",
            severity=NotificationSeverity.WARNING,
            topic="MSFT",
            score=-3.5
        )
        
        # Convert to dict
        data = notification.to_dict()
        assert 'id' in data
        assert data['message'] == "Test notification"
        assert data['severity'] == "warning"
        
        # Convert back from dict
        restored = Notification.from_dict(data)
        assert restored.message == notification.message
        assert restored.severity == notification.severity
        assert restored.topic == notification.topic
        assert restored.score == notification.score
        
        print("✓ Serialization works correctly")
        print(f"  Original: {notification.message}")
        print(f"  Restored: {restored.message}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_notification_manager():
    """Test notification manager basic operations."""
    print("=" * 60)
    print("TEST: Notification Manager")
    print("=" * 60)
    
    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Add notifications
            n1 = manager.add_notification(
                message="First notification",
                severity=NotificationSeverity.INFO,
                topic="TSLA",
                score=2.5
            )
            
            n2 = manager.add_notification(
                message="Second notification",
                severity=NotificationSeverity.SUCCESS,
                topic="MSFT",
                score=7.5
            )
            
            # Get all notifications
            notifications = manager.get_notifications()
            assert len(notifications) == 2
            
            # Get unread count
            unread_count = manager.get_unread_count()
            assert unread_count == 2
            
            print("✓ Notification manager works correctly")
            print(f"  Total notifications: {len(notifications)}")
            print(f"  Unread count: {unread_count}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_mark_as_read():
    """Test marking notifications as read."""
    print("=" * 60)
    print("TEST: Mark as Read")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Add notification
            n = manager.add_notification(
                message="Test notification",
                severity=NotificationSeverity.INFO
            )
            
            # Mark as read
            success = manager.mark_as_read(n.notification_id)
            assert success == True
            
            # Check unread count
            unread_count = manager.get_unread_count()
            assert unread_count == 0
            
            print("✓ Mark as read works correctly")
            print(f"  Unread count after marking: {unread_count}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_mark_all_as_read():
    """Test marking all notifications as read."""
    print("=" * 60)
    print("TEST: Mark All as Read")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Add multiple notifications
            manager.add_notification("Notification 1", NotificationSeverity.INFO)
            manager.add_notification("Notification 2", NotificationSeverity.WARNING)
            manager.add_notification("Notification 3", NotificationSeverity.SUCCESS)
            
            # Mark all as read
            count = manager.mark_all_as_read()
            assert count == 3
            
            # Check unread count
            unread_count = manager.get_unread_count()
            assert unread_count == 0
            
            print("✓ Mark all as read works correctly")
            print(f"  Notifications marked: {count}")
            print(f"  Remaining unread: {unread_count}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_delete_notification():
    """Test deleting notifications."""
    print("=" * 60)
    print("TEST: Delete Notification")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Add notification
            n = manager.add_notification("Test notification", NotificationSeverity.INFO)
            
            # Delete notification
            success = manager.delete_notification(n.notification_id)
            assert success == True
            
            # Check count
            notifications = manager.get_notifications()
            assert len(notifications) == 0
            
            print("✓ Delete notification works correctly")
            print(f"  Notifications remaining: {len(notifications)}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_subscriptions():
    """Test phone subscriptions."""
    print("=" * 60)
    print("TEST: Phone Subscriptions")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Add subscription
            sub = manager.add_subscription(
                phone_number="+1234567890",
                topics=["TSLA", "MSFT"],
                min_severity="warning"
            )
            
            assert sub['phone_number'] == "+1234567890"
            assert sub['topics'] == ["TSLA", "MSFT"]
            assert sub['min_severity'] == "warning"
            
            # Get subscriptions
            subs = manager.get_subscriptions()
            assert len(subs) == 1
            
            # Remove subscription
            success = manager.remove_subscription("+1234567890")
            assert success == True
            
            # Check count
            subs = manager.get_subscriptions()
            assert len(subs) == 0
            
            print("✓ Subscriptions work correctly")
            print(f"  Phone: {sub['phone_number']}")
            print(f"  Topics: {sub['topics']}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_score_threshold():
    """Test automatic notification on score threshold."""
    print("=" * 60)
    print("TEST: Score Threshold")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = NotificationManager(Path(tmpdir))
            
            # Test positive threshold
            manager.check_score_threshold(topic="TSLA", score=8.5)
            
            # Test negative threshold
            manager.check_score_threshold(topic="MSFT", score=-8.0)
            
            # Check notifications were created
            notifications = manager.get_notifications()
            assert len(notifications) == 2
            
            # Check severity
            assert notifications[0].severity == NotificationSeverity.CRITICAL
            assert notifications[1].severity == NotificationSeverity.SUCCESS
            
            print("✓ Score threshold works correctly")
            print(f"  Notifications created: {len(notifications)}")
            print(f"  Positive threshold: {notifications[1].message}")
            print(f"  Negative threshold: {notifications[0].message}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_persistence():
    """Test notification persistence across manager instances."""
    print("=" * 60)
    print("TEST: Persistence")
    print("=" * 60)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first manager and add notifications
            manager1 = NotificationManager(Path(tmpdir))
            manager1.add_notification("Test 1", NotificationSeverity.INFO)
            manager1.add_notification("Test 2", NotificationSeverity.WARNING)
            
            # Create second manager (should load from file)
            manager2 = NotificationManager(Path(tmpdir))
            notifications = manager2.get_notifications()
            
            assert len(notifications) == 2
            assert notifications[0].message in ["Test 1", "Test 2"]
            
            print("✓ Persistence works correctly")
            print(f"  Notifications loaded: {len(notifications)}")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print()
    print("=" * 60)
    print("NOTIFICATION MODULE - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_notification_creation,
        test_notification_serialization,
        test_notification_manager,
        test_mark_as_read,
        test_mark_all_as_read,
        test_delete_notification,
        test_subscriptions,
        test_score_threshold,
        test_persistence
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Notification Creation",
        "Serialization",
        "Manager Operations",
        "Mark as Read",
        "Mark All as Read",
        "Delete Notification",
        "Subscriptions",
        "Score Threshold",
        "Persistence"
    ]
    
    for name, result in zip(test_names, results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(results)
    total = len(results)
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed!")
        return 0
    else:
        print()
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
