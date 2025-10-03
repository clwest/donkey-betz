# Implementation Plan: Fix Agent Prompting System

## Overview
Step-by-step plan to replace generic template prompting with sophisticated, task-specific AI-powered prompts.

## Phase 1: Connect the Sophisticated Prompting System

### Step 1.1: Modify deploy_agent_magic()
**File**: `backend/ai_partner/personal_ai_services.py`
**Line**: 2152-2218

**Replace**:
```python
from ai_partner.services.intelligent_agent_prompt_builder import intelligent_agent_prompt_builder
```

**With**:
```python
from prompting_system.api_views.component_views import generate_ai_prompt_internal
from agent_orchestra.prompting_bridge import AgentPromptingBridge
```

### Step 1.2: Implement AI Prompt Generation
**New Implementation**:
```python
# Initialize prompting bridge
prompting_bridge = AgentPromptingBridge()

# Extract task characteristics
task_characteristics = await self._analyze_task_characteristics(task_description)

# Build proper user context from actual data
real_user_context = await self._build_real_user_context(user)

# Generate AI-powered prompt
if prompting_bridge._prompting_system_available:
    prompt_result = await sync_to_async(generate_ai_prompt_internal)(
        description=task_description,
        agent_specialization={
            'domains': task_characteristics['domains'],
            'expertiseLevel': real_user_context['expertise_level'],
            'focusAreas': task_characteristics['focus_areas'],
            'outputType': task_characteristics['output_type']
        },
        user_context=real_user_context,
        memory_context=memory_context,
        include_orchestration=False
    )
    
    if 'error' not in prompt_result:
        enhanced_task = prompt_result['prompt']
        prompt_metadata = prompt_result['metadata']
    else:
        # Fallback to enhanced legacy prompt
        enhanced_task = prompting_bridge.get_enhanced_prompt(
            agent_name=agent_name,
            base_prompt=agent_template.system_prompt_template,
            task=task_description,
            context={'user_context': real_user_context, 'memory': memory_context},
            user_id=user.id
        )
else:
    # Use bridge's legacy enhancement
    enhanced_task = prompting_bridge._enhance_prompt_legacy(
        agent_template.system_prompt_template,
        task_description,
        {'user_context': real_user_context}
    )
```

## Phase 2: Implement Real User Context

### Step 2.1: Create User Context Builder
**New Method in** `personal_ai_services.py`:

```python
async def _build_real_user_context(self, user: User) -> Dict[str, Any]:
    """Build actual user context from profile and history"""
    from asgiref.sync import sync_to_async
    
    # Get user profile
    try:
        profile = await sync_to_async(
            UserLifeProfile.objects.get
        )(user=user)
        
        profile_data = {
            'industry': profile.profession or 'General',
            'expertise_level': profile.expertise_level or 'intermediate',
            'interests': profile.interests or [],
            'skills': profile.skills or [],
            'goals': profile.goals or [],
            'challenges': profile.challenges or [],
            'values': profile.values or []
        }
    except:
        profile_data = {
            'industry': 'General',
            'expertise_level': 'intermediate'
        }
    
    # Get recent interaction patterns
    recent_interactions = await self._get_recent_interaction_patterns(user)
    
    # Get user preferences from settings
    user_preferences = await self._get_user_preferences(user)
    
    return {
        **profile_data,
        'recent_topics': recent_interactions.get('topics', []),
        'communication_style': recent_interactions.get('style', 'professional'),
        'typical_tasks': recent_interactions.get('task_types', []),
        'preferences': user_preferences,
        'user_id': user.id,
        'username': user.username
    }
```

### Step 2.2: Create Task Analyzer
**New Method**:

```python
async def _analyze_task_characteristics(self, task: str) -> Dict[str, Any]:
    """Analyze task to determine optimal prompt structure"""
    
    # Determine task type
    task_lower = task.lower()
    
    # Analysis tasks
    if any(word in task_lower for word in ['analyze', 'review', 'evaluate', 'assess', 'check']):
        task_type = 'analysis'
        output_type = 'analytical_report'
        
    # Creation tasks
    elif any(word in task_lower for word in ['create', 'write', 'generate', 'design', 'build']):
        task_type = 'creation'
        output_type = 'creative_output'
        
    # Research tasks
    elif any(word in task_lower for word in ['research', 'find', 'search', 'discover', 'investigate']):
        task_type = 'research'
        output_type = 'research_findings'
        
    # Quick info tasks
    elif any(word in task_lower for word in ['what is', 'how to', 'explain', 'tell me']):
        task_type = 'information'
        output_type = 'concise_explanation'
        
    # Action tasks
    elif any(word in task_lower for word in ['schedule', 'book', 'send', 'call', 'reminder']):
        task_type = 'action'
        output_type = 'action_confirmation'
        
    else:
        task_type = 'general'
        output_type = 'structured_response'
    
    # Extract domains
    domains = []
    domain_keywords = {
        'business': ['business', 'company', 'startup', 'revenue', 'sales', 'market'],
        'technical': ['code', 'api', 'database', 'system', 'technical', 'software'],
        'financial': ['financial', 'money', 'investment', 'stock', 'trading', 'crypto'],
        'creative': ['design', 'creative', 'content', 'video', 'image', 'art'],
        'marketing': ['marketing', 'campaign', 'audience', 'brand', 'social'],
        'personal': ['personal', 'life', 'health', 'relationship', 'goal']
    }
    
    for domain, keywords in domain_keywords.items():
        if any(kw in task_lower for kw in keywords):
            domains.append(domain)
    
    if not domains:
        domains = ['general']
    
    # Determine focus areas
    focus_areas = []
    if len(task.split()) < 10:
        focus_areas.append('quick_response')
    if '?' in task:
        focus_areas.append('question_answering')
    if any(word in task_lower for word in ['strategy', 'plan', 'roadmap']):
        focus_areas.append('strategic_planning')
    if any(word in task_lower for word in ['implement', 'execute', 'deploy']):
        focus_areas.append('implementation')
    
    return {
        'task_type': task_type,
        'output_type': output_type,
        'domains': domains,
        'focus_areas': focus_areas or ['general_assistance'],
        'estimated_complexity': 'simple' if len(task.split()) < 15 else 'complex',
        'requires_research': task_type in ['research', 'analysis'],
        'requires_creativity': task_type in ['creation', 'creative']
    }
```

## Phase 3: Integrate with Agent Execution

### Step 3.1: Update SpecializedAgent
**File**: `backend/agent_orchestra/orchestrator.py`
**Method**: `generate_agent_prompt()`

**Add Prompting Bridge Integration**:
```python
async def generate_agent_prompt(self) -> str:
    """Create enhanced specialized prompt with prompting system integration"""
    
    # Get instance data
    instance_data = await self._get_instance_data()
    
    # Initialize prompting bridge
    from agent_orchestra.prompting_bridge import AgentPromptingBridge
    prompting_bridge = AgentPromptingBridge()
    
    # Use sophisticated prompting if available
    if prompting_bridge._prompting_system_available:
        enhanced_prompt = prompting_bridge.get_enhanced_prompt(
            agent_name=instance_data['template_name'],
            base_prompt=instance_data['base_prompt'],
            task=instance_data['assigned_task'],
            context={
                'user_context': instance_data['user_context'],
                'task_context': instance_data['task_context'],
                'memory_context': instance_data.get('memory_context', {})
            },
            user_id=self.instance.user.id
        )
        
        # Track this prompt usage
        self.prompt_tracking = {
            'prompt': enhanced_prompt,
            'start_time': time.time(),
            'agent_name': instance_data['template_name']
        }
        
        return enhanced_prompt
    
    # Fallback to current enhancement
    return self.prompt_enhancer.generate_enhanced_prompt(...)
```

### Step 3.2: Add Prompt Effectiveness Tracking
**After Task Execution**:
```python
# In execute_task() after getting results
if hasattr(self, 'prompt_tracking') and prompting_bridge:
    execution_time = time.time() - self.prompt_tracking['start_time']
    
    prompting_bridge.track_execution(
        agent_name=self.prompt_tracking['agent_name'],
        prompt=self.prompt_tracking['prompt'],
        response=report,
        execution_time=execution_time,
        success=self.instance.current_status == 'completed',
        user_id=self.instance.user.id
    )
```

## Phase 4: Task-Specific Prompt Templates

### Step 4.1: Create Template Selector
**New File**: `backend/ai_partner/services/task_prompt_selector.py`

```python
class TaskPromptSelector:
    """Select appropriate prompt template based on task characteristics"""
    
    PROMPT_TEMPLATES = {
        'quick_info': {
            'structure': 'direct_answer',
            'max_length': 200,
            'format': 'concise',
            'sections': ['answer', 'source']
        },
        'analysis': {
            'structure': 'analytical_report',
            'max_length': 1000,
            'format': 'structured',
            'sections': ['summary', 'analysis', 'findings', 'recommendations']
        },
        'creation': {
            'structure': 'creative_output',
            'max_length': 'variable',
            'format': 'task_specific',
            'sections': ['output', 'variations', 'notes']
        },
        'research': {
            'structure': 'research_report',
            'max_length': 800,
            'format': 'cited',
            'sections': ['findings', 'sources', 'summary', 'next_steps']
        },
        'action': {
            'structure': 'action_result',
            'max_length': 100,
            'format': 'confirmation',
            'sections': ['status', 'details', 'next_action']
        }
    }
    
    @classmethod
    def select_template(cls, task_characteristics: Dict) -> Dict:
        """Select best template for task"""
        task_type = task_characteristics.get('task_type', 'general')
        
        # Quick responses for simple questions
        if 'quick_response' in task_characteristics.get('focus_areas', []):
            return cls.PROMPT_TEMPLATES['quick_info']
        
        # Map task type to template
        template_map = {
            'analysis': 'analysis',
            'creation': 'creation',
            'research': 'research',
            'information': 'quick_info',
            'action': 'action'
        }
        
        template_key = template_map.get(task_type, 'analysis')
        return cls.PROMPT_TEMPLATES[template_key]
```

## Phase 5: Testing and Validation

### Step 5.1: Create Test Suite
**File**: `backend/tests/test_prompting_improvements.py`

### Step 5.2: Validation Metrics
- Response length appropriate to task
- Structure matches task type
- User context properly included
- Memory context integrated
- No generic business language for technical tasks
- Concise responses for simple queries

## Implementation Order

1. **Day 1**: Implement Phase 1 (Connect Sophisticated System)
2. **Day 2**: Implement Phase 2 (Real User Context)
3. **Day 3**: Implement Phase 3 (Agent Integration)
4. **Day 4**: Implement Phase 4 (Task-Specific Templates)
5. **Day 5**: Testing and Refinement

## Success Criteria

1. ✅ Agents receive task-specific prompts
2. ✅ User context properly integrated
3. ✅ Response length matches task complexity
4. ✅ No hardcoded defaults
5. ✅ Sophisticated prompting system fully utilized
6. ✅ Prompt effectiveness tracked
7. ✅ Memory context included
8. ✅ Task type analysis working