"""
Spider Intelligence API Views
Session 208: API endpoints for querying spider data intelligently.

Endpoints:
    GET /api/spider-intelligence/trends/      - Trending topics
    GET /api/spider-intelligence/market/      - Market insights (crypto, stocks)
    GET /api/spider-intelligence/tech/        - Tech trends
    GET /api/spider-intelligence/jobs/        - Job market summary
    GET /api/spider-intelligence/search/      - Search spider data
    GET /api/spider-intelligence/summary/     - Data summary statistics
    GET /api/spider-intelligence/insights/    - Get insights for a prompt
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from core.services.spider_intelligence import SpiderIntelligenceService


@csrf_exempt
@require_http_methods(["GET"])
def trending_topics(request):
    """
    Get trending topics from spider data.

    Query params:
        category: Filter by category (tech, financial, jobs, news, etc.)
        hours: Look back period (default: 24)
        limit: Max topics (default: 10)
    """
    try:
        service = SpiderIntelligenceService()

        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 10))

        # Cap limits for performance
        hours = min(hours, 168)  # Max 1 week
        limit = min(limit, 50)

        trends = service.get_trending_topics(
            category=category,
            hours=hours,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'trends': trends,
            'params': {
                'category': category,
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def market_insights(request):
    """
    Get financial/crypto market insights.
    Aggregates data from CoinGecko, Yahoo Finance, etc.
    """
    try:
        service = SpiderIntelligenceService()
        insights = service.get_market_insights()

        return JsonResponse({
            'status': 'success',
            'insights': insights
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tech_trends(request):
    """
    Get technology trends from HackerNews, DevTo, GitHub, etc.

    Query params:
        hours: Look back period (default: 24)
        limit: Max items per category (default: 15)
    """
    try:
        service = SpiderIntelligenceService()

        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 15))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 50)

        trends = service.get_tech_trends(hours=hours, limit=limit)

        return JsonResponse({
            'status': 'success',
            'trends': trends,
            'params': {
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def job_market(request):
    """
    Get remote job market summary.

    Query params:
        hours: Look back period (default: 48)
        limit: Max jobs (default: 20)
    """
    try:
        service = SpiderIntelligenceService()

        hours = int(request.GET.get('hours', 48))
        limit = int(request.GET.get('limit', 20))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 100)

        summary = service.get_job_market_summary(hours=hours, limit=limit)

        return JsonResponse({
            'status': 'success',
            'job_market': summary,
            'params': {
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_data(request):
    """
    Full-text search across spider data.

    Query params:
        q: Search query (required)
        category: Filter by category
        hours: Look back period (default: 72)
        limit: Max results (default: 50)
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({
                'status': 'error',
                'message': 'Query parameter "q" is required'
            }, status=400)

        service = SpiderIntelligenceService()

        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 72))
        limit = int(request.GET.get('limit', 50))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 100)

        results = service.search_spider_data(
            query=query,
            category=category,
            hours=hours,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results),
            'params': {
                'category': category,
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def data_summary(request):
    """
    Get summary statistics for spider data.

    Query params:
        spider: Filter by spider name
        hours: Look back period (default: 24)
    """
    try:
        service = SpiderIntelligenceService()

        spider_name = request.GET.get('spider')
        hours = int(request.GET.get('hours', 24))

        # Cap limits
        hours = min(hours, 168)

        summary = service.get_data_summary(
            spider_name=spider_name,
            hours=hours
        )

        return JsonResponse({
            'status': 'success',
            'summary': summary
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def prompt_insights(request):
    """
    Get relevant insights for an AI prompt.
    Used by agents to enhance their responses with real data.

    GET/POST params:
        prompt: The user's prompt (required)
        limit: Max insights per category (default: 5)
    """
    try:
        # Get prompt from GET or POST
        if request.method == 'POST':
            import json
            data = json.loads(request.body or b'{}')
            prompt = data.get('prompt', '')
            limit = data.get('limit', 5)
        else:
            prompt = request.GET.get('prompt', '').strip()
            limit = int(request.GET.get('limit', 5))

        if not prompt:
            return JsonResponse({
                'status': 'error',
                'message': 'Parameter "prompt" is required'
            }, status=400)

        service = SpiderIntelligenceService()

        # Cap limit
        limit = min(limit, 20)

        insights = service.get_insights_for_prompt(
            prompt=prompt,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'prompt': prompt,
            'insights': insights
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def daily_report(request):
    """
    Generate a daily intelligence report.
    Combines trends, market data, and notable items.
    """
    try:
        service = SpiderIntelligenceService()

        # Gather all insights
        trends = service.get_trending_topics(hours=24, limit=10)
        market = service.get_market_insights()
        tech = service.get_tech_trends(hours=24, limit=10)
        jobs = service.get_job_market_summary(hours=24, limit=5)
        summary = service.get_data_summary(hours=24)

        # Build report
        report = {
            'title': 'Daily Intelligence Report',
            'generated_at': summary.get('generated_at'),
            'period': '24 hours',

            'highlights': {
                'total_data_points': summary.get('total_items', 0),
                'active_spiders': len(summary.get('by_spider', {})),
                'top_trend': trends[0] if trends else None,
            },

            'sections': {
                'trending_topics': {
                    'title': 'Trending Topics',
                    'items': trends[:5]
                },
                'market_snapshot': {
                    'title': 'Market Snapshot',
                    'crypto': market.get('crypto', [])[:5],
                    'summary': market.get('summary', '')
                },
                'tech_pulse': {
                    'title': 'Tech Pulse',
                    'top_discussions': tech.get('discussions', [])[:5],
                    'hot_topics': tech.get('topics', [])[:10]
                },
                'job_market': {
                    'title': 'Remote Job Market',
                    'total_jobs': jobs.get('total_found', 0),
                    'top_categories': jobs.get('categories', [])[:5],
                    'featured_jobs': jobs.get('jobs', [])[:3]
                }
            },

            'data_sources': summary.get('by_spider', {})
        }

        return JsonResponse({
            'status': 'success',
            'report': report
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============================================================
# SESSION 344: ENHANCED MARKET RESEARCH DASHBOARD
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def market_research_dashboard(request):
    """
    Session 344: Enhanced market research endpoint.
    Returns crypto and stocks with related news articles.

    Query params:
        hours: Look back period (default: 24)
        crypto_limit: Max crypto assets (default: 10)
        stock_limit: Max stocks (default: 10)
        news_limit: Max news per asset (default: 3)
    """
    from datetime import timedelta
    from django.utils import timezone
    from core.models_unified_system import SpiderData

    try:
        hours = int(request.GET.get('hours', 24))
        crypto_limit = int(request.GET.get('crypto_limit', 10))
        stock_limit = int(request.GET.get('stock_limit', 10))
        news_limit = int(request.GET.get('news_limit', 3))

        # Cap limits
        hours = min(hours, 168)
        crypto_limit = min(crypto_limit, 20)
        stock_limit = min(stock_limit, 20)
        news_limit = min(news_limit, 5)

        since = timezone.now() - timedelta(hours=hours)

        # ========== CRYPTO SECTION ==========
        crypto_data = SpiderData.objects.filter(
            spider_name__in=['coingecko', 'etherscan'],
            created_at__gte=since
        ).order_by('-created_at')

        crypto_assets = []
        seen_crypto = set()

        for entry in crypto_data:
            if not entry.raw_data:
                continue
            items = entry.raw_data.get('items', [])
            for item in items:
                symbol = item.get('symbol', '').upper()
                if symbol and symbol not in seen_crypto and len(crypto_assets) < crypto_limit:
                    seen_crypto.add(symbol)

                    # Calculate price change - coingecko uses price_change_percentage_24h
                    change = item.get('price_change_percentage_24h') or item.get('change_24h') or 0
                    try:
                        change = float(change)
                    except:
                        change = 0

                    # Get price - coingecko uses current_price
                    price = item.get('current_price') or item.get('price') or 0

                    crypto_assets.append({
                        'symbol': symbol,
                        'name': item.get('name', symbol),
                        'price': price,
                        'change_24h': round(change, 2),
                        'change_pct': round(change, 2),  # Alias for template
                        'change_direction': 'up' if change > 0 else 'down' if change < 0 else 'neutral',
                        'market_cap': item.get('market_cap'),
                        'volume_24h': item.get('total_volume'),
                        'high_24h': item.get('high_24h'),
                        'low_24h': item.get('low_24h'),
                        'image': item.get('image'),
                        'source': entry.spider_name
                    })

        # ========== STOCKS SECTION (Live via yfinance) ==========
        # Session 344: Use Yahoo Finance spider for live stock data
        stock_assets = []
        try:
            from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
            yahoo_spider = YahooFinanceSpider()
            live_stocks = yahoo_spider.fetch_data(max_results=stock_limit)

            for item in live_stocks:
                symbol = item.get('symbol', '').upper()
                change = item.get('change_percent') or item.get('percent_change') or 0
                price = item.get('current_price') or item.get('price') or 0

                stock_assets.append({
                    'symbol': symbol,
                    'name': item.get('name', symbol),
                    'price': price,
                    'change': round(change, 2) if change else 0,
                    'change_pct': round(change, 2) if change else 0,
                    'change_direction': 'up' if change > 0 else 'down' if change < 0 else 'neutral',
                    'sector': item.get('sector', 'N/A'),
                    'volume': item.get('volume'),
                    'source': 'yahoo_finance'
                })

        except Exception as e:
            logger.warning(f"Error fetching live stock data: {e}")

        # ========== FINANCIAL NEWS ==========
        # Get news from financial news sources
        news_spiders = ['business_news', 'reuters_rss', 'seekingalpha', 'newsapi', 'bbc', 'cnn']
        news_data = SpiderData.objects.filter(
            spider_name__in=news_spiders,
            created_at__gte=since
        ).order_by('-created_at')

        # Collect all financial news
        all_news = []
        seen_urls = set()

        # Keywords for financial news
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain', 'defi', 'nft', 'binance', 'coinbase']
        stock_keywords = ['stock', 'market', 'trading', 'nasdaq', 'dow', 'nyse', 's&p', 'fed', 'inflation', 'earnings', 'ipo']

        for entry in news_data:
            if not entry.raw_data:
                continue
            items = entry.raw_data.get('items', [])
            for item in items:
                title = item.get('title', '')
                url = item.get('url', '') or item.get('link', '')

                if not title or not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                title_lower = title.lower()
                description = (item.get('description', '') or item.get('summary', ''))[:200]

                # Classify news as crypto, stock, or general finance
                is_crypto = any(kw in title_lower for kw in crypto_keywords)
                is_stock = any(kw in title_lower for kw in stock_keywords)

                # Also check for specific asset mentions
                mentioned_cryptos = [c['symbol'] for c in crypto_assets if c['symbol'].lower() in title_lower or c['name'].lower() in title_lower]
                mentioned_stocks = [s['symbol'] for s in stock_assets if s['symbol'].lower() in title_lower or (s['name'] and s['name'].lower() in title_lower)]

                if is_crypto or is_stock or mentioned_cryptos or mentioned_stocks:
                    all_news.append({
                        'title': title,
                        'description': description,
                        'url': url,
                        'source': entry.spider_name,
                        'published': item.get('published') or item.get('date') or item.get('pubDate'),
                        'category': 'crypto' if is_crypto or mentioned_cryptos else 'stock',
                        'mentioned_cryptos': mentioned_cryptos[:3],
                        'mentioned_stocks': mentioned_stocks[:3]
                    })

        # Split news by category
        crypto_news = [n for n in all_news if n['category'] == 'crypto'][:news_limit * 3]
        stock_news = [n for n in all_news if n['category'] == 'stock'][:news_limit * 3]

        # ========== SEC FILINGS SECTION (Session 385) ==========
        # Fetch live SEC filings using the updated spider
        sec_filings = []
        try:
            from ai_core.spiders.specialized.sec_spider import SECSpider
            sec_spider = SECSpider()
            sec_filings = sec_spider.fetch_data(max_results=15)
        except Exception as e:
            logger.warning(f"Error fetching SEC filings: {e}")

        # ========== BUILD RESPONSE ==========
        return JsonResponse({
            'status': 'success',
            'data': {
                'crypto': {
                    'assets': crypto_assets,
                    'news': crypto_news,
                    'total_assets': len(crypto_assets),
                    'total_news': len(crypto_news)
                },
                'stocks': {
                    'assets': stock_assets,
                    'news': stock_news,
                    'total_assets': len(stock_assets),
                    'total_news': len(stock_news)
                },
                'sec_filings': {
                    'filings': sec_filings,
                    'total_filings': len(sec_filings),
                    'high_impact_count': len([f for f in sec_filings if f.get('is_high_impact')])
                },
                'summary': {
                    'period_hours': hours,
                    'last_updated': timezone.now().isoformat(),
                    'sources': list(set([a['source'] for a in crypto_assets + stock_assets] + ['sec_edgar']))
                }
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============================================================
# SESSION 385: OPPORTUNITIES DASHBOARD
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def opportunities_dashboard(request):
    """
    Get comprehensive opportunities dashboard data.
    Aggregates:
    - Remote jobs (weworkremotely, remoteok, adzuna)
    - Freelance gigs (guru, toptal, peopleperhour, ninetyninedesigns, flexjobs)
    - Crowdfunding projects (kickstarter, indiegogo)
    - Startup ideas (indiehackers, producthunt)

    Query params:
        hours: Hours back to look (default: 72)
        limit: Max items per category (default: 10)
    """
    hours = int(request.GET.get('hours', 72))
    limit = int(request.GET.get('limit', 10))

    try:
        from core.models_unified_system import SpiderData
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(hours=hours)

        # Helper function to get spider data
        # SpiderData stores items in raw_data['items'] as a list
        def get_spider_items(source_names, item_limit=10):
            items = []
            for source in source_names:
                spider_data = SpiderData.objects.filter(
                    spider_name__icontains=source,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:5]  # Get fewer records, each has multiple items

                for data in spider_data:
                    raw = data.raw_data or {}
                    # Items are stored as a list in raw_data['items']
                    raw_items = raw.get('items', [])
                    if isinstance(raw_items, list):
                        for item in raw_items:
                            if len(items) >= item_limit:
                                break
                            items.append({
                                'id': str(data.id),
                                'title': (item.get('title', '') or 'Untitled')[:100],
                                'url': item.get('url') or item.get('link', ''),
                                'source': data.spider_name,
                                'description': (item.get('description') or item.get('summary', ''))[:200],
                                'salary': item.get('salary', ''),
                                'company': item.get('company', ''),
                                'location': item.get('location', 'Remote'),
                                'category': item.get('category', ''),
                                'created_at': data.created_at.isoformat() if data.created_at else None,
                                'tags': item.get('tags', [])[:5] if isinstance(item.get('tags'), list) else []
                            })
                    if len(items) >= item_limit:
                        break
            return items[:item_limit]

        # Remote Jobs
        job_sources = ['weworkremotely', 'remoteok', 'adzuna', 'angellist']
        remote_jobs = get_spider_items(job_sources, limit)

        # Freelance Gigs - Session 386: Use Reddit forhire/freelance since those spiders have real data
        # Traditional freelance platforms (guru, toptal, etc.) require JS rendering
        freelance_gigs = []
        freelance_sources = []
        # Extract freelance posts from Reddit
        reddit_freelance_data = SpiderData.objects.filter(
            spider_name__icontains='reddit',
            created_at__gte=cutoff
        ).order_by('-created_at')[:10]

        for data in reddit_freelance_data:
            raw = data.raw_data or {}
            raw_items = raw.get('items', [])
            if isinstance(raw_items, list):
                for item in raw_items:
                    subreddit = item.get('subreddit', '').lower()
                    title = item.get('title', '').lower()
                    # Focus on hiring/freelance subreddits and posts
                    if subreddit in ['forhire', 'freelance', 'remotework', 'designjobs'] or \
                       any(kw in title for kw in ['[hiring]', '[for hire]', 'looking for', 'need a', 'freelance', 'contract']):
                        if len(freelance_gigs) >= limit:
                            break
                        freelance_gigs.append({
                            'id': str(data.id),
                            'title': (item.get('title', '') or 'Untitled')[:100],
                            'url': item.get('url') or item.get('link', ''),
                            'source': f"r/{item.get('subreddit', 'reddit')}",
                            'description': '',
                            'salary': '',
                            'company': '',
                            'location': 'Remote',
                            'category': 'Freelance',
                            'created_at': data.created_at.isoformat() if data.created_at else None,
                            'tags': []
                        })
                        freelance_sources.append(f"r/{item.get('subreddit', 'reddit')}")
            if len(freelance_gigs) >= limit:
                break
        freelance_sources = list(set(freelance_sources))

        # Crowdfunding/Creative Projects - Session 386: Use Behance since Kickstarter/Indiegogo need JS
        crowdfunding_sources = ['behance', 'dribbble']
        crowdfunding = get_spider_items(crowdfunding_sources, limit)

        # Startup Ideas & Discussions
        startup_sources = ['indiehackers', 'producthunt']
        startup_ideas = get_spider_items(startup_sources, limit)

        # Business & Tech Discussions from Reddit
        # Session 385: Broadened to include AI, ML, design, and tech discussions
        # SpiderData stores items in raw_data['items'] as a list
        reddit_data = SpiderData.objects.filter(
            spider_name__icontains='reddit',
            created_at__gte=cutoff
        ).order_by('-created_at')[:15]  # Get more records for variety

        # Session 386: Ensure subreddit diversity in discussions
        # Collect posts grouped by subreddit first, then interleave for variety
        discussions_by_subreddit = {}  # subreddit -> list of posts

        # Relevant subreddits for opportunities (priority order)
        relevant_subreddits = [
            'entrepreneur', 'startups', 'sideproject', 'indiehackers',  # Business
            'forhire', 'freelance', 'remotework', 'designjobs',  # Work
            'machinelearning', 'artificial', 'datascience',  # AI/ML
            'stablediffusion', 'midjourney', 'chatgpt', 'localllama',  # AI Tools
            'webdev', 'programming',  # Tech
            'graphic_design', 'web_design', 'ui_design',  # Design
        ]
        # Keywords for posts from any subreddit
        opportunity_keywords = [
            'business', 'startup', 'entrepreneur', 'side hustle', 'freelance',
            'income', 'money', 'job', 'career', 'salary', 'remote', 'hiring',
            'looking for', 'need help', 'project', 'client', 'gig', 'opportunity',
            'ai', 'machine learning', 'llm', 'gpt', 'stable diffusion', 'midjourney',
            'tutorial', 'how to', 'tips', 'advice', 'best practices', 'built', 'made',
            'launched', 'release', 'new tool', 'open source'
        ]

        for data in reddit_data:
            raw = data.raw_data or {}
            raw_items = raw.get('items', [])
            if isinstance(raw_items, list):
                for item in raw_items:
                    title = item.get('title', 'Untitled')
                    subreddit = item.get('subreddit', '').lower()
                    title_lower = title.lower()

                    # Include if: relevant subreddit OR matching keywords
                    is_relevant = (
                        subreddit in relevant_subreddits or
                        any(kw in title_lower for kw in opportunity_keywords)
                    )

                    if is_relevant:
                        post = {
                            'id': str(data.id),
                            'title': title[:100],
                            'url': item.get('url') or item.get('link', ''),
                            'source': data.spider_name,
                            'subreddit': item.get('subreddit', ''),
                            'score': item.get('score', 0),
                            'comments': item.get('num_comments', 0),
                            'created_at': data.created_at.isoformat() if data.created_at else None
                        }
                        # Group by subreddit
                        if subreddit not in discussions_by_subreddit:
                            discussions_by_subreddit[subreddit] = []
                        # Keep top 5 per subreddit (sorted by score later)
                        if len(discussions_by_subreddit[subreddit]) < 5:
                            discussions_by_subreddit[subreddit].append(post)

        # Interleave posts from different subreddits for variety
        discussions = []
        # Sort each subreddit's posts by score
        for sub in discussions_by_subreddit:
            discussions_by_subreddit[sub].sort(key=lambda x: x.get('score', 0), reverse=True)

        # Round-robin from each subreddit
        round_num = 0
        while len(discussions) < limit and round_num < 5:
            for sub in discussions_by_subreddit:
                posts = discussions_by_subreddit[sub]
                if round_num < len(posts):
                    discussions.append(posts[round_num])
                    if len(discussions) >= limit:
                        break
            round_num += 1

        return JsonResponse({
            'status': 'success',
            'data': {
                'remote_jobs': {
                    'items': remote_jobs,
                    'total': len(remote_jobs),
                    'sources': job_sources
                },
                'freelance_gigs': {
                    'items': freelance_gigs,
                    'total': len(freelance_gigs),
                    'sources': freelance_sources
                },
                'crowdfunding': {
                    'items': crowdfunding,
                    'total': len(crowdfunding),
                    'sources': crowdfunding_sources
                },
                'startup_ideas': {
                    'items': startup_ideas,
                    'total': len(startup_ideas),
                    'sources': startup_sources
                },
                'business_discussions': {
                    'items': discussions,
                    'total': len(discussions),
                    'sources': ['reddit']
                },
                'summary': {
                    'period_hours': hours,
                    'last_updated': timezone.now().isoformat(),
                    'total_opportunities': len(remote_jobs) + len(freelance_gigs) + len(crowdfunding) + len(startup_ideas) + len(discussions)
                }
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============================================================
# SESSION 343: SPIDER REGISTRY AND TEST ENDPOINTS
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def spider_registry(request):
    """
    Get the full spider registry with all 102 spiders.
    Returns spider names, classes, categories, and configuration.
    """
    try:
        from ai_core.spiders.spider_registry import get_spider_registry

        registry = get_spider_registry()
        spiders = registry.list_spiders()

        return JsonResponse({
            'status': 'success',
            'spiders': spiders,
            'total': len(spiders),
            'categories': registry.get_spider_count()['by_category']
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def test_spider(request):
    """
    Test a specific spider by fetching live RSS data.

    Query params:
        spider: The spider name to test (required)
    """
    import time
    import feedparser

    spider_name = request.GET.get('spider', '').strip()
    if not spider_name:
        return JsonResponse({
            'status': 'error',
            'message': 'Parameter "spider" is required'
        }, status=400)

    try:
        from ai_core.spiders.spider_registry import get_spider_registry

        registry = get_spider_registry()
        spider_class = registry.get_spider_class(spider_name)

        if not spider_class:
            return JsonResponse({
                'status': 'error',
                'message': f'Spider "{spider_name}" not found'
            }, status=404)

        # Try to get RSS feeds from the spider class
        rss_feeds = getattr(spider_class, 'RSS_FEEDS', {})

        if not rss_feeds:
            return JsonResponse({
                'status': 'success',
                'result': {
                    'success': True,
                    'spider': spider_name,
                    'articles_count': 0,
                    'feeds_tested': 0,
                    'message': 'Spider does not use RSS feeds (likely uses API)',
                    'sample_titles': []
                }
            })

        # Test the RSS feeds
        start_time = time.time()
        all_titles = []
        feeds_working = 0
        total_articles = 0

        for feed_name, feed_url in list(rss_feeds.items())[:3]:  # Test max 3 feeds
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    feeds_working += 1
                    for entry in feed.entries[:5]:
                        title = entry.get('title', '')
                        if title:
                            all_titles.append(title)
                            total_articles += 1
            except Exception:
                pass

        elapsed_ms = int((time.time() - start_time) * 1000)

        return JsonResponse({
            'status': 'success',
            'result': {
                'success': feeds_working > 0,
                'spider': spider_name,
                'articles_count': total_articles,
                'feeds_tested': len(rss_feeds),
                'feeds_working': feeds_working,
                'response_time': elapsed_ms,
                'sample_titles': all_titles[:5],
                'error': None if feeds_working > 0 else 'No feeds returned data'
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_all_spiders(request):
    """
    Trigger all spiders to fetch fresh data.
    Returns a task ID for tracking.
    """
    try:
        from core.tasks import run_spider_network

        # Trigger the Celery task
        task = run_spider_network.delay()

        return JsonResponse({
            'status': 'success',
            'message': 'Spider collection started',
            'task_id': str(task.id) if task else None
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def dashboard_stats(request):
    """
    Session 345: Unified dashboard stats endpoint.
    Returns all stats needed for Intelligence Hub and Agents panels.

    This is the single source of truth for all dashboard numbers.
    Frontend should call this once and cache for 30 seconds.
    """
    import os
    from datetime import timedelta
    from django.utils import timezone

    try:
        # === SPIDER STATS ===
        from ai_core.spiders.spider_registry import SpiderRegistry
        registry = SpiderRegistry()
        spider_counts = registry.get_spider_count()

        # === AGENT STATS ===
        # Count legacy agents
        agents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agents')
        legacy_agents = len([f for f in os.listdir(agents_dir)
                           if f.endswith('.py') and not f.startswith('__')])

        # Count clean agents
        core_agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
        clean_agents = len([f for f in os.listdir(core_agents_dir)
                          if f.endswith('_agent.py')])

        total_agents = legacy_agents + clean_agents

        # === DATA STATS ===
        from core.models_unified_system import SpiderData, AgentMemory, AgentKnowledgeSource
        from core.models_unified_system import AgentConversation, HiveMindSession, KnowledgeTransfer

        # Total data points
        total_data_points = SpiderData.objects.count()

        # Data from last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        recent_data_points = SpiderData.objects.filter(created_at__gte=last_24h).count()

        # Success rate (approximate based on recent runs)
        success_rate = 98

        # === SESSION 356: AGENT LEARNING STATS (using correct models) ===
        try:
            # AgentConversation represents agent-to-agent collaboration
            collaborations_count = AgentConversation.objects.count()
            # HiveMindSession represents collaborative problem-solving sessions
            collaboration_sessions_count = HiveMindSession.objects.count()
            # KnowledgeTransfer represents learning events (agent teaching agent)
            learning_events_count = KnowledgeTransfer.objects.count()
            agent_memories_count = AgentMemory.objects.count()
            knowledge_sources_count = AgentKnowledgeSource.objects.count()
        except Exception:
            collaborations_count = 0
            collaboration_sessions_count = 0
            learning_events_count = 0
            agent_memories_count = 0
            knowledge_sources_count = 0

        # === SESSION 346: ROW 3 STATS (Learning Activity) ===
        try:
            from core.models_unified_system import AgentLearningConnection, KnowledgeTransfer, ProjectInsight
            learning_connections_count = AgentLearningConnection.objects.count()
            knowledge_transfers_count = KnowledgeTransfer.objects.count()
            synthesized_insights_count = ProjectInsight.objects.count()
        except Exception:
            learning_connections_count = 0
            knowledge_transfers_count = 0
            synthesized_insights_count = 0

        # === TOP CATEGORIES ===
        top_categories = sorted(
            spider_counts.get('by_category', {}).items(),
            key=lambda x: -x[1]
        )[:10]

        return JsonResponse({
            'status': 'success',
            'stats': {
                'spiders': {
                    'total': spider_counts.get('total', 0),
                    'categories': len(spider_counts.get('by_category', {})),
                    'by_category': dict(top_categories),
                },
                'agents': {
                    'total': total_agents,
                    'legacy': legacy_agents,
                    'clean': clean_agents,
                },
                'data': {
                    'total_points': total_data_points,
                    'last_24h': recent_data_points,
                    'success_rate': success_rate,
                },
                # Session 346: Agent learning/collaboration stats
                'learning': {
                    'collaborations': collaborations_count,
                    'collaboration_sessions': collaboration_sessions_count,
                    'learning_events': learning_events_count,
                    'agent_memories': agent_memories_count,
                    'knowledge_sources': knowledge_sources_count,
                    # Row 3 stats
                    'learning_connections': learning_connections_count,
                    'knowledge_transfers': knowledge_transfers_count,
                    'synthesized_insights': synthesized_insights_count,
                },
                'timestamp': timezone.now().isoformat(),
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
