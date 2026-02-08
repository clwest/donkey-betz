"""
Session 963 Phase 3: Session Trace Builder

Incrementally assembles a session-trace-v1 JSON on DeliberationSession.trace.
Records the turn-by-turn timeline, tool calls, decisions, and performance metrics.
Never blocks conversations — all operations are try/except safe.
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 'session-trace-v1'


class SessionTraceBuilder:
    """Builds session traces incrementally on DeliberationSession.trace."""

    def init_trace(self, session) -> dict:
        """Initialize an empty trace on the session."""
        trace = {
            '$schema': SCHEMA_VERSION,
            'session_id': str(session.id),
            'trace_version': '1.0',
            'session_type': session.session_type,
            'initiated_by': '',
            'participants': session.participants or [],
            'inputs': {
                'objective': session.objective or '',
            },
            'deliberation': [],
            'decisions': [],
            'outputs': {},
            'performance': {},
        }
        session.trace = trace
        session.save(update_fields=['trace', 'updated_at'])
        return trace

    def _get_trace(self, session) -> dict:
        """Get existing trace or initialize."""
        trace = session.trace
        if not isinstance(trace, dict) or trace.get('$schema') != SCHEMA_VERSION:
            return self.init_trace(session)
        return trace

    def _save_trace(self, session, trace: dict):
        """Save updated trace to DB."""
        session.trace = trace
        session.save(update_fields=['trace', 'updated_at'])

    def append_turn(self, session, turn_number: int, agent_name: str,
                    role: str, content_hash: str, contains_tension: bool = False,
                    has_grounding: bool = False, grounding_refs: list = None):
        """
        Append a turn entry to the trace timeline.

        Called after each DeliberationTurn is persisted.
        """
        try:
            trace = self._get_trace(session)
            turn_entry = {
                'turn_number': turn_number,
                'agent_name': agent_name,
                'role': role,
                'timestamp': timezone.now().isoformat(),
                'content_hash': content_hash,
                'tool_calls': [],
                'claims_made': [],
                'contains_tension': contains_tension,
                'has_grounding': has_grounding,
                'grounding_refs': grounding_refs or [],
            }
            # Avoid duplicate turn numbers
            existing_turns = {t.get('turn_number') for t in trace['deliberation']}
            if turn_number not in existing_turns:
                trace['deliberation'].append(turn_entry)
                self._save_trace(session, trace)
        except Exception as e:
            logger.warning(f"[Phase 3] append_turn failed: {e}")

    def append_turn_from_model(self, session, turn):
        """
        Append a turn from a DeliberationTurn model instance.
        Convenience method that extracts fields from the model.
        """
        self.append_turn(
            session,
            turn_number=turn.turn_number,
            agent_name=turn.agent_name,
            role=turn.role or '',
            content_hash=turn.content_hash or '',
        )

    def attach_contract_snapshot(self, session, contract_type: str,
                                 contract_data: dict):
        """Attach a contract snapshot to the last turn or to decisions."""
        try:
            trace = self._get_trace(session)
            snapshot = {
                'contract_type': contract_type,
                'timestamp': timezone.now().isoformat(),
            }
            # Extract key fields based on contract type
            if contract_type == 'execution':
                snapshot['chosen_path'] = contract_data.get('chosen_path', '')
                snapshot['reason'] = contract_data.get('reason', '')
                snapshot['decision_owner'] = contract_data.get('decision_owner', '')
            elif contract_type == 'synthesis':
                claims = contract_data.get('claims', [])
                snapshot['claim_count'] = len(claims) if isinstance(claims, list) else 0
            elif contract_type == 'research':
                snapshot['question'] = contract_data.get('question', '')

            trace['decisions'].append(snapshot)
            self._save_trace(session, trace)
        except Exception as e:
            logger.warning(f"[Phase 3] attach_contract_snapshot failed: {e}")

    def attach_tool_calls(self, session, trace_id: str):
        """
        Attach tool call records to the trace.

        Looks up ToolCallRecord by trace_id and adds references.
        """
        try:
            from core.models_tool_calls import ToolCallRecord
            calls = ToolCallRecord.objects.filter(
                trace_id=trace_id,
            ).order_by('created_at').values_list('id', 'tool_name', 'created_at')[:20]

            if not calls:
                return

            trace = self._get_trace(session)
            tool_call_refs = []
            for call_id, tool_name, created_at in calls:
                tool_call_refs.append({
                    'id': str(call_id),
                    'tool_name': tool_name,
                    'timestamp': created_at.isoformat() if created_at else None,
                })

            if tool_call_refs:
                # Attach to the trace-level outputs
                trace['outputs']['tool_calls'] = tool_call_refs
                self._save_trace(session, trace)
        except Exception as e:
            logger.warning(f"[Phase 3] attach_tool_calls failed: {e}")

    def attach_decisions(self, session, trace_id: str):
        """
        Attach DecisionRecord entries linked by trace_id.
        """
        try:
            from core.models_decision_records import DecisionRecord
            records = DecisionRecord.objects.filter(
                trace_id=trace_id,
            ).order_by('created_at')[:10]

            if not records:
                return

            trace = self._get_trace(session)
            for r in records:
                trace['decisions'].append({
                    'decision_type': r.decision_type,
                    'agent_name': r.agent_name,
                    'action': (r.action or '')[:200],
                    'reasoning': (r.reasoning or '')[:200],
                    'confidence': r.confidence,
                    'was_successful': r.was_successful,
                    'timestamp': r.created_at.isoformat() if r.created_at else None,
                })
            self._save_trace(session, trace)
        except Exception as e:
            logger.warning(f"[Phase 3] attach_decisions failed: {e}")

    def finalize(self, session, state: dict = None):
        """
        Set performance metrics and mark the trace as complete.

        state: the ConversationOrchestrator state dict with total_turns, tension_count, etc.
        """
        try:
            trace = self._get_trace(session)
            perf = {
                'total_turns': len(trace['deliberation']),
                'total_decisions': len(trace['decisions']),
                'completed_at': timezone.now().isoformat(),
            }
            if state:
                perf['tension_count'] = state.get('tension_count', 0)
                perf['grounding_count'] = state.get('grounding_count', 0)
                perf['empty_agreement_count'] = state.get('empty_agreement_count', 0)

            trace['performance'] = perf
            self._save_trace(session, trace)
        except Exception as e:
            logger.warning(f"[Phase 3] finalize trace failed: {e}")


# Singleton
_builder_instance = None


def get_session_trace_builder() -> SessionTraceBuilder:
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = SessionTraceBuilder()
    return _builder_instance
