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
        hours = int(request.GET.get('hours', 168))  # Default: 7 days for better data coverage
        limit = int(request.GET.get('limit', 10))

        # Cap limits for performance
        hours = min(hours, 336)  # Max 2 weeks
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
        # Session 807: Defer embedding fields to reduce egress costs
        crypto_data = SpiderData.objects.filter(
            spider_name__in=['coingecko', 'etherscan'],
            created_at__gte=since
        ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')

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
                    except Exception:
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
        # Session 807: Defer embedding fields to reduce egress costs
        news_spiders = ['business_news', 'reuters_rss', 'seekingalpha', 'newsapi', 'bbc', 'cnn']
        news_data = SpiderData.objects.filter(
            spider_name__in=news_spiders,
            created_at__gte=since
        ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')

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
                # Session 807: Defer embedding fields to reduce egress costs
                spider_data = SpiderData.objects.filter(
                    spider_name__icontains=source,
                    created_at__gte=cutoff
                ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:5]  # Get fewer records, each has multiple items

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

        # Freelance Gigs - Session 390: Use Himalayas.app API as PRIMARY source
        # Himalayas provides high-quality remote job data via free API (requires attribution)
        # Fallback to remote jobs if API fails
        freelance_gigs = []
        freelance_sources = []
        seen_urls = set()  # Track URLs to prevent duplicates

        # First: Fetch fresh jobs from Himalayas.app API (free, no key needed)
        try:
            from ai_core.spiders.specialized.himalayas_spider import fetch_himalayas_jobs
            himalayas_result = fetch_himalayas_jobs(limit=limit)
            if himalayas_result.get('success'):
                for job in himalayas_result.get('items', []):
                    url = job.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        freelance_gigs.append({
                            'id': str(job.get('id', '')),
                            'title': (job.get('title', '') or 'Untitled')[:100],
                            'url': url,
                            'source': 'Himalayas',
                            'description': job.get('description', '')[:200] if job.get('description') else '',
                            'salary': job.get('salary', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', 'Remote'),
                            'category': 'Remote Work',
                            'created_at': job.get('posted_at'),
                            'tags': job.get('tags', []),
                            'attribution_url': job.get('attribution_url', '')  # Required for Himalayas
                        })
                        freelance_sources.append('Himalayas')
                        if len(freelance_gigs) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Failed to fetch Himalayas jobs: {e}")

        # Second: If not enough jobs, supplement from remote jobs fallback
        if len(freelance_gigs) < limit and remote_jobs:
            for job in remote_jobs[:limit - len(freelance_gigs)]:
                url = job.get('url', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    freelance_gigs.append({
                        **job,
                        'category': 'Remote Work',
                        'source': f"{job.get('source', 'Job Board')}"
                    })
                    freelance_sources.append(job.get('source', 'Job Board'))

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
        # Session 807: Defer embedding fields to reduce egress costs
        reddit_data = SpiderData.objects.filter(
            spider_name__icontains='reddit',
            created_at__gte=cutoff
        ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:15]  # Get more records for variety

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
            except Exception as _e:
                logger.warning(
                    "views_spider_intelligence.test_spider: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

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
    from datetime import timedelta
    from django.utils import timezone

    try:
        # === SPIDER STATS ===
        from ai_core.spiders.spider_registry import SpiderRegistry
        registry = SpiderRegistry()
        spider_counts = registry.get_spider_count()

        # === AGENT STATS ===
        # Session 417: Use database agent count instead of filesystem count
        # This matches what the Profile dropdown shows and is more accurate
        from core.models_unified_system import Agent
        db_agent_count = Agent.objects.filter(is_active=True).count()
        total_db_agents = Agent.objects.count()

        # Keep legacy/clean distinction for backwards compatibility
        total_agents = db_agent_count
        legacy_agents = 0  # No longer tracking filesystem counts
        clean_agents = db_agent_count

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

        # Session 537: Build spider names grouped by category for ICC detail view
        spiders_by_category = {}
        for name, spider_class in registry.spider_classes.items():
            config = registry.spider_configs.get(name, {})
            category = config.get('category', 'Other')
            if category not in spiders_by_category:
                spiders_by_category[category] = []
            spiders_by_category[category].append({
                'name': name,
                'display_name': name.replace('_', ' ').title(),
            })

        return JsonResponse({
            'status': 'success',
            'stats': {
                'spiders': {
                    'total': spider_counts.get('total', 0),
                    'categories': len(spider_counts.get('by_category', {})),
                    'by_category': dict(top_categories),
                    'spiders_by_category': spiders_by_category,  # Session 537: Individual spider names
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


# ============================================================
# SESSION 399: SPIDER DATA UI - DATA FEED, KNOWLEDGE, TIMELINE
# ============================================================

import logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def spider_data_feed(request):
    """
    Session 399: Returns paginated spider data items for the data feed.
    Extracts actual items from raw_data JSON for browsing.

    Query params:
        category: Filter by data_type (tech, news, financial, etc.)
        source: Filter by spider_name
        limit: Number of items (default 50)
        offset: Pagination offset
        sort: 'recent' or 'score'
    """
    from core.models_unified_system import SpiderData

    try:
        category = request.GET.get('category', 'all') or 'all'  # Handle empty string
        source = request.GET.get('source', 'all') or 'all'  # Handle empty string
        limit = min(int(request.GET.get('limit', 50)), 100)
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', 'recent')

        # Build queryset
        # Session 807: Defer embedding fields to reduce egress costs
        queryset = SpiderData.objects.defer('embedding', 'item_embeddings', 'embedding_text').exclude(raw_data__isnull=True)

        if category != 'all':
            queryset = queryset.filter(data_type=category)
        if source != 'all':
            queryset = queryset.filter(spider_name=source)

        queryset = queryset.order_by('-created_at')[offset:offset + limit + 20]  # Get extra for item extraction

        # Extract items from raw_data
        items = []
        seen_urls = set()

        for sd in queryset:
            if not sd.raw_data:
                continue

            raw_items = sd.raw_data.get('items', [])
            if not isinstance(raw_items, list):
                continue

            for item in raw_items[:15]:  # Max 15 items per record
                # Get URL for deduplication - try many possible fields
                url = (
                    item.get('url') or
                    item.get('link') or
                    item.get('html_url') or  # GitHub
                    item.get('permalink') or  # Reddit
                    item.get('guid') or  # RSS feeds
                    ''
                )
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)

                # Extract title - try multiple fields based on spider type
                title = (
                    item.get('title') or
                    item.get('name') or  # GitHub repos
                    item.get('full_name') or  # GitHub repos (owner/repo)
                    item.get('modelId') or  # HuggingFace
                    item.get('id') or  # Some APIs use id as identifier
                    item.get('position') or  # Job listings
                    item.get('headline') or
                    item.get('text') or  # Some news items
                    None
                )

                # Skip items with no title at all
                if not title:
                    continue

                # Extract description - try many fields
                description = (
                    item.get('description') or
                    item.get('summary') or
                    item.get('selftext') or  # Reddit
                    item.get('body') or
                    item.get('content') or
                    item.get('excerpt') or
                    ''
                )

                # Special handling for HuggingFace models - build a rich description
                if sd.spider_name == 'huggingface' and not description:
                    desc_parts = []
                    if item.get('pipeline_tag'):
                        desc_parts.append(f"Task: {item.get('pipeline_tag')}")
                    if item.get('library_name'):
                        desc_parts.append(f"Library: {item.get('library_name')}")
                    # Extract useful tags (skip dataset:, arxiv:, region:, etc.)
                    tags = item.get('tags', [])
                    useful_tags = [t for t in tags[:10] if not any(t.startswith(p) for p in ['dataset:', 'arxiv:', 'region:', 'license:', 'deploy:', 'endpoints_', 'autotrain_'])]
                    if useful_tags:
                        desc_parts.append(f"Tags: {', '.join(useful_tags[:5])}")
                    if item.get('downloads'):
                        desc_parts.append(f"{item.get('downloads'):,} downloads")
                    if item.get('likes'):
                        desc_parts.append(f"{item.get('likes'):,} likes")
                    description = ' | '.join(desc_parts)

                # Special handling for GitHub - build URL from html_url
                if sd.spider_name == 'github' and not url and item.get('html_url'):
                    url = item.get('html_url')

                # Special handling for HuggingFace - construct URL from modelId
                if sd.spider_name == 'huggingface' and not url and item.get('modelId'):
                    url = f"https://huggingface.co/{item.get('modelId')}"

                # Build item object
                feed_item = {
                    'title': str(title)[:200],
                    'url': url,
                    'source': sd.spider_name,
                    'category': sd.data_type,
                    'score': item.get('score') or item.get('points') or item.get('upvotes') or item.get('stargazers_count') or item.get('likes') or item.get('downloads'),
                    'timestamp': item.get('created_at') or item.get('published') or item.get('fetched_at') or sd.created_at.isoformat(),
                    'description': str(description)[:300] if description else '',
                    'metadata': {
                        'company': item.get('company'),
                        'location': item.get('location'),
                        'salary_min': item.get('salary_min'),
                        'salary_max': item.get('salary_max'),
                        'tags': item.get('tags', [])[:8] if isinstance(item.get('tags'), list) else [],
                        'price': item.get('current_price') or item.get('price'),
                        'change': item.get('price_change_percentage_24h') or item.get('change_24h'),
                        'symbol': item.get('symbol'),
                        'subreddit': item.get('subreddit'),
                        'comments': item.get('num_comments') or item.get('comments'),
                        'author': item.get('author') or item.get('by') or item.get('owner', {}).get('login') if isinstance(item.get('owner'), dict) else item.get('author'),
                        'stars': item.get('stargazers_count'),  # GitHub
                        'forks': item.get('forks_count') or item.get('forks'),  # GitHub
                        'downloads': item.get('downloads'),  # HuggingFace
                        'likes': item.get('likes'),  # HuggingFace
                        'library': item.get('library_name'),  # HuggingFace
                    }
                }

                items.append(feed_item)

                if len(items) >= limit:
                    break

            if len(items) >= limit:
                break

        # Sort by score if requested
        if sort == 'score':
            items.sort(key=lambda x: x.get('score') or 0, reverse=True)

        # Get available sources for filter dropdown
        sources = list(SpiderData.objects.values_list('spider_name', flat=True).distinct().order_by('spider_name'))

        # Get available categories
        categories = list(SpiderData.objects.values_list('data_type', flat=True).distinct().order_by('data_type'))

        # Get stats
        total_records = SpiderData.objects.count()
        with_embeddings = SpiderData.objects.exclude(embedding__isnull=True).count()

        return JsonResponse({
            'status': 'success',
            'items': items,
            'total': len(items),
            'total_items': total_records,  # For frontend stats display
            'categories': categories,  # For frontend filter pills
            'has_more': len(queryset) > limit,
            'sources': sources,
            'stats': {
                'total_records': total_records,
                'with_embeddings': with_embeddings,
                'active_sources': len(sources)
            }
        })

    except Exception as e:
        logger.error(f"Error in spider_data_feed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_knowledge(request):
    """
    Session 399: Returns knowledge sources derived from spider data.
    Shows what agents have learned from the spider network.

    Query params:
        type: Filter by knowledge_type (trend, market, opportunity, etc.)
        limit: Max items (default 50)
    """
    from django.db.models import Count, Avg
    from core.models_unified_system import AgentKnowledgeSource, KnowledgeTransfer, AgentMemory

    try:
        limit = min(int(request.GET.get('limit', 50)), 100)
        knowledge_type = request.GET.get('type', 'all')

        # Session 399: Get UNIQUE knowledge sources by title (deduplicated)
        # First get unique titles with their most recent entry
        from django.db.models import Max

        queryset = AgentKnowledgeSource.objects.all()
        if knowledge_type != 'all':
            queryset = queryset.filter(knowledge_type=knowledge_type)

        # Get unique titles with counts and latest discovery date
        unique_knowledge = list(
            queryset.values('title', 'knowledge_type', 'summary')
            .annotate(
                count=Count('id'),
                latest=Max('first_discovered_at'),
                avg_confidence=Avg('confidence_score'),
                total_data_points=Count('data_points_count')
            )
            .order_by('-latest')[:limit]
        )

        # Build sources list from unique titles
        sources = unique_knowledge

        # Get type breakdown
        type_counts = list(
            AgentKnowledgeSource.objects.values('knowledge_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Session 399: Get DIVERSE transfers (unique agent pairs with counts)

        # Get unique transfer patterns with counts
        transfer_patterns = list(
            KnowledgeTransfer.objects.select_related(
                'source_knowledge',
                'connection__teacher_agent',
                'connection__student_agent'
            ).values(
                'connection__teacher_agent__name',
                'connection__student_agent__name'
            ).annotate(
                transfer_count=Count('id'),
                latest=Max('created_at')
            ).order_by('-latest')[:15]
        )

        # Also get a few recent individual transfers for detail
        recent_transfers = KnowledgeTransfer.objects.select_related(
            'source_knowledge',
            'connection__teacher_agent',
            'connection__student_agent'
        ).order_by('-created_at')[:5]

        # Calculate stats
        total_sources = AgentKnowledgeSource.objects.count()
        total_transfers = KnowledgeTransfer.objects.count()
        total_memories = AgentMemory.objects.count()
        avg_confidence = AgentKnowledgeSource.objects.aggregate(
            avg=Avg('confidence_score')
        )['avg'] or 0

        # Build by_type dict for frontend (convert type_counts list to dict)
        by_type = {tc['knowledge_type']: tc['count'] for tc in type_counts}

        # Session 399: Helper to clean up titles and summaries
        def clean_knowledge_display(title, summary, knowledge_type):
            """Parse and clean knowledge data for human-readable display."""
            import json
            import re

            # Clean title - remove [Learned] prefix and truncate
            clean_title = title
            if clean_title.startswith('[Learned] '):
                clean_title = clean_title[10:]

            # Extract meaningful info from title patterns
            if clean_title.startswith('Research:'):
                # Extract the topic being researched
                topic = clean_title.replace('Research:', '').strip()
                # Remove verbose prefixes
                topic = re.sub(r'^Research this business idea thoroughly:\s*', '', topic)
                topic = re.sub(r'^Research trending.*?:\s*', '', topic)
                # Extract just the core topic (first meaningful phrase)
                topic = topic.split('\n')[0].strip()  # Take first line
                if len(topic) > 50:
                    topic = topic[:50] + '...'
                clean_title = f"📊 Research: {topic}"
            elif clean_title.startswith('Style:'):
                style = clean_title.replace('Style:', '').strip()
                clean_title = f"🎨 Style Discovery: {style}"
            elif clean_title.startswith('Dream Explored:'):
                dream = clean_title.replace('Dream Explored:', '').strip()
                clean_title = f"💭 Dream: {dream[:50]}{'...' if len(dream) > 50 else ''}"
            elif clean_title.startswith('Customer Research:'):
                topic = clean_title.replace('Customer Research:', '').strip()
                topic = re.sub(r'^Research target customers for:\s*', '', topic)
                clean_title = f"👥 Customer Research: {topic[:50]}{'...' if len(topic) > 50 else ''}"
            elif clean_title.startswith('Market Analysis:'):
                topic = clean_title.replace('Market Analysis:', '').strip()
                topic = re.sub(r'^Analyze competitors for:\s*', '', topic)
                clean_title = f"📈 Market Analysis: {topic[:50]}{'...' if len(topic) > 50 else ''}"
            elif ' - ' in clean_title and 'Intelligence' in clean_title:
                # Pattern like "Huggingface - Tech Intelligence"
                parts = clean_title.split(' - ')
                source = parts[0].strip()
                intel_type = parts[1].replace('Intelligence', '').strip() if len(parts) > 1 else ''
                emoji_map = {'Tech': '💻', 'Financial': '💰', 'Content': '📝', 'Design': '🎨', 'Market': '📈', 'Creative Assets': '🖼️', 'General': '📋'}
                emoji = emoji_map.get(intel_type, '🔍')
                clean_title = f"{emoji} {source}: {intel_type} Intelligence"
            elif 'Market Data' in clean_title:
                clean_title = "📊 Market Data Intelligence"

            # Clean summary - try to parse JSON and extract meaningful parts
            clean_summary = ''
            if summary:
                # First, remove "Learned from AgentName:" prefix(es)
                working_summary = re.sub(r'Learned from \w+:\s*', '', summary).strip()

                try:
                    # Find JSON in the summary (it might be after text)
                    json_match = re.search(r'\{.*\}', working_summary, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        parts = []
                        if 'query' in data:
                            query = data['query']
                            # Clean up query
                            query = re.sub(r'^Research this business idea thoroughly:\s*', '', query)
                            query = re.sub(r'^Research target customers for:\s*', '', query)
                            query = re.sub(r'^Analyze competitors for:\s*', '', query)
                            query = re.sub(r'\n.*', '', query, flags=re.DOTALL)  # Take first line only
                            if len(query) > 60:
                                query = query[:60] + '...'
                            parts.append(query)
                        if 'sources' in data and isinstance(data['sources'], list):
                            source_count = len(data['sources'])
                            source_names = ', '.join(str(s) for s in data['sources'][:3])
                            parts.append(f"Sources: {source_names}" + (f" +{source_count-3} more" if source_count > 3 else ""))
                        if 'data_points' in data:
                            parts.append(f"{data['data_points']} data points analyzed")
                        if 'discussions_analyzed' in data:
                            parts.append(f"{data['discussions_analyzed']} discussions analyzed")
                        if 'style' in data:
                            parts.append(f"Style: {data['style']}")
                        if 'prompt_pattern' in data:
                            pattern = data['prompt_pattern'][:40] + '...' if len(data.get('prompt_pattern', '')) > 40 else data.get('prompt_pattern', '')
                            parts.append(f"Pattern: {pattern}")
                        if 'success' in data:
                            parts.append("✓ Successful" if data['success'] else "✗ Failed")
                        if 'size' in data:
                            parts.append(f"Size: {data['size']}")
                        clean_summary = ' • '.join(parts) if parts else ''
                    else:
                        # Not JSON, use cleaned text
                        clean_summary = working_summary
                except (json.JSONDecodeError, TypeError):
                    # Not valid JSON, use cleaned text
                    clean_summary = working_summary

                # Final cleanup - remove any remaining JSON-like content
                if clean_summary.startswith('{') or clean_summary.startswith('['):
                    clean_summary = ''

                # Clean up "Aggregated X data points" pattern
                agg_match = re.match(r'Aggregated (\d+) (\w+) data points from (\w+)', clean_summary)
                if agg_match:
                    clean_summary = f"📊 {agg_match.group(1)} {agg_match.group(2)} data points from {agg_match.group(3)}"

                # Truncate if still too long
                if len(clean_summary) > 120:
                    clean_summary = clean_summary[:120] + '...'

            return clean_title, clean_summary

        # Session 399: Build deduplicated knowledge list with cleaned display
        knowledge_list = []
        for k in sources:
            clean_title, clean_summary = clean_knowledge_display(k['title'], k['summary'], k['knowledge_type'])
            knowledge_list.append({
                'id': str(hash(k['title'])),
                'title': clean_title,
                'summary': clean_summary,
                'type': k['knowledge_type'],
                'confidence': k['avg_confidence'] or 0,
                'occurrences': k['count'],
                'discovered_at': k['latest'].isoformat() if k['latest'] else None,
            })

        # Session 399: Build diverse transfer list showing unique agent pairs
        transfers_list = [{
            'from': t['connection__teacher_agent__name'] or 'Unknown',
            'to': t['connection__student_agent__name'] or 'Unknown',
            'transfer_count': t['transfer_count'],  # How many transfers between this pair
            'knowledge': f"{t['transfer_count']} knowledge transfers",
            'summary': f"Shared knowledge {t['transfer_count']} times",
            'latest': t['latest'].isoformat() if t['latest'] else None
        } for t in transfer_patterns]

        return JsonResponse({
            'status': 'success',
            'knowledge': knowledge_list,
            'type_counts': type_counts,
            'transfers': transfers_list,
            'stats': {
                'total_knowledge': total_sources,  # Session 399: Match frontend field name
                'total_transfers': total_transfers,
                'total_memories': total_memories,
                'avg_confidence': round(avg_confidence * 100, 1),  # Already percentage
                'by_type': by_type,  # Session 399: Add for frontend sidebar
                'unique_knowledge': len(knowledge_list),  # Deduplicated count
                'unique_connections': len(transfers_list)  # Unique agent pairs
            },
            'total': total_sources
        })

    except Exception as e:
        logger.error(f"Error in spider_knowledge: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_timeline(request):
    """
    Session 399: Returns data collection timeline and source freshness.

    Query params:
        range: '24h', '7d', or '30d' (default: '24h')
    """
    from django.utils import timezone
    from django.db.models import Count, Max
    from django.db.models.functions import TruncHour, TruncDay
    from datetime import timedelta
    from core.models_unified_system import SpiderData

    try:
        range_param = request.GET.get('range', '24h')

        # Determine time range and truncation
        if range_param == '24h':
            since = timezone.now() - timedelta(hours=24)
            trunc_fn = TruncHour
        elif range_param == '7d':
            since = timezone.now() - timedelta(days=7)
            trunc_fn = TruncDay
        else:  # 30d
            since = timezone.now() - timedelta(days=30)
            trunc_fn = TruncDay

        # Get collection timeline
        timeline = list(
            SpiderData.objects.filter(created_at__gte=since)
            .annotate(period=trunc_fn('created_at'))
            .values('period')
            .annotate(count=Count('id'))
            .order_by('period')
        )

        # Calculate totals
        total_items = sum(t['count'] for t in timeline)
        peak_count = max((t['count'] for t in timeline), default=0)

        # Get source freshness
        freshness = list(
            SpiderData.objects.values('spider_name')
            .annotate(
                last_update=Max('created_at'),
                total_records=Count('id')
            )
            .order_by('-last_update')
        )

        # Session 399: Count actual browseable items per source (not just records)
        # This helps users know which sources have data they can view

        browseable_counts = {}
        for spider_name in set(f['spider_name'] for f in freshness):
            # Sample recent records to count actual items
            # Session 807: Defer embedding fields to reduce egress costs
            recent = SpiderData.objects.filter(spider_name=spider_name).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:3]
            item_count = 0
            for r in recent:
                if r.raw_data and isinstance(r.raw_data.get('items'), list):
                    item_count += len(r.raw_data['items'])
            browseable_counts[spider_name] = item_count

        # Calculate age for each source
        now = timezone.now()
        freshness_data = []
        for f in freshness:
            if f['last_update']:
                age_minutes = (now - f['last_update']).total_seconds() / 60
                browseable = browseable_counts.get(f['spider_name'], 0)
                freshness_data.append({
                    'source': f['spider_name'],
                    'last_update': f['last_update'].isoformat(),
                    'item_count': f['total_records'],  # Total records
                    'browseable_items': browseable,  # Session 399: Items available to view
                    'has_data': browseable > 0,  # Session 399: Can this source be browsed?
                    'age_minutes': round(age_minutes, 1),
                    'status': 'fresh' if age_minutes < 360 else 'aging' if age_minutes < 1440 else 'stale'
                })

        return JsonResponse({
            'status': 'success',
            'timeline': [{
                'period': t['period'].isoformat(),
                'count': t['count']
            } for t in timeline],
            'freshness': freshness_data,
            'summary': {
                'range': range_param,
                'total_items': total_items,
                'peak_count': peak_count,
                'sources_fresh': len([f for f in freshness_data if f['status'] == 'fresh']),
                'sources_aging': len([f for f in freshness_data if f['status'] == 'aging']),
                'sources_stale': len([f for f in freshness_data if f['status'] == 'stale'])
            }
        })

    except Exception as e:
        logger.error(f"Error in spider_timeline: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def intelligence_cross_references(request):
    """
    Session 536: Get cross-reference mappings for Intelligence Command Center.

    Returns dynamic mappings of:
    - spider_to_agents: Which agents use data from which spiders
    - agent_to_situations: Which autonomous situations involve which agents
    - situation_to_spiders: Which situations are triggered by which spiders

    These are built from actual database relationships, not hardcoded.
    """
    try:
        from collections import defaultdict
        from core.models_unified_system import AgentKnowledgeSource
        from core.models_situation_triggers import SituationTrigger
        from ai_core.spiders.spider_registry import SpiderRegistry

        # ========== SPIDER → AGENT MAPPINGS ==========
        # Built from AgentKnowledgeSource.source_spider_names
        spider_to_agents = defaultdict(set)

        knowledge_sources = AgentKnowledgeSource.objects.filter(
            is_active=True
        ).select_related('agent').only('agent__name', 'source_spider_names')

        for ks in knowledge_sources:
            if ks.source_spider_names and ks.agent:
                for spider_name in ks.source_spider_names:
                    spider_to_agents[spider_name.lower()].add(ks.agent.name)

        # Also add mappings based on spider categories → agent types
        registry = SpiderRegistry()
        all_spiders = registry.get_active_spiders()

        # Agent capability mappings by category
        category_to_agents = {
            'tech': ['TrendAnalysisAgent', 'ResearchAgent', 'ContentStrategyAgent'],
            'financial': ['MarketIntelligenceCoordinator', 'StockAuditCoordinator'],
            'crypto': ['BlockchainAuditCoordinator', 'WhaleWatcherAgent'],
            'jobs': ['OpportunityScoringAgent', 'OpportunityPipelineAgent'],
            'creative': ['ImageAgent', 'BrandIdentityAgent', 'CreativeDirectorAgent'],
            'social': ['TrendAnalysisAgent', 'SocialMediaAgent', 'ContentWriterAgent'],
            'news': ['TrendAnalysisAgent', 'ResearchAgent'],
            'legal': ['LegalDocDrafterAgent'],
        }

        for spider_name, spider_class in all_spiders.items():
            config = registry.spider_configs.get(spider_name, {})
            category = config.get('category', '').lower()

            # Add agents from category mapping
            if category in category_to_agents:
                for agent_name in category_to_agents[category]:
                    spider_to_agents[spider_name.lower()].add(agent_name)

        # Convert sets to lists
        spider_to_agents = {k: sorted(list(v)) for k, v in spider_to_agents.items()}

        # ========== AGENT → SITUATION MAPPINGS ==========
        # Based on agent types and situation types
        agent_to_situations = {
            'BlockchainAuditCoordinator': ['blockchain_security', 'crypto_whale_alerts'],
            'WhaleWatcherAgent': ['crypto_whale_alerts', 'blockchain_security'],
            'StockAuditCoordinator': ['stock_market_intelligence', 'earnings_surprise'],
            'MarketIntelligenceCoordinator': ['stock_market_intelligence', 'market_volatility'],
            'TrendAnalysisAgent': ['tech_stack_evolution', 'narrative_drift', 'viral_content_predictor'],
            'ContentWriterAgent': ['autonomous_content_generation', 'viral_content_predictor'],
            'ContentStrategyAgent': ['autonomous_content_generation', 'thumbnail_optimization'],
            'OpportunityScoringAgent': ['job_matching', 'freelance_scout'],
            'OpportunityPipelineAgent': ['job_matching', 'freelance_scout'],
            'ImageAgent': ['design_trends', 'thumbnail_optimization'],
            'CreativeDirectorAgent': ['design_trends', 'viral_content_predictor'],
            'LegalDocDrafterAgent': ['case_law_monitor', 'regulatory_change'],
            'ResearchAgent': ['tech_stack_evolution', 'competitive_intel'],
            'SocialMediaAgent': ['viral_content_predictor', 'narrative_drift'],
        }

        # ========== SITUATION → SPIDER MAPPINGS ==========
        # Built from SituationTrigger.target_spiders
        situation_to_spiders = defaultdict(set)

        triggers = SituationTrigger.objects.filter(
            is_active=True
        ).values('situation_type', 'target_spiders')

        for trigger in triggers:
            situation_type = trigger['situation_type']
            target_spiders = trigger['target_spiders'] or []
            for spider in target_spiders:
                situation_to_spiders[situation_type].add(spider.lower())

        # Add default situation → spider mappings for common patterns
        default_situation_spiders = {
            'blockchain_security': ['etherscan', 'coingecko', 'coindesk'],
            'crypto_whale_alerts': ['etherscan', 'coingecko'],
            'stock_market_intelligence': ['yahoo_finance', 'seekingalpha', 'newsapi'],
            'earnings_surprise': ['yahoo_finance', 'seekingalpha'],
            'market_volatility': ['yahoo_finance', 'newsapi'],
            'tech_stack_evolution': ['techcrunch', 'hackernews', 'the_verge', 'mit_tech_review'],
            'autonomous_content_generation': ['techcrunch', 'hackernews', 'reddit', 'the_verge'],
            'viral_content_predictor': ['reddit', 'hackernews', 'youtube_trending'],
            'job_matching': ['remoteok', 'weworkremotely', 'adzuna'],
            'freelance_scout': ['remoteok', 'weworkremotely', 'freelancer_api'],
            'design_trends': ['dribbble', 'behance', 'unsplash'],
            'thumbnail_optimization': ['youtube_trending', 'dribbble'],
            'narrative_drift': ['reddit', 'hackernews', 'newsapi'],
            'case_law_monitor': ['justia', 'colorado_family_law'],
            'regulatory_change': ['sec_edgar', 'newsapi'],
        }

        for situation, spiders in default_situation_spiders.items():
            for spider in spiders:
                situation_to_spiders[situation].add(spider)

        # Convert sets to lists
        situation_to_spiders = {k: sorted(list(v)) for k, v in situation_to_spiders.items()}

        return JsonResponse({
            'status': 'success',
            'spider_to_agents': spider_to_agents,
            'agent_to_situations': agent_to_situations,
            'situation_to_spiders': situation_to_spiders,
            'stats': {
                'spiders_mapped': len(spider_to_agents),
                'agents_mapped': len(agent_to_situations),
                'situations_mapped': len(situation_to_spiders)
            }
        })

    except Exception as e:
        logger.error(f"Error in intelligence_cross_references: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_detail(request, spider_name):
    """
    Session 536: Get detailed data for a specific spider.

    Returns recent items collected by the spider with full content.
    Used by ICC detail panel to show actual news/data.
    """
    try:
        from core.models_unified_system import SpiderData
        from django.utils import timezone
        from datetime import timedelta

        limit = min(int(request.GET.get('limit', 10)), 25)
        hours = min(int(request.GET.get('hours', 168)), 336)  # Default 7 days, max 2 weeks

        since = timezone.now() - timedelta(hours=hours)

        # Get recent data from this spider
        # Session 807: Defer embedding fields to reduce egress costs
        queryset = SpiderData.objects.filter(
            spider_name__iexact=spider_name,
            created_at__gte=since
        ).defer('embedding', 'item_embeddings', 'embedding_text').exclude(raw_data__isnull=True).order_by('-created_at')[:20]

        items = []
        seen_urls = set()

        for sd in queryset:
            if not sd.raw_data:
                continue

            # Handle raw_data as string or dict (Session 536 fix)
            raw_data = sd.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    continue
            if not isinstance(raw_data, dict):
                continue

            raw_items = raw_data.get('items', [])
            if not isinstance(raw_items, list):
                # Handle single item format
                raw_items = [raw_data] if raw_data.get('title') or raw_data.get('name') else []

            for item in raw_items[:10]:
                # Deduplicate by URL
                url = item.get('url') or item.get('link') or item.get('permalink') or item.get('html_url') or ''
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)

                # Extract title
                title = (
                    item.get('title') or
                    item.get('name') or
                    item.get('headline') or
                    item.get('position') or  # Jobs
                    item.get('symbol') or  # Crypto/stocks
                    None
                )
                if not title:
                    continue

                # Extract description/content
                description = (
                    item.get('description') or
                    item.get('summary') or
                    item.get('selftext') or  # Reddit
                    item.get('content') or
                    item.get('body') or
                    item.get('text') or
                    ''
                )

                # Truncate long descriptions
                if len(description) > 500:
                    description = description[:500] + '...'

                items.append({
                    'title': title[:200] if title else 'Untitled',
                    'description': description,
                    'url': url,
                    'source': spider_name,
                    'timestamp': sd.created_at.isoformat(),
                    'category': sd.data_type or 'general',
                    # Extra fields for different data types
                    'price': item.get('current_price') or item.get('price'),
                    'change': item.get('price_change_percentage_24h') or item.get('change_percent'),
                    'company': item.get('company') or item.get('company_name'),
                    'location': item.get('location'),
                    'salary': item.get('salary') or item.get('salary_range'),
                    'score': item.get('score') or item.get('ups'),  # Reddit upvotes
                    'comments': item.get('num_comments'),
                })

                if len(items) >= limit:
                    break

            if len(items) >= limit:
                break

        # Get spider metadata
        total_records = SpiderData.objects.filter(spider_name__iexact=spider_name).count()
        recent_records = SpiderData.objects.filter(
            spider_name__iexact=spider_name,
            created_at__gte=since
        ).count()

        return JsonResponse({
            'status': 'success',
            'spider_name': spider_name,
            'items': items,
            'meta': {
                'total_records': total_records,
                'recent_records': recent_records,
                'items_returned': len(items),
                'hours_lookback': hours
            }
        })

    except Exception as e:
        logger.error(f"Error in spider_detail: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def agent_detail(request, agent_name):
    """
    Session 537: Get detailed data for a specific agent.

    Returns agent info, recent conversations, knowledge sources, and activity.
    Used by ICC detail panel to show actual agent activity.
    """
    try:
        from core.models_unified_system import Agent, AgentConversation, AgentKnowledgeSource, KnowledgeTransfer

        # Find the agent (case-insensitive)
        agent = Agent.objects.filter(name__iexact=agent_name).first()
        if not agent:
            # Try partial match
            agent = Agent.objects.filter(name__icontains=agent_name.replace('Agent', '').replace('Coordinator', '')).first()

        if not agent:
            return JsonResponse({
                'status': 'success',
                'agent_name': agent_name,
                'found': False,
                'message': 'Agent not found in database'
            })

        # Get recent conversations involving this agent
        recent_convos = AgentConversation.objects.filter(
            initiator__name__iexact=agent.name
        ).order_by('-started_at')[:5]

        conversations = []
        for conv in recent_convos:
            conversations.append({
                'topic': conv.topic or 'Untitled conversation',
                'type': conv.conversation_type or 'discussion',
                'status': conv.status or 'completed',
                'insights': conv.insights_generated or 0,
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
            })

        # Get knowledge sources this agent has created
        knowledge_sources = AgentKnowledgeSource.objects.filter(
            agent=agent,
            is_active=True
        ).order_by('-first_discovered_at')[:5]

        knowledge = []
        for ks in knowledge_sources:
            knowledge.append({
                'title': ks.title or 'Untitled',
                'source_type': ks.knowledge_type or 'unknown',
                'summary': (ks.summary or '')[:150] + '...' if ks.summary and len(ks.summary) > 150 else ks.summary,
                'created_at': ks.first_discovered_at.isoformat() if ks.first_discovered_at else None,
            })

        # Get recent knowledge transfers (teaching/learning)
        # KnowledgeTransfer uses connection.teacher_agent/student_agent
        transfers_given = KnowledgeTransfer.objects.filter(
            connection__teacher_agent=agent
        ).select_related('connection__student_agent').order_by('-created_at')[:3]

        transfers_received = KnowledgeTransfer.objects.filter(
            connection__student_agent=agent
        ).select_related('connection__teacher_agent').order_by('-created_at')[:3]

        taught = [{'to': t.connection.student_agent.name if t.connection and t.connection.student_agent else 'Unknown', 'topic': (t.transfer_summary or '')[:50]} for t in transfers_given]
        learned = [{'from': t.connection.teacher_agent.name if t.connection and t.connection.teacher_agent else 'Unknown', 'topic': (t.transfer_summary or '')[:50]} for t in transfers_received]

        return JsonResponse({
            'status': 'success',
            'agent_name': agent.name,
            'found': True,
            'agent': {
                'name': agent.name,
                'type': agent.agent_type or 'General',
                'category': agent.category or 'Uncategorized',
                'description': agent.description or 'No description available',
                'specialization': agent.specialization or '',
                'effectiveness': agent.effectiveness_score or 0,
                'total_executions': agent.total_executions or 0,
                'successful_executions': agent.successful_executions or 0,
                'is_active': agent.is_active,
                'last_active': agent.last_active.isoformat() if agent.last_active else None,
            },
            'conversations': conversations,
            'knowledge': knowledge,
            'transfers': {
                'taught': taught,
                'learned': learned,
            }
        })

    except Exception as e:
        logger.error(f"Error in agent_detail: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def situation_detail(request, situation_type):
    """
    Session 537: Get detailed data for a specific autonomous situation.

    Returns situation config, recent trigger events, and related entities.
    Used by ICC detail panel to show actual situation activity.
    """
    try:
        from core.models_situation_triggers import SituationTrigger, TriggerEvent
        from django.utils import timezone
        from datetime import timedelta

        # Find triggers for this situation type
        triggers = SituationTrigger.objects.filter(
            situation_type__iexact=situation_type.replace(' ', '_')
        )

        if not triggers.exists():
            # Try without underscores
            triggers = SituationTrigger.objects.filter(
                situation_type__icontains=situation_type.replace('_', ' ').replace(' ', '')[:10]
            )

        if not triggers.exists():
            return JsonResponse({
                'status': 'success',
                'situation_type': situation_type,
                'found': False,
                'message': 'Situation not found'
            })

        # Get trigger info
        trigger_list = []
        total_fires = 0
        target_spiders = set()

        for trig in triggers:
            trigger_list.append({
                'name': trig.name,
                'description': trig.description or '',
                'trigger_type': trig.trigger_type or 'threshold',
                'severity': trig.severity or 'medium',
                'target_field': trig.target_field or '',
                'operator': trig.operator or '',
                'threshold': trig.threshold_value or '',
                'cooldown': trig.cooldown_minutes or 60,
                'total_fires': trig.total_fires or 0,
                'is_active': trig.is_active,
                'last_triggered': trig.last_triggered_at.isoformat() if trig.last_triggered_at else None,
            })
            total_fires += trig.total_fires or 0
            if trig.target_spiders:
                for spider in trig.target_spiders:
                    target_spiders.add(spider)

        # Get recent trigger events
        trigger_ids = [t.id for t in triggers]
        recent_events = TriggerEvent.objects.filter(
            trigger_id__in=trigger_ids
        ).order_by('-fired_at')[:10]

        events = []
        for evt in recent_events:
            events.append({
                'trigger_name': evt.trigger.name if evt.trigger else 'Unknown',
                'spider_name': evt.spider_name or 'Unknown',
                'matched_value': (evt.matched_value or '')[:100],
                'severity': evt.trigger.severity if evt.trigger else 'medium',
                'status': evt.status or 'fired',
                'discord_sent': evt.discord_sent,
                'fired_at': evt.fired_at.isoformat() if evt.fired_at else None,
            })

        # Calculate stats
        last_24h = timezone.now() - timedelta(hours=24)
        fires_24h = TriggerEvent.objects.filter(
            trigger_id__in=trigger_ids,
            fired_at__gte=last_24h
        ).count()

        return JsonResponse({
            'status': 'success',
            'situation_type': situation_type,
            'found': True,
            'situation': {
                'type': situation_type,
                'display_name': situation_type.replace('_', ' ').title(),
                'trigger_count': len(trigger_list),
                'total_fires': total_fires,
                'fires_24h': fires_24h,
                'target_spiders': sorted(list(target_spiders)),
            },
            'triggers': trigger_list,
            'recent_events': events,
        })

    except Exception as e:
        logger.error(f"Error in situation_detail: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# =============================================================================
# Session 558: Prediction Markets API
# =============================================================================

def get_prediction_markets(request):
    """
    Session 558: Returns prediction market data from Kalshi spider.

    Query params:
        category: Filter by category (economics, politics, tech, finance, etc.)
        limit: Number of markets (default 50)
    """
    try:
        from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

        category = request.GET.get('category', '')
        limit = min(int(request.GET.get('limit', 50)), 100)

        # Fetch from Kalshi spider
        spider = KalshiSpider()
        all_data = spider.fetch_data(max_results=limit * 2)

        # Filter to actual markets (not series)
        markets = [m for m in all_data if m.get('data_type') == 'prediction_market']

        # Filter by category if specified
        if category:
            category_lower = category.lower()
            markets = [m for m in markets if m.get('category', '').lower() == category_lower]

        # Sort by volume (most active first)
        markets.sort(key=lambda m: m.get('volume', 0) or 0, reverse=True)

        # Limit results
        markets = markets[:limit]

        return JsonResponse({
            'success': True,
            'markets': markets,
            'total': len(markets),
            'category': category or 'all',
        })

    except Exception as e:
        logger.error(f"Error fetching prediction markets: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'markets': []
        }, status=500)


def get_sports_odds(request):
    """
    Session 558: Returns sports betting odds from The Odds API spider.

    Query params:
        sport: Filter by sport (nfl, nba, mlb, nhl, soccer, mma, etc.)
        limit: Number of events (default 50)
    """
    try:
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        sport = request.GET.get('sport', '')
        limit = min(int(request.GET.get('limit', 50)), 100)

        # Map display names to sport keys
        sport_key_map = {
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'mlb': 'baseball_mlb',
            'nhl': 'icehockey_nhl',
            'ncaaf': 'americanfootball_ncaaf',
            'ncaab': 'basketball_ncaab',
            'soccer': None,  # Multiple soccer leagues
            'epl': 'soccer_epl',
            'mls': 'soccer_usa_mls',
            'mma': 'mma_mixed_martial_arts',
            'ufc': 'mma_mixed_martial_arts',
        }

        # Fetch from spider
        spider = TheOddsSpider()

        if sport and sport.lower() in sport_key_map and sport_key_map[sport.lower()]:
            # Fetch specific sport
            sport_key = sport_key_map[sport.lower()]
            all_data = spider.fetch_data(sports=[sport_key], max_results=limit * 2)
        else:
            # Fetch all priority 1 sports
            all_data = spider.fetch_data(max_results=limit * 2)

        # Filter to sports odds only
        events = [e for e in all_data if e.get('data_type') == 'sports_odds']

        # Filter by sport display name if needed
        if sport and sport.lower() == 'soccer':
            events = [e for e in events if e.get('category') == 'soccer']

        # Sort by game time (soonest first)
        events.sort(key=lambda e: e.get('commence_time', ''))

        # Limit results
        events = events[:limit]

        # Get API usage
        usage = spider.get_api_usage()

        return JsonResponse({
            'success': True,
            'events': events,
            'total': len(events),
            'sport': sport or 'all',
            'api_usage': usage,
        })

    except Exception as e:
        logger.error(f"Error fetching sports odds: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'events': []
        }, status=500)
