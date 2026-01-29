# Session 862: Content Intelligence Layer

**Date:** January 28, 2026
**Status:** COMPLETE
**PRs:** #457 (Gallery Fix), #458 (Podcast Fix), #459 (Docs), #461 (Content Intelligence)

---

## Overview

This session implemented the Content Intelligence Layer based on analysis of the "AI Development Best Practices: Building Beyond PowerPoints" blog. The key insight was that the system was publishing internal operational knowledge as external marketing content.

## The Problem

The blog "AI Development Best Practices: Building Beyond PowerPoints" was:
- Categorized as `blog` (public content)
- But contained internal signals: "we built", "our agents", "our spiders"
- References to Kalshi spider, 6,000 conversations - operational details
- Should have been a build log or internal note, not a public blog

ChatGPT's analysis identified:
- Quality: 7.5/10 (solid B-tier)
- Structure: 6/10 (flat, no visual hierarchy)
- Presentation: 4/10 (missing hooks, callouts, stat boxes)
- Originality: 6/10 (overlaps with existing content)
- **Verdict:** Not a blog - it's operational knowledge

## Solution: Content Intelligence Layer

### 1. PublishGate Service

Location: `core/services/publish_gate.py`

Quality evaluation before publishing:

```python
from core.services.publish_gate import PublishGate, evaluate_blog

gate = PublishGate()
result = gate.apply_to_blog(blog)

# result.decision: 'publish', 'enhance', 'internal_only'
# result.quality_score: 0-1
# result.novelty_score: 0-1
# result.structure_score: 0-1
# result.content_type: 'public', 'internal', 'strategic'
```

**Quality Scoring:**
| Dimension | Threshold | What It Measures |
|-----------|-----------|------------------|
| Quality | 0.75 | Word count, intro/conclusion, sections |
| Novelty | 0.60 | Title uniqueness, topic freshness |
| Structure | 0.65 | Section variety, engagement elements |

**Decisions:**
- `publish`: All thresholds met → ready for public
- `enhance`: Quality > 0.6 but missing something → send to EditorAgent
- `internal_only`: Internal content or low quality → keep as build log

### 2. ContentClassifier Service

Location: `core/services/content_classifier.py`

Routes content to appropriate type:

```python
from core.services.content_classifier import ContentClassifier, classify_content

classifier = ContentClassifier()
result = classifier.classify_blog(blog)

# result.content_type: 'public', 'internal', 'strategic'
# result.suggested_category: 'blog', 'build_log', 'playbook', etc.
# result.confidence: 0-1
# result.signals_found: ['title:pattern', 'content:pattern', ...]
```

**Classification Signals:**

| Content Type | Title Patterns | Content Patterns |
|--------------|----------------|------------------|
| **Internal** | "how we built", "lessons learned" | "our agents", "our spiders", "action items for us" |
| **Public** | "how to", "guide to", "trends in" | "you will learn", "your business" |
| **Strategic** | "audit:", "analysis:", "dossier:" | "executive summary", "risk factors" |

### 3. SelfBlog Model Updates

New fields added:

```python
class SelfBlog(models.Model):
    # Content routing
    content_type = models.CharField(
        choices=[
            ('public', 'Public Content'),
            ('internal', 'Internal Content'),
            ('strategic', 'Strategic Content'),
        ],
        default='public'
    )

    # Quality scores
    quality_score = models.FloatField(null=True)
    novelty_score = models.FloatField(null=True)
    structure_score = models.FloatField(null=True)
    publish_ready = models.BooleanField(default=False)
    gate_notes = models.TextField(blank=True)

    # New categories
    CATEGORY_CHOICES = [
        ('blog', 'Blog Post'),
        ('build_log', 'Build Log'),       # NEW
        ('internal_note', 'Internal Note'), # NEW
        ('playbook', 'Playbook/Doctrine'),  # NEW
        ('dossier', 'Strategic Dossier'),   # NEW
        # ... existing categories
    ]

    # New statuses
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),      # NEW
        ('needs_enhancement', 'Needs Enhancement'), # NEW
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]
```

### 4. Management Command

```bash
# Evaluate specific blog
python manage.py apply_publish_gate --blog-id UUID

# Evaluate all blogs
python manage.py apply_publish_gate --all

# Evaluate only drafts
python manage.py apply_publish_gate --drafts-only

# Show summary statistics
python manage.py apply_publish_gate --summary

# Preview without saving
python manage.py apply_publish_gate --all --dry-run

# Auto-reclassify internal content
python manage.py apply_publish_gate --all --reclassify
```

---

## Content Flow After This Session

```
Agent Creates Content
         ↓
ContentClassifier
         ↓
┌────────────────┬────────────────┬────────────────┐
│ content_type   │ content_type   │ content_type   │
│ = 'public'     │ = 'internal'   │ = 'strategic'  │
└───────┬────────┴───────┬────────┴───────┬────────┘
        ↓                ↓                ↓
   PublishGate      Build Log        Dossier/Report
        ↓            (feeds           (for operators)
┌───────┴───────┐    learning)
│ Decision      │
├───────────────┤
│ publish →     │ Ready for external audience
│ enhance →     │ Send to EditorAgent
│ internal_only │ Reclassify as build_log
└───────────────┘
```

---

## Other Fixes in This Session

### Gallery API Resilience (PR #457)
- Added per-media-type error handling
- If images fail, videos/3D/Resolve still return
- `_media_errors` field shows partial failures

### Podcast Status Fix (PR #458)
- Frontend filtered for `status='published'`
- Backend uses `status='complete'`
- Fixed filter to match both
- 192 podcast episodes now display

### Synthetic Users (Earlier in Session)
- Created 15 persona archetypes for testing
- `python manage.py generate_synthetic_users --all`
- For testing agent recommendations before real users

---

## Files Created/Modified

### Created
| File | Purpose |
|------|---------|
| `core/services/publish_gate.py` | Quality gate service |
| `core/services/content_classifier.py` | Content routing service |
| `core/management/commands/apply_publish_gate.py` | Management command |
| `core/migrations/0206_session_862_content_intelligence.py` | Migration |

### Modified
| File | Changes |
|------|---------|
| `core/models_unified_system.py` | SelfBlog model updates |
| `core/views_image.py` | Gallery API error handling |
| `frontend/.../ContentStudioTab.tsx` | Podcast status filter fix |

---

## Next Steps

### P1: Apply to Production
1. Run migration on prod: `railway run python manage.py migrate core`
2. Evaluate the AI Development blog: `railway run python manage.py apply_publish_gate --blog-id fc2b9def-7f64-425b-90e8-d2b26326489d`
3. Verify classification as internal/build_log

### P2: EditorAgent
- Create agent that polishes content marked as `needs_enhancement`
- Add hooks, callouts, stat boxes
- Improve structure score

### P3: Internal Content → Learning Loop
- Build logs should feed `AgentLearning`, `AgentMemory`
- Create `LearningExtractionAgent` to extract insights
- Connect to playbook updates

### P4: Pre-Publish Integration
- Hook PublishGate into the publish workflow
- Auto-route content before it reaches external audience
- Dashboard for reviewing `needs_enhancement` content

---

## Key Insight

> "Your system is now producing multiple quality tiers. That's normal. What you're missing is an editorial layer."
> — ChatGPT Analysis

This session adds that editorial layer. The system now has the intelligence to distinguish between:
- **What to publish** (thought leadership)
- **What to enhance** (good ideas, weak presentation)
- **What to keep internal** (operational knowledge)

The goal: Stop generating noise, start building institutional intelligence.
