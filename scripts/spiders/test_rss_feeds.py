# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test RSS Feeds and Public APIs for Job Data
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime

async def test_job_rss_feeds():
    """Test RSS feeds and public APIs specifically"""

    print("🔍 TESTING RSS FEEDS & PUBLIC APIS")
    print("=" * 50)

    # Known working RSS feeds and APIs
    sources = [
        {
            'name': 'Hacker News Jobs',
            'url': 'https://hn.algolia.com/api/v1/search_by_date?tags=job',
            'type': 'api'
        },
        {
            'name': 'AngelList API',
            'url': 'https://angel.co/api/v1/jobs',
            'type': 'api'
        },
        {
            'name': 'RemoteOK API',
            'url': 'https://remoteok.io/api',
            'type': 'api'
        },
        {
            'name': 'Authentic Jobs API',
            'url': 'https://authenticjobs.com/api/',
            'type': 'api'
        },
        {
            'name': 'CrunchBoard RSS',
            'url': 'https://www.crunchboard.com/jobs/feed/',
            'type': 'rss'
        },
        {
            'name': 'Remote.com RSS',
            'url': 'https://remote.com/jobs.rss',
            'type': 'rss'
        },
        {
            'name': 'NoDesk RSS',
            'url': 'https://nodesk.co/remote-jobs/rss.xml',
            'type': 'rss'
        },
        {
            'name': 'WorkingNomads RSS',
            'url': 'https://www.workingnomads.co/jobs.rss',
            'type': 'rss'
        },
        {
            'name': 'FlexJobs RSS',
            'url': 'https://www.flexjobs.com/jobs/feed',
            'type': 'rss'
        },
        {
            'name': 'Indeed API',
            'url': 'https://indeed-indeed.p.rapidapi.com/apisearch',
            'type': 'api'
        },
        {
            'name': 'LinkedIn Jobs (Public)',
            'url': 'https://www.linkedin.com/jobs/search/?keywords=remote',
            'type': 'web'
        },
        {
            'name': 'Monster Jobs RSS',
            'url': 'https://rss.monster.com/rssfeeds.aspx',
            'type': 'rss'
        },
        {
            'name': 'SimplyHired RSS',
            'url': 'https://www.simplyhired.com/search?q=remote&frs=1',
            'type': 'web'
        },
        {
            'name': 'Glassdoor API',
            'url': 'https://api.glassdoor.com/api/api.htm',
            'type': 'api'
        },
        {
            'name': 'JoobleAPI',
            'url': 'https://jooble.org/api/',
            'type': 'api'
        },
        {
            'name': 'CareerBuilder RSS',
            'url': 'https://www.careerbuilder.com/jobs/rss/',
            'type': 'rss'
        }
    ]

    results = []
    working_feeds = []

    async with aiohttp.ClientSession() as session:
        for source in sources:
            print(f"\n📡 Testing: {source['name']} ({source['type'].upper()})")
            print(f"🔗 {source['url']}")

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; JobBot/1.0)',
                    'Accept': 'application/json, application/xml, text/xml, text/html, */*'
                }

                async with session.get(
                    source['url'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    status = response.status
                    content_type = response.headers.get('content-type', '')

                    print(f"📊 Status: {status}")
                    print(f"📄 Type: {content_type}")

                    if status == 200:
                        if 'json' in content_type or source['type'] == 'api':
                            try:
                                data = await response.json()
                                print(f"✅ JSON API Response")

                                if isinstance(data, dict):
                                    print(f"🔑 Keys: {list(data.keys())[:5]}")
                                    # Check for job-related keys
                                    job_keys = [k for k in data.keys() if 'job' in k.lower() or 'hit' in k.lower()]
                                    if job_keys:
                                        print(f"💼 Job data keys: {job_keys}")
                                        working_feeds.append(source)
                                elif isinstance(data, list):
                                    print(f"📋 Array with {len(data)} items")
                                    if len(data) > 0 and isinstance(data[0], dict):
                                        print(f"🔑 Item keys: {list(data[0].keys())[:5]}")
                                        working_feeds.append(source)
                            except:
                                text = await response.text()
                                if 'xml' in content_type or '<?xml' in text[:100]:
                                    print("🔖 XML/RSS Feed")
                                    # Parse RSS
                                    try:
                                        feed = feedparser.parse(text)
                                        if feed.entries:
                                            print(f"📰 RSS: {len(feed.entries)} entries")
                                            print(f"📝 Sample: {feed.entries[0].title[:50] if feed.entries else 'N/A'}")
                                            working_feeds.append(source)
                                    except:
                                        print("❌ Invalid RSS")
                                else:
                                    print("❌ Not JSON or XML")
                        else:
                            text = await response.text()
                            if 'xml' in content_type or '<?xml' in text[:100]:
                                print("🔖 RSS/XML Feed")
                                feed = feedparser.parse(text)
                                if feed.entries:
                                    print(f"📰 RSS: {len(feed.entries)} entries")
                                    working_feeds.append(source)
                            else:
                                print("📝 HTML/Text Response")
                                if 'job' in text.lower()[:1000]:
                                    print("💼 Contains job data")

                    elif status == 401:
                        print("🔐 Requires API Key")
                    elif status == 403:
                        print("🚫 Access Forbidden")
                    elif status == 404:
                        print("❓ Not Found")
                    else:
                        print(f"⚠️  Status: {status}")

                    results.append({
                        'name': source['name'],
                        'url': source['url'],
                        'type': source['type'],
                        'status': status,
                        'working': status == 200
                    })

            except Exception as e:
                print(f"💥 Error: {str(e)[:80]}")
                results.append({
                    'name': source['name'],
                    'url': source['url'],
                    'type': source['type'],
                    'status': 'error',
                    'working': False
                })

    print("\n" + "=" * 50)
    print("📊 RSS/API FEED SUMMARY")
    print("=" * 50)

    working_count = len(working_feeds)
    print(f"✅ Working feeds: {working_count}/{len(ources)}")

    if working_feeds:
        print("\n🎯 READY-TO-USE DATA SOURCES:")
        for feed in working_feeds:
            print(f"  ✅ {feed['name']} ({feed['type'].upper()})")

        print(f"\n🚀 IMPLEMENTATION PRIORITY:")
        print("1. Start with JSON APIs (easiest to parse)")
        print("2. Add RSS feeds (use feedparser)")
        print("3. Consider HTML scraping for remaining sites")

    return working_feeds

if __name__ == "__main__":
    working = asyncio.run(test_job_rss_feeds())

    if working:
        print(f"\n💡 You have {len(working)} working data sources ready to implement!")
        print("Next step: Update the freelance spider to use these real endpoints.")
    else:
        print("\n⚠️  No working feeds found. Consider using API keys or web scraping.")