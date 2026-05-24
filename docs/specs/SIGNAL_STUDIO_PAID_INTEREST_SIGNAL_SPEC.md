---
title: "Signal Studio — paid-interest signal affordance (spec)"
status: draft
created: 2026-05-24
session: 1137
audience: Chris (implementation) + Jessica (sign-off)
related:
  - SESSION_1137 Decision 13 (legal review demand-gate)
  - SESSION_1137 Decision 10 (Stripe SKU sequencing, Signal Studio first)
  - docs/apps/signal_studio_BRIEF.md
---

# Signal Studio — paid-interest signal affordance

> **Why this exists.** Session 1137 Decision 13 demand-gated Signal Studio's
> $2K legal review on a "concrete paying-interest signal" surfacing. Without
> a mechanism for users to express that interest, the trigger can never fire
> — and Signal Studio can never launch paid. This spec defines the minimal
> affordance that makes the demand-gate workable.

## Goal

Give Signal Studio's free-tier / demo-tier users a way to opt in to "notify
me when the paid version launches," capturing enough signal that Jessica can
make the legal-review trigger decision.

## Non-goals

- Full waitlist with priority queueing, referral mechanics, or gamification.
- Email marketing automation (welcome sequences, drip campaigns).
- Public counter (e.g. "1,247 people on the waitlist") — marketing-led,
  premature for this volume.
- Charging anything pre-trigger.

## Trigger condition (when the demand-gate fires)

Per Decision 13, the legal review (capped $2K) deploys when **EITHER**:

1. **≥ 5 unique users** submit the paid-interest form within any rolling
   90-day window, OR
2. **≥ 1 user submits the paid-interest form including the optional "what
   would you pay?" field with a value ≥ Pro tier price ($49/mo)**, OR
3. **Jessica overrides** based on outreach signal (named lead, partnership
   conversation, etc.) — manual unlock.

The numbers in (1) and (2) are deliberately small because Signal Studio is
pre-revenue. Tune up after first launch.

## Affordance shape (UI)

### Where it lives
- Footer of every Signal Studio page (sticky banner option for first-time
  visitors; dismissible).
- Inside the product, on any LLM-backed feature that requires a paid tier:
  *"This feature needs the paid version. Notify me when it launches →"*

### What the form captures
| Field | Required | Why |
|---|---|---|
| Email address | yes | The notify mechanism |
| Use case (short text, ≤140 chars) | yes | Demand-quality signal |
| "What would you pay per month if it launched today?" | optional | Tier-validation signal; triggers condition (2) |
| Workspace size (Solo / 2-5 / 6-20 / 20+) | optional | Sizing signal |

### What happens on submit
1. Persist row to `signal_studio_paid_interest` table (new — schema below).
2. Show confirmation: *"Got it. We'll email you at the launch."*
3. No automated follow-up email until launch — manual outreach allowed.

## Backend (Chris implementation)

### New table
```sql
CREATE TABLE signal_studio_paid_interest (
    id            UUID PRIMARY KEY,
    email         TEXT NOT NULL,
    use_case      TEXT NOT NULL,
    willing_pay   INT,                -- monthly $ they'd pay; NULL if blank
    workspace     TEXT,               -- "solo" | "2-5" | "6-20" | "20+" | NULL
    user_id       UUID,               -- if signed-in, link to user
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at   TIMESTAMPTZ         -- set when launch email sent
);
CREATE INDEX ON signal_studio_paid_interest (created_at);
CREATE INDEX ON signal_studio_paid_interest (email);
```

### New endpoint
```
POST /api/signal-studio/paid-interest
  body: { email, use_case, willing_pay?, workspace? }
  response: { id, message: "captured" }
```

- Rate-limit: 3 submissions per IP per hour (anti-spam).
- Email dedup: same email + same use_case within 7 days = no-op (return
  existing id).
- No auth required (free-tier users may not be signed in).

### Trigger detection (Jessica-facing)

A simple PA tool (Rigby-callable) or admin page that returns:

```
{
  total_signals: <count>,
  last_90d_signals: <count>,
  has_high_value_signal: <bool>,   // condition (2)
  trigger_state: "not_yet" | "ready" | "manually_overridden"
}
```

Jessica checks this weekly. When it flips to `ready`, the legal review
spend trigger from Decision 13 activates.

## Honest claims (per UDB_TRANSLATION_LAYER §2)

What this UI promises:
- We **will** email you when Signal Studio paid launches.
- We **may** reach out individually if your use case is interesting.

What this UI does **NOT** promise:
- A specific launch date.
- A discount or early-access deal.
- That paid will ever launch (if Decision 13 unlocks but go-to-market
  signal doesn't, Signal Studio stays free-tier indefinitely).

## Phase 5 follow-up items

1. **Jessica:** decide the "trigger checked weekly" rhythm and where
   trigger-state lives (Rigby chat? Dashboard? Email digest?).
2. **Chris:** implement endpoint + table + simple admin view (≤1 day).
3. **Jessica:** draft the form UI copy (use-case prompt question, button
   label).
4. **Chris:** add the affordance to Signal Studio frontend (≤½ day).
5. **Either:** announce on Signal Studio's existing comms (if any) once
   the form is live.

## Estimated effort

- Backend (Chris): ½ day (table + endpoint + 1 admin query).
- Frontend (Chris): ½ day (form widget, submit handler, confirmation state).
- Copy (Jessica): 30 min.
- **Total to make Decision 13 trigger workable: ~1.5 days of work.**

## Acceptance criteria

- [ ] Free-tier Signal Studio user can submit paid interest from the footer.
- [ ] Paywalled feature attempts show the same form inline with feature
      context.
- [ ] Row persists to `signal_studio_paid_interest` table.
- [ ] Rate-limit + dedup prevent obvious spam.
- [ ] Trigger-state query returns one of three states.
- [ ] No email is sent on submit (manual outreach only pre-launch).
- [ ] Trigger-state visible to Jessica via Rigby chat or admin page.
