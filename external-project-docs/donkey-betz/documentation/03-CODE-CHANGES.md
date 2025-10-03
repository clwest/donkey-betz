# Specific Code Changes Required

## File 1: backend/ai_partner/personal_ai_services.py

### Change 1: Import Sophisticated Prompting System
**Line**: 27 (add to imports)
```python
from prompting_system.api_views.component_views import generate_ai_prompt_internal
from agent_orchestra.prompting_bridge import AgentPromptingBridge
```

### Change 2: Replace Hardcoded User Context
**Lines**: 2158-2164
**Replace**:
```python
user_context = {
    'industry': 'Technology',
    'business_stage': 'Growth',
    'expertise_level': 'Intermediate',
    'urgency_level': 'standard'
}
```

**With**:
```python
user_context = await self._build_real_user_context(user)
```

### Change 3: Add Real User Context Method
**Line**: After line 2500 (new method)
```python
async def _build_real_user_context(self, user: User) -> Dict[str, Any]:
    """Build actual user context from profile and history"""
    from asgiref.sync import sync_to_async
    from ai_partner.models import UserLifeProfile
    
    context = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }
    
    # Get user profile if exists
    try:
        profile = await sync_to_async(UserLifeProfile.objects.get)(user=user)
        context.update({
            'industry': profile.profession or 'General',
            'expertise_level': getattr(profile, 'expertise_level', 'intermediate'),
            'interests': profile.interests or [],
            'skills': profile.skills or [],
            'goals': profile.goals or [],
            'challenges': profile.challenges or [],
            'values': profile.values or [],
            'current_role': profile.current_role or 'User',
            'business_stage': getattr(profile, 'business_stage', 'individual')
        })
    except UserLifeProfile.DoesNotExist:
        context.update({
            'industry': 'General',
            'expertise_level': 'intermediate',
            'business_stage': 'individual'
        })
    
    # Get recent conversation topics
    try:
        from shared_memory.models import UnifiedMemoryEntry
        recent_memories = await sync_to_async(list)(
            UnifiedMemoryEntry.objects.filter(
                user=user,
                source_system='conversation'
            ).order_by('-created_at')[:10]
        )
        
        recent_topics = []
        for memory in recent_memories:
            if memory.topics:
                recent_topics.extend(memory.topics)
        
        context['recent_topics'] = list(set(recent_topics))[:5]
    except:
        context['recent_topics'] = []
    
    # Determine urgency from message
    context['urgency_level'] = 'standard'  # Can be enhanced with actual urgency detection
    
    return context
```

### Change 4: Add Task Analysis Method
**Line**: After _build_real_user_context (new method)
```python
async def _analyze_task_characteristics(self, task: str) -> Dict[str, Any]:
    """Analyze task to determine optimal prompt structure"""
    task_lower = task.lower()
    
    # Quick task type detection
    if any(word in task_lower for word in ['analyze', 'review', 'evaluate', 'assess']):
        task_type = 'analysis'
        output_type = 'analytical_report'
        max_length = 800
    elif any(word in task_lower for word in ['create', 'write', 'generate', 'design']):
        task_type = 'creation'
        output_type = 'creative_output'
        max_length = 'variable'
    elif any(word in task_lower for word in ['research', 'find', 'search', 'investigate']):
        task_type = 'research'
        output_type = 'research_findings'
        max_length = 600
    elif any(word in task_lower for word in ['what is', 'how to', 'explain', 'tell me']):
        task_type = 'information'
        output_type = 'concise_explanation'
        max_length = 200
    elif any(word in task_lower for word in ['schedule', 'book', 'send', 'reminder']):
        task_type = 'action'
        output_type = 'action_confirmation'
        max_length = 100
    else:
        task_type = 'general'
        output_type = 'structured_response'
        max_length = 500
    
    # Extract domains
    domains = []
    if any(word in task_lower for word in ['business', 'company', 'startup', 'market']):
        domains.append('business')
    if any(word in task_lower for word in ['code', 'api', 'technical', 'software']):
        domains.append('technical')
    if any(word in task_lower for word in ['financial', 'stock', 'investment', 'crypto']):
        domains.append('financial')
    if any(word in task_lower for word in ['marketing', 'campaign', 'brand', 'social']):
        domains.append('marketing')
    
    if not domains:
        domains = ['general']
    
    # Determine focus areas based on task
    focus_areas = []
    if len(task.split()) < 10:
        focus_areas.append('quick_response')
    if '?' in task:
        focus_areas.append('question_answering')
    if 'strategy' in task_lower or 'plan' in task_lower:
        focus_areas.append('strategic_planning')
    
    return {
        'task_type': task_type,
        'output_type': output_type,
        'domains': domains,
        'focus_areas': focus_areas or ['general_assistance'],
        'max_length': max_length,
        'complexity': 'simple' if len(task.split()) < 15 else 'complex'
    }
```

### Change 5: Replace IntelligentAgentPromptBuilder Usage
**Lines**: 2152-2218
**Replace entire block with**:
```python
# 🚀 SOPHISTICATED PROMPTING SYSTEM - Use AI-powered prompt generation
try:
    # Analyze task characteristics
    task_characteristics = await self._analyze_task_characteristics(task_description)
    
    logger.info(f"🎯 Task Analysis: type={task_characteristics['task_type']}, domains={task_characteristics['domains']}")
    
    # Initialize prompting bridge
    prompting_bridge = AgentPromptingBridge()
    
    # Try sophisticated AI prompt generation first
    if prompting_bridge._prompting_system_available:
        try:
            # Generate AI-powered prompt
            prompt_result = await sync_to_async(generate_ai_prompt_internal)(
                description=task_description,
                agent_specialization={
                    'name': agent_name,
                    'domains': task_characteristics['domains'],
                    'expertiseLevel': user_context.get('expertise_level', 'intermediate'),
                    'focusAreas': task_characteristics['focus_areas']
                },
                user_context=user_context,
                task_characteristics=task_characteristics,
                memory_context=memory_context,
                include_orchestration=False
            )
            
            if 'error' not in prompt_result:
                enhanced_task = prompt_result.get('prompt', task_description)
                prompt_metadata = prompt_result.get('metadata', {})
                
                logger.info(f"✅ AI-powered prompt generated: {len(enhanced_task)} chars")
                logger.info(f"🔧 Prompt metadata: {prompt_metadata}")
                
                # Update orchestration with sophisticated prompting metadata
                orchestration.task_analysis['sophisticated_prompting'] = {
                    'applied': True,
                    'system': 'ai_powered',
                    'task_type': task_characteristics['task_type'],
                    'domains': task_characteristics['domains'],
                    'prompt_length': len(enhanced_task),
                    'metadata': prompt_metadata
                }
            else:
                raise Exception(f"AI prompt generation failed: {prompt_result.get('error')}")
                
        except Exception as e:
            logger.warning(f"AI prompt generation failed, using bridge: {e}")
            
            # Fallback to prompting bridge
            enhanced_task = prompting_bridge.get_enhanced_prompt(
                agent_name=agent_name,
                base_prompt=agent_template.system_prompt_template,
                task=task_description,
                context={
                    'user_context': user_context,
                    'task_context': task_characteristics,
                    'memory_context': memory_context
                },
                user_id=user.id
            )
            
            orchestration.task_analysis['sophisticated_prompting'] = {
                'applied': True,
                'system': 'prompting_bridge',
                'fallback_reason': str(e)
            }
    else:
        # Use legacy enhancement through bridge
        enhanced_task = prompting_bridge._enhance_prompt_legacy(
            agent_template.system_prompt_template,
            task_description,
            {'user_context': user_context, 'memory': memory_context}
        )
        
        orchestration.task_analysis['sophisticated_prompting'] = {
            'applied': False,
            'system': 'legacy',
            'reason': 'prompting_system_unavailable'
        }
    
    await sync_to_async(orchestration.save)()
    
except Exception as e:
    logger.error(f"❌ Sophisticated prompting failed completely: {e}", exc_info=True)
    enhanced_task = task_description  # Ultimate fallback
    
    orchestration.task_analysis['sophisticated_prompting'] = {
        'applied': False,
        'error': str(e),
        'fallback': 'original_task'
    }
    await sync_to_async(orchestration.save)()
```

## File 2: backend/agent_orchestra/orchestrator.py

### Change 1: Add Prompting Bridge to SpecializedAgent
**Line**: 844 (in __init__)
```python
def __init__(self, agent_instance: AgentInstance):
    self.instance = agent_instance
    self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    self.tools = []
    self.prompt_enhancer = UniversalAgentPromptEnhancer()
    self.mythology_integration = MythologyIntegration()
    
    # Add prompting bridge
    from agent_orchestra.prompting_bridge import AgentPromptingBridge
    self.prompting_bridge = AgentPromptingBridge()
    self.prompt_tracking = None
```

### Change 2: Update generate_agent_prompt Method
**Lines**: 945-1010
**Replace entire method with**:
```python
async def generate_agent_prompt(self) -> str:
    """Create enhanced specialized prompt using sophisticated prompting system"""
    
    # Get instance data
    @sync_to_async
    def get_instance_data():
        return {
            'base_prompt': self.instance.template.system_prompt_template,
            'username': self.instance.user.username,
            'user_id': self.instance.user.id,
            'user_context': self.instance.user_context,
            'assigned_task': self.instance.assigned_task,
            'task_context': self.instance.task_context,
            'template_name': self.instance.template.name,
            'specialization': self.instance.template.specialization
        }
    
    instance_data = await get_instance_data()
    
    # Try sophisticated prompting first
    if self.prompting_bridge._prompting_system_available:
        try:
            # Get memory context from task context
            memory_context = instance_data['task_context'].get('memory_context', {})
            
            # Build comprehensive context
            comprehensive_context = {
                'user_name': instance_data['username'],
                'user_context': instance_data['user_context'],
                'task_context': instance_data['task_context'],
                'memory_context': memory_context,
                'available_tools': self.tools,
                'template_specialization': instance_data['specialization']
            }
            
            # Get enhanced prompt from bridge
            enhanced_prompt = self.prompting_bridge.get_enhanced_prompt(
                agent_name=instance_data['template_name'],
                base_prompt=instance_data['base_prompt'],
                task=instance_data['assigned_task'],
                context=comprehensive_context,
                user_id=instance_data['user_id']
            )
            
            # Track for effectiveness monitoring
            self.prompt_tracking = {
                'prompt': enhanced_prompt,
                'start_time': time.time(),
                'agent_name': instance_data['template_name']
            }
            
            logger.info(f"✅ Using sophisticated prompt for {instance_data['template_name']}")
            return enhanced_prompt
            
        except Exception as e:
            logger.warning(f"Sophisticated prompting failed: {e}, using fallback")
    
    # Fallback to current prompt enhancer
    context = {
        'user_name': instance_data['username'],
        'user_context': instance_data['user_context'],
        'task_context': instance_data['task_context'],
        'available_tools': self.tools,
        'template_specialization': instance_data['specialization']
    }
    
    # Map agent name to type for enhancer
    agent_type_mapping = {
        'Market Intelligence Agent': 'market_intelligence',
        'Financial Agent': 'financial_analyst',
        'Business Agent': 'business_model',
        'Research Agent': 'market_intelligence',
        'Technical Agent': 'technical_research',
        'Content Agent': 'content_creation'
    }
    
    agent_type = agent_type_mapping.get(instance_data['template_name'], 'technical_research')
    
    return self.prompt_enhancer.generate_enhanced_prompt(
        agent_type=agent_type,
        task=instance_data['assigned_task'],
        context=context
    )
```

### Change 3: Add Prompt Effectiveness Tracking
**Line**: After line 910 (in execute_task method, after report generation)
```python
# Track prompt effectiveness if using sophisticated system
if self.prompt_tracking and self.prompting_bridge:
    try:
        execution_time = time.time() - self.prompt_tracking['start_time']
        
        self.prompting_bridge.track_execution(
            agent_name=self.prompt_tracking['agent_name'],
            prompt=self.prompt_tracking['prompt'],
            response=report,
            execution_time=execution_time,
            success=self.instance.current_status == 'completed',
            user_id=self.instance.user.id
        )
        
        logger.info(f"📊 Tracked prompt execution: {execution_time:.2f}s, success={self.instance.current_status == 'completed'}")
    except Exception as e:
        logger.warning(f"Could not track prompt execution: {e}")
```

## File 3: backend/prompting_system/api_views/component_views.py

### Change 1: Enhance generate_ai_prompt_internal
**Add task_characteristics parameter handling**
```python
def generate_ai_prompt_internal(
    description: str,
    agent_specialization: Dict[str, Any] = None,
    user_context: Dict[str, Any] = None,
    task_characteristics: Dict[str, Any] = None,  # NEW
    memory_context: str = None,  # NEW
    include_orchestration: bool = False
) -> Dict[str, Any]:
    """
    Enhanced internal AI prompt generation with task awareness
    """
    try:
        # Add task characteristics to prompt generation
        if task_characteristics:
            # Adjust prompt structure based on task type
            if task_characteristics.get('task_type') == 'information':
                # For simple info requests, use concise prompt
                base_template = "Provide a clear, concise answer to: {description}"
            elif task_characteristics.get('task_type') == 'action':
                # For actions, use confirmation-focused prompt
                base_template = "Execute and confirm: {description}"
            else:
                # Use full template for complex tasks
                base_template = None
        
        # Include memory context if provided
        if memory_context:
            description = f"{description}\n\nRelevant Context:\n{memory_context[:500]}"
        
        # Rest of existing implementation...
```

## File 4: backend/ai_partner/services/intelligent_agent_prompt_builder.py

### Change 1: Make Prompt Structure Dynamic
**Replace static _construct_comprehensive_prompt method**
```python
def _construct_comprehensive_prompt(self, **kwargs) -> str:
    """Construct prompt based on task characteristics"""
    
    # Get task characteristics
    task_chars = kwargs.get('task_characteristics', {})
    task_type = task_chars.get('task_type', 'general')
    max_length = task_chars.get('max_length', 500)
    
    # Simple tasks get simple prompts
    if task_type == 'information':
        return f"""# Agent: {kwargs['agent_name']}
Task: {kwargs['original_task']}

Provide a clear, concise answer (max {max_length} words).
Focus on accuracy and relevance.
{kwargs.get('context_background', '')}
"""
    
    # Action tasks get action prompts
    elif task_type == 'action':
        return f"""# Agent: {kwargs['agent_name']}
Action Required: {kwargs['original_task']}

Execute the requested action and confirm completion.
{kwargs.get('tools_resources', '')}

Provide:
1. Action status (success/failure)
2. Brief details
3. Any necessary follow-up
"""
    
    # Complex tasks get full structure
    else:
        # Use existing comprehensive template
        return super()._construct_comprehensive_prompt(**kwargs)
```

## Testing Files

### File: backend/tests/test_prompting_improvements.py
```python
"""Test suite for prompting system improvements"""

import pytest
from django.test import TestCase
from unittest.mock import Mock, patch, AsyncMock

class TestPromptingImprovements(TestCase):
    
    @pytest.mark.asyncio
    async def test_real_user_context_used(self):
        """Test that real user context is pulled from profile"""
        # Test implementation
        
    @pytest.mark.asyncio
    async def test_task_characteristics_analysis(self):
        """Test task analysis produces correct characteristics"""
        # Test implementation
        
    @pytest.mark.asyncio
    async def test_sophisticated_system_called(self):
        """Test that sophisticated prompting system is used"""
        # Test implementation
        
    @pytest.mark.asyncio
    async def test_prompt_length_matches_task(self):
        """Test that simple tasks get short prompts"""
        # Test implementation
```