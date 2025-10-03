# UKF Agent Integration Guide

## Overview

This guide provides comprehensive documentation for integrating agents with the Unified Knowledge Framework (UKF) system. The UKF enables agents to access, store, and share knowledge across the entire AI agent ecosystem.

**Status**: Phase C2 Complete - All 74 agents integrated with UKF (100% success rate)
**Version**: 1.0
**Last Updated**: August 4, 2025

## 🎯 Key Benefits

### For Agents:
- **Persistent Memory**: Access to all historical insights and learnings
- **Knowledge Sharing**: Learn from other agents' experiences and solutions
- **Context Continuity**: Maintain context across conversations and sessions
- **Intelligent Search**: Semantic and keyword search capabilities
- **Performance Enhancement**: Build upon previous analyses and recommendations

### For Users:
- **Consistent Experience**: Agents remember preferences and context
- **Improved Quality**: Responses informed by historical insights
- **Knowledge Continuity**: Work builds upon previous sessions
- **Personalization**: Agents adapt based on user patterns and preferences

## 🏗️ Architecture Overview

### UKF Components:
1. **UnifiedMemoryService** - Core service for memory operations
2. **AgentUKFIntegrator** - Helper class for agent-specific operations
3. **UKFIntegrationFramework** - Standardized integration patterns
4. **Memory Models** - Data structures for storing and retrieving memories

### Integration Layers:
1. **System Prompt Integration** - UKF capabilities added to agent prompts
2. **Function Access** - Direct UKF function calls within agent responses
3. **Context Injection** - Automatic memory context in conversations
4. **Storage Patterns** - Standardized memory creation and updates

## 🔧 Technical Implementation

### Agent Categories and Integration Patterns

The UKF integration system automatically categorizes agents and applies appropriate integration patterns:

#### Business Agents (74/74 agents)
**Integration Pattern**: Business-focused UKF prompts with market intelligence capabilities
**Use Cases**: Market analysis, competitive intelligence, business strategy, financial planning
**Example Agents**: Business Agent, Marketing Agent, Financial Agent, Market Research Specialist

#### Technical Agents (Future)
**Integration Pattern**: Technical-focused UKF prompts with architecture and code capabilities
**Use Cases**: Code solutions, architecture decisions, technical documentation, troubleshooting
**Example Use**: Store technical solutions, reference previous architectural decisions

#### Creative Agents (Future)
**Integration Pattern**: Creative-focused UKF prompts with content and campaign capabilities
**Use Cases**: Content strategy, creative concepts, brand guidelines, campaign performance
**Example Use**: Reference successful campaigns, maintain brand consistency

#### Basic Agents (Future)
**Integration Pattern**: General UKF prompts with universal memory capabilities
**Use Cases**: General assistance, task completion, user preferences
**Example Use**: Remember user preferences, maintain conversation context

### UKF Functions Available to Agents

#### 1. search_unified_memory(query, search_type='semantic', limit=10)
Search the unified knowledge system for relevant information.

**Parameters**:
- `query`: Search query (natural language or keywords)
- `search_type`: 'semantic' for conceptual search, 'keyword' for exact matches
- `limit`: Maximum number of results (default 10)

**Usage Examples**:
```python
# Semantic search for business concepts
search_unified_memory("marketing campaign performance analysis", search_type='semantic')

# Keyword search for specific terms
search_unified_memory("API rate limiting", search_type='keyword')

# Limited results for quick context
search_unified_memory("user preferences", limit=5)
```

#### 2. store_unified_memory(content, title, summary, importance=0.7, topics=[], technologies=[], projects=[])
Store important insights or information in the unified knowledge system.

**Parameters**:
- `content`: Main content to store (detailed information)
- `title`: Short descriptive title
- `summary`: Brief summary of the content
- `importance`: Importance score 0.0-1.0 (0.7+ recommended for valuable insights)
- `topics`: List of relevant topics/categories
- `technologies`: List of technologies mentioned (if applicable)
- `projects`: List of related projects (if applicable)

**Usage Examples**:
```python
# Store business insight
store_unified_memory(
    content="Email campaign with personalized subject lines achieved 25% higher CTR compared to generic subjects",
    title="Email Personalization Success",
    summary="Personalized email subject lines improve CTR by 25%",
    importance=0.8,
    topics=["email_marketing", "personalization", "campaign_optimization"],
    projects=["q4_email_campaign"]
)

# Store technical solution
store_unified_memory(
    content="Implemented Redis caching for API responses, reduced response time from 800ms to 120ms",
    title="API Performance Optimization",
    summary="Redis caching improved API performance by 85%",
    importance=0.9,
    topics=["performance", "caching", "api_optimization"],
    technologies=["redis", "python", "django"]
)
```

### Memory Context Integration Pattern

All integrated agents follow this pattern for memory-aware responses:

#### 1. Context Search Phase
- Search UKF for relevant past insights before responding
- Look for: similar questions, related projects, previous solutions
- Consider: user history, project context, domain expertise

#### 2. Context Integration Phase
- Reference relevant past insights in responses
- Build upon previous recommendations or decisions
- Acknowledge continuity: "Based on our previous analysis of X..."
- Avoid repeating outdated or superseded information

#### 3. Learning Storage Phase
- After providing response, identify new insights to store
- Store: new solutions, user preferences, successful approaches
- Update: existing knowledge with new information or corrections

#### 4. Context Attribution
- When referencing UKF content, acknowledge the source
- Use phrases like: "From previous analysis..." or "Building on earlier insights..."
- Maintain transparency about knowledge sources

## 🚀 Implementation Status

### Phase C2 Results (August 4, 2025):
- ✅ **74/74 agents** successfully integrated with UKF (100% success rate)
- ✅ **UKF Integration Framework** created and deployed
- ✅ **Standardized integration patterns** implemented
- ✅ **Memory context injection** patterns established
- ✅ **Testing infrastructure** created and validated

### Integration Statistics:
- **Total Agent Templates**: 74
- **Successfully Updated**: 74 (100%)
- **Skipped (already integrated)**: 0
- **Errors**: 0
- **Success Rate**: 100%

### Agent Categorization Results:
- **Business Agents**: 74 (100% of current agents)
- **Technical Agents**: 0 (future expansion)
- **Creative Agents**: 0 (future expansion)
- **Basic Agents**: 0 (future expansion)

## 📊 Usage Guidelines

### For Agent Developers

#### Best Practices:
1. **Always search before responding**: Check UKF for relevant context
2. **Store valuable insights**: Capture important learnings for future reference
3. **Use appropriate importance scores**: 0.8+ for critical insights, 0.6+ for useful information
4. **Include rich metadata**: Topics, technologies, and projects for better searchability
5. **Reference previous work**: Build upon existing knowledge rather than starting fresh

#### Common Patterns:
```python
# Pattern 1: Search and Reference
previous_insights = search_unified_memory("user's marketing preferences")
# Use insights to inform response, then reference: "Based on your previous preference for email marketing..."

# Pattern 2: Store New Learning
store_unified_memory(
    content="User prefers data-driven marketing approaches with clear ROI metrics",
    title="User Marketing Preference",
    summary="Data-driven marketing with ROI focus preferred",
    importance=0.7,
    topics=["user_preferences", "marketing_strategy"]
)

# Pattern 3: Update Existing Knowledge
# Search for existing insights, then store updated information with higher importance
```

### For System Administrators

#### Monitoring UKF Usage:
- Monitor agent UKF search patterns in logs
- Track memory creation rates and storage patterns
- Validate search result quality and relevance
- Monitor system performance under UKF load

#### Maintenance Tasks:
- Regular embedding generation for new memories
- Index optimization for search performance
- Data quality validation and cleanup
- Memory archival for old or obsolete information

## 🔍 Troubleshooting

### Common Issues:

#### 1. Search Returns No Results
**Cause**: Query too specific or no relevant memories exist
**Solution**: 
- Try broader search terms
- Use semantic search for conceptual queries
- Check if memories exist for the domain

#### 2. Memory Storage Fails
**Cause**: Invalid parameters or database connection issues
**Solution**:
- Validate required parameters (content, title, agent_name)
- Check database connectivity
- Verify user context is available

#### 3. Context Not Available
**Cause**: UKF service not properly initialized
**Solution**:
- Ensure UnifiedMemoryService is initialized with user_id
- Verify agent has access to UKF functions
- Check agent template integration status

#### 4. Performance Issues
**Cause**: Large result sets or complex queries
**Solution**:
- Use appropriate limit parameters
- Optimize search queries
- Consider caching for frequent searches

### Debugging Commands:

```bash
# Test UKF integration for specific agent
python manage.py test_agent_ukf_integration --agent-id=1

# Comprehensive UKF testing
python manage.py test_agent_ukf_integration --comprehensive

# Check UKF system health
python manage.py check_ukf_health

# Validate agent integration status
python manage.py integrate_agents_with_ukf --dry-run
```

## 📈 Performance Metrics

### Current Performance (Post Phase C2):
- **UKF Coverage**: 99.9% (39,736/39,784 records with embeddings)
- **Search Performance**: <0.5s average response time
- **Storage Success Rate**: 99%+ for valid requests
- **Agent Integration Rate**: 100% (74/74 agents)

### Performance Targets:
- **Search Response**: <500ms for 95% of queries
- **Storage Response**: <200ms for memory creation
- **Memory Availability**: 99.9% uptime
- **Search Accuracy**: >90% relevant results for business queries

## 🔗 Related Documentation

- **Phase C1 Implementation**: `documentation/reviews/session-C-memory-knowledge/phase-c1-completion.md`
- **UKF Service Documentation**: `backend/shared_memory/services.py`
- **Agent Templates**: `backend/agent_orchestra/models.py`
- **Integration Framework**: `backend/agent_orchestra/ukf_integration_framework.py`

## 🎯 Next Steps

### Phase C3: Memory System Consolidation
- Migrate legacy memory systems to UKF
- Consolidate conversation embeddings and learning intelligence
- Optimize system performance for larger datasets
- Implement advanced search and ranking algorithms

### Future Enhancements:
- **Multi-tenant UKF**: Separate knowledge bases for different organizations
- **Knowledge Graphs**: Relationship mapping between memories and concepts
- **Advanced Analytics**: Usage patterns and knowledge discovery
- **Real-time Collaboration**: Live knowledge sharing between agents

## 📞 Support

For technical questions or issues with UKF integration:

1. **Check Logs**: Review Django logs for UKF-related errors
2. **Run Tests**: Use the test commands to validate integration
3. **Review Documentation**: Check this guide and related documentation
4. **System Health**: Monitor UKF system health and performance metrics

**Integration Status**: ✅ Phase C2 Complete - Ready for Production Use
**Next Phase**: C3 - Memory System Consolidation