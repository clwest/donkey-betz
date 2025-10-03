# Unified User Memory System

A comprehensive framework for managing and utilizing user conversation memories from multiple sources (OpenAI ChatGPT, Claude, etc.) as a foundation for new projects.

## Overview

This system provides a unified approach to:
- Import conversation data from various AI platforms
- Extract and normalize memories into a consistent format
- Store memories in a searchable database
- Query and analyze conversation history
- Export memories for use in new projects

## Components

### 1. `analyze_conversations.py`
Quick analysis tool to understand the structure of conversation JSON files.

### 2. `conversation_processor.py`
Memory-efficient processor for converting large conversation files into a normalized format.

### 3. `unified_memory_system.py`
Main framework that provides:
- SQLite database storage
- Adapter pattern for multiple sources
- Search and query capabilities
- Export functionality

### 4. Web Interface (`memory_browser.html`)
Visual browser for exploring memories with search and filtering capabilities.

## Installation

```bash
# Clone or download the scripts to your development directory
cd /Users/donkeyking/development/

# No additional dependencies required - uses Python standard library
```

## Usage

### Step 1: Analyze Your Data

First, understand the structure of your conversation files:

```bash
python analyze_conversations.py
```

This will show you:
- File size and structure
- Number of conversations
- Message formats
- Date ranges
- Common patterns

### Step 2: Process Conversations

For large files, use the processor to convert conversations:

```bash
python conversation_processor.py
```

This creates individual JSON files for each conversation in a `processed_memories` directory.

### Step 3: Import to Unified System

Use the unified memory system to import all conversations:

```python
from unified_memory_system import UnifiedMemorySystem

# Initialize the system
memory_system = UnifiedMemorySystem("user_memory.db")

# Import OpenAI conversations
memory_system.import_conversations(
    source="openai",
    file_path="/path/to/conversations.json"
)

# Get statistics
stats = memory_system.get_statistics()
print(stats)
```

### Step 4: Query and Use Memories

```python
# Search for specific content
results = memory_system.search_memories("python programming")

# Get conversations by topic
python_convs = memory_system.get_conversations_by_topic("python")

# Get timeline of memories
timeline = memory_system.get_memory_timeline(
    start_time=datetime(2024, 1, 1).timestamp(),
    end_time=datetime(2024, 12, 31).timestamp()
)

# Export for use in new project
memory_system.export_memories("memories_export.json")
```

## Memory Schema

The unified memory format:

```json
{
  "id": "unique_memory_id",
  "source": "openai|claude|custom",
  "conversation_id": "parent_conversation_id",
  "timestamp": 1234567890.0,
  "content": "The actual message content",
  "role": "user|assistant|system",
  "metadata": {
    "model": "gpt-4",
    "title": "Conversation Title",
    "custom_field": "value"
  },
  "context": {
    "topics": ["python", "memory", "ai"],
    "entities": ["OpenAI", "ChatGPT"],
    "sentiment": "positive",
    "preferences": {}
  }
}
```

## Using Memories in New Projects

### 1. As Training Data

```python
# Load exported memories
import json

with open("memories_export.json", "r") as f:
    memories = json.load(f)

# Filter for specific use cases
training_data = [
    {
        "input": m["content"],
        "output": next_message["content"]
    }
    for m, next_message in zip(memories[:-1], memories[1:])
    if m["role"] == "user" and next_message["role"] == "assistant"
]
```

### 2. As Context for AI Assistants

```python
# Build user profile from memories
def build_user_profile(memories):
    profile = {
        "interests": extract_topics(memories),
        "communication_style": analyze_style(memories),
        "preferences": extract_preferences(memories),
        "knowledge_areas": identify_expertise(memories)
    }
    return profile

# Use in prompts
user_profile = build_user_profile(memories)
prompt = f"""Based on the user's profile:
{json.dumps(user_profile, indent=2)}

Please provide a personalized response to: {user_query}
"""
```

### 3. As Knowledge Base

```python
# Create a semantic search index
from your_embedding_library import create_embeddings, search

# Index memories
memory_embeddings = create_embeddings([m["content"] for m in memories])

# Search for relevant context
relevant_memories = search(query, memory_embeddings, top_k=5)
```

## Advanced Features

### Custom Adapters

Add support for new sources by creating custom adapters:

```python
class ClaudeAdapter(MemoryAdapter):
    def load_conversations(self, source_path: str) -> List[Dict[str, Any]]:
        # Implementation for Claude format
        pass
    
    def extract_memories(self, conversation: Dict[str, Any]) -> List[Memory]:
        # Extract memories from Claude format
        pass

# Register the adapter
memory_system.adapters["claude"] = ClaudeAdapter()
```

### Memory Analysis

```python
# Analyze conversation patterns
def analyze_conversation_patterns(memory_system):
    # Get all memories
    memories = memory_system.get_memory_timeline()
    
    # Analyze response times
    response_times = []
    for i in range(len(memories)-1):
        if memories[i]["role"] == "user" and memories[i+1]["role"] == "assistant":
            time_diff = memories[i+1]["timestamp"] - memories[i]["timestamp"]
            response_times.append(time_diff)
    
    # Analyze topics over time
    topics_by_month = defaultdict(list)
    for memory in memories:
        month = datetime.fromtimestamp(memory["timestamp"]).strftime("%Y-%m")
        topics_by_month[month].extend(memory.get("context", {}).get("topics", []))
    
    return {
        "avg_response_time": sum(response_times) / len(response_times),
        "topics_timeline": topics_by_month
    }
```

## Privacy and Security Considerations

1. **Data Storage**: All memories are stored locally in SQLite database
2. **Sensitive Information**: Consider implementing filters for PII before processing
3. **Access Control**: Add authentication if deploying the web interface
4. **Data Retention**: Implement policies for memory expiration if needed

## Troubleshooting

### Memory Import Errors
- Check JSON file format matches expected structure
- Verify file encoding (should be UTF-8)
- For large files, increase batch_size parameter

### Search Performance
- Create indexes on frequently searched fields
- Consider full-text search for large datasets
- Implement caching for common queries

## Future Enhancements

1. **NLP Integration**: Add sentiment analysis, entity extraction
2. **Vector Embeddings**: Semantic search capabilities
3. **Multi-user Support**: Separate memory spaces per user
4. **API Interface**: RESTful API for memory operations
5. **Real-time Sync**: Auto-import new conversations
6. **Memory Decay**: Implement forgetting mechanisms

## Contributing

Feel free to extend the system with:
- New adapter implementations
- Additional analysis tools
- Enhanced search capabilities
- Visualization components

## License

This system is provided as-is for personal and research use. Ensure you comply with the terms of service of the platforms from which you export conversation data.