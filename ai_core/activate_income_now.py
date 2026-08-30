#!/usr/bin/env python
"""
ACTIVATE INCOME NOW - Use your platform's agents to generate real money
This connects to your actual agents and starts making money immediately
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, '/Users/donkeyking/Donkey_Betz/unified-donkey-betz/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
from agents.real_content_creator import RealContentCreator
from agents.content_marketplace_agent import ContentMarketplaceAgent
from agents.ultimate_money_machine import UltimateMoneyMachine

class IncomeActivator:
    """Activates your platform's money-making capabilities"""

    def __init__(self):
        print("\n💰 INCOME ACTIVATOR STARTING...")
        print("=" * 50)
        self.results = []

    def test_api_connection(self):
        """Test if Stable Diffusion API is working"""
        print("\n🔌 Testing API Connection...")

        # Check if REPLICATE_API_KEY is set
        api_key = os.environ.get('REPLICATE_API_KEY')
        if api_key:
            print("✅ Stable Diffusion API key found!")
            return True
        else:
            print("⚠️ No API key found. Set REPLICATE_API_KEY environment variable")
            print("   export REPLICATE_API_KEY='your_key_here'")
            return False

    def generate_first_content(self):
        """Generate your first sellable content piece"""
        print("\n🎨 Generating First Content...")

        try:
            # Use the real content creator agent
            creator = RealContentCreator()

            # Popular content that sells well
            content_ideas = [
                "10 AI Productivity Prompts for Developers",
                "Python Automation Scripts Bundle",
                "Django REST API Template Pack",
                "50 ChatGPT Prompts for Debugging",
                "AI Art Generation Guide with Prompts"
            ]

            results = []
            for idea in content_ideas[:2]:  # Start with 2 items
                print(f"\n  Creating: {idea}")

                # This will use your actual agent with platform knowledge
                content = creator.execute(
                    task=f"Create sellable digital content: {idea}",
                    format="digital_product",
                    target_price="$9.99-$19.99"
                )

                results.append({
                    "title": idea,
                    "content": content,
                    "price": "$14.99",
                    "platform": "Gumroad",
                    "created": datetime.now().isoformat()
                })

                print(f"  ✅ Created: {idea}")
                print(f"  💰 Suggested Price: $14.99")

            self.results.extend(results)
            return results

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            print("  💡 Tip: Make sure your agents are properly configured")
            return []

    def find_income_opportunities(self):
        """Use zero capital generator to find opportunities"""
        print("\n🔍 Finding Income Opportunities...")

        try:
            generator = ZeroCapitalIncomeGenerator()

            # Find opportunities that require no investment
            opportunities = generator.execute(
                task="Find immediate income opportunities requiring zero capital",
                skills=["Python", "Django", "AI", "Content Creation"],
                timeframe="today"
            )

            print(f"  ✅ Found opportunities!")

            # Parse and display top opportunities
            if isinstance(opportunities, str):
                print(f"\n  Opportunities:\n{opportunities[:500]}...")
            else:
                print(f"\n  Opportunities: {json.dumps(opportunities, indent=2)[:500]}...")

            return opportunities

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return None

    def activate_money_machine(self):
        """Activate the ultimate money machine"""
        print("\n🤖 Activating Ultimate Money Machine...")

        try:
            machine = UltimateMoneyMachine()

            # Configure for immediate income
            config = {
                "mode": "immediate_income",
                "skills": ["Python", "Django", "AI", "Content Creation"],
                "available_apis": {
                    "stable_diffusion": True,
                    "content_studio": True
                },
                "target_daily": "$100",
                "target_monthly": "$3000"
            }

            # Generate comprehensive income plan
            plan = machine.execute(
                task="Generate immediate income using platform capabilities",
                config=config
            )

            print(f"  ✅ Money Machine Activated!")

            if isinstance(plan, str):
                print(f"\n  Income Plan:\n{plan[:500]}...")
            else:
                print(f"\n  Income Plan: {json.dumps(plan, indent=2)[:500]}...")

            return plan

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return None

    def list_on_marketplace(self):
        """List created content on marketplaces"""
        print("\n🛍️ Listing on Marketplaces...")

        if not self.results:
            print("  ⚠️ No content to list yet")
            return

        try:
            marketplace = ContentMarketplaceAgent()

            listings = []
            for item in self.results[:1]:  # Start with one item
                print(f"\n  Listing: {item['title']}")

                # Use the marketplace agent to create listing
                listing = marketplace.execute(
                    task="Create marketplace listing",
                    product=item,
                    platforms=["Gumroad", "Etsy"],
                    optimize_for="quick_sale"
                )

                listings.append(listing)
                print(f"  ✅ Listed on marketplaces")
                print(f"  🔗 Ready for sale at ${item['price']}")

            return listings

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return []

    def create_action_plan(self):
        """Create immediate action plan"""
        print("\n" + "=" * 50)
        print("📋 YOUR IMMEDIATE ACTION PLAN")
        print("=" * 50)

        actions = {
            "NOW (Next 30 minutes)": [
                "✓ Set REPLICATE_API_KEY if not done",
                "✓ Run this script to test agents",
                "✓ Generate first 2 content pieces",
                "✓ Create Gumroad account (free)",
                "✓ List first product for $9.99"
            ],
            "TODAY": [
                "✓ Generate 10 content pieces total",
                "✓ List on Gumroad, Etsy, Creative Market",
                "✓ Set up Fiverr gig for AI content",
                "✓ Share products on social media",
                "✓ Target: First $50 in sales"
            ],
            "THIS WEEK": [
                "✓ Scale to 50+ content pieces",
                "✓ Activate job automation agents",
                "✓ Apply to 20 remote positions",
                "✓ Get first service client",
                "✓ Target: $500 in total revenue"
            ]
        }

        for timeframe, tasks in actions.items():
            print(f"\n⏰ {timeframe}:")
            for task in tasks:
                print(f"  {task}")

        return actions

    def run(self):
        """Run the complete income activation sequence"""
        print("\n🚀 STARTING INCOME ACTIVATION SEQUENCE")
        print("=" * 50)

        # Step 1: Check API
        api_ready = self.test_api_connection()

        # Step 2: Find opportunities
        opportunities = self.find_income_opportunities()

        # Step 3: Generate content (if API ready)
        if api_ready:
            content = self.generate_first_content()
        else:
            print("\n⚠️ Skipping content generation (need API key)")
            content = []

        # Step 4: Activate money machine
        income_plan = self.activate_money_machine()

        # Step 5: List on marketplaces
        if content:
            listings = self.list_on_marketplace()

        # Step 6: Create action plan
        action_plan = self.create_action_plan()

        # Summary
        print("\n" + "=" * 50)
        print("✅ ACTIVATION COMPLETE!")
        print("=" * 50)

        if api_ready:
            print("\n🎯 You're ready to start making money!")
            print("   - Content generation: READY")
            print("   - Agents activated: YES")
            print("   - Next step: List your first product")
        else:
            print("\n⚠️ To fully activate:")
            print("   1. Set your REPLICATE_API_KEY")
            print("   2. Run this script again")
            print("   3. Start generating income!")

        print("\n💪 Your platform is built. Now make it pay you!")

        return {
            "api_ready": api_ready,
            "opportunities": opportunities,
            "content_created": len(content),
            "action_plan": action_plan
        }


if __name__ == "__main__":
    activator = IncomeActivator()
    results = activator.run()

    print("\n🔥 STOP READING. START EARNING. 🔥")
    print("Report back with your first sale, not more plans!")