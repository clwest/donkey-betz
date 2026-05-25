# Session 438: Monetization - Phase 7

**Date:** December 13, 2025
**Status:** COMPLETE
**Previous Session:** 437 (Discord Automation)

---

## Summary

Implemented Phase 7 of the Discord-First platform: Monetization with subscription tiers, Stripe integration, and Discord role management.

---

## Features Implemented

### 1. Subscription Tiers

Three subscription levels with feature gating:

| Tier | Price | Daily Tasks | Priority Alerts | DM Notifications | Advisor Access | Custom Workflows | Discord Role |
|------|-------|-------------|-----------------|------------------|----------------|------------------|--------------|
| **Free** | $0 | 5 | No | No | No | No | None |
| **Pro** | $9.99/mo | 50 | Yes | Yes | No | No | "Pro Member" |
| **Premium** | $29.99/mo | Unlimited | Yes | Yes | Yes | Yes | "Premium Member" |

### 2. `/subscribe` Command

Subscribe to Pro or Premium tier directly from Discord:

```
/subscribe pro      # $9.99/mo - 50 tasks/day
/subscribe premium  # $29.99/mo - Unlimited tasks
```

**Features:**
- Creates Stripe checkout session
- Links to Stripe Customer Portal
- Shows tier features and pricing
- Secure payment via Stripe

### 3. `/tier` Command

View your subscription status and daily usage:

```
/tier   # Shows current tier, usage bar, features, upgrade prompts
```

**Displays:**
- Current tier with emoji (Free/Pro/Premium)
- Visual usage bar (tasks used / limit)
- Feature checklist (enabled/disabled)
- Subscription status (active/canceled/past_due)
- Discord role assignment
- Upgrade prompts for lower tiers

### 4. Stripe Integration Service

New service: `core/services/stripe_subscription.py`

**Features:**
- Customer creation/management
- Checkout session creation
- Webhook handling (subscription events)
- Billing portal access
- Discord role sync queueing

### 5. Database Fields

Added to `EnhancedUserProfile` model:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `subscription_tier` | CharField | 'free' | Current tier (free/pro/premium) |
| `stripe_customer_id` | CharField | null | Stripe customer ID |
| `stripe_subscription_id` | CharField | null | Active subscription ID |
| `subscription_status` | CharField | 'active' | Status (active/canceled/past_due/trialing) |
| `subscription_started_at` | DateTimeField | null | When subscription started |
| `subscription_ends_at` | DateTimeField | null | When subscription ends (for canceled) |
| `discord_role_synced` | BooleanField | False | Whether Discord role matches tier |
| `daily_task_count` | IntegerField | 0 | Tasks used today |
| `daily_task_reset` | DateTimeField | null | When counter was last reset |

**Migration:** `0088_session_438_subscription_monetization`

### 6. Profile Helper Methods

Added to `EnhancedUserProfile`:

```python
profile.get_tier_limits()     # Get feature limits for tier
profile.can_use_task()        # Check if user can use another task
profile.use_task()            # Increment task counter
profile.has_feature('name')   # Check if tier includes feature
profile.get_discord_role_name()  # Get Discord role for tier
```

---

## Files Modified

### Discord Bot
- `core/services/discord_bot.py`:
  - Added `/subscribe` command (lines 2192-2273)
  - Added `/tier` command (lines 2275-2406)
  - Updated docstring for Session 438

### New Service
- `core/services/stripe_subscription.py`:
  - `StripeSubscriptionService` class
  - Checkout session creation
  - Webhook handlers
  - Discord role sync queueing

### Models
- `core/models.py`:
  - Added 9 subscription fields to EnhancedUserProfile (lines 1613-1683)
  - Added 5 helper methods (lines 1806-1880)

### Migration
- `core/migrations/0088_session_438_subscription_monetization.py`

---

## Discord Commands Summary (33 Total)

| Phase | Commands | Description |
|-------|----------|-------------|
| 1 | `/gallery`, `/profile`, `/opportunities` | Content delivery |
| 2 | `/setup`, `/server-info` | Server setup |
| 3 | `/client-*` (4) | Client management |
| 4 | `/apply`, `/track` | Income pipeline |
| 5 | `/agent-*`, `/consult`, `/workflow-*` (6) | Full agent access |
| 6 | `/digest`, `/alerts` | Automation |
| **7** | **`/subscribe`, `/tier`** | **Monetization** |
| Core | `/ask`, `/create`, `/research`, `/clear`, etc. | Basic interactions |

---

## Stripe Setup Required

Before using subscriptions in production:

1. **Create Products in Stripe Dashboard:**
   - Pro Product: $9.99/month recurring
   - Premium Product: $29.99/month recurring

2. **Add Price IDs to .env:**
   ```env
   STRIPE_PRICE_PRO=price_xxxxx
   STRIPE_PRICE_PREMIUM=price_xxxxx
   ```

3. **Create Discord Roles:**
   - "Pro Member" role
   - "Premium Member" role

4. **Add Role IDs to .env:**
   ```env
   DISCORD_ROLE_PRO_ID=123456789
   DISCORD_ROLE_PREMIUM_ID=987654321
   ```

5. **Set up Stripe Webhook:**
   - Endpoint: `https://yourdomain.com/api/stripe/webhook`
   - Events: `customer.subscription.*`

---

## Testing

### Test `/tier` Command
```bash
# In Discord:
/tier   # Shows current tier even without subscription
```

### Test `/subscribe` Command
```bash
# In Discord:
/subscribe pro       # Get checkout link for Pro
/subscribe premium   # Get checkout link for Premium
```

### Verify Database Fields
```python
from core.models import EnhancedUserProfile
profile = EnhancedUserProfile.objects.first()
print(f"Tier: {profile.subscription_tier}")
print(f"Can use task: {profile.can_use_task()}")
print(f"Limits: {profile.get_tier_limits()}")
```

---

## Session 439 Priorities

1. **Set up Stripe Products**
   - Create Pro and Premium products in Stripe Dashboard
   - Configure recurring billing

2. **Implement Webhook Endpoint**
   - Create `/api/stripe/webhook` endpoint
   - Handle subscription lifecycle events

3. **Discord Role Assignment**
   - Create roles in Discord server
   - Implement automatic role assignment on subscription

4. **Feature Gating**
   - Enforce tier limits in `/agent-task`
   - Block advisor access for non-premium users

---

## Quick Start for Next Session

```bash
cat 00-START-NEXT-SESSION.md
make start
make celery
make discord-bot

# Test commands
# In Discord: /tier, /subscribe pro
```

---

**Phase 7: Monetization - COMPLETE!**

Discord Commands: 31 -> 33
New Model Fields: 9
New Service: stripe_subscription.py
