# Phase 1: Unified Command Architecture - Implementation Prompt

## Objective
Create a unified, intelligent command system that consolidates all agent deployment methods into a single, coherent architecture that understands user intent and routes requests appropriately.

## Current State Analysis

### Existing Command Detection Methods
1. **Explicit Commands** (`personal_ai_services.py:1468`)
   - "deploy agent X"
   - "use agent Y"
   - "get help from Z"

2. **Keyword Detection** (scattered throughout)
   - Business keywords trigger business agents
   - Research keywords trigger research agents
   - Technical keywords trigger technical agents

3. **Manual Deployment** (Command Center)
   - User explicitly selects and deploys agents
   - No automatic intent detection

### Problems to Solve
- Multiple command detection methods create confusion
- No confidence scoring for deployment decisions
- Inconsistent command parsing across the system
- Limited natural language understanding
- No fallback mechanisms for uncertain cases

## Implementation Requirements

### 1. Unified Command Parser
Create a single class that handles all command parsing:

```python
class UnifiedCommandParser:
    """
    Single source of truth for all command parsing and intent detection.
    Location: backend/ai_partner/services/unified_command_parser.py
    """
    
    def parse_command(self, message: str, context: dict) -> CommandResult:
        """
        Parse any user message and determine intent.
        
        Args:
            message: User's input text
            context: Conversation context, user history, etc.
            
        Returns:
            CommandResult with action, confidence, parameters
        """
        pass
    
    def get_confidence_score(self, message: str, action: str) -> float:
        """Calculate confidence score for a proposed action."""
        pass
    
    def suggest_alternatives(self, message: str) -> List[CommandResult]:
        """Suggest alternative interpretations of the command."""
        pass
```

### 2. Intent Detection Engine
Enhance the existing intent detection with agent-specific capabilities:

```python
class EnhancedIntentDetector:
    """
    Advanced intent detection with agent deployment awareness.
    Location: backend/ai_partner/services/enhanced_intent_detector.py
    """
    
    def detect_intent(self, message: str) -> IntentResult:
        """
        Detect user intent with multiple confidence levels.
        
        Categories:
        - DIRECT_ANSWER: Assistant can answer directly
        - SINGLE_AGENT: Requires one agent
        - MULTI_AGENT: Requires multiple agents
        - COMPLEX_TASK: Requires orchestration
        - UNCLEAR: Need clarification
        """
        pass
    
    def requires_agent(self, intent: IntentResult) -> bool:
        """Determine if the intent requires agent deployment."""
        pass
    
    def get_required_agents(self, intent: IntentResult) -> List[str]:
        """Get list of agents needed for this intent."""
        pass
```

### 3. Agent Registry Enhancement
Upgrade the agent registry with capability matching:

```python
class AgentCapabilityRegistry:
    """
    Central registry of all agent capabilities and performance metrics.
    Location: backend/agent_orchestra/services/agent_registry.py
    """
    
    AGENT_CAPABILITIES = {
        "Research Agent": {
            "domains": ["research", "analysis", "information"],
            "keywords": ["research", "analyze", "find", "discover", "investigate"],
            "complexity": "medium-high",
            "avg_execution_time": 30,
            "success_rate": 0.92,
            "cost_estimate": "medium"
        },
        "Business Agent": {
            "domains": ["business", "strategy", "marketing", "sales"],
            "keywords": ["business", "market", "strategy", "revenue", "growth"],
            "complexity": "medium-high",
            "avg_execution_time": 45,
            "success_rate": 0.88,
            "cost_estimate": "high"
        },
        # ... more agents
    }
    
    def match_capabilities(self, requirements: dict) -> List[AgentMatch]:
        """Match requirements to agent capabilities."""
        pass
    
    def get_agent_availability(self, agent_name: str) -> bool:
        """Check if an agent is available for deployment."""
        pass
    
    def estimate_execution(self, agent_name: str, task: str) -> ExecutionEstimate:
        """Estimate time and cost for agent execution."""
        pass
```

### 4. Confidence Scoring System
Implement a robust confidence scoring mechanism:

```python
class ConfidenceScorer:
    """
    Calculate confidence scores for various decisions.
    Location: backend/ai_partner/services/confidence_scorer.py
    """
    
    CONFIDENCE_THRESHOLDS = {
        "auto_deploy": 0.85,      # Automatically deploy agent
        "suggest": 0.60,          # Suggest agent deployment
        "uncertain": 0.40,        # Ask for clarification
        "fallback": 0.0           # Use fallback response
    }
    
    def calculate_deployment_confidence(
        self, 
        message: str, 
        agent: str, 
        context: dict
    ) -> float:
        """Calculate confidence for deploying a specific agent."""
        pass
    
    def calculate_intent_confidence(
        self, 
        message: str, 
        intent: str
    ) -> float:
        """Calculate confidence for detected intent."""
        pass
```

## Integration Points

### 1. Main Assistant Integration
Modify `personal_ai_services.py` to use the unified system:

```python
# Before (multiple detection methods)
if "deploy" in message_lower and "agent" in message_lower:
    # Handle deployment
    
# After (unified approach)
command_result = self.unified_parser.parse_command(message, context)
if command_result.confidence >= 0.85:
    return await self.execute_command(command_result)
elif command_result.confidence >= 0.60:
    return await self.suggest_command(command_result)
else:
    return await self.clarify_intent(message)
```

### 2. WebSocket Integration
Add real-time command parsing feedback:

```python
# Send parsing status via WebSocket
await self.websocket_manager.send_update({
    "type": "command_parsing",
    "status": "analyzing",
    "confidence": command_result.confidence,
    "suggested_action": command_result.action
})
```

### 3. Database Schema Updates
Track command parsing and intent detection:

```sql
CREATE TABLE command_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    raw_message TEXT,
    parsed_command JSONB,
    detected_intent VARCHAR(50),
    confidence_score FLOAT,
    action_taken VARCHAR(50),
    feedback VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_deployments (
    id SERIAL PRIMARY KEY,
    command_history_id INTEGER REFERENCES command_history(id),
    agent_name VARCHAR(100),
    deployment_reason TEXT,
    confidence_score FLOAT,
    execution_time_ms INTEGER,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing Requirements

### Unit Tests
```python
# tests/test_unified_command_parser.py
def test_parse_explicit_command():
    """Test parsing of explicit deploy commands."""
    
def test_parse_implicit_intent():
    """Test parsing of implicit agent needs."""
    
def test_confidence_scoring():
    """Test confidence score calculation."""
    
def test_fallback_handling():
    """Test fallback when confidence is low."""
```

### Integration Tests
```python
# tests/test_command_integration.py
def test_end_to_end_command_flow():
    """Test complete flow from message to agent deployment."""
    
def test_websocket_updates():
    """Test real-time updates during command parsing."""
    
def test_multi_agent_detection():
    """Test detection of multi-agent requirements."""
```

## Success Criteria

### Functional Requirements
- [ ] Single entry point for all command parsing
- [ ] Support for natural language variations
- [ ] Confidence scoring for all decisions
- [ ] Fallback mechanisms for low confidence
- [ ] Alternative suggestions for medium confidence

### Performance Requirements
- [ ] Command parsing < 100ms
- [ ] Intent detection < 50ms
- [ ] Confidence calculation < 20ms
- [ ] Total decision time < 200ms

### Quality Requirements
- [ ] 95% accuracy for explicit commands
- [ ] 85% accuracy for implicit intents
- [ ] 90% user satisfaction with suggestions
- [ ] Zero duplicate command handlers

## Implementation Steps

### Step 1: Create Base Classes (Day 1)
1. Create `UnifiedCommandParser` class
2. Create `EnhancedIntentDetector` class
3. Create `AgentCapabilityRegistry` class
4. Create `ConfidenceScorer` class

### Step 2: Implement Core Logic (Day 2)
1. Implement command parsing logic
2. Implement intent detection algorithms
3. Implement capability matching
4. Implement confidence scoring

### Step 3: Integration (Day 3)
1. Integrate with `personal_ai_services.py`
2. Add WebSocket updates
3. Create database tables
4. Update API endpoints

### Step 4: Testing (Day 4)
1. Write unit tests
2. Write integration tests
3. Performance testing
4. User acceptance testing

### Step 5: Documentation (Day 5)
1. Update API documentation
2. Create usage examples
3. Document configuration options
4. Create troubleshooting guide

## Configuration

### Environment Variables
```bash
# Command parser configuration
COMMAND_PARSER_CONFIDENCE_THRESHOLD=0.85
COMMAND_PARSER_SUGGESTION_THRESHOLD=0.60
COMMAND_PARSER_MAX_ALTERNATIVES=3

# Intent detection configuration
INTENT_DETECTOR_USE_ML=true
INTENT_DETECTOR_CACHE_TTL=3600

# Agent registry configuration
AGENT_REGISTRY_UPDATE_INTERVAL=300
AGENT_REGISTRY_PERFORMANCE_WINDOW=7d
```

### Feature Flags
```python
FEATURE_FLAGS = {
    "unified_command_parser": True,
    "confidence_scoring": True,
    "auto_deployment": False,  # Start with manual confirmation
    "multi_agent_support": False,  # Enable in Phase 2
}
```

## Rollback Plan

If issues arise:
1. Feature flag to disable unified parser
2. Fallback to existing command detection
3. Preserve all existing methods (don't delete yet)
4. Monitor error rates and performance
5. Quick revert via environment variable

## Notes for Implementation

### Priority Order
1. **High Priority**: Unified command parser (core functionality)
2. **Medium Priority**: Confidence scoring (improves UX)
3. **Low Priority**: Multi-agent detection (Phase 2 feature)

### Gotchas to Avoid
- Don't break existing command center functionality
- Preserve backward compatibility
- Test with real user messages
- Consider edge cases (typos, abbreviations)
- Handle multiple languages if needed

### Dependencies
- Existing intent detection service
- Agent Orchestra models
- Personal AI services
- WebSocket manager
- Database connections

## Questions to Answer

Before implementation:
1. Should we use ML models for intent detection?
2. What confidence thresholds work best?
3. How to handle ambiguous commands?
4. Should we log all command parsing for training?
5. How to measure parser accuracy?

## Definition of Done

- [ ] All classes implemented and tested
- [ ] Integration with main assistant complete
- [ ] WebSocket updates working
- [ ] Database schema updated
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] Code reviewed and approved
- [ ] Deployed to staging environment