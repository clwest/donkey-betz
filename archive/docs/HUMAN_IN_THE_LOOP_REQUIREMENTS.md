# 🚨 HUMAN-IN-THE-LOOP REQUIREMENTS

## Critical Issue Identified (2025-09-18)

### Problem: AI Misinterprets User Intent
When a user selects a job opportunity like "AI Prompt Engineering Services" and clicks "Start Plan", the system incorrectly assumes they want to **learn the skill** rather than **apply for the position**.

**Current Behavior (WRONG):**
- User selects: "AI Prompt Engineering Services" job
- AI researches: "How to learn prompt engineering"
- AI creates plan: "Take courses, practice prompts, build portfolio"

**Expected Behavior (CORRECT):**
- User selects: "AI Prompt Engineering Services" job
- AI researches: The specific company, role requirements, application process
- AI creates plan: "Tailor resume for this role, write cover letter, prepare portfolio examples relevant to their needs"

## Root Cause
The system lacks **context awareness** about user intent:
1. It treats all opportunities the same (jobs vs income streams)
2. It doesn't distinguish between "I want to apply for this job" vs "I want to learn this skill"
3. No confirmation step to clarify user intent

## Proposed Solutions

### 1. Add Intent Clarification (Quick Fix)
```javascript
// When user clicks "Start Plan", show dialog:
"What would you like to do with this opportunity?"
- [ ] Apply for this position
- [ ] Learn this skill
- [ ] Research the market
- [ ] Save for later
```

### 2. Differentiate Opportunity Types
```python
# In job_income_bridge.py
opportunity = {
    'type': 'job_application',  # vs 'skill_development' or 'business_start'
    'intent': 'apply',          # vs 'learn' or 'research'
    'context': {
        'company_name': 'TechCorp',
        'job_listing_url': 'https://...',
        'application_deadline': '2025-09-30'
    }
}
```

### 3. Add Human Verification Step
Before executing any action plan:
1. Show the AI's interpretation: "I understand you want to [APPLY FOR] this [JOB POSITION]"
2. Show planned actions: "I will research [COMPANY], prepare [APPLICATION MATERIALS]"
3. Get confirmation: "Is this correct?" [Yes] [No, I want to...]

### 4. Implement Feedback Loop
```python
class ActionPlanFeedback:
    def __init__(self):
        self.intent_corrections = []  # Track when AI misunderstands
        self.success_metrics = []     # Track what actually worked

    def learn_from_correction(self, original_intent, corrected_intent):
        # Store this to improve future interpretations
        self.intent_corrections.append({
            'original': original_intent,
            'corrected': corrected_intent,
            'timestamp': datetime.now()
        })
```

## Implementation Priority

### Phase 1: Immediate (Prevent Confusion)
1. ✅ Add simple intent clarification dialog
2. ✅ Differentiate "Apply" vs "Learn" actions
3. ✅ Show plan preview before execution

### Phase 2: Short-term (Improve Accuracy)
1. ⬜ Add opportunity type metadata
2. ⬜ Implement context-aware action planning
3. ⬜ Add human feedback collection

### Phase 3: Long-term (Learn & Adapt)
1. ⬜ Build intent prediction model from corrections
2. ⬜ Implement personalized action templates
3. ⬜ Create success tracking metrics

## Example: Correct Behavior

When user selects "AI Prompt Engineering Services" job:

```
🎯 Opportunity Selected: AI Prompt Engineering Services
📍 Type: Job Application
🏢 Company: Digital Agency

What would you like to do?
> ✓ Apply for this position
  ○ Learn prompt engineering skills
  ○ Research similar opportunities

Creating application plan...

📝 Application Plan:
1. Research Digital Agency's AI services
2. Analyze job requirements vs your skills
3. Customize resume highlighting:
   - Previous AI project experience
   - Prompt engineering examples
   - Relevant technical skills
4. Write tailored cover letter
5. Prepare portfolio of prompt examples
6. Submit application via platform
7. Set follow-up reminder for 3 days

Proceed with this plan? [Yes] [Modify] [Cancel]
```

## Testing Checklist

- [ ] Job opportunities trigger "apply" actions
- [ ] Skill opportunities trigger "learn" actions
- [ ] Business opportunities trigger "start" actions
- [ ] User can correct misinterpreted intent
- [ ] System learns from corrections
- [ ] Plans are relevant to actual intent

## Success Metrics

1. **Intent Accuracy**: % of times AI correctly interprets user intent
2. **Correction Rate**: How often users need to correct the AI
3. **Completion Rate**: % of action plans actually completed
4. **User Satisfaction**: Feedback on relevance of generated plans

## Notes for Next Developer

**Chris says**: "The AI needs to understand context. When I click on a job, I want to APPLY for it, not learn the skill from scratch. This is costing users real opportunities while the AI teaches them basics they already know!"

**Key Insight**: The difference between "I want this job" and "I want to learn this skill" is HUGE for users trying to generate income quickly. Getting this wrong wastes critical time.

**Remember**: Users coming to Income Builder are looking for immediate income opportunities, not long-term education plans. Default to action-oriented, application-focused plans unless explicitly told otherwise.