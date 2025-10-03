# 📚 Markdown Import Guide for UKF System

## 🎯 Overview

This guide helps you transform your "random notes" into structured, searchable knowledge within the Donkey Betz UKF system. Your system can track:
- **9 content types**: documentation, idea, solution, question, research, experiment, rant, note, project
- **Emotional context**: frustrated, excited, confused, breakthrough, stuck, neutral
- **Relationships**: idea evolution chains, parent-child relationships
- **Quality metrics**: importance, clarity, completeness scores

## 🚀 Quick Start Workflow

### Step 1: Preprocess Your Notes
Transform random notes into structured markdown:

```bash
cd backend
python scripts/preprocess_markdown_notes.py ~/my-notes --output ~/structured-notes
```

This will:
- ✅ Add metadata headers (title, summary, key points)
- ✅ Detect content type and emotional context
- ✅ Extract people, technologies, and concepts
- ✅ Organize by category folders
- ✅ Generate preprocessing report

### Step 2: Import to UKF System
Import structured notes into the database:

```bash
python scripts/batch_import_to_ukf.py ~/structured-notes --user-id 3
```

This will:
- ✅ Create MarkdownDocument records
- ✅ Extract all metadata fields
- ✅ Generate embeddings for search
- ✅ Track import batch
- ✅ Create import report

### Step 3: Verify Import
Test that your documents are searchable:

```bash
python manage.py shell -c "
from ukf_system.services.unified_memory_search import get_unified_search_service
results = get_unified_search_service().search('your search term', user_id=3)
print(f'Found {results[\"total_results\"]} results')
"
```

## 📝 Structured Markdown Format

### Ideal Structure for Maximum Searchability

```markdown
# Clear, Descriptive Title

## Executive Summary
Brief 1-2 paragraph overview that captures the essence of the content.

## Key Points
- Main takeaway or insight #1
- Critical learning or decision #2  
- Important technical detail #3
- Key relationship or connection #4
- Action item or next step #5

## [Type] Overview
Replace [Type] with: Documentation, Idea, Solution, Question, Research, Experiment, Rant, Note, or Project

### Context/Background
Detailed context about why this content exists.

### Implementation/Details
The main body of your content with all details.

### Status/Progress
Current state: Planning, In Progress, Complete, Blocked, etc.

### Next Steps/Recommendations
- [ ] Action item 1
- [ ] Follow-up task 2

## Metadata
- **Date**: July 18, 2025
- **Type**: Solution
- **Importance**: High
- **Emotional Context**: Breakthrough
- **People Mentioned**: @john, @sarah, Bob Smith
- **Technologies**: Python, Django, PostgreSQL, Redis
- **Tags**: authentication, jwt, backend, security
- **Related Projects**: donkey-betz, auth-system
```

## 🔄 Transforming Random Notes

### Example 1: Technical Note
**Before:**
```
jwt tokens failing in prod
talked to john - issue with expiry
fixed by updating SECRET_KEY rotation
need to document this somewhere
```

**After:**
```markdown
# JWT Token Expiry Fix in Production

## Executive Summary
Resolved production JWT authentication failures caused by SECRET_KEY rotation timing issues.

## Key Points
- JWT tokens were failing due to SECRET_KEY mismatch
- Coordinated with @john to identify root cause
- Implemented proper key rotation strategy
- Production authentication restored

## Solution Overview

### Problem Description
Production JWT tokens were being rejected despite valid credentials.

### Implementation
Updated SECRET_KEY rotation to maintain old key for grace period during rotation.

### Status
✅ Complete - Authentication working in production

### Next Steps
- [ ] Document key rotation process
- [ ] Set up monitoring for auth failures
- [ ] Create runbook for future rotations

## Metadata
- **Date**: July 18, 2025
- **Type**: Solution
- **Importance**: Critical
- **Emotional Context**: Breakthrough
- **People Mentioned**: @john
- **Technologies**: JWT, Django, Python
- **Tags**: authentication, production, fix, security
```

### Example 2: Idea/Thought Note
**Before:**
```
what if we used embeddings for all user content?
could search across everything
probably expensive but worth testing
```

**After:**
```markdown
# Universal Embeddings for User Content Search

## Executive Summary
Proposal to implement vector embeddings across all user-generated content for unified semantic search capabilities.

## Key Points
- Enable semantic search across all content types
- Use pgvector for efficient similarity search
- Potential high compute cost but significant UX improvement
- Could unify disparate search systems

## Idea Overview

### Concept
Implement universal vector embeddings for all user content to enable semantic search.

### Implementation Considerations
- Compute costs for embedding generation
- Storage requirements for vectors
- Real-time vs batch processing
- Integration with existing search

### Status
💡 Idea - Needs feasibility study

### Next Steps
- [ ] Research embedding model options
- [ ] Calculate cost estimates
- [ ] Prototype with subset of data
- [ ] Benchmark search performance

## Metadata
- **Date**: July 18, 2025
- **Type**: Idea
- **Importance**: High
- **Emotional Context**: Excited
- **Technologies**: embeddings, pgvector, search, ML
- **Tags**: idea, search, machine-learning, architecture
```

## 🛠️ Advanced Features

### 1. Relationship Tracking
Link related documents by adding to metadata:
```markdown
- **Parent Document**: /path/to/parent.md
- **Related Ideas**: idea-123, idea-456
- **Implements**: solution-789
```

### 2. Custom Categories
The preprocessor auto-detects, but you can override:
- Place in specific folders: `ideas/`, `solutions/`, `research/`
- Add category to metadata: `- **Category**: investigation`

### 3. Quality Scoring
The system calculates quality based on:
- **Completeness**: Has summary, key points, metadata
- **Clarity**: Well-structured with clear sections
- **Importance**: Marked as critical/high + has action items

### 4. Batch Operations

#### Test Import (First 10 Files)
```bash
python scripts/preprocess_markdown_notes.py ~/notes --output ~/test-notes
find ~/test-notes -name "*.md" | head -10 | xargs -I {} cp {} ~/test-import/
python scripts/batch_import_to_ukf.py ~/test-import --user-id 3
```

#### Import Without Embeddings (Faster)
```bash
python scripts/batch_import_to_ukf.py ~/structured-notes --no-embeddings
# Generate embeddings later:
python manage.py generate_embeddings --model-type ukf
```

#### Category-Specific Import
```bash
# Import only solutions
python scripts/batch_import_to_ukf.py ~/structured-notes/solution --user-id 3
```

## 📊 Monitoring Import Progress

### Check Import Status
```bash
python manage.py shell -c "
from ukf_system.models import ImportBatch, MarkdownDocument
latest = ImportBatch.objects.latest('created_at')
print(f'Batch {latest.id}: {latest.successful_items}/{latest.total_items} imported')
print(f'Total documents: {MarkdownDocument.objects.count()}')
"
```

### View Recent Imports
```bash
python manage.py shell -c "
from ukf_system.models import MarkdownDocument
recent = MarkdownDocument.objects.order_by('-imported_date')[:10]
for doc in recent:
    print(f'{doc.title[:50]} - {doc.primary_type} - {doc.importance}')
"
```

## 🔍 Using Your Imported Knowledge

### 1. Unified Search (Web UI)
Navigate to: http://localhost:5173/memory-palace/unified-search
- Search across all documents and conversations
- Filter by type, date, importance
- View document relationships

### 2. API Search
```python
from ukf_system.services.unified_memory_search import get_unified_search_service

search_service = get_unified_search_service()
results = search_service.search(
    query="jwt authentication",
    user_id=3,
    include_documents=True,
    include_conversations=True,
    limit=20
)

for result in results['results']:
    print(f"{result['title']} - {result['relevance_score']}")
```

### 3. Agent Integration
Your AI agents can now access this knowledge:
```python
from agent_orchestra.conductor import AgentConductor

conductor = AgentConductor(user_id=3)
response = await conductor.process_request(
    "What do we know about JWT authentication issues?",
    agent_slug="general-assistant"
)
```

## ⚡ Performance Tips

1. **Batch Processing**: Import 100-500 files at a time
2. **Preprocessing**: Clean up files before import (remove duplicates)
3. **Embeddings**: Generate during off-peak hours
4. **Categories**: Organize by type for faster filtered searches
5. **Deduplication**: System auto-detects duplicates by content hash

## 🎯 Next Steps After Import

1. **Test Search**: Verify documents are findable
2. **Review Categories**: Check auto-categorization accuracy
3. **Link Related Docs**: Add parent/child relationships
4. **Generate Reports**: Use analytics endpoints
5. **Train Agents**: Update agent prompts to use new knowledge

## 🆘 Troubleshooting

### Import Fails
- Check file encoding (UTF-8 required)
- Verify user permissions (`user_id=3` for testuser)
- Look for special characters in filenames

### Search Not Finding Documents
- Ensure embeddings were generated
- Check `processing_status='completed'`
- Verify search service cache is cleared

### Duplicate Documents
- System prevents duplicates by content hash
- Check preprocessing report for skipped files
- Use `--force` flag to reimport

## 📈 Success Metrics

After successful import, you should see:
- ✅ Documents searchable in unified search
- ✅ Metadata properly extracted and displayed
- ✅ Categories logically organized
- ✅ Embeddings generated (for semantic search)
- ✅ Import batch tracked with statistics
- ✅ AI agents can access the knowledge

---

Your random notes are about to become a powerful, searchable knowledge base! 🚀