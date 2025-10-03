# Onboarding System Integration Guide

## Overview
A comprehensive onboarding system has been implemented to guide new users through profile setup with an interactive Q&A flow.

## Backend Setup

### 1. Run Migration
```bash
cd backend
python manage.py migrate
```

### 2. Test API Endpoints
```bash
python test_onboarding_api.py
```

## Frontend Integration

### 1. Add Route
In your main router file (e.g., `App.tsx` or `routes.tsx`):

```typescript
import Onboarding from '@/features/onboarding/pages/Onboarding';
import OnboardingGuard from '@/features/onboarding/components/OnboardingGuard';

// Add route
<Route path="/onboarding" element={<Onboarding />} />

// Wrap protected routes with OnboardingGuard
<OnboardingGuard>
  <Routes>
    {/* Your existing routes */}
  </Routes>
</OnboardingGuard>
```

### 2. Add Status Badge to User Profile
```typescript
import OnboardingStatusBadge from '@/features/onboarding/components/OnboardingStatusBadge';

// In your profile or settings component
<OnboardingStatusBadge showDetails />
```

### 3. Check Onboarding on Login
In your authentication flow:

```typescript
import { onboardingService } from '@/features/onboarding/services/onboardingService';

// After successful login
const needsOnboarding = await onboardingService.needsOnboarding();
if (needsOnboarding) {
  navigate('/onboarding');
}
```

## Features Implemented

### Backend Models
- **OnboardingProfile**: Tracks user progress through onboarding
- **OnboardingQuestion**: Predefined questions for each stage
- **OnboardingResponse**: User answers with fact extraction
- **OnboardingInsight**: AI-generated insights from responses

### Onboarding Stages
1. **Welcome**: Get user's preferred name
2. **Profile Basics**: Location, occupation, company
3. **Interests Q&A**: Hobbies, learning interests, areas of interest
4. **Goals Q&A**: Current goals, challenges, support needs
5. **Work Q&A**: Projects, skills, work style
6. **Preferences**: Communication style, AI assistance preferences

### API Endpoints
- `GET /api/ai-partner/onboarding/status/` - Current onboarding status
- `POST /api/ai-partner/onboarding/submit-response/` - Submit answer
- `POST /api/ai-partner/onboarding/skip-question/` - Skip optional question
- `GET /api/ai-partner/onboarding/stage-questions/` - Get all questions for a stage
- `POST /api/ai-partner/onboarding/complete/` - Complete onboarding
- `GET /api/ai-partner/onboarding/insights/` - Get AI insights
- `POST /api/ai-partner/onboarding/reset/` - Reset progress

### Frontend Components
- **OnboardingWizard**: Main wizard component with progress tracking
- **OnboardingGuard**: Redirect users who need onboarding
- **OnboardingStatusBadge**: Shows completion status
- **onboardingService**: API service for all endpoints

## Key Benefits

1. **Progressive Profiling**: Learn about users gradually
2. **Fact Extraction**: Automatically extract facts from responses
3. **Personalization**: Use collected data to personalize AI responses
4. **Flexible Flow**: Required and optional questions
5. **Progress Tracking**: Visual progress and time tracking
6. **Insights Generation**: AI analyzes responses for patterns

## Testing

### Backend Test
```bash
# Run the test script
python test_onboarding_api.py

# Reset onboarding for a user
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from ai_partner.onboarding_models import OnboardingProfile
>>> User = get_user_model()
>>> user = User.objects.get(email="testuser@example.com")
>>> OnboardingProfile.objects.filter(user=user).delete()
```

### Frontend Test
1. Navigate to `/onboarding` when not logged in (should redirect to login)
2. Log in and navigate to `/onboarding`
3. Complete the flow and verify:
   - Progress bar updates
   - Questions display correctly
   - Answers are submitted
   - Facts are extracted (check profile)
   - Completion redirects properly

## Customization

### Adding Questions
Edit `STAGE_QUESTIONS` in `/backend/ai_partner/services/onboarding_service.py`

### Changing Stages
Modify `ONBOARDING_STAGES` in `/backend/ai_partner/onboarding_models.py`

### Styling
The frontend uses Tailwind CSS with a gradient theme. Modify colors in `OnboardingWizard.tsx`

## Next Steps

1. **Analytics Dashboard**: Track onboarding completion rates
2. **A/B Testing**: Test different question flows
3. **Dynamic Questions**: Generate questions based on previous answers
4. **Multi-language Support**: Internationalize the onboarding flow
5. **Integration with Main Chat**: Use onboarding data in conversations