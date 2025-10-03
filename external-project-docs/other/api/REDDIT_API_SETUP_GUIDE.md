# Reddit API Setup Guide

## Quick Setup (5 minutes)

### 1. Create Reddit App

1. **Go to Reddit Apps Page**
   - Visit: https://www.reddit.com/prefs/apps
   - Log in to your Reddit account

2. **Create New App**
   - Click "Create App" or "Create Another App"
   - Fill in:
     - **Name**: DonkeyBetz Bot
     - **App type**: Select "script" (for personal use)
     - **Description**: Business idea scout for DonkeyBetz
     - **About URL**: (leave blank)
     - **Redirect URI**: http://localhost:8000/callback (required but not used)
   - Click "Create app"

3. **Get Your Credentials**
   - **Client ID**: The string under "personal use script" (14 characters)
   - **Client Secret**: The secret key shown (27 characters)

### 2. Configure Environment

Add to your `.env` file:
```bash
# Reddit API
REDDIT_CLIENT_ID=your_14_char_client_id_here
REDDIT_CLIENT_SECRET=your_27_char_secret_here
REDDIT_USER_AGENT=DonkeyBetz/1.0
```

### 3. Install Dependencies

```bash
cd backend
pip install praw asyncpraw
```

### 4. Test the Integration

```bash
python test_reddit_api.py
```

## What the Reddit API Provides

### 1. **Real Business Ideas**
- Hot posts from business/startup subreddits
- Real engagement metrics (upvotes, comments, awards)
- Actual user discussions and feedback
- Timestamp data for trend analysis

### 2. **User Credibility**
- Account age and karma scores
- Post/comment history analysis
- Premium status and verification
- Credibility scoring for idea validation

### 3. **Trending Analysis**
- Real-time trending topics
- Keyword frequency analysis
- Sentiment tracking
- Market interest indicators

### 4. **Search Capabilities**
- Search across multiple subreddits
- Time-based filtering (hour, day, week, month)
- Keyword and phrase matching
- Advanced query parameters

## Subreddits We Monitor

### Business & Startups
- r/Entrepreneur
- r/startups
- r/SaaS
- r/Business_Ideas
- r/Startup_Ideas
- r/smallbusiness

### Niche Communities
- r/EntrepreneurRideAlong
- r/indiebiz
- r/sidehustle
- r/passive_income
- r/ecommerce
- r/SocialMediaMarketing

### Investment & Growth
- r/growthhacking
- r/venturecapital

## ML Feature Extraction

The Reddit API provides rich data for ML scoring:

### Engagement Features
- `upvote_ratio` - Quality indicator (0-1)
- `score` - Total upvotes
- `num_comments` - Discussion level
- `awards` - Premium engagement
- `velocity` - Score per hour

### User Features
- `author_karma` - User reputation
- `account_age` - Credibility factor
- `is_premium` - Paid member status
- `verified_email` - Trust indicator

### Content Features
- `title_length` - Conciseness
- `text_length` - Detail level
- `has_tldr` - Summarization
- `question_count` - Engagement seeking

### Temporal Features
- `created_utc` - Post timestamp
- `hours_old` - Recency
- `time_of_day` - Posting patterns
- `day_of_week` - Activity patterns

## Rate Limits

Reddit API has the following limits:
- **60 requests per minute** (OAuth)
- **10 requests per minute** (Non-OAuth)
- **1000 listings per request** maximum
- **Respect 2-second delay** between requests

Our service handles rate limiting automatically with:
- Request queuing
- Automatic retries
- Cache layer (15-minute TTL)
- Batch processing

## Integration Status

### ✅ Completed
- Reddit API Service implementation
- Mock data fallback
- Integration with enhanced_tools
- Caching layer
- Error handling
- Test suite

### 🚧 Next Steps
1. Add Reddit credentials to production
2. Enable real-time monitoring
3. Implement ML scoring pipeline
4. Add to Reddit Scout agent
5. Create dashboard for insights

## Troubleshooting

### "Reddit API not configured"
- Check .env file has credentials
- Restart Django server after adding credentials
- Verify credentials at reddit.com/prefs/apps

### "Rate limit exceeded"
- Service automatically handles this
- Check cache is working (Redis)
- Reduce request frequency if needed

### "Import error: praw"
- Run: `pip install praw asyncpraw`
- Check virtual environment is active
- Update requirements.txt

## Security Notes

- **Never commit credentials** to git
- Use read-only OAuth scope
- Rotate secrets periodically
- Monitor API usage in Reddit dashboard

## Ready to Use!

With credentials configured, the system will:
1. Fetch real Reddit data instead of simulations
2. Provide authentic engagement metrics
3. Enable trend analysis with real data
4. Improve ML scoring accuracy significantly

The integration seamlessly falls back to mock data when credentials aren't available, ensuring the system always works.