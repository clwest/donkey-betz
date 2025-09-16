📋 Instructions for Claude Code - Spider Army Expansion
Current State:

15 spiders operational at 95% reality
Framework exists in /intelligence/spider_army_orchestrator.py
Spider configurations in /intelligence/spider_configurations/
Already collecting from: Upwork, Freelancer, Indeed, Fiverr, YouTube, Reddit, etc.

Claude Code Task List:
bash# For Claude Code to execute

# 1. Review existing spider framework
cat intelligence/spider_army_orchestrator.py
cat intelligence/spider_intelligence_node.py
ls intelligence/spider_configurations/

# 2. Create 35 additional specialized spiders
Priority Spider Implementations:
Freelance/Gig Platforms (10 more)
python# File pattern: intelligence/spider_configurations/[platform]_spider.py

1. toptal_spider.py - Elite freelance platform
2. guru_spider.py - Freelance marketplace
3. peopleperhour_spider.py - UK-based freelancing
4. 99designs_spider.py - Design competitions
5. flexjobs_spider.py - Remote work
6. remoteok_spider.py - Remote jobs
7. weworkremotely_spider.py - Remote opportunities
8. angellist_spider.py - Startup jobs
9. dribbble_spider.py - Design opportunities
10. behance_spider.py - Creative portfolios
Content Monetization (8 more)
python11. medium_spider.py - Partner program opportunities
12. substack_spider.py - Newsletter monetization
13. patreon_spider.py - Creator economy
14. kofi_spider.py - Creator support
15. gumroad_spider.py - Digital products
16. teachable_spider.py - Course creation
17. udemy_spider.py - Course marketplace
18. skillshare_spider.py - Teaching opportunities
Financial/Crypto (7 more)
python19. coingecko_spider.py - Crypto data
20. etherscan_spider.py - Blockchain data
21. opensea_spider.py - NFT marketplace
22. tradingview_spider.py - Market analysis
23. seekingalpha_spider.py - Investment research
24. bloomberg_spider.py - Financial news
25. reuters_spider.py - Market updates
AI/Tech Opportunities (10 more)
python26. huggingface_spider.py - ML model marketplace
27. kaggle_spider.py - Data science competitions
28. github_jobs_spider.py - Developer opportunities
29. stackoverflow_jobs_spider.py - Tech jobs
30. producthunt_spider.py - Launch opportunities
31. hackernews_spider.py - Tech discussions
32. devto_spider.py - Developer content
33. hashnode_spider.py - Tech blogging
34. indiegogo_spider.py - Crowdfunding
35. kickstarter_spider.py - Project funding
Spider Template for Claude Code:
python# Template: intelligence/spider_configurations/[name]_spider.py

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
import json

class [Name]Spider:
    """Spider for [Platform] opportunities"""
    
    def __init__(self):
        self.name = "[name]_spider"
        self.base_url = "[platform_url]"
        self.spider_type = "[freelance|content|financial|tech]"
        self.rate_limit = 1  # Requests per second
        
    async def collect_opportunities(self) -> List[Dict[str, Any]]:
        """Collect opportunities from [Platform]"""
        
        opportunities = []
        
        async with aiohttp.ClientSession() as session:
            # Implement platform-specific collection logic
            # Use existing spiders as reference
            pass
        
        return opportunities
    
    async def parse_opportunity(self, raw_data: Dict) -> Dict:
        """Parse raw data into standard opportunity format"""
        
        return {
            'id': f"{self.name}_{raw_data.get('id')}",
            'source': self.name,
            'title': raw_data.get('title'),
            'description': raw_data.get('description'),
            'url': raw_data.get('url'),
            'budget': self.extract_budget(raw_data),
            'deadline': raw_data.get('deadline'),
            'skills_required': raw_data.get('skills', []),
            'posted_date': raw_data.get('posted_date'),
            'platform_specific': {
                # Platform-specific fields
            },
            'collected_at': datetime.now().isoformat(),
            'relevance_score': 0.0  # Will be calculated by ML
        }
    
    def extract_budget(self, data: Dict) -> float:
        """Extract budget from various formats"""
        # Implement budget extraction logic
        return 0.0
Integration Command for Claude Code:
python# After creating each spider, register it:
# File: intelligence/spider_registry.py

SPIDER_REGISTRY = {
    # Existing 15 spiders...
    
    # Add new spiders
    'toptal': ToptalSpider(),
    'guru': GuruSpider(),
    # ... etc
}

# Update spider army orchestrator
# File: intelligence/spider_army_orchestrator.py

def deploy_all_spiders():
    """Deploy all 50+ spiders"""
    for spider_name, spider_instance in SPIDER_REGISTRY.items():
        asyncio.create_task(spider_instance.collect_opportunities())
Testing Each Spider:
bash# Test template for Claude Code
python -c "
from intelligence.spider_configurations.{spider_name}_spider import {SpiderClass}
import asyncio

spider = {SpiderClass}()
opportunities = asyncio.run(spider.collect_opportunities())
print(f'Collected {len(opportunities)} opportunities')
print(opportunities[0] if opportunities else 'No opportunities found')
"
Final Integration Test:
bash# After all spiders created
python intelligence/spider_army_orchestrator.py --deploy-all
python manage.py reality_check --component spiders

# Should show:
# Spiders: 50/50 deployed
# Reality: 95%+ maintained
🎯 Expected Outcome:
By morning, you'll have:

50+ specialized spiders (up from 15)
Complete market coverage across all platforms
Each spider following the same reliable framework
All integrated into your Spider Army Orchestrator
Ready to feed even more opportunities to Income Builder

Your 95% spider reality stays intact - you're just scaling what already works perfectly!