---
originating_session: 866
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 866: ATS Keyword Optimization Module

**Date:** January 29, 2026
**Status:** COMPLETE

## Overview

Built the ATS (Applicant Tracking System) Keyword Optimization Module - a complete resume-to-job matching and optimization system. This feature was requested by a HiveMind brainstorm session about customer personas and job seeking.

## What Was Built

### 1. ATS Keyword Service (`core/services/ats_keyword_service.py`)

Core service with 590+ lines of keyword intelligence:

**Keyword Categories:**
- `technical_skills`: programming languages, frameworks, databases, cloud/devops, AI/ML
- `soft_skills`: leadership, communication, problem-solving, etc.
- `certifications`: AWS, PMP, Scrum, Six Sigma, etc.
- `experience_levels`: junior, mid, senior, lead, executive
- `action_verbs`: achieved, built, developed, implemented, etc.

**Key Methods:**
- `extract_keywords(text, use_llm=False)` - Extract and categorize keywords from text
- `score_resume_match(resume_text, job_description)` - Score resume against job with weighted categories
- `get_optimization_suggestions(resume_text, job_description, user_skills)` - Prioritized improvement suggestions
- `generate_ats_optimized_summary(user_profile, job_description, style)` - Generate ATS-friendly summaries

**Industry Detection:**
- Fintech, Healthcare, E-commerce, SaaS, AI/ML keywords
- Automatic industry classification based on keyword presence

### 2. ATS Models (`core/models_ats_optimization.py`)

Four Django models for the ATS system:

| Model | Purpose |
|-------|---------|
| `PersonaResumeTemplate` | Industry/role-specific resume templates with keywords and examples |
| `ATSKeywordMapping` | Canonical keyword mappings with performance metrics |
| `ResumeOptimizationLog` | Conversion funnel tracking (signup → interview → offer) |
| `ResumeRewriteOrder` | Paid resume rewrite orders ($79/$149/$249 tiers) |

**Conversion Funnel Stages:**
1. signup → analyzed → downloaded_free → purchased_* → resume_delivered → applied → interview → offer

### 3. ATS API Views (`core/views_ats_optimization.py`)

Six API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ats/analyze/` | POST | Score resume against job description |
| `/api/ats/extract-keywords/` | POST | Extract keywords from any text |
| `/api/ats/optimize/` | POST | Get prioritized optimization suggestions |
| `/api/ats/templates/` | GET | List persona resume templates |
| `/api/ats/generate-summary/` | POST | Generate ATS-optimized professional summary |
| `/api/ats/stats/` | GET | Admin-only conversion statistics |

### 4. Database Migration

Migration `0208_session_866_ats_optimization.py` creates:
- 4 new tables
- 3 indexes for optimization log queries

## Usage Examples

### Extract Keywords
```python
from core.services.ats_keyword_service import ats_keyword_service

result = ats_keyword_service.extract_keywords(job_description)
# Returns: {
#   'keywords': ['python', 'django', 'aws', ...],
#   'categories': {'technical_skills': [...], 'soft_skills': [...], ...},
#   'total_count': 15,
#   'detected_industry': 'tech'
# }
```

### Score Resume Match
```python
result = ats_keyword_service.score_resume_match(resume_text, job_description)
# Returns: {
#   'overall_score': 70.0,
#   'match_level': 'good',
#   'category_scores': {...},
#   'missing_keywords': ['kubernetes', 'communication']
# }
```

### Get Optimization Suggestions
```python
suggestions = ats_keyword_service.get_optimization_suggestions(
    resume_text, job_description, user_skills=['python', 'aws']
)
# Returns prioritized keywords to add, placement tips, action verbs
```

### API Usage
```bash
curl -X POST http://localhost:8000/api/ats/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer with 5 years experience...",
    "job_description": "Senior Python Developer at Tech Startup...",
    "include_suggestions": true
  }'
```

## Files Changed/Created

| File | Action |
|------|--------|
| `core/services/ats_keyword_service.py` | Created - Core ATS service |
| `core/models_ats_optimization.py` | Created - 4 Django models |
| `core/views_ats_optimization.py` | Created - 6 API views |
| `core/urls.py` | Modified - Added 6 URL patterns |
| `core/models/__init__.py` | Modified - Added model imports |
| `core/models.py` | Modified - Added model imports |
| `core/migrations/0208_session_866_ats_optimization.py` | Created |

## Scoring Algorithm

The ATS score is calculated with weighted categories:

| Category | Weight |
|----------|--------|
| Technical Skills | 40% |
| Soft Skills | 20% |
| Certifications | 15% |
| Experience Level | 15% |
| Action Verbs | 5% |
| Industry Specific | 5% |

**Match Levels:**
- 85%+ = Excellent
- 70-84% = Good
- 50-69% = Moderate
- 30-49% = Low
- <30% = Poor

## Integration with Existing Systems

The ATS module integrates with:
- `ExtendedUserProfile` - Retrieves user skills for personalized suggestions
- `ResumeVersion` - Links to existing resume storage model
- Conversion tracking for monetization analytics

## Future Enhancements

1. **LLM-Enhanced Extraction**: `use_llm=True` parameter for advanced keyword extraction
2. **Template Marketplace**: Persona-specific resume templates for different industries
3. **A/B Testing**: Built-in variant tracking for optimization experiments
4. **Interview Correlation**: Track which keywords lead to interviews

## Testing

```bash
# Test keyword extraction
python manage.py shell -c "
from core.services.ats_keyword_service import ats_keyword_service
result = ats_keyword_service.extract_keywords('Python Django AWS developer')
print(result['categories']['technical_skills'])
"

# Test resume scoring
python manage.py shell -c "
from core.services.ats_keyword_service import ats_keyword_service
result = ats_keyword_service.score_resume_match(resume_text, job_description)
print(f'Score: {result[\"overall_score\"]}%')
"
```

## Connection to HiveMind Brainstorm

This module implements the "Resume Optimizer AI" task from the HiveMind brainstorm session about customer personas:

> "Build the ATS keyword mapping module with industry-specific scoring"

The brainstorm identified three customer personas:
1. **Tech Professional** - Needs ATS optimization for tech keywords
2. **Career Changer** - Needs skill translation across industries
3. **Executive** - Needs leadership keyword optimization

This module addresses all three with industry-specific keyword categories and persona-tailored templates.
