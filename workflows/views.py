"""
Views for workflows app.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def workflow_list(request):
    """
    List all workflows.
    """
    return Response({
        'workflows': [
            {
                'id': 1,
                'name': 'Content Pipeline',
                'description': 'Automated content generation workflow',
                'status': 'active',
                'created_at': '2024-01-15T10:00:00Z'
            },
            {
                'id': 2,
                'name': 'Social Media Scheduler',
                'description': 'Schedule and post to multiple platforms',
                'status': 'active',
                'created_at': '2024-01-14T09:00:00Z'
            }
        ]
    })

@api_view(['GET'])
def workflow_templates(request):
    """
    Get workflow templates.
    """
    return Response({
        'templates': [
            {
                'id': 1,
                'name': 'Blog Content Workflow',
                'description': 'Generate, edit, and publish blog posts',
                'category': 'content',
                'steps': ['research', 'outline', 'write', 'edit', 'publish'],
                'agents': [],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'stop',
                    'save_intermediate': True
                }
            },
            {
                'id': 2,
                'name': 'Video Production Workflow',
                'description': 'Script, produce, and publish videos',
                'category': 'video',
                'steps': ['script', 'storyboard', 'produce', 'edit', 'publish'],
                'agents': [],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'stop',
                    'save_intermediate': True
                }
            },
            {
                'id': 3,
                'name': 'Email Marketing Workflow',
                'description': 'Design, test, and send email campaigns',
                'category': 'email',
                'steps': ['design', 'write', 'test', 'schedule', 'send'],
                'agents': [],
                'flow_config': {
                    'type': 'sequential',
                    'error_handling': 'stop',
                    'save_intermediate': True
                }
            }
        ]
    })