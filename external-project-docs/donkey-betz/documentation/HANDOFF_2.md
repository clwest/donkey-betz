# Step 2: Core Extraction - Handoff Document

## 🎯 Objective
Extract only the essential code from each component into a clean, new codebase.

## 📁 New Project Structure

```
ai-content-studio/
├── backend/
│   ├── agents/
│   │   ├── models.py      (20 lines)
│   │   ├── services.py    (100 lines)
│   │   └── views.py       (50 lines)
│   ├── memory/
│   │   ├── models.py      (30 lines)
│   │   ├── services.py    (80 lines)
│   │   └── views.py       (40 lines)
│   ├── content/
│   │   ├── models.py      (40 lines)
│   │   ├── services.py    (150 lines)
│   │   └── views.py       (60 lines)
│   ├── tools/
│   │   ├── registry.py    (50 lines)
│   │   ├── base.py        (30 lines)
│   │   └── builtin.py     (100 lines)
│   ├── prompting/
│   │   ├── models.py      (20 lines)
│   │   ├── optimizer.py   (60 lines)
│   │   └── templates.py   (40 lines)
│   ├── mythology/
│   │   ├── validator.py   (50 lines)
│   │   └── rules.py       (30 lines)
│   ├── core/
│   │   ├── settings.py    (100 lines)
│   │   ├── urls.py        (30 lines)
│   │   └── studio.py      (200 lines) # Main orchestrator
│   └── manage.py
└── frontend/
    └── (addressed in step-05)
```

## 🔧 Extraction Tasks

### Task 1: Create New Project
```bash
mkdir ai-content-studio
cd ai-content-studio
python -m venv venv
source venv/bin/activate
pip install django djangorestframework celery redis openai
```

### Task 2: Extract Agents
**From**: `donkey_betz/backend/agent_orchestra/`
**Take**:
- AgentTemplate model (simplified)
- Basic deployment function
- Status checking
- Result retrieval

**Leave**: Everything else

### Task 3: Extract Memory
**From**: `donkey_betz/backend/shared_memory/`
**Take**:
- UnifiedMemoryEntry model (simplified)
- Store function
- Search function (basic text search only)

**Leave**: Embeddings, complex search

### Task 4: Extract Content
**From**: `donkey_betz/backend/content/`
**Take**:
- ContentItem model
- Text generation service
- Image generation service (if API keys exist)

**Leave**: Video, social media, publishing

### Task 5: Extract Tools
**From**: `donkey_betz/backend/tools/`
**Take**:
- Tool base class
- Web search tool
- File operations tool
- Data analysis tool

**Leave**: Complex integrations

### Task 6: Extract Prompting
**From**: `donkey_betz/backend/prompting/`
**Take**:
- Basic prompt templates
- Simple optimization logic

**Leave**: A/B testing, mutations

### Task 7: Extract Mythology
**From**: `donkey_betz/backend/mythology/`
**Take**:
- Basic quality check
- Safety validation

**Leave**: Complex scoring, patterns

## 📊 Simplified Database Schema

```sql
-- Only 6 tables instead of 45+

CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    template TEXT,
    created_at TIMESTAMP
);

CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP
);

CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    content TEXT,
    agent_id INTEGER REFERENCES agents(id),
    memory_id INTEGER REFERENCES memories(id),
    created_at TIMESTAMP
);

CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    config JSONB
);

CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    template TEXT,
    variables JSONB
);

CREATE TABLE validations (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id),
    score FLOAT,
    passed BOOLEAN
);
```

## 🔌 Simplified API Endpoints

```python
# Only 12 endpoints instead of 129+

urlpatterns = [
    # Agents
    path('api/agents/deploy/', deploy_agent),
    path('api/agents/<id>/status/', agent_status),
    path('api/agents/<id>/result/', agent_result),
    
    # Memory
    path('api/memory/store/', store_memory),
    path('api/memory/search/', search_memory),
    
    # Content
    path('api/content/generate/', generate_content),
    path('api/content/<id>/', get_content),
    
    # Tools
    path('api/tools/list/', list_tools),
    path('api/tools/execute/', execute_tool),
    
    # Prompting
    path('api/prompts/optimize/', optimize_prompt),
    
    # Mythology
    path('api/validate/', validate_content),
    
    # Main
    path('api/studio/create/', create_with_studio),
]
```

## ✅ Extraction Checklist

- [ ] New project created
- [ ] Virtual environment setup
- [ ] Django project initialized
- [ ] Agents extracted and simplified
- [ ] Memory extracted and simplified
- [ ] Content extracted and simplified
- [ ] Tools extracted and simplified
- [ ] Prompting extracted and simplified
- [ ] Mythology extracted and simplified
- [ ] Database migrations created
- [ ] API endpoints wired
- [ ] Basic tests passing

## 🎯 Success Criteria

- Code compiles without errors
- Database migrations run successfully
- All 12 API endpoints respond
- No dependencies on old codebase
- Total codebase under 2,000 lines

## 📅 Timeline
**Duration**: 2-3 days
**Output**: Clean, minimal codebase

---

## Next Step
Move to `step-03-integration/` once extraction is complete.