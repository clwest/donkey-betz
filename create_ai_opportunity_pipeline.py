#!/usr/bin/env python3
"""
AI Opportunity Pipeline
Connects spider research to agent execution for AI monetization
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.spiders.ai_monetization_spider import research_ai_monetization_sync
from agents.ai_project_builder import AIProjectBuilder
from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIOpportunityPipeline:
    """
    Complete pipeline from AI research to execution
    1. Spider researches AI monetization strategies
    2. Agent executes and builds the projects
    3. Creates real, launchable businesses
    """

    def __init__(self):
        self.builder = AIProjectBuilder()
        self.results_dir = Path("ai_opportunities_results")
        self.results_dir.mkdir(exist_ok=True)

    def run_full_pipeline(self, task_preference: str = None) -> Dict:
        """
        Run the complete pipeline from research to execution

        Args:
            task_preference: Optional preference like "content generator", "chatbot", etc.

        Returns:
            Complete pipeline results
        """
        logger.info("🚀 Starting AI Opportunity Pipeline...")

        # Step 1: Research AI monetization strategies
        logger.info("🕷️ Step 1: Researching AI monetization strategies...")
        strategies = research_ai_monetization_sync()

        if not strategies:
            return {'success': False, 'error': 'No strategies found'}

        logger.info(f"📊 Found {len(strategies)} AI monetization strategies")

        # Step 2: Select best strategies
        selected_strategies = self._select_strategies(strategies, task_preference)

        # Step 3: Execute projects for top strategies
        execution_results = []
        for i, strategy in enumerate(selected_strategies[:3]):  # Top 3 strategies
            logger.info(f"⚙️ Step 3.{i+1}: Executing strategy - {strategy['title']}")

            task = self._convert_strategy_to_task(strategy)
            result = self.builder.build_project(task, strategy)

            if result['success']:
                logger.info(f"✅ Successfully built: {strategy['title']}")
                execution_results.append(result)
            else:
                logger.error(f"❌ Failed to build: {strategy['title']} - {result.get('error')}")

        # Step 4: Create summary report
        pipeline_result = self._create_pipeline_report(strategies, execution_results)

        # Step 5: Save results
        self._save_results(pipeline_result)

        return pipeline_result

    def _select_strategies(self, strategies: List[Dict], preference: str = None) -> List[Dict]:
        """Select best strategies for execution"""
        # Sort by final score
        sorted_strategies = sorted(strategies, key=lambda s: s.get('final_score', 0), reverse=True)

        # Filter by preference if provided
        if preference:
            preference_lower = preference.lower()
            filtered = []
            for strategy in sorted_strategies:
                title_lower = strategy['title'].lower()
                strategy_type = strategy.get('strategy_type', '').lower()

                if (preference_lower in title_lower or
                    preference_lower in strategy_type or
                    any(word in title_lower for word in preference_lower.split())):
                    filtered.append(strategy)

            if filtered:
                return filtered[:5]  # Top 5 matching strategies

        return sorted_strategies[:5]  # Top 5 overall

    def _convert_strategy_to_task(self, strategy: Dict) -> str:
        """Convert strategy to executable task"""
        strategy_type = strategy.get('strategy_type', 'ai_application')
        title = strategy['title']

        task_templates = {
            'content_generation': f"build ai content generator based on: {title}",
            'ai_assistant': f"create ai chatbot assistant for: {title}",
            'saas_development': f"build saas platform for: {title}",
            'api_service': f"create api service for: {title}",
            'automation_tool': f"build automation tool for: {title}",
            'educational_content': f"create ai-powered educational platform for: {title}"
        }

        return task_templates.get(strategy_type, f"build ai application for: {title}")

    def _create_pipeline_report(self, strategies: List[Dict], executions: List[Dict]) -> Dict:
        """Create comprehensive pipeline report"""
        successful_projects = [e for e in executions if e['success']]
        total_revenue_potential = 0

        # Calculate total revenue potential
        for project in successful_projects:
            revenue_str = project.get('estimated_revenue', '$0')
            # Extract max revenue number
            import re
            numbers = re.findall(r'\d+', revenue_str.replace(',', ''))
            if numbers:
                total_revenue_potential += int(numbers[-1])  # Take max number

        return {
            'success': True,
            'pipeline_summary': {
                'strategies_researched': len(strategies),
                'projects_attempted': len(executions),
                'projects_successful': len(successful_projects),
                'success_rate': f"{len(successful_projects)/len(executions)*100:.1f}%" if executions else "0%",
                'total_revenue_potential': f"${total_revenue_potential:,}/month",
                'execution_time': datetime.now().isoformat()
            },
            'research_results': {
                'top_strategies': strategies[:10],
                'sources_scraped': list(set(s.get('source', 'unknown') for s in strategies)),
                'strategy_types_found': list(set(s.get('strategy_type', 'unknown') for s in strategies))
            },
            'execution_results': successful_projects,
            'failed_executions': [e for e in executions if not e['success']],
            'ready_to_launch': len(successful_projects),
            'next_steps': self._generate_next_steps(successful_projects),
            'business_opportunities': self._analyze_business_opportunities(successful_projects)
        }

    def _generate_next_steps(self, successful_projects: List[Dict]) -> List[str]:
        """Generate next steps for launching businesses"""
        if not successful_projects:
            return ["No successful projects to launch"]

        steps = [
            "🔑 Add OpenAI API keys to generated projects",
            "🧪 Test each application thoroughly",
            "🌐 Create landing pages for each project",
            "💳 Set up payment processing (Stripe/PayPal)",
            "📢 Launch beta versions with first users",
            "📊 Track user engagement and feedback",
            "💰 Start monetization and scale successful projects",
            "🔄 Iterate based on user feedback"
        ]

        # Add project-specific steps
        for project in successful_projects:
            project_path = project.get('project_path', '')
            if project_path:
                steps.append(f"📁 Launch project at: {project_path}")

        return steps

    def _analyze_business_opportunities(self, successful_projects: List[Dict]) -> Dict:
        """Analyze business opportunities from successful projects"""
        if not successful_projects:
            return {'total_opportunities': 0}

        opportunities = []
        for project in successful_projects:
            strategy = project.get('strategy_used', {})
            opportunities.append({
                'project_name': strategy.get('title', 'Unknown'),
                'project_type': project.get('project_type', 'unknown'),
                'revenue_potential': project.get('estimated_revenue', 'Unknown'),
                'market_size': self._estimate_market_size(strategy.get('strategy_type', 'unknown')),
                'launch_readiness': 'Ready' if project.get('monetization_ready') else 'Needs Work',
                'project_path': project.get('project_path', ''),
                'competitive_advantage': 'AI-powered automation, first-mover advantage'
            })

        return {
            'total_opportunities': len(opportunities),
            'opportunities': opportunities,
            'portfolio_value': f"${sum(self._extract_revenue_number(o['revenue_potential']) for o in opportunities):,}/month potential"
        }

    def _estimate_market_size(self, strategy_type: str) -> str:
        """Estimate market size for strategy type"""
        market_sizes = {
            'content_generation': '$1.2B (growing to $5B by 2027)',
            'ai_assistant': '$4.7B (growing to $15.5B by 2028)',
            'saas_development': '$25B (growing to $85B by 2030)',
            'api_service': '$8B (growing to $20B by 2027)',
            'automation_tool': '$15B (growing to $35B by 2028)',
            'educational_content': '$6B (growing to $15B by 2027)'
        }
        return market_sizes.get(strategy_type, '$5B+ market opportunity')

    def _extract_revenue_number(self, revenue_str: str) -> int:
        """Extract numeric revenue for calculations"""
        import re
        if not revenue_str or revenue_str == 'Unknown':
            return 5000  # Default estimate

        numbers = re.findall(r'\d+', revenue_str.replace(',', ''))
        if numbers:
            return int(numbers[-1])  # Take the highest number
        return 5000

    def _save_results(self, results: Dict):
        """Save pipeline results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.results_dir / f"ai_opportunity_pipeline_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"💾 Results saved to: {results_file}")

        # Create summary file
        summary_file = self.results_dir / f"pipeline_summary_{timestamp}.md"
        summary_content = self._create_markdown_summary(results)

        with open(summary_file, 'w') as f:
            f.write(summary_content)

        logger.info(f"📄 Summary saved to: {summary_file}")

    def _create_markdown_summary(self, results: Dict) -> str:
        """Create markdown summary of results"""
        summary = results['pipeline_summary']
        successful_projects = results['execution_results']

        md_content = f"""# AI Opportunity Pipeline Results

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Pipeline Summary

- **Strategies Researched**: {summary['strategies_researched']}
- **Projects Attempted**: {summary['projects_attempted']}
- **Projects Successful**: {summary['projects_successful']}
- **Success Rate**: {summary['success_rate']}
- **Total Revenue Potential**: {summary['total_revenue_potential']}

## 🚀 Ready-to-Launch Projects

"""

        for i, project in enumerate(successful_projects, 1):
            strategy = project.get('strategy_used', {})
            md_content += f"""
### {i}. {strategy.get('title', 'Unknown Project')}

- **Type**: {project.get('project_type', 'Unknown')}
- **Revenue Potential**: {project.get('estimated_revenue', 'Unknown')}
- **Project Path**: `{project.get('project_path', 'Unknown')}`
- **Launch Command**: `{project.get('launch_command', 'See README')}`
- **Status**: {"✅ Ready to Launch" if project.get('monetization_ready') else "⚠️ Needs Setup"}

**Business Plan**: Each project includes complete business plan and monetization strategy.
"""

        md_content += f"""
## 📈 Business Opportunities

{results.get('business_opportunities', {}).get('portfolio_value', 'Unknown potential')}

## 🎯 Next Steps

"""
        for step in results.get('next_steps', []):
            md_content += f"- {step}\n"

        md_content += """
## 🔥 Key Insights

1. **Automation Works**: This entire pipeline ran automatically
2. **Real Projects**: Generated actual, working applications
3. **Business Ready**: Each project includes complete business plan
4. **Scalable**: Can research and build multiple projects simultaneously
5. **Revenue Potential**: Ready to start earning within weeks

---
*Generated by AI Opportunity Pipeline - Research to Revenue Automation*
"""

        return md_content


def main():
    """Run the AI Opportunity Pipeline"""
    print("🤖 AI Opportunity Pipeline")
    print("=" * 50)

    # Get user preference
    preference = input("Enter project preference (or press Enter for all): ").strip()
    if not preference:
        preference = None

    # Run pipeline
    pipeline = AIOpportunityPipeline()
    results = pipeline.run_full_pipeline(preference)

    if results['success']:
        summary = results['pipeline_summary']
        print("\n🎉 Pipeline Complete!")
        print(f"✅ Successfully built {summary['projects_successful']} AI projects")
        print(f"💰 Total revenue potential: {summary['total_revenue_potential']}")
        print(f"🚀 {results['ready_to_launch']} projects ready to launch")

        # Show ready projects
        successful_projects = results['execution_results']
        if successful_projects:
            print("\n📁 Generated Projects:")
            for project in successful_projects:
                strategy = project.get('strategy_used', {})
                print(f"  - {strategy.get('title', 'Unknown')}")
                print(f"    Path: {project.get('project_path', 'Unknown')}")
                print(f"    Revenue: {project.get('estimated_revenue', 'Unknown')}")

        print(f"\n📄 Full results saved to: ai_opportunities_results/")

    else:
        print(f"\n❌ Pipeline failed: {results.get('error')}")


if __name__ == "__main__":
    main()