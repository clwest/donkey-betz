# Automated Reddit Scout System

## 🎯 Overview

The Automated Reddit Scout system continuously discovers high-quality startup ideas from Reddit without manual intervention. It includes duplicate prevention, score filtering, and rate limiting to ensure only premium ideas are captured.

## 📅 Schedule

### 🔄 Regular Scouting (Every 6 Hours)
- **Task**: `auto-reddit-scout`
- **Schedule**: Every 6 hours (12 AM, 6 AM, 12 PM, 6 PM)
- **Parameters**:
  - Minimum score: `8.0` (high quality only)
  - Max ideas per run: `3`
  - Subreddits: `startupideas`, `SomebodyMakeThis`, `entrepreneur`, `Business_Ideas`

### 🌟 Premium Scouting (Daily)
- **Task**: `premium-reddit-scout`
- **Schedule**: Daily at 9 AM
- **Parameters**:
  - Minimum score: `8.5` (premium quality only)
  - Max ideas per run: `1` (only the best)
  - Subreddits: `startupideas`, `SomebodyMakeThis`

## 🛡️ Safety Features

### Duplicate Prevention
- **DeletedRedditIdea Model**: Tracks deleted ideas with SHA256 content hash
- **Content Hashing**: `title + subreddit` combination prevents re-discovery
- **User-Specific**: Each user's deletions are tracked separately

### Rate Limiting
- **6-Hour Window**: Skips users who have received ideas in the last 6 hours
- **Max Ideas Check**: Respects per-run limits to prevent spam
- **Recent Activity**: Monitors `discovered_at` timestamps

### Quality Filtering
- **Score Thresholds**: Only saves ideas above minimum scores
- **Subreddit Filtering**: Focuses on high-quality startup communities
- **Automation Mode**: Different behavior for scheduled vs manual runs

## 🔧 Components

### 1. Django Management Command
```bash
python manage.py auto_scout_reddit [options]
```

**Options:**
- `--user-id=N`: Scout for specific user (default: all users)
- `--min-score=X`: Minimum score threshold (default: 8.0)
- `--max-ideas=N`: Max ideas per run (default: 5)
- `--subreddits=list`: Comma-separated subreddit list
- `--dry-run`: Test mode (no database saves)
- `--verbose`: Detailed logging

### 2. Celery Task
```python
from agent_orchestra.tasks import auto_scout_reddit_task

result = auto_scout_reddit_task(
    user_id=None,          # None for all users
    min_score=8.0,         # Score threshold
    max_ideas=3,           # Ideas per run
    subreddits=['...'],    # Target subreddits
    dry_run=False          # Production mode
)
```

### 3. Reddit Scout Enhancements
- **Automation Parameters**: `min_score_threshold`, `max_ideas_per_run`, `target_subreddits`
- **Automated Mode Flag**: `automated_mode` for different behavior
- **Synchronous Wrapper**: `discover_startup_ideas()` for Celery compatibility

## 📊 Monitoring

### Logging
- **Task Status**: Success/failure with detailed metrics
- **Discovery Counts**: Ideas found vs ideas saved
- **Skip Reasons**: Rate limiting, duplicates, low scores
- **Performance**: Execution time and resource usage

### Metrics Tracked
- `total_processed`: Users processed
- `total_discovered`: High-quality ideas found
- `min_score`: Quality threshold used
- `subreddits`: Communities scanned
- `dry_run`: Test mode indicator

## 🔍 How It Works

### 1. User Selection
```python
# Target users who have used Reddit Scout before
users = User.objects.filter(
    reddit_ideas__isnull=False
).distinct()
```

### 2. Rate Limiting Check
```python
recent_cutoff = timezone.now() - timedelta(hours=6)
recent_ideas = RedditIdea.objects.filter(
    user=user,
    discovered_at__gte=recent_cutoff
).count()

if recent_ideas >= max_ideas:
    # Skip this user
    continue
```

### 3. Duplicate Prevention
```python
# Check if idea was previously deleted
content_hash = hashlib.sha256(
    f"{title.lower().strip()}:{subreddit.lower()}".encode()
).hexdigest()

if DeletedRedditIdea.objects.filter(
    user=user, 
    content_hash=content_hash
).exists():
    # Skip this idea
    continue
```

### 4. Quality Filtering
```python
# In automated mode, apply stricter filtering
if self.automated_mode:
    if idea_score < self.min_score_threshold:
        # Skip low-score idea
        continue
```

## 🎛️ Configuration

### Celery Beat Settings
```python
# server/celery.py
app.conf.beat_schedule = {
    'auto-reddit-scout': {
        'task': 'agent_orchestra.tasks.auto_scout_reddit_task',
        'schedule': crontab(minute=0, hour='*/6'),
        'kwargs': {
            'min_score': 8.0,
            'max_ideas': 3,
            'subreddits': ['startupideas', 'SomebodyMakeThis'],
            'dry_run': False
        }
    }
}
```

### Environment Variables
- `OPENAI_API_KEY`: Required for idea scoring
- `CELERY_BROKER_URL`: Redis/RabbitMQ for task queue
- `CELERY_RESULT_BACKEND`: Result storage backend

## 🧪 Testing

### Test Script
```bash
python test_reddit_automation.py
```

**Tests Include:**
- Dry run functionality
- Duplicate prevention system
- Score filtering logic
- Rate limiting behavior
- Management command execution

### Manual Testing
```bash
# Test with dry run
python manage.py auto_scout_reddit --dry-run --verbose

# Test specific user
python manage.py auto_scout_reddit --user-id=1 --max-ideas=1

# Test high threshold
python manage.py auto_scout_reddit --min-score=9.0 --dry-run
```

## 🚀 Deployment

### Starting the System
```bash
# Start Celery worker
celery -A server worker -l info

# Start Celery Beat scheduler
celery -A server beat -l info

# Check scheduled tasks
celery -A server inspect scheduled
```

### Monitoring Commands
```bash
# Check task status
celery -A server status

# View active tasks
celery -A server inspect active

# Cancel all tasks
celery -A server purge
```

## 📈 Performance Optimization

### Best Practices
1. **Score Thresholds**: Use 8.0+ for automation to reduce noise
2. **Subreddit Selection**: Focus on quality communities
3. **Rate Limiting**: 6-hour windows prevent user overwhelm
4. **Batch Processing**: Process multiple users efficiently
5. **Error Handling**: Graceful degradation on API failures

### Scaling Considerations
- **API Rate Limits**: Reddit API has request limits
- **Processing Time**: Higher thresholds reduce processing
- **Storage Growth**: Monitor database size
- **User Load**: Scale workers based on user count

## 🔧 Troubleshooting

### Common Issues

1. **No Ideas Discovered**
   - Check API keys and Reddit access
   - Verify score thresholds aren't too high
   - Ensure target subreddits are active

2. **Duplicate Ideas**
   - Verify DeletedRedditIdea model is working
   - Check content hash generation
   - Review duplicate detection logic

3. **Rate Limiting Triggered**
   - Users getting too many ideas too quickly
   - Adjust max_ideas or time windows
   - Check recent activity calculations

4. **Celery Tasks Not Running**
   - Verify Celery Beat is running
   - Check Redis/broker connectivity
   - Review task registration

### Debug Commands
```bash
# Check Redis ideas
redis-cli keys "*reddit*"

# View recent log entries
tail -f celery.log | grep reddit

# Test task manually
python -c "from agent_orchestra.tasks import auto_scout_reddit_task; print(auto_scout_reddit_task(dry_run=True))"
```

## 📋 Maintenance

### Regular Tasks
- **Monitor Discovery Rates**: Track ideas found vs saved
- **Review Score Thresholds**: Adjust based on quality
- **Clean Old Data**: Remove stale deleted idea records
- **Update Subreddits**: Add/remove communities as needed

### Database Maintenance
```sql
-- Check discovery stats
SELECT COUNT(*), AVG(score) FROM agent_orchestra_redditidea 
WHERE discovered_at >= NOW() - INTERVAL '7 days';

-- Clean old deleted records (optional)
DELETE FROM agent_orchestra_deletedredditidea 
WHERE deleted_at < NOW() - INTERVAL '90 days';
```

## 🎉 Success Metrics

The automated system is working correctly when:
- ✅ High-quality ideas (8.0+ score) are discovered regularly
- ✅ No duplicate ideas appear after deletion
- ✅ Users aren't overwhelmed with too many ideas
- ✅ System respects rate limits and API quotas
- ✅ Celery tasks complete successfully without errors

---

*This automation system ensures users receive a steady stream of premium startup opportunities without manual intervention, while maintaining quality and preventing spam.*