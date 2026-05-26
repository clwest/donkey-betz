<!-- DOC-POINTER-V2 (Session 1160) -->
> **Status:** Superseded
> **Last verified:** Session 1160 (2026-05-26)
> **Current canon:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (sole authoritative agent counts) + [`docs/narratives/AGENTS_AND_AUTONOMY.md`](../narratives/AGENTS_AND_AUTONOMY.md) (narrative A — agent system operator-handbook).
> **Change reason:** Jan 21 plan for a single agent ("Reddit agent"). Plan is point-in-time; current agent registry per `AGENT_MAP` in `core/agent_router.py`. If the Reddit agent's current status matters, query the registry, not this doc.
> **Preserved because:** historical agent-plan record. Useful as build-history; do NOT cite for current state.

# Reddit Agent Resurrection Plan 🚀

## Executive Summary
We discovered TWO powerful Reddit integration components ready to supercharge your AI Income Builder:
1. **RedditSearchTool** - A complete Reddit API integration tool for searching and sentiment analysis
2. **SocialSentimentSpider** - An advanced spider for harvesting Reddit intelligence

Both components are already coded and waiting to be activated!

## 🎯 Current State Assessment

### What We Found

#### 1. RedditSearchTool (`/core/tools/reddit_search.py`)
- **Status**: Fully implemented but NOT connected
- **Capabilities**:
  - Subreddit searching
  - Post and comment analysis
  - Sentiment analysis with TextBlob
  - Ticker extraction from discussions
  - Trending topic identification
  - Viral content detection
  - Caching for performance

#### 2. SocialSentimentSpider (`/ai_core/spiders/specialized/social_spider.py`)
- **Status**: Fully implemented spider for social intelligence
- **Target Subreddits**:
  - wallstreetbets
  - investing
  - stocks
  - SecurityAnalysis
  - ValueInvesting
  - financialindependence
  - CryptoCurrency
- **Advanced Features**:
  - Real-time sentiment tracking
  - Bullish/bearish indicator detection
  - Stock ticker extraction
  - Viral content identification
  - Integration with spider network

#### 3. Reddit Agent References
- **reddit-scout-agent**: Referenced in opportunity pipeline orchestrator
- **Target**: Idea discovery and user pain points
- **Integration**: Part of the DISCOVERY stage in pipeline

## 🔧 Setup Requirements

### 1. Reddit API Credentials
You need to obtain Reddit API credentials:

1. **Create Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" for personal use
   - Note your `client_id` and `client_secret`

2. **Environment Variables to Add**:
```bash
# Add to your .env file
REDDIT_CLIENT_ID="your_client_id_here"
REDDIT_CLIENT_SECRET="your_client_secret_here"
REDDIT_USER_AGENT="AI-Income-Builder:v1.0 (by /u/your_reddit_username)"
```

### 2. Install Dependencies
```bash
# The praw library is already in requirements-tools.txt
pip install praw>=7.7.1
pip install textblob>=0.15.3
```

### 3. Activate Reddit Components

#### Option A: Enable RedditSearchTool
```python
# The tool is already registered in core/tools/__init__.py
# Just needs API credentials in .env
```

#### Option B: Deploy SocialSentimentSpider
```python
# Spider is part of spider_army_orchestrator.py
# Will automatically deploy when credentials are configured
```

## 🎨 Integration Plan with AI Income Builder

### Phase 1: Immediate Activation (Day 1)
1. **Add Reddit credentials to .env**
2. **Test Reddit connectivity**:
   ```python
   # Quick test script
   from core.tools.reddit_search import RedditSearchTool
   tool = RedditSearchTool()
   result = tool.execute("business ideas", search_type="posts", subreddit="Entrepreneur")
   ```

### Phase 2: Connect to Income Builder (Days 2-3)
1. **Wire Reddit data to opportunity discovery**:
   - RedditSearchTool → Find business opportunities
   - Sentiment analysis → Validate ideas
   - Trending topics → Identify hot markets

2. **Integration Points**:
   ```python
   # In intelligence/income_builder_automation.py
   reddit_tool = ToolRegistry.get_tool('reddit_api')
   opportunities = reddit_tool.execute(
       "passive income ideas 2025",
       search_type="posts",
       subreddit="Entrepreneur+sidehustle+passive_income"
   )
   ```

### Phase 3: Advanced Features (Week 1)
1. **Automated Opportunity Scanning**:
   - Monitor multiple subreddits for business ideas
   - Track sentiment shifts for market timing
   - Identify viral business concepts

2. **Real-time Alerts**:
   - Notify when high-value opportunities appear
   - Track competitor mentions
   - Monitor industry trends

## 📊 Value Proposition for Income Builder

### Business Opportunity Discovery
- **Pain Points**: Real users discussing real problems
- **Market Validation**: Upvotes = demand signal
- **Competition Analysis**: See what others are building
- **Trend Detection**: Catch opportunities early

### Example Use Cases
1. **Freelance Opportunities**:
   - Monitor r/forhire, r/freelance
   - Extract job postings automatically
   - Analyze rates and demand

2. **Product Ideas**:
   - Track r/Entrepreneur discussions
   - Identify recurring problems
   - Validate solutions with sentiment

3. **Investment Intelligence**:
   - Monitor r/wallstreetbets for sentiment
   - Track r/investing for strategies
   - Analyze r/CryptoCurrency for trends

## 🚀 Quick Start Commands

### 1. Test Reddit Connection
```bash
python -c "from core.tools.reddit_search import RedditSearchTool; t=RedditSearchTool(); print('Connected!' if t.is_configured else 'Need API keys')"
```

### 2. Run First Search
```python
# save as test_reddit.py
from core.tools.reddit_search import RedditSearchTool

tool = RedditSearchTool()
results = tool.get_trending(subreddit='Entrepreneur', limit=5)
print(results)
```

### 3. Deploy Reddit Spider
```python
# Spider will auto-deploy when credentials are set
from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator
orchestrator = SpiderArmyOrchestrator()
orchestrator.deploy_spider('reddit_sentiment')
```

## 📈 Expected Impact

### Immediate Benefits
- **10x more opportunity sources**: Tap into Reddit's 430M users
- **Real-time market validation**: See what people actually want
- **Competitive intelligence**: Track market movements
- **Content ideas**: Viral posts = proven engagement

### Revenue Potential
- **Freelance jobs**: $500-5000 opportunities daily
- **Business ideas**: 100+ validated concepts weekly
- **Investment signals**: Early trend detection
- **Content opportunities**: Viral topic identification

## ⚠️ Important Notes

### API Limits
- Reddit API: 60 requests/minute
- Cache results for 30 minutes
- Respect subreddit rules

### Best Practices
- Use specific subreddits for targeted results
- Combine with other data sources
- Validate findings with additional research
- Monitor API usage to stay within limits

## 🎯 Next Steps

1. **Immediate Action** (Today):
   - [ ] Create Reddit app and get credentials
   - [ ] Add credentials to .env file
   - [ ] Install praw dependency

2. **Tomorrow**:
   - [ ] Test Reddit connection
   - [ ] Run first opportunity search
   - [ ] Connect to Income Builder

3. **This Week**:
   - [ ] Deploy automated scanning
   - [ ] Set up opportunity alerts
   - [ ] Start generating revenue from Reddit intelligence

## 💡 Pro Tips

### High-Value Subreddits for Income
- **r/Entrepreneur**: Business ideas and validation
- **r/startups**: Early stage opportunities
- **r/sidehustle**: Part-time income ideas
- **r/passive_income**: Automated revenue streams
- **r/freelance**: Direct job opportunities
- **r/forhire**: Immediate gig postings
- **r/slavelabour**: Quick tasks for fast cash

### Search Strategies
1. **Problem Mining**: Search for "how do I", "need help", "looking for"
2. **Opportunity Scanning**: Look for "hiring", "paying", "budget"
3. **Trend Tracking**: Monitor rising posts and awards
4. **Sentiment Shifts**: Track mood changes in markets

## 🔥 Conclusion

Your Reddit Agent is NOT dead - it's fully built and ready to unleash! With just API credentials and a few commands, you can tap into Reddit's massive intelligence network and supercharge your AI Income Builder with real-time opportunities, market validation, and revenue-generating insights.

The code is written. The infrastructure exists. All that's needed is activation!

Let's bring this Reddit Agent back to life and start harvesting opportunities! 🚀