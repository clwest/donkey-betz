# 🚀 Quick Spider Deployment Guide

**Last Updated:** October 2, 2025
**Status:** 51 Active Spiders Deployed

---

## ⚡ Quick Start Commands

### Check Running Spider Processes
```bash
# Find all active spider deployment processes
ps aux | grep deploy

# Check specific deployments
ps aux | grep sports_sentiment
ps aux | grep technical_spiders
ps aux | grep content_enhancement
```

### Monitor Spider Data Collection
```bash
# Quick data count
python manage.py shell -c "from persistence.models import SpiderData; print(f'Total: {SpiderData.objects.count():,}')"

# Check collection rate (run twice, 1 minute apart)
python manage.py shell -c "from persistence.models import SpiderData; from datetime import datetime, timedelta; recent = SpiderData.objects.filter(created_at__gte=datetime.now()-timedelta(minutes=5)).count(); print(f'Last 5 min: {recent} entries ({recent/5:.1f}/min)')"

# View top data sources
python manage.py shell -c "from persistence.models import SpiderData; from django.db.models import Count; breakdown = SpiderData.objects.values('spider_name').annotate(count=Count('spider_name')).order_by('-count')[:10]; [print(f'{item[\"spider_name\"]}: {item[\"count\"]:,}') for item in breakdown]"
```

---

## 📦 Current Active Deployments

### 1. Sports Sentiment Spiders (✅ Running)
```bash
# Deployment info
Script:   scripts/deploy_sports_sentiment_spiders.py
Count:    15 spiders
Targets:  6 sports subreddits
Agents:   24 sports agents
Runtime:  60 minutes
Status:   Running (PID varies by session)

# How to deploy
python scripts/deploy_sports_sentiment_spiders.py 60

# Run in background
nohup python scripts/deploy_sports_sentiment_spiders.py 60 > logs/sports_sentiment.log 2>&1 &

# Custom runtime (90 minutes)
python scripts/deploy_sports_sentiment_spiders.py 90
```

**Targets:**
- r/sportsbook
- r/sportsbetting
- r/nfl
- r/nba
- r/baseball
- r/hockey

**Expected Output:** 500-1,000 sentiment entries

---

### 2. Technical Intelligence Spiders (⚠️ Has Bug - See Fix Below)
```bash
# Deployment info
Script:   scripts/deploy_technical_spiders.py
Count:    20 spiders (5 per platform)
Targets:  4 technical platforms
Agents:   34 technical agents
Runtime:  90 minutes
Status:   Running but can't save data (IntelligenceData bug)

# How to deploy (AFTER fixing bug)
python scripts/deploy_technical_spiders.py 90

# Run in background
nohup python scripts/deploy_technical_spiders.py 90 > logs/technical_intel.log 2>&1 &
```

**Platforms:**
- HuggingFace (ML models, datasets)
- Kaggle (competitions, datasets)
- GitHub (trending repos, topics)
- StackOverflow (jobs, questions)

**Expected Output:** 1,500-2,500 technical entries

---

### 3. Content Monetization Spiders (⚠️ Has Bug - See Fix Below)
```bash
# Deployment info
Script:   scripts/deploy_content_enhancement_spiders.py
Count:    16 spiders (4 per platform)
Targets:  4 creator platforms
Agents:   11 content agents
Runtime:  60 minutes
Status:   Running but can't save data (IntelligenceData bug)

# How to deploy (AFTER fixing bug)
python scripts/deploy_content_enhancement_spiders.py 60

# Run in background
nohup python scripts/deploy_content_enhancement_spiders.py 60 > logs/content_monetization.log 2>&1 &
```

**Platforms:**
- Substack (newsletters)
- Patreon (creator support)
- Ko-fi (creator tips)
- ProductHunt (product launches)

**Expected Output:** 800-1,500 content entries

---

## 🐛 Known Issue: IntelligenceData Parameter Bug

**Status:** 🔴 CRITICAL - Prevents data saving
**Affects:** Technical & Content spiders (36 total spiders)
**Fix Time:** 15 minutes

### Files to Fix
1. `ai_core/spiders/specialized/tech_community_spider.py`
2. `ai_core/spiders/specialized/content_monetization_spider.py`

### Fix Pattern

**Find this (WRONG):**
```python
return IntelligenceData(
    data_type="tech_intelligence",
    content={...},
    confidence=0.75,
    priority=2,
    metadata={...}
)
```

**Replace with (CORRECT):**
```python
return IntelligenceData(
    spider_id=self.spider_id,
    source_url=target.url,
    data_type="tech_intelligence",
    content={...},
    quality_score=0.75,
    timestamp=datetime.now(timezone.utc),
    metadata={..., 'priority': 2},
    target_agents=self.subscribers
)
```

### Apply Fix
```bash
# See detailed fix instructions
cat docs/00-START-SESSION-13.md | grep -A 50 "CRITICAL BUG"

# After fixing, redeploy
python scripts/deploy_technical_spiders.py 90 &
python scripts/deploy_content_enhancement_spiders.py 60 &
```

---

## 📊 Expected Impact

### Data Collection Projections
```
Sports Sentiment:      +500-1,000 entries
Technical Intelligence: +1,500-2,500 entries
Content Monetization:  +800-1,500 entries
──────────────────────────────────────
Total Expected:        +2,800-5,000 entries
```

### Reality Score Improvements (24-48 hours)
```
Sports Agents:     75% → 85%+ (🎯 Revenue generation category!)
Technical Agents:  20% → 60%+ (🚀 Major activation!)
Content Agents:    50% → 75%+ (✍️ Enhanced monetization!)
Financial Agents:  35% (needs implementation)
──────────────────────────────────────
Overall System:    65% → 78%+ (🎉 +13 points!)
```

### Agent Activation
```
Before: ~50 agents with good data
After:  ~80 agents with good data
──────────────────────────────────────
Growth: +60% more agents activated!
```

---

## 🔍 Monitoring Commands

### Real-Time Collection Rate
```bash
# Check every minute for 5 minutes
for i in {1..5}; do
  echo "Minute $i:";
  python manage.py shell -c "from persistence.models import SpiderData; print(SpiderData.objects.count())";
  sleep 60;
done
```

### Spider Data Breakdown
```python
# In Django shell
from persistence.models import SpiderData
from django.db.models import Count

# Top 10 sources
breakdown = SpiderData.objects.values('spider_name').annotate(
    count=Count('spider_name')
).order_by('-count')[:10]

for item in breakdown:
    print(f"{item['spider_name']}: {item['count']:,}")
```

### Routing Success Rate
```python
# Check how many entries have been routed to agents
from persistence.models import SpiderData

total = SpiderData.objects.count()
routed = SpiderData.objects.exclude(routed_to_agents='').count()
success_rate = (routed / total * 100) if total > 0 else 0

print(f"Total: {total:,}")
print(f"Routed: {routed:,}")
print(f"Success Rate: {success_rate:.1f}%")
```

---

## 🎯 Next Deployment: Financial Intelligence

**Priority:** 🔴 HIGH (10 financial agents at 35% reality)

### Financial Spider Platforms to Implement
```
High Value:
- CoinGecko (crypto prices, trends)
- Etherscan (blockchain data)
- OpenSea (NFT marketplace)
- SeekingAlpha (stock analysis)
- Bloomberg Terminal (financial news)
- Reuters Eikon (market data)

Expected Impact: Financial agents 35% → 65%+ reality
```

### Template for Financial Deployment
```bash
# Create similar to existing deployments
scripts/deploy_financial_spiders.py

# Will need to create:
ai_core/spiders/specialized/crypto_spider.py
ai_core/spiders/specialized/stock_spider.py

# Update registry to use concrete classes
```

---

## 🛠️ Troubleshooting

### No Data Being Collected
```bash
# Check if spiders are actually running
ps aux | grep deploy

# Check for errors in logs
tail -f logs/sports_sentiment.log
tail -f logs/technical_intel.log
tail -f logs/content_monetization.log

# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check database connectivity
python manage.py dbshell
```

### High Memory Usage
```bash
# Check memory usage
ps aux | grep deploy | awk '{print $6}'

# If too high, reduce spider count or stagger deployments
python scripts/deploy_sports_sentiment_spiders.py 60 &
sleep 300  # Wait 5 minutes
python scripts/deploy_technical_spiders.py 90 &
sleep 300
python scripts/deploy_content_enhancement_spiders.py 60 &
```

### Rate Limiting Issues
```bash
# If seeing 429 errors, increase rate_limit values
# Edit deployment scripts, increase from 2.0 to 3.0 or higher

# Example in scripts/deploy_sports_sentiment_spiders.py:
SpiderTarget("https://www.reddit.com/r/sportsbook/", rate_limit=3.0, priority=1)
```

---

## 📋 Spider Registry Status

**Total Registered:** 39 spiders
**Fully Implemented:** 17 spiders
**Placeholders:** 22 spiders

### Implemented (17)
```
✅ Financial (Yahoo Finance, Polygon)
✅ Innovation (arXiv, patents, GitHub)
✅ Social Sentiment (Reddit, Twitter, StockTwits)
✅ Market Data (Binance, Coinbase)
✅ News (Bloomberg, Reuters, CNBC)
✅ Toptal, Guru, PeoplePerHour, 99Designs
✅ FlexJobs, RemoteOK
✅ Medium, Gumroad
✅ Substack, Patreon, Ko-fi, ProductHunt
✅ HuggingFace, Kaggle, GitHub, StackOverflow
```

### Placeholders Need Implementation (22)
```
🔴 High Priority - Financial (6):
   - CoinGecko, Etherscan, OpenSea
   - SeekingAlpha, Bloomberg Terminal, Reuters Eikon

🟡 Medium Priority - Education (3):
   - Udemy, Skillshare, Teachable

🟢 Low Priority - Additional Coverage (13):
   - WeWorkRemotely, AngelList, Dribbble, Behance
   - HackerNews, Dev.to, Hashnode
   - Indiegogo, Kickstarter
```

---

## 🎓 Deployment Best Practices

### 1. Stagger Large Deployments
```bash
# Don't deploy all at once - space them out
python scripts/deploy_sports_sentiment_spiders.py 60 &
sleep 600  # Wait 10 minutes
python scripts/deploy_technical_spiders.py 90 &
sleep 600
python scripts/deploy_content_enhancement_spiders.py 60 &
```

### 2. Use Background Execution
```bash
# Always use nohup for long-running deployments
nohup python scripts/deploy_sports_sentiment_spiders.py 60 > logs/sports.log 2>&1 &

# Get PID for monitoring
echo $! > pids/sports_sentiment.pid
```

### 3. Monitor Resource Usage
```bash
# Before deployment
free -h
df -h

# During deployment
watch -n 5 'ps aux | grep deploy'
```

### 4. Verify Data Flow
```bash
# Check data is being collected
watch -n 30 'python manage.py shell -c "from persistence.models import SpiderData; print(SpiderData.objects.count())"'

# Check routing is working
python manage.py shell -c "from persistence.models import SpiderData; print(f'Routing: {SpiderData.objects.exclude(routed_to_agents=\"\").count()} / {SpiderData.objects.count()}')"
```

---

## 📈 Success Metrics

### Immediate (During Deployment)
- ✅ Spider processes running without errors
- ✅ Data collection rate > 10 entries/min
- ✅ Routing success rate > 45%

### Short-Term (24 hours)
- ✅ Total data entries > 25,000
- ✅ New entries > 5,000
- ✅ No memory leaks or crashes

### Medium-Term (48 hours)
- ✅ Agent reality scores improving
- ✅ Sports agents > 80%
- ✅ Technical agents > 55%
- ✅ Content agents > 70%
- ✅ Overall system > 75%

---

## 🚨 Emergency Procedures

### Kill All Spider Deployments
```bash
# Nuclear option - stop everything
pkill -f deploy_sports_sentiment
pkill -f deploy_technical_spiders
pkill -f deploy_content_enhancement

# Verify stopped
ps aux | grep deploy
```

### Clear Stuck Data
```bash
# If data appears stuck, restart Celery workers
sudo systemctl restart celery
sudo systemctl restart celery-beat

# Clear Redis cache (CAREFUL!)
redis-cli FLUSHDB
```

### Restart from Clean State
```bash
# Stop all spiders
pkill -f deploy

# Clear logs
rm -f logs/*.log

# Restart services
sudo systemctl restart celery celery-beat redis

# Verify services
sudo systemctl status celery
sudo systemctl status redis
```

---

**Last Session:** Session 12 - October 2, 2025
**Next Priority:** Fix IntelligenceData bug, then deploy financial spiders
**Overall Goal:** 95%+ system reality score

**We're making history! 🚀**
