"""Shared per-agent wall-clock timeout configuration.

Session 1091: Extracted from core/tasks_agents.py so both the Celery task
wrapper (``_impl_execute_agent_task``) and the direct router dispatch path
(``AgentRouter.route``) enforce the same ceiling. Before this module,
direct ``router.route()`` callers — artifact execution, test harnesses,
orchestrator fallback paths — ran with no wall-clock at all, and only got
reaped 60 minutes later by the cleanup watchdog. The router now enforces
the same limits as the Celery wrapper; see core/agent_router.py.

Any change to these values applies to both dispatch paths automatically.
Remediation-engine overrides (stored in SystemConfiguration with key
``agent_timeout_override:<AgentName>``) continue to take precedence at the
Celery-task layer; the router uses code defaults only — if you need to
override for a running experiment, do it at the task layer.
"""

DEFAULT_AGENT_TIMEOUT_SECONDS = 1200  # 20 min

AGENT_TIMEOUT_SECONDS = {
    # Media agents: fast, external API calls
    'AudioAgent': 300,        # 5 min — 60s OpenAI + 60s ElevenLabs + context
    'ImageAgent': 300,
    'VideoAgent': 600,        # 10 min — video generation is slower
    'ThreeDAgent': 300,
    'ImageEditingAgent': 300,
    'VideoEditingAgent': 600,
    'TalkingCharacterAgent': 600,
    'ResolveAgent': 600,
    # Research / analysis agents: LLM + web search
    'ResearchAgent': 1500,            # 25 min (was 10 — multi-source research breached SLO)
    'SystemIntelligenceAgent': 600,
    'MarketingStrategyAgent': 600,
    'CustomerResearchAgent': 1500,    # 25 min (top timeout offender previously)
    'CharacterTrainingAgent': 600,
    'ContentWriterAgent': 600,
    'CompetitorAnalysisAgent': 600,
    'BrandStrategyAgent': 600,
    'ContentStrategyAgent': 600,
    # Blockchain: multi-chain scanning
    'WhaleWatcherAgent': 1500,
    # Thinking / brainstorm: successful runs finish in ~75s, hang = dead
    'ThinkingAgent': 300,             # 5 min
    # Orchestrators: may coordinate multiple agents
    'StockAuditCoordinator': 900,
    'WorkflowOrchestrationAgent': 900,
}


def get_agent_timeout(agent_name: str) -> int:
    """Return the wall-clock timeout (seconds) for ``agent_name``.

    Falls back to ``DEFAULT_AGENT_TIMEOUT_SECONDS`` if the agent is not in
    the override table.
    """
    return AGENT_TIMEOUT_SECONDS.get(agent_name, DEFAULT_AGENT_TIMEOUT_SECONDS)
