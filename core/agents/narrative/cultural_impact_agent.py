"""
Session 471: Cultural Impact Agent

Analyzes second-order effects of narrative shifts.
"If people start believing X instead of Y, what happens next?"
"""

import logging
from typing import Dict, Any, List
from django.utils import timezone

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_cultural_impact_with_ml(impact_data: dict) -> dict:
    """Analyze cultural impact using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for impact text analysis
        result = router.auto_route(
            data=impact_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'impact_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML cultural impact analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CulturalImpactAgent(BaseAgent):
    """
    Analyzes the downstream effects of narrative shifts.

    Responsibilities:
    1. Predict second-order effects of belief changes
    2. Identify affected sectors/domains
    3. Estimate timeline of impact
    4. Generate actionable insights
    """

    name = "CulturalImpactAgent"
    description = "Analyzes second-order effects and downstream implications of narrative shifts"
    system_prompt = """You are the Cultural Impact Agent - an expert at predicting the downstream effects of narrative shifts.

Your role:
1. Predict second-order effects of belief changes
2. Identify affected sectors/domains
3. Estimate timeline of impact
4. Generate actionable insights

You answer the question: "If people start believing X instead of Y, what happens next?"

You have access to:
- Shift impact analysis tools
- Cross-domain correlation
- Historical impact patterns
- Prediction frameworks

When analyzing cultural impact, consider:
- Who is affected (stakeholders, sectors, demographics)
- What behaviors change as beliefs shift
- When the effects will manifest (timeline)
- How to capitalize or protect against the shift
- What indicators to watch for the predicted effects"""

    def __init__(self, user=None):
        super().__init__(user)
        self.tools = self._build_tools()

    def _build_tools(self) -> List[Dict[str, Any]]:
        """Build the tools available to this agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "analyze_shift_impact",
                    "description": "Analyze the potential impact of a narrative shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shift_id": {
                                "type": "string",
                                "description": "UUID of the NarrativeShift to analyze"
                            }
                        },
                        "required": ["shift_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "predict_second_order_effects",
                    "description": "Predict downstream effects if a narrative becomes dominant",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative"
                            },
                            "assumption": {
                                "type": "string",
                                "description": "Assumption about the narrative's future (e.g., 'becomes dominant', 'fades')"
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "identify_affected_domains",
                    "description": "Identify other domains that would be affected by a narrative shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative"
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_action_recommendations",
                    "description": "Generate actionable recommendations based on narrative analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shift_id": {
                                "type": "string",
                                "description": "UUID of the NarrativeShift (optional)"
                            },
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the Narrative (optional)"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for recommendations"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_impact_analysis",
                    "description": "Save the cultural impact analysis to a narrative shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shift_id": {
                                "type": "string",
                                "description": "UUID of the NarrativeShift"
                            },
                            "analysis": {
                                "type": "string",
                                "description": "The cultural impact analysis text"
                            },
                            "second_order_effects": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of predicted second-order effects"
                            }
                        },
                        "required": ["shift_id", "analysis"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_historical_parallels",
                    "description": "Find historical parallels to understand potential impact",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_description": {
                                "type": "string",
                                "description": "Description of the narrative to find parallels for"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Domain to search in"
                            }
                        },
                        "required": ["narrative_description"]
                    }
                }
            }
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the LLM."""
        if tool_name == "analyze_shift_impact":
            return self._analyze_shift_impact(tool_input)
        elif tool_name == "predict_second_order_effects":
            return self._predict_second_order_effects(tool_input)
        elif tool_name == "identify_affected_domains":
            return self._identify_affected_domains(tool_input)
        elif tool_name == "generate_action_recommendations":
            return self._generate_action_recommendations(tool_input)
        elif tool_name == "save_impact_analysis":
            return self._save_impact_analysis(tool_input)
        elif tool_name == "find_historical_parallels":
            return self._find_historical_parallels(tool_input)

        else:
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, tool_input)

    def _analyze_shift_impact(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of a narrative shift."""
        from core.models_narrative_drift import NarrativeShift
        import uuid

        shift_id = tool_input.get('shift_id')

        # Validate UUID format
        try:
            uuid.UUID(str(shift_id))
        except (ValueError, TypeError):
            # Return a conceptual analysis when no valid shift ID is provided
            return {
                'shift_id': shift_id,
                'analysis_type': 'conceptual',
                'message': f"No valid shift ID provided. Returning conceptual analysis for: {shift_id}",
                'impact_analysis': {
                    'impact_score': 0.65,
                    'affected_domains': ['culture', 'tech', 'markets'],
                    'estimated_timeline': 'Medium-term (weeks to months)',
                    'confidence': 0.7,
                    'note': 'This is a conceptual analysis. For actual shift tracking, create a NarrativeShift record first.'
                }
            }

        try:
            shift = NarrativeShift.objects.get(id=shift_id)
        except NarrativeShift.DoesNotExist:
            return {"error": f"Shift {shift_id} not found"}

        # Domain impact mapping - which domains affect which others
        domain_connections = {
            'politics': ['markets', 'geopolitics', 'culture'],
            'markets': ['crypto', 'tech', 'geopolitics'],
            'tech': ['markets', 'culture', 'health'],
            'culture': ['politics', 'health', 'tech'],
            'geopolitics': ['markets', 'politics', 'climate'],
            'crypto': ['markets', 'tech'],
            'climate': ['politics', 'markets', 'geopolitics'],
            'health': ['politics', 'culture', 'tech'],
        }

        # Estimate impact scope
        affected_domains = domain_connections.get(shift.domain, [])

        # Calculate impact score
        base_impact = float(shift.importance)
        confidence_modifier = float(shift.confidence)

        # Adjust based on old narrative's prominence
        old_mentions = shift.old_narrative.mention_count
        prominence_modifier = min(old_mentions / 100, 1.0) if old_mentions > 0 else 0.2

        impact_score = base_impact * confidence_modifier * (0.5 + prominence_modifier * 0.5)

        # Generate impact timeline estimate
        if impact_score > 0.7:
            timeline = "Immediate (days to weeks)"
        elif impact_score > 0.4:
            timeline = "Medium-term (weeks to months)"
        else:
            timeline = "Long-term (months to years)"

        return {
            'shift_id': str(shift.id),
            'shift_summary': shift.shift_summary,
            'domain': shift.domain,
            'old_narrative': shift.old_narrative.title,
            'new_narrative': shift.new_narrative.title if shift.new_narrative else 'Unknown/Emerging',
            'impact_analysis': {
                'impact_score': round(impact_score, 2),
                'affected_domains': affected_domains,
                'estimated_timeline': timeline,
                'confidence': float(shift.confidence),
                'importance': float(shift.importance)
            },
            'existing_analysis': {
                'historian': shift.historian_analysis[:200] if shift.historian_analysis else None,
                'trend_break': shift.trend_break_analysis[:200] if shift.trend_break_analysis else None,
                'cultural': shift.cultural_impact_analysis[:200] if shift.cultural_impact_analysis else None
            }
        }

    def _is_valid_uuid(self, value: str) -> bool:
        """Check if a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, TypeError):
            return False

    def _predict_second_order_effects(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Predict second-order effects of a narrative change."""
        from core.models_narrative_drift import Narrative

        narrative_id = tool_input.get('narrative_id')
        assumption = tool_input.get('assumption', 'becomes dominant')

        # Validate UUID format
        if not self._is_valid_uuid(narrative_id):
            return {
                'narrative_id': narrative_id,
                'analysis_type': 'conceptual',
                'assumption': assumption,
                'second_order_effects': [
                    "Policy and regulatory adjustments",
                    "Capital flow shifts",
                    "Consumer behavior changes",
                    "Media narrative realignment"
                ],
                'timeline': 'Medium-term (weeks to months)',
                'note': 'Conceptual analysis - no valid narrative ID provided'
            }

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        # Domain-specific effect templates
        effect_templates = {
            'politics': {
                'becomes dominant': [
                    "Policy changes in alignment with narrative",
                    "Political realignment and party positioning",
                    "Media coverage shift",
                    "Public opinion polls reflect change"
                ],
                'fades': [
                    "Political capital lost for supporters",
                    "Alternative narratives gain space",
                    "Media attention shifts elsewhere"
                ]
            },
            'markets': {
                'becomes dominant': [
                    "Capital flows shift toward aligned sectors",
                    "Analyst recommendations change",
                    "Investor sentiment indicators move",
                    "Related asset valuations adjust"
                ],
                'fades': [
                    "Previous positions become contrarian plays",
                    "Sector rotation opportunity",
                    "Valuation reset for affected assets"
                ]
            },
            'tech': {
                'becomes dominant': [
                    "Investment focus shifts to aligned technologies",
                    "Talent migration toward related companies",
                    "Regulatory attention increases",
                    "Consumer behavior adapts"
                ],
                'fades': [
                    "Alternative technologies gain attention",
                    "Disappointed expectations create opportunities",
                    "Pivot opportunities for incumbents"
                ]
            },
            'crypto': {
                'becomes dominant': [
                    "Capital allocation shifts within crypto ecosystem",
                    "Protocol development priorities change",
                    "Regulatory responses accelerate",
                    "Institutional adoption patterns shift"
                ],
                'fades': [
                    "Contrarian buying opportunity",
                    "Alternative narratives emerge",
                    "Consolidation in affected protocols"
                ]
            },
            'culture': {
                'becomes dominant': [
                    "Content creation trends shift",
                    "Brand positioning adapts",
                    "Consumer preferences evolve",
                    "Social norms gradually change"
                ],
                'fades': [
                    "Backlash/counter-movements emerge",
                    "Nostalgia cycles create opportunities",
                    "New subcultures form in response"
                ]
            },
            'geopolitics': {
                'becomes dominant': [
                    "International relations recalibrate",
                    "Trade patterns shift",
                    "Defense priorities adjust",
                    "Alliance dynamics evolve"
                ],
                'fades': [
                    "Power vacuum creates uncertainty",
                    "Regional dynamics rebalance",
                    "New narratives fill the void"
                ]
            },
            'climate': {
                'becomes dominant': [
                    "Policy and regulation accelerate",
                    "Investment in related sectors increases",
                    "Corporate behavior adapts",
                    "Consumer choices shift"
                ],
                'fades': [
                    "Economic priorities reassert",
                    "Skeptic narratives gain traction",
                    "Gradual policy rollbacks"
                ]
            },
            'health': {
                'becomes dominant': [
                    "Healthcare investment priorities shift",
                    "Public behavior adapts",
                    "Regulatory focus changes",
                    "Research funding reallocates"
                ],
                'fades': [
                    "Alternative approaches gain attention",
                    "Complacency risk increases",
                    "New health narratives emerge"
                ]
            }
        }

        domain = narrative.domain
        effects = effect_templates.get(domain, {}).get(assumption, [
            "Domain-specific effects to be analyzed",
            "Cross-domain spillover likely",
            "Timeline depends on narrative strength"
        ])

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'domain': domain,
            'assumption': assumption,
            'current_status': narrative.status,
            'predicted_effects': effects,
            'confidence': 'Moderate - based on domain patterns',
            'note': 'These are template predictions. Real impact depends on specific narrative content and context.'
        }

    def _identify_affected_domains(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Identify domains affected by a narrative."""
        from core.models_narrative_drift import Narrative

        narrative_id = tool_input.get('narrative_id')

        # Validate UUID format
        if not self._is_valid_uuid(narrative_id):
            return {
                'narrative_id': narrative_id,
                'analysis_type': 'conceptual',
                'primary_domain': 'culture',
                'affected_domains': [
                    {'domain': 'tech', 'connection_strength': 0.7, 'impact_type': 'direct'},
                    {'domain': 'markets', 'connection_strength': 0.6, 'impact_type': 'indirect'},
                    {'domain': 'politics', 'connection_strength': 0.5, 'impact_type': 'delayed'}
                ],
                'note': 'Conceptual analysis - no valid narrative ID provided'
            }

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        # Domain interdependency matrix (strength of connection 0-1)
        interdependency = {
            'politics': {'markets': 0.8, 'geopolitics': 0.9, 'culture': 0.6, 'climate': 0.7, 'health': 0.5},
            'markets': {'politics': 0.6, 'tech': 0.8, 'crypto': 0.9, 'geopolitics': 0.7},
            'tech': {'markets': 0.8, 'culture': 0.6, 'health': 0.5, 'crypto': 0.7},
            'culture': {'politics': 0.5, 'tech': 0.4, 'health': 0.3},
            'geopolitics': {'politics': 0.9, 'markets': 0.8, 'climate': 0.6},
            'crypto': {'markets': 0.9, 'tech': 0.7, 'geopolitics': 0.4},
            'climate': {'politics': 0.8, 'markets': 0.6, 'geopolitics': 0.5, 'health': 0.4},
            'health': {'politics': 0.6, 'culture': 0.5, 'tech': 0.4}
        }

        primary_domain = narrative.domain
        connections = interdependency.get(primary_domain, {})

        affected = []
        for domain, strength in sorted(connections.items(), key=lambda x: -x[1]):
            affected.append({
                'domain': domain,
                'connection_strength': strength,
                'impact_level': 'High' if strength > 0.7 else 'Medium' if strength > 0.4 else 'Low'
            })

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'primary_domain': primary_domain,
            'affected_domains': affected,
            'total_affected': len(affected)
        }

    def _generate_action_recommendations(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations."""
        from core.models_narrative_drift import NarrativeShift, Narrative

        shift_id = tool_input.get('shift_id')
        narrative_id = tool_input.get('narrative_id')
        context = tool_input.get('context', '')

        # Check if we have valid UUIDs
        has_valid_shift = shift_id and self._is_valid_uuid(shift_id)
        has_valid_narrative = narrative_id and self._is_valid_uuid(narrative_id)

        if not has_valid_shift and not has_valid_narrative:
            # Return conceptual recommendations
            return {
                'analysis_type': 'conceptual',
                'recommendations': [
                    "Monitor social media trends for narrative evolution",
                    "Track key influencer positions on the topic",
                    "Watch for mainstream media adoption timing",
                    "Identify contrarian investment opportunities",
                    "Monitor regulatory/policy responses"
                ],
                'priority': 'medium',
                'timeline': 'ongoing',
                'note': 'Conceptual recommendations - no valid shift or narrative ID provided'
            }

        shift = None
        narrative = None

        if has_valid_shift:
            try:
                shift = NarrativeShift.objects.get(id=shift_id)
                narrative = shift.old_narrative
            except NarrativeShift.DoesNotExist:
                pass

        if has_valid_narrative and not narrative:
            try:
                narrative = Narrative.objects.get(id=narrative_id)
            except Narrative.DoesNotExist:
                pass

        if not narrative:
            return {"error": "No valid shift or narrative found"}

        # Generate domain-specific recommendations
        domain_recommendations = {
            'politics': [
                "Monitor upcoming elections/legislation for alignment",
                "Track policy maker statements for position changes",
                "Watch for media narrative adoption timing"
            ],
            'markets': [
                "Review sector exposure relative to narrative",
                "Identify mispriced assets based on old beliefs",
                "Monitor institutional flow data for confirmation"
            ],
            'tech': [
                "Track venture funding patterns in related areas",
                "Monitor developer community sentiment",
                "Watch for enterprise adoption signals"
            ],
            'crypto': [
                "Monitor on-chain metrics for confirmation",
                "Track exchange flows and whale movements",
                "Watch DeFi protocol migrations"
            ],
            'culture': [
                "Monitor social media trend metrics",
                "Track brand/creator positioning shifts",
                "Watch for mainstream media adoption"
            ],
            'geopolitics': [
                "Monitor diplomatic communications",
                "Track trade flow changes",
                "Watch defense posture adjustments"
            ],
            'climate': [
                "Track policy announcement timing",
                "Monitor corporate commitment changes",
                "Watch energy investment patterns"
            ],
            'health': [
                "Monitor research funding announcements",
                "Track regulatory agency positions",
                "Watch healthcare investment flows"
            ]
        }

        recommendations = domain_recommendations.get(narrative.domain, [
            "Continue monitoring narrative development",
            "Look for cross-domain spillover",
            "Track key influencer positions"
        ])

        # Add timing recommendations based on narrative status
        if narrative.status == 'emerging':
            recommendations.append("Early stage - high uncertainty but maximum optionality")
        elif narrative.status == 'dominant':
            recommendations.append("Established narrative - consensus positions already priced in")
        elif narrative.status == 'shifting':
            recommendations.append("Transition phase - key window for repositioning")
        elif narrative.status == 'fading':
            recommendations.append("Declining narrative - contrarian opportunity if reversal likely")

        return {
            'narrative': narrative.title,
            'domain': narrative.domain,
            'status': narrative.status,
            'recommendations': recommendations,
            'context_provided': context,
            'generated_at': timezone.now().isoformat()
        }

    def _save_impact_analysis(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Save cultural impact analysis to a shift record."""
        from core.models_narrative_drift import NarrativeShift

        shift_id = tool_input.get('shift_id')
        analysis = tool_input.get('analysis')
        second_order_effects = tool_input.get('second_order_effects', [])

        # Validate UUID format
        if not self._is_valid_uuid(shift_id):
            return {
                'shift_id': shift_id,
                'analysis_saved': False,
                'analysis_type': 'conceptual',
                'message': 'Analysis recorded (conceptual - no valid shift ID for persistence)',
                'analysis_preview': analysis[:200] if analysis else None,
                'effects_count': len(second_order_effects)
            }

        try:
            shift = NarrativeShift.objects.get(id=shift_id)
        except NarrativeShift.DoesNotExist:
            return {"error": f"Shift {shift_id} not found"}

        shift.cultural_impact_analysis = analysis
        shift.second_order_effects = second_order_effects
        shift.save()

        return {
            'shift_id': str(shift.id),
            'analysis_saved': True,
            'effects_count': len(second_order_effects)
        }

    def _find_historical_parallels(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Find historical parallels to a narrative."""
        from core.models_narrative_drift import Narrative, NarrativeShift, NarrativeStatus

        description = tool_input.get('narrative_description', '')
        domain = tool_input.get('domain')

        # Search for similar past narratives
        queryset = Narrative.objects.filter(
            status__in=[NarrativeStatus.FADING, NarrativeStatus.DEAD]
        ).order_by('-peak_mentions')

        if domain:
            queryset = queryset.filter(domain=domain)

        # Simple keyword matching (could use embeddings in future)
        keywords = description.lower().split()
        matches = []

        for narrative in queryset[:50]:
            score = 0
            narrative_text = f"{narrative.title} {narrative.description}".lower()

            for keyword in keywords:
                if len(keyword) > 3 and keyword in narrative_text:
                    score += 1

            if score > 0:
                # Get any shifts this narrative was involved in
                shifts = NarrativeShift.objects.filter(old_narrative=narrative)[:1]
                shift_outcome = None
                if shifts:
                    shift = shifts[0]
                    shift_outcome = {
                        'new_narrative': shift.new_narrative.title if shift.new_narrative else 'Unknown',
                        'second_order_effects': shift.second_order_effects[:3] if shift.second_order_effects else []
                    }

                matches.append({
                    'id': str(narrative.id),
                    'title': narrative.title,
                    'domain': narrative.domain,
                    'peak_mentions': narrative.peak_mentions,
                    'peak_date': narrative.peak_date.isoformat() if narrative.peak_date else None,
                    'relevance_score': score,
                    'shift_outcome': shift_outcome
                })

        matches.sort(key=lambda x: -x['relevance_score'])

        return {
            'query': description,
            'domain_filter': domain,
            'parallels_found': len(matches),
            'parallels': matches[:5]
        }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the cultural impact analysis task."""
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("cultural_impact_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting cultural impact analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            logger.info(f"CulturalImpactAgent executing: {task[:100]}...")

        system_prompt = """You are the Cultural Impact Agent - a specialist in analyzing second-order effects of narrative shifts.

Your role:
1. Predict what happens DOWNSTREAM when beliefs change
2. Identify which other domains will be affected
3. Estimate timelines for impact propagation
4. Generate actionable recommendations

You have access to tools for:
- Analyzing shift impact across domains
- Predicting second-order effects
- Identifying affected domains
- Generating action recommendations
- Finding historical parallels
- Saving your analysis

Key questions to answer:
- "If people start believing X, what happens to Y?"
- "Which sectors/domains get affected first?"
- "How long until we see real-world effects?"
- "What should someone DO based on this shift?"

When analyzing impact, consider:
- Direct effects (immediate, obvious)
- Second-order effects (downstream, less obvious)
- Feedback loops (effects that amplify or dampen)
- Timeline (when effects become visible)

Provide clear, actionable analysis with specific recommendations."""

        # Build full prompt with system and task
        full_prompt = f"{system_prompt}\n\nTask: {task}"

        # Call GPT using BaseAgent's _call_openai
        try:
            gpt_response = self._call_openai(full_prompt)

            # Process response - extract content and handle any tool calls
            content = gpt_response.get('content', '')
            tool_calls = gpt_response.get('tool_calls', [])

            # Process tool calls if any
            tool_results = []
            tool_calls_made = []
            for tc in tool_calls:
                tool_calls_made.append({'name': tc['name'], 'input': tc['arguments']})
                tool_result = self._handle_tool_call(tc['name'], tc['arguments'])
                tool_results.append(tool_result)

            # Synthesize tool results if GPT content was empty
            if tool_results and not content:
                content = self._synthesize_tool_results(tool_calls_made, tool_results, task)
            message = content or "Cultural impact analysis complete"

            result = AgentResult(
                success=True,
                message=message,
                data={'tool_results': tool_results, 'analysis': message, 'full_text': message},
                agent_name=self.name
            )

            if message and len(message) > 100:
                self._save_to_deliverable(
                    title=f"Cultural Impact Analysis: {task[:50]}",
                    content=message,
                    deliverable_type='analysis',
                    category='Analysis',
                    tags=['cultural', 'impact', 'analysis', 'narrative'],
                    content_format='markdown',
                    metadata={'task': task},
                )
        except Exception as e:
            logger.error(f"CulturalImpactAgent error: {e}")
            result = AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

        # Record learning outcome for collective intelligence
        try:
            self._record_learning_outcome(
                task=task,
                result=result,
                success=result.success if hasattr(result, 'success') else True,
                context={
                    'agent_type': self.__class__.__name__,
                    'execution_time_ms': result.execution_time_ms if hasattr(result, 'execution_time_ms') else 0,
                }
            )
        except Exception as le:
            logger.warning(f"Failed to record learning outcome: {le}")

        return result
