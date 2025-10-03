# Unified Prompting System Architecture

## Overview

The Unified Prompting System is a comprehensive framework that manages, optimizes, and evolves prompts across the entire Donkey Betz platform. It integrates with all major systems to provide context-aware, learning-enabled, and mythology-resistant prompting.

## Core Architecture

### 1. Prompt Registry (Central Hub)
```python
# Core models in prompting_system app
class PromptTemplate(models.Model):
    """Base prompt template with versioning"""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)  # agent, system, user, task
    template = models.TextField()
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey('self', null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_prompts')
    
    # Performance metrics
    usage_count = models.IntegerField(default=0)
    avg_response_quality = models.FloatField(null=True)
    avg_completion_time = models.FloatField(null=True)
    
    # Embeddings for similarity search
    embedding = models.JSONField(null=True)
    
class PromptComponent(models.Model):
    """Reusable prompt components"""
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # context, instruction, example, constraint
    content = models.TextField()
    is_dynamic = models.BooleanField(default=False)
    
class ComposedPrompt(models.Model):
    """Dynamically composed prompts from components"""
    id = models.UUIDField(primary_key=True)
    template = models.ForeignKey(PromptTemplate)
    components = models.ManyToManyField(PromptComponent, through='PromptComposition')
    
class PromptComposition(models.Model):
    """Ordering and configuration of components"""
    prompt = models.ForeignKey(ComposedPrompt)
    component = models.ForeignKey(PromptComponent)
    order = models.IntegerField()
    configuration = models.JSONField(null=True)
```

### 2. Context Enhancement Engine
```python
class ContextEnhancer:
    """Enhances prompts with relevant context from all systems"""
    
    def enhance_prompt(self, base_prompt: str, context: Dict) -> str:
        # 1. Memory Palace integration
        memories = self.fetch_relevant_memories(context)
        
        # 2. UKF knowledge injection
        knowledge = self.fetch_ukf_knowledge(context)
        
        # 3. Agent history and performance
        agent_context = self.fetch_agent_context(context)
        
        # 4. User profile and preferences
        user_context = self.fetch_user_context(context)
        
        # 5. Task-specific requirements
        task_context = self.fetch_task_context(context)
        
        return self.compose_enhanced_prompt(
            base_prompt, memories, knowledge, 
            agent_context, user_context, task_context
        )
```

### 3. Learning Intelligence Integration
```python
class PromptLearningService:
    """Learns from prompt performance and optimizes"""
    
    def analyze_prompt_performance(self, prompt_id: str, execution_result: Dict):
        # Track quality metrics
        quality_score = self.calculate_quality_score(execution_result)
        
        # Identify successful patterns
        patterns = self.extract_successful_patterns(prompt_id, execution_result)
        
        # Generate optimization suggestions
        suggestions = self.generate_optimizations(prompt_id, patterns)
        
        # Update prompt metrics
        self.update_prompt_metrics(prompt_id, quality_score)
        
    def evolve_prompt(self, prompt_id: str) -> PromptTemplate:
        # Create new version based on learnings
        original = PromptTemplate.objects.get(id=prompt_id)
        evolved = self.apply_learned_optimizations(original)
        return evolved
```

### 4. Mythology Detection & Prevention
```python
class PromptMythologyGuard:
    """Prevents mythology in prompts and responses"""
    
    def validate_prompt(self, prompt: str) -> Dict:
        # Check for mythology-prone patterns
        mythology_risk = self.detect_mythology_patterns(prompt)
        
        # Add anti-mythology instructions if needed
        if mythology_risk > 0.5:
            prompt = self.inject_anti_mythology_instructions(prompt)
            
        return {
            'prompt': prompt,
            'mythology_risk': mythology_risk,
            'mitigations_applied': True if mythology_risk > 0.5 else False
        }
    
    def inject_anti_mythology_instructions(self, prompt: str) -> str:
        return prompt + """
        
IMPORTANT: Base all responses on verified data only. Do not:
- Inflate numbers without explicit data
- Create fictional statistics or metrics  
- Lose important context when summarizing
- Make unsupported claims about capabilities
Always cite sources and acknowledge uncertainties."""
```

### 5. Dynamic Prompt Composer
```python
class DynamicPromptComposer:
    """Composes prompts dynamically based on context"""
    
    def compose_prompt(self, request: PromptRequest) -> str:
        # 1. Select base template
        template = self.select_optimal_template(request)
        
        # 2. Gather components
        components = self.gather_components(request)
        
        # 3. Apply context enhancement
        enhanced = self.context_enhancer.enhance_prompt(template, request.context)
        
        # 4. Apply mythology prevention
        guarded = self.mythology_guard.validate_prompt(enhanced)
        
        # 5. Apply learning optimizations
        optimized = self.apply_learned_optimizations(guarded['prompt'])
        
        return optimized
```

## Integration Points

### 1. Agent Orchestra Integration
- Each agent gets prompts from the unified system
- Agent performance feeds back to learning system
- Tool awareness automatically injected
- Cross-agent prompt coordination

### 2. Memory Palace Integration  
- Relevant memories injected into prompts
- New insights captured for future use
- Semantic search for similar past prompts
- Memory-based prompt optimization

### 3. UKF System Integration
- Knowledge base search for prompt enhancement
- Document context injection
- Idea and solution pattern matching
- Knowledge-aware prompt generation

### 4. Learning Intelligence Integration
- Prompt performance tracking
- A/B testing of prompt variations
- Evolutionary optimization
- Pattern recognition and application

### 5. Mythology Lab Integration
- Real-time mythology detection in prompts
- Response validation and correction
- Mythology pattern database updates
- Agent behavior influence tracking

## API Endpoints

```python
# prompting_system/urls.py
urlpatterns = [
    # Template management
    path('templates/', PromptTemplateViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('templates/<uuid:pk>/', PromptTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
    
    # Prompt composition
    path('compose/', ComposePromptView.as_view()),
    path('enhance/', EnhancePromptView.as_view()),
    
    # Learning and optimization
    path('analyze/', AnalyzePromptPerformanceView.as_view()),
    path('evolve/<uuid:prompt_id>/', EvolvePromptView.as_view()),
    
    # Component management
    path('components/', PromptComponentViewSet.as_view({'get': 'list', 'post': 'create'})),
    
    # Mythology prevention
    path('validate/', ValidatePromptView.as_view()),
    
    # Analytics
    path('analytics/performance/', PromptPerformanceAnalyticsView.as_view()),
    path('analytics/usage/', PromptUsageAnalyticsView.as_view()),
]
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
1. Create prompting_system Django app
2. Define models and migrations
3. Build basic CRUD operations
4. Create prompt registry

### Phase 2: Integration Layer (Week 2)
1. Connect to Agent Orchestra
2. Integrate Memory Palace
3. Link UKF system
4. Add context enhancement

### Phase 3: Intelligence Features (Week 3)
1. Implement learning algorithms
2. Add mythology detection
3. Build optimization engine
4. Create analytics dashboard

### Phase 4: Advanced Features (Week 4)
1. Dynamic composition
2. A/B testing framework
3. Real-time adaptation
4. Performance monitoring

## Key Benefits

1. **Unified Management**: Single source of truth for all prompts
2. **Context Awareness**: Leverages all available data for enhancement
3. **Continuous Improvement**: Learning-based optimization
4. **Mythology Prevention**: Built-in safeguards against AI folklore
5. **Performance Tracking**: Data-driven prompt evolution
6. **Reusability**: Component-based architecture
7. **Version Control**: Full prompt history and rollback

## Success Metrics

- Prompt response quality improvement: Target 25%
- Mythology detection rate: >90%
- Context relevance score: >0.8
- Agent task completion rate improvement: 20%
- Prompt reuse rate: >60%
- Average composition time: <100ms

## Technical Requirements

- Django 4.2+
- PostgreSQL with vector extensions
- Redis for caching
- OpenAI API for embeddings
- Celery for async processing
- WebSocket support for real-time updates