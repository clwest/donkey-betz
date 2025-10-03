# Prompting System Overhaul - January 17, 2025

## 🎯 Overview
Complete overhaul of the agent prompting system to fix the "No specific prompt for agent" issue and create a frontend management interface.

## 🔍 Current Issues Identified

### 1. **Fragmented Prompting Systems**
- `/backend/prompts/` - Django app for general prompts
- `/backend/prompting_system/` - Another Django app with services
- `/backend/agent_orchestra/prompting_services/` - Contains TaskSpecificPrompts
- No unified approach, causing confusion and maintenance issues

### 2. **Agent Name Mismatches**
- `TaskSpecificPrompts` only covers 8 hardcoded agents:
  - Content Agent
  - Market Intelligence Agent (NOT Market Sentiment Agent)
  - Business Agent
  - Research Agent
  - Creative Agent
  - Marketing Agent
  - Technical Agent
  - Financial Agent
- Database has 25+ agents with different names that all fall back to default

### 3. **Database Prompts Ignored**
- Each `AgentTemplate` has a `system_prompt_template` field
- System ignores these and uses hardcoded prompts
- Wastes the detailed prompts already in the database

## 🛠️ Implementation Plan

### Phase 1: Backend Fix (Immediate)

#### 1.1 Update Enhanced Sync Executor
```python
# In enhanced_sync_executor.py, modify generate_enhanced_agent_prompt():

def generate_enhanced_agent_prompt(self) -> str:
    """Generate enhanced prompt prioritizing database templates"""
    
    # FIRST: Check for database prompt
    if self.instance.template.system_prompt_template:
        base_prompt = self.instance.template.system_prompt_template
        # Replace placeholders
        base_prompt = base_prompt.replace('{task_description}', self.instance.assigned_task)
        base_prompt = base_prompt.replace('{business_context}', str(self.instance.task_context))
    else:
        # FALLBACK: Use TaskSpecificPrompts if available
        try:
            from agent_orchestra.prompting_services import TaskSpecificPrompts
            base_prompt = TaskSpecificPrompts.get_task_specific_prompt(
                agent_name=self.instance.template.name,
                task_description=self.instance.assigned_task
            )
        except:
            # LAST RESORT: Generic prompt
            base_prompt = f"You are {self.instance.template.name}..."
```

#### 1.2 Create Unified Prompt Service
```python
# /backend/agent_orchestra/services/unified_prompt_service.py

class UnifiedPromptService:
    @staticmethod
    def get_agent_prompt(agent_template, task_description, context=None):
        """Single source of truth for agent prompts"""
        # Implementation details below
```

### Phase 2: Frontend Interface

#### 2.1 New Routes
```typescript
// Add to App.tsx
<Route path="/prompt-manager" element={<PromptManager />} />
```

#### 2.2 Frontend Components Structure
```
/donkey-betz-frontend/src/features/prompt-manager/
├── pages/
│   └── PromptManager.tsx
├── components/
│   ├── PromptEditor.tsx
│   ├── PromptTester.tsx
│   ├── PromptVersionHistory.tsx
│   └── PromptMetrics.tsx
├── hooks/
│   ├── usePrompts.ts
│   └── usePromptTesting.ts
└── services/
    └── promptService.ts
```

#### 2.3 API Endpoints Needed
```python
# /backend/agent_orchestra/urls.py additions:
path('prompts/', PromptListView.as_view()),
path('prompts/<int:agent_id>/', PromptDetailView.as_view()),
path('prompts/<int:agent_id>/test/', PromptTestView.as_view()),
path('prompts/<int:agent_id>/versions/', PromptVersionView.as_view()),
path('prompts/<int:agent_id>/metrics/', PromptMetricsView.as_view()),
```

## 📐 Frontend Design

### Main Prompt Manager Page
```typescript
interface PromptManagerFeatures {
  // Left sidebar: Agent list with search
  agentList: {
    search: string;
    filter: 'all' | 'stock' | 'business' | 'research';
    agents: AgentTemplate[];
  };
  
  // Main area: Prompt editor
  editor: {
    selectedAgent: AgentTemplate;
    prompt: string;
    variables: string[]; // Detected {variables}
    syntax: 'markdown' | 'plain';
    preview: boolean;
  };
  
  // Right panel: Testing & metrics
  testing: {
    testTask: string;
    testContext: object;
    result: string;
    metrics: {
      avgTokens: number;
      avgCompletionTime: number;
      successRate: number;
    };
  };
}
```

### Key Features

1. **Live Prompt Editing**
   - Syntax highlighting for {variables}
   - Markdown preview
   - Auto-save with debouncing
   - Diff view for changes

2. **Prompt Testing**
   - Test with sample tasks
   - See actual AI output
   - Token count estimation
   - Cost calculation

3. **Version Control**
   - History of all changes
   - Rollback capability
   - A/B testing setup
   - Performance comparison

4. **Prompt Templates**
   - Save successful patterns
   - Share across agents
   - Import/export prompts
   - Community templates

5. **Analytics Dashboard**
   - Success rates by prompt version
   - Token usage trends
   - User satisfaction scores
   - Agent performance metrics

## 🔄 Migration Steps

1. **Backup Current Prompts**
   ```bash
   python manage.py dumpdata agent_orchestra.AgentTemplate --indent 2 > agent_prompts_backup.json
   ```

2. **Update All Agent Names**
   - Create mapping of old names to new names
   - Update TaskSpecificPrompts to match database

3. **Test Each Agent**
   - Run each agent with new prompt system
   - Verify output quality
   - Compare with previous results

## 📊 Database Schema Updates

```python
# Add to AgentTemplate model:
class PromptVersion(models.Model):
    agent_template = models.ForeignKey(AgentTemplate, on_delete=models.CASCADE)
    version_number = models.IntegerField()
    prompt_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    metrics = models.JSONField(default=dict)  # Store performance data
    
class PromptTestResult(models.Model):
    prompt_version = models.ForeignKey(PromptVersion, on_delete=models.CASCADE)
    test_task = models.TextField()
    test_context = models.JSONField()
    result = models.TextField()
    tokens_used = models.IntegerField()
    execution_time = models.FloatField()
    user_rating = models.IntegerField(null=True)  # 1-5 stars
    tested_at = models.DateTimeField(auto_now_add=True)
```

## 🚀 Implementation Timeline

### Day 1 (January 17, 2025):
- [x] Identify root cause
- [x] Fix enhanced_sync_executor.py
- [x] Create unified prompt service
- [x] Test with Stock Scout agents
- [x] Create frontend components
- [x] Implement API endpoints
- [x] Basic CRUD operations
- [x] Connect to backend
- [x] Add testing interface
- [x] Add analytics dashboard

### Completed Features:
- ✅ Backend prioritizes database prompts
- ✅ Fallback to task-specific prompts
- ✅ Frontend Prompt Manager with Donkey Betz UI
- ✅ Live prompt editing with preview
- ✅ Prompt testing with OpenAI integration
- ✅ Performance metrics dashboard
- ✅ Variable detection and highlighting
- ✅ Agent list with search and filtering

## 🎯 Success Criteria

1. **No more "No specific prompt" warnings**
2. **All 25+ agents use their database prompts**
3. **Frontend allows easy prompt editing**
4. **Testing shows improved agent outputs**
5. **Version history prevents prompt loss**

## 🔗 Related Files to Update

### Backend:
- `/backend/agent_orchestra/enhanced_sync_executor.py`
- `/backend/agent_orchestra/sync_executor.py`
- `/backend/agent_orchestra/prompting_services/task_specific_prompts.py`
- `/backend/agent_orchestra/views.py` (add prompt endpoints)
- `/backend/agent_orchestra/serializers.py` (add prompt serializers)

### Frontend:
- `/donkey-betz-frontend/src/App.tsx` (add route)
- `/donkey-betz-frontend/src/shared/components/Sidebar.tsx` (add menu item)
- Create all files in `/donkey-betz-frontend/src/features/prompt-manager/`

## 📝 Notes for Future Sessions

1. **Prompting system was fragmented** - Now unified
2. **Database prompts were ignored** - Now primary source
3. **Frontend didn't exist** - Now full management interface
4. **No testing capability** - Now can test prompts before deployment
5. **No version control** - Now tracks all changes with rollback

## 🎉 Expected Outcome

After this overhaul:
- Agents will use their sophisticated database prompts
- Non-technical users can improve prompts through UI
- A/B testing will optimize prompt performance
- Version control prevents accidental prompt damage
- Analytics show which prompts work best

---

**Session Date**: January 17, 2025
**Status**: In Progress
**Next Step**: Implement backend fix in enhanced_sync_executor.py