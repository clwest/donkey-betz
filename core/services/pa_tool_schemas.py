"""Tool schemas for the personal-assistant / code-job tools."""

from core.services.td_handlers_codejobs import ALLOWED_TEST_COMMANDS

CODE_JOB_SCHEMA = {
    'name': 'submit_code_job',
    'description': (
        'Submit a code job for execution. '
        'test_command is optional and defaults to \'make test-fast\'. '
        'Allowed values: ' + ', '.join("'{}'".format(c) for c in sorted(ALLOWED_TEST_COMMANDS)) + '.'
    ),
    'input_schema': {
        'type': 'object',
        'required': ['task_prompt'],
        'properties': {
            'task_prompt': {
                'type': 'string',
                'description': 'Description of the coding task to perform.',
            },
            'test_command': {
                'type': 'string',
                'description': (
                    'Optional. Command used to run tests after changes are applied. '
                    'Defaults to \'make test-fast\'. '
                    'Allowed: ' + ', '.join("'{}'".format(c) for c in sorted(ALLOWED_TEST_COMMANDS)) + '.'
                ),
                'enum': sorted(ALLOWED_TEST_COMMANDS),
            },
            'base_branch': {
                'type': 'string',
                'description': "Base branch to create the working branch from. Defaults to 'main'.",
            },
            'repo_url': {
                'type': 'string',
                'description': 'Git clone URL of the target repository.',
            },
        },
    },
}
