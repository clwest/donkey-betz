"""
Content Monetization Spider Army
Intelligence gathering for content creation and monetization opportunities
"""

import scrapy
import re
import json
from datetime import datetime
from urllib.parse import urljoin
from .base_spider import ContentOpportunitySpider


class YouTubeChannelAnalyzerSpider(ContentOpportunitySpider):
    """
    YouTube channel and trend analyzer
    Identifies viral content patterns and monetization opportunities
    """

    name = 'youtube_analyzer'
    allowed_domains = ['youtube.com']

    # Target content niches for analysis
    target_niches = [
        'ai tutorials',
        'passive income',
        'crypto education',
        'stock market',
        'entrepreneurship',
        'tech reviews',
        'productivity',
        'online business',
        'digital marketing',
        'web development'
    ]

    def start_requests(self):
        """Generate YouTube search requests"""
        for niche in self.target_niches:
            # Search for recent popular videos in niche
            search_query = niche.replace(' ', '+')
            url = f"https://www.youtube.com/results?search_query={search_query}&sp=CAMSAhAB"  # Recent + Popular

            yield scrapy.Request(
                url=url,
                callback=self.parse_youtube_search,
                meta={'niche': niche}
            )

    def parse_youtube_search(self, response):
        """Parse YouTube search results"""
        # YouTube uses dynamic loading, so we'll extract from initial script data
        scripts = response.css('script::text').getall()

        for script in scripts:
            if 'var ytInitialData = ' in script:
                try:
                    # Extract JSON data from script
                    json_start = script.find('var ytInitialData = ') + len('var ytInitialData = ')
                    json_end = script.find(';</script>', json_start)
                    if json_end == -1:
                        json_end = script.find(';', json_start)

                    if json_end > json_start:
                        json_str = script[json_start:json_end]
                        data = json.loads(json_str)

                        # Process video data
                        videos = self.extract_youtube_videos(data, response)
                        for video in videos:
                            intelligence = self.process_item(video, response)
                            if intelligence:
                                yield intelligence

                except Exception as e:
                    self.logger.error(f"Error parsing YouTube JSON: {e}")

                break

    def extract_youtube_videos(self, data, response):
        """Extract video data from YouTube JSON"""
        videos = []

        try:
            # Navigate through YouTube's complex JSON structure
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {})
            section_list = contents.get('sectionListRenderer', {}).get('contents', [])

            for section in section_list:
                item_section = section.get('itemSectionRenderer', {})
                contents = item_section.get('contents', [])

                for item in contents:
                    video_renderer = item.get('videoRenderer')
                    if video_renderer:
                        video_data = self.extract_video_data(video_renderer, response)
                        if video_data:
                            videos.append(video_data)

        except Exception as e:
            self.logger.error(f"Error extracting YouTube videos: {e}")

        return videos

    def extract_video_data(self, video_renderer, response):
        """Extract individual video data from renderer"""
        try:
            video_id = video_renderer.get('videoId')
            if not video_id:
                return None

            title_runs = video_renderer.get('title', {}).get('runs', [])
            title = title_runs[0].get('text', '') if title_runs else ''

            # Extract view count
            view_count_text = ''
            view_count_runs = video_renderer.get('viewCountText', {}).get('simpleText', '')
            if view_count_runs:
                view_count_text = view_count_runs

            # Extract channel name
            channel_name = ''
            owner_text = video_renderer.get('ownerText', {}).get('runs', [])
            if owner_text:
                channel_name = owner_text[0].get('text', '')

            # Extract publish time
            publish_time = ''
            published_time_text = video_renderer.get('publishedTimeText', {}).get('simpleText', '')
            if published_time_text:
                publish_time = published_time_text

            # Extract thumbnail
            thumbnail_url = ''
            thumbnails = video_renderer.get('thumbnail', {}).get('thumbnails', [])
            if thumbnails:
                thumbnail_url = thumbnails[-1].get('url', '')  # Get highest quality

            video_data = {
                'video_id': video_id,
                'title': title,
                'channel_name': channel_name,
                'view_count_text': view_count_text,
                'publish_time': publish_time,
                'thumbnail_url': thumbnail_url,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'niche': response.meta.get('niche'),
                'platform': 'youtube',
                'data_type': 'video_trend',
                'scraped_at': datetime.now().isoformat(),
                'monetization_potential': self.calculate_monetization_potential(title, view_count_text),
                'content_analysis': self.analyze_content_patterns(title)
            }

            return video_data

        except Exception as e:
            self.logger.error(f"Error extracting video data: {e}")
            return None

    def calculate_monetization_potential(self, title, view_count_text):
        """Calculate monetization potential based on title and views"""
        score = 0.5

        # High-value keywords boost score
        high_value_keywords = [
            'how to make money', 'passive income', 'side hustle', 'earn online',
            'tutorial', 'course', 'strategy', 'tips', 'secrets', 'guide'
        ]

        title_lower = title.lower()
        keyword_matches = sum(1 for keyword in high_value_keywords if keyword in title_lower)
        score += keyword_matches * 0.1

        # Parse view count for engagement score
        if view_count_text:
            views = self.parse_view_count(view_count_text)
            if views:
                if views > 1000000:  # 1M+ views
                    score += 0.3
                elif views > 100000:  # 100K+ views
                    score += 0.2
                elif views > 10000:   # 10K+ views
                    score += 0.1

        return min(1.0, score)

    def parse_view_count(self, view_text):
        """Parse view count text into number"""
        if not view_text:
            return None

        # Extract number from text like "1.2M views" or "500K views"
        numbers = re.findall(r'([\d.]+)([KMB]?)', view_text)
        if numbers:
            num_str, suffix = numbers[0]
            try:
                num = float(num_str)
                if suffix == 'K':
                    num *= 1000
                elif suffix == 'M':
                    num *= 1000000
                elif suffix == 'B':
                    num *= 1000000000
                return int(num)
            except ValueError:
                pass

        return None

    def analyze_content_patterns(self, title):
        """Analyze content patterns for trending topics"""
        patterns = {
            'tutorial': bool(re.search(r'\b(how to|tutorial|guide|step by step)\b', title, re.IGNORECASE)),
            'money_focused': bool(re.search(r'\b(money|income|profit|earn|cash|dollar)\b', title, re.IGNORECASE)),
            'urgency': bool(re.search(r'\b(now|today|fast|quick|instant|immediate)\b', title, re.IGNORECASE)),
            'numbers': bool(re.search(r'\$?\d+[KMB]?|\d{4}', title)),
            'ai_related': bool(re.search(r'\b(ai|artificial intelligence|chatgpt|automation|machine learning)\b', title, re.IGNORECASE)),
            'crypto_related': bool(re.search(r'\b(crypto|bitcoin|ethereum|blockchain|defi|nft)\b', title, re.IGNORECASE))
        }

        return patterns


class SubstackNewsletterSpider(ContentOpportunitySpider):
    """
    Substack newsletter trend analyzer
    Identifies successful newsletter patterns and monetization strategies
    """

    name = 'substack_analyzer'
    allowed_domains = ['substack.com']

    # Target newsletter categories
    newsletter_categories = [
        'technology',
        'business',
        'finance',
        'entrepreneurship',
        'ai',
        'crypto',
        'productivity',
        'marketing'
    ]

    def start_requests(self):
        """Generate Substack exploration requests"""
        # Substack discovery page
        yield scrapy.Request(
            url="https://substack.com/discover",
            callback=self.parse_substack_discover,
            meta={'page_type': 'discover'}
        )

        # Category pages
        for category in self.newsletter_categories:
            url = f"https://substack.com/discover/category/{category}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_substack_category,
                meta={'category': category}
            )

    def parse_substack_discover(self, response):
        """Parse Substack discovery page"""
        newsletter_links = response.css('a[href*="/p/"]::attr(href)').getall()

        for link in newsletter_links[:20]:  # Limit to avoid overwhelming
            if link.startswith('/'):
                link = urljoin(response.url, link)
            yield scrapy.Request(
                url=link,
                callback=self.parse_newsletter_post,
                meta={'source': 'discover'}
            )

    def parse_substack_category(self, response):
        """Parse Substack category page"""
        newsletter_cards = response.css('[data-testid="publication-card"]')

        for card in newsletter_cards:
            try:
                newsletter_data = self.extract_newsletter_data(card, response)
                if newsletter_data:
                    intelligence = self.process_item(newsletter_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting newsletter data: {e}")

    def extract_newsletter_data(self, card, response):
        """Extract newsletter data from Substack card"""
        try:
            title = card.css('h3::text').get() or card.css('h2::text').get()
            if not title:
                return None

            description = card.css('p::text').get() or ""
            author = card.css('[class*="author"]::text').get() or ""
            subscribers = card.css('[class*="subscriber"]::text').get() or ""

            newsletter_url = card.css('a::attr(href)').get()
            if newsletter_url:
                newsletter_url = urljoin(response.url, newsletter_url)

            newsletter_data = {
                'title': title.strip(),
                'description': description.strip(),
                'author': author.strip(),
                'subscribers_text': subscribers.strip(),
                'newsletter_url': newsletter_url,
                'category': response.meta.get('category'),
                'platform': 'substack',
                'data_type': 'newsletter_trend',
                'scraped_at': datetime.now().isoformat(),
                'monetization_analysis': self.analyze_newsletter_monetization(title, description, subscribers)
            }

            return newsletter_data

        except Exception as e:
            self.logger.error(f"Error extracting newsletter data: {e}")
            return None

    def parse_newsletter_post(self, response):
        """Parse individual newsletter post"""
        try:
            post_data = self.extract_post_data(response)
            if post_data:
                intelligence = self.process_item(post_data, response)
                if intelligence:
                    yield intelligence

        except Exception as e:
            self.logger.error(f"Error parsing newsletter post: {e}")

    def extract_post_data(self, response):
        """Extract post data from Substack post"""
        try:
            title = response.css('h1::text').get()
            if not title:
                return None

            author = response.css('[class*="author-name"]::text').get() or ""
            content_preview = ' '.join(response.css('p::text').getall()[:3])  # First 3 paragraphs

            # Extract engagement metrics if available
            likes = response.css('[class*="like-count"]::text').get() or ""
            comments = response.css('[class*="comment-count"]::text').get() or ""

            post_data = {
                'title': title.strip(),
                'author': author.strip(),
                'content_preview': content_preview.strip(),
                'likes': likes.strip(),
                'comments': comments.strip(),
                'post_url': response.url,
                'platform': 'substack',
                'data_type': 'newsletter_post',
                'scraped_at': datetime.now().isoformat(),
                'content_analysis': self.analyze_post_content(title, content_preview)
            }

            return post_data

        except Exception as e:
            self.logger.error(f"Error extracting post data: {e}")
            return None

    def analyze_newsletter_monetization(self, title, description, subscribers):
        """Analyze newsletter monetization potential"""
        text = f"{title} {description}".lower()

        monetization_indicators = {
            'premium_model': bool(re.search(r'\b(premium|paid|subscription|member)\b', text)),
            'business_focus': bool(re.search(r'\b(business|entrepreneur|startup|invest|money)\b', text)),
            'education_focus': bool(re.search(r'\b(learn|course|tutorial|guide|training)\b', text)),
            'high_value_niche': bool(re.search(r'\b(finance|tech|ai|crypto|real estate)\b', text)),
        }

        # Parse subscriber count
        subscriber_count = self.parse_subscriber_count(subscribers)

        return {
            'indicators': monetization_indicators,
            'subscriber_count': subscriber_count,
            'monetization_score': sum(monetization_indicators.values()) * 0.25
        }

    def parse_subscriber_count(self, subscribers_text):
        """Parse subscriber count from text"""
        if not subscribers_text:
            return None

        numbers = re.findall(r'([\d.]+)([KM]?)', subscribers_text)
        if numbers:
            num_str, suffix = numbers[0]
            try:
                num = float(num_str)
                if suffix == 'K':
                    num *= 1000
                elif suffix == 'M':
                    num *= 1000000
                return int(num)
            except ValueError:
                pass

        return None

    def analyze_post_content(self, title, content):
        """Analyze post content for trending topics"""
        text = f"{title} {content}".lower()

        trending_topics = {
            'ai_trend': bool(re.search(r'\b(ai|chatgpt|artificial intelligence|automation|ml)\b', text)),
            'crypto_trend': bool(re.search(r'\b(crypto|bitcoin|blockchain|defi|web3)\b', text)),
            'business_trend': bool(re.search(r'\b(startup|entrepreneur|business|saas|growth)\b', text)),
            'investment_trend': bool(re.search(r'\b(invest|stock|market|portfolio|trading)\b', text)),
            'productivity_trend': bool(re.search(r'\b(productivity|workflow|efficiency|tools)\b', text)),
        }

        return trending_topics


class TwitterInfluencerSpider(ContentOpportunitySpider):
    """
    Twitter/X influencer and trend analyzer
    Note: This would require Twitter API access for full functionality
    """

    name = 'twitter_trends'
    allowed_domains = ['twitter.com', 'x.com']

    def start_requests(self):
        """
        Generate requests for Twitter trends
        Note: Twitter's new structure makes scraping difficult without API
        This is a basic implementation for educational purposes
        """
        # Public trending topics page (limited access)
        yield scrapy.Request(
            url="https://twitter.com/explore/tabs/trending",
            callback=self.parse_twitter_trends,
            meta={'trend_type': 'general'}
        )

    def parse_twitter_trends(self, response):
        """
        Parse Twitter trends page
        Note: This is limited due to Twitter's authentication requirements
        """
        # Twitter now requires authentication for most content
        # This would need to be implemented with proper API access
        self.logger.info("Twitter trends parsing requires API access")

        # Placeholder for when API access is implemented
        trend_data = {
            'message': 'Twitter trends spider requires API integration',
            'platform': 'twitter',
            'data_type': 'social_trend',
            'scraped_at': datetime.now().isoformat(),
            'note': 'Implement with Twitter API for full functionality'
        }

        intelligence = self.process_item(trend_data, response)
        if intelligence:
            yield intelligence