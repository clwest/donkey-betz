#!/usr/bin/env python
"""
Deploy Comprehensive Spider Army
Activate ALL income category spiders for maximum opportunity discovery
"""

import os
import sys
import django
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from intelligence.unified_spider_job_bridge import UnifiedSpiderJobBridge
from ai_core.agents.intelligent_job_matcher import IntelligentJobMatcher


class ComprehensiveSpiderDeployment:
    """Deploy massive spider army across ALL income categories"""

    def __init__(self):
        self.bridge = UnifiedSpiderJobBridge()
        self.matcher = IntelligentJobMatcher()

        # All income categories to scan
        self.income_categories = {
            'freelance_work': {
                'spiders': ['upwork_opportunities', 'freelancer_opportunities', 'fiverr_gig_analyzer'],
                'keywords': ['freelance', 'contract', 'remote work', 'project-based'],
                'expected_opportunities': 50
            },
            'job_opportunities': {
                'spiders': ['indeed_job', 'linkedin_jobs', 'remote_job_boards'],
                'keywords': ['full-time', 'part-time', 'remote', 'tech jobs'],
                'expected_opportunities': 100
            },
            'e_commerce': {
                'spiders': ['amazon_fba_opportunities', 'shopify_dropshipping', 'etsy_handmade', 'print_on_demand'],
                'keywords': ['amazon fba', 'dropshipping', 'ecommerce', 'online selling'],
                'expected_opportunities': 75
            },
            'digital_services': {
                'spiders': ['online_coaching', 'online_tutoring', 'virtual_assistant', 'online_marketplace'],
                'keywords': ['coaching', 'tutoring', 'virtual assistant', 'consulting'],
                'expected_opportunities': 60
            },
            'real_estate': {
                'spiders': ['rental_property', 'airbnb_opportunity', 'real_estate_wholesaling'],
                'keywords': ['rental property', 'airbnb', 'real estate investment', 'wholesaling'],
                'expected_opportunities': 40
            },
            'content_creation': {
                'spiders': ['youtube_channel_analyzer', 'substack_newsletter', 'twitter_influencer'],
                'keywords': ['youtube', 'newsletter', 'content creation', 'influencer'],
                'expected_opportunities': 30
            },
            'financial_opportunities': {
                'spiders': ['stock_news', 'crypto_intelligence', 'market_data', 'sec_filings'],
                'keywords': ['trading', 'investing', 'crypto', 'financial markets'],
                'expected_opportunities': 25
            },
            'advisor_intelligence': {
                'spiders': ['berkshire_hathaway', 'cathie_wood_innovation', 'ray_dalio_macro', 'peter_thiel_startup'],
                'keywords': ['investment advice', 'business strategy', 'startup advice'],
                'expected_opportunities': 20
            }
        }

        print(f"\n🕷️ COMPREHENSIVE SPIDER ARMY INITIALIZED")
        print(f"📊 Categories: {len(self.income_categories)}")
        print(f"🎯 Total Expected Opportunities: {sum(cat['expected_opportunities'] for cat in self.income_categories.values())}")

    async def deploy_full_spider_army(self):
        """Deploy ALL spiders across ALL income categories"""
        print("\n" + "="*80)
        print("🚀 DEPLOYING COMPREHENSIVE SPIDER ARMY")
        print("="*80)

        deployment_results = {}
        total_opportunities = 0

        for category, config in self.income_categories.items():
            print(f"\n📂 Category: {category.upper().replace('_', ' ')}")
            print(f"   Spiders: {len(config['spiders'])}")
            print(f"   Keywords: {', '.join(config['keywords'])}")

            # Deploy category spiders
            category_result = await self._deploy_category_spiders(category, config)
            deployment_results[category] = category_result
            total_opportunities += category_result['opportunities_found']

            print(f"   ✅ Found: {category_result['opportunities_found']} opportunities")

        print(f"\n" + "="*80)
        print(f"🎉 DEPLOYMENT COMPLETE!")
        print(f"📊 Total Opportunities Found: {total_opportunities}")
        print(f"🕷️ Total Spiders Deployed: {sum(len(cat['spiders']) for cat in self.income_categories.values())}")
        print("="*80)

        return deployment_results

    async def _deploy_category_spiders(self, category, config):
        """Deploy spiders for specific category"""
        try:
            # Create search criteria for this category
            search_criteria = {
                'keywords': config['keywords'],
                'category': category,
                'spider_types': config['spiders'],
                'max_results_per_spider': 20
            }

            # Deploy spiders
            deployment = await self.bridge.activate_spider_deployment(
                user_request=f"Scan {category} opportunities",
                search_criteria=search_criteria
            )

            return {
                'deployment_id': deployment['deployment_id'],
                'spiders_deployed': len(config['spiders']),
                'opportunities_found': deployment['jobs_found'],
                'sources': deployment['sources'],
                'expected_vs_actual': f"{deployment['jobs_found']}/{config['expected_opportunities']}"
            }

        except Exception as e:
            print(f"   ⚠️ Error deploying {category}: {e}")
            return {
                'deployment_id': None,
                'spiders_deployed': 0,
                'opportunities_found': 0,
                'sources': [],
                'error': str(e)
            }

    async def analyze_opportunity_distribution(self, deployment_results):
        """Analyze the distribution of opportunities across categories"""
        print("\n" + "="*80)
        print("📊 OPPORTUNITY DISTRIBUTION ANALYSIS")
        print("="*80)

        # Get all opportunities from cache
        from django.core.cache import cache
        all_opportunities = cache.get('unified_live_jobs', [])

        if not all_opportunities:
            print("❌ No opportunities in cache")
            return

        # Categorize opportunities
        category_breakdown = {}
        uncategorized = []

        for opp in all_opportunities:
            categorized = False
            opp_text = f"{opp.get('title', '')} {opp.get('description', '')}".lower()

            for category, config in self.income_categories.items():
                if any(keyword.lower() in opp_text for keyword in config['keywords']):
                    if category not in category_breakdown:
                        category_breakdown[category] = []
                    category_breakdown[category].append(opp)
                    categorized = True
                    break

            if not categorized:
                uncategorized.append(opp)

        # Display breakdown
        print(f"\n📈 Opportunity Breakdown:")
        for category, opportunities in category_breakdown.items():
            avg_budget = self._calculate_average_budget(opportunities)
            print(f"   {category.upper().replace('_', ' ')}: {len(opportunities)} opportunities")
            print(f"      Average Budget: {avg_budget}")
            print(f"      Top Opportunity: {opportunities[0].get('title', 'N/A')[:50]}...")

        if uncategorized:
            print(f"\n❓ Uncategorized: {len(uncategorized)} opportunities")

        return category_breakdown

    def _calculate_average_budget(self, opportunities):
        """Calculate average budget from opportunities"""
        budgets = []
        for opp in opportunities:
            budget_text = opp.get('budget', opp.get('salary', ''))
            if budget_text and '$' in str(budget_text):
                # Extract numbers from budget text
                import re
                numbers = re.findall(r'[\d,]+', str(budget_text))
                if numbers:
                    budget = int(numbers[0].replace(',', ''))
                    budgets.append(budget)

        if budgets:
            return f"${sum(budgets) // len(budgets):,}"
        return "Not specified"

    async def match_agents_to_all_opportunities(self):
        """Match agents to ALL discovered opportunities"""
        print("\n" + "="*80)
        print("🤖 MATCHING AGENTS TO ALL OPPORTUNITIES")
        print("="*80)

        from django.core.cache import cache
        all_opportunities = cache.get('unified_live_jobs', [])

        if not all_opportunities:
            print("❌ No opportunities to match")
            return

        matched_opportunities = []
        match_stats = {
            'total_processed': 0,
            'successfully_matched': 0,
            'high_confidence_matches': 0,
            'medium_confidence_matches': 0,
            'low_confidence_matches': 0
        }

        print(f"🔄 Processing {len(all_opportunities)} opportunities...")

        for i, opportunity in enumerate(all_opportunities[:50]):  # Limit to 50 for demo
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(all_opportunities[:50])}")

            try:
                match = await self.matcher.match_job_with_learning(opportunity)
                match_stats['total_processed'] += 1

                if match:
                    opportunity['agent_match'] = match
                    matched_opportunities.append(opportunity)
                    match_stats['successfully_matched'] += 1

                    # Categorize by confidence
                    confidence = match['confidence']
                    if confidence >= 0.8:
                        match_stats['high_confidence_matches'] += 1
                    elif confidence >= 0.6:
                        match_stats['medium_confidence_matches'] += 1
                    else:
                        match_stats['low_confidence_matches'] += 1

            except Exception as e:
                print(f"   ⚠️ Error matching opportunity {i}: {e}")
                continue

        # Display results
        print(f"\n✅ Matching Complete!")
        print(f"   Total Processed: {match_stats['total_processed']}")
        print(f"   Successfully Matched: {match_stats['successfully_matched']}")
        print(f"   High Confidence (80%+): {match_stats['high_confidence_matches']}")
        print(f"   Medium Confidence (60-80%): {match_stats['medium_confidence_matches']}")
        print(f"   Low Confidence (<60%): {match_stats['low_confidence_matches']}")

        return matched_opportunities, match_stats

    async def display_top_opportunities_by_category(self, matched_opportunities):
        """Display top opportunities in each category"""
        print("\n" + "="*80)
        print("🏆 TOP OPPORTUNITIES BY CATEGORY")
        print("="*80)

        # Group by category
        category_opportunities = {}
        for opp in matched_opportunities:
            opp_text = f"{opp.get('title', '')} {opp.get('description', '')}".lower()

            for category, config in self.income_categories.items():
                if any(keyword.lower() in opp_text for keyword in config['keywords']):
                    if category not in category_opportunities:
                        category_opportunities[category] = []
                    category_opportunities[category].append(opp)
                    break

        # Display top opportunities per category
        for category, opportunities in category_opportunities.items():
            if not opportunities:
                continue

            print(f"\n📂 {category.upper().replace('_', ' ')}")

            # Sort by match confidence
            opportunities.sort(key=lambda x: x.get('agent_match', {}).get('confidence', 0), reverse=True)

            for i, opp in enumerate(opportunities[:3]):  # Top 3 per category
                match = opp.get('agent_match', {})
                agent_name = match.get('agent', {}).get('name', 'Unknown')
                confidence = match.get('confidence', 0)
                budget = opp.get('budget', opp.get('salary', 'Not specified'))

                print(f"   [{i+1}] {opp.get('title', 'Unknown Title')}")
                print(f"       Budget: {budget}")
                print(f"       Agent: {agent_name} ({confidence:.0%} confidence)")
                print(f"       Source: {opp.get('source', 'Unknown')}")


async def main():
    """Deploy the comprehensive spider army"""
    print("\n🕷️ COMPREHENSIVE SPIDER ARMY DEPLOYMENT")
    print("="*90)

    deployment = ComprehensiveSpiderDeployment()

    # Step 1: Deploy all spiders
    deployment_results = await deployment.deploy_full_spider_army()

    # Step 2: Analyze opportunity distribution
    category_breakdown = await deployment.analyze_opportunity_distribution(deployment_results)

    # Step 3: Match agents to all opportunities
    matched_opportunities, match_stats = await deployment.match_agents_to_all_opportunities()

    # Step 4: Display top opportunities by category
    await deployment.display_top_opportunities_by_category(matched_opportunities)

    print("\n" + "="*90)
    print("🎉 COMPREHENSIVE SPIDER DEPLOYMENT COMPLETE!")
    print("="*90)
    print("\n🎯 Summary:")
    print(f"   Categories Scanned: {len(deployment.income_categories)}")
    print(f"   Total Spiders Deployed: {sum(len(cat['spiders']) for cat in deployment.income_categories.values())}")
    print(f"   Opportunities Discovered: {sum(r.get('opportunities_found', 0) for r in deployment_results.values())}")
    print(f"   Successfully Matched: {match_stats.get('successfully_matched', 0)}")
    print(f"   High Confidence Matches: {match_stats.get('high_confidence_matches', 0)}")

    print("\n💡 Next Steps:")
    print("   1. Review top opportunities in each category")
    print("   2. Select opportunities that match your interests")
    print("   3. Deploy agents to apply/pursue selected opportunities")
    print("   4. Track results and optimize based on success rates")


if __name__ == "__main__":
    asyncio.run(main())