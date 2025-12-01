"""
News Harvesting Spider - Real-Time News Intelligence
===================================================

Specialized spider for gathering real-time news from financial and tech sources.
Processes news articles for sentiment, market impact, and trend analysis.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class NewsHarvesterSpider(BaseIntelligenceSpider):
    """Real-time news harvesting and analysis spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.news_categories = [
            'breaking_news', 'earnings', 'mergers', 'ipos', 'regulatory',
            'technology', 'crypto', 'markets', 'economy', 'fed'
        ]

        self.market_impact_keywords = {
            'high': ['breaking', 'unprecedented', 'major', 'significant', 'massive'],
            'medium': ['important', 'notable', 'considerable', 'substantial'],
            'low': ['minor', 'slight', 'small', 'limited']
        }

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process news data"""
        try:
            if any(source in target.url for source in ['bloomberg', 'reuters', 'wsj', 'ft']):
                return await self._process_financial_news(raw_data, target)
            elif any(source in target.url for source in ['techcrunch', 'wired', 'verge']):
                return await self._process_tech_news(raw_data, target)
            else:
                return await self._process_general_news(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing news data: {e}")
            return None

    async def _process_financial_news(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process financial news articles"""
        try:
            articles = []

            # Extract articles from different formats
            if 'content' in data:
                # HTML content
                soup = BeautifulSoup(data['content'], 'html.parser')
                articles = self._extract_articles_from_html(soup, 'financial')
            elif 'articles' in data:
                # API format
                articles = data['articles']
            elif 'entries' in data:
                # RSS feed format
                articles = self._process_rss_entries(data['entries'])

            # Analyze each article
            for article in articles:
                # Sentiment analysis
                article['sentiment'] = self._analyze_news_sentiment(article)

                # Market impact assessment
                article['market_impact'] = self._assess_market_impact(article)

                # Category classification
                article['category'] = self._classify_news_category(article)

                # Extract entities (companies, people, etc.)
                article['entities'] = self._extract_entities(article)

                # Calculate urgency score
                article['urgency_score'] = self._calculate_urgency_score(article)

            # Create news analysis
            news_analysis = {
                'total_articles': len(articles),
                'sentiment_breakdown': self._analyze_sentiment_breakdown(articles),
                'impact_distribution': self._analyze_impact_distribution(articles),
                'trending_topics': self._identify_trending_topics(articles),
                'breaking_news': self._identify_breaking_news(articles),
                'market_movers': self._identify_market_movers(articles)
            }

            # Create intelligence content
            intelligence_content = {
                'articles': articles,
                'news_analysis': news_analysis,
                'market_insights': self._generate_market_insights(articles),
                'alert_worthy': self._identify_alert_worthy_news(articles)
            }

            quality_score = self._calculate_news_quality(intelligence_content)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="financial_news",
                content=intelligence_content,
                metadata={
                    'article_count': len(articles),
                    'breaking_news_count': len(news_analysis['breaking_news']),
                    'high_impact_count': sum(1 for a in articles if a.get('market_impact') == 'high'),
                    'data_source': 'financial_news'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'financial', 'market_impact', 'breaking'],
                target_agents=['news_analysis_agent', 'market_impact_agent', 'alert_system_agent'],
                target_advisors=['warren_buffett', 'ray_dalio', 'financial_strategist', 'legal_counsel']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing financial news: {e}")
            return None

    def _extract_articles_from_html(self, soup: BeautifulSoup, news_type: str) -> List[Dict[str, Any]]:
        """Extract articles from HTML"""
        articles = []

        try:
            # Common selectors for news articles
            article_selectors = [
                'article', '.article', '.story', '.post',
                '[data-module="ArticleBody"]', '.news-item'
            ]

            for selector in article_selectors:
                article_elements = soup.select(selector)

                for element in article_elements[:20]:  # Limit to 20 articles
                    article = self._extract_article_data(element)
                    if article and article.get('title'):
                        articles.append(article)

                if articles:  # If we found articles with this selector, use them
                    break

        except Exception as e:
            self.logger.warning(f"Error extracting articles from HTML: {e}")

        return articles

    def _extract_article_data(self, element) -> Dict[str, Any]:
        """Extract article data from HTML element"""
        article = {
            'title': '',
            'summary': '',
            'content': '',
            'author': '',
            'published_time': '',
            'url': '',
            'source': '',
            'tags': []
        }

        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', '.title', '.headline', '[data-module="ArticleHeadline"]']
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    article['title'] = title_elem.get_text().strip()
                    break

            # Extract summary/description
            summary_selectors = ['.summary', '.description', '.excerpt', '.lead', 'p']
            for selector in summary_selectors:
                summary_elem = element.select_one(selector)
                if summary_elem:
                    summary_text = summary_elem.get_text().strip()
                    if len(summary_text) > 50:  # Ensure it's substantial
                        article['summary'] = summary_text[:500]  # Limit length
                        break

            # Extract author
            author_selectors = ['.author', '.byline', '[data-module="ArticleAuthor"]']
            for selector in author_selectors:
                author_elem = element.select_one(selector)
                if author_elem:
                    article['author'] = author_elem.get_text().strip()
                    break

            # Extract publish time
            time_selectors = ['time', '.timestamp', '.date', '[data-module="ArticleTimestamp"]']
            for selector in time_selectors:
                time_elem = element.select_one(selector)
                if time_elem:
                    time_text = time_elem.get('datetime') or time_elem.get_text()
                    article['published_time'] = time_text.strip()
                    break

            # Extract URL
            link_elem = element.select_one('a')
            if link_elem and link_elem.get('href'):
                article['url'] = link_elem['href']

            # Extract tags
            tag_selectors = ['.tags', '.categories', '.topics']
            for selector in tag_selectors:
                tag_elems = element.select(f'{selector} a, {selector} span')
                if tag_elems:
                    article['tags'] = [tag.get_text().strip() for tag in tag_elems[:5]]
                    break

            # If no publish time, use current time
            if not article['published_time']:
                article['published_time'] = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            self.logger.warning(f"Error extracting article data: {e}")

        return article

    def _strip_html(self, text: str) -> str:
        """Strip HTML tags from text content.

        Session 293: RSS feeds often contain HTML in summaries.
        """
        if not text:
            return ''
        try:
            soup = BeautifulSoup(text, 'html.parser')
            clean_text = soup.get_text(separator=' ', strip=True)
            return ' '.join(clean_text.split())
        except Exception:
            import re
            return re.sub(r'<[^>]+>', '', text).strip()

    def _process_rss_entries(self, entries: List[Any]) -> List[Dict[str, Any]]:
        """Process RSS feed entries"""
        articles = []

        for entry in entries[:20]:  # Limit to 20 entries
            # Session 293: Strip HTML from all text fields - RSS often contains markup
            raw_summary = getattr(entry, 'summary', '')
            raw_content = ''
            if hasattr(entry, 'content') and entry.content:
                raw_content = entry.content[0].get('value', '')

            article = {
                'title': self._strip_html(getattr(entry, 'title', '')),
                'summary': self._strip_html(raw_summary),
                'content': self._strip_html(raw_content),
                'author': self._strip_html(getattr(entry, 'author', '')),
                'published_time': getattr(entry, 'published', ''),
                'url': getattr(entry, 'link', ''),
                'source': getattr(entry, 'source', {}).get('title', ''),
                'tags': [self._strip_html(tag.term) for tag in getattr(entry, 'tags', [])]
            }

            # Use summary for content if content is empty
            if not article['content'] and article['summary']:
                article['content'] = article['summary']

            if article['title']:  # Only add if we have a title
                articles.append(article)

        return articles

    def _analyze_news_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of news article"""
        try:
            # Combine title and summary for analysis
            text = f"{article.get('title', '')} {article.get('summary', '')}"

            # Use TextBlob for basic sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Enhance with financial-specific sentiment
            financial_sentiment = self._analyze_financial_sentiment(text)

            return {
                'polarity': polarity,  # -1 (negative) to 1 (positive)
                'subjectivity': subjectivity,  # 0 (objective) to 1 (subjective)
                'financial_sentiment': financial_sentiment,
                'classification': self._classify_sentiment(polarity, financial_sentiment)
            }

        except Exception as e:
            self.logger.warning(f"Error analyzing sentiment: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.5, 'classification': 'neutral'}

    def _analyze_financial_sentiment(self, text: str) -> float:
        """Analyze financial-specific sentiment"""
        positive_words = [
            'growth', 'profit', 'gain', 'surge', 'rally', 'bullish', 'optimistic',
            'breakthrough', 'expansion', 'success', 'outperform', 'beat', 'exceed'
        ]

        negative_words = [
            'loss', 'decline', 'fall', 'crash', 'bearish', 'pessimistic',
            'concern', 'risk', 'threat', 'struggle', 'miss', 'disappoint'
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count + negative_count == 0:
            return 0.0

        return (positive_count - negative_count) / (positive_count + negative_count)

    def _classify_sentiment(self, polarity: float, financial_sentiment: float) -> str:
        """Classify overall sentiment"""
        combined_sentiment = (polarity + financial_sentiment) / 2

        if combined_sentiment > 0.1:
            return 'positive'
        elif combined_sentiment < -0.1:
            return 'negative'
        else:
            return 'neutral'

    def _assess_market_impact(self, article: Dict[str, Any]) -> str:
        """Assess potential market impact of news"""
        try:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            impact_score = 0

            # Check for high impact keywords
            for impact_level, keywords in self.market_impact_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        if impact_level == 'high':
                            impact_score += 3
                        elif impact_level == 'medium':
                            impact_score += 2
                        else:
                            impact_score += 1

            # Check for market-moving events
            market_events = [
                'earnings', 'merger', 'acquisition', 'ipo', 'bankruptcy',
                'regulatory', 'fed', 'interest rate', 'gdp', 'inflation'
            ]

            for event in market_events:
                if event in text:
                    impact_score += 2

            # Check for company mentions (simplified)
            company_indicators = ['inc', 'corp', 'ltd', 'co.', 'company']
            if any(indicator in text for indicator in company_indicators):
                impact_score += 1

            # Classify impact
            if impact_score >= 6:
                return 'high'
            elif impact_score >= 3:
                return 'medium'
            else:
                return 'low'

        except Exception as e:
            self.logger.warning(f"Error assessing market impact: {e}")
            return 'low'

    def _classify_news_category(self, article: Dict[str, Any]) -> str:
        """Classify news into categories"""
        try:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()

            category_keywords = {
                'earnings': ['earnings', 'quarterly', 'revenue', 'profit'],
                'mergers': ['merger', 'acquisition', 'buyout', 'takeover'],
                'regulatory': ['regulatory', 'regulation', 'fda', 'sec', 'compliance'],
                'technology': ['technology', 'tech', 'ai', 'software', 'digital'],
                'crypto': ['crypto', 'bitcoin', 'blockchain', 'ethereum'],
                'economy': ['economy', 'economic', 'gdp', 'inflation', 'unemployment'],
                'fed': ['federal reserve', 'fed', 'interest rate', 'monetary policy'],
                'ipos': ['ipo', 'initial public offering', 'going public'],
                'breaking_news': ['breaking', 'urgent', 'alert', 'developing']
            }

            for category, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    return category

            return 'general'

        except Exception as e:
            self.logger.warning(f"Error classifying news category: {e}")
            return 'general'

    def _extract_entities(self, article: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract named entities from article"""
        entities = {
            'companies': [],
            'people': [],
            'locations': [],
            'tickers': []
        }

        try:
            text = f"{article.get('title', '')} {article.get('summary', '')}"

            # Extract potential tickers
            ticker_pattern = r'\b([A-Z]{1,5})\b'
            potential_tickers = re.findall(ticker_pattern, text)

            # Filter out common false positives
            false_positives = {
                'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
                'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'DID', 'GET', 'HAS'
            }

            entities['tickers'] = [t for t in potential_tickers if t not in false_positives][:5]

            # Extract company names (simplified)
            company_pattern = r'\b([A-Z][a-z]+ (?:Inc|Corp|Ltd|Co\.?|Company|Corporation))\b'
            entities['companies'] = re.findall(company_pattern, text)[:5]

            # Extract proper nouns as potential people/places
            proper_noun_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            proper_nouns = re.findall(proper_noun_pattern, text)[:10]

            # Simple heuristic: if it contains common name words, it's probably a person
            name_indicators = ['CEO', 'President', 'Chairman', 'CFO', 'said', 'stated']
            context_text = text.lower()

            for noun in proper_nouns:
                if any(indicator in context_text for indicator in ['ceo', 'president', 'chairman']):
                    entities['people'].append(noun)
                else:
                    entities['locations'].append(noun)

            # Limit each category
            for category in entities:
                entities[category] = entities[category][:3]

        except Exception as e:
            self.logger.warning(f"Error extracting entities: {e}")

        return entities

    def _calculate_urgency_score(self, article: Dict[str, Any]) -> float:
        """Calculate urgency score for article"""
        try:
            urgency_score = 0.0

            # Time factor
            published_time = article.get('published_time', '')
            if published_time:
                try:
                    pub_time = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
                    hours_ago = (datetime.now(timezone.utc) - pub_time).total_seconds() / 3600
                    # More recent = higher urgency
                    time_factor = max(0, 1 - (hours_ago / 24))  # Decay over 24 hours
                    urgency_score += time_factor * 0.3
                except:
                    pass

            # Market impact factor
            impact = article.get('market_impact', 'low')
            if impact == 'high':
                urgency_score += 0.4
            elif impact == 'medium':
                urgency_score += 0.2

            # Category factor
            category = article.get('category', 'general')
            urgent_categories = ['breaking_news', 'earnings', 'regulatory', 'fed']
            if category in urgent_categories:
                urgency_score += 0.3

            return min(1.0, urgency_score)

        except Exception as e:
            self.logger.warning(f"Error calculating urgency score: {e}")
            return 0.0

    def _analyze_sentiment_breakdown(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment breakdown across articles"""
        breakdown = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'avg_polarity': 0.0,
            'avg_subjectivity': 0.0
        }

        if not articles:
            return breakdown

        polarities = []
        subjectivities = []

        for article in articles:
            sentiment = article.get('sentiment', {})
            classification = sentiment.get('classification', 'neutral')

            breakdown[classification] += 1
            polarities.append(sentiment.get('polarity', 0))
            subjectivities.append(sentiment.get('subjectivity', 0.5))

        breakdown['avg_polarity'] = sum(polarities) / len(polarities)
        breakdown['avg_subjectivity'] = sum(subjectivities) / len(subjectivities)

        return breakdown

    def _analyze_impact_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze market impact distribution"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}

        for article in articles:
            impact = article.get('market_impact', 'low')
            distribution[impact] += 1

        return distribution

    def _identify_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify trending topics from articles"""
        topic_counts = {}

        for article in articles:
            # Count category occurrences
            category = article.get('category', 'general')
            topic_counts[category] = topic_counts.get(category, 0) + 1

            # Count entity mentions
            entities = article.get('entities', {})
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    topic_counts[entity] = topic_counts.get(entity, 0) + 1

        # Sort by frequency and return top topics
        trending = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return [{'topic': topic, 'mentions': count} for topic, count in trending]

    def _identify_breaking_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify breaking news articles"""
        breaking_news = []

        for article in articles:
            if (article.get('category') == 'breaking_news' or
                article.get('urgency_score', 0) > 0.8 or
                article.get('market_impact') == 'high'):

                breaking_news.append({
                    'title': article.get('title', ''),
                    'urgency_score': article.get('urgency_score', 0),
                    'market_impact': article.get('market_impact', 'low'),
                    'sentiment': article.get('sentiment', {}).get('classification', 'neutral'),
                    'url': article.get('url', '')
                })

        return sorted(breaking_news, key=lambda x: x['urgency_score'], reverse=True)[:10]

    def _identify_market_movers(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify articles about potential market movers"""
        market_movers = []

        for article in articles:
            entities = article.get('entities', {})
            tickers = entities.get('tickers', [])

            if tickers and article.get('market_impact') in ['high', 'medium']:
                market_movers.append({
                    'title': article.get('title', ''),
                    'tickers': tickers,
                    'market_impact': article.get('market_impact', 'low'),
                    'sentiment': article.get('sentiment', {}).get('classification', 'neutral'),
                    'category': article.get('category', 'general')
                })

        return market_movers[:10]

    def _generate_market_insights(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market insights from news analysis"""
        insights = {
            'market_mood': 'neutral',
            'key_themes': [],
            'sector_sentiment': {},
            'risk_factors': [],
            'opportunities': []
        }

        if not articles:
            return insights

        # Determine overall market mood
        positive_count = sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'positive')
        negative_count = sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'negative')

        if positive_count > negative_count * 1.5:
            insights['market_mood'] = 'optimistic'
        elif negative_count > positive_count * 1.5:
            insights['market_mood'] = 'pessimistic'
        else:
            insights['market_mood'] = 'mixed'

        # Extract key themes
        category_counts = {}
        for article in articles:
            category = article.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1

        insights['key_themes'] = [
            {'theme': theme, 'frequency': count}
            for theme, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return insights

    def _identify_alert_worthy_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify news worthy of immediate alerts"""
        alert_worthy = []

        for article in articles:
            alert_score = 0

            # High urgency score
            if article.get('urgency_score', 0) > 0.8:
                alert_score += 3

            # High market impact
            if article.get('market_impact') == 'high':
                alert_score += 3

            # Breaking news category
            if article.get('category') == 'breaking_news':
                alert_score += 2

            # Strong sentiment (very positive or negative)
            sentiment_polarity = article.get('sentiment', {}).get('polarity', 0)
            if abs(sentiment_polarity) > 0.5:
                alert_score += 1

            if alert_score >= 4:  # Threshold for alerts
                alert_worthy.append({
                    'title': article.get('title', ''),
                    'alert_score': alert_score,
                    'urgency_score': article.get('urgency_score', 0),
                    'market_impact': article.get('market_impact', 'low'),
                    'category': article.get('category', 'general'),
                    'entities': article.get('entities', {}),
                    'url': article.get('url', '')
                })

        return sorted(alert_worthy, key=lambda x: x['alert_score'], reverse=True)[:5]

    def _calculate_news_quality(self, content: Dict[str, Any]) -> float:
        """Calculate quality score for news intelligence"""
        score = 0.0

        # Article count
        article_count = len(content.get('articles', []))
        score += min(0.3, article_count / 20)  # Up to 20 articles = full score

        # Analysis completeness
        if content.get('news_analysis'):
            score += 0.3

        # Market insights generated
        if content.get('market_insights'):
            score += 0.2

        # Alert-worthy news identified
        alert_count = len(content.get('alert_worthy', []))
        score += min(0.2, alert_count / 5)  # Up to 5 alerts = full score

        return score

    async def _process_tech_news(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process technology news (similar to financial news but with tech focus)"""
        # Implementation would be similar to financial news but with tech-specific analysis
        return await self._process_financial_news(data, target)

    async def _process_general_news(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general news data"""
        try:
            news_data = data.copy() if isinstance(data, dict) else {'raw_data': data}
            news_data['timestamp'] = datetime.now(timezone.utc).isoformat()

            quality_score = self.calculate_data_quality(news_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_news",
                content=news_data,
                metadata={'data_source': 'general_news'},
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'general'],
                target_agents=['news_analysis_agent'],
                target_advisors=['financial_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general news: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['title', 'published_time']

    def get_timestamp_field(self) -> Optional[str]:
        return 'published_time'

    def get_relevance_keywords(self) -> List[str]:
        return ['news', 'breaking', 'market', 'financial', 'earnings', 'merger']

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        try:
            # Check for required fields
            if not data.get('title'):
                return False

            # Check urgency score range
            if 'urgency_score' in data:
                score = float(data['urgency_score'])
                if score < 0 or score > 1:
                    return False

            # Check sentiment values
            sentiment = data.get('sentiment', {})
            if 'polarity' in sentiment:
                polarity = float(sentiment['polarity'])
                if polarity < -1 or polarity > 1:
                    return False

            return True
        except (ValueError, TypeError):
            return False