# Requirements for Free Tool Integration

## Python Packages Needed

Add to `backend/requirements.txt`:

```txt
# Free Search Tools
duckduckgo-search==6.3.5    # DuckDuckGo search (FREE!)
arxiv==2.1.3                 # ArXiv paper search (FREE!)

# Optional free tools for Phase 3
wikipedia-api==0.7.1         # Wikipedia access
praw==7.7.1                  # Reddit API
beautifulsoup4==4.12.3       # Web scraping fallback
newspaper3k==0.2.8           # Article extraction
```

## Installation

```bash
cd backend
pip install duckduckgo-search arxiv

# Or for all at once
pip install -r requirements.txt
```

## Quick Test Scripts

### Test DuckDuckGo
```python
# backend/test_duckduckgo.py
from duckduckgo_search import DDGS

def test_search():
    with DDGS() as ddgs:
        results = list(ddgs.text("Donkey Betz AI platform", max_results=5))
        for r in results:
            print(f"- {r['title']}")
            print(f"  {r['body'][:100]}...")
            print(f"  URL: {r['link']}\n")

if __name__ == "__main__":
    test_search()
```

### Test ArXiv
```python
# backend/test_arxiv.py
import arxiv

def test_arxiv():
    search = arxiv.Search(
        query="transformer attention mechanism",
        max_results=3,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    for result in search.results():
        print(f"Title: {result.title}")
        print(f"Authors: {', '.join(author.name for author in result.authors)}")
        print(f"Published: {result.published}")
        print(f"PDF: {result.pdf_url}")
        print(f"Abstract: {result.summary[:200]}...\n")

if __name__ == "__main__":
    test_arxiv()
```

## No API Keys Needed! 🎉

Unlike OpenAI/Google/Perplexity, these tools work immediately:
- ✅ No registration required
- ✅ No API keys to manage  
- ✅ No rate limits (within reason)
- ✅ No billing surprises
- ✅ Privacy friendly

## Usage Limits (Soft Guidelines)

### DuckDuckGo
- No official rate limit
- Be reasonable: ~1 request/second is fine
- They may throttle if abusive
- Use caching to minimize requests

### ArXiv
- No hard rate limit
- Bulk downloads: Use their bulk data service
- Be nice: Space out requests
- Cache papers locally (they don't change)

## Integration Timeline

**After Claude Code completes current work:**

Week 1: Basic Integration (2-3 days)
- Install packages
- Create tool classes
- Add to Tool Orchestra

Week 2: Memory Integration (2-3 days)  
- Store search results in Unified Memory
- Enable cross-agent learning from searches
- Add deduplication for repeated searches

Week 3: Frontend Display (2-3 days)
- Show which tools were used
- Display cost savings
- Add source attribution
