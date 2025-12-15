# Session 450: Stripe Integration for Voice Marketplace

**Date:** December 14, 2025
**Status:** COMPLETE
**Focus:** Integrate Stripe payments for voice marketplace - Discord + Web App

---

## Summary

Added Stripe payment processing to the voice marketplace, enabling users to purchase voice generation credits through both Discord and the web app. The 70/30 revenue split (creator/platform) is automatically calculated on each transaction.

---

## What Was Built

### 1. Stripe Voice Payment Service (`core/services/stripe_voice_payments.py`)

Central service handling all payment operations:

| Method | Purpose |
|--------|---------|
| `create_checkout_session()` | Create Stripe Checkout session for voice purchase |
| `handle_webhook()` | Process Stripe webhook events (payment confirmation) |
| `get_checkout_status()` | Check payment session status |
| `get_voice_price_estimate()` | Calculate price without creating session |
| `simulate_purchase()` | Test purchases when Stripe not configured |

**Key Features:**
- Automatic 70/30 revenue split calculation
- Support for all 3 pricing models (per_minute, per_character, flat_rate)
- Minimum price of $0.10 per transaction
- Duration estimation based on text length (~150 chars/minute)
- Graceful fallback when Stripe not configured (simulated mode)

### 2. REST API Endpoints (`core/views_stripe_voice.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/voice-checkout/create/` | POST | Create Stripe checkout session |
| `/api/voice-checkout/price/` | GET/POST | Get price estimate |
| `/api/voice-checkout/webhook/` | POST | Stripe webhook handler |
| `/api/voice-checkout/status/<session_id>/` | GET | Check payment status |
| `/api/voice-checkout/simulate/` | POST | Test purchase (no real payment) |
| `/voice-checkout/success/` | GET | Post-payment success page |
| `/voice-checkout/cancel/` | GET | Payment cancelled page |

### 3. Discord Command (`/voice-buy`)

New command added to `VoiceMarketplaceCommands` cog:

```
/voice-buy <voice_name> <text_length> [content_type]
```

**Parameters:**
- `voice_name`: Voice name or partial ID
- `text_length`: Number of characters (10-50,000)
- `content_type`: animated_series, audiobook, video, podcast, commercial, personal

**Flow:**
1. User runs `/voice-buy DonkeyKing 500 animated_series`
2. Bot calculates price based on voice's pricing model
3. Bot creates Stripe Checkout session
4. Bot returns embed with checkout URL
5. User clicks link, completes payment on Stripe
6. Webhook confirms payment, creates VoiceTransaction

**Response Embed Shows:**
- Voice name and owner
- Character count and estimated audio duration
- Price breakdown
- Revenue split (70% creator / 30% platform)
- Clickable checkout link

### 4. Web App Voice Marketplace (`voice_marketplace_panel.html`)

Full marketplace UI added to AI Studio:

**Stats Dashboard:**
- Available voices count
- My voices count
- My earnings
- Purchase history
- Featured voices

**Browse Features:**
- Search by name, style, accent
- Filter by gender, age range, use case
- Sort by rating, popularity, price, newest
- Pagination (12 per page)

**Voice Cards:**
- Name, description preview
- Star rating and review count
- Price display
- Gender and age badges
- Click to view details

**Detail Modal:**
- Full voice info
- Purchase form (characters, use case)
- Live price calculation
- Preview generation
- Stripe checkout button

### 5. Navigation Update

Added "Voices" tab to `studio_tabs.html`:
- Position: After Portfolio, before Leadership
- Icon: Microphone emoji
- Tooltip: "Voice Marketplace - Buy & Sell AI Voices"

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `core/services/stripe_voice_payments.py` | CREATE | 320 |
| `core/views_stripe_voice.py` | CREATE | 280 |
| `core/urls.py` | MODIFY | +22 |
| `core/services/discord_bot.py` | MODIFY | +200 |
| `ai_core/templates/components/panels/voice_marketplace_panel.html` | CREATE | 380 |
| `ai_core/templates/components/navigation/studio_tabs.html` | MODIFY | +7 |
| `ai_core/templates/ai_image_studio.html` | MODIFY | +4 |

---

## Checkout Flow

### Discord Flow
```
User: /voice-buy DonkeyKing 500 animated_series
  ↓
Bot: Finds voice, calculates price ($0.50)
  ↓
Bot: Creates Stripe Checkout Session
  ↓
Bot: Returns embed with checkout URL
  ↓
User: Clicks link → Stripe hosted checkout
  ↓
User: Completes payment
  ↓
Stripe: Sends webhook to /api/voice-checkout/webhook/
  ↓
Server: Creates VoiceTransaction, updates stats
  ↓
User: Redirected to success page
```

### Web Flow
```
User: Clicks "Voices" tab
  ↓
UI: Loads marketplace grid
  ↓
User: Clicks voice card → Detail modal
  ↓
User: Sets character count → Price updates
  ↓
User: Clicks "Checkout with Stripe"
  ↓
API: POST /api/voice-checkout/create/
  ↓
Server: Creates Stripe Checkout Session
  ↓
User: Redirected to Stripe checkout
  ↓
[Same as Discord from here]
```

---

## Environment Variables

Already configured in `.env`:
```bash
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLIC_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...  # Optional but recommended
```

---

## Testing

### Test API Endpoints
```bash
# Get price estimate (requires auth)
curl "http://localhost:8000/api/voice-checkout/price/?voice_id=<uuid>&text_length=500"

# Create checkout (requires auth)
curl -X POST http://localhost:8000/api/voice-checkout/create/ \
  -H "Content-Type: application/json" \
  -d '{"voice_id": "<uuid>", "text_length": 500}'

# Simulate purchase (requires auth)
curl -X POST http://localhost:8000/api/voice-checkout/simulate/ \
  -H "Content-Type: application/json" \
  -d '{"voice_id": "<uuid>", "text_length": 500}'
```

### Test Discord Command
```
/voice-buy voice_name:DonkeyKing text_length:500 content_type:animated_series
```

### Test Webhooks (Local Development)
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/voice-checkout/webhook/
```

---

## Revenue Split Implementation

The 70/30 split is calculated in `VoiceTransaction` creation:

```python
gross_price = voice.calculate_cost(text_length, duration_seconds)
platform_fee = (gross_price * Decimal('0.30')).quantize(Decimal('0.01'))
owner_payout = gross_price - platform_fee
```

**Example:**
- Voice: $0.50/minute
- Text: 500 chars (~3.3 minutes)
- Gross: $1.65
- Platform (30%): $0.50
- Creator (70%): $1.15

---

## What's Still Needed (Future Sessions)

1. **Stripe Connect** - Voice owners connect bank accounts for automatic payouts
2. **Payout Processing** - Automated weekly/monthly payouts to creators
3. **Earnings Dashboard** - Detailed analytics for voice sellers
4. **Purchase History** - Track what voices user has purchased
5. **Audio Delivery** - Generate and deliver audio after purchase

---

## Related Sessions

- **Session 440:** Voice Marketplace Models (VoiceProfile, VoiceTransaction)
- **Session 441-444:** Voice Cloning Pipeline
- **Session 438:** Stripe Subscription Service (reference implementation)
- **Session 449:** Learning Loops for AI Content Pipeline

---

## Golden Goose Strategy Progress

From the Golden Goose Strategy document:

| Pre-Market Checklist | Status |
|---------------------|--------|
| AISeriesWorkflowAgent | DONE (Sessions 445-448) |
| Learning Loops | DONE (Session 449) |
| Stripe Integration | **DONE (Session 450)** |
| User Video Upload | Pending |

**3 of 4 pre-market items complete!**
