# Extraction Checklist - Component Mining Guide

## 🎯 Purpose
This document guides an AI agent through systematically extracting valuable components from each section of the codebase to build the new AI Content Studio.

## 📋 Extraction Instructions for Agent

### Agent Prompt Template
```
You are a code extraction specialist. For each section below:
1. Navigate to the specified directory
2. Identify files matching the "KEEP" criteria
3. Copy ONLY the essential code (removing complexity)
4. Document what was extracted and why
5. Note any dependencies that must come along
6. Flag any issues or decisions needed
```

---

## 1️⃣ MEMORY SYSTEM EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/shared_memory/`

### Extract These Components

#### Models (KEEP SIMPLIFIED)
```python
# FROM: shared_memory/models.py
✅ EXTRACT:
- UnifiedMemoryEntry model (simplify to just core fields)
  - user (ForeignKey)
  - content_text (TextField) 
  - embedding (VectorField)
  - created_at (DateTimeField)
  - metadata (JSONField)
  - importance_score (FloatField)

❌ REMOVE:
- All other fields (30+ unnecessary fields)
- Complex permissions
- Multi-tenant logic
- Audit fields
- Relationship tables
```

#### Services (KEEP CORE ONLY)
```python
# FROM: shared_memory/services.py
✅ EXTRACT:
- store_memory() function
- search_memories() function (vector search)
- get_embedding() function
- Only these 3 functions!

❌ REMOVE:
- Complex visibility rules
- Permission checks
- Caching logic (add later if needed)
- Analytics tracking
- All other methods (50+ methods)
```

#### Database Migrations
```python
# FROM: shared_memory/migrations/
✅ EXTRACT:
- Create a NEW migration with simplified model
- Include pgvector extension setup
- Include HNSW index creation

❌ REMOVE:
- All historical migrations
- Complex upgrade paths
```

### Dependencies to Note
- `pgvector` PostgreSQL extension
- `openai` for embeddings
- `numpy` for vector operations
- Existing 267K+ embedded memories (migrate later)

### Extraction Output
```
📁 new-project/memory/
├── models.py      (50 lines max)
├── services.py    (100 lines max)
├── __init__.py
└── migrations/
    └── 0001_initial.py
```

---

## 2️⃣ AGENT SYSTEM EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/agent_orchestra/`

### Extract These Components

#### Models (SINGLE AGENT TYPE)
```python
# FROM: agent_orchestra/models.py
✅ EXTRACT:
- AgentInstance model (simplified)
  - user (ForeignKey)
  - task (TextField)
  - status (CharField)
  - result (JSONField)
  - created_at (DateTimeField)

❌ REMOVE:
- AgentTemplate (54 templates)
- TaskOrchestration
- AgentChannel
- All relationship models
- Collaboration models
```

#### Core Agent Logic
```python
# FROM: agent_orchestra/services/
✅ EXTRACT:
- BasicAgentExecutor class
- execute_task() method
- Simple OpenAI integration

❌ REMOVE:
- Orchestration logic
- Parallel execution
- Agent routing
- Team coordination
- WebSocket updates
- Progress tracking
```

#### Simplified Execution
```python
# FROM: agent_orchestra/tasks.py
✅ EXTRACT:
- Single synchronous execute function
- Basic error handling
- Simple timeout (30 seconds)

❌ REMOVE:
- Celery tasks
- Async execution
- Queue management
- Background processing
```

### Dependencies to Note
- `openai` for GPT-4 calls
- Memory system for context
- Simple timeout mechanism

### Extraction Output
```
📁 new-project/agents/
├── models.py      (30 lines max)
├── executor.py    (150 lines max)
├── __init__.py
└── migrations/
    └── 0001_initial.py
```

---

## 3️⃣ CONTENT GENERATION EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/content/`

### Extract These Components

#### Models (SIMPLIFIED)
```python
# FROM: content/models.py
✅ EXTRACT:
- Content model
  - user (ForeignKey)
  - type (CharField: 'text', 'image')
  - prompt (TextField)
  - result (TextField/URLField)
  - created_at (DateTimeField)

❌ REMOVE:
- All other content types
- Publishing models
- Campaign models
- Analytics models
```

#### Generation Services
```python
# FROM: content/views.py and services.py
✅ EXTRACT:
- generate_text() function
- generate_image() function
- Basic OpenAI/DALL-E integration

❌ REMOVE:
- Video generation
- Audio generation
- Complex pipelines
- Batch processing
- Templates
```

### Dependencies to Note
- `openai` for GPT-4 and DALL-E
- Simple file storage for images

### Extraction Output
```
📁 new-project/content/
├── models.py      (30 lines max)
├── generators.py  (100 lines max)
├── __init__.py
└── migrations/
    └── 0001_initial.py
```

---

## 4️⃣ TOOL SYSTEM EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/tool_orchestra/`

### Extract These Components

#### Core Tools Only
```python
# FROM: tool_orchestra/tools/
✅ EXTRACT (Just 3 tools):
1. web_search.py - Simple Google search
2. data_analyzer.py - Basic data analysis
3. image_analyzer.py - Simple image understanding

❌ REMOVE:
- All other tools (30+ tools)
- Complex tool routing
- Tool discovery
- External API integrations
```

#### Simple Tool Interface
```python
# FROM: tool_orchestra/base.py
✅ EXTRACT:
- BaseTool class with execute() method
- Simple tool registry

❌ REMOVE:
- Authentication per tool
- Rate limiting
- Caching
- Monitoring
```

### Dependencies to Note
- `googlesearch-python` for web search
- `pillow` for image processing
- Keep it minimal

### Extraction Output
```
📁 new-project/tools/
├── base.py        (20 lines max)
├── web_search.py  (30 lines max)
├── analyzer.py    (30 lines max)
└── __init__.py
```

---

## 5️⃣ PROMPTING SYSTEM EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/prompts/`

### Extract These Components

#### Prompt Optimization
```python
# FROM: prompts/services.py
✅ EXTRACT:
- optimize_prompt() function
- Basic prompt templates (3-5 max)
- Simple enhancement logic

❌ REMOVE:
- Complex mutation systems
- A/B testing
- Analytics
- Version control
- Template management
```

### Dependencies to Note
- Works with agent system
- Simple string manipulation

### Extraction Output
```
📁 new-project/prompts/
├── optimizer.py   (50 lines max)
├── templates.py   (30 lines max)
└── __init__.py
```

---

## 6️⃣ MYTHOLOGY/VALIDATION EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/mythology/`

### Extract These Components

#### Simple Validation
```python
# FROM: mythology/services.py
✅ EXTRACT:
- validate_content() function
- Basic quality checks
- Simple safety filters

❌ REMOVE:
- Complex scoring systems
- Pattern analysis
- ML models
- Detailed reporting
```

### Dependencies to Note
- Basic Python string operations
- Simple rule engine

### Extraction Output
```
📁 new-project/validation/
├── validator.py   (40 lines max)
└── __init__.py
```

---

## 7️⃣ API LAYER EXTRACTION

### Location
`/Users/donkeyking/development/donkey_betz/backend/`

### Extract These Components

#### Simple REST API
```python
# FROM: Various views.py files
✅ CREATE NEW:
- /api/auth/register/
- /api/auth/login/
- /api/content/create/
- /api/content/list/
- /api/memory/search/

❌ REMOVE:
- All other 120+ endpoints
- Complex serializers
- Permissions
- Pagination
- Filtering
```

### Extraction Output
```
📁 new-project/api/
├── views.py       (200 lines max)
├── urls.py        (20 lines max)
├── auth.py        (50 lines max)
└── __init__.py
```

---

## 8️⃣ ORCHESTRATOR EXTRACTION

### Create New Central Hub
```python
# NEW FILE - This ties everything together
# new-project/studio.py

class ContentStudio:
    def __init__(self):
        self.memory = MemoryService()
        self.agent = AgentExecutor()
        self.content = ContentGenerator()
        self.tools = ToolRegistry()
        self.prompts = PromptOptimizer()
        self.validator = ContentValidator()
    
    def create_content(self, request):
        # 1. Optimize prompt
        prompt = self.prompts.optimize(request['prompt'])
        
        # 2. Get memory context
        context = self.memory.search(prompt)
        
        # 3. Execute with agent
        result = self.agent.execute(prompt, context)
        
        # 4. Validate
        if self.validator.validate(result):
            # 5. Store in memory
            self.memory.store(result)
            return result
        
        return None
```

---

## 🎯 EXTRACTION EXECUTION PLAN

### For AI Agent to Execute

```python
# AGENT INSTRUCTIONS
def execute_extraction():
    """
    Step-by-step extraction process
    """
    
    # 1. Create new project
    create_directory("ai-content-studio")
    
    # 2. Extract each component
    for section in EXTRACTION_CHECKLIST:
        print(f"Extracting {section.name}...")
        
        # Navigate to source
        source_files = read_directory(section.location)
        
        # Extract only needed code
        extracted = extract_essential(source_files, section.keep_criteria)
        
        # Simplify
        simplified = remove_complexity(extracted)
        
        # Write to new project
        write_files(f"ai-content-studio/{section.output}", simplified)
        
        # Document what was extracted
        log_extraction(section.name, files_count, lines_count)
    
    # 3. Create orchestrator
    create_orchestrator()
    
    # 4. Wire together
    integrate_components()
    
    # 5. Test
    run_tests()
    
    print("Extraction complete!")
```

---

## 📊 EXTRACTION METRICS TARGET

### Before Extraction
- **Files**: 500+
- **Lines of Code**: 100,000+
- **Models**: 45+
- **Dependencies**: 50+
- **Endpoints**: 129+

### After Extraction
- **Files**: 20-30
- **Lines of Code**: 1,000-1,500
- **Models**: 5
- **Dependencies**: 10
- **Endpoints**: 5

### Reduction Target: 95-98%

---

## ✅ EXTRACTION VALIDATION CHECKLIST

### Each Component Must:
- [ ] Run standalone (with minimal dependencies)
- [ ] Have clear input/output
- [ ] Be under 200 lines
- [ ] Have obvious purpose
- [ ] Connect simply to orchestrator

### Final System Must:
- [ ] Start with one command
- [ ] Create content in < 30 seconds
- [ ] Use memory effectively
- [ ] Deploy to Render in 1 hour
- [ ] Support payments

---

## 🚀 NEXT STEPS FOR AGENT

1. **Review this checklist** with human
2. **Get approval** on what to extract
3. **Create new project** structure
4. **Begin extraction** section by section
5. **Test each component** as extracted
6. **Wire together** with orchestrator
7. **Deploy and test** full system

---

## 💡 AGENT TIPS

### Do's:
- ✅ Copy code, then simplify
- ✅ Keep the vector store magic
- ✅ Preserve core functionality
- ✅ Test after each extraction
- ✅ Document decisions

### Don'ts:
- ❌ Don't extract everything
- ❌ Don't keep complex abstractions
- ❌ Don't preserve "nice to have" features
- ❌ Don't maintain backward compatibility
- ❌ Don't overthink - if uncertain, leave it out

---

## 🎯 SUCCESS CRITERIA

The extraction is successful when:
1. New project runs with `python manage.py runserver`
2. Can create text and image content
3. Memory search returns relevant results
4. Total codebase < 2000 lines
5. Deploys successfully to Render
6. First customer can pay and use it

---

**REMEMBER**: We're extracting VALUE, not code. Every line must earn its place in the new system.

**Target**: From 100,000 lines to 1,000 lines that actually work and make money.