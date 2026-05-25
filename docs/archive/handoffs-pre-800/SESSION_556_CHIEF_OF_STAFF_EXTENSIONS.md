# Session 556: Chief of Staff Layer Extensions - Implementation Guide

**Date:** December 26, 2025
**Status:** PLANNING - Ready for Implementation
**Prerequisites:** Session 555 Chief of Staff Layer (Complete)

---

## Overview

This document outlines four extension options for the Chief of Staff Layer built in Session 555. Each option can be implemented independently or in combination.

### Extension Options

| Option | Name | Priority | Effort |
|--------|------|----------|--------|
| A | Discord Integration | HIGH | Medium |
| B | Boardroom UI Integration | HIGH | Medium |
| C | Auto-Review Generation | MEDIUM | Low |
| D | Dream Reviews | MEDIUM | Low |

---

## Option A: Discord Integration for Chief of Staff

### Purpose
Enable mobile decision-making via Discord bot commands. Users can review artifacts, interrogate Pro/Con sides, and make decisions from their phone.

### Discord Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/review <artifact_id>` | Show review document summary | `/review abc123` |
| `/review-list` | List pending reviews | `/review-list` |
| `/ask-pro <review_id> <question>` | Ask Pro side a question | `/ask-pro def456 What's the upside?` |
| `/ask-con <review_id> <question>` | Ask Con side a question | `/ask-con def456 What could go wrong?` |
| `/decide <review_id> <decision>` | Make decision | `/decide def456 approve` |

### Implementation Steps

#### Step 1: Add ReviewCommands Cog

Create new cog in `core/services/discord_bot.py`:

```python
class ReviewCommands(commands.Cog):
    """Discord commands for Chief of Staff review documents."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="review", description="Show review document for an artifact")
    @app_commands.describe(artifact_id="The artifact ID to review")
    async def review(self, interaction: discord.Interaction, artifact_id: str):
        """Display review document summary."""
        await interaction.response.defer()

        try:
            from core.services.review_document import review_service
            from core.models_conversation_artifacts import ExtractedArtifact

            # Get or create review
            review = review_service.get_or_create_for_artifact(artifact_id)

            # Build embed
            embed = discord.Embed(
                title=f"📋 Review: {review.target_type.title()}",
                color=self._get_lean_color(review.ai_lean),
                description=review.neutral_summary[:500]
            )

            # Add fields
            embed.add_field(
                name="✅ Pro Case",
                value=review.pro_case[:500] + "..." if len(review.pro_case) > 500 else review.pro_case,
                inline=False
            )
            embed.add_field(
                name="❌ Con Case",
                value=review.con_case[:500] + "..." if len(review.con_case) > 500 else review.con_case,
                inline=False
            )
            embed.add_field(
                name="🤖 AI Recommendation",
                value=f"**{review.ai_lean.replace('_', ' ').title()}** ({review.ai_confidence:.0%} confidence)\n{review.ai_recommendation[:300]}",
                inline=False
            )
            embed.add_field(
                name="❓ Open Questions",
                value="\n".join(f"• {q}" for q in review.open_questions[:5]) or "None",
                inline=False
            )

            # Add footer with commands
            embed.set_footer(text=f"Review ID: {review.id}\nUse /ask-pro or /ask-con to interrogate sides")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @app_commands.command(name="review-list", description="List pending review documents")
    async def review_list(self, interaction: discord.Interaction):
        """List all pending reviews."""
        await interaction.response.defer()

        try:
            from core.models_conversation_artifacts import ReviewDocument

            reviews = ReviewDocument.objects.filter(
                status='awaiting_human'
            ).order_by('-created_at')[:10]

            if not reviews:
                await interaction.followup.send("📭 No pending reviews")
                return

            embed = discord.Embed(
                title="📋 Pending Reviews",
                color=discord.Color.blue(),
                description=f"Found {reviews.count()} reviews awaiting decision"
            )

            for review in reviews:
                lean_emoji = self._get_lean_emoji(review.ai_lean)
                embed.add_field(
                    name=f"{lean_emoji} {review.target_type.title()}",
                    value=f"ID: `{str(review.id)[:8]}...`\nAI: {review.ai_lean} ({review.ai_confidence:.0%})\nQuestions: {review.questions_asked_pro + review.questions_asked_con}",
                    inline=True
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @app_commands.command(name="ask-pro", description="Ask the Pro side a question")
    @app_commands.describe(
        review_id="The review document ID",
        question="Your question for the Pro advocate"
    )
    async def ask_pro(self, interaction: discord.Interaction, review_id: str, question: str):
        """Ask Pro side a question."""
        await interaction.response.defer()

        try:
            from core.services.side_chat import side_chat_service
            from core.models_conversation_artifacts import ReviewDocument

            review = ReviewDocument.objects.get(id=review_id)
            result = side_chat_service.ask_side(review, 'pro', question)

            embed = discord.Embed(
                title="✅ Pro Advocate",
                color=discord.Color.green(),
                description=result['answer'][:2000]
            )
            embed.add_field(
                name="Your Question",
                value=question[:500],
                inline=False
            )
            embed.set_footer(text=f"Questions asked: Pro {review.questions_asked_pro} | Con {review.questions_asked_con}")

            await interaction.followup.send(embed=embed)

        except ReviewDocument.DoesNotExist:
            await interaction.followup.send("❌ Review not found")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @app_commands.command(name="ask-con", description="Ask the Con side a question")
    @app_commands.describe(
        review_id="The review document ID",
        question="Your question for the Con skeptic"
    )
    async def ask_con(self, interaction: discord.Interaction, review_id: str, question: str):
        """Ask Con side a question."""
        await interaction.response.defer()

        try:
            from core.services.side_chat import side_chat_service
            from core.models_conversation_artifacts import ReviewDocument

            review = ReviewDocument.objects.get(id=review_id)
            result = side_chat_service.ask_side(review, 'con', question)

            embed = discord.Embed(
                title="❌ Con Skeptic",
                color=discord.Color.red(),
                description=result['answer'][:2000]
            )
            embed.add_field(
                name="Your Question",
                value=question[:500],
                inline=False
            )
            embed.set_footer(text=f"Questions asked: Pro {review.questions_asked_pro} | Con {review.questions_asked_con}")

            await interaction.followup.send(embed=embed)

        except ReviewDocument.DoesNotExist:
            await interaction.followup.send("❌ Review not found")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @app_commands.command(name="decide", description="Make a decision on a review")
    @app_commands.describe(
        review_id="The review document ID",
        decision="Your decision",
        conditions="Optional conditions (for approve_with_conditions)"
    )
    @app_commands.choices(decision=[
        app_commands.Choice(name="Approve", value="approved"),
        app_commands.Choice(name="Approve with Conditions", value="approved_with_conditions"),
        app_commands.Choice(name="Decline", value="declined"),
        app_commands.Choice(name="Defer", value="deferred"),
    ])
    async def decide(
        self,
        interaction: discord.Interaction,
        review_id: str,
        decision: str,
        conditions: str = ""
    ):
        """Make a decision on a review document."""
        await interaction.response.defer()

        try:
            from django.utils import timezone
            from core.models_conversation_artifacts import ReviewDocument, ExtractedArtifact

            review = ReviewDocument.objects.get(id=review_id)

            # Update review document
            review.status = decision
            review.decision_conditions = conditions
            review.decided_at = timezone.now()
            review.save()

            # Cascade to artifact if applicable
            if review.target_type == 'artifact':
                try:
                    artifact = ExtractedArtifact.objects.get(id=review.target_id)
                    if decision in ['approved', 'approved_with_conditions']:
                        artifact.status = 'approved'
                    elif decision == 'declined':
                        artifact.status = 'rejected'
                    elif decision == 'deferred':
                        artifact.status = 'deferred'
                    artifact.save()
                except ExtractedArtifact.DoesNotExist:
                    pass

            # Send confirmation
            decision_emoji = {
                'approved': '✅',
                'approved_with_conditions': '⚠️',
                'declined': '❌',
                'deferred': '⏸️'
            }.get(decision, '📋')

            embed = discord.Embed(
                title=f"{decision_emoji} Decision Recorded",
                color=discord.Color.green() if 'approved' in decision else discord.Color.orange(),
                description=f"Review **{decision.replace('_', ' ').title()}**"
            )

            if conditions:
                embed.add_field(name="Conditions", value=conditions, inline=False)

            embed.set_footer(text=f"Review ID: {review.id}")

            await interaction.followup.send(embed=embed)

        except ReviewDocument.DoesNotExist:
            await interaction.followup.send("❌ Review not found")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    def _get_lean_color(self, lean: str) -> discord.Color:
        """Get color based on AI lean."""
        colors = {
            'strong_approve': discord.Color.green(),
            'lean_approve': discord.Color.dark_green(),
            'neutral': discord.Color.gold(),
            'lean_decline': discord.Color.orange(),
            'strong_decline': discord.Color.red(),
            'pilot': discord.Color.blue(),
            'defer': discord.Color.greyple(),
        }
        return colors.get(lean, discord.Color.blue())

    def _get_lean_emoji(self, lean: str) -> str:
        """Get emoji based on AI lean."""
        emojis = {
            'strong_approve': '🟢',
            'lean_approve': '🟡',
            'neutral': '⚪',
            'lean_decline': '🟠',
            'strong_decline': '🔴',
            'pilot': '🔵',
            'defer': '⏸️',
        }
        return emojis.get(lean, '📋')
```

#### Step 2: Register the Cog

In `core/services/discord_bot.py`, add to `setup_hook`:

```python
async def setup_hook(self):
    # ... existing cogs ...
    await self.add_cog(ReviewCommands(self))
```

#### Step 3: Add Notification on New Reviews

Post to `#boardroom` when review documents are generated:

```python
# In core/services/review_document.py, after generating review:
async def _notify_discord(self, review_doc):
    from core.services.discord_notifications import DiscordNotificationService

    service = DiscordNotificationService()
    await service.send_to_channel(
        channel_name='boardroom',
        embed={
            'title': '📋 New Review Awaiting Decision',
            'description': review_doc.neutral_summary[:500],
            'color': 0x3498db,
            'fields': [
                {'name': 'AI Lean', 'value': review_doc.ai_lean, 'inline': True},
                {'name': 'Confidence', 'value': f'{review_doc.ai_confidence:.0%}', 'inline': True},
            ],
            'footer': {'text': f'Use /review {review_doc.id} to view details'}
        }
    )
```

### Files to Modify

| File | Changes |
|------|---------|
| `core/services/discord_bot.py` | Add ReviewCommands cog (~200 lines) |
| `core/services/review_document.py` | Add Discord notification (~20 lines) |

### Estimated Effort: 3-4 hours

---

## Option B: Boardroom UI Integration

### Purpose
Display review documents in the web UI Boardroom tab, allowing users to review artifacts, ask Pro/Con questions, and make decisions with a visual interface.

### UI Design

```
┌─────────────────────────────────────────────────────────────────┐
│ BOARDROOM                                              [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│ [Dreams Tab] [Reviews Tab] [Decisions Tab]                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📋 PENDING REVIEWS (3)                                       │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │                                                              │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ 🔵 Discord Content Scheduling                           │ │ │
│ │ │ AI: Pilot (68%)                                         │ │ │
│ │ │ "This proposal suggests automating Discord content..."  │ │ │
│ │ │                                                         │ │ │
│ │ │ [View Details] [Ask Pro 💬] [Ask Con 💬]                │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │                                                              │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ 🟢 API Rate Limiting Strategy                           │ │ │
│ │ │ AI: Strong Approve (85%)                                │ │ │
│ │ │ "Implement rate limiting to prevent abuse..."           │ │ │
│ │ │                                                         │ │ │
│ │ │ [View Details] [Ask Pro 💬] [Ask Con 💬]                │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │                                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Expanded Review View

```
┌─────────────────────────────────────────────────────────────────┐
│ REVIEW: Discord Content Scheduling                    [← Back]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ NEUTRAL SUMMARY                                                  │
│ ─────────────────────────────────────────────────────────────── │
│ This proposal suggests implementing automated content           │
│ scheduling for Discord channels based on performance data...    │
│                                                                  │
├─────────────────────────────────┬───────────────────────────────┤
│ ✅ PRO CASE                     │ ❌ CON CASE                    │
│ ─────────────────────────────── │ ─────────────────────────────  │
│ • Increases engagement by 40%   │ • Risk of content fatigue      │
│ • Saves 5 hours/week            │ • May feel inauthentic         │
│ • Data-driven optimization      │ • Algorithm changes risk       │
│                                 │                                │
│ [Ask Pro 💬]                    │ [Ask Con 💬]                   │
├─────────────────────────────────┴───────────────────────────────┤
│                                                                  │
│ 🤖 AI RECOMMENDATION                                             │
│ ─────────────────────────────────────────────────────────────── │
│ Lean: PILOT (68% confidence)                                    │
│ Consider a narrow pilot with 2 channels first to validate       │
│ engagement assumptions before full rollout...                   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ ❓ OPEN QUESTIONS                                                │
│ • What's the rollback plan if engagement drops?                 │
│ • How will we measure authenticity perception?                  │
│ • What's the minimum viable pilot scope?                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [✅ Approve] [⚠️ Approve with Conditions] [❌ Decline] [⏸️ Defer]│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Side Chat Modal

```
┌─────────────────────────────────────────────────────────────────┐
│ 💬 Ask Pro Advocate                                      [X]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ You: What if engagement actually drops?                     │ │
│ │                                                              │ │
│ │ Pro: Even in a scenario where initial engagement dips,      │ │
│ │ the long-term data shows that consistent, optimized         │ │
│ │ scheduling leads to 40% higher retention. The key is...     │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ You: How confident are you in those numbers?                │ │
│ │                                                              │ │
│ │ Pro: The data comes from 3 case studies of similar          │ │
│ │ communities. While every community is unique...             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Ask a question...                                    [Send] │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Questions asked: 2 of 5 (before reminder)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Add Reviews Sub-Tab to Boardroom

In `ai_core/templates/ai_image_studio.html`, add new sub-tab:

```html
<!-- In Boardroom tab content -->
<div class="boardroom-subtabs">
    <button class="subtab-btn active" data-subtab="dreams">Dreams</button>
    <button class="subtab-btn" data-subtab="reviews">Reviews</button>
    <button class="subtab-btn" data-subtab="decisions">Decisions</button>
</div>

<div id="reviews-subtab" class="subtab-content" style="display: none;">
    <div class="reviews-header">
        <h3>📋 Pending Reviews</h3>
        <button onclick="refreshReviews()" class="refresh-btn">Refresh</button>
    </div>
    <div id="reviews-list" class="reviews-grid">
        <!-- Populated via JavaScript -->
    </div>
</div>
```

#### Step 2: Add JavaScript Functions

```javascript
// Fetch and display reviews
async function loadReviews() {
    try {
        const response = await fetch('/api/reviews/?status=awaiting_human');
        const data = await response.json();

        if (data.success) {
            renderReviewsList(data.reviews);
        }
    } catch (error) {
        console.error('Error loading reviews:', error);
    }
}

function renderReviewsList(reviews) {
    const container = document.getElementById('reviews-list');

    if (reviews.length === 0) {
        container.innerHTML = '<div class="empty-state">No pending reviews</div>';
        return;
    }

    container.innerHTML = reviews.map(review => `
        <div class="review-card" data-review-id="${review.id}">
            <div class="review-header">
                <span class="lean-badge ${review.ai_lean}">${getLeanEmoji(review.ai_lean)}</span>
                <span class="review-type">${review.target_type}</span>
            </div>
            <div class="review-summary">${review.neutral_summary}</div>
            <div class="review-meta">
                AI: ${formatLean(review.ai_lean)} (${Math.round(review.ai_confidence * 100)}%)
            </div>
            <div class="review-actions">
                <button onclick="viewReviewDetails('${review.id}')" class="btn-secondary">View Details</button>
                <button onclick="openSideChat('${review.id}', 'pro')" class="btn-pro">Ask Pro 💬</button>
                <button onclick="openSideChat('${review.id}', 'con')" class="btn-con">Ask Con 💬</button>
            </div>
        </div>
    `).join('');
}

// Side chat modal
async function openSideChat(reviewId, side) {
    const modal = document.getElementById('side-chat-modal');
    modal.dataset.reviewId = reviewId;
    modal.dataset.side = side;

    // Load existing chat history
    const response = await fetch(`/api/reviews/${reviewId}/`);
    const data = await response.json();

    const history = side === 'pro' ? data.review.pro_chat_history : data.review.con_chat_history;
    renderChatHistory(history);

    modal.style.display = 'flex';
    document.getElementById('side-chat-title').textContent =
        side === 'pro' ? '✅ Ask Pro Advocate' : '❌ Ask Con Skeptic';
}

async function sendSideChatMessage() {
    const modal = document.getElementById('side-chat-modal');
    const reviewId = modal.dataset.reviewId;
    const side = modal.dataset.side;
    const input = document.getElementById('side-chat-input');
    const question = input.value.trim();

    if (!question) return;

    // Add user message to UI
    appendChatMessage('user', question);
    input.value = '';

    // Send to API
    const endpoint = `/api/reviews/${reviewId}/ask-${side}/`;
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
    });

    const data = await response.json();

    if (data.success) {
        appendChatMessage('assistant', data.answer);
        updateQuestionCounter(data.total_questions);
    }
}

// Decision modal
async function makeDecision(reviewId, decision) {
    const conditions = decision === 'approved_with_conditions'
        ? prompt('Enter conditions:')
        : '';

    const reasoning = prompt('Optional: Enter your reasoning');

    const response = await fetch(`/api/reviews/${reviewId}/decide/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({decision, conditions, reasoning})
    });

    const data = await response.json();

    if (data.success) {
        showNotification(`Decision recorded: ${decision}`);
        loadReviews(); // Refresh list
    }
}
```

#### Step 3: Add CSS Styles

```css
/* Review cards */
.reviews-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
}

.review-card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: 1rem;
    border-left: 4px solid var(--accent);
}

.review-card[data-lean="strong_approve"] { border-left-color: #22c55e; }
.review-card[data-lean="lean_approve"] { border-left-color: #84cc16; }
.review-card[data-lean="neutral"] { border-left-color: #eab308; }
.review-card[data-lean="lean_decline"] { border-left-color: #f97316; }
.review-card[data-lean="strong_decline"] { border-left-color: #ef4444; }
.review-card[data-lean="pilot"] { border-left-color: #3b82f6; }
.review-card[data-lean="defer"] { border-left-color: #6b7280; }

/* Side chat modal */
.side-chat-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.side-chat-content {
    background: var(--card-bg);
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
}

.chat-input-area {
    padding: 1rem;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 0.5rem;
}

/* Decision buttons */
.decision-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    padding: 1rem;
}

.btn-approve { background: #22c55e; color: white; }
.btn-conditions { background: #f59e0b; color: white; }
.btn-decline { background: #ef4444; color: white; }
.btn-defer { background: #6b7280; color: white; }
```

### Files to Modify

| File | Changes |
|------|---------|
| `ai_core/templates/ai_image_studio.html` | Add Reviews sub-tab HTML (~100 lines) |
| `ai_core/static/js/ai_studio.js` | Add JavaScript functions (~200 lines) |
| `ai_core/static/css/ai_studio.css` | Add CSS styles (~100 lines) |

### Estimated Effort: 4-5 hours

---

## Option C: Auto-Review Generation

### Purpose
Automatically generate review documents for high-priority artifacts that have been pending for too long, ensuring nothing falls through the cracks.

### Trigger Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| High composite score | >= 0.7 | Generate review immediately |
| Pending duration | > 24 hours | Generate review and notify |
| Urgency score | >= 0.8 | Generate review within 1 hour |

### Implementation Steps

#### Step 1: Add Celery Task

In `core/tasks.py`:

```python
@shared_task(bind=True, name='generate_pending_reviews')
def generate_pending_reviews(self):
    """
    Auto-generate review documents for pending artifacts.

    Runs hourly via Celery Beat.
    Targets:
    - High-priority artifacts (composite_score >= 0.7)
    - Artifacts pending > 24 hours
    - Urgent artifacts (urgency_score >= 0.8)
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_conversation_artifacts import ExtractedArtifact, ReviewDocument
    from core.services.review_document import review_service
    from core.services.discord_notifications import DiscordNotificationService

    logger.info("Starting auto-review generation scan...")

    now = timezone.now()
    generated_count = 0

    # Find artifacts needing reviews
    pending_artifacts = ExtractedArtifact.objects.filter(
        status='pending'
    ).exclude(
        id__in=ReviewDocument.objects.filter(
            target_type='artifact'
        ).values_list('target_id', flat=True)
    )

    for artifact in pending_artifacts:
        should_generate = False
        reason = ""

        # Check high priority
        if artifact.composite_score >= 0.7:
            should_generate = True
            reason = f"High priority (score: {artifact.composite_score:.2f})"

        # Check pending duration
        elif now - artifact.created_at > timedelta(hours=24):
            should_generate = True
            reason = f"Pending > 24h (since {artifact.created_at})"

        # Check urgency
        elif artifact.urgency_score >= 0.8:
            should_generate = True
            reason = f"Urgent (urgency: {artifact.urgency_score:.2f})"

        if should_generate:
            try:
                logger.info(f"Generating review for artifact {artifact.id}: {reason}")
                review = review_service.generate_review_document(artifact)
                generated_count += 1

                # Notify Discord
                discord_service = DiscordNotificationService()
                discord_service.send_embed(
                    channel_name='boardroom',
                    title='📋 Auto-Generated Review',
                    description=f"**{artifact.title}**\n\n{review.neutral_summary[:300]}",
                    color=0x3498db,
                    fields=[
                        {'name': 'Reason', 'value': reason, 'inline': True},
                        {'name': 'AI Lean', 'value': review.ai_lean, 'inline': True},
                        {'name': 'Confidence', 'value': f'{review.ai_confidence:.0%}', 'inline': True},
                    ],
                    footer=f'Use /review {review.id} to respond'
                )

            except Exception as e:
                logger.error(f"Failed to generate review for {artifact.id}: {e}")

    logger.info(f"Auto-review generation complete: {generated_count} reviews generated")

    return {
        'generated': generated_count,
        'scanned': pending_artifacts.count()
    }
```

#### Step 2: Add Celery Beat Schedule

In `core/celery.py`:

```python
app.conf.beat_schedule.update({
    'generate-pending-reviews': {
        'task': 'generate_pending_reviews',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'queue': 'default'},
    },
})
```

#### Step 3: Add Manual Trigger Endpoint

In `core/views_artifacts.py`:

```python
@csrf_exempt
@require_http_methods(["POST"])
def trigger_auto_reviews(request):
    """
    Manually trigger auto-review generation.

    POST /api/artifacts/trigger-auto-reviews/
    """
    try:
        from core.tasks import generate_pending_reviews

        result = generate_pending_reviews.delay()

        return JsonResponse({
            'success': True,
            'task_id': str(result.id),
            'message': 'Auto-review generation triggered'
        })
    except Exception as e:
        logger.error(f"Error triggering auto-reviews: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
```

### Files to Modify

| File | Changes |
|------|---------|
| `core/tasks.py` | Add generate_pending_reviews task (~80 lines) |
| `core/celery.py` | Add beat schedule (~5 lines) |
| `core/views_artifacts.py` | Add trigger endpoint (~20 lines) |
| `core/urls.py` | Add URL route (~2 lines) |

### Estimated Effort: 2-3 hours

---

## Option D: Dream Reviews

### Purpose
Extend the ReviewDocument system to work with AgentDream approvals, enabling the same Pro/Con interrogation workflow for dream investment decisions.

### Why This Works

The ReviewDocument model is already polymorphic with `target_type` supporting 'dream':

```python
target_type = models.CharField(max_length=50, choices=[
    ('artifact', 'Extracted Artifact'),
    ('dream', 'Agent Dream'),        # Already supported!
    ('project', 'Creative Project'),
    ('decision', 'Agent Decision'),
    ('experiment', 'Experiment'),
])
```

### Implementation Steps

#### Step 1: Add Dream Review Generation

In `core/services/review_document.py`:

```python
def generate_dream_review(self, dream) -> 'ReviewDocument':
    """
    Generate a review document for an AgentDream.

    Args:
        dream: AgentDream instance

    Returns:
        ReviewDocument: The generated review document
    """
    from core.models_conversation_artifacts import ReviewDocument, SideChat

    logger.info(f"Generating review document for dream: {dream.title[:50]}")

    # Gather dream context
    context = self._gather_dream_context(dream)

    # Generate analysis
    analysis = self._generate_dream_analysis(dream, context)

    # Create ReviewDocument
    with transaction.atomic():
        review_doc = ReviewDocument.objects.create(
            target_type='dream',
            target_id=dream.id,
            neutral_summary=analysis.get('neutral_summary', 'Summary not available'),
            pro_case=analysis.get('pro_case', 'Pro case not available'),
            con_case=analysis.get('con_case', 'Con case not available'),
            open_questions=analysis.get('open_questions', []),
            key_evidence=analysis.get('key_evidence', {'pro': [], 'con': []}),
            ai_recommendation=analysis.get('ai_recommendation', 'No recommendation'),
            ai_lean=analysis.get('ai_lean', 'neutral'),
            ai_confidence=float(analysis.get('ai_confidence', 0.5)),
            status='awaiting_human',
        )

        # Create side chats
        SideChat.objects.create(review_document=review_doc, side='pro')
        SideChat.objects.create(review_document=review_doc, side='con')

    logger.info(f"Dream review created: {review_doc.id}")
    return review_doc

def _gather_dream_context(self, dream) -> Dict[str, Any]:
    """Gather context from an AgentDream."""
    return {
        'dream_type': 'Agent Dream',
        'title': dream.title,
        'description': dream.description,
        'dream_content': dream.content,
        'impact_assessment': dream.impact_assessment,
        'resource_requirements': dream.resource_requirements,
        'priority': dream.priority,
        'source_agent': dream.agent.name if dream.agent else None,
        'created_at': dream.created_at.isoformat(),
    }

def _generate_dream_analysis(self, dream, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analysis for a dream."""

    prompt = f"""Analyze this Agent Dream for human review and provide a balanced assessment.

DREAM:
Title: {context['title']}
Description: {context['description']}
Content: {context['dream_content'][:1000]}

Impact Assessment: {context.get('impact_assessment', 'Not provided')}
Resource Requirements: {context.get('resource_requirements', 'Not specified')}
Priority: {context.get('priority', 'Unknown')}
Dreaming Agent: {context.get('source_agent', 'Unknown')}

TASK: Provide a balanced decision brief in JSON format with:

1. "neutral_summary": 2-3 sentence objective summary of what this dream proposes
2. "pro_case": 3-5 bullet points arguing FOR investing in this dream
3. "con_case": 3-5 bullet points arguing AGAINST or highlighting risks
4. "open_questions": List of 2-4 questions to resolve before committing
5. "key_evidence": {{"pro": [...supporting points], "con": [...concerning points]}}
6. "ai_recommendation": 2-3 sentence recommendation
7. "ai_lean": One of: strong_approve, lean_approve, neutral, lean_decline, strong_decline, pilot, defer
8. "ai_confidence": Float 0-1

Consider: Is this dream actionable? Does it align with platform goals? What's the ROI?"""

    try:
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an objective analyst evaluating Agent Dreams for investment. "
                        "Be balanced, consider resource implications, and provide actionable insights."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Validate
        valid_leans = ['strong_approve', 'lean_approve', 'neutral', 'lean_decline', 'strong_decline', 'pilot', 'defer']
        if result.get('ai_lean') not in valid_leans:
            result['ai_lean'] = 'neutral'

        result['ai_confidence'] = max(0.0, min(1.0, float(result.get('ai_confidence', 0.5))))

        return result

    except Exception as e:
        logger.error(f"Failed to generate dream analysis: {e}")
        return self._fallback_dream_analysis(context)

def _fallback_dream_analysis(self, context: Dict) -> Dict:
    """Fallback analysis if API fails."""
    return {
        'neutral_summary': f"Dream from {context.get('source_agent', 'an agent')}: {context['title']}",
        'pro_case': "- Agent has identified an opportunity\n- Could advance platform capabilities",
        'con_case': "- Requires investment\n- May have opportunity costs",
        'open_questions': ["What resources are needed?", "What's the timeline?"],
        'key_evidence': {'pro': ['Agent proposal'], 'con': ['Needs evaluation']},
        'ai_recommendation': "Review the dream details and consider platform priorities.",
        'ai_lean': 'neutral',
        'ai_confidence': 0.3,
    }
```

#### Step 2: Add API Endpoint

In `core/views_artifacts.py`:

```python
@csrf_exempt
@require_http_methods(["POST"])
def generate_review_for_dream(request, dream_id):
    """
    Generate a review document for an AgentDream.

    POST /api/dreams/<uuid>/generate-review/
    """
    try:
        from core.models_unified_system import AgentDream
        from core.services.review_document import review_service
        from core.models_conversation_artifacts import ReviewDocument

        # Check for existing review
        try:
            existing = ReviewDocument.objects.get(
                target_type='dream',
                target_id=dream_id
            )
            return JsonResponse({
                'success': True,
                'review': _serialize_review(existing, full=True),
                'message': 'Existing review found'
            })
        except ReviewDocument.DoesNotExist:
            pass

        # Generate new review
        dream = AgentDream.objects.get(id=dream_id)
        review = review_service.generate_dream_review(dream)

        return JsonResponse({
            'success': True,
            'review': _serialize_review(review, full=True),
            'message': 'Dream review document generated'
        })
    except AgentDream.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Dream not found'}, status=404)
    except Exception as e:
        logger.error(f"Error generating dream review for {dream_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
```

#### Step 3: Add URL Route

In `core/urls.py`:

```python
path('api/dreams/<uuid:dream_id>/generate-review/', views_artifacts.generate_review_for_dream, name='api_generate_dream_review'),
```

#### Step 4: Update Side Chat Context

In `core/services/side_chat.py`, update `_build_context`:

```python
def _build_context(self, review_doc, side: str) -> str:
    """Build context string from review document."""
    from core.models_conversation_artifacts import ExtractedArtifact
    from core.models_unified_system import AgentDream

    target_context = ""

    if review_doc.target_type == 'artifact':
        try:
            artifact = ExtractedArtifact.objects.get(id=review_doc.target_id)
            target_context = f"""
ARTIFACT DETAILS:
- Type: {artifact.get_artifact_type_display()}
- Title: {artifact.title}
- Description: {artifact.description}
- Importance: {artifact.importance_score:.2f}
- Urgency: {artifact.urgency_score:.2f}
"""
        except ExtractedArtifact.DoesNotExist:
            target_context = "ARTIFACT: Details not available"

    elif review_doc.target_type == 'dream':
        try:
            dream = AgentDream.objects.get(id=review_doc.target_id)
            target_context = f"""
DREAM DETAILS:
- Title: {dream.title}
- Description: {dream.description}
- Agent: {dream.agent.name if dream.agent else 'Unknown'}
- Priority: {dream.priority}
- Content Preview: {dream.content[:500]}...
"""
        except AgentDream.DoesNotExist:
            target_context = "DREAM: Details not available"

    # ... rest of context building
```

### Files to Modify

| File | Changes |
|------|---------|
| `core/services/review_document.py` | Add dream review methods (~150 lines) |
| `core/services/side_chat.py` | Update context building (~30 lines) |
| `core/views_artifacts.py` | Add dream review endpoint (~40 lines) |
| `core/urls.py` | Add URL route (~2 lines) |

### Estimated Effort: 2-3 hours

---

## Implementation Order Recommendation

| Order | Option | Reason |
|-------|--------|--------|
| 1 | **C: Auto-Review** | Lowest effort, immediate value, generates test data |
| 2 | **D: Dream Reviews** | Low effort, extends existing system naturally |
| 3 | **A: Discord** | Medium effort, high mobile utility |
| 4 | **B: Boardroom UI** | Highest effort, best full experience |

### Combined Effort Estimate

| Option | Hours | Priority |
|--------|-------|----------|
| A: Discord | 3-4 | HIGH |
| B: Boardroom UI | 4-5 | HIGH |
| C: Auto-Review | 2-3 | MEDIUM |
| D: Dream Reviews | 2-3 | MEDIUM |
| **Total** | **11-15** | - |

---

## Testing Checklist

### Option A: Discord
- [ ] `/review <id>` shows review summary embed
- [ ] `/review-list` shows pending reviews
- [ ] `/ask-pro` returns Pro perspective response
- [ ] `/ask-con` returns Con perspective response
- [ ] `/decide approve` updates review and artifact
- [ ] Discord notification on new reviews

### Option B: Boardroom UI
- [ ] Reviews sub-tab loads pending reviews
- [ ] Review card shows summary and AI lean
- [ ] Expanded view shows full pro/con cases
- [ ] Side chat modal opens and loads history
- [ ] Side chat messages send and receive
- [ ] Decision buttons update status
- [ ] List refreshes after decision

### Option C: Auto-Review
- [ ] Celery Beat triggers hourly
- [ ] High-priority artifacts get reviews
- [ ] 24h+ pending artifacts get reviews
- [ ] Discord notification on auto-generation
- [ ] Manual trigger endpoint works

### Option D: Dream Reviews
- [ ] Generate review for dream works
- [ ] Side chats have dream context
- [ ] Ask Pro/Con work for dreams
- [ ] Decision updates dream status

---

## Future Enhancements (Beyond Session 556)

1. **Email Notifications** - "3 reviews awaiting your decision"
2. **Review Templates** - Pre-defined questions for common artifact types
3. **Bulk Decisions** - Approve/decline multiple similar items
4. **Review Analytics** - Track decision patterns, time-to-decision
5. **Escalation Rules** - Auto-escalate if pending > 48h
6. **Review Delegation** - Assign reviews to specific team members

---

*Generated: December 26, 2025*
*Session 556 Chief of Staff Extensions - Planning Document*
