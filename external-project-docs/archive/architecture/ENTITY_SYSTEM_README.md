# Entity System - Preventing AI Hallucinations

## Overview

The Entity System prevents AI from hallucinating about entity identities, specifically ensuring that "Donkey Betz" is correctly identified as a platform/project, NOT a person.

## How It Works

### 1. Entity Registry (`knowledge_base/entity_registry.py`)
- Hardcoded entities for Chris (user ID 2)
- Defines what entities ARE and what they ARE NOT
- Provides facts and context rules

### 2. Context Injection (`knowledge_base/context_middleware.py`)
- Detects entity mentions in user queries
- Injects clarifications into AI prompts
- Adds established facts and context rules

### 3. Response Validation (`ai_partner/response_validator.py`)
- Validates AI responses for entity confusion
- Catches phrases like "Donkey Betz is a person"
- Provides corrections when hallucinations detected

### 4. Integration (`ai_partner/services/learning_enhanced_personal_ai.py`)
- Entity context injected before AI generation
- Responses validated after generation
- Corrections applied if needed

## Testing

Run the test script to verify the system:
```bash
python test_entity_system.py
```

Expected output:
- ✅ Entity Registry correctly identifies Donkey Betz as platform
- ✅ Context injection adds clarifications to prompts
- ✅ Response validation catches hallucinations
- ✅ Entity-aware service integrates all components

## Key Entities

### Donkey Betz
- **Type**: platform/project
- **NOT**: person, influencer, crypto figure, individual
- **Facts**: 
  - It's a platform/project, NOT a person
  - Created and owned by Chris
  - Has 19 real businesses using it
  - Part of the move_that_ass ecosystem
  - Uses AI agents for sports analysis

### Chris
- **Type**: person/developer
- **Role**: creator/owner
- **Owns**: donkey_betz, move_that_ass

### move_that_ass
- **Type**: project/ecosystem
- **Contains**: AI agents, memory palace, mythology lab, donkey_betz

## Database Setup

1. Run migrations:
```bash
python manage.py migrate knowledge_base
```

2. Populate Chris's entities:
```bash
python manage.py populate_chris_entities
```

## Feature Flags

In `settings.py`:
```python
FEATURE_FLAGS = {
    'entity_context_injection': True,  # Enable entity context
    'response_validation': True,       # Enable response validation
}
```

## Future Enhancements

1. **Multi-tenant Support**: Each user can define their own entities
2. **Dynamic Learning**: Learn entities from imported chat histories
3. **Entity Relationships**: Build knowledge graphs
4. **Import Adapters**: Support ChatGPT, Claude, and other chatbot exports

## Troubleshooting

If AI still hallucinates about Donkey Betz:
1. Check entity registry is loaded (user ID must be 2)
2. Verify feature flags are enabled
3. Check logs for "Entity confusion detected"
4. Run test script to validate system

## Success Metrics

Before Entity System:
- AI: "Donkey Betz is a crypto influencer..."
- AI: "The person named Donkey Betz..."

After Entity System:
- AI: "Donkey Betz is your sports betting platform..."
- AI: "The Donkey Betz platform uses AI agents..."

The system ensures factual accuracy about entity identities!