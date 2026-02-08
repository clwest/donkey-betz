"""
Session 970 Phase 5.1: Verify Surgical Moves Phase 0-3 end-to-end.

Management command that either runs a real 4-turn debate conversation and
checks all artifacts, or reports on an existing session.

Usage:
    python manage.py verify_surgical_moves                     # smoke test (runs LLM)
    python manage.py verify_surgical_moves --mode=report-only  # check latest session
    python manage.py verify_surgical_moves --session-id=<uuid> # check specific session
"""

import json

from django.core.management.base import BaseCommand

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
)


class Command(BaseCommand):
    help = 'Verify Surgical Moves Phase 0-3 end-to-end'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            default='smoke',
            choices=['smoke', 'report-only'],
            help='smoke = run a real debate then report; report-only = check latest session',
        )
        parser.add_argument(
            '--session-id',
            type=str,
            default=None,
            help='Check a specific existing session instead of running a new one',
        )

    def handle(self, *args, **options):
        session_id = options['session_id']

        if options['mode'] == 'smoke' and not session_id:
            session_id = self._run_smoke_test()
            if not session_id:
                self.stderr.write(self.style.ERROR('Smoke test failed: no session created'))
                return

        if not session_id:
            # report-only: grab the latest completed session
            latest = (
                DeliberationSession.objects
                .filter(status='completed')
                .order_by('-created_at')
                .first()
            )
            if not latest:
                self.stderr.write(self.style.ERROR('No completed deliberation sessions found'))
                return
            session_id = str(latest.id)

        self._print_report(session_id)

    def _run_smoke_test(self):
        """Run a real 4-turn debate and return the session ID."""
        self.stdout.write(self.style.WARNING('Running smoke test (LLM tokens will be spent)...'))
        try:
            from core.conversation_orchestrator import ConversationOrchestrator
            orchestrator = ConversationOrchestrator()
            result = orchestrator.generate_conversation(
                agent1={
                    'name': 'TrendAnalysisAgent',
                    'type': 'TrendAnalysis',
                    'specialization': 'trend_analysis',
                },
                agent2={
                    'name': 'MarketIntelligenceAgent',
                    'type': 'MarketIntelligence',
                    'specialization': 'market_intelligence',
                },
                topic='Should the platform prioritize content quality scoring or volume scaling?',
                conversation_type='debate',
                num_turns=4,
                objective='Reach a clear decision with concrete next steps',
                success_criteria=['Decision made', 'Risks identified', 'Timeline proposed'],
            )
            sid = result.get('deliberation_session_id')
            if sid:
                self.stdout.write(self.style.SUCCESS(f'Smoke test completed: session {sid}'))
            return sid
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Smoke test error: {e}'))
            return None

    def _print_report(self, session_id):
        """Query all artifacts and print a structured verification report."""
        try:
            session = DeliberationSession.objects.get(id=session_id)
        except DeliberationSession.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Session {session_id} not found'))
            return

        turns = DeliberationTurn.objects.filter(session=session).order_by('turn_number')
        contracts = ContractRecord.objects.filter(session=session).order_by('created_at')
        ep = session.evidence_pack or {}
        trace = session.trace or {}

        turn_count = turns.count()
        contract_list = list(contracts)

        self.stdout.write('')
        self.stdout.write('=== Surgical Moves Verification Report ===')
        self.stdout.write(f'Session: {session.id}')
        self.stdout.write(f'Status: {session.status}')
        self.stdout.write(f'Objective: "{(session.objective or "")[:100]}"')
        self.stdout.write('')

        checks = []

        # --- Phase 0: Connectors ---
        self.stdout.write('--- Phase 0: Connectors ---')

        # Contract serialization
        if contract_list:
            contract_detail = []
            for c in contract_list:
                size = len(json.dumps(c.contract_data or {}))
                contract_detail.append(f'{c.contract_type}: {size}B')
            detail = f'{len(contract_list)} records ({", ".join(contract_detail)})'
            checks.append(('PASS', 'Contract serialization', detail))
        else:
            checks.append(('WARN', 'Contract serialization', '0 contracts found'))

        # Decision enforcement
        exec_contracts = [c for c in contract_list if c.contract_type == 'execution']
        if exec_contracts:
            cdata = exec_contracts[0].contract_data or {}
            verdict = cdata.get('chosen_path', cdata.get('decision', 'present'))
            if isinstance(verdict, str):
                verdict = verdict[:100]
            checks.append(('PASS', 'Decision enforcement', f'{verdict}'))
        else:
            checks.append(('WARN', 'Decision enforcement', 'No execution contract'))

        # Doc read tracking
        internal_refs = len(ep.get('internal_refs', []))
        status = 'PASS' if internal_refs > 0 else 'WARN'
        checks.append((status, 'Doc read tracking', f'{internal_refs} internal_refs in evidence pack'))

        self._print_checks(checks)
        checks.clear()

        # --- Phase 1: Persistence ---
        self.stdout.write('')
        self.stdout.write('--- Phase 1: Persistence ---')

        status = 'PASS' if session.status == 'completed' else 'WARN'
        checks.append((status, 'DeliberationSession created + completed', f'Status: {session.status}'))

        status = 'PASS' if turn_count > 0 else 'FAIL'
        checks.append((status, 'DeliberationTurn count', str(turn_count)))

        status = 'PASS' if len(contract_list) > 0 else 'WARN'
        checks.append((status, 'ContractRecord count', str(len(contract_list))))

        self._print_checks(checks)
        checks.clear()

        # --- Phase 3: Evidence + Trace ---
        self.stdout.write('')
        self.stdout.write('--- Phase 3: Evidence + Trace ---')

        sources = len(ep.get('sources', []))
        claims = len(ep.get('claims', []))
        contradictions = len(ep.get('contradictions', []))
        evidence_total = sources + claims + contradictions + internal_refs
        status = 'PASS' if evidence_total > 0 else 'WARN'
        detail = f'{sources} sources, {claims} claims, {contradictions} contradictions, {internal_refs} internal_refs'
        checks.append((status, 'Evidence pack', detail))

        trace_turns = len(trace.get('deliberation', []))
        status = 'PASS' if trace_turns > 0 else 'WARN'
        checks.append((status, 'Session trace', f'{trace_turns} turns recorded'))

        mem_count = len(ep.get('memory_retrievals', []))
        status = 'PASS' if mem_count > 0 else 'WARN'
        checks.append((status, 'Memory retrievals', str(mem_count)))

        self._print_checks(checks)

        # --- Summary ---
        self.stdout.write('')
        all_checks = self._collect_all_checks(session, turns, contracts, ep, trace)
        pass_count = sum(1 for s, _, _ in all_checks if s == 'PASS')
        warn_count = sum(1 for s, _, _ in all_checks if s == 'WARN')
        fail_count = sum(1 for s, _, _ in all_checks if s == 'FAIL')
        total = len(all_checks)

        summary = f'=== Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL (of {total}) ==='
        if fail_count > 0:
            self.stdout.write(self.style.ERROR(summary))
        elif warn_count > 0:
            self.stdout.write(self.style.WARNING(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))

    def _print_checks(self, checks):
        for status, name, detail in checks:
            if status == 'PASS':
                line = self.style.SUCCESS(f'[PASS] {name}: {detail}')
            elif status == 'WARN':
                line = self.style.WARNING(f'[WARN] {name}: {detail}')
            else:
                line = self.style.ERROR(f'[FAIL] {name}: {detail}')
            self.stdout.write(line)

    def _collect_all_checks(self, session, turns, contracts, ep, trace):
        """Re-collect all checks for summary counting."""
        checks = []
        contract_list = list(contracts)
        turn_count = turns.count()
        internal_refs = len(ep.get('internal_refs', []))

        checks.append(('PASS' if contract_list else 'WARN', 'contracts', ''))
        exec_c = [c for c in contract_list if c.contract_type == 'execution']
        checks.append(('PASS' if exec_c else 'WARN', 'enforcement', ''))
        checks.append(('PASS' if internal_refs > 0 else 'WARN', 'doc_tracking', ''))
        checks.append(('PASS' if session.status == 'completed' else 'WARN', 'session', ''))
        checks.append(('PASS' if turn_count > 0 else 'FAIL', 'turns', ''))
        checks.append(('PASS' if contract_list else 'WARN', 'contract_records', ''))

        sources = len(ep.get('sources', []))
        claims = len(ep.get('claims', []))
        contradictions = len(ep.get('contradictions', []))
        evidence_total = sources + claims + contradictions + internal_refs
        checks.append(('PASS' if evidence_total > 0 else 'WARN', 'evidence', ''))
        trace_turns = len(trace.get('deliberation', []))
        checks.append(('PASS' if trace_turns > 0 else 'WARN', 'trace', ''))
        mem_count = len(ep.get('memory_retrievals', []))
        checks.append(('PASS' if mem_count > 0 else 'WARN', 'memory', ''))

        return checks
