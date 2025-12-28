"""
Opportunity AI Analyzer - AI-Powered Opportunity Analysis and Automation Detection

This module analyzes opportunities to determine which can be automated by AI agents,
matches them with capable agents, and creates application plans for automated execution.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.llm_enforcer import LLMEnforcer
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry, AdvisorDomain

logger = logging.getLogger(__name__)


class AutomationLevel(Enum):
    """Levels of automation for opportunities"""
    NONE = "none"                    # Cannot be automated
    PARTIAL = "partial"              # Some steps can be automated
    SUBSTANTIAL = "substantial"      # Most steps can be automated
    FULL = "full"                   # Fully automatable


class OpportunityType(Enum):
    """Types of opportunities that can be analyzed"""
    JOB_APPLICATION = "job_application"
    FREELANCE_GIG = "freelance_gig"
    BUSINESS_OPPORTUNITY = "business_opportunity"
    INVESTMENT_OPPORTUNITY = "investment_opportunity"
    LEARNING_OPPORTUNITY = "learning_opportunity"
    NETWORKING_OPPORTUNITY = "networking_opportunity"


@dataclass
class AutomationCapability:
    """Represents an automation capability for an opportunity"""
    capability_name: str
    description: str
    required_agent_types: List[str]
    confidence_score: float
    automation_steps: List[str]
    estimated_time_saved_hours: float
    risk_level: str  # "low", "medium", "high"


@dataclass
class OpportunityAnalysis:
    """Complete analysis of an opportunity for automation potential"""
    opportunity_id: str
    opportunity_type: OpportunityType
    automation_level: AutomationLevel
    automation_score: float  # 0.0 to 1.0

    # Automation details
    can_automate: List[str]  # Steps that can be automated
    cannot_automate: List[str]  # Steps requiring human intervention
    recommended_agents: List[Dict[str, Any]]
    recommended_advisors: List[Dict[str, Any]]

    # Execution plan
    automation_workflow: List[Dict[str, Any]]
    estimated_success_rate: float
    estimated_time_savings: float
    required_human_approval: bool

    # Risk assessment
    automation_risks: List[str]
    mitigation_strategies: List[str]

    # Performance tracking
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    confidence_level: float = 0.0
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)


class OpportunityAIAnalyzer:
    """
    AI-powered analyzer for opportunity automation detection and planning.

    This class uses LLM capabilities to analyze opportunities and determine
    which aspects can be automated by agents or require advisor consultation.
    """

    def __init__(self):
        self.llm_enforcer = LLMEnforcer()
        self.agent_registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()
        self.logger = logging.getLogger(__name__)

        # Initialize capability mapping
        self._initialize_capability_mapping()

    def _initialize_capability_mapping(self):
        """Initialize mapping of opportunity types to automation capabilities"""
        self.capability_mapping = {
            OpportunityType.JOB_APPLICATION: {
                'research_company': {
                    'agents': ['research', 'web_scraper', 'data_analyst'],
                    'automation_level': 'full',
                    'confidence': 0.9
                },
                'analyze_job_requirements': {
                    'agents': ['nlp_processor', 'requirements_analyst'],
                    'automation_level': 'full',
                    'confidence': 0.85
                },
                'match_skills': {
                    'agents': ['skill_matcher', 'profile_analyzer'],
                    'automation_level': 'full',
                    'confidence': 0.8
                },
                'generate_cover_letter': {
                    'agents': ['content_generator', 'writing_assistant'],
                    'automation_level': 'substantial',
                    'confidence': 0.75
                },
                'submit_application': {
                    'agents': ['form_filler', 'automation_bot'],
                    'automation_level': 'partial',
                    'confidence': 0.6
                },
                'follow_up': {
                    'agents': ['communication_bot', 'follow_up_scheduler'],
                    'automation_level': 'partial',
                    'confidence': 0.7
                }
            },
            OpportunityType.FREELANCE_GIG: {
                'analyze_requirements': {
                    'agents': ['requirements_analyst', 'scope_analyzer'],
                    'automation_level': 'full',
                    'confidence': 0.85
                },
                'estimate_pricing': {
                    'agents': ['pricing_analyst', 'market_researcher'],
                    'automation_level': 'substantial',
                    'confidence': 0.75
                },
                'create_proposal': {
                    'agents': ['proposal_writer', 'content_generator'],
                    'automation_level': 'substantial',
                    'confidence': 0.8
                },
                'negotiate_terms': {
                    'agents': ['negotiation_assistant'],
                    'automation_level': 'partial',
                    'confidence': 0.5
                }
            },
            OpportunityType.INVESTMENT_OPPORTUNITY: {
                'research_investment': {
                    'agents': ['financial_researcher', 'market_analyst'],
                    'automation_level': 'full',
                    'confidence': 0.9
                },
                'analyze_financials': {
                    'agents': ['financial_analyst', 'risk_assessor'],
                    'automation_level': 'full',
                    'confidence': 0.85
                },
                'compare_alternatives': {
                    'agents': ['comparison_engine', 'decision_matrix'],
                    'automation_level': 'substantial',
                    'confidence': 0.8
                },
                'execute_transaction': {
                    'agents': ['trading_bot', 'execution_engine'],
                    'automation_level': 'partial',
                    'confidence': 0.4
                }
            }
        }

    def analyze_opportunity(self, opportunity: Dict[str, Any], user_profile: Dict[str, Any]) -> OpportunityAnalysis:
        """
        Analyze an opportunity for automation potential.

        Args:
            opportunity: Opportunity data to analyze
            user_profile: User profile for personalization

        Returns:
            Complete opportunity analysis with automation recommendations
        """
        try:
            # Determine opportunity type
            opp_type = self._classify_opportunity_type(opportunity)

            # Perform AI-powered analysis
            ai_analysis = self._perform_ai_analysis(opportunity, user_profile, opp_type)

            # Map to automation capabilities
            automation_capabilities = self._map_automation_capabilities(opp_type, opportunity)

            # Find suitable agents
            recommended_agents = self._find_suitable_agents(automation_capabilities, opportunity)

            # Find relevant advisors
            recommended_advisors = self._find_relevant_advisors(opportunity, opp_type)

            # Calculate automation score
            automation_score = self._calculate_automation_score(automation_capabilities, ai_analysis)

            # Determine automation level
            automation_level = self._determine_automation_level(automation_score)

            # Create automation workflow
            automation_workflow = self._create_automation_workflow(
                automation_capabilities, recommended_agents, opportunity
            )

            # Assess risks
            risks, mitigations = self._assess_automation_risks(automation_workflow, opportunity)

            # Create analysis result
            analysis = OpportunityAnalysis(
                opportunity_id=opportunity.get('id', f"opp_{datetime.now().timestamp()}"),
                opportunity_type=opp_type,
                automation_level=automation_level,
                automation_score=automation_score,
                can_automate=self._extract_automatable_steps(automation_capabilities),
                cannot_automate=self._extract_manual_steps(automation_capabilities, opportunity),
                recommended_agents=recommended_agents,
                recommended_advisors=recommended_advisors,
                automation_workflow=automation_workflow,
                estimated_success_rate=self._estimate_success_rate(automation_capabilities),
                estimated_time_savings=self._estimate_time_savings(automation_capabilities),
                required_human_approval=self._requires_human_approval(automation_level, opportunity),
                automation_risks=risks,
                mitigation_strategies=mitigations,
                confidence_level=ai_analysis.get('confidence', 0.7),
                analysis_metadata={
                    'ai_analysis': ai_analysis,
                    'opportunity_data': opportunity,
                    'user_profile_used': bool(user_profile)
                }
            )

            self.logger.info(f"✅ Analyzed opportunity {opportunity.get('title', 'Unknown')} - "
                           f"Automation Level: {automation_level.value}, Score: {automation_score:.2f}")

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing opportunity: {e}")
            # Return basic analysis with error info
            return OpportunityAnalysis(
                opportunity_id=opportunity.get('id', 'error'),
                opportunity_type=OpportunityType.JOB_APPLICATION,
                automation_level=AutomationLevel.NONE,
                automation_score=0.0,
                can_automate=[],
                cannot_automate=['Error in analysis'],
                recommended_agents=[],
                recommended_advisors=[],
                automation_workflow=[],
                estimated_success_rate=0.0,
                estimated_time_savings=0.0,
                required_human_approval=True,
                automation_risks=[f"Analysis error: {str(e)}"],
                mitigation_strategies=['Manual review required'],
                analysis_metadata={'error': str(e)}
            )

    def _classify_opportunity_type(self, opportunity: Dict[str, Any]) -> OpportunityType:
        """Classify the type of opportunity based on its content"""
        try:
            # Use opportunity type if provided
            if 'type' in opportunity:
                type_mapping = {
                    'job': OpportunityType.JOB_APPLICATION,
                    'gig': OpportunityType.FREELANCE_GIG,
                    'freelance': OpportunityType.FREELANCE_GIG,
                    'business': OpportunityType.BUSINESS_OPPORTUNITY,
                    'investment': OpportunityType.INVESTMENT_OPPORTUNITY,
                    'learning': OpportunityType.LEARNING_OPPORTUNITY,
                    'networking': OpportunityType.NETWORKING_OPPORTUNITY
                }

                opp_type = type_mapping.get(opportunity['type'].lower())
                if opp_type:
                    return opp_type

            # Analyze content for classification
            content = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()

            # Job application keywords
            if any(keyword in content for keyword in ['job', 'position', 'role', 'employment', 'hire', 'salary']):
                return OpportunityType.JOB_APPLICATION

            # Freelance/gig keywords
            if any(keyword in content for keyword in ['freelance', 'gig', 'contract', 'project', 'hourly']):
                return OpportunityType.FREELANCE_GIG

            # Investment keywords
            if any(keyword in content for keyword in ['invest', 'stock', 'fund', 'return', 'portfolio']):
                return OpportunityType.INVESTMENT_OPPORTUNITY

            # Business keywords
            if any(keyword in content for keyword in ['business', 'partnership', 'venture', 'startup']):
                return OpportunityType.BUSINESS_OPPORTUNITY

            # Default to job application
            return OpportunityType.JOB_APPLICATION

        except Exception as e:
            self.logger.error(f"Error classifying opportunity type: {e}")
            return OpportunityType.JOB_APPLICATION

    def _perform_ai_analysis(self, opportunity: Dict[str, Any], user_profile: Dict[str, Any], opp_type: OpportunityType) -> Dict[str, Any]:
        """Use AI to analyze the opportunity for automation potential"""
        try:
            # Build analysis prompt
            prompt = f"""
            Analyze this {opp_type.value.replace('_', ' ')} opportunity for AI automation potential:

            Opportunity Details:
            Title: {opportunity.get('title', 'N/A')}
            Description: {opportunity.get('description', 'N/A')}
            Requirements: {opportunity.get('requirements', [])}
            Company: {opportunity.get('company', 'N/A')}
            Location: {opportunity.get('location', 'N/A')}

            User Profile:
            Skills: {user_profile.get('skills', {}).get('top_skills', [])}
            Goals: {user_profile.get('goals', [])}
            Experience: {user_profile.get('user_role', 'N/A')}

            Please analyze:
            1. Which steps in applying/pursuing this opportunity can be automated
            2. What level of human oversight is needed
            3. What are the risks of automation
            4. Confidence level in automation success (0-100%)
            5. Specific challenges that might prevent automation

            Respond in JSON format with keys: automatable_steps, manual_steps, confidence, risks, challenges
            """

            # Get AI analysis
            ai_result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                context="Opportunity automation analysis",
                agent_name="OpportunityAnalyzer",
                task_type="analysis",
                max_tokens=800,
                temperature=0.3
            )

            if ai_result['success']:
                try:
                    # Try to parse JSON response
                    analysis = json.loads(ai_result['response'])
                    analysis['ai_generated'] = True
                    return analysis
                except json.JSONDecodeError:
                    # If not JSON, parse text response
                    return self._parse_text_analysis(ai_result['response'])
            else:
                # Fallback to rule-based analysis
                return self._fallback_analysis(opportunity, opp_type)

        except Exception as e:
            self.logger.warning(f"AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(opportunity, opp_type)

    def _fallback_analysis(self, opportunity: Dict[str, Any], opp_type: OpportunityType) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        # Rule-based analysis based on opportunity type
        if opp_type == OpportunityType.JOB_APPLICATION:
            return {
                'automatable_steps': ['research company', 'analyze requirements', 'match skills'],
                'manual_steps': ['final review', 'interview preparation', 'salary negotiation'],
                'confidence': 75,
                'risks': ['Generic applications', 'Missing personal touch'],
                'challenges': ['Company-specific requirements', 'Custom questions'],
                'ai_generated': False
            }
        elif opp_type == OpportunityType.FREELANCE_GIG:
            return {
                'automatable_steps': ['requirements analysis', 'initial proposal draft'],
                'manual_steps': ['custom pricing', 'client communication', 'final negotiation'],
                'confidence': 65,
                'risks': ['Underbidding', 'Scope misunderstanding'],
                'challenges': ['Unique client needs', 'Creative requirements'],
                'ai_generated': False
            }
        else:
            return {
                'automatable_steps': ['research', 'initial analysis'],
                'manual_steps': ['final decision', 'execution', 'monitoring'],
                'confidence': 50,
                'risks': ['Incomplete analysis', 'Market changes'],
                'challenges': ['Complex requirements', 'High stakes decisions'],
                'ai_generated': False
            }

    def _parse_text_analysis(self, text_response: str) -> Dict[str, Any]:
        """Parse text AI response into structured data"""
        try:
            # Simple text parsing
            lines = text_response.split('\n')
            analysis = {
                'automatable_steps': [],
                'manual_steps': [],
                'confidence': 50,
                'risks': [],
                'challenges': [],
                'ai_generated': True
            }

            current_section = None
            for line in lines:
                line = line.strip()
                if 'automatable' in line.lower():
                    current_section = 'automatable_steps'
                elif 'manual' in line.lower():
                    current_section = 'manual_steps'
                elif 'risk' in line.lower():
                    current_section = 'risks'
                elif 'challenge' in line.lower():
                    current_section = 'challenges'
                elif 'confidence' in line.lower():
                    # Extract confidence number
                    import re
                    confidence_match = re.search(r'(\d+)', line)
                    if confidence_match:
                        analysis['confidence'] = int(confidence_match.group(1))
                elif line.startswith('-') or line.startswith('•') and current_section:
                    # Extract bullet point
                    item = line[1:].strip()
                    if item and current_section in analysis:
                        analysis[current_section].append(item)

            return analysis

        except Exception as e:
            self.logger.error(f"Error parsing text analysis: {e}")
            return self._fallback_analysis({}, OpportunityType.JOB_APPLICATION)

    def _map_automation_capabilities(self, opp_type: OpportunityType, opportunity: Dict[str, Any]) -> List[AutomationCapability]:
        """Map opportunity to specific automation capabilities"""
        capabilities = []

        if opp_type in self.capability_mapping:
            capability_map = self.capability_mapping[opp_type]

            for cap_name, cap_data in capability_map.items():
                capability = AutomationCapability(
                    capability_name=cap_name,
                    description=f"Automate {cap_name.replace('_', ' ')} for this {opp_type.value.replace('_', ' ')}",
                    required_agent_types=cap_data['agents'],
                    confidence_score=cap_data['confidence'],
                    automation_steps=self._generate_automation_steps(cap_name, opp_type),
                    estimated_time_saved_hours=self._estimate_time_saved(cap_name),
                    risk_level=self._assess_capability_risk(cap_name, cap_data['automation_level'])
                )
                capabilities.append(capability)

        return capabilities

    def _find_suitable_agents(self, capabilities: List[AutomationCapability], opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find agents suitable for automating the opportunity"""
        suitable_agents = []

        for capability in capabilities:
            for agent_type in capability.required_agent_types:
                # Find agents matching this type
                agents = self.agent_registry.list_agents()

                for agent in agents:
                    agent_name = agent.get('name', '').lower()
                    agent_spec = agent.get('specialization', '').lower()
                    agent_caps = [cap.lower() for cap in agent.get('capabilities', [])]

                    # Check if agent matches requirements
                    if (agent_type in agent_name or
                        agent_type in agent_spec or
                        any(agent_type in cap for cap in agent_caps)):

                        agent_data = {
                            'agent_id': agent.get('id'),
                            'name': agent.get('name'),
                            'specialization': agent.get('specialization'),
                            'capabilities': agent.get('capabilities', []),
                            'automation_capability': capability.capability_name,
                            'confidence': capability.confidence_score,
                            'estimated_time_saved': capability.estimated_time_saved_hours
                        }

                        # Avoid duplicates
                        if not any(a['name'] == agent_data['name'] for a in suitable_agents):
                            suitable_agents.append(agent_data)

                        # Limit to top matches
                        if len(suitable_agents) >= 10:
                            break

            if len(suitable_agents) >= 10:
                break

        # Sort by confidence score
        suitable_agents.sort(key=lambda x: x['confidence'], reverse=True)
        return suitable_agents[:5]  # Top 5 agents

    def _find_relevant_advisors(self, opportunity: Dict[str, Any], opp_type: OpportunityType) -> List[Dict[str, Any]]:
        """Find advisors relevant for this opportunity type"""
        try:
            # Map opportunity type to advisor domains
            domain_mapping = {
                OpportunityType.JOB_APPLICATION: [AdvisorDomain.CAREER_COACHING, AdvisorDomain.NEGOTIATION_STRATEGY],
                OpportunityType.FREELANCE_GIG: [AdvisorDomain.BUSINESS_STRATEGY, AdvisorDomain.SALES_OPTIMIZATION],
                OpportunityType.BUSINESS_OPPORTUNITY: [AdvisorDomain.BUSINESS_STRATEGY, AdvisorDomain.STARTUP_CONSULTING],
                OpportunityType.INVESTMENT_OPPORTUNITY: [AdvisorDomain.INVESTMENT_STRATEGY, AdvisorDomain.RISK_MANAGEMENT],
                OpportunityType.LEARNING_OPPORTUNITY: [AdvisorDomain.EDUCATION_STRATEGY, AdvisorDomain.CAREER_COACHING],
                OpportunityType.NETWORKING_OPPORTUNITY: [AdvisorDomain.CAREER_COACHING, AdvisorDomain.MARKETING_STRATEGY]
            }

            relevant_domains = domain_mapping.get(opp_type, [AdvisorDomain.BUSINESS_STRATEGY])
            recommended_advisors = []

            for domain in relevant_domains:
                advisors = self.advisor_registry.list_advisors(domain=domain)

                for advisor in advisors[:3]:  # Top 3 per domain
                    advisor_data = {
                        'advisor_id': advisor.id,
                        'name': advisor.name,
                        'title': advisor.title,
                        'domain': advisor.domain.value,
                        'expertise_level': advisor.expertise_level.value,
                        'specializations': advisor.specializations,
                        'typical_duration': advisor.typical_engagement_duration,
                        'satisfaction_rating': advisor.satisfaction_rating
                    }
                    recommended_advisors.append(advisor_data)

            # Sort by expertise level and satisfaction
            expertise_order = {'legend': 4, 'master': 3, 'expert': 2, 'specialist': 1}
            recommended_advisors.sort(
                key=lambda x: (expertise_order.get(x['expertise_level'], 0), x['satisfaction_rating']),
                reverse=True
            )

            return recommended_advisors[:3]  # Top 3 overall

        except Exception as e:
            self.logger.error(f"Error finding relevant advisors: {e}")
            return []

    def _calculate_automation_score(self, capabilities: List[AutomationCapability], ai_analysis: Dict[str, Any]) -> float:
        """Calculate overall automation score for the opportunity"""
        if not capabilities:
            return 0.0

        # Weight factors
        capability_score = sum(cap.confidence_score for cap in capabilities) / len(capabilities)
        ai_confidence = ai_analysis.get('confidence', 50) / 100.0

        # Calculate weighted score
        automation_score = (capability_score * 0.6) + (ai_confidence * 0.4)

        # Apply penalties for high-risk items
        high_risk_capabilities = [cap for cap in capabilities if cap.risk_level == 'high']
        if high_risk_capabilities:
            risk_penalty = len(high_risk_capabilities) / len(capabilities) * 0.2
            automation_score = max(0.0, automation_score - risk_penalty)

        return min(1.0, automation_score)

    def _determine_automation_level(self, automation_score: float) -> AutomationLevel:
        """Determine automation level based on score"""
        if automation_score >= 0.8:
            return AutomationLevel.FULL
        elif automation_score >= 0.6:
            return AutomationLevel.SUBSTANTIAL
        elif automation_score >= 0.3:
            return AutomationLevel.PARTIAL
        else:
            return AutomationLevel.NONE

    def _create_automation_workflow(self, capabilities: List[AutomationCapability],
                                  agents: List[Dict[str, Any]], opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create step-by-step automation workflow"""
        workflow = []

        # Sort capabilities by logical execution order
        ordered_capabilities = sorted(capabilities, key=lambda x: self._get_execution_order(x.capability_name))

        for i, capability in enumerate(ordered_capabilities):
            # Find best agent for this capability
            suitable_agent = None
            for agent in agents:
                if agent.get('automation_capability') == capability.capability_name:
                    suitable_agent = agent
                    break

            step = {
                'step_number': i + 1,
                'capability': capability.capability_name,
                'description': capability.description,
                'agent': suitable_agent['name'] if suitable_agent else 'Manual execution required',
                'agent_id': suitable_agent['agent_id'] if suitable_agent else None,
                'automation_steps': capability.automation_steps,
                'estimated_duration_hours': capability.estimated_time_saved_hours,
                'confidence': capability.confidence_score,
                'risk_level': capability.risk_level,
                'requires_approval': capability.risk_level in ['medium', 'high'],
                'fallback_plan': self._create_fallback_plan(capability)
            }
            workflow.append(step)

        return workflow

    def _get_execution_order(self, capability_name: str) -> int:
        """Get logical execution order for capability"""
        order_map = {
            'research_company': 1,
            'research_investment': 1,
            'analyze_requirements': 2,
            'analyze_job_requirements': 2,
            'analyze_financials': 2,
            'match_skills': 3,
            'estimate_pricing': 3,
            'compare_alternatives': 3,
            'generate_cover_letter': 4,
            'create_proposal': 4,
            'submit_application': 5,
            'negotiate_terms': 5,
            'execute_transaction': 5,
            'follow_up': 6
        }
        return order_map.get(capability_name, 99)

    def _create_fallback_plan(self, capability: AutomationCapability) -> str:
        """Create fallback plan if automation fails"""
        return f"If {capability.capability_name} automation fails, manual execution with human oversight required. " \
               f"Estimated additional time: {capability.estimated_time_saved_hours * 2} hours."

    def _extract_automatable_steps(self, capabilities: List[AutomationCapability]) -> List[str]:
        """Extract list of steps that can be automated"""
        return [cap.capability_name.replace('_', ' ').title() for cap in capabilities
                if cap.confidence_score >= 0.6]

    def _extract_manual_steps(self, capabilities: List[AutomationCapability], opportunity: Dict[str, Any]) -> List[str]:
        """Extract steps that require manual intervention"""
        manual_steps = []

        # Always manual steps
        manual_steps.extend(['Final review and approval', 'Personal customization', 'Relationship building'])

        # Low-confidence capabilities become manual
        low_confidence_caps = [cap for cap in capabilities if cap.confidence_score < 0.6]
        for cap in low_confidence_caps:
            manual_steps.append(f"Manual {cap.capability_name.replace('_', ' ')}")

        # High-risk capabilities require manual oversight
        high_risk_caps = [cap for cap in capabilities if cap.risk_level == 'high']
        for cap in high_risk_caps:
            manual_steps.append(f"Human oversight for {cap.capability_name.replace('_', ' ')}")

        return list(set(manual_steps))  # Remove duplicates

    def _estimate_success_rate(self, capabilities: List[AutomationCapability]) -> float:
        """Estimate overall success rate for automation"""
        if not capabilities:
            return 0.0

        # Calculate based on individual capability confidence
        individual_success_rates = [cap.confidence_score for cap in capabilities]

        # Overall success is product of individual successes (assuming dependencies)
        overall_success = 1.0
        for rate in individual_success_rates:
            overall_success *= rate

        # Add some baseline success even if individual rates are low
        baseline_success = 0.3
        final_success = baseline_success + (overall_success * (1 - baseline_success))

        return min(0.95, final_success)  # Cap at 95%

    def _estimate_time_savings(self, capabilities: List[AutomationCapability]) -> float:
        """Estimate total time savings from automation"""
        return sum(cap.estimated_time_saved_hours for cap in capabilities)

    def _requires_human_approval(self, automation_level: AutomationLevel, opportunity: Dict[str, Any]) -> bool:
        """Determine if human approval is required"""
        # Always require approval for high-value opportunities
        compensation = opportunity.get('compensation', {})
        if isinstance(compensation, dict):
            max_comp = compensation.get('max', 0)
            if max_comp > 100000:  # High-value opportunity
                return True

        # Require approval for partial automation or less
        if automation_level in [AutomationLevel.NONE, AutomationLevel.PARTIAL]:
            return True

        # Financial and business opportunities always need approval
        if any(keyword in opportunity.get('description', '').lower()
               for keyword in ['investment', 'financial', 'money', 'funding']):
            return True

        return False

    def _assess_automation_risks(self, workflow: List[Dict[str, Any]],
                                opportunity: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Assess risks and create mitigation strategies"""
        risks = []
        mitigations = []

        # Analyze workflow risks
        high_risk_steps = [step for step in workflow if step.get('risk_level') == 'high']
        if high_risk_steps:
            risks.append("High-risk automation steps present")
            mitigations.append("Implement human review checkpoints before high-risk steps")

        # Check for critical opportunity characteristics
        if 'urgent' in opportunity.get('description', '').lower():
            risks.append("Time pressure may lead to rushed automation")
            mitigations.append("Set up accelerated review process with key stakeholders")

        # Financial risks
        compensation = opportunity.get('compensation', {})
        if isinstance(compensation, dict) and compensation.get('max', 0) > 50000:
            risks.append("High-value opportunity increases stakes of automation errors")
            mitigations.append("Implement multi-level approval process for high-value opportunities")

        # Generic automation risks
        risks.extend([
            "Potential for generic or impersonal responses",
            "Missing context that human would catch",
            "Technology failures during critical timing"
        ])

        mitigations.extend([
            "Include personalization review step",
            "Implement context validation checks",
            "Maintain manual backup processes"
        ])

        return risks, mitigations

    def _generate_automation_steps(self, capability_name: str, opp_type: OpportunityType) -> List[str]:
        """Generate specific automation steps for a capability"""
        step_templates = {
            'research_company': [
                'Gather company information from public sources',
                'Analyze company culture and values',
                'Identify key personnel and decision makers',
                'Research recent company news and developments'
            ],
            'analyze_job_requirements': [
                'Extract required skills and qualifications',
                'Identify preferred experience levels',
                'Analyze job responsibilities and duties',
                'Identify application requirements and deadlines'
            ],
            'match_skills': [
                'Compare user skills to job requirements',
                'Identify skill gaps and strengths',
                'Calculate compatibility score',
                'Generate skill-based talking points'
            ],
            'generate_cover_letter': [
                'Create personalized opening paragraph',
                'Highlight relevant experience and skills',
                'Address specific job requirements',
                'Include compelling closing with call to action'
            ]
        }

        return step_templates.get(capability_name, [
            f'Execute {capability_name.replace("_", " ")}',
            'Validate results',
            'Format output appropriately'
        ])

    def _estimate_time_saved(self, capability_name: str) -> float:
        """Estimate time saved for specific capability"""
        time_estimates = {
            'research_company': 2.0,
            'analyze_job_requirements': 1.0,
            'match_skills': 0.5,
            'generate_cover_letter': 1.5,
            'submit_application': 0.5,
            'follow_up': 0.25,
            'analyze_requirements': 1.5,
            'estimate_pricing': 1.0,
            'create_proposal': 2.0,
            'negotiate_terms': 0.5,
            'research_investment': 3.0,
            'analyze_financials': 2.0,
            'compare_alternatives': 1.0,
            'execute_transaction': 0.5
        }

        return time_estimates.get(capability_name, 1.0)

    def _assess_capability_risk(self, capability_name: str, automation_level: str) -> str:
        """Assess risk level for specific capability"""
        high_risk_capabilities = [
            'submit_application', 'execute_transaction', 'negotiate_terms'
        ]

        medium_risk_capabilities = [
            'generate_cover_letter', 'create_proposal', 'estimate_pricing'
        ]

        if capability_name in high_risk_capabilities:
            return 'high'
        elif capability_name in medium_risk_capabilities:
            return 'medium'
        else:
            return 'low'


def analyze_opportunity_batch(opportunities: List[Dict[str, Any]],
                            user_profile: Dict[str, Any]) -> List[OpportunityAnalysis]:
    """
    Analyze a batch of opportunities for automation potential.

    Args:
        opportunities: List of opportunity data
        user_profile: User profile for personalization

    Returns:
        List of opportunity analyses
    """
    analyzer = OpportunityAIAnalyzer()
    analyses = []

    for opportunity in opportunities:
        try:
            analysis = analyzer.analyze_opportunity(opportunity, user_profile)
            analyses.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing opportunity {opportunity.get('id', 'unknown')}: {e}")
            # Continue with other opportunities
            continue

    return analyses