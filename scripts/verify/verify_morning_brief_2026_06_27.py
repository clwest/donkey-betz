"""Session 1240 — verify the 06-27 morning_brief fire.

This is the 3rd-fire verification (first with all 6 Session 1238 Sub-step D
PRs cumulatively live). Yesterday's 66/100 baseline read was earned with
NONE of Sub-step D merged yet, so today is the first apples-to-apples
follow-up window.

Run from project root::

    .venv/bin/python scripts/verify/verify_morning_brief_2026_06_27.py
    .venv/bin/python scripts/verify/verify_morning_brief_2026_06_27.py --date 2026-06-28

Default date is 2026-06-27. Pass ``--date YYYY-MM-DD`` to verify any other
fire (re-usable for future Sub-step E daily reads).

Exit code 0 if all checks pass, 1 if any check fails. Each check prints
PASS/FAIL + supporting evidence so Chris can see WHAT was checked without
re-reading the source.

Checks (in order):

1. Did the beat task fire at 13:00 UTC?
2. Did SUCCESS status land in CeleryTaskEvent?
3. Did the deliverable persist for chris on 06-27?
4. Did it land in the Morning Brief workspace (NOT cf708a2e leak)?
5. PR #2655 — Decision Card validator + dynamic Denver TZ:
   - 'MDT' present, 'MST' absent (it's summer)
   - Decision Cards end with periods (no truncation)
6. PR #2656 — Lane 1 self-referential health alarm filter:
   - SELF_CHECK_EVIDENCE block injected if health alarms surfaced
7. PR #2657 — Lane 4 odds-missing fallback:
   - 3-block fallback ('Data status' / 'What we can still do today' / 'Action')
     present if odds source was thin
8. PR #2658 — Lane 3 adaptive no-signal + MUSCULAR plain-English:
   - 'Coverage map' present if Lane 3 returned no signal
   - 'Agent activity anomaly' substituted for raw 'MUSCULAR: No Agent Activity'
"""

import argparse
import os
import sys
from datetime import date, datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
django.setup()


DEFAULT_DATE = date(2026, 6, 27)
LEAK_WORKSPACE_PREFIX = 'cf708a2e'  # PR #2653 held this from leaking
TARGET_DATE = DEFAULT_DATE  # mutated by main() if --date passed


def _check(name, passed, evidence=''):
    """Print a PASS/FAIL line and return passed."""
    icon = '✅' if passed else '❌'
    print(f'{icon}  {name}')
    if evidence:
        for line in evidence.strip().split('\n'):
            print(f'      {line}')
    return passed


def check_beat_fire():
    """Check the morning brief beat fired on TARGET_DATE.

    Accepts both pre- and post-S1258-PR-3.3 task names so the script
    works for historical 06-27 verification (legacy task) and for
    post-migration fires (MissionRunner-backed task). The migration
    preserves the beat row name + cadence; only the task target
    changed. CeleryTaskEvent.task_name reflects the dispatched task
    name, so historical rows still carry the legacy name and
    post-migration rows carry the new one.
    """
    from django.db.models import Q
    from core.models import CeleryTaskEvent
    ev = CeleryTaskEvent.objects.filter(
        Q(task_name='core.tasks.generate_morning_brief_daily')
        | Q(task_name='chief_of_staff_morning_brief_run'),
        started_at__date=TARGET_DATE,
    ).order_by('-started_at').first()
    if not ev:
        return _check(
            f'1. Beat task fired on {TARGET_DATE}',
            False,
            'No CeleryTaskEvent row found for either '
            'core.tasks.generate_morning_brief_daily (pre-S1258) or '
            'chief_of_staff_morning_brief_run (post-S1258 PR 3.3). '
            'Check beat process is running and that '
            '`pkill -9 -f celery; rm -f .celery*.pid; make celery` '
            'ran before bed last night.',
        )
    return _check(
        f'1. Beat task fired on {TARGET_DATE}',
        True,
        f'task_name={ev.task_name} '
        f'started_at={ev.started_at.isoformat()} '
        f'duration_seconds={ev.duration_seconds} status={ev.status}',
    ), ev


def check_status_success(ev):
    if not ev:
        return _check('2. Beat task SUCCESS', False, 'No event to check.')
    passed = ev.status == 'SUCCESS'
    return _check(
        '2. Beat task SUCCESS',
        passed,
        f'status={ev.status} '
        f'error_type={ev.error_type!r} '
        f'error_message={ev.error_message[:200]!r}',
    )


def get_deliverable():
    from core.models_deliverables import Deliverable
    d = Deliverable.objects.filter(
        user__username='chris',
        category='Morning Brief',
        created_at__date=TARGET_DATE,
    ).order_by('-created_at').first()
    return d


def check_deliverable_persisted(d):
    if not d:
        return _check(
            '3. Deliverable persisted for chris/2026-06-27',
            False,
            'No Deliverable row found. Check workflow logs for failures '
            'in _execute_create_morning_brief_deliverable_step.',
        )
    return _check(
        '3. Deliverable persisted for chris/2026-06-27',
        True,
        f'id={d.id} title={d.title!r} content_len={len(d.content)}',
    )


def check_workspace_not_leaked(d):
    if not d:
        return _check('4. NOT in cf708a2e leak workspace', False, 'No deliverable.')
    ws_id = str(d.workspace_id or '')
    passed = not ws_id.startswith(LEAK_WORKSPACE_PREFIX)
    return _check(
        '4. NOT in cf708a2e leak workspace (PR #2653 still holds)',
        passed,
        f'workspace_id={ws_id!r} workspace.name={d.workspace.name if d.workspace else "<none>"}',
    )


def check_decision_card_tz_and_completeness(d):
    if not d:
        return _check('5. Decision Cards: MDT + complete (PR #2655)', False, 'No deliverable.')
    content = d.content
    has_mdt = 'MDT' in content
    has_mst = 'MST' in content
    # Decision Cards typically have multiple decisions; spot-check the last one
    # ends with a period (most common truncation signature was "...trailing off").
    decisions_section = content.split('Decision', 1)[-1] if 'Decision' in content else ''
    last_500 = decisions_section[-500:].rstrip()
    ends_clean = last_500.endswith(('.', '!', '?')) or '*' in last_500[-5:]
    passed = has_mdt and not has_mst and ends_clean
    return _check(
        '5. Decision Cards: MDT (not MST), no truncation (PR #2655)',
        passed,
        f'has_MDT={has_mdt} has_MST={has_mst} ends_clean={ends_clean}\n'
        f'last_80_chars={last_500[-80:]!r}',
    )


def check_lane_1_self_check_present(d):
    if not d:
        return _check('6. Lane 1 self-check (PR #2656)', False, 'No deliverable.')
    content = d.content
    # SELF_CHECK_EVIDENCE block fires only when health-alarm keywords detected
    # in Lane 1 text. If no alarms, no block expected — that's still a pass.
    has_alarm = any(
        kw in content.lower() for kw in (
            'no agent activity', 'worker stall', 'no executions',
            'agents went silent', 'health alarm',
        )
    )
    has_self_check = 'SELF_CHECK_EVIDENCE' in content or 'auto-downgraded' in content
    if has_alarm:
        passed = has_self_check
        evidence = (
            f'health alarm detected → expected self-check block. '
            f'has_SELF_CHECK_EVIDENCE={has_self_check}'
        )
    else:
        passed = True
        evidence = 'no health alarms in Lane 1 → self-check not expected (correct)'
    return _check('6. Lane 1 self-check on health alarms (PR #2656)', passed, evidence)


def check_lane_4_odds_fallback(d):
    if not d:
        return _check('7. Lane 4 odds fallback (PR #2657)', False, 'No deliverable.')
    content = d.content
    # Lane 4 has 'sports_edge_scan' or similar slot; if thin, fallback fires.
    thin_signal = 'No multi-bookmaker odds' in content
    fallback_blocks = (
        'Data status' in content
        and 'What we can still do today' in content
        and 'Action' in content
    )
    # Either substantive Lane 4 (no thin marker), or the 3-block fallback fired
    passed = not thin_signal or fallback_blocks
    return _check(
        '7. Lane 4 odds-missing fallback fires when needed (PR #2657)',
        passed,
        f'thin_signal_detected={thin_signal} fallback_blocks_present={fallback_blocks}',
    )


def check_lane_3_coverage_map_and_humanization(d):
    if not d:
        return _check('8. Lane 3 coverage + MUSCULAR humanized (PR #2658)', False, 'No deliverable.')
    content = d.content
    # Lane 3 no-signal fallback injects 'Coverage map'
    no_signal_markers = (
        'No confirmed competitor change events' in content
        or 'No changes detected' in content
    )
    coverage_map_present = 'Coverage map' in content
    lane_3_ok = not no_signal_markers or coverage_map_present
    # MUSCULAR humanization: raw form GONE, friendly form present (if MUSCULAR
    # appears at all)
    has_raw_jargon = 'MUSCULAR: No Agent Activity' in content
    has_humanized = 'Agent activity anomaly' in content or '[MUSCULAR]' in content
    mentions_muscular = 'MUSCULAR' in content
    if mentions_muscular:
        humanized_ok = (not has_raw_jargon) and has_humanized
    else:
        humanized_ok = True
    passed = lane_3_ok and humanized_ok
    return _check(
        '8. Lane 3 coverage map on no-signal + MUSCULAR humanized (PR #2658)',
        passed,
        f'no_signal={no_signal_markers} coverage_map={coverage_map_present} '
        f'raw_jargon={has_raw_jargon} humanized={has_humanized}',
    )


def main():
    global TARGET_DATE
    parser = argparse.ArgumentParser(
        description=(__doc__ or '').split('\n\n')[0],
    )
    parser.add_argument(
        '--date', type=str, default=None,
        help='Date to verify in YYYY-MM-DD (default: 2026-06-27)',
    )
    args = parser.parse_args()
    if args.date:
        TARGET_DATE = datetime.strptime(args.date, '%Y-%m-%d').date()

    print('=' * 78)
    print(f'  Morning brief {TARGET_DATE} verification')
    if TARGET_DATE == DEFAULT_DATE:
        print(f'  (Session 1240 FIRST THING — 3rd fire, 1st with Sub-step D PRs cumulative)')
    print('=' * 78)

    fire_result = check_beat_fire()
    # check_beat_fire returns either bool (failure) or (bool, event) tuple
    if isinstance(fire_result, tuple):
        fire_ok, ev = fire_result
    else:
        fire_ok, ev = fire_result, None

    status_ok = check_status_success(ev)
    d = get_deliverable()
    deliv_ok = check_deliverable_persisted(d)
    ws_ok = check_workspace_not_leaked(d)
    tz_ok = check_decision_card_tz_and_completeness(d)
    lane1_ok = check_lane_1_self_check_present(d)
    lane4_ok = check_lane_4_odds_fallback(d)
    lane3_ok = check_lane_3_coverage_map_and_humanization(d)

    all_ok = all([fire_ok, status_ok, deliv_ok, ws_ok, tz_ok, lane1_ok, lane4_ok, lane3_ok])
    print()
    print('=' * 78)
    if all_ok:
        print('  ✅  ALL CHECKS PASSED — Sub-step D verified-shipped.')
        print('  Next: send brief to Rigby for audience-fit verdict.')
    else:
        print('  ❌  ONE OR MORE CHECKS FAILED — Sub-step D NOT verified.')
        print('  Next: drill into the failed check(s) above. Each prints the')
        print('  specific evidence so you can find the regression source.')
    print('=' * 78)
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
