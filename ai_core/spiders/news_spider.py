"""
News Intelligence Spider - Real-time News Collection
Phase 2: Authenticated News APIs Integration
Collects news from multiple sources using API authentication
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_request_layer import web_request_layer
from api_manager import api_vault, api_manager
from oauth_handler import oauth_handler, social_collector
from bluesky_handler import bluesky_handler, bluesky_collector

logger = logging.getLogger(__name__)


class NewsIntelligenceSpider:
    """
    Collects real-time news from multiple authenticated sources

    Sources:
    - NewsAPI (requires API key)
    - GNews (requires API key)
    - Reddit news subreddits
    - Twitter news feeds
    - HackerNews (no auth)
    - Financial news sites
    """

    def __init__(self):
        self.web_layer = web_request_layer
        self.api_manager = api_manager
        self.oauth = oauth_handler
        self.social = social_collector
        self.bluesky = bluesky_handler
        self.bluesky_collector = bluesky_collector

        # News categories to monitor
        self.categories = [
            'technology', 'business', 'finance', 'science',
            'health', 'sports', 'entertainment'
        ]

        # Reddit news subreddits
        self.news_subreddits = [
            'worldnews', 'news', 'technews', 'stocks',
            'CryptoCurrency', 'artificial', 'MachineLearning'
        ]

    async def collect_all_news(self, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Collect news from all available sources"""

        if not keywords:
            keywords = ['AI', 'technology', 'finance', 'crypto', 'jobs']

        all_news = {
            'timestamp': datetime.now().isoformat(),
            'keywords': keywords,
            'sources': {},
            'articles': [],
            'social_sentiment': {},
            'trending': [],
            'summary': {}
        }

        # Initialize web layer
        await self.web_layer.initialize()
        await self.oauth.initialize()

        # 1. NewsAPI (if configured)
        logger.info("📰 Fetching from NewsAPI...")
        newsapi_articles = await self._fetch_newsapi(keywords)
        if newsapi_articles:
            all_news['sources']['newsapi'] = len(newsapi_articles)
            all_news['articles'].extend(newsapi_articles)

        # 2. HackerNews (no auth required)
        logger.info("📰 Fetching from HackerNews...")
        hn_articles = await self._fetch_hackernews()
        if hn_articles:
            all_news['sources']['hackernews'] = len(hn_articles)
            all_news['articles'].extend(hn_articles)

        # 3. Reddit News
        logger.info("📰 Fetching from Reddit news subreddits...")
        reddit_news = await self._fetch_reddit_news(keywords)
        if reddit_news:
            all_news['sources']['reddit'] = len(reddit_news)
            all_news['articles'].extend(reddit_news)

        # 4. Bluesky News (much better than Twitter!)
        logger.info("📰 Fetching from Bluesky...")
        bluesky_news = await self._fetch_bluesky_news(keywords)
        if bluesky_news:
            all_news['sources']['bluesky'] = len(bluesky_news)
            all_news['articles'].extend(bluesky_news)

        # 5. Financial News
        logger.info("📰 Fetching financial news...")
        financial_news = await self._fetch_financial_news()
        if financial_news:
            all_news['sources']['financial'] = len(financial_news)
            all_news['articles'].extend(financial_news)

        # Calculate sentiment and trends
        all_news['social_sentiment'] = self._analyze_sentiment(all_news['articles'])
        all_news['trending'] = self._extract_trending_topics(all_news['articles'])

        # Generate summary
        all_news['summary'] = {
            'total_articles': len(all_news['articles']),
            'sources_used': len(all_news['sources']),
            'avg_sentiment': all_news['social_sentiment'].get('average', 0),
            'top_keywords': all_news['trending'][:5] if all_news['trending'] else []
        }

        logger.info(f"✅ Collected {all_news['summary']['total_articles']} news articles from {all_news['summary']['sources_used']} sources")

        return all_news

    async def _fetch_newsapi(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        articles = []

        # Check if API key is available
        if not await self.api_manager.vault.can_make_request('newsapi'):
            logger.warning("NewsAPI rate limited or not configured")
            return articles

        try:
            # Search for each keyword
            for keyword in keywords[:3]:  # Limit to conserve quota
                response = await self.api_manager.make_authenticated_request(
                    service='newsapi',
                    url='https://newsapi.org/v2/everything',
                    params={
                        'q': keyword,
                        'sortBy': 'popularity',
                        'pageSize': 5,
                        'language': 'en'
                    }
                )

                if response and response.get('json'):
                    news_data = response['json']
                    if 'articles' in news_data:
                        for article in news_data['articles'][:5]:
                            articles.append({
                                'source': 'newsapi',
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'url': article.get('url', ''),
                                'published_at': article.get('publishedAt', ''),
                                'author': article.get('author', ''),
                                'source_name': article.get('source', {}).get('name', ''),
                                'keyword': keyword,
                                'sentiment': None,  # To be analyzed
                                'relevance_score': self._calculate_relevance(article, keyword)
                            })

            logger.info(f"✅ Fetched {len(articles)} articles from NewsAPI")

        except Exception as e:
            logger.error(f"Error fetching NewsAPI: {e}")

        return articles

    async def _fetch_hackernews(self) -> List[Dict[str, Any]]:
        """Fetch top stories from HackerNews"""
        articles = []

        try:
            # Get top story IDs
            response = await self.web_layer.fetch('https://hacker-news.firebaseio.com/v0/topstories.json')

            if response['status'] == 200 and response['json']:
                story_ids = response['json'][:10]  # Get top 10 stories

                # Fetch each story
                for story_id in story_ids:
                    story_response = await self.web_layer.fetch(
                        f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    )

                    if story_response['status'] == 200 and story_response['json']:
                        story = story_response['json']
                        articles.append({
                            'source': 'hackernews',
                            'title': story.get('title', ''),
                            'description': f"Score: {story.get('score', 0)} | Comments: {story.get('descendants', 0)}",
                            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'published_at': datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                            'author': story.get('by', ''),
                            'source_name': 'HackerNews',
                            'hn_score': story.get('score', 0),
                            'hn_comments': story.get('descendants', 0),
                            'sentiment': None,
                            'relevance_score': min(1.0, story.get('score', 0) / 100)
                        })

            logger.info(f"✅ Fetched {len(articles)} articles from HackerNews")

        except Exception as e:
            logger.error(f"Error fetching HackerNews: {e}")

        return articles

    async def _fetch_reddit_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch news from Reddit news subreddits"""
        articles = []

        try:
            # Get posts from news subreddits
            for subreddit in self.news_subreddits[:3]:  # Limit to conserve rate limits
                posts = await self.oauth.get_subreddit_posts(subreddit, sort='hot', limit=5)

                if posts:
                    for post in posts[:3]:
                        # Check if post contains any keyword
                        post_text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
                        matching_keywords = [kw for kw in keywords if kw.lower() in post_text]

                        if matching_keywords or subreddit in ['worldnews', 'news']:
                            articles.append({
                                'source': 'reddit',
                                'title': post.get('title', ''),
                                'description': post.get('selftext', '')[:500] if post.get('selftext') else '',
                                'url': f"https://reddit.com{post.get('permalink', '')}",
                                'published_at': datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                                'author': post.get('author', ''),
                                'source_name': f"r/{subreddit}",
                                'reddit_score': post.get('score', 0),
                                'reddit_comments': post.get('num_comments', 0),
                                'keywords': matching_keywords,
                                'sentiment': None,
                                'relevance_score': min(1.0, post.get('score', 0) / 1000)
                            })

            logger.info(f"✅ Fetched {len(articles)} news articles from Reddit")

        except Exception as e:
            logger.error(f"Error fetching Reddit news: {e}")

        return articles

    async def _fetch_bluesky_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch news from Bluesky - the open, decentralized Twitter alternative"""
        articles = []

        try:
            # Authenticate with Bluesky
            if await self.bluesky.authenticate():
                # Search for news-related posts
                news_keywords = [f"{kw} news" for kw in keywords[:3]]

                for keyword in news_keywords:
                    posts = await self.bluesky.search_posts(keyword, limit=10)

                    if posts:
                        for post in posts[:5]:  # Limit to 5 per keyword
                            # Filter for news-like posts
                            text = post.get('text', '')

                            # Check if it looks like news (has substantial text, or embeds)
                            if len(text) > 50 or post.get('embed'):
                                articles.append({
                                    'source': 'bluesky',
                                    'title': text[:100] + '...' if len(text) > 100 else text,
                                    'description': text,
                                    'url': f"https://bsky.app/profile/{post['author']['handle']}/post/{post['uri'].split('/')[-1]}",
                                    'published_at': post.get('created_at', ''),
                                    'author': f"@{post['author']['handle']}",
                                    'source_name': 'Bluesky',
                                    'bluesky_metrics': post['metrics'],
                                    'keyword': keyword,
                                    'sentiment': None,
                                    'relevance_score': self._calculate_bluesky_relevance(post)
                                })

                logger.info(f"✅ Fetched {len(articles)} news items from Bluesky")
            else:
                logger.warning("Could not authenticate with Bluesky - check BLUESKY_IDENTIFIER and BLUESKY_PASSWORD in .env")

        except Exception as e:
            logger.error(f"Error fetching Bluesky news: {e}")

        return articles

    async def _fetch_financial_news(self) -> List[Dict[str, Any]]:
        """Fetch financial news from specialized sources"""
        articles = []

        try:
            # Fetch from Alpha Vantage news sentiment (if configured)
            if await self.api_manager.vault.can_make_request('alpha_vantage'):
                response = await self.api_manager.make_authenticated_request(
                    service='alpha_vantage',
                    url='https://www.alphavantage.co/query',
                    params={
                        'function': 'NEWS_SENTIMENT',
                        'topics': 'technology,finance',
                        'limit': 10
                    }
                )

                if response and response.get('json'):
                    feed = response['json'].get('feed', [])
                    for item in feed[:5]:
                        articles.append({
                            'source': 'alpha_vantage',
                            'title': item.get('title', ''),
                            'description': item.get('summary', ''),
                            'url': item.get('url', ''),
                            'published_at': item.get('time_published', ''),
                            'author': '',
                            'source_name': item.get('source', ''),
                            'sentiment_score': item.get('overall_sentiment_score', 0),
                            'ticker_sentiment': item.get('ticker_sentiment', []),
                            'relevance_score': float(item.get('relevance', 0))
                        })

            logger.info(f"✅ Fetched {len(articles)} financial news articles")

        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")

        return articles

    def _calculate_relevance(self, article: Dict, keyword: str) -> float:
        """Calculate relevance score for an article"""
        score = 0.0
        keyword_lower = keyword.lower()

        # Check title
        if keyword_lower in article.get('title', '').lower():
            score += 0.5

        # Check description
        if keyword_lower in article.get('description', '').lower():
            score += 0.3

        # Check source reputation
        reputable_sources = ['reuters', 'bloomberg', 'techcrunch', 'wired', 'forbes']
        source_name = article.get('source', {}).get('name', '').lower()
        if any(source in source_name for source in reputable_sources):
            score += 0.2

        return min(1.0, score)

    def _calculate_bluesky_relevance(self, post: Dict) -> float:
        """Calculate relevance score for a Bluesky post"""
        metrics = post.get('metrics', {})

        # Normalize metrics to 0-1 scale
        reposts = min(1.0, metrics.get('reposts', 0) / 50)
        likes = min(1.0, metrics.get('likes', 0) / 200)
        replies = min(1.0, metrics.get('replies', 0) / 20)
        engagement = min(1.0, metrics.get('engagement', 0) / 300)

        # Weight the metrics (Bluesky has different engagement patterns than Twitter)
        score = (reposts * 0.35) + (likes * 0.35) + (replies * 0.2) + (engagement * 0.1)

        return min(1.0, score)

    def _analyze_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment of collected articles"""
        # Simple sentiment analysis based on keywords
        positive_words = ['success', 'growth', 'profit', 'innovation', 'breakthrough', 'surge', 'gain']
        negative_words = ['loss', 'decline', 'crash', 'fail', 'crisis', 'threat', 'risk', 'concern']

        sentiment_scores = []

        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()

            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)

            # Calculate sentiment score (-1 to 1)
            if positive_count + negative_count > 0:
                sentiment = (positive_count - negative_count) / (positive_count + negative_count)
            else:
                sentiment = 0

            article['sentiment'] = sentiment
            sentiment_scores.append(sentiment)

        # Calculate aggregate sentiment
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            positive_articles = sum(1 for s in sentiment_scores if s > 0.1)
            negative_articles = sum(1 for s in sentiment_scores if s < -0.1)
            neutral_articles = len(sentiment_scores) - positive_articles - negative_articles

            return {
                'average': avg_sentiment,
                'positive': positive_articles,
                'negative': negative_articles,
                'neutral': neutral_articles,
                'distribution': {
                    'positive_pct': (positive_articles / len(sentiment_scores)) * 100,
                    'negative_pct': (negative_articles / len(sentiment_scores)) * 100,
                    'neutral_pct': (neutral_articles / len(sentiment_scores)) * 100
                }
            }

        return {'average': 0, 'positive': 0, 'negative': 0, 'neutral': 0}

    def _extract_trending_topics(self, articles: List[Dict]) -> List[str]:
        """Extract trending topics from articles"""
        from collections import Counter

        # Extract significant words from titles
        words = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were'}

        for article in articles:
            title = article.get('title', '').lower()
            title_words = [w for w in title.split() if len(w) > 3 and w not in stop_words]
            words.extend(title_words)

        # Count word frequency
        word_counts = Counter(words)

        # Get top trending topics
        trending = [word for word, count in word_counts.most_common(20)]

        return trending

    async def monitor_breaking_news(self, keywords: List[str], interval_minutes: int = 15):
        """Monitor for breaking news continuously"""
        logger.info(f"🔍 Starting news monitoring for keywords: {keywords}")

        while True:
            try:
                # Collect news
                news = await self.collect_all_news(keywords)

                # Check for breaking news (high relevance + recent)
                breaking = []
                for article in news['articles']:
                    # Check if article is from last hour
                    try:
                        published = datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00'))
                        if datetime.now(published.tzinfo) - published < timedelta(hours=1):
                            if article.get('relevance_score', 0) > 0.7:
                                breaking.append(article)
                    except:
                        pass

                if breaking:
                    logger.info(f"🚨 BREAKING NEWS: {len(breaking)} high-relevance articles!")
                    for article in breaking[:3]:
                        logger.info(f"   - {article['title'][:100]}")

                # Wait before next check
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in news monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


async def test_news_spider():
    """Test the news intelligence spider"""
    print("\n" + "="*60)
    print("📰 TESTING NEWS INTELLIGENCE SPIDER")
    print("="*60)

    spider = NewsIntelligenceSpider()

    # Test news collection
    print("\n🔍 Collecting news from all sources...")
    news = await spider.collect_all_news(['AI', 'technology', 'cryptocurrency'])

    if news['articles']:
        print(f"\n✅ Collected {news['summary']['total_articles']} articles from {news['summary']['sources_used']} sources")

        # Show source breakdown
        print("\n📊 Articles by source:")
        for source, count in news['sources'].items():
            print(f"   - {source}: {count} articles")

        # Show sentiment analysis
        sentiment = news['social_sentiment']
        if sentiment:
            print(f"\n😊 Sentiment Analysis:")
            print(f"   - Average: {sentiment['average']:.2f} (-1 to 1 scale)")
            print(f"   - Positive: {sentiment.get('positive', 0)} articles")
            print(f"   - Negative: {sentiment.get('negative', 0)} articles")
            print(f"   - Neutral: {sentiment.get('neutral', 0)} articles")

        # Show trending topics
        if news['trending']:
            print(f"\n🔥 Trending Topics:")
            for i, topic in enumerate(news['trending'][:10], 1):
                print(f"   {i}. {topic}")

        # Show sample articles
        print(f"\n📰 Sample Articles:")
        for i, article in enumerate(news['articles'][:5], 1):
            print(f"\n   {i}. {article['title'][:100]}")
            print(f"      Source: {article['source_name']}")
            print(f"      Relevance: {article.get('relevance_score', 0):.2f}")
            print(f"      Sentiment: {article.get('sentiment', 0):.2f}")
            if article.get('url'):
                print(f"      URL: {article['url'][:80]}...")

    else:
        print("❌ No news articles collected")

    # Clean up
    await spider.web_layer.close()
    await spider.oauth.close()

    print("\n" + "="*60)
    print("News Spider Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_news_spider())