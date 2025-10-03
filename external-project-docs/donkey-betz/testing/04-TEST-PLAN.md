# Test Plan for Prompting System Improvements

## Overview
Comprehensive test plan to validate that the new prompting system produces appropriate, task-specific prompts.

## Test Categories

### 1. Simple Information Queries
These should receive SHORT, DIRECT responses without business frameworks.

#### Test Case 1.1: Time Query
**Input**: "What time is it?"
**Expected Output**:
- Length: < 50 words
- No business strategy sections
- Direct time information
- No implementation roadmap

#### Test Case 1.2: Definition Query
**Input**: "What is Redis?"
**Expected Output**:
- Length: < 150 words
- Clear definition
- Brief explanation
- No strategic analysis

#### Test Case 1.3: Status Check
**Input**: "Check my calendar"
**Expected Output**:
- Length: < 100 words
- Calendar information only
- No business recommendations
- Action confirmation format

### 2. Analysis Tasks
These should receive structured analytical responses.

#### Test Case 2.1: Stock Analysis
**Input**: "Analyze AAPL stock performance"
**Expected Output**:
- Structured analysis format
- Data-driven insights
- Financial metrics
- Reasonable length (500-800 words)
- NOT generic business strategy template

#### Test Case 2.2: Code Review
**Input**: "Review this Python function for improvements"
**Expected Output**:
- Technical analysis format
- Code-specific feedback
- No business language
- Practical suggestions

### 3. Creation Tasks
These should focus on the output, not analysis.

#### Test Case 3.1: Tweet Creation
**Input**: "Write a tweet about our new feature"
**Expected Output**:
- The actual tweet (280 chars)
- Maybe 2-3 variations
- Brief notes if needed
- NOT 800-word strategy document

#### Test Case 3.2: Email Draft
**Input**: "Draft an email to cancel a meeting"
**Expected Output**:
- The email text
- Subject line
- Brief tone notes
- NOT strategic analysis of meeting cancellation

### 4. Research Tasks
These should provide findings with sources.

#### Test Case 4.1: Market Research
**Input**: "Research competitors in the CRM space"
**Expected Output**:
- List of competitors
- Key findings
- Data sources
- Structured but not overly verbose

#### Test Case 4.2: Technical Research
**Input**: "Find the best Python web frameworks"
**Expected Output**:
- Framework comparison
- Technical criteria
- Recommendations based on use case
- No business strategy language

### 5. Action Tasks
These should confirm action taken.

#### Test Case 5.1: Scheduling
**Input**: "Schedule a meeting for tomorrow at 2pm"
**Expected Output**:
- Confirmation of scheduling
- Meeting details
- < 50 words
- No strategic analysis of meetings

#### Test Case 5.2: Reminder Setting
**Input**: "Remind me to call John at 3pm"
**Expected Output**:
- Reminder confirmation
- Time and details
- Brief acknowledgment
- No business framework

## User Context Tests

### Test Case 6.1: Technical User
**User Profile**: Software Engineer, 5 years experience
**Input**: "How do I optimize database queries?"
**Expected Output**:
- Technical depth appropriate for experience
- Code examples
- Advanced techniques
- No basic explanations

### Test Case 6.2: Non-Technical User
**User Profile**: Marketing Manager, non-technical
**Input**: "Explain how our API works"
**Expected Output**:
- Simple language
- Business benefits focus
- Analogies and examples
- No code snippets

### Test Case 6.3: New User
**User Profile**: No history, first interaction
**Input**: "Help me get started"
**Expected Output**:
- Welcoming tone
- Overview of capabilities
- Simple examples
- No assumptions about expertise

## Memory Context Tests

### Test Case 7.1: Previous Context Reference
**Previous Context**: Discussed launching a startup
**Input**: "What should I do next?"
**Expected Output**:
- References startup discussion
- Contextual next steps
- Continuity with previous conversation

### Test Case 7.2: Conflicting Context
**Previous Context**: User said they hate long responses
**Input**: "Analyze my business model"
**Expected Output**:
- Respects preference for brevity
- Condensed analysis
- Offers to expand if needed

## Integration Tests

### Test Case 8.1: Prompting System Available
**Setup**: Sophisticated system enabled
**Test**: Deploy any agent
**Verify**:
- `generate_ai_prompt_internal()` is called
- Prompting bridge is used
- Tracking is enabled

### Test Case 8.2: Prompting System Unavailable
**Setup**: Sophisticated system disabled
**Test**: Deploy any agent
**Verify**:
- Falls back to legacy enhancement
- No errors thrown
- Basic functionality maintained

### Test Case 8.3: Partial Failure
**Setup**: AI generation fails, bridge available
**Test**: Deploy agent with complex task
**Verify**:
- Attempts AI generation
- Falls back to bridge
- Logs failure appropriately

## Performance Tests

### Test Case 9.1: Response Time
**Metric**: Time to generate prompt
**Target**: < 500ms for simple tasks
**Target**: < 2s for complex tasks with AI generation

### Test Case 9.2: Token Efficiency
**Metric**: Prompt length vs output quality
**Target**: Simple tasks use < 500 tokens
**Target**: Complex tasks use < 2000 tokens

## Validation Metrics

### Quantitative Metrics
1. **Response Length Appropriateness**
   - Simple queries: < 200 words
   - Analysis tasks: 500-1000 words
   - Action confirmations: < 100 words

2. **Context Integration Rate**
   - User context included: 100%
   - Memory context when relevant: > 80%
   - Task characteristics identified: 100%

3. **Fallback Rate**
   - Sophisticated system success: > 90%
   - Bridge fallback: < 10%
   - Legacy fallback: < 1%

### Qualitative Metrics
1. **Task Relevance**: Response directly addresses the task
2. **Tone Appropriateness**: Matches user expertise level
3. **Structure Fit**: Format matches task type
4. **No Over-Engineering**: Simple tasks get simple responses

## Test Execution Plan

### Phase 1: Unit Tests (Day 1)
- Test individual methods in isolation
- Mock external dependencies
- Verify logic correctness

### Phase 2: Integration Tests (Day 2)
- Test component interactions
- Real database and services
- End-to-end prompt generation

### Phase 3: User Acceptance Tests (Day 3)
- Real user scenarios
- Various agent types
- Different task complexities

### Phase 4: Performance Tests (Day 4)
- Load testing
- Response time measurement
- Token usage analysis

### Phase 5: Regression Tests (Day 5)
- Ensure existing functionality intact
- Verify no breaking changes
- Validate fallback mechanisms

## Success Criteria

✅ **Pass Criteria**:
1. 100% of simple queries receive concise responses
2. 100% of tasks use real user context (not hardcoded)
3. > 90% of prompts generated by sophisticated system
4. Average response quality score > 8/10
5. No regression in existing functionality

❌ **Fail Criteria**:
1. Any simple query receives business framework response
2. Hardcoded user context still in use
3. Sophisticated system success rate < 80%
4. Response time > 5s for any task
5. Any agent deployment failures

## Test Data

### User Profiles
```python
TEST_USERS = [
    {
        'username': 'tech_expert',
        'profession': 'Software Engineer',
        'expertise_level': 'advanced',
        'interests': ['coding', 'ai', 'startups']
    },
    {
        'username': 'business_user',
        'profession': 'CEO',
        'expertise_level': 'intermediate',
        'interests': ['strategy', 'growth', 'leadership']
    },
    {
        'username': 'new_user',
        'profession': None,
        'expertise_level': 'beginner',
        'interests': []
    }
]
```

### Test Tasks
```python
TEST_TASKS = {
    'simple': [
        "What time is it?",
        "What's the weather?",
        "Define machine learning"
    ],
    'analysis': [
        "Analyze our conversion funnel",
        "Review this month's performance",
        "Evaluate market opportunity"
    ],
    'creation': [
        "Write a LinkedIn post",
        "Create a project plan",
        "Design a landing page"
    ],
    'research': [
        "Research AI tools for marketing",
        "Find best practices for remote work",
        "Investigate blockchain use cases"
    ],
    'action': [
        "Schedule team standup",
        "Send report to client",
        "Set reminder for tomorrow"
    ]
}
```