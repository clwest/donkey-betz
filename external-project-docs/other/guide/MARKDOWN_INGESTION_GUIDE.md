# Markdown Knowledge Ingestion System 📚🧠

## Overview

The Markdown Knowledge Ingestion System transforms scattered markdown documentation throughout the project into a searchable AI memory system. This allows the AI to access millions of tokens of investigation notes, chat logs, and documentation that would otherwise be too large for any single session.

## Architecture

### Components

1. **MarkdownCatalog** - Discovers and categorizes all .md files
2. **MarkdownChunker** - Intelligently chunks content respecting markdown structure  
3. **MarkdownMemoryIngester** - Stores chunks in Django Memory model with deduplication
4. **Code Assistant Integration** - Searches markdown memories for enhanced responses

### File Categories

Files are automatically categorized based on keywords in filenames:

- **investigation**: REALITY, TEST, MYSTERY, INVESTIGATION, SPACE_MAN, ENGINE
- **chat_logs**: CHAT, Q&A, CONVERSATION, HANDOFF, SESSION
- **documentation**: README, GUIDE, SETUP, API, DOCS, CLAUDE.md
- **fixes**: FIX, EMERGENCY, PATCH, SOLUTION, RESOLVED
- **reports**: REPORT, SUMMARY, DEBRIEF, STATUS, ANALYSIS
- **stories**: STORY, TALE, NARRATIVE, ADVENTURE
- **general**: Everything else

## Usage

### Quick Start

```bash
# Activate backend environment
cd backend && source .venv/bin/activate

# Run full ingestion
python manage.py ingest_markdown

# Or test with small batch first
python scripts/test_markdown_ingestion.py

# Test search functionality
python scripts/test_markdown_ingestion.py search
```

### Command Options

```bash
# Specify custom root path
python manage.py ingest_markdown --path /path/to/markdown/files

# Run in test mode (limited files)
python manage.py ingest_markdown --test
```

## Implementation Details

### Token Limits
- Max 2000 tokens per chunk
- 200 token overlap between chunks
- Uses tiktoken with cl100k_base encoding

### Chunking Strategy
1. First tries to split by markdown headers (# ## ### etc)
2. If section too large, splits by paragraphs
3. Maintains overlap for context continuity
4. Preserves markdown formatting

### Deduplication
- Uses MD5 hash of content
- Checks existing memories before creating new ones
- Tracks processed hashes in memory

### Storage
- Uses existing Memory model from ai_partner app
- Stored with user_id=2 (testuser)
- Conversation ID format: `markdown_ingestion_{category}`
- Rich metadata includes source file, section, tokens

## File Structure

```
backend/
├── scripts/
│   ├── markdown_ingestion.py      # Main ingestion script
│   └── test_markdown_ingestion.py # Test script
├── ai_partner/
│   ├── management/
│   │   └── commands/
│   │       └── ingest_markdown.py # Django management command
│   └── code_assistant_service.py  # Enhanced with markdown search
└── MARKDOWN_INGESTION_GUIDE.md    # This file
```

## Expected Output

### Console Output
```
📚 Cataloging markdown files...
Found 47 markdown files
Total tokens: 2,845,923

📂 Processing investigation files...
investigation files: 100%|████████| 12/12 [00:45<00:00,  3.75s/file]

📂 Processing chat_logs files...
chat_logs files: 100%|████████| 8/8 [00:32<00:00,  4.00s/file]

✅ Ingestion complete! Created 1,247 memory entries
Report saved to: markdown_ingestion_report.json
```

### Report File
The system generates `markdown_ingestion_report.json` with:
- Total files processed
- Token counts by category
- Largest files list
- Processing duration
- Memory creation statistics

## Integration with Code Assistant

The Code Assistant now automatically searches markdown memories when answering questions about the codebase. Results appear as "Related Documentation" in responses.

### Search Features
- Searches content and section titles
- Returns up to 3 most relevant files
- Shows filename, category, and section
- Prioritizes exact matches

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the backend directory
   - Activate virtual environment first

2. **Permission Errors**
   - Check file read permissions
   - Some system files may be inaccessible

3. **Memory Errors**
   - Large files are processed in chunks
   - Progress bars show current status

4. **Duplicate Detection**
   - System tracks content hashes
   - Run multiple times safely

### Skipped Directories
The following are automatically skipped:
- `/node_modules/`
- `/venv/`
- `/.git/`
- `/__pycache__/`
- `/.pytest_cache/`
- `/migrations/`

## Benefits

1. **Persistent Knowledge**: Documentation becomes permanent AI memory
2. **Context Preservation**: Future AI sessions can access all project history
3. **Searchable Archive**: Quick retrieval of relevant documentation
4. **Reality Engine Insights**: All investigation notes become accessible
5. **No Token Limits**: Millions of tokens available through search

## Future Enhancements

- Vector embeddings for semantic search
- Automatic re-ingestion on file changes
- Web UI for browsing ingested content
- Export to other formats
- Integration with more AI features