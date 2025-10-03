# AI Profile Intelligents

## Overview
The AI Profile Intelligents system is Donkey Betz's sophisticated user learning and personalization framework that builds comprehensive user profiles through conversation analysis while maintaining strict privacy controls. It enables highly personalized AI interactions by understanding user preferences, patterns, and context.

## Architecture

### Profile System Structure
```
AI Profile Intelligents
├── User Profile Models
│   ├── UserLifeProfile (comprehensive life context)
│   ├── UserProfile (enhanced intelligence)
│   ├── ProfileUpdateLog (audit trail)
│   └── ExtractedFact (confidence-scored facts)
├── Learning Mechanisms
│   ├── Automatic Fact Extraction
│   ├── Pattern Recognition
│   ├── Confidence Scoring
│   └── Context Analysis
├── Privacy Controls
│   ├── Fact Learning Toggle
│   ├── Profile Sharing Toggle
│   ├── Data Retention Settings
│   └── Export/Delete Options
└── Integration Layer
    ├── Profile Context Builder
    ├── Agent Personalization
    ├── Prompt Adaptation
    └── Memory Integration
```

### Learning Pipeline
1. **Conversation Analysis** → Extract facts from messages
2. **Pattern Recognition** → Identify behavioral patterns
3. **Confidence Scoring** → Validate fact accuracy
4. **Profile Update** → Store high-confidence facts
5. **Agent Integration** → Personalize interactions

## Current State
- **Fact Categories**: 10+ types (personal, professional, preferences, etc.)
- **Learning Methods**: Regex patterns, context analysis, behavior tracking
- **Privacy Levels**: Strict, balanced, performance modes
- **Confidence Threshold**: 0.6 for automatic updates
- **Data Retention**: Default 365 days (user configurable)
- **Export Formats**: JSON, CSV for data portability

## Key Components

### User Learning Mechanisms

#### Automatic Fact Extraction
```python
# Fact extraction patterns
- Names: "I'm John", "call me Sarah"
- Locations: "I live in NYC", "based in London"
- Occupations: "I work as a developer", "I'm a designer"
- Companies: "I work at Google", "employed by Microsoft"
- Relationships: "my wife Sarah", "my colleague Tom"
- Skills: "I know Python", "experienced in React"
- Interests: "I love hiking", "interested in AI"
- Goals: "I want to learn ML", "planning to start a company"
```

#### Pattern Recognition
- **Communication Style**: Technical, casual, formal, creative
- **Learning Style**: Visual, hands-on, theoretical, example-based
- **Active Hours**: Time-based activity patterns
- **Topic Preferences**: Frequently discussed subjects
- **Emotional Patterns**: Stress indicators, enthusiasm markers

#### Confidence Scoring
- **Direct Statements**: 0.9-1.0 confidence
- **Contextual Inference**: 0.6-0.8 confidence
- **Pattern-Based**: 0.5-0.7 confidence
- **Update Threshold**: 0.6 minimum

### Profile Data Structure

#### UserLifeProfile
```python
Professional Context:
- profession, current_role, career_goals
- skills[], interests[], expertise_areas[]

Personal Context:
- life_goals, values[], challenges[]
- strengths[], preferences{}

Behavioral Patterns:
- energy_patterns, communication_style
- learning_style, productivity_times

AI Preferences:
- preferred_ai_personality (5 types)
- response_length, formality_level
```

#### UserProfile (Enhanced)
```python
Basic Information:
- preferred_name, location, timezone

Professional:
- occupation, company, tech_stack[]
- expertise_areas[], years_experience

Personal:
- interests[], hobbies[]
- family_context, important_dates{}

Relationships:
- mentioned_people[{name, relationship, context}]

Projects & Goals:
- current_projects[], goals[]
- challenges[], achievements[]
```

### How Agents Use Profiles

#### Context Injection
```python
# Profile context added to agent prompts
{
    "user_context": {
        "name": "John",
        "expertise": ["Python", "React"],
        "communication_style": "technical",
        "current_goals": ["Learn ML", "Build SaaS"],
        "recent_topics": ["database optimization"]
    }
}
```

#### Personalization Examples
1. **Language Adaptation**: Technical users get detailed explanations
2. **Example Selection**: Code examples for developers, analogies for others
3. **Task Routing**: Complex tasks for experts, guided steps for beginners
4. **Time Awareness**: Considers user's productive hours
5. **Relationship Context**: References known colleagues/projects

### Privacy and Control Features

#### User Controls
- **Fact Learning**: Enable/disable automatic extraction
- **Profile Sharing**: Control what agents can access
- **Fact Correction**: Edit or remove incorrect facts
- **Data Export**: Download all profile data
- **Profile Reset**: Complete data deletion

#### Privacy Modes
1. **Strict**: Minimal learning, no sharing
2. **Balanced**: Learn with consent, selective sharing
3. **Performance**: Full learning and sharing

## API Endpoints

### Profile Management
- `GET /api/ai-partner/profile/summary/` - Profile overview
- `GET /api/ai-partner/profile/details/` - Detailed profile
- `POST /api/ai-partner/profile/settings/` - Update privacy
- `GET /api/ai-partner/profile/facts/` - View extracted facts
- `POST /api/ai-partner/profile/correct-fact/` - Correct facts
- `GET /api/ai-partner/profile/analytics/` - Learning analytics
- `POST /api/ai-partner/profile/reset/` - Reset profile
- `POST /api/ai-partner/profile/export/` - Export data

### Fact Management
- `GET /api/ai-partner/facts/by-category/` - Facts by type
- `POST /api/ai-partner/facts/update-confidence/` - Adjust confidence
- `DELETE /api/ai-partner/facts/{id}/` - Remove fact

## Database Models

### Core Schema
```python
UserLifeProfile
    ├── user (OneToOne → User)
    ├── professional_context (JSON)
    ├── personal_context (JSON)
    ├── ai_personality_preference
    ├── privacy_settings (JSON)
    └── cost_controls (JSON)

UserProfile
    ├── user (OneToOne → User)
    ├── basic_info (Encrypted)
    ├── professional_info (Encrypted)
    ├── relationships (Encrypted JSON)
    ├── behavioral_patterns (JSON)
    └── privacy_controls

ExtractedFact
    ├── user (FK → User)
    ├── category, subcategory
    ├── fact_text, confidence_score
    ├── source_conversation (FK)
    └── metadata (JSON)

ProfileUpdateLog
    ├── user, field_name
    ├── old_value, new_value
    ├── update_source, confidence
    └── timestamp
```

## Integration Points

### Internal Systems
- **Agent Orchestra**: Provides user context for task execution
- **Memory Palace**: Links memories to profile facts
- **Learning Intelligence**: Uses profile for pattern learning
- **Prompting System**: Adapts prompts to user style
- **AI Partner**: Primary conversation interface

### Context Flow
```
User Message → Fact Extraction → Profile Update
                                        ↓
Agent Response ← Personalization ← Profile Context
```

## Known Issues
- Fact extraction can miss context in complex sentences
- Confidence scoring needs refinement for indirect statements
- Profile merging when facts conflict needs improvement
- Time pattern detection is basic

## Future Enhancements
- Natural language profile queries ("What do you know about me?")
- Multi-modal profile building (voice, image preferences)
- Collaborative profiles for team contexts
- Predictive preference modeling
- Cross-platform profile sync
- Advanced relationship mapping
- Emotional intelligence tracking

## Code Examples

### Profile Summary Request
```python
# GET /api/ai-partner/profile/summary/
{
    "exists": true,
    "completeness": 0.82,
    "total_facts_learned": 67,
    "fact_learning_enabled": true,
    "profile_sharing_enabled": true,
    "communication_style": "technical",
    "expertise_areas": ["Python", "React", "AWS"],
    "current_projects": 3,
    "active_goals": 5
}
```

### Fact Correction
```python
# POST /api/ai-partner/profile/correct-fact/
{
    "fact_id": "fact-123",
    "corrected_value": "Senior Developer",
    "category": "professional",
    "confidence": 1.0
}
```

### Privacy Settings Update
```python
# POST /api/ai-partner/profile/settings/
{
    "fact_learning_enabled": true,
    "profile_sharing_enabled": true,
    "privacy_level": "balanced",
    "data_retention_days": 180,
    "allowed_fact_categories": ["professional", "interests"]
}
```