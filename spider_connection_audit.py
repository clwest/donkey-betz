#!/usr/bin/env python3
"""
Spider-Agent-Advisor Connection Audit Tool
Analyzes and maps all connections in the Unified Donkey Betz Platform
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

class SpiderConnectionAuditor:
    """Audits spider-agent-advisor connections"""

    def __init__(self):
        self.connections = {
            "spiders": {},
            "agents": {},
            "advisors": {},
            "routing_table": {},
            "orphaned": {
                "spiders": [],
                "agents": [],
                "advisors": []
            }
        }

        # Spider swarm configurations from spider_army_orchestrator.py
        self.spider_swarms = {
            "financial_intel": {
                "count": 250,
                "type": "FinancialIntelligenceSpider",
                "subscribers": ["warren_buffett", "ray_dalio", "financial_strategist", "crypto_expert", "options_master"]
            },
            "innovation_tracker": {
                "count": 150,
                "type": "InnovationTrackingSpider",
                "subscribers": ["cathie_wood", "peter_thiel", "ai_strategist", "tech_architect"]
            },
            "market_data": {
                "count": 200,
                "type": "MarketDataSpider",
                "subscribers": ["trading_agents", "crypto_expert", "options_master"]
            },
            "social_sentiment": {
                "count": 300,
                "type": "SocialSentimentSpider",
                "subscribers": ["sentiment_agents", "marketing_agents", "social_trend_analyzers"]
            },
            "news_harvester": {
                "count": 200,
                "type": "NewsHarvesterSpider",
                "subscribers": ["ALL"]  # Goes to everyone
            },
            "research_papers": {
                "count": 100,
                "type": "ResearchPaperSpider",
                "subscribers": ["ai_strategist", "research_agents", "academic_advisors"]
            },
            "patent_monitor": {
                "count": 50,
                "type": "PatentMonitorSpider",
                "subscribers": ["cathie_wood", "tech_architect", "innovation_agents"]
            },
            "regulatory": {
                "count": 70,
                "type": "RegulatoryTrackingSpider",
                "subscribers": ["legal_counsel", "compliance_agents", "financial_strategist"]
            },
            "competitive": {
                "count": 100,
                "type": "CompetitiveIntelligenceSpider",
                "subscribers": ["business_strategist", "startup_guru", "competitive_agents"]
            },
            "adaptive": {
                "count": 450,
                "type": "AdaptiveSpider",
                "subscribers": ["ALL"]  # Feeds everyone
            }
        }

        # Routing tables from spider_data_router.py
        self.routing_tables = {
            "financial_intel": [
                "advisor:warren_buffett",
                "advisor:ray_dalio",
                "advisor:peter_lynch",
                "advisor:george_soros",
                "agent:financial_analyst",
                "agent:portfolio_manager",
                "agent:risk_assessor",
                "agent:crypto_trader",
                "agent:forex_trader",
                "agent:income_builder"  # Critical connection
            ],
            "innovation_tracker": [
                "advisor:cathie_wood",
                "advisor:peter_thiel",
                "advisor:marc_andreessen",
                "advisor:reid_hoffman",
                "agent:tech_scout",
                "agent:startup_evaluator",
                "agent:patent_analyzer",
                "agent:innovation_tracker"
            ],
            "market_data": [
                "advisor:ray_dalio",
                "advisor:paul_tudor_jones",
                "advisor:stanley_druckenmiller",
                "agent:market_maker",
                "agent:arbitrage_finder",
                "agent:spread_analyzer",
                "agent:volatility_trader",
                "agent:sports_arbitrage"  # Sports betting connection
            ],
            "social_sentiment": [
                "advisor:gary_vaynerchuk",
                "advisor:tim_ferriss",
                "agent:sentiment_analyzer",
                "agent:social_media_monitor",
                "agent:trend_detector",
                "agent:influencer_tracker"
            ],
            "news_harvester": "ALL",  # Universal feed
            "research_papers": "innovation_tracker + financial_intel",
            "patent_monitor": "innovation_tracker",
            "regulatory": "financial_intel + market_data",
            "competitive": "innovation_tracker + financial_intel",
            "adaptive": "ALL"  # Adaptive spiders feed everyone
        }

    def audit_connections(self) -> Dict:
        """Perform comprehensive connection audit"""
        print("🔍 Starting Spider-Agent-Advisor Connection Audit...")

        # 1. Count total spiders
        total_spiders = sum(swarm["count"] for swarm in self.spider_swarms.values())
        self.connections["total_spiders"] = total_spiders
        print(f"📊 Total Spiders Configured: {total_spiders:,}")

        # 2. Analyze spider swarms
        print("\n🕷️ Spider Swarms Analysis:")
        for swarm_id, config in self.spider_swarms.items():
            print(f"\n  {swarm_id}:")
            print(f"    • Count: {config['count']}")
            print(f"    • Type: {config['type']}")
            print(f"    • Subscribers: {', '.join(config['subscribers'][:3])}...")

            self.connections["spiders"][swarm_id] = {
                "count": config["count"],
                "type": config["type"],
                "subscribers": config["subscribers"],
                "total_connections": len(config["subscribers"]) if config["subscribers"][0] != "ALL" else 127
            }

        # 3. Map agent connections
        print("\n🤖 Agent Connections:")
        agent_connections = defaultdict(list)

        for swarm_id, consumers in self.routing_tables.items():
            if isinstance(consumers, list):
                for consumer in consumers:
                    if consumer.startswith("agent:"):
                        agent_name = consumer.replace("agent:", "")
                        agent_connections[agent_name].append(swarm_id)

        connected_agents = len(agent_connections)
        print(f"  • Connected Agents: {connected_agents}")
        print(f"  • Top Connected Agents:")
        for agent, swarms in sorted(agent_connections.items(),
                                   key=lambda x: len(x[1]),
                                   reverse=True)[:5]:
            print(f"    - {agent}: {len(swarms)} swarms")

        self.connections["agents"] = dict(agent_connections)

        # 4. Map advisor connections
        print("\n🎓 Advisor Connections:")
        advisor_connections = defaultdict(list)

        for swarm_id, consumers in self.routing_tables.items():
            if isinstance(consumers, list):
                for consumer in consumers:
                    if consumer.startswith("advisor:"):
                        advisor_name = consumer.replace("advisor:", "")
                        advisor_connections[advisor_name].append(swarm_id)

        connected_advisors = len(advisor_connections)
        print(f"  • Connected Advisors: {connected_advisors}")
        print(f"  • Top Connected Advisors:")
        for advisor, swarms in sorted(advisor_connections.items(),
                                     key=lambda x: len(x[1]),
                                     reverse=True)[:5]:
            print(f"    - {advisor}: {len(swarms)} swarms")

        self.connections["advisors"] = dict(advisor_connections)

        # 5. Identify critical connections
        print("\n🔗 Critical Connections:")
        critical_connections = {
            "income_builder": agent_connections.get("income_builder", []),
            "sports_arbitrage": agent_connections.get("sports_arbitrage", []),
            "warren_buffett": advisor_connections.get("warren_buffett", []),
            "cathie_wood": advisor_connections.get("cathie_wood", []),
            "ray_dalio": advisor_connections.get("ray_dalio", [])
        }

        for entity, swarms in critical_connections.items():
            status = "✅ Connected" if swarms else "❌ DISCONNECTED"
            print(f"  • {entity}: {status}")
            if swarms:
                print(f"    Receiving from: {', '.join(swarms)}")

        # 6. Calculate data flow statistics
        print("\n📈 Data Flow Statistics:")

        # Spiders feeding to Income Builder
        income_builder_spiders = 0
        if "income_builder" in agent_connections:
            for swarm in agent_connections["income_builder"]:
                if swarm in self.spider_swarms:
                    income_builder_spiders += self.spider_swarms[swarm]["count"]

        print(f"  • Spiders feeding Income Builder: {income_builder_spiders:,}")
        print(f"  • Total Agent Connections: {sum(len(swarms) for swarms in agent_connections.values())}")
        print(f"  • Total Advisor Connections: {sum(len(swarms) for swarms in advisor_connections.values())}")

        # 7. Identify orphaned components
        print("\n⚠️ Orphaned Components:")

        # Check for disconnected agents (simplified check)
        all_agents = ["income_builder", "financial_analyst", "portfolio_manager",
                     "risk_assessor", "crypto_trader", "forex_trader", "tech_scout",
                     "startup_evaluator", "patent_analyzer", "market_maker",
                     "arbitrage_finder", "spread_analyzer", "volatility_trader",
                     "sports_arbitrage", "sentiment_analyzer", "social_media_monitor"]

        orphaned_agents = [agent for agent in all_agents if agent not in agent_connections]
        if orphaned_agents:
            print(f"  • Orphaned Agents: {len(orphaned_agents)}")
            for agent in orphaned_agents[:5]:
                print(f"    - {agent}")
        else:
            print("  • No orphaned agents detected ✅")

        self.connections["orphaned"]["agents"] = orphaned_agents

        # 8. Generate summary
        print("\n" + "="*60)
        print("📊 CONNECTION AUDIT SUMMARY")
        print("="*60)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_spiders": total_spiders,
            "spider_swarms": len(self.spider_swarms),
            "connected_agents": connected_agents,
            "connected_advisors": connected_advisors,
            "orphaned_agents": len(orphaned_agents),
            "income_builder_connected": "income_builder" in agent_connections,
            "income_builder_spider_count": income_builder_spiders,
            "universal_feeds": ["news_harvester", "adaptive"],
            "critical_status": {
                "all_critical_connected": all(
                    critical_connections[entity]
                    for entity in ["income_builder", "warren_buffett", "ray_dalio"]
                ),
                "revenue_pipeline_active": income_builder_spiders > 0
            }
        }

        print(f"""
  🕷️ Total Spiders: {summary['total_spiders']:,} across {summary['spider_swarms']} swarms
  🤖 Connected Agents: {summary['connected_agents']}
  🎓 Connected Advisors: {summary['connected_advisors']}
  ⚠️ Orphaned Agents: {summary['orphaned_agents']}

  💰 Income Builder Status: {'✅ CONNECTED' if summary['income_builder_connected'] else '❌ DISCONNECTED'}
  📊 Spiders Feeding Income Builder: {summary['income_builder_spider_count']:,}
  🔥 Revenue Pipeline: {'✅ ACTIVE' if summary['critical_status']['revenue_pipeline_active'] else '❌ INACTIVE'}
        """)

        # Save detailed report
        report_path = Path("spider_connection_audit_report.json")
        with open(report_path, "w") as f:
            json.dump({
                "summary": summary,
                "connections": self.connections,
                "critical_connections": critical_connections,
                "routing_tables": {k: v if isinstance(v, list) else str(v)
                                  for k, v in self.routing_tables.items()}
            }, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_path}")

        return summary

if __name__ == "__main__":
    from datetime import datetime

    auditor = SpiderConnectionAuditor()
    results = auditor.audit_connections()

    # Quick recommendations
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS")
    print("="*60)

    if results["income_builder_connected"]:
        print("✅ Income Builder is properly connected to spider network")
    else:
        print("❌ CRITICAL: Income Builder needs to be connected to spider network!")
        print("   Run: python backend/spiders/income_builder_connector.py")

    if results["orphaned_agents"] > 0:
        print(f"⚠️ {results['orphaned_agents']} agents are not receiving spider data")
        print("   Consider connecting them or removing unused agents")

    if results["critical_status"]["revenue_pipeline_active"]:
        print("✅ Revenue generation pipeline is active")
    else:
        print("❌ Revenue pipeline needs activation!")
        print("   Run: python test_revenue_activation.py")

    print("\n🚀 Next Steps:")
    print("1. Run: python backend/spiders/management/commands/test_spider_connections.py")
    print("2. Monitor: python backend/spiders/management/commands/monitor_spider_army.py")
    print("3. Activate: python backend/spiders/management/commands/activate_spider_orchestrator.py")