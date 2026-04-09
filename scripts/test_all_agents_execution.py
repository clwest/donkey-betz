#!/usr/bin/env python
"""
Agent Execution Test Suite - Session 638
=========================================

Tests actual execution of all 71 agents with relevant tasks.
Each agent gets a task appropriate to its purpose.

Usage:
    # Test all agents
    DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python scripts/test_all_agents_execution.py

    # Test specific category
    DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python scripts/test_all_agents_execution.py --category stocks

    # Test single agent
    DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python scripts/test_all_agents_execution.py --agent ResearchAgent
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.agent_router import AgentRouter

# Define test tasks for each agent
AGENT_TESTS = {
    # Creation Agents
    "ImageAgent": "Create a simple logo concept for a tech startup called 'NeuralFlow'",
    "VideoAgent": "Generate a 5-second intro animation concept for a YouTube channel",
    "AudioAgent": "Create a short podcast intro script with voice direction",
    "ThreeDAgent": "Design a 3D model concept for a futuristic coffee mug",

    # Editing Agents
    "ImageEditingAgent": "Describe how to upscale and enhance a low-resolution photo",
    "VideoEditingAgent": "Create an editing plan for a 30-second promotional video",

    # Research Agents
    "ResearchAgent": "Research the latest trends in artificial intelligence for 2025",

    # Writing Agents
    "ContentWriterAgent": "Write a short paragraph about the benefits of meditation",

    # Strategy Agents
    "ContentStrategyAgent": "Create a content strategy outline for a fitness brand",
    "BrandIdentityAgent": "Suggest brand identity elements for a sustainable fashion company",
    "SEOOptimizerAgent": "Suggest SEO keywords for an article about remote work",
    "SocialMediaAgent": "Create a social media post plan for launching a new app",

    # Executive Agents
    "CTOAgent": "Evaluate the technical feasibility of building a mobile app",
    "COOAgent": "Create an operations plan for a small e-commerce business",
    "CreativeDirectorAgent": "Provide creative direction for a brand refresh campaign",
    "MeetingCoordinatorAgent": "Plan an agenda for a product launch meeting",

    # Analysis Agents
    "TrendAnalysisAgent": "Analyze current trends in sustainable technology",
    "OpportunityScoringAgent": "Score this opportunity: Launch a podcast about AI",
    "MarketIntelligenceAgent": "Provide market intelligence on the EV charging industry",

    # Training Agents
    "CharacterTrainingAgent": "Describe the process to train a custom character model",
    "TrainedCreationAgent": "Generate an image using a trained character concept",

    # Security Agents
    "MemoryIsolationAgent": "Check memory isolation status for the current session",
    "ContentAuditAgent": "Audit this content for policy compliance: 'Buy our product now!'",

    # Business Agents
    "CompetitorAnalysisAgent": "Analyze competitors in the meal delivery space",
    "CustomerResearchAgent": "Create a customer persona for a meditation app",
    "BrandStrategyAgent": "Develop a brand strategy for a new coffee shop chain",
    "MarketingStrategyAgent": "Create a marketing strategy for a B2B SaaS product",

    # Legal Agents
    "LegalDocDrafterAgent": "Draft an outline for a basic non-disclosure agreement",

    # Development Agents
    "CodeGeneratorAgent": "Generate a Python function to calculate factorial",
    "FullStackDeveloperAgent": "Design a REST API endpoint for user authentication",
    "CodeReviewAgent": "Review this code: def add(a,b): return a+b",
    "DevOpsAgent": "Create a deployment checklist for a Django application",

    # Stock Agents
    "StockAuditCoordinator": "Coordinate an audit of AAPL stock performance",
    "StockAnalystAgent": "Analyze the current state of TSLA stock",
    "MarketMovementMonitorAgent": "Monitor recent market movements in tech sector",
    "InstitutionalWatcherAgent": "Check institutional holdings for NVDA",
    "MarketAnomalyDetectorAgent": "Detect any anomalies in recent market activity",
    "BullCaseAgent": "Present the bull case for investing in AI companies",
    "BearCaseAgent": "Present the bear case for the current stock market",
    "SignalScannerAgent": "Scan for trading signals in the semiconductor sector",
    "MarketIntelligenceCoordinator": "Coordinate market intelligence gathering for crypto",

    # Blockchain Agents
    "BlockchainAuditCoordinator": "Coordinate an audit of Ethereum smart contracts",
    "SmartContractAuditorAgent": "Audit a simple ERC-20 token contract concept",
    "TransactionMonitorAgent": "Monitor recent large transactions on Ethereum",
    "WhaleWatcherAgent": "Watch for whale movements in Bitcoin",
    "ExploitDetectorAgent": "Check for common smart contract vulnerabilities",

    # Narrative Agents
    "NarrativeDriftCoordinator": "Analyze narrative drift in AI technology coverage",
    "NarrativeHistorianAgent": "Trace the historical narrative of electric vehicles",
    "TrendBreakDetectorAgent": "Detect any narrative breaks in climate change coverage",
    "CulturalImpactAgent": "Assess cultural impact of social media on Gen Z",

    # Content Studio Agents
    "AutonomousContentStudioCoordinator": "Plan content for an AI-focused YouTube channel",
    "TopicMinerAgent": "Mine trending topics in the technology space",
    "ContrarianAgent": "Provide contrarian view on AI hype",
    "PerformanceAnalystAgent": "Analyze content performance metrics",

    # Podcast Agents
    "PodcastCoordinatorAgent": "Plan a podcast episode about future of work",
    "DebateAdvocateAgent": "Argue in favor of remote work being the future",
    "DebateSkepticAgent": "Argue against fully remote work policies",
    "ModeratorAgent": "Moderate a debate about AI regulation",

    # Rendering Agents
    "ResolveAgent": "Create a color grading plan for a short film",

    # Orchestration Agents
    "WorkflowAgent": "Create a workflow for content creation process",
    "WorkflowOrchestrationAgent": "Orchestrate a multi-step research workflow",
    "OpportunityPipelineAgent": "Build an opportunity pipeline for freelance work",
    "ContentExecutorAgent": "Execute a content creation plan for a blog post",
    "CampaignOrchestratorAgent": "Orchestrate a marketing campaign for product launch",
    "AISeriesWorkflowAgent": "Plan a series of AI-generated educational videos",

    # Markets Agents
    "PredictionMarketAnalyst": "Analyze prediction markets for 2025 elections",
    "SportsOddsAnalyst": "Analyze odds for upcoming NFL games",
    "ArbitrageDetector": "Detect arbitrage opportunities in sports betting",

    # Utility Agents
    "ThinkingAgent": "Think through the implications of AGI development",
    "TechnicalDocumentAgent": "Create technical documentation outline for an API",
}

def test_agent(agent_name: str, task: str, timeout: int = 120) -> dict:
    """Test a single agent with a task."""
    result = {
        "agent": agent_name,
        "task": task[:50] + "..." if len(task) > 50 else task,
        "success": False,
        "time_seconds": 0,
        "message": "",
        "error": None
    }

    start_time = time.time()

    try:
        router = AgentRouter(user=None)
        agent_result = router.route(agent_name, task, {})

        result["time_seconds"] = round(time.time() - start_time, 2)
        result["success"] = agent_result.success
        result["message"] = agent_result.message[:100] if agent_result.message else "No message"

        if not agent_result.success:
            result["error"] = agent_result.error

    except Exception as e:
        result["time_seconds"] = round(time.time() - start_time, 2)
        result["error"] = str(e)[:200]

    return result

def print_result(result: dict, index: int, total: int):
    """Print a single test result."""
    status = "✅" if result["success"] else "❌"
    time_str = f"{result['time_seconds']}s"

    print(f"\n[{index}/{total}] {status} {result['agent']} ({time_str})")
    print(f"    Task: {result['task']}")

    if result["success"]:
        print(f"    Message: {result['message'][:80]}...")
    else:
        print(f"    Error: {result['error'][:80] if result['error'] else 'Unknown error'}...")

def run_tests(agents_to_test: dict, category: str = None) -> list:
    """Run tests for specified agents."""
    results = []
    total = len(agents_to_test)

    print("=" * 60)
    print(f"AGENT EXECUTION TEST SUITE")
    print(f"Testing {total} agents")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for i, (agent_name, task) in enumerate(agents_to_test.items(), 1):
        result = test_agent(agent_name, task)
        results.append(result)
        print_result(result, i, total)

    return results

def print_summary(results: list):
    """Print test summary."""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    total_time = sum(r["time_seconds"] for r in results)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Agents Tested: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Average Time: {total_time/len(results):.1f}s per agent")

    if failed:
        print(f"\n❌ FAILED AGENTS ({len(failed)}):")
        for r in failed:
            print(f"  - {r['agent']}: {r['error'][:60] if r['error'] else 'Unknown'}...")

    if successful:
        print(f"\n✅ SUCCESSFUL AGENTS ({len(successful)}):")
        for r in sorted(successful, key=lambda x: x["time_seconds"]):
            print(f"  - {r['agent']} ({r['time_seconds']}s)")

    print("\n" + "=" * 60)

def save_results(results: list, filename: str = None):
    """Save results to JSON file."""
    if not filename:
        filename = f"agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    filepath = f"/Users/donkeyking/development/unified-donkey-betz/logs/{filename}"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(results),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to: {filepath}")

# Agent categories for group testing
AGENT_CATEGORIES = {
    "creation": ["ImageAgent", "VideoAgent", "AudioAgent", "ThreeDAgent"],
    "editing": ["ImageEditingAgent", "VideoEditingAgent"],
    "research": ["ResearchAgent"],
    "writing": ["ContentWriterAgent"],
    "strategy": ["ContentStrategyAgent", "BrandIdentityAgent", "SEOOptimizerAgent", "SocialMediaAgent"],
    "executive": ["CTOAgent", "COOAgent", "CreativeDirectorAgent", "MeetingCoordinatorAgent"],
    "analysis": ["TrendAnalysisAgent", "OpportunityScoringAgent", "MarketIntelligenceAgent"],
    "training": ["CharacterTrainingAgent", "TrainedCreationAgent"],
    "security": ["MemoryIsolationAgent", "ContentAuditAgent"],
    "business": ["CompetitorAnalysisAgent", "CustomerResearchAgent", "BrandStrategyAgent", "MarketingStrategyAgent"],
    "legal": ["LegalDocDrafterAgent"],
    "development": ["CodeGeneratorAgent", "FullStackDeveloperAgent", "CodeReviewAgent", "DevOpsAgent"],
    "stocks": ["StockAuditCoordinator", "StockAnalystAgent", "MarketMovementMonitorAgent",
               "InstitutionalWatcherAgent", "MarketAnomalyDetectorAgent", "BullCaseAgent",
               "BearCaseAgent", "SignalScannerAgent", "MarketIntelligenceCoordinator"],
    "blockchain": ["BlockchainAuditCoordinator", "SmartContractAuditorAgent",
                   "TransactionMonitorAgent", "WhaleWatcherAgent", "ExploitDetectorAgent"],
    "narrative": ["NarrativeDriftCoordinator", "NarrativeHistorianAgent",
                  "TrendBreakDetectorAgent", "CulturalImpactAgent"],
    "content_studio": ["AutonomousContentStudioCoordinator", "TopicMinerAgent",
                       "ContrarianAgent", "PerformanceAnalystAgent"],
    "podcast": ["PodcastCoordinatorAgent", "DebateAdvocateAgent", "DebateSkepticAgent", "ModeratorAgent"],
    "rendering": ["ResolveAgent"],
    "orchestration": ["WorkflowAgent", "WorkflowOrchestrationAgent", "OpportunityPipelineAgent",
                      "ContentExecutorAgent", "CampaignOrchestratorAgent", "AISeriesWorkflowAgent"],
    "markets": ["PredictionMarketAnalyst", "SportsOddsAnalyst", "ArbitrageDetector"],
    "utility": ["ThinkingAgent", "TechnicalDocumentAgent"],
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test agent execution")
    parser.add_argument("--agent", help="Test specific agent")
    parser.add_argument("--category", help="Test specific category")
    parser.add_argument("--save", action="store_true", help="Save results to file")
    args = parser.parse_args()

    # Determine which agents to test
    if args.agent:
        if args.agent not in AGENT_TESTS:
            print(f"Unknown agent: {args.agent}")
            print(f"Available: {', '.join(sorted(AGENT_TESTS.keys()))}")
            sys.exit(1)
        agents_to_test = {args.agent: AGENT_TESTS[args.agent]}
    elif args.category:
        if args.category not in AGENT_CATEGORIES:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(sorted(AGENT_CATEGORIES.keys()))}")
            sys.exit(1)
        agents_to_test = {a: AGENT_TESTS[a] for a in AGENT_CATEGORIES[args.category]}
    else:
        agents_to_test = AGENT_TESTS

    # Run tests
    results = run_tests(agents_to_test)
    print_summary(results)

    if args.save:
        save_results(results)
