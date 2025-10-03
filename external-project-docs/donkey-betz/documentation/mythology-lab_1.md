# Mythology Lab

## Overview
The Mythology Lab is Donkey Betz's advanced system for detecting, preventing, and tracking AI-generated mythologies (hallucinations). It monitors how false information is created, mutates, and propagates through the multi-agent system, providing guards and learning mechanisms to improve accuracy over time.

## Architecture

### Core Detection System
```
Mythology Lab
├── Detection Layer
│   ├── MythDetector (real-time pattern matching)
│   ├── Context Loss Tracker
│   ├── Numeric Inflation Monitor
│   └── Semantic Drift Analyzer
├── Prevention Layer
│   ├── MythologyGuardService
│   ├── Anti-Mythology Instructions
│   ├── Strong Guards for High Risk
│   └── Response Validation
├── Tracking Layer
│   ├── MythologyEvent Storage
│   ├── MythPropagation Network
│   ├── Pattern Recognition
│   └── Agent Profiling
└── Learning Layer
    ├── Pattern Database
    ├── Guard Effectiveness
    ├── Agent Behavior Analysis
    └── Myth Evolution Tracking
```

### Mythology Types Tracked
1. **Numeric Inflation**: Numbers growing without basis (e.g., "350 deployments")
2. **Context Loss**: Important details dropped during summarization
3. **Semantic Drift**: Meaning changing across retellings
4. **False Authority**: Unverified claims ("studies show", "experts confirm")
5. **Capability Exaggeration**: Claims beyond actual abilities
6. **Temporal Distortion**: False timeline claims

## Current State
- **Known Myths Database**: Including "350 deployments", "4,215 instances"
- **Pattern Detection**: 6 core pattern types with regex matching
- **Risk Scoring**: 0.0-1.0 confidence in mythology detection
- **Multi-LLM Tracking**: Cross-model propagation monitoring
- **Agent Profiling**: Classification of myth creators and spreaders
- **Alert System**: Real-time notifications for critical myths

## Key Components

### Hallucination Detection Methods

#### MythDetector Class
```python
# Core detection capabilities
- detect_context_loss(): Compare original vs stored content
- track_numeric_inflation(): Monitor growing numbers
- identify_semantic_drift(): Track meaning changes
- calculate_myth_confidence_score(): 0-1 mythology likelihood
```

#### Detection Patterns
```python
MYTHOLOGY_PATTERNS = {
    'numeric_inflation': r'\b\d{3,}\s*(deployments?|instances?|users?)\b',
    'false_authority': r'(studies show|experts confirm|research proves)',
    'context_loss': r'(we have|our system) (successfully|always|never)',
    'capability_exaggeration': r'(can do anything|unlimited|infinite)',
    'temporal_distortion': r'(has been|have been).{0,20}(years?|months?)'
}
```

### Prevention Mechanisms and Guards

#### MythologyGuardService
1. **Pre-Generation Guards**
   - Inject anti-mythology instructions
   - Apply strong guards for high-risk prompts
   - Add verification requirements

2. **Post-Generation Validation**
   - Validate responses for mythology patterns
   - Check context retention
   - Suggest corrections for detected myths

3. **Guard Types**
   - Pattern-based detection guards
   - Instruction injection guards
   - Response validation guards
   - Context preservation guards

### Propagation Tracking System

#### MythPropagation Model
Tracks how myths spread between agents:
- **Propagation Methods**: memory_share, conversation, inference, retrieval
- **Cross-Model Tracking**: Monitors myths crossing LLM boundaries
- **Generation Tracking**: How many "hops" a myth has traveled
- **Network Analysis**: Identifies super-spreaders and amplifiers

#### AgentMythologyProfile
Agent behavior classification:
- **Myth Creator**: Originates new mythologies
- **Super Spreader**: Rapidly propagates myths
- **Myth Amplifier**: Exaggerates existing myths
- **Normal Participant**: Average mythology behavior
- **Myth Resistant**: Rarely creates or spreads myths

### Learning Loop and Pattern Database

#### MythPattern Model
Stores identified patterns for analysis:
- Pattern signatures and characteristics
- Frequency tracking
- Example collection
- Risk scoring
- Evolution tracking

#### Learning Mechanisms
1. **Pattern Recognition**: Identify new mythology types
2. **Guard Effectiveness**: Track which guards work best
3. **Agent Learning**: Adjust agent behavior based on mythology history
4. **Prompt Evolution**: Improve prompts to reduce mythology

## API Endpoints

### Core Mythology APIs
- `GET /api/mythology-lab/dashboard/` - Mythology dashboard view
- `GET /api/mythology-lab/api/events/` - List mythology events
- `GET /api/mythology-lab/api/propagation/` - Propagation network data
- `GET /api/mythology-lab/api/analytics/` - Mythology analytics
- `POST /api/mythology-lab/api/experiments/` - Control experiments

### Integration Points
- Embedded in prompting system for pre/post validation
- Integrated with agent responses for real-time detection
- Connected to memory system for propagation tracking
- Linked to learning intelligence for pattern extraction

## Database Models

### Core Schema
```python
MythologyEvent
    ├── event_type (creation, mutation, propagation, detection)
    ├── original_content (what was first said)
    ├── mutated_content (how it changed)
    ├── mutation_type (context_loss, inflation, etc.)
    ├── confidence_score (0.0-1.0)
    ├── source_llm_provider (OpenAI, Anthropic, etc.)
    └── source_llm_model (gpt-4, claude-3, etc.)

MythPropagation
    ├── myth_event (FK → MythologyEvent)
    ├── from_agent → to_agent
    ├── propagation_method
    ├── generation (hop count)
    └── is_cross_model (bool)

MythPattern
    ├── pattern_type
    ├── pattern_signature (unique identifier)
    ├── frequency
    ├── risk_score
    └── examples (JSON)

AgentMythologyProfile
    ├── agent_id
    ├── myths_created/spread
    ├── classification
    └── trust_score
```

## Integration Points

### Internal Systems
- **Agent Orchestra**: Pre/post generation validation
- **Memory Palace**: Tracks mythology in stored memories
- **Prompting System**: Injects anti-mythology guards
- **Learning Intelligence**: Extracts patterns for improvement
- **AI Partner**: Validates conversation responses

### Prevention Integration
```python
# Example: Guard injection in prompting
if mythology_risk > 0.3:
    prompt += ANTI_MYTHOLOGY_INSTRUCTION
if mythology_risk > 0.6:
    prompt += STRONG_MYTHOLOGY_GUARDS
```

## Known Issues
- Some subtle mythologies escape pattern detection
- Cross-model propagation tracking can miss indirect paths
- Guard injection sometimes makes responses overly cautious
- Pattern database needs regular manual curation

## Future Enhancements
- Machine learning-based mythology detection
- Automated pattern discovery using clustering
- Real-time mythology correction in responses
- User-specific mythology preferences
- Cross-system mythology tracking
- Mythology immunization for agents
- Predictive mythology prevention

## Code Examples

### Mythology Detection
```python
# Detect mythology in content
detector = MythDetector()
result = detector.detect_mythology(
    memory={'content': 'Our system has 350 deployments'},
    context=previous_memories
)
# Returns: {
#   'mythology_confidence': 0.8,
#   'detected_patterns': ['known_myth'],
#   'recommendations': ['Known myth detected: 350 deployments']
# }
```

### Guard Application
```python
# Apply mythology guards to prompt
guard_service = MythologyGuardService()
guarded = guard_service.validate_and_guard_prompt(
    prompt="Tell me about our deployment statistics",
    template_id="business-stats-template"
)
# Returns guarded prompt with anti-mythology instructions
```

### Propagation Tracking
```python
# Track myth propagation
MythPropagation.objects.create(
    myth_event=mythology_event,
    from_agent_id=source_agent.id,
    to_agent_id=target_agent.id,
    propagation_method='memory_share',
    is_cross_model=True  # Different LLM providers
)
```