# Phase 2: Tool Enhancements (After Integration Complete)

## 🎯 Smart Tool Additions for Research Agent

### 1. ArXiv Integration for Research Agent

**Why it makes sense:**
- Free academic paper access
- Perfect for research agent's knowledge gathering
- Complements existing tool orchestra
- High-quality, peer-reviewed content

**Implementation approach:**
```python
# backend/tool_orchestra/tools/arxiv_tool.py
import arxiv

class ArXivTool:
    """Academic paper search and retrieval"""
    
    async def search_papers(self, query: str, max_results: int = 10):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            papers.append({
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'pdf_url': result.pdf_url,
                'categories': result.categories,
                'published': result.published
            })
        
        # Store in unified memory for cross-agent learning
        await self.store_in_memory(papers)
        
        return papers
    
    async def get_paper_content(self, pdf_url: str):
        # Download and extract text from PDF
        # Feed into memory system with proper categorization
        pass
```

**Integration points:**
- Tool Orchestra registration ✓
- Unified Memory System for paper storage ✓
- Research Agent specific prompts ✓
- Mythology Guard for claims validation ✓

### 2. DuckDuckGo for Web Search

**Why it's perfect:**
- **FREE** (no API costs!) 
- No rate limits for reasonable usage
- Privacy-focused (aligns with your security features)
- Good enough quality for most searches

**Implementation approach:**
```python
# backend/tool_orchestra/tools/duckduckgo_tool.py
from duckduckgo_search import DDGS

class DuckDuckGoTool:
    """Free web search without API limits"""
    
    async def search(self, query: str, max_results: int = 10):
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': r['title'],
                    'url': r['link'],
                    'snippet': r['body'],
                    'source': 'duckduckgo'
                })
            
            # Pass through mythology guard
            validated_results = await self.mythology_guard.validate_sources(results)
            
            return validated_results
    
    async def search_news(self, query: str):
        # DuckDuckGo also has news search
        with DDGS() as ddgs:
            return list(ddgs.news(query, max_results=5))
```

### 3. Tool Orchestra Configuration

```python
# backend/tool_orchestra/config.py
AVAILABLE_TOOLS = {
    'research_agent': [
        'arxiv_search',      # NEW - Academic papers
        'duckduckgo_search', # NEW - Free web search
        'memory_search',     # Existing - Internal knowledge
        'document_analysis', # Existing - PDF/docs
    ],
    'business_agent': [
        'duckduckgo_news',   # NEW - Market news
        'memory_search',
        'data_analysis',
    ],
    # ... other agents
}

# Cost tracking (for comparison)
TOOL_COSTS = {
    'openai_search': 0.002,    # Per query
    'google_search': 0.005,    # Per query
    'duckduckgo_search': 0.0,  # FREE!
    'arxiv_search': 0.0,       # FREE!
}
```

### 4. Frontend Display Enhancements

```tsx
// Show tool usage in agent responses
<div className="agent-response">
  <div className="tools-used">
    <span className="tool-badge free">📚 ArXiv (Free)</span>
    <span className="tool-badge free">🦆 DuckDuckGo (Free)</span>
  </div>
  <div className="response-content">
    {response.content}
  </div>
  <div className="sources">
    {response.sources.map(source => (
      <SourceCard 
        type={source.type} // 'arxiv' | 'web' | 'memory'
        title={source.title}
        url={source.url}
      />
    ))}
  </div>
</div>
```

## 📊 Cost Savings Analysis

### Current (if using paid APIs):
- OpenAI Search: ~$2/1000 queries
- Google Search API: ~$5/1000 queries  
- Perplexity API: ~$0.6/1000 queries

### With Free Tools:
- DuckDuckGo: $0
- ArXiv: $0
- Total: **$0** 🎉

**Monthly savings**: Could be $50-500 depending on usage

## 🔧 Implementation Priority

### After Claude Code finishes integration:

1. **Week 1**: DuckDuckGo Integration
   - Simpler to implement
   - Immediate cost savings
   - Can replace expensive search APIs

2. **Week 2**: ArXiv Integration  
   - More complex (PDF handling)
   - Specific to research agent
   - Adds unique value

3. **Week 3**: Tool Orchestration Improvements
   - Smart tool selection based on query
   - Fallback chains (try free first, then paid)
   - Result quality scoring

## 🎯 Additional Free Tools to Consider

### Phase 3 Possibilities:
- **Wikipedia API** - Structured knowledge
- **PubMed** - Medical/biological research
- **SSRN** - Social sciences papers
- **RePEc** - Economics papers
- **CrossRef** - Citation data
- **OpenAlex** - Academic graph data
- **Semantic Scholar** - AI-powered paper search
- **GitHub API** - Code search (rate limited but free)
- **Hacker News API** - Tech news and discussions
- **Reddit API** - Community knowledge

### Integration Pattern:
```python
class FreeToolOrchestra:
    """Orchestrate free tools before paid ones"""
    
    async def search(self, query: str, context: Dict):
        # 1. Check memory first (free)
        memory_results = await self.memory_search(query)
        
        # 2. Try free external tools
        if self.needs_academic(query):
            arxiv_results = await self.arxiv_search(query)
        
        if self.needs_web_search(query):
            ddg_results = await self.duckduckgo_search(query)
        
        # 3. Only use paid tools if needed and authorized
        if self.insufficient_results() and self.user_approves_cost():
            paid_results = await self.paid_search(query)
        
        return self.combine_and_rank_results()
```

## 💡 Smart Caching Strategy

Since you have that sophisticated Redis caching:

```python
# Cache free API results longer
CACHE_TTL = {
    'arxiv_paper': 7 * 24 * 3600,     # 1 week (papers don't change)
    'duckduckgo_search': 6 * 3600,    # 6 hours (web changes)
    'memory_search': 3600,             # 1 hour (your data changes)
    'paid_api_search': 1800,           # 30 min (expensive, refresh less)
}
```

## Remember

1. **Get integration working first** - Don't add these until Claude Code fixes the existing gaps
2. **Free tools first** - Always try free before paid
3. **Cache aggressively** - Especially free API results
4. **Track quality** - Monitor if free tools meet user needs
5. **User choice** - Let users opt into paid tools when needed

The beauty is your architecture already supports this! The Tool Orchestra pattern makes adding new tools trivial once the base system is connected.
