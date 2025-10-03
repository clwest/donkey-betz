# 📚 Document Analysis & AI Context Builder Guide

## Overview
Two powerful tools to process hundreds of development session documents and generate comprehensive insights or prepare them for AI consumption.

## 🔧 Tools

### 1. Documentation Analyzer (`documentation_analyzer.py`)
Analyzes your project documentation to extract patterns, features, timeline, and generate comprehensive overviews.

**Features:**
- Loads and analyzes hundreds of documents
- Extracts features, tech stack, issues, and patterns
- Generates timeline of development
- Optional AI-powered deep analysis
- Creates comprehensive overview and detailed reports

**Usage:**
```bash
# Basic analysis (no AI)
python documentation_analyzer.py /path/to/your/docs

# With AI analysis (requires OpenAI API key)
python documentation_analyzer.py /path/to/your/docs --use-ai

# Custom file pattern
python documentation_analyzer.py /path/to/your/docs --pattern "session*.md"

# Specify output directory
python documentation_analyzer.py /path/to/your/docs --output my_analysis
```

**Output Files:**
- `overview_YYYYMMDD.md` - Human-readable project overview
- `detailed_report_YYYYMMDD.json` - Detailed analysis data
- `features_timeline_YYYYMMDD.json` - Feature development timeline

### 2. Context Builder (`context_builder.py`)
Intelligently prepares documentation for feeding into AI systems like GPT-5 or Claude.

**Features:**
- Smart categorization (overview, recent, features, API, etc.)
- Priority-based document selection
- Multiple strategies (balanced, recent_focus, feature_focus)
- Token-aware context building
- Chunking for very large codebases

**Usage:**
```bash
# Build balanced context (default)
python context_builder.py /path/to/your/docs

# Focus on recent changes
python context_builder.py /path/to/your/docs --strategy recent_focus

# Create chunks for large codebases
python context_builder.py /path/to/your/docs --chunks --chunk-size 50000

# Set maximum token limit
python context_builder.py /path/to/your/docs --max-tokens 150000

# Custom output
python context_builder.py /path/to/your/docs --output my_context.md
```

**Strategies:**
- `balanced` - Mix of all document types
- `recent_focus` - Emphasize recent changes
- `feature_focus` - Emphasize features and capabilities  
- `complete` - Try to include everything

**Output Files:**
- `ai_context.md` - Optimized context for AI
- `context_chunk_XXX.md` - Multiple chunks (if using --chunks)
- `document_index.json` - Index of all documents

## 📊 Example Workflow

### For Your 400+ Documents

1. **First, analyze the documentation:**
```bash
python documentation_analyzer.py ~/your-project/docs --use-ai
```
This generates an overview of what you've built over 18 months.

2. **Then, build context for AI:**
```bash
# For feeding into GPT-5/Claude in one go
python context_builder.py ~/your-project/docs --strategy balanced --max-tokens 100000

# OR for very large codebases, create chunks
python context_builder.py ~/your-project/docs --chunks --chunk-size 50000 --output context_chunks/
```

3. **Feed to AI Assistant:**
- Copy the content from `ai_context.md` 
- Or feed chunks sequentially from `context_chunks/`
- The AI will have comprehensive understanding of your project

## 🎯 Best Practices

### For Documentation Analysis:
1. Run without AI first to get quick overview
2. Use AI analysis on sample (it analyzes first 20 docs) to save costs
3. Review the generated timeline to understand project evolution
4. Check the tech stack detection for accuracy

### For Context Building:
1. Use `balanced` strategy for general understanding
2. Use `recent_focus` when asking about recent changes
3. Use `feature_focus` when asking about capabilities
4. Use chunks if total documentation exceeds 100k tokens
5. Always review the document index to understand what was included

## 💡 Tips

1. **Token Limits:**
   - GPT-4: ~8k tokens
   - GPT-4-32k: ~32k tokens
   - GPT-5: ~100k+ tokens (adjust --max-tokens accordingly)
   - Claude: ~100k tokens

2. **File Patterns:**
   - Use `--pattern "2024*.md"` for year-specific docs
   - Use `--pattern "*session*.md"` for session notes only
   - Use `--pattern "*.md"` for all markdown files

3. **Large Codebases:**
   - If you have 400+ docs, definitely use chunking
   - Each chunk can be fed separately to maintain context
   - The index file helps track what's in each chunk

## 🔍 Understanding the Output

### Overview Document Includes:
- Development timeline with start/end dates
- Technology stack frequency analysis
- Feature development chronology
- Document statistics
- AI-generated insights (if enabled)

### Context Document Includes:
- Prioritized documentation
- Category-based organization
- Token count tracking
- Smart summarization for large docs
- Metadata headers

## 🚀 Quick Start for Your 400 Documents

```bash
# 1. Install requirements (if needed)
pip install openai tiktoken rich python-dotenv

# 2. Set your OpenAI API key (for AI analysis)
export OPENAI_API_KEY='your-key-here'

# 3. Run analysis
python documentation_analyzer.py ~/your-18-month-project/docs --use-ai

# 4. Build AI context
python context_builder.py ~/your-18-month-project/docs --chunks --output ai_chunks/

# 5. Review the generated overview
cat analysis_output/overview_*.md

# 6. Feed chunks to GPT-5 or Claude as needed
# Each chunk in ai_chunks/ can be copied into the AI
```

## 📈 Expected Results

For 400+ documents, expect:
- **Analysis Time**: 2-5 minutes (longer with AI)
- **Overview Size**: 5-10 pages
- **Context Chunks**: 8-10 files of ~50k tokens each
- **Insights**: Tech evolution, feature timeline, development patterns

This system will transform your 18 months of documentation into actionable insights and AI-ready context!