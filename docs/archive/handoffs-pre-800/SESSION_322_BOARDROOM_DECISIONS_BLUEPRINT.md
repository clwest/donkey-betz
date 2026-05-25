# Session 322: Boardroom Decisions Blueprint

**Date:** December 2, 2025
**Status:** Planning Complete - Ready for Implementation
**Priority:** High - Closes the Agent Intelligence Loop
**Estimated Phases:** 3 (can be done incrementally)

---

## Executive Summary

Agent conversations are generating valuable governance artifacts (policies, architecture decisions, pipeline specs) but these insights currently evaporate after the conversation ends. This blueprint outlines how to:

1. **Capture** decision summaries from conversations
2. **Display** them in a Boardroom Decisions UI
3. **Promote** important decisions to canonical policies
4. **Feed** policies back to agents to influence future behavior

This transforms agent conversations from "interesting chatter" into a **self-improving governance system**.

---

## Current State

### What We Have
- `AgentConversation` model with `conclusion` text field
- Conversations generate quality discussions (verified in Session 322)
- Examples of valuable outputs:
  - Prompt Engineering Policy (BookmakerAgent + CTOAgent)
  - Memory Isolation Architecture (MemoryIsolationAgent + CreationAgent)
  - Image Pipeline Spec (ImageEditingAgent + CreativeDirectorAgent)

### What's Missing
- Structured extraction of decisions from conclusions
- Persistent storage of decision summaries
- UI to view/manage decisions
- Feedback loop to inject policies into agent context

---

## Phase 1: Data Model + Extraction

### 1.1 Create AgentDecisionSummary Model

**File:** `core/models.py` (or `core/models_unified_system.py`)

```python
class AgentDecisionSummary(models.Model):
    """
    Structured decision extracted from agent conversations.
    These can be promoted to canonical policies that affect future agent behavior.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to source conversation
    conversation = models.ForeignKey(
        'AgentConversation',
        on_delete=models.CASCADE,
        related_name='decisions'
    )

    # Decision metadata
    topic = models.CharField(max_length=255)
    decision_type = models.CharField(
        max_length=50,
        choices=[
            ('policy', 'Policy'),
            ('architecture', 'Architecture'),
            ('pipeline', 'Pipeline'),
            ('product', 'Product Feature'),
            ('experiment', 'Experiment'),
            ('guideline', 'Guideline'),
        ]
    )
    impact_area = models.CharField(
        max_length=50,
        choices=[
            ('prompting', 'Prompt Engineering'),
            ('memory', 'Memory & Storage'),
            ('image', 'Image Generation'),
            ('video', 'Video Generation'),
            ('audio', 'Audio Generation'),
            ('workflow', 'Workflows'),
            ('agents', 'Agent Behavior'),
            ('security', 'Security & Privacy'),
            ('infrastructure', 'Infrastructure'),
            ('product', 'Product/UX'),
        ]
    )

    # The actual decision content
    key_insights = models.JSONField(default=list)  # List of 3-5 bullet points
    recommended_stance = models.TextField()  # The main policy/decision
    suggested_feature = models.TextField(blank=True)  # Optional feature suggestion
    rationale = models.TextField(blank=True)  # Why this decision was made

    # Participants who contributed
    participants = models.JSONField(default=list)  # List of agent names

    # Governance status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('canonical', 'Canonical Policy'),
            ('experiment', 'Active Experiment'),
            ('superseded', 'Superseded'),
            ('rejected', 'Rejected'),
        ],
        default='draft'
    )
    is_canonical = models.BooleanField(default=False)
    promoted_at = models.DateTimeField(null=True, blank=True)
    promoted_by = models.CharField(max_length=100, blank=True)  # 'human' or agent name

    # If this supersedes a previous decision
    supersedes = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superseded_by'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['decision_type', 'impact_area']),
            models.Index(fields=['status']),
            models.Index(fields=['is_canonical']),
        ]

    def __str__(self):
        return f"[{self.decision_type}] {self.topic}"

    def promote_to_canonical(self, promoted_by='human'):
        """Promote this decision to canonical policy status."""
        from django.utils import timezone
        self.status = 'canonical'
        self.is_canonical = True
        self.promoted_at = timezone.now()
        self.promoted_by = promoted_by
        self.save()

    def get_policy_context(self):
        """Get this decision formatted for injection into agent prompts."""
        insights = '\n'.join(f'  - {i}' for i in self.key_insights[:3])
        return f"""
[CANONICAL POLICY: {self.topic}]
Type: {self.get_decision_type_display()}
Area: {self.get_impact_area_display()}
Key Points:
{insights}
Stance: {self.recommended_stance}
"""
```

### 1.2 Create Decision Extractor Service

**File:** `core/services/decision_extractor.py`

```python
"""
Decision Extractor Service
Extracts structured decisions from agent conversation conclusions.
Uses GPT to parse the conclusion text into structured format.
"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
Analyze this agent conversation conclusion and extract a structured decision summary.

CONVERSATION TOPIC: {topic}
PARTICIPANTS: {participants}
CONCLUSION:
{conclusion}

Extract the following in JSON format:
{{
    "decision_type": "policy|architecture|pipeline|product|experiment|guideline",
    "impact_area": "prompting|memory|image|video|audio|workflow|agents|security|infrastructure|product",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommended_stance": "The main policy or decision in 1-2 sentences",
    "suggested_feature": "Optional: specific feature or implementation suggestion",
    "rationale": "Why this decision makes sense in 1-2 sentences"
}}

Rules:
- key_insights should be 3-5 actionable bullet points
- recommended_stance should be definitive, not wishy-washy
- If no clear decision emerged, return null
- Be concise but complete
"""


class DecisionExtractor:
    """Extracts structured decisions from conversation conclusions."""

    def __init__(self):
        self.client = OpenAI()

    def extract_decision(
        self,
        conversation
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a decision from a conversation's conclusion.

        Args:
            conversation: AgentConversation instance

        Returns:
            Dict with decision fields, or None if no clear decision
        """
        if not conversation.conclusion:
            logger.debug(f"No conclusion for conversation {conversation.id}")
            return None

        # Get participant names
        participants = [p.name for p in conversation.participants.all()]
        if conversation.initiator and conversation.initiator.name not in participants:
            participants.insert(0, conversation.initiator.name)

        prompt = EXTRACTION_PROMPT.format(
            topic=conversation.topic,
            participants=', '.join(participants),
            conclusion=conversation.conclusion
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract structured decisions from agent discussions. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Validate required fields
            if not result.get('recommended_stance'):
                return None

            # Add participants
            result['participants'] = participants
            result['topic'] = conversation.topic

            return result

        except Exception as e:
            logger.error(f"Error extracting decision: {e}")
            return None

    def create_decision_from_conversation(self, conversation) -> Optional['AgentDecisionSummary']:
        """
        Extract and create an AgentDecisionSummary from a conversation.

        Returns the created summary, or None if extraction failed.
        """
        from core.models import AgentDecisionSummary

        extracted = self.extract_decision(conversation)
        if not extracted:
            return None

        try:
            summary = AgentDecisionSummary.objects.create(
                conversation=conversation,
                topic=extracted.get('topic', conversation.topic),
                decision_type=extracted.get('decision_type', 'guideline'),
                impact_area=extracted.get('impact_area', 'agents'),
                key_insights=extracted.get('key_insights', []),
                recommended_stance=extracted.get('recommended_stance', ''),
                suggested_feature=extracted.get('suggested_feature', ''),
                rationale=extracted.get('rationale', ''),
                participants=extracted.get('participants', []),
            )

            logger.info(f"Created decision summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error creating decision summary: {e}")
            return None


def get_decision_extractor():
    """Get singleton decision extractor instance."""
    return DecisionExtractor()
```

### 1.3 Auto-Extract on Conversation Conclude

**File:** `core/tasks.py` - Modify `run_agent_conversation` task

Add at the end of the conversation conclude logic:

```python
# Session 322: Auto-extract decision summary
try:
    from core.services.decision_extractor import get_decision_extractor
    extractor = get_decision_extractor()
    decision = extractor.create_decision_from_conversation(conversation)
    if decision:
        logger.info(f"💡 [BOARDROOM] Extracted decision: {decision.topic}")
except Exception as e:
    logger.warning(f"Could not extract decision: {e}")
```

### 1.4 Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 1.5 Backfill Existing Conversations

**File:** `core/management/commands/backfill_decisions.py`

```python
from django.core.management.base import BaseCommand
from core.models import AgentConversation, AgentDecisionSummary
from core.services.decision_extractor import get_decision_extractor

class Command(BaseCommand):
    help = 'Backfill decision summaries from existing conversations'

    def handle(self, *args, **options):
        extractor = get_decision_extractor()

        # Get conversations with conclusions that don't have decisions yet
        conversations = AgentConversation.objects.filter(
            status='concluded',
            conclusion__isnull=False
        ).exclude(
            decisions__isnull=False
        ).order_by('-started_at')[:50]  # Last 50

        created = 0
        for conv in conversations:
            decision = extractor.create_decision_from_conversation(conv)
            if decision:
                created += 1
                self.stdout.write(f"Created: {decision.topic}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} decision summaries"))
```

---

## Phase 2: API + UI

### 2.1 API Endpoints

**File:** `core/views_agent_learning.py` - Add new endpoints

```python
@require_http_methods(["GET"])
def get_boardroom_decisions(request):
    """
    Get agent decision summaries for the Boardroom UI.

    GET /api/boardroom/decisions/

    Query params:
    - limit: Max decisions to return (default 20)
    - decision_type: Filter by type (policy, architecture, etc.)
    - impact_area: Filter by area (prompting, memory, etc.)
    - status: Filter by status (draft, canonical, etc.)
    - canonical_only: If 'true', only return canonical policies
    """
    try:
        from core.models import AgentDecisionSummary

        limit = int(request.GET.get('limit', 20))
        decision_type = request.GET.get('decision_type')
        impact_area = request.GET.get('impact_area')
        status = request.GET.get('status')
        canonical_only = request.GET.get('canonical_only', 'false').lower() == 'true'

        queryset = AgentDecisionSummary.objects.select_related(
            'conversation'
        ).order_by('-created_at')

        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)
        if impact_area:
            queryset = queryset.filter(impact_area=impact_area)
        if status:
            queryset = queryset.filter(status=status)
        if canonical_only:
            queryset = queryset.filter(is_canonical=True)

        decisions = queryset[:limit]

        decisions_data = []
        for d in decisions:
            decisions_data.append({
                'id': str(d.id),
                'topic': d.topic,
                'decision_type': d.decision_type,
                'decision_type_display': d.get_decision_type_display(),
                'impact_area': d.impact_area,
                'impact_area_display': d.get_impact_area_display(),
                'key_insights': d.key_insights,
                'recommended_stance': d.recommended_stance,
                'suggested_feature': d.suggested_feature,
                'rationale': d.rationale,
                'participants': d.participants,
                'status': d.status,
                'status_display': d.get_status_display(),
                'is_canonical': d.is_canonical,
                'promoted_at': d.promoted_at.isoformat() if d.promoted_at else None,
                'conversation_id': str(d.conversation.id) if d.conversation else None,
                'created_at': d.created_at.isoformat(),
            })

        # Get counts by type for filters
        from django.db.models import Count
        type_counts = dict(
            AgentDecisionSummary.objects.values('decision_type')
            .annotate(count=Count('id'))
            .values_list('decision_type', 'count')
        )

        return JsonResponse({
            'success': True,
            'decisions': decisions_data,
            'count': len(decisions_data),
            'total': AgentDecisionSummary.objects.count(),
            'canonical_count': AgentDecisionSummary.objects.filter(is_canonical=True).count(),
            'type_counts': type_counts,
        })

    except Exception as e:
        logger.error(f"Error getting boardroom decisions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def promote_decision(request, decision_id):
    """
    Promote a decision to canonical policy status.

    POST /api/boardroom/decisions/{decision_id}/promote/
    """
    try:
        from core.models import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        decision.promote_to_canonical(promoted_by='human')

        return JsonResponse({
            'success': True,
            'message': f'Decision "{decision.topic}" promoted to canonical policy',
            'decision_id': str(decision.id)
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Decision not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error promoting decision: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def reject_decision(request, decision_id):
    """
    Reject a decision (mark as not applicable).

    POST /api/boardroom/decisions/{decision_id}/reject/
    """
    try:
        from core.models import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        decision.status = 'rejected'
        decision.save()

        return JsonResponse({
            'success': True,
            'message': f'Decision "{decision.topic}" marked as rejected'
        })

    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Decision not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### 2.2 URL Routes

**File:** `core/urls.py` - Add routes

```python
# Boardroom Decisions API
path('api/boardroom/decisions/', get_boardroom_decisions, name='boardroom-decisions'),
path('api/boardroom/decisions/<uuid:decision_id>/promote/', promote_decision, name='promote-decision'),
path('api/boardroom/decisions/<uuid:decision_id>/reject/', reject_decision, name='reject-decision'),
```

### 2.3 Frontend UI Component

**File:** `ai_core/templates/ai_image_studio.html` - Add Boardroom Decisions section

Add to the Social tab, after Agent Dreams:

```html
<!-- Session 322: Boardroom Decisions Section -->
<div class="card mb-4" style="background: #1a1a1a; border: 2px solid #f59e0b;">
    <div class="card-header d-flex justify-content-between align-items-center" style="background: rgba(245, 158, 11, 0.2); border-bottom: 1px solid #f59e0b;">
        <h5 class="mb-0" style="color: #f59e0b;">🏛️ Boardroom Decisions</h5>
        <div>
            <span class="badge me-2" style="background: #f59e0b;" id="canonical-count-badge">0 Policies</span>
            <select class="form-select form-select-sm d-inline-block" style="width: auto; background: #2d2d2d; border-color: #f59e0b; color: #fff;" id="decision-type-filter">
                <option value="">All Types</option>
                <option value="policy">Policy</option>
                <option value="architecture">Architecture</option>
                <option value="pipeline">Pipeline</option>
                <option value="product">Product</option>
                <option value="guideline">Guideline</option>
            </select>
        </div>
    </div>
    <div class="card-body" style="max-height: 500px; overflow-y: auto;">
        <div id="boardroom-decisions-list">
            <p class="text-muted text-center">Loading decisions...</p>
        </div>
    </div>
</div>
```

### 2.4 Frontend JavaScript

```javascript
// Session 322: Boardroom Decisions
async function loadBoardroomDecisions(filter = '') {
    try {
        let url = '/api/boardroom/decisions/?limit=20';
        if (filter) url += `&decision_type=${filter}`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            updateBoardroomDecisions(data);
        }
    } catch (error) {
        console.error('Error loading boardroom decisions:', error);
    }
}

function updateBoardroomDecisions(data) {
    const container = document.getElementById('boardroom-decisions-list');
    const canonicalBadge = document.getElementById('canonical-count-badge');

    if (canonicalBadge) {
        canonicalBadge.textContent = `${data.canonical_count} Policies`;
    }

    if (!data.decisions || data.decisions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <span style="font-size: 32px; opacity: 0.5;">🏛️</span>
                <p class="text-muted mt-2 mb-0">No decisions yet...</p>
                <small class="text-muted">Agent conversations will generate policy decisions</small>
            </div>
        `;
        return;
    }

    const typeColors = {
        'policy': '#f59e0b',
        'architecture': '#8b5cf6',
        'pipeline': '#10b981',
        'product': '#3b82f6',
        'experiment': '#ec4899',
        'guideline': '#6b7280'
    };

    const typeIcons = {
        'policy': '📋',
        'architecture': '🏗️',
        'pipeline': '⚡',
        'product': '🎯',
        'experiment': '🧪',
        'guideline': '📖'
    };

    container.innerHTML = data.decisions.map(d => {
        const color = typeColors[d.decision_type] || '#6b7280';
        const icon = typeIcons[d.decision_type] || '📄';
        const timeAgo = formatTimeAgo(d.created_at);
        const insights = d.key_insights.slice(0, 3).map(i =>
            `<li style="color: #d1d5db; font-size: 12px;">${i}</li>`
        ).join('');

        const canonicalBadge = d.is_canonical
            ? '<span class="badge bg-success ms-2">Canonical</span>'
            : '';

        const actionButtons = d.is_canonical ? '' : `
            <div class="mt-2">
                <button class="btn btn-sm btn-outline-success me-1" onclick="promoteDecision('${d.id}')">
                    ✅ Adopt as Policy
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="rejectDecision('${d.id}')">
                    ❌ Reject
                </button>
            </div>
        `;

        return `
            <div class="decision-item p-3 mb-3" style="background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 4px solid ${color};">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <span style="font-size: 18px; margin-right: 8px;">${icon}</span>
                        <strong style="color: ${color};">${d.topic}</strong>
                        ${canonicalBadge}
                    </div>
                    <small class="text-muted">${timeAgo}</small>
                </div>
                <div class="mb-2">
                    <span class="badge" style="background: ${color};">${d.decision_type_display}</span>
                    <span class="badge bg-secondary ms-1">${d.impact_area_display}</span>
                </div>
                <p style="color: #e5e7eb; font-size: 14px; margin-bottom: 8px;">${d.recommended_stance}</p>
                <ul style="margin: 0; padding-left: 20px;">${insights}</ul>
                <div class="mt-2">
                    <small class="text-muted">Participants: ${d.participants.join(', ')}</small>
                </div>
                ${actionButtons}
            </div>
        `;
    }).join('');
}

async function promoteDecision(decisionId) {
    try {
        const response = await fetch(`/api/boardroom/decisions/${decisionId}/promote/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        });
        const data = await response.json();
        if (data.success) {
            loadBoardroomDecisions();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error promoting decision:', error);
    }
}

async function rejectDecision(decisionId) {
    try {
        const response = await fetch(`/api/boardroom/decisions/${decisionId}/reject/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        });
        const data = await response.json();
        if (data.success) {
            loadBoardroomDecisions();
        }
    } catch (error) {
        console.error('Error rejecting decision:', error);
    }
}

// Add to refreshAllSocialComponents()
if (typeof loadBoardroomDecisions === 'function') {
    loadBoardroomDecisions();
    console.log('  ✓ Boardroom Decisions: loading latest');
}

// Filter handler
document.getElementById('decision-type-filter')?.addEventListener('change', function() {
    loadBoardroomDecisions(this.value);
});
```

---

## Phase 3: Policy Feedback Loop

### 3.1 Policy Context Service

**File:** `core/services/policy_context.py`

```python
"""
Policy Context Service
Retrieves canonical policies to inject into agent prompts.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class PolicyContextService:
    """Provides canonical policy context for agent prompts."""

    def get_policies_for_agent(
        self,
        agent_name: str,
        impact_areas: Optional[List[str]] = None
    ) -> str:
        """
        Get canonical policies relevant to an agent.

        Args:
            agent_name: Name of the agent requesting context
            impact_areas: Optional filter by impact area

        Returns:
            Formatted policy context string for injection into prompts
        """
        from core.models import AgentDecisionSummary

        queryset = AgentDecisionSummary.objects.filter(
            is_canonical=True
        ).order_by('-promoted_at')

        if impact_areas:
            queryset = queryset.filter(impact_area__in=impact_areas)

        policies = queryset[:10]  # Max 10 policies

        if not policies:
            return ""

        context_parts = ["\n=== CANONICAL POLICIES ===\n"]
        context_parts.append("The following policies have been established through agent deliberation:\n")

        for policy in policies:
            context_parts.append(policy.get_policy_context())

        context_parts.append("\nYou should align your recommendations with these established policies.\n")
        context_parts.append("=== END POLICIES ===\n")

        return '\n'.join(context_parts)

    def get_policies_by_area(self, impact_area: str) -> List['AgentDecisionSummary']:
        """Get all canonical policies for a specific impact area."""
        from core.models import AgentDecisionSummary
        return list(
            AgentDecisionSummary.objects.filter(
                is_canonical=True,
                impact_area=impact_area
            ).order_by('-promoted_at')
        )


def get_policy_context_service():
    """Get singleton policy context service."""
    return PolicyContextService()
```

### 3.2 Inject Policies into Agent Prompts

**File:** `core/prompts/registry.py` - Modify prompt building

```python
def build_agent_prompt(agent_name: str, base_prompt: str) -> str:
    """Build agent prompt with policy context injected."""
    from core.services.policy_context import get_policy_context_service

    # Determine relevant impact areas based on agent
    agent_areas = {
        'ImageAgent': ['image', 'workflow'],
        'VideoAgent': ['video', 'workflow'],
        'PromptEngineeringAgent': ['prompting', 'agents'],
        'MemoryIsolationAgent': ['memory', 'security'],
        'CreativeDirectorAgent': ['image', 'video', 'product'],
        # Add more mappings as needed
    }

    areas = agent_areas.get(agent_name, None)

    policy_service = get_policy_context_service()
    policy_context = policy_service.get_policies_for_agent(agent_name, areas)

    if policy_context:
        return base_prompt + "\n" + policy_context

    return base_prompt
```

### 3.3 Inject Policies into Conversations

**File:** `core/tasks.py` - Modify conversation generation

When generating conversation prompts, append relevant policies:

```python
# In run_agent_conversation, when building the conversation context:
from core.services.policy_context import get_policy_context_service

policy_service = get_policy_context_service()
policy_context = policy_service.get_policies_for_agent(
    agent_name=current_agent.name,
    impact_areas=None  # Get all canonical policies
)

# Append to the conversation system prompt
if policy_context:
    conversation_context += f"\n{policy_context}"
```

---

## Testing Checklist

### Phase 1 Tests
- [ ] `AgentDecisionSummary` model created and migrated
- [ ] `DecisionExtractor` can parse conversation conclusions
- [ ] Auto-extraction triggers when conversation concludes
- [ ] Backfill command works on existing conversations
- [ ] No errors in Celery logs during extraction

### Phase 2 Tests
- [ ] `/api/boardroom/decisions/` returns decisions
- [ ] Filtering by type/area works
- [ ] Promote button changes status to canonical
- [ ] Reject button changes status to rejected
- [ ] UI displays decisions with correct styling
- [ ] Canonical badge appears on promoted decisions
- [ ] Decision type filter works in UI

### Phase 3 Tests
- [ ] `PolicyContextService` returns canonical policies
- [ ] Policies are injected into agent prompts
- [ ] Agents reference policies in their responses
- [ ] Conversation context includes relevant policies
- [ ] Policy changes affect future agent behavior

---

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `core/services/decision_extractor.py` | Extract decisions from conclusions |
| `core/services/policy_context.py` | Provide policies to agents |
| `core/management/commands/backfill_decisions.py` | Backfill existing conversations |

### Files to Modify
| File | Changes |
|------|---------|
| `core/models.py` or `core/models_unified_system.py` | Add `AgentDecisionSummary` model |
| `core/tasks.py` | Auto-extract on conversation conclude |
| `core/views_agent_learning.py` | Add boardroom API endpoints |
| `core/urls.py` | Add boardroom URL routes |
| `ai_core/templates/ai_image_studio.html` | Add Boardroom Decisions UI |
| `core/prompts/registry.py` | Inject policies into prompts |

---

## Success Metrics

1. **Decision Capture Rate**: % of concluded conversations that produce decisions
2. **Canonical Policy Count**: Number of promoted policies
3. **Policy Influence**: Agent responses that reference canonical policies
4. **Governance Efficiency**: Time from discussion to canonical policy

---

## Future Enhancements

1. **Versioned Policies**: Track policy changes over time
2. **Policy Conflicts**: Detect when new decisions conflict with existing policies
3. **A/B Experiments**: Run policies as experiments before canonizing
4. **Policy Analytics**: Track which policies are most referenced/effective
5. **Human Override Audit**: Log when humans override agent decisions
6. **Cross-Agent Policy Consistency**: Ensure all agents respect the same policies

---

**Status:** Blueprint complete. Ready for Phase 1 implementation.
