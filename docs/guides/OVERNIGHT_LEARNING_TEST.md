# 🌙 Overnight Autonomous Learning Test Guide

**Purpose**: Run the autonomous learning system overnight to generate learning data and observe how the system improves itself.

**Status**: ✅ Safe for overnight testing (completely local, no public deployment)

---

## 🚀 Quick Start

### Option 1: Full Night Test (8 hours)
```bash
# Start the overnight test
python scripts/overnight_learning_test.py --duration 480

# This will run for 8 hours (480 minutes)
# Safe to leave running overnight
```

### Option 2: Short Test (2 hours)
```bash
# For testing during the day
python scripts/overnight_learning_test.py --duration 120
```

### Option 3: Custom Duration
```bash
# Specify any duration in minutes
python scripts/overnight_learning_test.py --duration 360  # 6 hours
```

---

## 📊 What It Does

### Every 30-Minute Cycle:

1. **🕷️ Spider Deployment**
   - Deploys 10 different spider types
   - 3 spiders per type (30 total per cycle)
   - Collects real data from:
     - Freelance platforms (Guru, Toptal, RemoteOK, etc.)
     - Content platforms (Medium, Gumroad)
     - Market data (Financial, Social Sentiment)

2. **🤖 Agent Execution**
   - Executes 10 diverse agents
   - Each with different tasks
   - Agents include:
     - Market Analyst
     - Content Creator
     - Data Scientist
     - Business Analyst
     - And 6 more...

3. **🧠 Autonomous Learning**
   - AgentExecution records created automatically
   - Django signals fire learning bridges
   - Learning orchestrator processes insights
   - UserAgentLearning records generated
   - System improves itself!

4. **📈 Progress Monitoring**
   - Logs everything to console and file
   - Tracks learning record creation
   - Shows confidence scores
   - Reports errors

---

## 📝 Logs & Output

### Real-Time Monitoring
```bash
# Watch the test run in real-time
tail -f overnight_learning_test.log
```

### What You'll See:
```
2025-10-02 23:00:00 [INFO] 🌙 OVERNIGHT AUTONOMOUS LEARNING TEST STARTED
2025-10-02 23:00:05 [INFO] 🕷️  Deploying 10 spider types...
2025-10-02 23:02:15 [INFO]   ✅ guru: 42 items collected
2025-10-02 23:04:30 [INFO]   ✅ toptal: 38 items collected
2025-10-02 23:10:00 [INFO] 🤖 Executing 10 agents...
2025-10-02 23:10:05 [INFO]   ✅ market-analyst completed successfully
2025-10-02 23:15:00 [INFO] 📊 Learning Progress:
2025-10-02 23:15:00 [INFO]   AgentExecution records: 145
2025-10-02 23:15:00 [INFO]   UserAgentLearning records: 312
```

### Log Files Created:
1. **overnight_learning_test.log** - Detailed execution log
2. **overnight_test_report_YYYYMMDD_HHMMSS.json** - Final summary report

---

## 🌅 Review Results in the Morning

### Simple Review:
```bash
python scripts/review_overnight_results.py
```

### Custom Time Range:
```bash
# Review last 12 hours
python scripts/review_overnight_results.py --hours 12

# Review last 24 hours
python scripts/review_overnight_results.py --hours 24
```

### What You'll See:
```
================================================================================
  OVERNIGHT AUTONOMOUS LEARNING TEST RESULTS
================================================================================

📊 OVERALL STATISTICS

Time Period: Last 12 hours
From: 2025-10-01 23:00:00
To: 2025-10-02 11:00:00

📈 Data Generated:
  • Agent Executions: 240
  • Learning Records: 520
  • Spider Data: 1,850
  • Learning Ratio: 2.17 records per execution

================================================================================
  🤖 AGENT EXECUTION BREAKDOWN
================================================================================

Agent                          Completed    Failed       Success Rate
--------------------------------------------------------------------------------
market-analyst                 28           2            93.3%
content-creator                25           0            100.0%
data-scientist                 24           1            96.0%
...

================================================================================
  🧠 LEARNING INSIGHTS GENERATED
================================================================================

Learning Domain                          Count      Avg Confidence
--------------------------------------------------------------------------------
agent_execution_performance              145        0.68
task_type_general                        120        0.62
collaboration                            98         0.71
...
```

---

## 🛑 Stop the Test Anytime

The test can be safely stopped at any time:

```bash
# Press Ctrl+C in the terminal
# or
# Close the terminal window
```

The final report will be generated automatically when stopped.

---

## 📊 Expected Results

### After 8 Hours:
- **~16 cycles** (one every 30 minutes)
- **~480 spider deployments** (30 per cycle)
- **~160 agent executions** (10 per cycle)
- **~320-400 learning records** (2-2.5 per execution)
- **~2,000-3,000 spider data items** collected

### Learning Quality:
- **Initial confidence**: 0.50-0.60
- **After learning**: 0.65-0.75+
- **High confidence records**: 50-100
- **Learning domains**: 10-15 different types

---

## 🔍 What to Look For

### Good Signs:
✅ Learning records increasing over time
✅ Confidence scores improving (trending up)
✅ High success rate for agent executions (>90%)
✅ Diverse learning domains
✅ Multiple learning sources

### Things to Watch:
⚠️ Agent execution failures (should be <10%)
⚠️ Spider collection errors (some sites block scrapers)
⚠️ Low confidence scores (<0.40 may need more data)

---

## 💡 Tips for Best Results

### 1. Ensure Server is Running
```bash
# The Django server must be running
# Check with:
ps aux | grep daphne

# If not running:
daphne -p 8000 core.asgi:application
```

### 2. Check Database Space
```bash
# Make sure you have enough disk space
df -h .
```

### 3. Monitor Memory Usage
```bash
# Check memory periodically
top -l 1 | grep -E "PhysMem|Python"
```

### 4. Keep Logs Manageable
```bash
# Rotate logs if they get too large
# The test automatically limits log size
```

---

## 🎯 Use Cases

### 1. Test Autonomous Learning
**Goal**: Verify the learning system works end-to-end
**Duration**: 2-4 hours
**Focus**: Check learning record creation and confidence scores

### 2. Performance Testing
**Goal**: See how system performs under load
**Duration**: 4-8 hours
**Focus**: Monitor error rates and execution times

### 3. Data Collection
**Goal**: Build up learning data for agents
**Duration**: 8-12 hours
**Focus**: Maximize spider data collection

### 4. Long-Term Learning
**Goal**: Observe learning improvements over time
**Duration**: Multiple nights
**Focus**: Track confidence score trends

---

## 🔧 Troubleshooting

### Test Won't Start
```bash
# Check Django setup
python manage.py check

# Verify user exists
python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username='chris').exists())"
```

### No Learning Records Created
```bash
# Check if learning bridges are active
python manage.py shell -c "from core.models_unified_system import UserAgentLearning; print(UserAgentLearning.objects.count())"

# Verify AgentExecution records are being created
python manage.py shell -c "from core.models_unified_system import AgentExecution; print(AgentExecution.objects.count())"
```

### Spiders Failing
```bash
# Some websites block scrapers - this is normal
# Check which spiders work best:
python manage.py shell -c "from persistence.models import SpiderData; print(SpiderData.objects.values('spider_name').annotate(count=models.Count('id')).order_by('-count'))"
```

---

## 📈 Next Steps After Test

1. **Review Results**
   ```bash
   python scripts/review_overnight_results.py
   ```

2. **Check Specific Agents**
   ```bash
   python manage.py shell -c "
   from core.models_unified_system import UserAgentLearning
   from django.contrib.auth import get_user_model
   User = get_user_model()
   chris = User.objects.get(username='chris')

   # Show learning for specific agent
   learning = UserAgentLearning.objects.filter(
       user=chris,
       agent_name='market-analyst'
   ).order_by('-confidence_score')[:5]

   for l in learning:
       print(f'{l.learning_domain}: {l.confidence_score:.2f}')
   "
   ```

3. **Analyze Trends**
   - Compare confidence scores over time
   - Identify best-performing agents
   - Find learning gaps that need more data

4. **Iterate**
   - Run more tests focusing on weak agents
   - Adjust spider types based on what works
   - Experiment with different task types

---

## 🎉 Success Criteria

The test is successful if:

✅ **Learning records are created** (any amount is good!)
✅ **Confidence scores exist** (even low scores show learning)
✅ **Multiple learning domains** covered
✅ **No critical errors** (some spider failures are OK)
✅ **System continues running** throughout the test

**Even modest results prove the autonomous learning system works!**

---

## 🔒 Safety Notes

- ✅ **Completely local** - No public deployment
- ✅ **Safe to stop anytime** - No data corruption risk
- ✅ **No external dependencies** - Works offline (except web scraping)
- ✅ **Resource efficient** - Designed for overnight running
- ✅ **Automatic cleanup** - Logs are managed automatically

---

**Happy Testing!** 🚀

Watch your AI system learn and improve itself overnight! 🧠✨
