"""
Session 962 Phase 1: Deliberation Persistence Tests
====================================================

Tests that the orchestrator creates DeliberationSession, turns, and contracts.
Uses Django TestCase with mocked LLM calls.
"""

import hashlib
from unittest.mock import MagicMock, patch, AsyncMock

from django.test import TestCase
from django.utils import timezone

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
)


class TestDeliberationSessionModel(TestCase):
    """Direct model tests for DeliberationSession."""

    def test_create_session(self):
        session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Test debate on AI policy',
            participants=[{'agent_name': 'Agent1', 'role': 'advocate'}],
            status='active',
        )
        self.assertIsNotNone(session.id)
        self.assertEqual(session.session_type, 'hivemind')
        self.assertEqual(session.status, 'active')
        self.assertEqual(len(session.participants), 1)

    def test_session_str(self):
        session = DeliberationSession.objects.create(
            session_type='agent',
            objective='Short obj',
            status='pending',
        )
        self.assertIn('agent', str(session))
        self.assertIn('pending', str(session))

    def test_session_completion(self):
        session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Complete me',
            status='active',
        )
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save(update_fields=['status', 'completed_at', 'updated_at'])

        session.refresh_from_db()
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.completed_at)

    def test_parent_session_fk(self):
        parent = DeliberationSession.objects.create(
            session_type='composite',
            objective='Parent',
        )
        child = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Child',
            parent_session=parent,
        )
        self.assertEqual(child.parent_session_id, parent.id)
        self.assertEqual(parent.children.count(), 1)


class TestDeliberationTurnModel(TestCase):
    """Direct model tests for DeliberationTurn."""

    def setUp(self):
        self.session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Turn test',
            status='active',
        )

    def test_create_turn(self):
        turn = DeliberationTurn.objects.create(
            session=self.session,
            turn_number=1,
            agent_name='BullCaseAgent',
            role='advocate',
            content='The market is bullish because...',
        )
        self.assertEqual(turn.turn_number, 1)
        self.assertEqual(turn.agent_name, 'BullCaseAgent')

    def test_content_hash_auto_computed(self):
        content = 'This is test content for hashing'
        turn = DeliberationTurn.objects.create(
            session=self.session,
            turn_number=1,
            agent_name='TestAgent',
            content=content,
        )
        expected_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        self.assertEqual(turn.content_hash, expected_hash)

    def test_unique_turn_constraint(self):
        DeliberationTurn.objects.create(
            session=self.session,
            turn_number=1,
            agent_name='Agent1',
            content='First turn',
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DeliberationTurn.objects.create(
                session=self.session,
                turn_number=1,
                agent_name='Agent2',
                content='Duplicate turn number',
            )

    def test_multiple_turns_ordered(self):
        for i in range(1, 4):
            DeliberationTurn.objects.create(
                session=self.session,
                turn_number=i,
                agent_name=f'Agent{i}',
                content=f'Turn {i} content',
            )
        turns = list(self.session.turns.values_list('turn_number', flat=True))
        self.assertEqual(turns, [1, 2, 3])


class TestContractRecordModel(TestCase):
    """Direct model tests for ContractRecord."""

    def setUp(self):
        self.session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Contract test',
            status='active',
        )

    def test_create_execution_contract(self):
        contract = ContractRecord.objects.create(
            session=self.session,
            contract_type='execution',
            contract_data={
                'chosen_path': 'Deploy to production',
                'reason': 'All tests pass',
                'decision_owner': 'CTOAgent',
            },
        )
        self.assertEqual(contract.contract_type, 'execution')
        self.assertEqual(contract.contract_data['chosen_path'], 'Deploy to production')

    def test_create_research_contract(self):
        contract = ContractRecord.objects.create(
            session=self.session,
            contract_type='research',
            contract_data={'question': 'What is market outlook?'},
        )
        self.assertEqual(contract.contract_type, 'research')

    def test_create_synthesis_contract(self):
        contract = ContractRecord.objects.create(
            session=self.session,
            contract_type='synthesis',
            contract_data={'claims': ['Claim 1', 'Claim 2']},
        )
        self.assertEqual(contract.contract_type, 'synthesis')

    def test_cascade_delete(self):
        """Deleting session cascades to turns and contracts."""
        DeliberationTurn.objects.create(
            session=self.session,
            turn_number=1,
            agent_name='Agent1',
            content='Test',
        )
        ContractRecord.objects.create(
            session=self.session,
            contract_type='execution',
            contract_data={'test': True},
        )
        session_id = self.session.id
        self.session.delete()
        self.assertEqual(DeliberationTurn.objects.filter(session_id=session_id).count(), 0)
        self.assertEqual(ContractRecord.objects.filter(session_id=session_id).count(), 0)
