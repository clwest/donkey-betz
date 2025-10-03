# Prompting System

## Overview
The Prompting System is Donkey Betz's central infrastructure for managing, composing, and optimizing prompts across all AI interactions. It features a library of 66 templates from 14+ platforms, 1,882 extracted components, 390 learning examples, and sophisticated cross-domain adaptation capabilities.

## Architecture

### System Hierarchy
```
Prompting System
├── Template Library (66 templates)
│   ├── Platform Templates (14 sources)
│   ├── Dynamic Templates (with variables)
│   ├── Performance Tracking
│   └── Version Control
├── Component Library (1,882 components)
│   ├── Behavioral Components
│   ├── Domain Specific Components
│   ├── Tool Usage Components
│   └── Constraint Components
├── Example Library (390 examples)
│   ├── Task Demonstrations
│   ├── Input/Output Pairs
│   ├── Step-by-Step Sequences
│   └── Cross-Domain Examples
└── Cross-Domain Adapter
    ├── Domain Mapping Engine
    ├── Pattern Preservation
    ├── Quality Scoring
    └── Adaptation Tracking
```

### Service Architecture
- **Dynamic Prompt Composer**: Real-time prompt generation
- **Template Composer**: Multi-template merging
- **Mythology Guard Service**: Hallucination prevention
- **Learning Intelligence Service**: Performance optimization
- **Context Enhancer**: Memory/knowledge injection
- **Agent Integration**: Seamless agent prompt optimization

## Current State
- **Templates**: 66 from Anthropic, OpenAI, Cursor, Windsurf, Devin, Google, Mistral, Replit, XAI, Hume, Manus, MultiOn, Donkey Betz
- **Components**: 1,882 extracted and categorized
- **Examples**: 390 for few-shot learning
- **Adaptability**: Cross-domain conversion between 8+ domains
- **Performance**: Sub-100ms composition time
- **Integration**: Full Template Library & Prompt Manager UI

## Key Components

### Template Library (66 Templates)

#### Template Sources
1. **Anthropic** (Claude templates)
2. **OpenAI** (GPT templates)
3. **Cursor** (Code editor AI)
4. **Windsurf** (IDE AI)
5. **Devin** (AI software engineer)
6. **Google** (Gemini templates)
7. **Mistral** (Open-source LLM)
8. **Replit** (Coding platform)
9. **XAI** (Grok templates)
10. **Hume** (Emotional AI)
11. **Manus** (Hand gesture AI)
12. **MultiOn** (Web automation)
13. **Aider** (Pair programming)
14. **Donkey Betz** (Custom)

#### Template Features
- **Dynamic Variables**: `{{agent_name}}`, `{{company}}`, `{{capabilities}}`
- **Version Control**: Parent-child versioning
- **Performance Metrics**: Usage count, quality score, completion time
- **Mythology Tracking**: Incident counting
- **Embedding Support**: 1536-dim vectors for similarity

### Component Extraction (1,882 Components)

#### Component Types
1. **Behavioral** (423): Personality, communication style
2. **Domain Specific** (512): Industry expertise
3. **Tool Usage** (287): API/tool instructions
4. **Constraint** (198): Limitations, rules
5. **Communication** (156): Tone, format
6. **Context Setup** (134): Environment config
7. **Workflow** (98): Process steps
8. **Error Handling** (74): Failure recovery

#### Component Features
- **Adaptability Score**: 0.0-1.0 cross-domain potential
- **Usage Tracking**: Effectiveness metrics
- **Pattern Association**: Related components
- **Dynamic Content**: Variable substitution

### Example Adaptation (390 Examples)

#### Example Categories
- **Task Demonstration**: Step-by-step examples
- **Input/Output Pairs**: Expected behaviors
- **Error Correction**: What not to do
- **Before/After**: Transformation examples
- **Reasoning**: Chain-of-thought examples

#### Domains Supported
- Coding → Business
- Business → Creative
- Academic → Technical
- Healthcare → Legal
- Marketing → Finance
- And more...

### Cross-Domain Adapter Capabilities

#### Adaptation Process
1. **Pattern Extraction**: Identify core patterns
2. **Domain Mapping**: Convert terminology
3. **Context Preservation**: Maintain intent
4. **Quality Validation**: Score adaptation
5. **Usage Tracking**: Learn from feedback

## API Endpoints

### Template Operations
- `GET /api/prompting/templates/` - List all templates
- `GET /api/prompting/templates/{id}/` - Get template details
- `GET /api/prompting/templates/{id}/preview/` - Preview with components
- `GET /api/prompting/templates/{id}/abstracted/` - Get dynamic version
- `POST /api/prompting/templates/compose_templates/` - Merge templates
- `GET /api/prompting/templates/platforms/` - List platforms

### Component Library
- `GET /api/prompting/component-library/overview/` - Statistics
- `GET /api/prompting/component-library/browse/` - Browse components
- `POST /api/prompting/component-library/search/` - Search components
- `POST /api/prompting/component-library/{id}/adapt/` - Adapt component
- `POST /api/prompting/component-library/combine/` - Combine components

### Example Management
- `GET /api/prompting/examples/` - List examples
- `GET /api/prompting/examples/by-domain/` - Domain filtering
- `POST /api/prompting/examples/{id}/adapt/` - Cross-domain adaptation

### Dynamic Composition
- `POST /api/prompting/compose/` - Compose prompt
- `POST /api/prompting/templates/compose_dynamic/` - Agent-specific
- `POST /api/prompting/agent/` - Optimized agent prompt

## Database Models

### Core Schema
```python
PromptTemplate
    ├── name, category, template
    ├── version, parent_version
    ├── performance_score, usage_count
    ├── avg_response_quality, avg_completion_time
    ├── mythology_incidents
    ├── source_platform
    └── embedding (1536 dimensions)

PromptComponent
    ├── name, type, content
    ├── category, description
    ├── is_reusable, usage_count
    ├── effectiveness_score
    └── metadata (JSON)

ExtractedTemplateComponent
    ├── template (FK)
    ├── component_type, text
    ├── adaptability_score
    ├── domain_terms
    └── search_vector

ExtractedExample
    ├── template (FK)
    ├── example_type, complexity
    ├── input_text, output_text
    ├── domain, adaptability_score
    └── metadata (JSON)
```

## Integration Points

### Internal Systems
- **Agent Orchestra**: Provides optimized prompts for agents
- **Memory Palace**: Injects relevant memories into prompts
- **Knowledge Base**: Adds domain knowledge to prompts
- **Mythology Lab**: Validates prompts for hallucinations
- **Learning Intelligence**: Optimizes prompts based on performance
- **Tool Orchestra**: Maps generic tools to specific APIs

### UI Integration
- **Template Library** (`/template-library`): Browse and select templates
- **Prompt Manager** (`/prompt-manager`): Edit agent prompts
- **Bi-directional Integration**: Import templates into agents

## Known Issues
- Some dynamic templates don't display abstracted content correctly (fixed)
- Template similarity search could be more accurate
- Component extraction sometimes misses nested patterns
- Cross-domain adaptation quality varies by domain pair

## Future Enhancements
- AI-powered template generation from descriptions
- Real-time A/B testing of prompt variations
- Multi-language prompt support
- Visual prompt composition builder
- Automated prompt optimization cycles
- Template marketplace for sharing
- Version control with diff visualization

## Code Examples

### Using a Template
```python
# POST /api/prompting/templates/{id}/compose/
{
    "context": {
        "agent_name": "Marketing Strategist",
        "company": "TechStartup Inc",
        "capabilities": ["market_analysis", "content_creation"],
        "user_context": {
            "goals": ["increase brand awareness"],
            "industry": "B2B SaaS"
        }
    },
    "include_components": ["memory_injection", "mythology_guard"]
}
```

### Cross-Domain Adaptation
```python
# POST /api/prompting/examples/{id}/adapt/
{
    "example_id": "coding-debug-example-123",
    "target_domain": "business",
    "preserve_patterns": true,
    "quality_threshold": 0.7
}
# Converts coding debug example to business problem-solving
```

### Dynamic Composition
```python
# POST /api/prompting/compose/
{
    "base_template": "agent-base-template",
    "components": [
        {"type": "behavioral", "content": "Be concise and actionable"},
        {"type": "tool_usage", "agent_tools": ["web_search", "calculator"]},
        {"type": "mythology_guard", "level": "strong"}
    ],
    "context": {
        "task": "Create marketing campaign",
        "user_preferences": {"style": "data-driven"}
    }
}
```