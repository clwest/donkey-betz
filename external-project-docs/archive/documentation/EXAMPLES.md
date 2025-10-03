# 🚀 Universal Knowledge Format (UKF) - Examples & Quickstart

This document provides practical examples of using the Universal Knowledge Format system.

## 🎯 Quick Start

### 1. Basic Setup

```bash
# Navigate to UKF directory
cd /Users/donkeyking/development/universal_knowledge_system/ukf

# Run quick validation
python test_framework.py --quick

# Initialize database and ingest data
python ingestion_pipeline.py --config ingestion_config.json
```

### 2. Create Your First UKF Entry

```python
from schema import UKFGenerator, EntryType, ParticipantType, PrimaryType

# Initialize generator
generator = UKFGenerator()

# Create a conversation entry
entry = generator.create_entry(
    content_raw="I'm having trouble with Redis authentication in my Django app. Can you help?",
    entry_type=EntryType.CONVERSATION,
    sender_id="chris",
    sender_type=ParticipantType.HUMAN,
    receiver_id="assistant",
    receiver_type=ParticipantType.AI_ASSISTANT,
    platform="move_that_ass",
    format="chat",
    location="memory://debugging_session_001",
    primary_type=PrimaryType.QUESTION,
    categories=["debugging", "infrastructure"],
    tags=["redis", "django", "authentication"],
    session_id="debugging_session_001"
)

print(f"Created entry: {entry.id}")
print(f"Summary: {entry.content.summary}")
```

### 3. Search Across All Knowledge

```python
from universal_search import UniversalKnowledgeSearch, SearchFilter

# Initialize search
search = UniversalKnowledgeSearch("ukf_database.db")

# Basic search
results = search.search("redis debugging")
print(f"Found {results.total_count} entries")

# Advanced filtered search
filters = SearchFilter(
    types=["conversation", "document"],
    categories=["debugging"],
    tags=["redis"],
    date_range={"from": "2024-01-01", "to": "2025-12-31"},
    importance=["high", "critical"]
)

filtered_results = search.search("authentication", filters)
for result in filtered_results.results:
    print(f"- {result.title} ({result.platform}) - Score: {result.relevance_score}")
```

## 📚 Complete Examples

### Example 1: Ingesting ChatGPT Conversations

```python
from conversation_parsers import ChatGPTParser
from ingestion_pipeline import UniversalIngestionPipeline

# Initialize components
parser = ChatGPTParser()
pipeline = UniversalIngestionPipeline("ukf_database.db")

# Parse ChatGPT export
entries = parser.parse_conversations("chatgpt_conversations.json")
print(f"Parsed {len(entries)} conversation entries")

# Store in UKF database
for entry in entries:
    pipeline._store_entry(entry)

print(f"Migration stats: {parser.stats}")
```

### Example 2: Processing Documents

```python
from document_processors import DocumentProcessorManager

manager = DocumentProcessorManager()

# Process different document types
sources = [
    "/path/to/document.pdf",
    "https://example.com/article",
    "https://youtube.com/watch?v=example"
]

for source in sources:
    entry = manager.process_document(source, project="research")
    if entry:
        print(f"Processed: {entry.source.location}")
        print(f"Categories: {entry.classification.categories}")
        print(f"Tags: {entry.classification.tags}")
```

### Example 3: Agent Communication Integration

```python
from agent_communication_converters import AgentCommunicationConverter

converter = AgentCommunicationConverter()

# Convert live orchestration
orchestration_data = {
    'id': 'orch_001',
    'user_id': 'chris',
    'initial_request': {
        'user_message': 'Create a business plan for AI-powered fitness tracking',
        'selected_agents': ['business_strategy_agent', 'market_research_agent']
    },
    'agent_results': [
        {
            'agent_name': 'business_strategy_agent',
            'status': 'completed',
            'result': 'Market analysis shows $2.4B TAM for AI fitness apps...',
            'execution_time': 45.2
        }
    ],
    'final_result': {
        'overall_status': 'completed',
        'consolidated_result': 'Comprehensive business plan with market validation...'
    }
}

entries = converter.convert_orchestration_session(orchestration_data)
print(f"Converted orchestration to {len(entries)} UKF entries")
```

### Example 4: Live Conversation Integration

```python
from conversation_parsers import LiveConversationParser

parser = LiveConversationParser()

# Parse real-time conversation
entries = parser.parse_live_conversation(
    user_message="Help me debug this Redis connection timeout",
    assistant_response="Let's check your Redis configuration. First, verify the connection string...",
    conversation_id="live_debug_session",
    context={'project': 'move_that_ass', 'issue_type': 'infrastructure'}
)

# Entries are ready for storage
for entry in entries:
    print(f"Entry: {entry.participants.sender.id} → {entry.participants.receiver.id}")
    print(f"Content: {entry.content.summary}")
```

### Example 5: Migration from Existing Systems

```python
from migration_tools import MigrationManager

# Initialize migration
manager = MigrationManager("ukf_database.db")

# Migrate from UCKS
ucks_result = manager.migrate_ucks_database("ucks_knowledge.db")
print(f"UCKS Migration: {ucks_result['entries_migrated']} entries")

# Migrate from move_that_ass
mta_result = manager.migrate_move_that_ass_data("move_that_ass/db.sqlite3")
print(f"Move That Ass Migration: {mta_result['entries_migrated']} entries")

# Migrate ChatGPT exports
chatgpt_result = manager.migrate_chatgpt_exports("chatgpt_exports/")
print(f"ChatGPT Migration: {chatgpt_result['entries_migrated']} entries")

# Get overall stats
stats = manager.get_migration_stats()
print(f"Total migrated: {stats['total_migrated']}")
print(f"By source: {stats['by_source']}")
```

### Example 6: Temporal Analysis

```python
from temporal_integrity import TemporalIntegrityManager

temporal = TemporalIntegrityManager("ukf_database.db")

# Validate temporal integrity
report = temporal.validate_temporal_integrity()
print(f"Integrity Score: {report['integrity_score']}%")
print(f"Total Issues: {report['total_issues']}")

# Establish relationships
relationships = temporal.establish_temporal_relationships()
print(f"Created {relationships} temporal relationships")

# Analyze patterns
patterns = temporal.analyze_temporal_patterns()
print("Activity by hour:", patterns['activity_by_hour'])

# Generate timeline
timeline = temporal.generate_temporal_timeline({
    'project': 'move_that_ass',
    'limit': 20
})

for item in timeline:
    print(f"{item['timestamp']}: {item['summary']}")
```

## 🔧 Integration Examples

### Django Integration

```python
# In your Django views.py
from ukf.conversation_parsers import LiveConversationParser
from ukf.ingestion_pipeline import UniversalIngestionPipeline

def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST['message']
        
        # Process with your AI
        ai_response = your_ai_process(user_message)
        
        # Convert to UKF
        parser = LiveConversationParser()
        entries = parser.parse_live_conversation(
            user_message=user_message,
            assistant_response=ai_response,
            conversation_id=request.session.session_key,
            context={'project': 'django_app', 'user_id': request.user.id}
        )
        
        # Store in UKF database
        pipeline = UniversalIngestionPipeline("ukf_database.db")
        for entry in entries:
            pipeline._store_entry(entry)
        
        return JsonResponse({'response': ai_response})
```

### Memory Palace Integration

```python
# Integrate with existing Memory Palace
from ukf.universal_search import MemoryPalaceSearchAdapter

class EnhancedMemoryRetrieval:
    def __init__(self):
        self.ukf_search = UniversalKnowledgeSearch("ukf_database.db")
        self.adapter = MemoryPalaceSearchAdapter(self.ukf_search)
    
    def find_relevant_memories(self, query: str, limit: int = 10):
        # This now searches across ALL knowledge sources
        memories = self.adapter.find_relevant_memories(query, limit)
        
        # Convert to existing format
        return [
            {
                'content': memory['content'],
                'relevance_score': memory['relevance_score'],
                'source': memory['source'],
                'created_at': memory['created_at']
            }
            for memory in memories
        ]
```

### Agent Integration

```python
# For AI agents to search across all knowledge
from ukf.universal_search import AgentSearchAdapter

class EnhancedAgent:
    def __init__(self, agent_name: str):
        self.name = agent_name
        self.ukf_search = UniversalKnowledgeSearch("ukf_database.db")
        self.adapter = AgentSearchAdapter(self.ukf_search)
    
    def search_knowledge(self, query: str, context: dict = None):
        # Search across conversations, documents, previous agent results
        knowledge = self.adapter.search_knowledge(query, context)
        
        return [
            {
                'title': item['title'],
                'content': item['content'],
                'source': item['source'],
                'relevance': item['relevance'],
                'type': item['type']
            }
            for item in knowledge
        ]
```

## 🧪 Testing Examples

### Unit Testing

```python
import unittest
from ukf.schema import UKFGenerator, UKFValidator

class TestUKF(unittest.TestCase):
    def setUp(self):
        self.generator = UKFGenerator()
        self.validator = UKFValidator()
    
    def test_entry_creation(self):
        entry = self.generator.create_entry(
            content_raw="Test content",
            entry_type=EntryType.CONVERSATION,
            sender_id="test",
            sender_type=ParticipantType.HUMAN,
            receiver_id="assistant",
            receiver_type=ParticipantType.AI_ASSISTANT,
            platform="test",
            format="test",
            location="test://location",
            primary_type=PrimaryType.CONVERSATION
        )
        
        self.assertIsNotNone(entry.id)
        self.assertTrue(self.validator.validate_entry(entry))
    
    def test_search_functionality(self):
        search = UniversalKnowledgeSearch("test_database.db")
        results = search.search("test query")
        self.assertIsNotNone(results)
        self.assertGreaterEqual(results.total_count, 0)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# Full pipeline test
def test_full_pipeline():
    # Create test database
    pipeline = UniversalIngestionPipeline("test_ukf.db")
    
    # Create and store entry
    generator = UKFGenerator()
    entry = generator.create_entry(
        content_raw="Integration test content with Redis and debugging",
        entry_type=EntryType.CONVERSATION,
        sender_id="test_user",
        sender_type=ParticipantType.HUMAN,
        receiver_id="assistant",
        receiver_type=ParticipantType.AI_ASSISTANT,
        platform="test",
        format="chat",
        location="test://integration",
        primary_type=PrimaryType.QUESTION,
        tags=["redis", "debugging", "test"]
    )
    
    # Store entry
    assert pipeline._store_entry(entry)
    
    # Search for entry
    search = UniversalKnowledgeSearch("test_ukf.db")
    results = search.search("redis debugging")
    
    # Verify results
    assert results.total_count > 0
    assert any(result.id == entry.id for result in results.results)
    
    print("✅ Full pipeline test passed")
```

## 📊 Monitoring and Analytics

### Statistics Dashboard

```python
def get_ukf_dashboard_stats():
    search = UniversalKnowledgeSearch("ukf_database.db")
    temporal = TemporalIntegrityManager("ukf_database.db")
    
    # Basic stats
    stats = search.get_statistics()
    
    # Temporal patterns
    patterns = temporal.analyze_temporal_patterns()
    
    # Recent activity
    timeline = temporal.generate_temporal_timeline({
        'start_date': (datetime.now() - timedelta(days=7)).isoformat(),
        'limit': 100
    })
    
    return {
        'total_entries': stats['total_entries'],
        'by_platform': stats['by_platform'],
        'by_type': stats['by_type'],
        'recent_activity': len(timeline),
        'peak_activity_hour': max(patterns['activity_by_hour'], key=lambda x: x['count'])['hour'],
        'integrity_score': temporal.validate_temporal_integrity()['integrity_score']
    }
```

## 🎯 Real-World Use Cases

### Use Case 1: Debugging Assistant

```python
class DebuggingAssistant:
    def __init__(self):
        self.search = UniversalKnowledgeSearch("ukf_database.db")
    
    def find_similar_issues(self, error_description: str):
        # Search across all debugging sessions
        filters = SearchFilter(
            categories=["debugging"],
            success_status=["succeeded"],
            importance=["high", "critical"]
        )
        
        results = self.search.search(error_description, filters)
        
        return [
            {
                'solution': result.content_snippet,
                'context': result.categories,
                'success_rate': result.relevance_score,
                'when': result.created_at
            }
            for result in results.results[:5]
        ]
```

### Use Case 2: Knowledge Discovery

```python
class KnowledgeDiscovery:
    def __init__(self):
        self.search = UniversalKnowledgeSearch("ukf_database.db")
    
    def discover_connections(self, topic: str):
        # Find all related entries
        results = self.search.search(topic, include_aggregations=True)
        
        # Analyze connections
        connections = {
            'related_topics': set(),
            'key_people': set(),
            'technologies': set(),
            'projects': set()
        }
        
        for result in results.results:
            connections['related_topics'].update(result.categories)
            connections['technologies'].update(result.tags)
            if result.project:
                connections['projects'].add(result.project)
        
        return {k: list(v) for k, v in connections.items()}
```

### Use Case 3: Learning Progress Tracker

```python
class LearningTracker:
    def __init__(self):
        self.search = UniversalKnowledgeSearch("ukf_database.db")
        self.temporal = TemporalIntegrityManager("ukf_database.db")
    
    def track_skill_development(self, skill: str, timeframe_days: int = 90):
        start_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()
        
        # Find all entries related to the skill
        filters = SearchFilter(
            tags=[skill],
            date_range={"from": start_date},
            limit=1000
        )
        
        results = self.search.search(skill, filters)
        
        # Analyze progression
        progression = {
            'questions_asked': 0,
            'solutions_found': 0,
            'projects_completed': 0,
            'skill_level_trend': []
        }
        
        for result in results.results:
            if result.type == 'conversation' and 'question' in result.summary.lower():
                progression['questions_asked'] += 1
            elif result.success_status == 'succeeded':
                progression['solutions_found'] += 1
        
        return progression
```

## 🚀 Next Steps

1. **Install Dependencies**: Ensure all required packages are installed
2. **Run Tests**: Use `python test_framework.py` to validate your setup
3. **Start Ingestion**: Use `python ingestion_pipeline.py` to begin importing data
4. **Build Integrations**: Connect UKF to your existing systems
5. **Monitor Progress**: Use the analytics tools to track your knowledge growth

## 📞 Support

For issues or questions:
- Check the test framework output for validation errors
- Review the ingestion logs for import issues
- Examine the temporal integrity reports for data quality

The Universal Knowledge Format creates a unified view of ALL your knowledge - conversations, documents, agent communications, and more - searchable through a single interface with identical results every time! 🎯