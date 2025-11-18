# VUTS Notification Module

A comprehensive notification system for alerting users about important sentiment changes and updates.

## Features

- **In-App Notifications**: Display notifications in the web UI with badge indicators
- **Browser Alerts**: Trigger audible browser notifications using the Notification API
- **Phone Subscriptions**: Subscribe phone numbers for critical alerts (SMS/webhook ready)
- **Severity Levels**: info, success, warning, critical
- **Persistent Storage**: JSON-based notification and subscription storage
- **Read/Unread Tracking**: Mark notifications as read/unread
- **Topic Filtering**: Filter notifications by stock symbols/topics

## Quick Start

### Creating Notifications

```python
from notifications import NotificationManager, NotificationSeverity

# Initialize manager
manager = NotificationManager()

# Add a notification
notification = manager.add_notification(
    message="Extremely positive sentiment detected for TSLA",
    severity=NotificationSeverity.SUCCESS,
    topic="TSLA",
    score=8.5
)

# Check score thresholds automatically
manager.check_score_threshold(topic="TSLA", score=8.5)
```

### Retrieving Notifications

```python
# Get all notifications
all_notifications = manager.get_notifications()

# Get unread only
unread = manager.get_notifications(unread_only=True)

# Get limited count
recent = manager.get_notifications(limit=10)

# Get unread count
count = manager.get_unread_count()
```

### Managing Read Status

```python
# Mark as read
manager.mark_as_read(notification_id="notif_1234567890")

# Mark all as read
count = manager.mark_all_as_read()
```

### Phone Subscriptions

```python
# Add subscription
subscription = manager.add_subscription(
    phone_number="+1234567890",
    topics=["TSLA", "MSFT"],  # None = all topics
    min_severity="warning"     # info, success, warning, critical
)

# Get subscriptions
subscriptions = manager.get_subscriptions()

# Remove subscription
manager.remove_subscription(phone_number="+1234567890")
```

## Web UI Integration

The notification system is integrated with the Flask web UI:

### API Endpoints

- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/unread` - Get unread notifications
- `POST /api/notifications/<id>/mark-read` - Mark notification as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `DELETE /api/notifications/<id>` - Delete notification
- `GET /api/notifications/count` - Get unread count
- `POST /api/notifications/subscribe` - Add phone subscription
- `DELETE /api/notifications/subscribe` - Remove phone subscription
- `GET /api/notifications/subscriptions` - Get subscriptions

### Browser Notifications

The UI includes JavaScript code to request browser notification permissions and display notifications with sound alerts.

```javascript
// Request permission (done automatically on page load)
Notification.requestPermission();

// Notifications are automatically displayed when new ones arrive
```

## Data Storage

Notifications are stored in JSON files:

```
output/
├── notifications.json              # All notifications
└── notification_subscriptions.json # Phone subscriptions
```

### Notification Format

```json
{
  "id": "notif_1700000000000",
  "message": "Extremely positive sentiment for TSLA",
  "severity": "success",
  "topic": "TSLA",
  "score": 8.5,
  "timestamp": "2024-11-18T12:00:00",
  "read": false
}
```

### Subscription Format

```json
{
  "phone_number": "+1234567890",
  "topics": ["TSLA", "MSFT"],
  "min_severity": "warning",
  "created_at": "2024-11-18T12:00:00",
  "active": true
}
```

## Severity Levels

| Level | Usage | Color | Example |
|-------|-------|-------|---------|
| `info` | General updates | Blue | "New article analyzed" |
| `success` | Positive events | Green | "Extremely positive sentiment (+8.5)" |
| `warning` | Concerning events | Orange | "Negative sentiment trend" |
| `critical` | Urgent issues | Red | "Extremely negative sentiment (-8.5)" |

## Automatic Notifications

The sentiment analyzer can automatically create notifications:

```python
# In sentiment_analyzer.py
from notifications import NotificationManager

manager = NotificationManager()

# After analyzing an article
if score >= 7.0:
    manager.add_notification(
        message=f"Extremely positive sentiment for {topic}",
        severity=NotificationSeverity.SUCCESS,
        topic=topic,
        score=score
    )
```

## Integration with Sentiment Analysis

To automatically notify on extreme sentiment scores:

```python
from notifications import NotificationManager

manager = NotificationManager()

# Check score thresholds
manager.check_score_threshold(
    topic="TSLA",
    score=8.5,
    threshold_positive=7.0,
    threshold_negative=-7.0
)
```

## Phone/SMS Integration

The subscription system is designed to integrate with SMS/webhook services:

```python
# In your notification sender (e.g., scheduled job)
from notifications import NotificationManager

manager = NotificationManager()

# Get subscriptions
subscriptions = manager.get_subscriptions()

# For each new critical notification
for notification in manager.get_notifications(unread_only=True):
    if notification.severity == NotificationSeverity.CRITICAL:
        for sub in subscriptions:
            # Check if subscriber is interested
            if notification.severity.value in ['warning', 'critical']:
                if not sub['topics'] or notification.topic in sub['topics']:
                    # Send SMS/webhook here
                    send_sms(sub['phone_number'], notification.message)
```

### Recommended SMS/Webhook Services

- **Twilio**: SMS delivery
- **AWS SNS**: SMS and push notifications
- **Zapier**: Webhook-based integrations
- **IFTTT**: Webhook-based automations

## Testing

```bash
cd scratch
python src/tests/test_notifications.py
```

## Future Enhancements

- Email notifications
- Slack/Discord webhooks
- Custom notification rules/filters
- Notification scheduling
- Batch notification digests
- Notification history archival

## Security Notes

- Phone numbers are stored in plain text (consider encryption for production)
- No authentication on subscription endpoints (add auth for production)
- Rate limiting recommended for SMS delivery
- Validate phone numbers before storing

## Examples

See `demos/demo_notifications.py` for complete examples.
