# User Integration Notes for Opportunities Hub
## Current State Documentation for Future Development

> **📘 Note:** User Profile, AI Configuration, and Command & Control systems have been consolidated into **USER_PROFILE_AND_AI_CONFIG.md**

### 🔑 Key Connection Points

## 1. User Profile System
**Current Status:** Partially implemented
- **Model:** `UnifiedUser` in `/persistence/models.py`
- **Extended Profile Endpoint:** `/api/profile/extended/` (needs auth token)
- **Frontend Store:** `useAuthStore` in `/frontend/src/store/authStore.ts`

### Critical Files to Review:
```
/persistence/models.py - UnifiedUser model with extended fields
/frontend/src/components/OpportunitiesHub.tsx - Line 245: fetchUserProfile()
/frontend/src/store/authStore.ts - User state management
```

## 2. Opportunities Hub Integration Points

### Data Flow:
```
User Profile → Skill Matching → Opportunities Filter → Personalized Results
```

### Key Functions in OpportunitiesHub.tsx:
- **Line 244-249:** `fetchUserProfile()` - Currently tries to fetch extended profile
- **Line 423-436:** Application status tracking (commented out, needs implementation)
- **Line 333-337:** Fetches opportunities from multiple endpoints

### Endpoints That Need User Context:
```javascript
// These endpoints exist but need user personalization:
/api/v1/intelligence/opportunities/ - Should filter by user skills
/api/opportunities/ - Should match user preferences
/api/profile/extended/ - Needs proper auth and extended fields
```

## 3. Missing User Features That Need Implementation

### A. User Skills & Experience
```python
# Need to add to UnifiedUser model:
- skills (JSONField or M2M)
- experience_years
- job_preferences
- salary_expectations
- remote_preference
- industry_preferences
```

### B. Application Tracking
```python
# Need new model:
class JobApplication(models.Model):
    user = ForeignKey(UnifiedUser)
    opportunity_id = CharField()
    status = CharField(choices=['viewed', 'saved', 'applied', 'interviewing', 'rejected', 'accepted'])
    applied_at = DateTimeField()
    notes = TextField()
```

### C. Personalization Engine
The system has 149 agents but they're not connected to user preferences:
- Income Builder Agent needs user financial goals
- Career Advisor needs user career history
- Skills Matcher needs user competencies

## 4. WebSocket Connections for User

### Current WebSocket Structure:
```javascript
// OpportunitiesHub uses WebSocket but no user context
wsRef.current = new WebSocket('ws://localhost:8000/ws/opportunities/');

// Should be:
wsRef.current = new WebSocket(`ws://localhost:8000/ws/opportunities/?user_id=${userId}`);
```

### Backend Consumer Needs:
```python
# /intelligence/consumers.py or similar needs:
class OpportunitiesConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['user'].id
        # Filter opportunities by user preferences
```

## 5. Authentication & Authorization

### Current Auth:
- Token-based auth using `authToken` in localStorage
- Backend expects: `Authorization: Token <token>`
- Frontend apiClient adds token automatically

### What's Working:
✅ Login/logout flow
✅ Token storage and retrieval
✅ Protected routes with AuthGuard

### What Needs User Integration:
❌ User onboarding flow (collecting skills/preferences)
❌ Profile completion wizard
❌ Skill assessment system

## 6. Income Builder Integration

### Current Implementation:
```python
# /ai_core/intelligence/income_builder.py
class AIIncomeBuilder:
    # Has ML pipeline and agent connections
    # But no user context!
```

### Needs:
```python
async def generate_opportunities(self, user: UnifiedUser):
    # Filter by user.skills
    # Match user.salary_expectations
    # Consider user.location_preferences
```

## 7. Quick Apply Feature

### Current State:
- UI button exists in OpportunitiesHub
- No backend implementation
- No resume storage

### Needs Implementation:
```python
# User model needs:
resume = FileField()
cover_letter_template = TextField()
linkedin_url = URLField()

# Application endpoint:
POST /api/jobs/apply/
{
    "opportunity_id": "xxx",
    "resume_id": "xxx",
    "cover_letter": "personalized"
}
```

## 8. Revenue Tracking Per User

### Current Mock Data:
```javascript
// OpportunitiesHub.tsx has placeholder:
totalEarnings: 2847.50
successRate: 87
```

### Needs Real Implementation:
```python
class UserEarnings(models.Model):
    user = ForeignKey(UnifiedUser)
    opportunity_id = CharField()
    amount = DecimalField()
    earned_date = DateTimeField()
    status = CharField()  # pending, confirmed, paid
```

## 9. Agent Assignments

### Current State:
- 149 agents registered in `/agents/registry.py`
- 25 advisors in `/advisors/registry.py`
- But no user → agent mapping!

### Needs:
```python
class UserAgentAssignment(models.Model):
    user = ForeignKey(UnifiedUser)
    agent_name = CharField()
    specialization = CharField()
    is_active = BooleanField()

# Or in UnifiedUser:
assigned_agents = JSONField(default=list)  # ["income_optimizer", "resume_builder", etc.]
```

## 10. Database Schema Considerations

### Current Tables:
- `unified_users` (main user table)
- `unified_embeddings` (for RAG/memory)
- No job/opportunity tracking tables!

### Needed Tables:
```sql
-- User preferences and skills
CREATE TABLE user_profiles_extended (
    user_id FK,
    skills JSONB,
    experience_years INT,
    desired_salary INT,
    industries TEXT[]
);

-- Application tracking
CREATE TABLE job_applications (
    id SERIAL,
    user_id FK,
    opportunity_id VARCHAR,
    status VARCHAR,
    applied_at TIMESTAMP
);

-- Earnings tracking
CREATE TABLE user_earnings (
    user_id FK,
    amount DECIMAL,
    source VARCHAR,
    date TIMESTAMP
);
```

## 11. Frontend State Management

### Current Stores:
- `authStore` - Basic user auth
- No profile store!
- No opportunities preferences store!

### Needs:
```typescript
// userProfileStore.ts
interface UserProfile {
    skills: string[];
    experience: number;
    preferences: {
        remote: boolean;
        salary_min: number;
        industries: string[];
    };
    applications: Map<string, ApplicationStatus>;
}
```

## 12. Critical Integration Sequence

### When implementing user features, follow this order:

1. **Extend UnifiedUser model** with skills, preferences
2. **Create profile API endpoints** for updating user data
3. **Build onboarding flow** to collect user information
4. **Connect opportunities filtering** to user preferences
5. **Implement application tracking** with status management
6. **Wire up WebSocket** with user context
7. **Connect agents** to user profile for personalization
8. **Enable Quick Apply** with resume management
9. **Track earnings** and success metrics per user

## 13. Environment Variables Needed

```bash
# Add to .env:
USER_ONBOARDING_REQUIRED=true
MIN_PROFILE_COMPLETION=70  # Percentage before allowing opportunities
DEFAULT_AGENT_ASSIGNMENTS=income_builder,resume_optimizer,career_coach
```

## 14. Testing User Flows

### Key User Journeys to Test:
1. **New User:** Signup → Onboarding → Profile Setup → View Opportunities
2. **Returning User:** Login → Updated Opportunities → Quick Apply
3. **Power User:** Multiple Applications → Track Status → View Earnings

## 15. Migration Considerations

### When adding user fields:
```bash
# After modifying UnifiedUser model:
python manage.py makemigrations persistence
python manage.py migrate

# May need to backfill data:
python manage.py shell
>>> from persistence.models import UnifiedUser
>>> UnifiedUser.objects.update(skills=[], preferences={})
```

## 🚨 CRITICAL: Current Blockers

1. **No User Skills Data:** Can't personalize without knowing user capabilities
2. **No Application Tracking:** Can't show application status without database table
3. **No Resume Storage:** Quick Apply won't work without resume management
4. **No User-Agent Mapping:** 149 agents aren't assigned to users
5. **No Earnings Tracking:** Revenue dashboard shows mock data

## 💡 Quick Wins for Next Session

1. Add `skills` JSONField to UnifiedUser model
2. Create `/api/profile/skills/` endpoint
3. Add skills input to frontend profile page
4. Filter opportunities by skills match
5. Store application clicks in localStorage (temporary)

## 🔗 Connection Points Summary

```
UnifiedUser Model (skills, preferences)
    ↓
Profile API (/api/profile/extended/)
    ↓
OpportunitiesHub.fetchUserProfile()
    ↓
Filter opportunities by user.skills
    ↓
Track applications in database
    ↓
Show personalized success metrics
```

---

**Last Updated:** September 18, 2025
**Next Phase:** User Profile System Implementation
**Priority:** HIGH - System needs user context for personalization