# ⚡ Quick Reference Guide - Document Analysis Tools

## 🎯 Common Tasks

### Analyze Your Project Documentation
```bash
# Quick analysis (no AI)
python documentation_analyzer.py ~/your-project/docs

# With AI insights (requires OpenAI key)
python documentation_analyzer.py ~/your-project/docs --use-ai

# Custom file pattern
python documentation_analyzer.py ~/your-project --pattern "*.md"
```

### Prepare Documentation for AI (GPT-5/Claude)
```bash
# Create chunks for large projects
python context_builder.py ~/your-project/docs --chunks

# Different strategies
python context_builder.py ~/docs --strategy recent_focus  # Focus on recent
python context_builder.py ~/docs --strategy feature_focus # Focus on features
python context_builder.py ~/docs --strategy balanced      # Default, balanced
```

### Combine Chunks for Easy Upload
```bash
# Create single master file
python combine_chunks.py donkey_betz_chunks

# Also create split versions
python combine_chunks.py donkey_betz_chunks --split
```

### Upload to AI Content Studio
```bash
# Upload directory to Personal Knowledge
python upload_to_studio.py ~/project/docs --collection "Project Name"

# With custom batch size
python upload_to_studio.py ~/docs --batch-size 20

# Without batch mode (one by one)
python upload_to_studio.py ~/docs --no-batch
```

### Test Everything is Working
```bash
# Quick test (30 seconds)
python test_knowledge_system.py quick

# Full test suite
python test_knowledge_system.py

# Check embeddings
python check_embeddings.py quick

# Full embedding check
python check_embeddings.py
```

### Trigger Indexing/Embeddings
```bash
# Trigger indexing for first 20 docs
python trigger_indexing.py

# Create embeddings (needs OpenAI key in .env)
python create_embeddings.py --quick  # First 10 docs
python create_embeddings.py --all    # All documents
```

## 📁 Output Files

### After Analysis
```
donkey_betz_analysis/
├── overview_YYYYMMDD.md          # Human-readable summary
├── detailed_report_YYYYMMDD.json # Detailed analysis
└── features_timeline_YYYYMMDD.json # Feature timeline
```

### After Context Building
```
donkey_betz_chunks/
├── context_chunk_001.md ... XXX.md # Individual chunks
└── document_index.json              # Document index

master_context_all.md                # Complete context file
master_parts/
└── master_context_part_01-05.md    # Split versions
```

## 🔍 Quick Checks

### Check Upload Status
```bash
curl -s http://localhost:8001/api/personal-knowledge/list/ \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
  | python -m json.tool | grep total_entries
```

### Test Search
```bash
curl -X POST http://localhost:8001/api/personal-knowledge/search/ \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
  -H "Content-Type: application/json" \
  -d '{"query": "Django"}'
```

### Get AI Context
```bash
curl "http://localhost:8001/api/personal-knowledge/context/?prompt=test&limit=5" \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>"
```

## 🚀 Start-to-Finish Example

```bash
# 1. Analyze your documentation
python documentation_analyzer.py ~/my-project/docs

# 2. Build context for AI
python context_builder.py ~/my-project/docs --chunks

# 3. Combine chunks
python combine_chunks.py donkey_betz_chunks

# 4. Upload to AI Content Studio
python upload_to_studio.py ~/my-project/docs --collection "My Project"

# 5. Test everything
python test_knowledge_system.py quick

# 6. Trigger indexing if needed
python trigger_indexing.py
```

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "No module named 'tiktoken'" | `pip install tiktoken rich` |
| "OpenAI API key not found" | Add to `.env`: `OPENAI_API_KEY=your-key` |
| Search returns 0 results | Run `python trigger_indexing.py` |
| 405 Method Not Allowed | Restart server: `make dev` |
| SQLite limitations | Upgrade to PostgreSQL for vector search |

## 🔑 Important Values

- **API Token**: `<redacted-993f8273-2026-04-20>`
- **Backend URL**: `http://localhost:8001`
- **Frontend URL**: `http://localhost:8080`
- **Personal Knowledge**: `http://localhost:8080/personal-knowledge`

## 📝 Help Commands

All tools support `--help`:
```bash
python documentation_analyzer.py --help
python context_builder.py --help
python upload_to_studio.py --help
# etc...
```

## 🎉 Success Indicators

- ✅ `test_knowledge_system.py` shows "ALL TESTS PASSED"
- ✅ Personal Knowledge page shows your documents
- ✅ Search returns results (after indexing)
- ✅ Content generation uses your uploaded docs

---

**Quick Test**: After setup, generate a blog post about your project - if it references your documentation, everything is working! 🚀