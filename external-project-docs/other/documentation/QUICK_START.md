# Documentation Intelligence System - Quick Start Guide

Transform your 13,244+ markdown files into a searchable, AI-powered knowledge base in under 2 hours.

## 🎯 What This Does

1. **Scans** all markdown files and creates comprehensive inventory
2. **Deduplicates** to remove 20-30% redundant content
3. **Generates embeddings** using OpenAI (cost: ~$1-2)
4. **Uploads to database** with pgvector for semantic search
5. **Enables AI-powered Q&A** across all your documentation

## 📋 Prerequisites

### 1. Install Dependencies
```bash
cd /Users/donkeyking/development/documentation-intelligence-system
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
# Required for embedding generation and search
export OPENAI_API_KEY="your-openai-key-here"

# Database connection (choose your platform)
# For AI Content Studio:
export DB_NAME="ai_content_studio"
export DB_USER="postgres"
export DB_PASSWORD="your-password"
export DB_HOST="localhost"
export DB_PORT="5432"

# Or for DBAO Studio:
# export DB_NAME="dbao_studio"
# (same other vars)
```

### 3. Ensure PostgreSQL + pgvector is Running
```bash
# Check PostgreSQL is running
psql -h localhost -U postgres -l

# Ensure pgvector extension is available
psql -h localhost -U postgres -d your_database -c "CREATE EXTENSION IF NOT EXISTS vector"
```

## 🚀 Step-by-Step Execution

### Step 1: Scan All Documentation (5-10 minutes)
```bash
python 1_scan_documentation.py
```

**What it does:**
- Scans all 13,244+ markdown files
- Detects duplicates by hash
- Categorizes by project, category, status
- Generates comprehensive inventory

**Output:**
- `scan-results/inventory.json` - Full file inventory
- `scan-results/duplicates.json` - Duplicate detection
- `scan-results/SCAN_REPORT.md` - Human-readable report

**Expected Results:**
```
📊 Results:
   • Total Files: 13,244
   • Total Size: 450.00 MB
   • Duplicate Groups: 150-200
   • Potential Savings: 50-100 MB
```

### Step 2: Deduplicate Files (2-5 minutes)
```bash
python 2_deduplicate_docs.py
```

**What it does:**
- Identifies exact duplicates (100% match)
- Finds near-duplicates (85%+ similarity)
- Creates deduplication plan
- **DRY RUN by default** - no files moved

**Output:**
- `dedup-results/deduplication_plan.json` - Action plan
- `dedup-results/DEDUPLICATION_REPORT.md` - Review report

**Review the report, then execute (optional):**
```python
# Edit 2_deduplicate_docs.py line ~150:
# Change: execute_deduplication(plan, dry_run=True)
# To:     execute_deduplication(plan, dry_run=False)
```

### Step 3: Generate Embeddings (30-60 minutes)
```bash
python 3_generate_embeddings.py
```

**What it does:**
- Chunks large documents (1000 tokens each)
- Generates OpenAI embeddings in batches
- Processes only "active" status documents
- Saves embeddings for upload

**Cost Estimation:**
```
💰 Cost Estimation:
   • Total chunks: ~8,000-10,000
   • Estimated tokens: 4-5 million
   • Estimated cost: $0.80-$1.00
```

**Confirmation required** - Script will ask before proceeding.

**Output:**
- `embeddings/embeddings.json` - All embeddings
- `embeddings/embeddings_summary.json` - Statistics

### Step 4: Upload to Database (5-10 minutes)
```bash
python 4_upload_to_database.py
```

**What it does:**
- Creates `documentation_index` table
- Uploads embeddings and metadata
- Creates HNSW vector index for fast search
- Creates full-text search index
- Adds helper search functions

**Choose platform:**
```
1. AI Content Studio (port 8001)
2. DBAO Studio (port 8000)
3. Custom database
```

**Output:**
- Database table with all documentation
- Vector and full-text indexes
- Search functions: `semantic_search()`, `keyword_search()`
- `search/SEARCH_USAGE_GUIDE.md` - API examples

### Step 5: Search Your Documentation! (Instant)
```bash
# Interactive mode
python 5_search_docs.py

# Command-line search
python 5_search_docs.py "how to configure memory system"
```

**Interactive Commands:**
```
Search> /semantic how do I use embeddings
Search> /keyword memory system configuration
Search> /ask What is the difference between AI Content Studio and DBAO?
Search> /project ai-content-studio
Search> /quit
```

## 📊 Expected Timeline

| Phase | Time | Cost | Output |
|-------|------|------|--------|
| **1. Scan** | 5-10 min | Free | Inventory & duplicates |
| **2. Deduplicate** | 2-5 min | Free | Dedup plan |
| **3. Generate Embeddings** | 30-60 min | $0.80-$1.00 | Embeddings file |
| **4. Upload** | 5-10 min | Free | Searchable database |
| **5. Search** | Instant | $0.001/query | AI-powered answers |
| **Total** | **45-90 min** | **~$1** | **Full system** |

## 🎉 What You Get

### 1. Semantic Search
Find documentation by **meaning**, not just keywords:
```python
results = semantic_search("How do I optimize performance?")
# Finds: "Performance tuning", "Speed optimization", "Efficiency tips"
```

### 2. Keyword Search
Traditional full-text search:
```python
results = keyword_search("Redis & cache & configuration")
# Finds: Documents mentioning Redis cache configuration
```

### 3. AI-Powered Q&A
Ask questions in natural language:
```python
answer = ask_question("What's the difference between the two platforms?")
# Returns: "AI Content Studio focuses on content generation with..."
```

### 4. Filtered Search
Search within specific projects or categories:
```python
results = semantic_search("agent orchestration", project="dbao-studio")
# Only searches DBAO documentation
```

## 🔧 Troubleshooting

### Issue: psycopg2 install fails
```bash
# Use binary version
pip install psycopg2-binary
```

### Issue: pgvector not found
```bash
# Install pgvector
pip install pgvector

# Or install PostgreSQL pgvector extension:
# https://github.com/pgvector/pgvector#installation
```

### Issue: OpenAI rate limit
```python
# Edit batch_size in 3_generate_embeddings.py
# Line ~60: Change batch_size=20 to batch_size=10
# Add longer sleep: time.sleep(1.0)
```

### Issue: Database connection failed
```bash
# Verify PostgreSQL is running
pg_isready

# Check credentials
psql -h localhost -U postgres -d your_database

# Update environment variables
export DB_NAME="correct_database_name"
export DB_PASSWORD="correct_password"
```

## 📈 Success Metrics

After completion, you should have:

✅ **Scanned**: 13,244 files → ~8,500 active documents
✅ **Deduplicated**: 20-30% storage savings
✅ **Embedded**: 8,000-10,000 searchable chunks
✅ **Indexed**: Vector + full-text search ready
✅ **Search Time**: <1 second average response
✅ **AI Answers**: GPT-4 powered documentation Q&A

## 🚀 Next Steps

### 1. Create Web Interface
Build a search UI using the database:
```python
# Example Flask app
from flask import Flask, request, jsonify

@app.route('/search')
def search():
    query = request.args.get('q')
    results = semantic_search(conn, query)
    return jsonify(results)
```

### 2. Integrate with Platforms
Add search to AI Content Studio or DBAO:
```python
# In your Django views
from documentation_search import semantic_search

def search_docs_api(request):
    query = request.GET.get('q')
    results = semantic_search(query)
    return JsonResponse({'results': results})
```

### 3. Create Slack Bot
Enable team to search documentation via Slack:
```python
@slack_app.command("/search-docs")
def search_command(ack, command):
    ack()
    results = semantic_search(command['text'])
    # Post results to Slack
```

### 4. Add Auto-Update
Keep documentation fresh:
```python
# Cron job to re-scan and update
0 2 * * * cd /path/to/system && python 1_scan_documentation.py && python 3_generate_embeddings.py && python 4_upload_to_database.py
```

## 💡 Pro Tips

1. **Start with active docs only** - Archive old content first
2. **Review deduplication report** - Verify before deleting files
3. **Use project filters** - Narrow search scope for better results
4. **Chunk size matters** - Smaller chunks = more precise search
5. **Monitor costs** - OpenAI embedding costs are low (~$1) but queries add up
6. **Cache embeddings** - Store query embeddings to reduce API calls
7. **Version control** - Keep backup before deduplication

## 📚 Additional Resources

- **OpenAI Embeddings Guide**: https://platform.openai.com/docs/guides/embeddings
- **pgvector Documentation**: https://github.com/pgvector/pgvector
- **Vector Search Best Practices**: https://www.pinecone.io/learn/vector-search/

## 🆘 Support

If you encounter issues:

1. Check the generated reports in each phase
2. Review error messages in console output
3. Verify environment variables are set correctly
4. Ensure PostgreSQL + pgvector are properly installed
5. Check OpenAI API key has sufficient credits

---

**Ready to get started?**

```bash
# Run all phases sequentially
python 1_scan_documentation.py && \
python 2_deduplicate_docs.py && \
python 3_generate_embeddings.py && \
python 4_upload_to_database.py && \
python 5_search_docs.py
```

**That's it!** Your documentation is now a self-learning, searchable AI knowledge base. 🎉
