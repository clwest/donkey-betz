"""Code job handler: runtime defaults and allowlist validation for test_command."""

import logging

logger = logging.getLogger(__name__)

# Allowlist of permitted test_command overrides
ALLOWED_TEST_COMMANDS = frozenset([
    'make test-fast',
    'make test',
    'make lint',
])

DEFAULT_TEST_COMMAND = 'make test-fast'


def resolve_test_command(test_command):
    """Return a validated test command, defaulting to 'make test-fast'.

    Args:
        test_command: The requested test command, or None/empty string.

    Returns:
        A validated test command string.

    Raises:
        ValueError: If test_command is not in the allowlist.
    """
    if not test_command:
        logger.debug('test_command not provided; defaulting to %r', DEFAULT_TEST_COMMAND)
        return DEFAULT_TEST_COMMAND

    if test_command not in ALLOWED_TEST_COMMANDS:
        raise ValueError(
            f'test_command {test_command!r} is not allowed. '
            f'Permitted values: {sorted(ALLOWED_TEST_COMMANDS)}'
        )

    return test_command


def handle_code_job(job):
    """Process an incoming code job payload with validation and defaults.

    Applies runtime defaulting for test_command and enforces the allowlist.
    Works regardless of whether a Repo row exists in the database.

    Args:
        job: Code job payload dict (may contain 'test_command').

    Returns:
        Normalised job dict with 'test_command' always set to an allowed value.

    Raises:
        ValueError: If the requested test_command is not in the allowlist.
    """
    test_command = resolve_test_command(job.get('test_command') or '')
    return {**job, 'test_command': test_command}
