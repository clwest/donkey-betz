# AI Profile Intelligence Name Issue - Investigation & Fix Summary

## Issue Description
The user reported that their AI Profile Intelligence had stored their name earlier today, but it was lost and the assistant no longer knew their name.

## Root Cause Analysis

### 1. Data Investigation
- **UserProfile table**: Only 1 profile exists (testuser), with no preferred_name set
- **OnboardingProfile**: Shows completed onboarding but preferred_name was empty
- **OnboardingResponse**: Found response "Donkey King" to "What would you like me to call you?" question
- **ExtractedFacts**: 7 facts extracted, but NONE related to the user's name

### 2. Bug Identified
The onboarding system failed to:
1. Extract the preferred_name from the onboarding response
2. Save it to the OnboardingProfile
3. Transfer it to the UserProfile during onboarding completion

### 3. System Prompt Issue
The system prompt had "Chris" hardcoded instead of using dynamic user names.

## Fixes Applied

### 1. Data Fix (Immediate)
Manually synced the name "Donkey King" from OnboardingResponse to both OnboardingProfile and UserProfile.

### 2. Code Fix - Onboarding Service
Added special handling in `OnboardingService.submit_response()` to extract name from the "What would you like me to call you?" question:

```python
# Special handling for name question
if 'call you' in question.question_text.lower() and response.response_text:
    profile.preferred_name = response.response_text.strip()
    profile.save()
    logger.info(f"Set preferred_name for {self.user.username}: {profile.preferred_name}")
```

### 3. System Prompt Personalization
- Changed hardcoded "Chris" to `{{user_name}}` template variable in `simplified_system_prompt.py`
- Updated `PersonalAIService.get_system_prompt()` to replace `{{user_name}}` with actual user's preferred name from UserProfile

## Files Modified
1. `/ai_partner/services/onboarding_service.py` - Added name extraction logic
2. `/ai_partner/simplified_system_prompt.py` - Changed hardcoded name to template variable
3. `/ai_partner/personal_ai_services.py` - Added logic to populate user's name in system prompt

## Verification
- UserProfile now has preferred_name: "Donkey King"
- Profile completeness increased from 18.2% to 27.3%
- System prompt will now use the actual user's name instead of "Chris"

## Prevention
The fix ensures that:
1. Future onboarding responses for name questions are properly extracted
2. The name is saved to both OnboardingProfile and UserProfile
3. The AI assistant uses the personalized name in all interactions

## Status
✅ Issue resolved - The AI Profile Intelligence now properly stores and uses the user's preferred name.