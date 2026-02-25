"""
Session 1075: PlanV1 schema — validation, normalization, and legacy conversion.

Defines the stable Plan JSON contract so the PA can generate plans
deterministically and the ExecutorDriver can execute them safely.

PlanV1 schema:
{
    "version": "v1",
    "title": "...",
    "context": {"repo_name": "...", "base_branch": "..."},
    "steps": [
        {"id": "s1", "type": "shell", "cmd": "...", ...},
        {"id": "s2", "type": "apply_patch", "patch": "...", ...},
    ]
}
"""

from __future__ import annotations

from dataclasses import dataclass

PLAN_VERSION = 'v1'
VALID_STEP_TYPES = frozenset({'shell', 'apply_patch'})
VALID_NETWORK_VALUES = frozenset({'off', 'on'})


# ── Validation ───────────────────────────────────────────────────────────────


@dataclass
class PlanValidationError:
    field: str
    message: str


def validate_plan_v1(plan: dict) -> list[PlanValidationError]:
    """Validate a PlanV1 JSON structure.

    Returns a list of errors. Empty list means valid.
    """
    errors: list[PlanValidationError] = []

    version = plan.get('version')
    if version != PLAN_VERSION:
        errors.append(PlanValidationError('version', f'Expected "{PLAN_VERSION}", got {version!r}'))

    title = plan.get('title')
    if not title or not isinstance(title, str):
        errors.append(PlanValidationError('title', 'Required non-empty string'))

    context = plan.get('context')
    if context is not None and not isinstance(context, dict):
        errors.append(PlanValidationError('context', 'Must be an object if provided'))

    steps = plan.get('steps')
    if not isinstance(steps, list) or len(steps) == 0:
        errors.append(PlanValidationError('steps', 'Required non-empty array of steps'))
        return errors

    seen_ids: set[str] = set()

    for i, step in enumerate(steps):
        prefix = f'steps[{i}]'

        if not isinstance(step, dict):
            errors.append(PlanValidationError(prefix, 'Each step must be an object'))
            continue

        step_id = step.get('id')
        if not step_id or not isinstance(step_id, str):
            errors.append(PlanValidationError(f'{prefix}.id', 'Required non-empty string'))
        elif step_id in seen_ids:
            errors.append(PlanValidationError(f'{prefix}.id', f'Duplicate step id: {step_id!r}'))
        else:
            seen_ids.add(step_id)

        step_type = step.get('type')
        if step_type not in VALID_STEP_TYPES:
            errors.append(PlanValidationError(
                f'{prefix}.type',
                f'Must be one of {sorted(VALID_STEP_TYPES)}, got {step_type!r}',
            ))
            continue

        ra = step.get('requires_approval')
        if ra is not None and not isinstance(ra, bool):
            errors.append(PlanValidationError(
                f'{prefix}.requires_approval', 'Must be a boolean',
            ))

        if step_type == 'shell':
            errors.extend(_validate_shell_step(step, prefix))
        elif step_type == 'apply_patch':
            errors.extend(_validate_patch_step(step, prefix))

    return errors


def _validate_shell_step(step: dict, prefix: str) -> list[PlanValidationError]:
    errors: list[PlanValidationError] = []

    cmd = step.get('cmd')
    if not cmd or not isinstance(cmd, str):
        errors.append(PlanValidationError(f'{prefix}.cmd', 'Required non-empty string'))

    cwd = step.get('cwd')
    if cwd is not None and not isinstance(cwd, str):
        errors.append(PlanValidationError(f'{prefix}.cwd', 'Must be a string'))

    env = step.get('env')
    if env is not None and not isinstance(env, dict):
        errors.append(PlanValidationError(f'{prefix}.env', 'Must be an object'))

    network = step.get('network')
    if network is not None and network not in VALID_NETWORK_VALUES:
        errors.append(PlanValidationError(
            f'{prefix}.network',
            f'Must be one of {sorted(VALID_NETWORK_VALUES)}, got {network!r}',
        ))

    return errors


def _validate_patch_step(step: dict, prefix: str) -> list[PlanValidationError]:
    errors: list[PlanValidationError] = []

    patch = step.get('patch')
    if not patch or not isinstance(patch, str):
        errors.append(PlanValidationError(f'{prefix}.patch', 'Required non-empty string'))

    return errors


# ── Normalization ────────────────────────────────────────────────────────────


def normalize_plan_v1(plan: dict) -> dict:
    """Normalize a validated PlanV1, filling defaults.

    Call only after validate_plan_v1 returns no errors.
    """
    steps = []
    for step in plan.get('steps', []):
        normalized: dict = {
            'id': step['id'],
            'type': step['type'],
            'requires_approval': step.get('requires_approval', False),
        }

        if step['type'] == 'shell':
            normalized['cmd'] = step['cmd']
            normalized['cwd'] = step.get('cwd', '.')
            normalized['env'] = step.get('env', {})
            normalized['network'] = step.get('network', 'off')
            # network=on auto-requires approval
            if normalized['network'] == 'on':
                normalized['requires_approval'] = True

        elif step['type'] == 'apply_patch':
            normalized['patch'] = step['patch']

        steps.append(normalized)

    return {
        'version': PLAN_VERSION,
        'title': plan.get('title', ''),
        'context': plan.get('context', {}),
        'steps': steps,
    }


# ── Legacy conversion ────────────────────────────────────────────────────────


def is_legacy_plan(plan_input) -> bool:
    """Detect legacy plan format: a bare list of {command, description}."""
    return isinstance(plan_input, list) and len(plan_input) > 0 and isinstance(plan_input[0], dict)


def normalize_legacy_plan(steps: list[dict], summary: str = '') -> dict:
    """Convert legacy [{command, description}, ...] to PlanV1 format."""
    v1_steps = []
    for i, step in enumerate(steps):
        cmd = step.get('command', '')
        desc = step.get('description', f'Step {i}')
        v1_steps.append({
            'id': f's{i}',
            'type': 'shell',
            'cmd': cmd,
            'cwd': '.',
            'env': {},
            'network': 'off',
            'requires_approval': False,
        })

    return {
        'version': PLAN_VERSION,
        'title': summary or 'Legacy plan',
        'context': {},
        'steps': v1_steps,
    }


# ── Helpers for policy bridge ────────────────────────────────────────────────


def extract_commands_from_plan(plan: dict) -> list[dict]:
    """Extract step commands for policy classification.

    Returns list of dicts with 'command' key for shell steps.
    """
    result = []
    for step in plan.get('steps', []):
        if step.get('type') == 'shell':
            result.append({
                'command': step.get('cmd', ''),
                'description': f"Step {step.get('id', '?')}: {step.get('cmd', '')}",
            })
        elif step.get('type') == 'apply_patch':
            result.append({
                'command': '',
                'description': f"Step {step.get('id', '?')}: apply patch",
            })
    return result
