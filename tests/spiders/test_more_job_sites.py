# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test Additional Job Sites for Scraping Opportunities
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_additional_job_sites():
    """Test a comprehensive list of job/freelance sites"""

    print("🔍 TESTING ADDITIONAL JOB SITES FOR SCRAPING")
    print("=" * 60)

    # Comprehensive list of job/freelance platforms
    test_sites = [
        # Freelance Platforms
        {
            'name': 'Fiverr (Public API)',
            'url': 'https://api.fiverr.com/v1/search/gigs',
            'type': 'api'
        },
        {
            'name': 'Guru.com Jobs',
            'url': 'https://www.guru.com/d/jobs/',
            'type': 'web'
        },
        {
            'name': 'PeoplePerHour',
            'url': 'https://www.peopleperhour.com/freelance-jobs',
            'type': 'web'
        },
        {
            'name': '99designs',
            'url': 'https://99designs.com/projects',
            'type': 'web'
        },
        {
            'name': 'Toptal (Public)',
            'url': 'https://www.toptal.com/developers',
            'type': 'web'
        },

        # Remote Job Boards
        {
            'name': 'We Work Remotely',
            'url': 'https://weworkremotely.com/jobs.rss',
            'type': 'rss'
        },
        {
            'name': 'Remote.co',
            'url': 'https://remote.co/remote-jobs/developer/',
            'type': 'web'
        },
        {
            'name': 'FlexJobs',
            'url': 'https://www.flexjobs.com/jobs',
            'type': 'web'
        },
        {
            'name': 'Authentic Jobs',
            'url': 'https://authenticjobs.com/jobs/remote',
            'type': 'web'
        },
        {
            'name': 'JustRemote',
            'url': 'https://justremote.co/remote-jobs',
            'type': 'web'
        },

        # Tech Job Boards
        {
            'name': 'Stack Overflow Jobs',
            'url': 'https://stackoverflow.com/jobs',
            'type': 'web'
        },
        {
            'name': 'GitHub Jobs',
            'url': 'https://jobs.github.com/positions.json',
            'type': 'api'
        },
        {
            'name': 'Dice Jobs',
            'url': 'https://www.dice.com/jobs',
            'type': 'web'
        },
        {
            'name': 'AngelList Talent',
            'url': 'https://angel.co/company/jobs',
            'type': 'web'
        },
        {
            'name': 'Y Combinator Jobs',
            'url': 'https://www.worklist.com/jobs',
            'type': 'web'
        },

        # Content/Creative Platforms
        {
            'name': 'Contently',
            'url': 'https://contently.com/freelancers/',
            'type': 'web'
        },
        {
            'name': 'ClearVoice',
            'url': 'https://www.clearvoice.com/freelancers',
            'type': 'web'
        },
        {
            'name': 'WriterAccess',
            'url': 'https://www.writeraccess.com/freelance-writing-jobs/',
            'type': 'web'
        },

        # Alternative APIs
        {
            'name': 'JSearch API (via RapidAPI)',
            'url': 'https://jsearch.p.rapidapi.com/search',
            'type': 'api'
        },
        {
            'name': 'Adzuna API',
            'url': 'https://api.adzuna.com/v1/api/jobs/us/search/1',
            'type': 'api'
        },
        {
            'name': 'Reed Jobs API',
            'url': 'https://www.reed.co.uk/api/1.0/search',
            'type': 'api'
        },
        {
            'name': 'Indeed RSS',
            'url': 'https://rss.indeed.com/rss',
            'type': 'rss'
        },
        {
            'name': 'Craigslist Gigs',
            'url': 'https://newyork.craigslist.org/search/ggg',
            'type': 'web'
        },

        # International Platforms
        {
            'name': 'Workana (Latin America)',
            'url': 'https://www.workana.com/jobs',
            'type': 'web'
        },
        {
            'name': 'Naukri (India)',
            'url': 'https://www.naukri.com/remote-jobs',
            'type': 'web'
        }
    ]

    results = []
    accessible_count = 0

    async with aiohttp.ClientSession() as session:
        for site in test_sites:
            print(f"\n🌐 Testing: {site['name']} ({site['type'].upper()})")
            print(f"📡 URL: {site['url']}")

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }

                async with session.get(
                    site['url'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                    allow_redirects=True
                ) as response:

                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    final_url = str(response.url)

                    print(f"📊 Status: {status}")
                    print(f"📄 Content-Type: {content_type}")

                    if final_url != site['url']:
                        print(f"🔄 Redirected to: {final_url}")

                    accessible = False
                    data_type = 'none'

                    if status == 200:
                        accessible = True
                        accessible_count += 1

                        # Analyze content
                        if 'json' in content_type:
                            try:
                                data = await response.json()
                                data_type = 'json'
                                if isinstance(data, dict):
                                    print(f"✅ JSON API - Keys: {list(data.keys())[:5]}")
                                elif isinstance(data, list):
                                    print(f"✅ JSON Array - {len(data)} items")
                                    if len(data) > 0 and isinstance(data[0], dict):
                                        print(f"📋 Sample keys: {list(data[0].keys())[:5]}")
                            except:
                                print("❌ Invalid JSON")
                                accessible = False
                        else:
                            text = await response.text()
                            text_lower = text.lower()

                            if 'xml' in content_type or '<?xml' in text[:100]:
                                data_type = 'xml/rss'
                                print("🔖 XML/RSS feed detected")
                                if 'job' in text_lower[:1000] or 'gig' in text_lower[:1000]:
                                    print("💼 Job content detected")
                            else:
                                data_type = 'html'
                                print(f"📝 HTML Page - {len(text)} chars")

                                # Check for job indicators
                                job_indicators = ['job', 'position', 'hire', 'freelance', 'gig', 'contract', 'remote', 'work']
                                found_indicators = [word for word in job_indicators if word in text_lower[:2000]]
                                if found_indicators:
                                    print(f"💼 Job indicators found: {found_indicators[:3]}")

                                # Check for data structures
                                if 'application/json' in text or 'window.__' in text:
                                    print("📊 Embedded JSON data detected")
                                    data_type = 'html+json'

                    elif status == 403:
                        print("🚫 Access Forbidden - Site blocks bots")
                    elif status == 404:
                        print("❓ Not Found - Endpoint may have moved")
                    elif status == 429:
                        print("⏳ Rate Limited")
                    elif status in [301, 302, 303, 307, 308]:
                        print(f"🔄 Redirect ({status})")
                    else:
                        print(f"⚠️  Status: {status}")

                    results.append({
                        'name': site['name'],
                        'url': site['url'],
                        'type': site['type'],
                        'status': status,
                        'content_type': content_type,
                        'data_type': data_type,
                        'accessible': accessible,
                        'final_url': final_url,
                        'timestamp': datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                print("⏰ Timeout")
                results.append({
                    'name': site['name'],
                    'url': site['url'],
                    'type': site['type'],
                    'status': 'timeout',
                    'accessible': False,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"💥 Error: {str(e)[:100]}")
                results.append({
                    'name': site['name'],
                    'url': site['url'],
                    'type': site['type'],
                    'status': f'error: {str(e)[:50]}',
                    'accessible': False,
                    'timestamp': datetime.now().isoformat()
                })

    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE SCRAPING ANALYSIS")
    print("=" * 60)

    print(f"✅ Accessible sites: {accessible_count}/{len(test_sites)}")

    # Group by type
    by_type = {}
    for result in results:
        if result['accessible']:
            site_type = result['type']
            if site_type not in by_type:
                by_type[site_type] = []
            by_type[site_type].append(result['name'])

    for site_type, sites in by_type.items():
        print(f"\n🎯 {site_type.upper()} Sources ({len(ites)}):")
        for site in sites:
            print(f"  ✅ {site}")

    print(f"\n🚀 RECOMMENDATIONS:")
    if accessible_count > 5:
        print("🎉 Excellent! Multiple sources available for diverse job data")
    elif accessible_count > 2:
        print("👍 Good selection of sources available")
    else:
        print("⚠️  Limited sources - consider API keys or alternative approaches")

    print(f"\n💡 Best immediate targets:")
    priority_sites = [r for r in results if r['accessible'] and r['data_type'] in ['json', 'xml/rss']]
    for site in priority_sites[:5]:
        print(f"  🎯 {site['name']} - {site['data_type']}")

    return results

if __name__ == "__main__":
    asyncio.run(test_additional_job_sites())