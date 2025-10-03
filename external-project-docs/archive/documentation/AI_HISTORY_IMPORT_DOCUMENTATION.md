# AI History Import System Documentation

## Overview

The AI History Import System allows users to import their conversation history from other AI platforms (ChatGPT, Claude, Grok, Bard, etc.) to instantly have a rich history in Donkey Betz instead of starting from scratch.

## Architecture

### Backend Components

1. **Models** (`ai_partner/conversation_import_models.py`)
   - `ConversationImport`: Tracks import jobs with progress
   - `ImportedConversation`: Links imported conversations to import jobs

2. **Parsers** (`ai_partner/services/conversation_import_parsers.py`)
   - `ChatGPTParser`: Handles ChatGPT's complex mapping structure
   - `ClaudeParser`: Supports both JSON and CSV formats
   - `GrokParser`: Flexible parser for various Grok formats
   - `BardParser`: Google Takeout format support
   - `UniversalParser`: Auto-detection for unknown formats

3. **Import Service** (`ai_partner/services/conversation_import_service.py`)
   - Manages the import process with async Celery tasks
   - Handles deduplication using content hashing
   - Generates embeddings for imported conversations
   - Ensures user data isolation

4. **API Views** (`ai_partner/views_conversation_import.py`)
   - `POST /api/ai-partner/conversation-import/` - Start new import
   - `GET /api/ai-partner/conversation-import/<id>/status/` - Check progress
   - `GET /api/ai-partner/conversation-imports/` - List user's imports
   - `GET /api/ai-partner/conversation-import/stats/` - Import statistics
   - `DELETE /api/ai-partner/conversation-import/<id>/cancel/` - Cancel import

### Frontend Components

1. **ConversationImport Component** (`ConversationImport.tsx`)
   - Multi-step wizard interface
   - Platform selection with export instructions
   - Drag-and-drop file upload
   - Real-time progress tracking

2. **ImportWizardModal** (`ImportWizardModal.tsx`)
   - Onboarding modal for new users
   - Explains benefits of importing history
   - Skip option for later

3. **Import Service** (`importService.ts`)
   - API client for import endpoints
   - New user detection logic
   - Stats and progress tracking

## User Flow

### First-Time User Experience

1. User logs in for the first time
2. System detects no conversation history
3. Import wizard modal appears automatically
4. User can:
   - Select their AI platform
   - Follow export instructions
   - Upload their export file
   - Skip for later

### Import Process

1. **Platform Selection**
   - User chooses from supported platforms
   - Platform-specific instructions displayed

2. **File Upload**
   - Drag-and-drop or click to upload
   - File validation by platform type

3. **Processing**
   - Async processing with Celery
   - Real-time progress updates
   - Shows imported/failed/duplicate counts

4. **Completion**
   - Success message with stats
   - Option to start chatting or import more

## Privacy & Security

### User Data Isolation

- All queries filter by `user` field
- Import jobs belong to specific users
- No cross-user data access possible

### Deduplication

- Content-based hashing prevents duplicates
- Checks by both content hash and original ID
- Platform-specific duplicate detection

### Data Handling

- Temporary file storage during import
- Files deleted after processing
- No permanent storage of raw exports

## Platform Export Formats

### ChatGPT
```json
{
  "conversations": [{
    "title": "Conversation Title",
    "create_time": 1234567890,
    "conversation_id": "uuid",
    "mapping": {
      "message_id": {
        "message": {
          "author": {"role": "user/assistant"},
          "content": {"parts": ["message text"]}
        }
      }
    }
  }]
}
```

### Claude
```json
[{
  "conversation_id": "...",
  "created_at": "2024-01-01T00:00:00Z",
  "messages": [
    {"role": "human", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}]
```

### Generic Format
The system attempts to detect:
- Arrays of conversations
- Objects with "conversations" key
- Message role indicators
- Timestamp fields

## Technical Implementation

### Async Processing

```python
@shared_task
def process_conversation_import(import_job_id: int):
    """Celery task for async import processing"""
    service = ConversationImportService()
    return service.process_import(import_job_id)
```

### Embedding Generation

- Uses existing `ConversationEmbeddingPipeline`
- Generates embeddings for each imported conversation
- Enables semantic search on imported history

### Error Handling

- Graceful handling of malformed exports
- Per-conversation error tracking
- Partial success support

## Testing Checklist

- [ ] Test ChatGPT JSON import
- [ ] Test Claude JSON/CSV import
- [ ] Test duplicate detection
- [ ] Test user isolation
- [ ] Test onboarding flow
- [ ] Test progress tracking
- [ ] Test error handling
- [ ] Test embedding generation

## Future Enhancements

1. Support more platforms (Perplexity, Poe, etc.)
2. Selective import (date ranges, topics)
3. Import preview before processing
4. Merge similar conversations
5. Export in Donkey Betz format