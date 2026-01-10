# Option 2: Monetization Activation

**Priority:** 2 (Second)
**Status:** Not Started
**Estimated Effort:** Medium-High (3-4 sessions)

---

## Goal

Transform the platform from impressive technology into an active income generator by activating existing monetization infrastructure and creating clear revenue pathways.

---

## Problem Statement

The platform has extensive monetization infrastructure that's not actively generating revenue:
- Voice Marketplace exists but isn't promoted
- Content Studio creates content but doesn't auto-publish to revenue platforms
- Opportunities are scored but applications aren't tracked to revenue
- No subscription tiers leveraging the 19 autonomous situations
- No visibility into what's generating money

---

## Existing Infrastructure

| Component | Status | Gap |
|-----------|--------|-----|
| Voice Marketplace | Built | No promotion, discoverability low |
| Stripe Integration | Working | Subscriptions not tiered by features |
| Content Studio | Operational | No auto-publish to YouTube/platforms |
| Opportunity Scoring | Working | No application → revenue tracking |
| Discord Bot | 40+ commands | No premium command tiers |

---

## Deliverables

### 1. Voice Marketplace Activation

**Requirements:**
- [ ] Featured voices on homepage/landing
- [ ] Voice preview player (hear before you buy)
- [ ] Creator profiles with portfolios
- [ ] Voice categories (professional, character, accent, etc.)
- [ ] Search and discovery improvements
- [ ] Revenue split display (70/30)
- [ ] Payout tracking for creators
- [ ] Promotion via Discord (#voice-marketplace channel)

**Revenue Model:**
- Creator uploads voice → sets price ($5-$100)
- Buyer purchases → 70% to creator, 30% platform
- Recurring for subscription voices

---

### 2. Content Auto-Publishing Pipeline

**Requirements:**
- [ ] Connect Content Studio to YouTube API
- [ ] Connect to TikTok API (if available)
- [ ] Connect to Instagram API (Reels)
- [ ] Publish queue with scheduling
- [ ] Thumbnail auto-generation
- [ ] Description/tags from Content Studio metadata
- [ ] Analytics integration (track views, revenue)
- [ ] AdSense revenue tracking

**Revenue Model:**
- Platform creates content → auto-publishes
- Ad revenue tracked per video
- Potential for multi-channel network (MCN) approach

---

### 3. Opportunity-to-Revenue Pipeline

**Requirements:**
- [ ] Track when user applies to opportunity
- [ ] Follow-up system (did they get the job?)
- [ ] Revenue recording (what did they earn?)
- [ ] Success rate metrics
- [ ] Referral tracking (opportunity source)
- [ ] Revenue attribution to specific spiders/agents

**Data Model:**
```python
class OpportunityApplication(models.Model):
    opportunity = ForeignKey(Opportunity)
    user = ForeignKey(User)
    applied_at = DateTimeField
    status = CharField  # applied, interviewing, accepted, rejected
    outcome_recorded = BooleanField
    revenue_earned = DecimalField
    platform_fee = DecimalField  # if applicable
```

**Revenue Model:**
- Track user earnings from platform-found opportunities
- Optional: Success fee (% of first month's earnings)
- Affiliate revenue if opportunity has referral program

---

### 4. Subscription Tiers

**Requirements:**
- [ ] Define tier structure:
  - **Free:** Basic AI assistant, limited generations
  - **Creator ($19/mo):** Unlimited generations, Content Studio
  - **Pro ($49/mo):** All situations, Voice Marketplace selling
  - **Enterprise ($199/mo):** API access, custom situations
- [ ] Feature gating per tier
- [ ] Usage tracking and limits
- [ ] Upgrade prompts at appropriate moments
- [ ] Stripe subscription management
- [ ] Billing portal integration

**Implementation:**
```python
class SubscriptionTier(models.Model):
    TIERS = [
        ('free', 'Free'),
        ('creator', 'Creator'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    user = OneToOneField(User)
    tier = CharField(choices=TIERS)

    # Feature access
    autonomous_situations = JSONField  # list of enabled situations
    generation_limit = IntegerField  # per month, 0 = unlimited
    voice_marketplace_seller = BooleanField
    api_access = BooleanField
```

---

### 5. Revenue Dashboard

**Requirements:**
- [ ] Total revenue (all time, this month, today)
- [ ] Revenue by source:
  - Subscriptions
  - Voice Marketplace
  - Content Ad Revenue
  - Opportunity Success Fees
- [ ] Revenue trends (charts)
- [ ] Top earning voices/content
- [ ] Payout tracking (what's owed to creators)
- [ ] Export for accounting

**Visualizations:**
- Revenue over time (line chart)
- Revenue by source (pie chart)
- Top 10 revenue items (bar chart)
- MRR (Monthly Recurring Revenue) tracking

---

### 6. Discord Premium Commands

**Requirements:**
- [ ] Define which commands are premium:
  - Free: `/ask`, `/status`, `/gallery`
  - Creator: `/create`, `/research`, `/workflow-run`
  - Pro: `/agent-task`, `/consult`, `/studio-create`
  - Enterprise: `/api-key`, `/custom-situation`
- [ ] Tier checking before command execution
- [ ] Upgrade prompts for blocked commands
- [ ] Usage tracking per command

---

## Technical Implementation

### Backend Changes

#### New Models

```python
# core/models_monetization.py

class SubscriptionTier(models.Model):
    user = OneToOneField(User)
    tier = CharField
    stripe_subscription_id = CharField
    features = JSONField
    generation_count = IntegerField
    generation_limit = IntegerField

class RevenueEvent(models.Model):
    source = CharField  # subscription, voice, content, opportunity
    amount = DecimalField
    currency = CharField
    user = ForeignKey(User, null=True)
    metadata = JSONField
    created_at = DateTimeField

class OpportunityApplication(models.Model):
    opportunity = ForeignKey(Opportunity)
    user = ForeignKey(User)
    applied_at = DateTimeField
    status = CharField
    revenue_earned = DecimalField

class ContentRevenue(models.Model):
    episode = ForeignKey(ChannelEpisode)
    platform = CharField  # youtube, tiktok, instagram
    views = IntegerField
    ad_revenue = DecimalField
    date = DateField
```

#### New API Endpoints

```python
# Subscription Management
GET  /api/subscription/status/
POST /api/subscription/upgrade/
POST /api/subscription/cancel/
GET  /api/subscription/portal/

# Revenue Tracking
GET  /api/revenue/dashboard/
GET  /api/revenue/by-source/
GET  /api/revenue/export/
POST /api/revenue/record/

# Opportunity Tracking
POST /api/opportunities/<id>/apply/
PATCH /api/opportunities/<id>/application/
POST /api/opportunities/<id>/record-revenue/

# Voice Marketplace
GET  /api/voice-marketplace/featured/
GET  /api/voice-marketplace/categories/
GET  /api/voice-marketplace/my-earnings/
```

#### Stripe Webhook Updates

Enhance existing webhook handler:
```python
def handle_stripe_webhook(request):
    # Existing: subscription created/updated/cancelled
    # Add: invoice.paid → record revenue
    # Add: payout.paid → track creator payouts
```

---

### Frontend Changes

#### New Pages/Sections

1. **Pricing Page** - Tier comparison
2. **Revenue Dashboard** - Admin view of all revenue
3. **Creator Earnings** - Voice creators see their earnings
4. **Opportunity Tracker** - Users track applications
5. **Upgrade Modal** - Prompted when hitting limits

#### Voice Marketplace Enhancements

- Homepage featured section
- Category browsing
- Search with filters
- Voice preview player
- "Sell Your Voice" CTA

---

## Implementation Steps

### Phase 1: Subscription Tiers
1. [ ] Create SubscriptionTier model
2. [ ] Define tier features matrix
3. [ ] Implement feature gating
4. [ ] Create pricing page
5. [ ] Integrate with existing Stripe

### Phase 2: Revenue Tracking
1. [ ] Create RevenueEvent model
2. [ ] Add revenue recording on payments
3. [ ] Build revenue dashboard
4. [ ] Add export functionality

### Phase 3: Voice Marketplace Activation
1. [ ] Add featured voices section
2. [ ] Improve discovery/search
3. [ ] Add voice preview
4. [ ] Create creator earnings page
5. [ ] Promote in Discord

### Phase 4: Opportunity Pipeline
1. [ ] Create OpportunityApplication model
2. [ ] Add application tracking UI
3. [ ] Build follow-up system
4. [ ] Add revenue recording

### Phase 5: Content Revenue
1. [ ] YouTube API integration
2. [ ] Auto-publish from Content Studio
3. [ ] Track video performance
4. [ ] Record ad revenue

---

## Revenue Projections

| Source | Monthly Target | Notes |
|--------|----------------|-------|
| Subscriptions | $500 | 25 Creator + 5 Pro |
| Voice Marketplace | $200 | 20 sales @ $10 avg |
| Content Revenue | $100 | AdSense from auto-content |
| Opportunity Fees | $100 | 2 successful placements |
| **Total** | **$900** | Conservative first month |

---

## Success Criteria

1. **Subscriptions:** At least 10 paid users
2. **Voice Sales:** At least 5 voice purchases
3. **Revenue Visibility:** Dashboard shows all revenue sources
4. **Tracking:** Opportunity → revenue pipeline works end-to-end
5. **Auto-publish:** At least 1 video auto-published to YouTube

---

## Dependencies

- Existing Stripe integration (`core/services/stripe_*.py`)
- Existing Voice Marketplace models
- Content Studio (Option 1 dashboard helpful for monitoring)
- YouTube API credentials (need to obtain)

---

## Notes

- Start with subscriptions as quickest win
- Voice Marketplace already has infrastructure, just needs activation
- YouTube API has quota limits - be mindful
- Consider affiliate programs for opportunities (Adzuna, etc.)
