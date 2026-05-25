# Session 439: Subscription Enforcement & Billing

**Date:** December 13, 2025
**Status:** COMPLETE
**Previous Session:** 438 (Monetization + Voice AI)

---

## Summary

Completed the subscription infrastructure from Session 438 by implementing:
- Stripe webhook endpoint for subscription lifecycle events
- Automatic Discord role assignment on subscription changes
- Feature gating for agent tasks and advisor access
- `/cancel` and `/billing` subscription management commands

---

## Features Implemented

### 1. Stripe Webhook Endpoint

**New File:** `core/views_stripe.py`

Handles Stripe webhook events:
- `customer.subscription.created` - Activate subscription
- `customer.subscription.updated` - Update tier/status
- `customer.subscription.deleted` - Downgrade to free
- `checkout.session.completed` - Log successful checkout
- `invoice.payment_succeeded` - Log successful payment
- `invoice.payment_failed` - Log failed payment

**Endpoint:** `POST /api/stripe/webhook/`

```python
# Webhook signature verification (production)
event = stripe.Webhook.construct_event(
    payload, sig_header, STRIPE_WEBHOOK_SECRET
)
```

### 2. Discord Role Manager

**New Cog:** `RoleManager` in `discord_bot.py`

Automatic role assignment based on subscription tier:
- Background task polls cache every 10 seconds
- Picks up role sync requests from Stripe webhook
- Assigns/removes Pro Member and Premium Member roles
- Updates `discord_role_synced` flag on profile

**Environment Variables Required:**
```env
DISCORD_ROLE_PRO_ID=123456789012345678
DISCORD_ROLE_PREMIUM_ID=987654321098765432
```

### 3. Feature Gating

**Agent Tasks (`/agent-task`):**
- Checks subscription tier limits before execution
- Shows upgrade prompt when limit reached
- Increments daily task counter on success

**Advisor Access (`/consult`):**
- Premium-only feature
- Shows upgrade prompt for Free/Pro users
- Lists Premium benefits (25 advisors, unlimited tasks)

**Tier Limits:**
| Tier | Daily Tasks | Advisor Access |
|------|-------------|----------------|
| Free | 5 | No |
| Pro | 50 | No |
| Premium | Unlimited | Yes |

### 4. New Discord Commands

| Command | Description |
|---------|-------------|
| `/cancel` | Cancel subscription at end of billing period |
| `/billing` | Access Stripe Customer Portal for billing management |

**Total Discord Commands: 38**

---

## Files Created/Modified

### New Files
- `core/views_stripe.py` - Stripe webhook handlers
- `docs/handoffs/SESSION_439_SUBSCRIPTION_ENFORCEMENT.md` - This file

### Modified Files
- `core/urls.py`:
  - Added import for `views_stripe`
  - Added `/api/stripe/webhook/` endpoint
  - Added `/api/stripe/subscription-status/` endpoint

- `core/services/discord_bot.py`:
  - Added `tasks` to imports for background tasks
  - Added `RoleManager` cog with role sync background task
  - Added subscription limit check to `/agent-task`
  - Added Premium-only check to `/consult`
  - Added `/cancel` command
  - Added `/billing` command

---

## Architecture

### Subscription Flow

```
User clicks /subscribe
        │
        ▼
Stripe Checkout Session
        │
        ▼
User completes payment
        │
        ▼
Stripe sends webhook
        │
        ▼
┌─────────────────────────────────┐
│ /api/stripe/webhook/            │
│ - Verify signature              │
│ - Update EnhancedUserProfile    │
│ - Queue Discord role sync       │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│ RoleManager Background Task     │
│ (polls every 10 seconds)        │
│ - Check cache for pending syncs │
│ - Assign/remove Discord roles   │
│ - Update profile.discord_role_synced │
└─────────────────────────────────┘
```

### Feature Gating Flow

```
User runs /agent-task
        │
        ▼
Check subscription tier
        │
        ├── Free: 5 tasks/day limit
        ├── Pro: 50 tasks/day limit
        └── Premium: Unlimited
        │
        ▼
   ┌────────────┐
   │ Limit OK?  │
   └────────────┘
        │
    No  │  Yes
        │   │
        ▼   ▼
   Show     Execute agent
   upgrade  Increment counter
   prompt
```

---

## Discord Commands Summary (38 Total)

| Category | Commands | Count |
|----------|----------|-------|
| Interactive | `/ask`, `/create`, `/research`, `/clear` | 4 |
| System | `/status`, `/spiders` | 2 |
| Agents | `/agents`, `/agent`, `/agent-list`, `/agent-task` | 4 |
| Advisors | `/advisors`, `/consult` | 2 |
| Workflows | `/workflow-list`, `/workflow-run` | 2 |
| Data | `/trending` | 1 |
| Content | `/gallery`, `/profile` | 2 |
| Income | `/opportunities`, `/apply`, `/track` | 3 |
| Automation | `/digest`, `/alerts` | 2 |
| **Monetization** | `/subscribe`, `/tier`, `/cancel`, `/billing` | **4** |
| Voice AI | `/voice`, `/speak`, `/ask-voice` | 3 |
| Account | `/link`, `/unlink` | 2 |
| Server | `/setup`, `/server-info` | 2 |
| Clients | `/client-add`, `/client-list`, `/client-deliver`, `/client-invite` | 4 |
| Help | `/help` | 1 |

---

## Stripe Setup Required

### 1. Create Webhook in Stripe Dashboard

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/stripe/webhook/`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret

### 2. Add Environment Variables

```env
# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRICE_PRO=price_xxxxx
STRIPE_PRICE_PREMIUM=price_xxxxx

# Discord Roles (create these in your server)
DISCORD_ROLE_PRO_ID=123456789012345678
DISCORD_ROLE_PREMIUM_ID=987654321098765432
```

### 3. Create Discord Roles

1. Go to Discord Server Settings → Roles
2. Create "Pro Member" role with desired color/permissions
3. Create "Premium Member" role with desired color/permissions
4. Copy role IDs (right-click role → Copy ID)

---

## Testing

### Test Webhook (Local Development)

```bash
# Use Stripe CLI for local testing
stripe listen --forward-to localhost:8000/api/stripe/webhook/

# Trigger test events
stripe trigger customer.subscription.created
```

### Test Feature Gating

```bash
# In Discord:
/agent-task ResearchAgent "Test task"  # Should work for first 5 tasks
# After 5 tasks on Free tier:
/agent-task ResearchAgent "Another task"  # Should show upgrade prompt

/consult warren "Investment advice"  # Should show Premium-only prompt
```

### Test Subscription Management

```bash
# In Discord:
/tier           # View current subscription
/subscribe pro  # Get checkout link
/billing        # Access billing portal
/cancel         # Cancel subscription
```

---

## Session 440 Next Steps

1. **Production Deployment**
   - Set up Stripe webhook in production
   - Configure production environment variables

2. **Usage Analytics**
   - Track daily/weekly usage per tier
   - Monitor conversion rates

3. **Tier Upgrade Prompts**
   - Proactive prompts when approaching limits
   - Usage summary in `/digest`

4. **White-label (Phase 9)**
   - Custom branding per server
   - Multi-tenant subscription management

---

**Session 439: Subscription Enforcement - COMPLETE!**

Discord Commands: 36 -> 38
New Webhook: /api/stripe/webhook/
New Cog: RoleManager (background role sync)
Feature Gating: /agent-task + /consult
