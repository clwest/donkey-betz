# Session 562: Push Notifications for Arbitrage Alerts

**Date:** December 27, 2025
**Status:** COMPLETE
**Branch:** feature/session-52-ai-assistant

---

## Summary

Implemented Web Push notifications for arbitrage alerts using the Web Push API (RFC 8030) with VAPID authentication. Users can now receive real-time browser notifications when profitable arbitrage opportunities are detected, even when the AI Studio tab isn't active.

---

## Features Implemented

### 1. Database Models (`core/models_push_notifications.py`)

| Model | Purpose |
|-------|---------|
| **PushSubscription** | Stores Web Push subscription data (endpoint, keys) |
| **NotificationPreference** | User preferences for alerts (profit threshold, sports, quiet hours) |
| **NotificationLog** | History of sent notifications for rate limiting |

### 2. Push Notification Service (`core/services/push_notification_service.py`)

- VAPID-authenticated push messages via `pywebpush`
- `send_arb_alert()` - Sends arb notifications to subscribers
- `send_line_movement_alert()` - Sends line movement alerts
- `send_test_notification()` - Test push delivery
- Rate limiting and quiet hours support

### 3. API Endpoints (`core/views_push_notifications.py`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/push/vapid-key/` | GET | Public | Get VAPID public key |
| `/api/v1/push/subscribe/` | POST | Public | Subscribe to push |
| `/api/v1/push/unsubscribe/` | POST | Public | Unsubscribe |
| `/api/v1/push/preferences/` | GET/PUT | Auth | Manage preferences |
| `/api/v1/push/status/` | GET | Auth | Check subscription status |
| `/api/v1/push/test/` | POST | Auth | Send test notification |

### 4. Service Worker (`ai_core/static/js/push-service-worker.js`)

- Handles incoming push events
- Shows notifications with custom icons and actions
- Click-to-navigate to betting dashboard
- Supports "View Details" and "Dismiss" actions

### 5. Frontend UI (`betting/betting_notifications.html`)

- 8th sub-tab in Betting Dashboard
- Enable/disable push notifications
- Configure arbitrage alert threshold
- Filter by sports
- Line movement alerts toggle
- Quiet hours configuration
- Rate limiting settings
- Test notification button

### 6. Celery Task (`core/tasks.py`)

- `scan_arbs_and_notify()` - Runs every 5 minutes
- Detects arbitrage opportunities via ArbitrageDetector agent
- Sends push notifications for 1%+ profit opportunities
- Rate limited to top 5 arbs per scan

---

## Configuration

### VAPID Keys (in `settings.py`)

```python
VAPID_PUBLIC_KEY = env('VAPID_PUBLIC_KEY', 'BFoZhpwPq8...')
VAPID_PRIVATE_KEY = env('VAPID_PRIVATE_KEY', '263F9LYf...')
VAPID_ADMIN_EMAIL = env('VAPID_ADMIN_EMAIL', 'admin@donkeybetz.com')
PUSH_NOTIFICATIONS_ENABLED = env_bool('PUSH_NOTIFICATIONS_ENABLED', True)
```

### Celery Beat Schedule

```python
'scan-arbs-and-notify': {
    'task': 'core.tasks.scan_arbs_and_notify',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
}
```

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `core/models_push_notifications.py` | Database models |
| `core/services/push_notification_service.py` | Push notification service |
| `core/views_push_notifications.py` | API views |
| `ai_core/static/js/push-service-worker.js` | Service worker |
| `ai_core/templates/components/panels/betting/betting_notifications.html` | UI component |
| `core/migrations/0127_session_562_push_notifications.py` | Migration |

### Modified Files

| File | Changes |
|------|---------|
| `core/models.py` | Import push notification models |
| `core/settings.py` | VAPID keys and push settings |
| `core/urls.py` | Push notification API routes |
| `core/auth_middleware.py` | Added public paths for push endpoints |
| `core/tasks.py` | Added `scan_arbs_and_notify()` task |
| `core/celery.py` | Added beat schedule |
| `betting_dashboard_panel.html` | Added Alerts tab |

---

## User Flow

1. **Enable Notifications**
   - User goes to Betting > Alerts tab
   - Clicks "Enable Notifications"
   - Browser prompts for permission
   - Service worker registers and subscribes

2. **Configure Preferences**
   - Set minimum profit threshold (default 1.0%)
   - Select sports to alert on
   - Enable line movement alerts
   - Set quiet hours

3. **Receive Alerts**
   - Celery scans for arbs every 5 minutes
   - When 1%+ arb found, notification sent
   - Click notification to open Betting > Arbitrage tab

---

## Testing

```bash
# Verify VAPID key endpoint
curl http://localhost:8000/api/v1/push/vapid-key/

# Check service worker
curl -I http://localhost:8000/static/js/push-service-worker.js

# Verify models
.venv/bin/python manage.py shell -c "from core.models_push_notifications import *; print('OK')"

# Run arb scan manually
.venv/bin/celery -A core call core.tasks.scan_arbs_and_notify
```

---

## Dependencies

Added to `requirements.txt`:
```
pywebpush==2.1.2
```

---

## Session 563 Priorities

From Session 562 roadmap:
1. **Mobile-Responsive Improvements** - Better touch UI for betting dashboard
2. **Betting Patterns Analysis** - Historical win/loss tracking
3. **Export Functionality** - CSV/PDF export for bet history
4. **WebSocket Notification Fallback** - In-app notifications when push fails

---

## Betting Dashboard Sub-Tabs (8)

1. Overview - Recent wagers, stats, top arbs
2. Live Odds - Sport filters, game cards
3. Arbitrage - Scanner with profit filters
4. Prediction Markets - Kalshi integration
5. Bankroll - P/L charts, win rate
6. Futures - Championship odds
7. Line Movement - Historical odds charts
8. **Alerts** - Push notification settings (NEW)

---

## Architecture Notes

### Push Flow
```
Browser
    ↓ (VAPID subscription)
/api/v1/push/subscribe/
    ↓
PushSubscription (DB)
    ↓
scan_arbs_and_notify() [Celery, every 5 min]
    ↓
ArbitrageDetector.execute()
    ↓
PushNotificationService.send_arb_alert()
    ↓
pywebpush → FCM/Mozilla Push Service
    ↓
Service Worker → Browser Notification
```

### Security
- VAPID authentication prevents unauthorized push
- Subscriptions linked to users for preferences
- Rate limiting prevents notification spam
- Quiet hours respect user sleep schedules
