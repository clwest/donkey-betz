---
originating_session: 849
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 849 - Decision to Initiative Linking

**Date:** January 27, 2026
**Focus:** Auto-link Decisions with Proposed Features to Initiatives
**PR:** #362

---

## What Was Done

Implemented ChatGPT's feedback from Session 848:

> "When a Learning has Proposed Feature, auto-create/link an Initiative"

### New Features

1. **Initiative ForeignKey on AgentDecisionSummary**
   - Decisions now link directly to Initiatives
   - Enables tracing: Conversation → Decision → Initiative → Stage Docs

2. **Artifact Type Classification**
   - New field `artifact_type` on AgentDecisionSummary
   - Values: `learning`, `initiative_stage_doc`, `report`, `playbook`, `decision`
   - Helps classify what kind of artifact was produced

3. **Auto-Initiative Creation**
   - When a decision has `suggested_feature`, an Initiative is auto-created
   - The decision becomes a "learning" artifact linked to the Initiative
   - The Initiative gets the feature name from the decision's `suggested_feature`

---

## Technical Implementation

### New Model Fields (AgentDecisionSummary)

```python
# Session 849: Link to Initiative for tracking decisions with proposed features
initiative = models.ForeignKey(
    'core.Initiative',
    null=True, blank=True, on_delete=models.SET_NULL,
    related_name='source_decisions',
    help_text="Session 849: Initiative created from this decision's proposed feature"
)

# Session 849: Artifact type classification
artifact_type = models.CharField(
    max_length=30,
    choices=[
        ('learning', 'Learning'),
        ('initiative_stage_doc', 'Initiative Stage Document'),
        ('report', 'Report'),
        ('playbook', 'Playbook'),
        ('decision', 'Decision'),
    ],
    default='decision',
    help_text="Session 849: Type of artifact this decision represents"
)
```

### Auto-Linking Logic (decision_extractor.py)

```python
def auto_link_initiative_for_decision(decision) -> Optional['Initiative']:
    """
    Session 849: Auto-create and link an Initiative when a decision has a suggested_feature.

    This creates the crucial link:
    Conversation → Decision (with suggested_feature) → Initiative → Stage 1 doc
    """
    # Only create initiative if there's a suggested feature
    if not decision.suggested_feature or len(decision.suggested_feature.strip()) < 10:
        return None

    # Skip if already linked
    if decision.initiative_id:
        return decision.initiative

    # Create/get Initiative and link
    service = get_initiative_integration_service()
    initiative, created = service.get_or_create_initiative(
        topic=feature_name,
        description=f"Auto-created from conversation decision...",
        source_decision_id=str(decision.id),
        created_by="DecisionExtractor"
    )

    decision.initiative = initiative
    decision.artifact_type = 'learning'
    decision.save()
    return initiative
```

### Flow

1. Conversation ends with DecisionSummary containing "Proposed Feature"
2. DecisionExtractor creates AgentDecisionSummary
3. `auto_link_initiative_for_decision()` checks for `suggested_feature`
4. If present, creates/links Initiative
5. Decision is marked as `artifact_type='learning'`

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_unified_system.py` | Added `initiative` ForeignKey and `artifact_type` field to AgentDecisionSummary |
| `core/services/decision_extractor.py` | Added `auto_link_initiative_for_decision()` function |
| `core/migrations/0195_session_849_decision_initiative_link.py` | Django migration for new fields |

---

## ChatGPT Feedback Addressed

| Feedback Item | Status |
|---------------|--------|
| Auto-create/link Initiative when Learning has Proposed Feature | ✅ DONE |
| Add artifact_type to every output | ✅ DONE (on AgentDecisionSummary) |
| Add initiative_id as linkage | ✅ DONE (ForeignKey on AgentDecisionSummary) |

### Still TODO (from ChatGPT feedback)

1. **UI "Trace" panel** - Show conversation → initiative → stage docs → pilots → results
2. **UI "Inbox" view** - Group items by initiative_id
3. **"Needs decision" badge** - For items with questions in synthesis
4. **Fix synthesis template** - String slicing and deduplication issues

---

## Testing

```bash
# 1. Start platform
make start && make celery

# 2. Run a conversation that produces a Proposed Feature
# The DecisionExtractor will auto-create an Initiative

# 3. Verify the link
python manage.py shell -c "
from core.models_unified_system import AgentDecisionSummary
from core.models_document_registry import Initiative

# Check recent decisions with initiatives
decisions = AgentDecisionSummary.objects.filter(initiative__isnull=False)[:5]
for d in decisions:
    print(f'{d.topic[:40]}: {d.artifact_type} -> {d.initiative.name}')"

# 4. Check initiative source_decisions reverse lookup
python manage.py shell -c "
from core.models_document_registry import Initiative

for i in Initiative.objects.all()[:5]:
    decisions = i.source_decisions.all()
    print(f'{i.name[:40]}: {decisions.count()} source decisions')"
```

---

## Architecture Impact

This creates a complete traceability chain:

```
AgentConversation / HiveMindSession
        ↓ (DecisionExtractor)
AgentDecisionSummary (suggested_feature, artifact_type='learning')
        ↓ (auto_link_initiative_for_decision)
Initiative (5-stage pipeline)
        ↓ (link_document_to_stage)
InitiativeStage → SelfBlog
```

The system now automatically tracks the journey from conversational insight to formal project.

---

**Session 849 Complete - Decisions with Proposed Features now auto-create Initiatives**
