# Session 507 - Narrative Drift Discord Commands

**Date:** December 19, 2025
**Previous Session:** 506 (Narrative Drift Detection Fix)
**Status:** COMPLETE

---

## Summary

Added 4 new Discord commands for comprehensive Narrative Drift monitoring, bringing the total narrative-related commands to 9. Also updated the NarrativeAlert model to support user-specific watch/subscription functionality.

---

## New Discord Commands

### 1. `/narrative-evidence <narrative_id> [limit]`
View evidence collected for a specific narrative.

**Parameters:**
- `narrative_id` (required): First 8 characters of the narrative UUID
- `limit` (optional): Number of evidence items to show (default: 10)

**Features:**
- Shows sentiment breakdown (supports/contradicts/neutral) with emoji indicators
- Displays confidence percentage
- Shows source URL snippets
- Timestamps for each evidence item

### 2. `/narrative-domains`
Get an overview of all narrative domains with statistics.

**Shows for each domain:**
- Total narratives and active count
- Shifts in last 24h and 7d
- Evidence collected in last 24h
- Fire emoji (🔥) indicator for domains with recent shifts

**Domains tracked:**
- 🏛️ Politics
- 📈 Markets
- 💻 Tech
- 🎭 Culture
- 🌍 Geopolitics
- ₿ Crypto
- 🌱 Climate
- 🏥 Health

### 3. `/narrative-watch <action> [narrative_id]`
Subscribe to alerts for specific narrative shifts.

**Actions:**
- `list` - Show your watched narratives and recent alerts
- `watch` - Start watching a narrative (requires narrative_id)
- `unwatch` - Stop watching a narrative (requires narrative_id)

**Features:**
- Creates subscription records in NarrativeAlert table
- Prevents duplicate subscriptions
- Shows unread alerts count

### 4. `/narrative-trending`
Show narratives that are currently shifting or have high activity.

**Shows:**
- Currently Shifting: Narratives with status='shifting'
- High Evidence Activity: Narratives with most evidence in last 24h
- Recent Shift Detections: Shifts detected in last 24h, ordered by confidence

---

## Database Changes

### NarrativeAlert Model Updates

**New Fields:**
```python
user_discord_id = models.CharField(max_length=100, blank=True, default='', db_index=True)
message = models.TextField(blank=True, default='')
is_read = models.BooleanField(default=False)
```

**Updated alert_type choices:**
```python
choices=[
    ('shift_detected', 'Narrative Shift Detected'),
    ('new_narrative', 'New Narrative Emerging'),
    ('narrative_dying', 'Narrative Fading'),
    ('contradictions', 'Contradictions Detected'),
    ('high_importance', 'High Importance Alert'),
    ('subscription', 'User Subscription'),  # NEW
]
```

**Migration:** `core/migrations/0115_session_507_narrative_alert_watch_fields.py`

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/discord_bot.py` | Added 4 new commands (~460 lines) in NarrativeCommands Cog |
| `core/models_narrative_drift.py` | Added user_discord_id, message, is_read fields + subscription type |
| `core/migrations/0115_session_507_narrative_alert_watch_fields.py` | New migration |
| `docs/handoffs/SESSION_506_NARRATIVE_DRIFT_FIX.md` | Updated with sentiment analyzer docs |
| `00-START-NEXT-SESSION.md` | Updated for Session 508 |

---

## All Narrative Drift Commands (9 Total)

| Command | Description | Session |
|---------|-------------|---------|
| `/narratives` | List tracked narratives | 471 |
| `/narrative-shifts` | List recent shifts | 471 |
| `/narrative-scan` | Run manual scan | 471 |
| `/narrative-seed` | Seed domain narratives | 471 |
| `/narrative-status` | System status | 471 |
| `/narrative-evidence` | View narrative evidence | **507** |
| `/narrative-domains` | Domain overview | **507** |
| `/narrative-watch` | Subscribe to alerts | **507** |
| `/narrative-trending` | Trending narratives | **507** |

---

## Technical Notes

### Watch Subscription Flow
1. User runs `/narrative-watch watch <id>`
2. Creates NarrativeAlert with `alert_type='subscription'` and `user_discord_id`
3. When narrative shifts, system can query subscriptions and notify users
4. User can list watches with `/narrative-watch list`
5. User can unsubscribe with `/narrative-watch unwatch <id>`

### Evidence Display
- Sentiment emojis: ✅ supports, ❌ contradicts, ➖ neutral
- Confidence shown as percentage
- Source URLs truncated to 30 chars
- Content snippets truncated to 80 chars

### Discord Command Limit Fix
Discord has a 100 command limit per guild. Adding 4 new narrative commands pushed us to 103 commands.

**Removed 4 low-usage commands:**
1. `/beep` - Voice test command
2. `/server-info` - Server config utility
3. `/brief-feedback` - Market Intelligence Brief rating
4. `/action` - Trading action tracking

**Result:** 99 commands (under limit), all commands syncing properly.

---

## Session 508 Ideas

1. Add automated Discord notifications when watched narratives shift
2. Consider Huggingface sentiment model for ML-based detection
3. Add more narratives to track across different domains
4. Create narrative comparison command
5. Add historical trend visualization
