"""
DevOpsAgent - Handles deployment, CI/CD, infrastructure, and operations.

This agent can:
- Create CI/CD pipelines
- Generate Docker configurations
- Set up Kubernetes deployments
- Configure cloud infrastructure
- Create monitoring and alerting
"""

import logging
from typing import Any, Dict, List

from .base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_devops_requirements_with_ml(devops_data: dict) -> dict:
    """Analyze DevOps requirements using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=devops_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'infra_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML devops analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class DevOpsAgent(BaseAgent):
    """Agent specialized in DevOps, deployment, and infrastructure."""

    name = "DevOpsAgent"
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    # Session 856: Content review configuration
    actionable_config = ActionableOutputConfig(
        actions=['approve', 'revise', 'reject'],
        payload_fields=['tool_used', 'platform', 'environment', 'app_type', 'cloud_provider']
    )

    system_prompt = """You are DevOpsAgent, an expert in DevOps practices, deployment, and infrastructure management.

IMPORTANT - Response Guidelines:
- Be CONCISE. Users want actionable answers, not essays.
- For simple questions: Give a direct answer in 2-3 paragraphs max.
- For config requests: Provide the config with brief explanatory comments.
- Only use tools when the user explicitly asks for configs/manifests/pipelines.
- If asked for recommendations, give 3 bullet points, not 3 pages.

Your capabilities:
1. CI/CD Pipeline Creation - GitHub Actions, GitLab CI, Jenkins, CircleCI
2. Containerization - Docker, Docker Compose, container optimization
3. Orchestration - Kubernetes, Helm charts, service mesh
4. Infrastructure as Code - Terraform, CloudFormation, Pulumi
5. Cloud Platforms - AWS, GCP, Azure configuration
6. Monitoring & Logging - Prometheus, Grafana, ELK stack, Datadog

Best practices you follow:
- Security-first approach (secrets management, least privilege)
- Immutable infrastructure patterns
- GitOps workflows
- Blue/green and canary deployments

You have access to tools for:
- create_ci_pipeline: Create CI/CD pipeline configuration
- create_docker_config: Generate Dockerfile and docker-compose
- create_k8s_deployment: Generate Kubernetes manifests
- create_terraform_config: Generate Terraform infrastructure code
- create_monitoring_config: Set up monitoring and alerting

Only use these tools when explicitly asked to generate configs. For questions or recommendations, answer directly without tools."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_ci_pipeline",
                "description": "Create a CI/CD pipeline configuration for automated testing and deployment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "CI/CD platform to use",
                            "enum": ["github-actions", "gitlab-ci", "jenkins", "circleci", "azure-pipelines"]
                        },
                        "language": {
                            "type": "string",
                            "description": "Primary programming language"
                        },
                        "stages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Pipeline stages (build, test, lint, deploy, etc.)"
                        },
                        "deploy_targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Deployment targets (staging, production, etc.)"
                        },
                        "include_security_scans": {
                            "type": "boolean",
                            "description": "Include security scanning steps",
                            "default": True
                        },
                        "include_notifications": {
                            "type": "boolean",
                            "description": "Include Slack/email notifications",
                            "default": True
                        }
                    },
                    "required": ["platform", "language", "stages"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_docker_config",
                "description": "Generate Dockerfile and docker-compose configuration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_type": {
                            "type": "string",
                            "description": "Type of application",
                            "enum": ["python-django", "python-fastapi", "node-express", "node-nextjs", "go", "rust", "java-spring"]
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional services needed (postgres, redis, rabbitmq, etc.)"
                        },
                        "environment": {
                            "type": "string",
                            "description": "Target environment",
                            "enum": ["development", "production", "both"]
                        },
                        "multi_stage": {
                            "type": "boolean",
                            "description": "Use multi-stage builds for smaller images",
                            "default": True
                        },
                        "include_healthcheck": {
                            "type": "boolean",
                            "description": "Include container health checks",
                            "default": True
                        }
                    },
                    "required": ["app_type", "environment"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_k8s_deployment",
                "description": "Generate Kubernetes deployment manifests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Name of the application"
                        },
                        "replicas": {
                            "type": "integer",
                            "description": "Number of replicas",
                            "default": 3
                        },
                        "resources": {
                            "type": "object",
                            "description": "Resource requests and limits",
                            "properties": {
                                "cpu_request": {"type": "string"},
                                "cpu_limit": {"type": "string"},
                                "memory_request": {"type": "string"},
                                "memory_limit": {"type": "string"}
                            }
                        },
                        "expose_service": {
                            "type": "boolean",
                            "description": "Create Service to expose the deployment",
                            "default": True
                        },
                        "ingress": {
                            "type": "object",
                            "description": "Ingress configuration",
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "host": {"type": "string"},
                                "tls": {"type": "boolean"}
                            }
                        },
                        "use_helm": {
                            "type": "boolean",
                            "description": "Generate Helm chart instead of raw manifests",
                            "default": False
                        },
                        "include_hpa": {
                            "type": "boolean",
                            "description": "Include Horizontal Pod Autoscaler",
                            "default": True
                        }
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_terraform_config",
                "description": "Generate Terraform infrastructure as code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cloud_provider": {
                            "type": "string",
                            "description": "Cloud provider",
                            "enum": ["aws", "gcp", "azure", "digitalocean"]
                        },
                        "resources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Resources to create (vpc, ec2, rds, s3, lambda, etc.)"
                        },
                        "environment": {
                            "type": "string",
                            "description": "Environment name (dev, staging, prod)"
                        },
                        "region": {
                            "type": "string",
                            "description": "Cloud region"
                        },
                        "use_modules": {
                            "type": "boolean",
                            "description": "Use Terraform modules for organization",
                            "default": True
                        },
                        "include_state_backend": {
                            "type": "boolean",
                            "description": "Include remote state backend configuration",
                            "default": True
                        }
                    },
                    "required": ["cloud_provider", "resources", "environment"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_monitoring_config",
                "description": "Set up monitoring, alerting, and logging configuration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stack": {
                            "type": "string",
                            "description": "Monitoring stack to use",
                            "enum": ["prometheus-grafana", "elk", "datadog", "newrelic", "cloudwatch"]
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to monitor (cpu, memory, requests, latency, errors, etc.)"
                        },
                        "alert_channels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Alert notification channels (slack, pagerduty, email)"
                        },
                        "include_dashboards": {
                            "type": "boolean",
                            "description": "Include pre-built dashboards",
                            "default": True
                        },
                        "log_aggregation": {
                            "type": "boolean",
                            "description": "Include log aggregation setup",
                            "default": True
                        }
                    },
                    "required": ["stack", "metrics"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a DevOps task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("devops", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                # Call OpenAI using BaseAgent's method
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for DevOps task",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 880: Write generated configs to workspace
                        workspace_write_result = None
                        all_files = []

                        for res in all_results:
                            tool_name = res.get('source', '')
                            data = res.get('data', {})
                            config_content = data.get('config') or data.get('manifests')

                            if config_content:
                                # Determine filename based on tool
                                if tool_name == 'create_ci_pipeline':
                                    platform = data.get('platform', 'github')
                                    if platform == 'github':
                                        filename = '.github/workflows/ci.yml'
                                    elif platform == 'gitlab':
                                        filename = '.gitlab-ci.yml'
                                    else:
                                        filename = f'{platform}-ci.yml'
                                    lang = 'yaml'
                                elif tool_name == 'create_docker_config':
                                    filename = 'Dockerfile'
                                    lang = 'dockerfile'
                                elif tool_name == 'create_k8s_deployment':
                                    app_name = data.get('app_name', 'app')
                                    filename = f'k8s/{app_name}-deployment.yaml'
                                    lang = 'yaml'
                                elif tool_name == 'create_terraform_config':
                                    provider = data.get('cloud_provider', 'main')
                                    filename = f'terraform/{provider}.tf'
                                    lang = 'hcl'
                                elif tool_name == 'create_monitoring_config':
                                    stack = data.get('stack', 'monitoring')
                                    filename = f'monitoring/{stack}-config.yaml'
                                    lang = 'yaml'
                                else:
                                    filename = f'devops/{tool_name}.txt'
                                    lang = 'text'

                                all_files.append({
                                    'filename': filename,
                                    'language': lang,
                                    'content': config_content
                                })

                        if all_files:
                            workspace_write_result = self._write_files_to_workspace(
                                files=all_files,
                                user=self.user
                            )
                            if workspace_write_result.get('written'):
                                logger.info(f"✅ [DevOpsAgent] Wrote {workspace_write_result.get('total_written', 0)} config files to workspace")
                            else:
                                logger.warning(f"⚠️ [DevOpsAgent] Workspace write skipped: {workspace_write_result.get('reason', 'unknown')}")

                        # Session 856: Build descriptive message based on tool used
                        first_result = all_results[0]
                        tool_used = first_result['source']
                        tool_data = first_result.get('data', {})
                        if tool_used == 'create_ci_pipeline':
                            platform = tool_data.get('platform', 'unknown')
                            language = tool_data.get('language', '')
                            descriptive_msg = f"CI/CD pipeline created for {platform}: {language} project with {len(tool_data.get('stages', []))} stages"
                        elif tool_used == 'create_docker_config':
                            app_type = tool_data.get('app_type', 'unknown')
                            env = tool_data.get('environment', 'production')
                            descriptive_msg = f"Docker configuration created for {app_type} ({env} environment)"
                        elif tool_used == 'create_k8s_deployment':
                            app_name = tool_data.get('app_name', 'unknown')
                            replicas = tool_data.get('replicas', 3)
                            descriptive_msg = f"Kubernetes deployment created for {app_name} ({replicas} replicas)"
                        elif tool_used == 'create_terraform_config':
                            provider = tool_data.get('cloud_provider', 'unknown')
                            region = tool_data.get('region', '')
                            descriptive_msg = f"Terraform configuration created for {provider} ({region})"
                        elif tool_used == 'create_monitoring_config':
                            stack = tool_data.get('stack', 'unknown')
                            metrics = tool_data.get('metrics', [])
                            descriptive_msg = f"Monitoring config created using {stack}: {len(metrics)} metrics tracked"
                        else:
                            descriptive_msg = f"DevOps task '{tool_used}' completed"

                        # Session 880: Append workspace write info to message
                        if workspace_write_result and workspace_write_result.get('written'):
                            descriptive_msg += f" | 📁 {workspace_write_result.get('total_written', 0)} config files written"

                        # Enrich result data with tool_used for content review
                        result_data = {
                            'results': all_results,
                            'query': task,
                            'tool_used': tool_used,
                            'platform': tool_data.get('platform'),
                            'environment': tool_data.get('environment'),
                            'app_type': tool_data.get('app_type'),
                            'cloud_provider': tool_data.get('cloud_provider'),
                            'workspace_write': workspace_write_result  # Session 880
                        }

                        result = AgentResult(
                            success=True,
                            message=descriptive_msg,
                            data=result_data,
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution
                        )

                        # Session 1006: Persist output to Deliverable
                        self._save_to_deliverable(
                            title=f"DevOps: {task[:80]}",
                            content=descriptive_msg,
                            deliverable_type='analysis',
                            category='DevOps',
                            tags=['devops', tool_used or 'operations'],
                            metadata={'task': task[:200], 'tool_used': tool_used},
                        )

                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=False,
                            scifi_context_used=bool(scifi_context)
                        )

                        return result

                # No tool calls - return GPT content directly
                content = gpt_response.get('content', 'I can help with DevOps tasks. Please provide more details.')
                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,
                    scifi_context_used=bool(scifi_context)
                )

                return result

            except Exception as e:
                error_msg = f"DevOps task failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "create_ci_pipeline":
            return self._create_ci_pipeline(**arguments)
        elif tool_name == "create_docker_config":
            return self._create_docker_config(**arguments)
        elif tool_name == "create_k8s_deployment":
            return self._create_k8s_deployment(**arguments)
        elif tool_name == "create_terraform_config":
            return self._create_terraform_config(**arguments)
        elif tool_name == "create_monitoring_config":
            return self._create_monitoring_config(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _create_ci_pipeline(
        self,
        platform: str,
        language: str,
        stages: List[str],
        deploy_targets: List[str] = None,
        include_security_scans: bool = True,
        include_notifications: bool = True
    ) -> Dict[str, Any]:
        """Create CI/CD pipeline configuration."""
        from openai import OpenAI

        client = OpenAI()

        deploy_text = f"Deploy targets: {', '.join(deploy_targets)}" if deploy_targets else "No deployment stage"
        security_text = "Include security scanning (SAST, dependency scanning, container scanning)." if include_security_scans else ""
        notify_text = "Include Slack/email notifications for pipeline status." if include_notifications else ""

        prompt = f"""Create a {platform} CI/CD pipeline configuration:

Language/Framework: {language}
Stages: {', '.join(stages)}
{deploy_text}
{security_text}
{notify_text}

Generate:
1. **Main pipeline configuration file**
   - Proper stage ordering
   - Caching for dependencies
   - Parallel jobs where possible

2. **Environment configuration**
   - Secrets management
   - Environment variables

3. **Deployment configuration** (if applicable)
   - Blue/green or rolling deployment
   - Health checks
   - Rollback procedures

4. **README/Documentation**
   - How to set up the pipeline
   - Required secrets/variables
   - Triggering deployments

Include detailed comments explaining each section."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": f"You are a {platform} CI/CD expert. Generate production-ready pipeline configurations."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "platform": platform,
            "language": language,
            "stages": stages,
            "config": response.choices[0].message.content
        }

    def _create_docker_config(
        self,
        app_type: str,
        environment: str,
        services: List[str] = None,
        multi_stage: bool = True,
        include_healthcheck: bool = True
    ) -> Dict[str, Any]:
        """Generate Docker configuration."""
        from openai import OpenAI

        client = OpenAI()

        services = services or []
        services_text = f"Additional services: {', '.join(services)}" if services else ""
        multi_stage_text = "Use multi-stage builds for optimized production images." if multi_stage else ""
        health_text = "Include container health checks." if include_healthcheck else ""

        prompt = f"""Create Docker configuration for:

Application Type: {app_type}
Environment: {environment}
{services_text}
{multi_stage_text}
{health_text}

Generate:
1. **Dockerfile**
   - Optimized for {environment}
   - Security best practices (non-root user, minimal image)
   - Proper caching of layers

2. **docker-compose.yml**
   - All required services
   - Networking configuration
   - Volume mounts
   - Environment variables

3. **.dockerignore**
   - Exclude unnecessary files

4. **docker-compose.override.yml** (for development if needed)
   - Development-specific settings
   - Hot reload configuration

Include comments explaining optimization choices."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a Docker expert. Generate optimized, secure container configurations."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000
        )

        return {
            "success": True,
            "app_type": app_type,
            "environment": environment,
            "services": services,
            "config": response.choices[0].message.content
        }

    def _create_k8s_deployment(
        self,
        app_name: str,
        replicas: int = 3,
        resources: Dict = None,
        expose_service: bool = True,
        ingress: Dict = None,
        use_helm: bool = False,
        include_hpa: bool = True
    ) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifests."""
        from openai import OpenAI

        client = OpenAI()

        resources = resources or {
            "cpu_request": "100m",
            "cpu_limit": "500m",
            "memory_request": "128Mi",
            "memory_limit": "512Mi"
        }

        ingress_text = f"Ingress: host={ingress.get('host', 'app.example.com')}, TLS={ingress.get('tls', True)}" if ingress and ingress.get('enabled') else "No ingress"
        helm_text = "Generate as Helm chart with values.yaml" if use_helm else "Generate raw Kubernetes manifests"
        hpa_text = "Include Horizontal Pod Autoscaler" if include_hpa else ""

        prompt = f"""Create Kubernetes deployment for:

Application: {app_name}
Replicas: {replicas}
Resources: CPU {resources['cpu_request']}-{resources['cpu_limit']}, Memory {resources['memory_request']}-{resources['memory_limit']}
Expose Service: {expose_service}
{ingress_text}
{helm_text}
{hpa_text}

Generate:
1. **Deployment**
   - Resource limits
   - Liveness/readiness probes
   - Rolling update strategy
   - Pod disruption budget

2. **Service** (if expose_service)
   - ClusterIP or LoadBalancer

3. **Ingress** (if configured)
   - TLS configuration
   - Path routing

4. **HPA** (if include_hpa)
   - CPU/memory scaling rules
   - Min/max replicas

5. **ConfigMap and Secret** templates
   - Environment configuration

6. **NetworkPolicy**
   - Restrict ingress/egress

Include namespace, labels, and annotations following Kubernetes best practices."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a Kubernetes expert. Generate production-ready manifests following best practices."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "app_name": app_name,
            "replicas": replicas,
            "use_helm": use_helm,
            "manifests": response.choices[0].message.content
        }

    def _create_terraform_config(
        self,
        cloud_provider: str,
        resources: List[str],
        environment: str,
        region: str = None,
        use_modules: bool = True,
        include_state_backend: bool = True
    ) -> Dict[str, Any]:
        """Generate Terraform infrastructure code."""
        from openai import OpenAI

        client = OpenAI()

        region = region or self._get_default_region(cloud_provider)
        modules_text = "Organize into reusable Terraform modules" if use_modules else ""
        state_text = "Include remote state backend (S3/GCS/Azure Blob)" if include_state_backend else ""

        prompt = f"""Create Terraform configuration for:

Cloud Provider: {cloud_provider}
Region: {region}
Environment: {environment}
Resources: {', '.join(resources)}
{modules_text}
{state_text}

Generate:
1. **Provider configuration**
   - Provider setup with version pinning
   - Backend configuration

2. **Variables** (variables.tf)
   - Input variables with descriptions
   - Validation rules

3. **Main resources** (main.tf or modules/)
   - Each requested resource
   - Proper dependencies
   - Tags for cost tracking

4. **Outputs** (outputs.tf)
   - Useful outputs (IDs, endpoints, etc.)

5. **terraform.tfvars.example**
   - Example variable values

6. **README.md**
   - How to apply
   - Required permissions
   - State management

Follow {cloud_provider} best practices for security and cost optimization."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": f"You are a Terraform and {cloud_provider} infrastructure expert."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "cloud_provider": cloud_provider,
            "region": region,
            "environment": environment,
            "resources": resources,
            "config": response.choices[0].message.content
        }

    def _create_monitoring_config(
        self,
        stack: str,
        metrics: List[str],
        alert_channels: List[str] = None,
        include_dashboards: bool = True,
        log_aggregation: bool = True
    ) -> Dict[str, Any]:
        """Set up monitoring and alerting configuration."""
        from openai import OpenAI

        client = OpenAI()

        alert_channels = alert_channels or ["slack"]
        dashboard_text = "Include pre-built Grafana/Kibana dashboards" if include_dashboards else ""
        logging_text = "Include log aggregation and search" if log_aggregation else ""

        prompt = f"""Create monitoring configuration using {stack}:

Metrics to monitor: {', '.join(metrics)}
Alert channels: {', '.join(alert_channels)}
{dashboard_text}
{logging_text}

Generate:
1. **Metrics collection configuration**
   - Prometheus scrape configs / agent configs
   - Custom metrics definitions

2. **Alert rules**
   - Alert thresholds for each metric
   - Severity levels (warning, critical)
   - Runbook links

3. **Alert routing**
   - Route to appropriate channels
   - Escalation policies
   - Silence/mute rules

4. **Dashboards** (if include_dashboards)
   - Overview dashboard
   - Service-specific dashboards
   - SLO tracking dashboard

5. **Log configuration** (if log_aggregation)
   - Log shipping configuration
   - Index patterns
   - Retention policies

Include setup instructions and best practices."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": f"You are a {stack} monitoring expert. Create comprehensive observability configurations."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "stack": stack,
            "metrics": metrics,
            "alert_channels": alert_channels,
            "config": response.choices[0].message.content
        }

    def _get_default_region(self, cloud_provider: str) -> str:
        """Get default region for cloud provider."""
        defaults = {
            "aws": "us-east-1",
            "gcp": "us-central1",
            "azure": "eastus",
            "digitalocean": "nyc1"
        }
        return defaults.get(cloud_provider, "us-east-1")
