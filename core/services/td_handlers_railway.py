"""
Railway Platform Tool — PA tool handler for Railway infrastructure management.

Gives Rigby direct access to Railway operations: service status, logs,
restarts, redeployments, and variable inspection.

Uses Railway's GraphQL API (https://backboard.railway.com/graphql/v2)
with Bearer token authentication via RAILWAY_API_TOKEN env var.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Railway API config
_API_URL = 'https://backboard.railway.com/graphql/v2'
_PROJECT_ID = 'a11eb739-9bd2-4f7b-adc6-f97554164f33'
_ENVIRONMENT_ID = '4045e5be-c118-4e3a-8931-c071f50ad119'
_TIMEOUT = 20  # seconds


def _get_token() -> str:
    return os.environ.get('RAILWAY_API_TOKEN', '')


def _gql(query: str, variables: Optional[dict] = None) -> dict:
    """Execute a Railway GraphQL query."""
    token = _get_token()
    if not token:
        return {'error': 'RAILWAY_API_TOKEN not configured'}

    try:
        resp = requests.post(
            _API_URL,
            json={'query': query, 'variables': variables or {}},
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        if 'errors' in data:
            return {'error': data['errors'][0].get('message', str(data['errors']))}
        return data.get('data', {})
    except requests.Timeout:
        return {'error': 'Railway API timed out'}
    except requests.RequestException as e:
        return {'error': f'Railway API error: {str(e)[:200]}'}


# ── Queries ────────────────────────────────────────────────────────────────

def list_services() -> dict:
    """List all services with their current deployment status."""
    query = """
    query($projectId: String!) {
        project(id: $projectId) {
            name
            environments(first: 1) {
                edges {
                    node {
                        id
                        name
                        serviceInstances {
                            edges {
                                node {
                                    serviceId
                                    serviceName
                                    latestDeployment {
                                        id
                                        status
                                        createdAt
                                        meta
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    data = _gql(query, {'projectId': _PROJECT_ID})
    if 'error' in data:
        return data

    try:
        env = data['project']['environments']['edges'][0]['node']
        services = []
        for edge in env['serviceInstances']['edges']:
            svc = edge['node']
            dep = svc.get('latestDeployment') or {}
            meta = dep.get('meta') or {}
            services.append({
                'name': svc['serviceName'],
                'service_id': svc['serviceId'],
                'status': dep.get('status', 'unknown'),
                'deployed_at': dep.get('createdAt', ''),
                'commit': meta.get('commitHash', '')[:12],
                'commit_message': (meta.get('commitMessage') or '')[:80],
            })
        return {
            'action': 'services',
            'project': data['project']['name'],
            'environment': env['name'],
            'services': sorted(services, key=lambda s: s['name']),
            'total': len(services),
        }
    except (KeyError, IndexError) as e:
        return {'error': f'Failed to parse services: {e}'}


def get_service_logs(service_name: str, limit: int = 50) -> dict:
    """Get recent deploy logs for a service."""
    # First resolve service ID
    svc_list = list_services()
    if 'error' in svc_list:
        return svc_list

    service = next(
        (s for s in svc_list.get('services', []) if s['name'] == service_name),
        None,
    )
    if not service:
        available = [s['name'] for s in svc_list.get('services', [])]
        return {'error': f'Service "{service_name}" not found. Available: {available}'}

    deployment_id = None
    # Get deployment ID from a more detailed query
    query = """
    query($projectId: String!) {
        project(id: $projectId) {
            environments(first: 1) {
                edges {
                    node {
                        serviceInstances {
                            edges {
                                node {
                                    serviceName
                                    latestDeployment {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    data = _gql(query, {'projectId': _PROJECT_ID})
    if 'error' in data:
        return data

    try:
        env = data['project']['environments']['edges'][0]['node']
        for edge in env['serviceInstances']['edges']:
            svc = edge['node']
            if svc['serviceName'] == service_name:
                dep = svc.get('latestDeployment') or {}
                deployment_id = dep.get('id')
                break
    except (KeyError, IndexError):
        pass

    if not deployment_id:
        return {'error': f'No deployment found for {service_name}'}

    # Get deployment logs
    log_query = """
    query($deploymentId: String!, $limit: Int!) {
        deploymentLogs(deploymentId: $deploymentId, limit: $limit) {
            ... on Log {
                message
                timestamp
                severity
            }
        }
    }
    """
    log_data = _gql(log_query, {'deploymentId': deployment_id, 'limit': limit})
    if 'error' in log_data:
        # Logs endpoint may not be available via this query — return what we have
        return {
            'action': 'logs',
            'service': service_name,
            'deployment_id': deployment_id,
            'status': service['status'],
            'note': 'Deploy logs may require Railway dashboard for full access',
            'error_detail': log_data.get('error', ''),
        }

    logs = log_data.get('deploymentLogs', [])
    return {
        'action': 'logs',
        'service': service_name,
        'deployment_id': deployment_id,
        'log_count': len(logs),
        'logs': [
            f"[{l.get('severity', 'INFO')}] {l.get('message', '')}"
            for l in (logs if isinstance(logs, list) else [])
        ][-limit:],
    }


def restart_service(service_name: str) -> dict:
    """Restart a Railway service (re-runs the latest deployment)."""
    svc_list = list_services()
    if 'error' in svc_list:
        return svc_list

    service = next(
        (s for s in svc_list.get('services', []) if s['name'] == service_name),
        None,
    )
    if not service:
        available = [s['name'] for s in svc_list.get('services', [])]
        return {'error': f'Service "{service_name}" not found. Available: {available}'}

    # Restart = redeploy the latest deployment
    query = """
    mutation($serviceId: String!, $environmentId: String!) {
        serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
    }
    """
    data = _gql(query, {
        'serviceId': service['service_id'],
        'environmentId': _ENVIRONMENT_ID,
    })
    if 'error' in data:
        return data

    return {
        'action': 'restart',
        'service': service_name,
        'status': 'restart_triggered',
        'previous_status': service['status'],
        'note': 'Service will restart with the latest deployment. Check status in ~30s.',
    }


def redeploy_service(service_name: str) -> dict:
    """Trigger a fresh build + deploy for a Railway service."""
    svc_list = list_services()
    if 'error' in svc_list:
        return svc_list

    service = next(
        (s for s in svc_list.get('services', []) if s['name'] == service_name),
        None,
    )
    if not service:
        available = [s['name'] for s in svc_list.get('services', [])]
        return {'error': f'Service "{service_name}" not found. Available: {available}'}

    query = """
    mutation($serviceId: String!, $environmentId: String!) {
        serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
    }
    """
    data = _gql(query, {
        'serviceId': service['service_id'],
        'environmentId': _ENVIRONMENT_ID,
    })
    if 'error' in data:
        return data

    return {
        'action': 'redeploy',
        'service': service_name,
        'status': 'redeploy_triggered',
        'note': 'Fresh build + deploy triggered. Takes 2-5 minutes.',
    }


def get_service_metrics(service_name: str) -> dict:
    """Get basic service info and deployment details."""
    svc_list = list_services()
    if 'error' in svc_list:
        return svc_list

    service = next(
        (s for s in svc_list.get('services', []) if s['name'] == service_name),
        None,
    )
    if not service:
        available = [s['name'] for s in svc_list.get('services', [])]
        return {'error': f'Service "{service_name}" not found. Available: {available}'}

    return {
        'action': 'metrics',
        'service': service_name,
        'service_id': service['service_id'],
        'status': service['status'],
        'deployed_at': service['deployed_at'],
        'commit': service['commit'],
        'commit_message': service['commit_message'],
    }


def list_variables(service_name: str) -> dict:
    """List env vars for a service (values masked for security)."""
    svc_list = list_services()
    if 'error' in svc_list:
        return svc_list

    service = next(
        (s for s in svc_list.get('services', []) if s['name'] == service_name),
        None,
    )
    if not service:
        available = [s['name'] for s in svc_list.get('services', [])]
        return {'error': f'Service "{service_name}" not found. Available: {available}'}

    query = """
    query($projectId: String!, $environmentId: String!, $serviceId: String!) {
        variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
    }
    """
    data = _gql(query, {
        'projectId': _PROJECT_ID,
        'environmentId': _ENVIRONMENT_ID,
        'serviceId': service['service_id'],
    })
    if 'error' in data:
        return data

    raw_vars = data.get('variables', {})
    # Mask values for security — show key names + first/last 4 chars
    masked = {}
    for k, v in sorted(raw_vars.items()):
        if k.startswith('RAILWAY_'):
            continue  # Skip Railway auto-injected vars
        v_str = str(v)
        if len(v_str) > 12:
            masked[k] = f'{v_str[:4]}...{v_str[-4:]}'
        elif len(v_str) > 4:
            masked[k] = f'{v_str[:2]}...{v_str[-2:]}'
        else:
            masked[k] = v_str  # Short values shown in full (e.g. "true", "False")

    return {
        'action': 'variables',
        'service': service_name,
        'total': len(masked),
        'variables': masked,
    }


# ── Handler (called from ToolDispatcher) ───────────────────────────────────

class RailwayToolMixin:
    """Mixin providing Railway platform management for ToolDispatcher."""

    def _handle_railway(self, tool_name: str, payload: Dict[str, Any],
                        user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Railway platform ops: services, logs, restart, redeploy, variables."""
        action = payload.get('action', 'help')
        service_name = payload.get('service_name', '').strip()
        limit = min(int(payload.get('limit', 50)), 200)

        try:
            if action == 'help':
                return {
                    'tool': 'railway_tool',
                    'actions': [
                        'services — list all Railway services with deployment status',
                        'logs — view recent deploy logs for a service (requires service_name)',
                        'restart — restart a service (requires service_name)',
                        'redeploy — trigger fresh build + deploy (requires service_name)',
                        'metrics — get service details and deployment info (requires service_name)',
                        'variables — list env vars for a service, masked (requires service_name)',
                    ],
                }

            if action == 'services':
                return list_services()

            if action == 'logs':
                if not service_name:
                    return {'error': 'Provide service_name (e.g. "celery-long-running")'}
                return get_service_logs(service_name, limit)

            if action == 'restart':
                if not service_name:
                    return {'error': 'Provide service_name to restart'}
                return restart_service(service_name)

            if action == 'redeploy':
                if not service_name:
                    return {'error': 'Provide service_name to redeploy'}
                return redeploy_service(service_name)

            if action == 'metrics':
                if not service_name:
                    return {'error': 'Provide service_name for metrics'}
                return get_service_metrics(service_name)

            if action == 'variables':
                if not service_name:
                    return {'error': 'Provide service_name to list variables'}
                return list_variables(service_name)

            return {'error': f'Unknown railway_tool action: {action}'}

        except Exception as e:
            logger.error(f"[RAILWAY] {action} error: {e}", exc_info=True)
            return {'error': f'Railway tool error: {str(e)[:200]}'}
