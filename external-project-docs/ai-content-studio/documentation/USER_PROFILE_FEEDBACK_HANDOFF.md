# User Profile & Feedback Systems - Implementation Handoff

## Overview
This document outlines the implementation requirements for two critical features:
1. **User Profile System** - Auto-populate campaign information
2. **AI Feedback System** - Rate and improve AI-generated content

---

## 🧑‍💼 User Profile System

### Purpose
Allow users to save their business information once and have it automatically populate in all new campaigns, eliminating repetitive data entry.

### Database Schema

```python
# backend/content/models_user_profile.py

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Business Information
    company_name = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ], blank=True)
    
    # Products/Services
    primary_product = models.CharField(max_length=500, blank=True)
    product_description = models.TextField(blank=True)
    unique_selling_points = models.JSONField(default=list)  # List of USPs
    
    # Target Audience
    target_audience = models.TextField(blank=True)
    customer_personas = models.JSONField(default=list)  # List of persona objects
    geographic_markets = models.JSONField(default=list)  # List of markets
    
    # Brand Voice
    brand_tone = models.CharField(max_length=50, default='professional', choices=[
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('friendly', 'Friendly'),
        ('authoritative', 'Authoritative'),
        ('playful', 'Playful'),
        ('inspirational', 'Inspirational'),
    ])
    brand_values = models.JSONField(default=list)  # List of core values
    content_guidelines = models.TextField(blank=True)  # Do's and don'ts
    
    # Marketing Preferences
    preferred_channels = models.JSONField(default=list)  # ['email', 'social', 'blog', etc.]
    marketing_goals = models.JSONField(default=list)  # ['awareness', 'leads', 'sales', etc.]
    competitor_info = models.TextField(blank=True)
    
    # AI Preferences
    ai_creativity_level = models.FloatField(default=0.7)  # 0.1 to 1.0
    preferred_content_length = models.CharField(max_length=20, default='medium', choices=[
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
        ('extra_long', 'Extra Long'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
```

### API Endpoints

```python
# backend/api/views_user_profile.py

class UserProfileView(APIView):
    """
    GET /api/user/profile/ - Get current user's profile
    PUT /api/user/profile/ - Update profile
    """
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)
    
    def put(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ProfileQuickSetupView(APIView):
    """
    POST /api/user/profile/quick-setup/ - Wizard for initial setup
    """
    
    def post(self, request):
        # Guided setup with AI assistance
        # Takes basic info and generates complete profile
        pass
```

### Frontend Implementation

```typescript
// ai-studio-web/src/pages/profile/ProfilePage.tsx

interface UserProfile {
  company_name: string;
  company_description: string;
  industry: string;
  company_size: string;
  primary_product: string;
  product_description: string;
  target_audience: string;
  brand_tone: string;
  // ... other fields
}

export function ProfilePage() {
  // Profile edit form with sections:
  // 1. Company Information
  // 2. Products & Services
  // 3. Target Audience
  // 4. Brand Voice
  // 5. AI Preferences
  
  // Quick Setup Wizard for new users
  // - Step 1: Basic company info
  // - Step 2: Product/service description
  // - Step 3: Target audience
  // - Step 4: Brand voice selection
  // - AI generates the rest
}
```

### Campaign Integration

```typescript
// When creating a new campaign:

const createCampaignFromProfile = async () => {
  const profile = await userService.getProfile();
  
  const campaign = await campaignService.createCampaign({
    title: 'New Campaign',
    description: '',
    campaign_type: 'multi',
    // Auto-populate from profile
    target_audience: profile.target_audience,
    config: {
      business: profile.company_name,
      product: profile.primary_product,
    },
    tone: profile.brand_tone,
  });
  
  return campaign;
};
```

### First-Time User Experience

1. **Onboarding Flow**:
   - After signup, prompt to complete profile
   - Quick setup wizard (5 minutes)
   - AI assists in generating complete profile from minimal input

2. **Progressive Disclosure**:
   - Start with essential fields
   - Add more details over time
   - Show completion percentage

3. **Smart Defaults**:
   - Analyze first few campaigns to suggest profile updates
   - Learn from user's content choices

---

## ⭐ AI Feedback System

### Purpose
Allow users to rate AI-generated content and provide feedback to improve future generations.

### Database Schema

```python
# backend/content/models_feedback.py

class ContentFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='feedback')
    
    # Rating
    rating = models.IntegerField(choices=[
        (1, '1 - Poor'),
        (2, '2 - Below Average'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ])
    
    # Detailed Feedback
    accuracy = models.IntegerField(null=True, blank=True)  # 1-5
    creativity = models.IntegerField(null=True, blank=True)  # 1-5
    relevance = models.IntegerField(null=True, blank=True)  # 1-5
    tone_match = models.IntegerField(null=True, blank=True)  # 1-5
    
    # What worked/didn't work
    liked = models.TextField(blank=True)  # What user liked
    disliked = models.TextField(blank=True)  # What needs improvement
    suggestions = models.TextField(blank=True)  # Specific suggestions
    
    # Actions taken
    was_edited = models.BooleanField(default=False)
    was_regenerated = models.BooleanField(default=False)
    was_used = models.BooleanField(default=False)  # Actually used in production
    
    # Performance (if used)
    performance_metrics = models.JSONField(default=dict, blank=True)
    # e.g., {'clicks': 100, 'conversions': 10, 'engagement_rate': 0.15}
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content']  # One feedback per user per content

class CampaignContentFeedback(models.Model):
    """Specific to campaign content"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign_content = models.ForeignKey(CampaignContent, on_delete=models.CASCADE)
    
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    feedback_text = models.TextField(blank=True)
    
    # Track edits
    original_content = models.TextField()  # Store original for comparison
    edited_content = models.TextField(blank=True)  # If user edited
    
    # Effectiveness tracking
    performed_well = models.BooleanField(null=True)  # Did it work in real use?
    
    created_at = models.DateTimeField(auto_now_add=True)
```

### Frontend Components

```typescript
// ai-studio-web/src/components/feedback/FeedbackWidget.tsx

interface FeedbackWidgetProps {
  contentId: string;
  contentType: 'blog' | 'email' | 'social' | 'ebook' | 'podcast';
  onFeedbackSubmit?: (feedback: Feedback) => void;
}

export function FeedbackWidget({ contentId, contentType, onFeedbackSubmit }: FeedbackWidgetProps) {
  return (
    <div className="feedback-widget">
      {/* Quick Rating */}
      <div className="quick-rating flex gap-2">
        <button onClick={() => submitRating(1)}>👎</button>
        <button onClick={() => submitRating(5)}>👍</button>
      </div>
      
      {/* Detailed Feedback Modal */}
      <button onClick={openDetailedFeedback}>
        Provide Detailed Feedback
      </button>
      
      {/* One-click Actions */}
      <div className="quick-actions">
        <button onClick={regenerateWithFeedback}>
          Regenerate Better Version
        </button>
        <button onClick={saveAsGoodExample}>
          Save as Good Example
        </button>
      </div>
    </div>
  );
}
```

### Feedback Integration Points

1. **Campaign Detail Page**:
   - Star rating on each content item
   - "This worked well" / "Needs improvement" buttons
   - Edit tracking (compare original vs edited)

2. **After Generation**:
   - Immediate feedback option
   - "Not quite right? Tell us why" prompt

3. **Gallery View**:
   - Show ratings on content
   - Filter by rating
   - "Top Rated" section

### AI Learning Integration

```python
# backend/ai_partner/feedback_learning.py

class FeedbackLearner:
    """
    Use feedback to improve AI prompts
    """
    
    def analyze_feedback_patterns(self, user_id):
        """
        Identify what user consistently likes/dislikes
        """
        feedback = ContentFeedback.objects.filter(user_id=user_id)
        
        patterns = {
            'preferred_tone': self.analyze_tone_preferences(feedback),
            'optimal_length': self.analyze_length_preferences(feedback),
            'style_preferences': self.analyze_style_patterns(feedback),
            'common_edits': self.analyze_edit_patterns(feedback),
        }
        
        return patterns
    
    def enhance_prompt_with_feedback(self, base_prompt, user_id):
        """
        Modify prompts based on user's feedback history
        """
        patterns = self.analyze_feedback_patterns(user_id)
        
        enhanced_prompt = base_prompt
        
        # Add user preferences
        if patterns['preferred_tone']:
            enhanced_prompt += f"\nTone preference: {patterns['preferred_tone']}"
        
        # Add examples of what worked
        good_examples = self.get_highly_rated_content(user_id)
        if good_examples:
            enhanced_prompt += f"\nStyle similar to: {good_examples[0]}"
        
        # Avoid what didn't work
        poor_patterns = self.get_poor_patterns(user_id)
        if poor_patterns:
            enhanced_prompt += f"\nAvoid: {poor_patterns}"
        
        return enhanced_prompt
```

### Feedback Analytics Dashboard

```typescript
// ai-studio-web/src/pages/analytics/FeedbackAnalytics.tsx

export function FeedbackAnalytics() {
  // Show:
  // - Average ratings by content type
  // - Most successful content (highest ratings + performance)
  // - Common improvement requests
  // - Learning progress over time
  // - Suggestions for profile updates based on feedback
}
```

---

## Implementation Priority

### Phase 1: Basic User Profile (1-2 days)
1. Create UserProfile model
2. Add profile API endpoints
3. Create basic profile edit page
4. Integrate with campaign creation

### Phase 2: Quick Feedback (1 day)
1. Add rating field to CampaignContent
2. Add thumbs up/down buttons
3. Store ratings in database

### Phase 3: Advanced Profile Features (2-3 days)
1. Profile setup wizard
2. AI-assisted profile generation
3. Multiple personas support
4. Team profiles (shared business info)

### Phase 4: Detailed Feedback System (2-3 days)
1. Detailed feedback forms
2. Edit tracking
3. Performance metrics integration
4. Feedback analytics dashboard

### Phase 5: AI Learning (3-4 days)
1. Feedback pattern analysis
2. Prompt enhancement based on feedback
3. Personalized AI responses
4. A/B testing with feedback

---

## Quick Start Implementation

To get started quickly, begin with:

1. **Minimal Profile**: Just company name, product, and audience
2. **Simple Rating**: 1-5 stars on generated content
3. **Basic Integration**: Auto-populate campaigns from profile

This can be done in 1-2 days and provides immediate value.

---

## Testing Considerations

1. **Profile Completeness**:
   - Test with empty profiles
   - Test with partial profiles
   - Test with complete profiles

2. **Feedback Collection**:
   - Ensure feedback is optional
   - Test bulk feedback submission
   - Test feedback analytics

3. **Performance**:
   - Profile caching
   - Feedback aggregation optimization
   - Learning algorithm efficiency

---

## Future Enhancements

1. **Team Collaboration**:
   - Shared company profiles
   - Team feedback aggregation
   - Department-specific settings

2. **Advanced Learning**:
   - Neural network for preference prediction
   - Cross-user learning (similar businesses)
   - Industry-specific optimizations

3. **Integration Extensions**:
   - CRM integration for customer data
   - Analytics platform integration
   - Marketing automation connections

---

## Notes for Implementation

- Start simple, iterate based on user feedback
- Profile should be optional but encouraged
- Feedback should be frictionless (one-click when possible)
- Show users how their feedback improves results
- Consider GDPR/privacy for profile data
- Allow export/import of profile data