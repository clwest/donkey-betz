"""Substrate adapters for the Golden Evals validator harness.

Each adapter binds one substrate (``AgentExecution``, ``ChatConversation``)
to the shared :class:`~core.services.golden_evals.context.EvalRunContext`
shape defined by canon_v2 Item 6.

New substrates: add a subclass of :class:`SubstrateAdapter`, register it in
:data:`ADAPTER_REGISTRY` below, and add the corresponding constant to
:mod:`core.services.golden_evals.context`.
"""

from ..context import SUBSTRATE_AGENT_EXECUTION, SUBSTRATE_CHAT_CONVERSATION
from .agent_execution import AgentExecutionAdapter
from .base import SubstrateAdapter
from .chat_conversation import ChatConversationAdapter


ADAPTER_REGISTRY: dict[str, type[SubstrateAdapter]] = {
    SUBSTRATE_AGENT_EXECUTION: AgentExecutionAdapter,
    SUBSTRATE_CHAT_CONVERSATION: ChatConversationAdapter,
}


__all__ = [
    "ADAPTER_REGISTRY",
    "AgentExecutionAdapter",
    "ChatConversationAdapter",
    "SubstrateAdapter",
]
