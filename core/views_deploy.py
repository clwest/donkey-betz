"""
Deployment views for generated AI projects
"""
import os
import json
from pathlib import Path
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

PROJECT_BASE = Path("/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects")

@csrf_exempt
@require_http_methods(["GET"])
def view_generated_files(request, project_name):
    """View all generated files for a project"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    try:
        # Try the project name as-is first, then with cleaning transformations
        possible_names = [
            project_name,
            project_name.lower(),
            project_name.lower().replace(" ", "_"),
            project_name.lower().replace(" ", "_").replace("-", "_"),
            project_name.lower().replace(" ", "-").replace("_", "-")
        ]

        project_dir = None
        for name in possible_names:
            test_dir = PROJECT_BASE / name
            if test_dir.exists():
                project_dir = test_dir
                break

        if not project_dir:
            return JsonResponse({
                'success': False,
                'error': f'Project {project_name} not found'
            }, status=404)

        files = []
        for file_path in project_dir.glob("*"):
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                files.append({
                    'name': file_path.name,
                    'path': str(file_path.relative_to(PROJECT_BASE)),
                    'content': content,
                    'size': file_path.stat().st_size,
                    'language': get_language_from_extension(file_path.suffix)
                })

        return JsonResponse({
            'success': True,
            'project': project_name,
            'files': files,
            'total_files': len(files)
        })

    except Exception as e:
        logger.error(f"Error viewing files: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def download_project(request, project_name):
    """Download project as ZIP file"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    try:
        import zipfile
        import tempfile

        # Try the project name as-is first, then with cleaning transformations
        possible_names = [
            project_name,
            project_name.lower(),
            project_name.lower().replace(" ", "_"),
            project_name.lower().replace(" ", "_").replace("-", "_"),
            project_name.lower().replace(" ", "-").replace("_", "-")
        ]

        project_dir = None
        for name in possible_names:
            test_dir = PROJECT_BASE / name
            if test_dir.exists():
                project_dir = test_dir
                break

        if not project_dir:
            return JsonResponse({
                'success': False,
                'error': f'Project {project_name} not found'
            }, status=404)

        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_dir.glob("**/*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_dir)
                        zipf.write(file_path, arcname)

            # Return ZIP file
            response = FileResponse(
                open(tmp.name, 'rb'),
                content_type='application/zip'
            )
            response['Content-Disposition'] = f'attachment; filename="{project_name}.zip"'
            return response

    except Exception as e:
        logger.error(f"Error downloading project: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def deploy_project(request):
    """Deploy generated project (create Docker container, etc.)"""
    try:
        data = json.loads(request.body or b"{}")
        project_name = data.get('project_name', '')
        deploy_type = data.get('deploy_type', 'local')  # local, docker, cloud

        # Try the project name as-is first, then with cleaning transformations
        possible_names = [
            project_name,
            project_name.lower(),
            project_name.lower().replace(" ", "_"),
            project_name.lower().replace(" ", "_").replace("-", "_"),
            project_name.lower().replace(" ", "-").replace("_", "-")
        ]

        project_dir = None
        for name in possible_names:
            test_dir = PROJECT_BASE / name
            if test_dir.exists():
                project_dir = test_dir
                break

        if not project_dir:
            return JsonResponse({
                'success': False,
                'error': f'Project {project_name} not found'
            }, status=404)

        if deploy_type == 'local':
            # Create virtual environment and install dependencies
            deployment_info = deploy_local(project_dir, project_dir.name)
        elif deploy_type == 'docker':
            # Create Dockerfile and build container
            deployment_info = deploy_docker(project_dir, project_dir.name)
        else:
            deployment_info = {
                'status': 'pending',
                'message': f'Deployment type {deploy_type} not yet implemented'
            }

        return JsonResponse({
            'success': True,
            'project': project_name,
            'deployment': deployment_info
        })

    except Exception as e:
        logger.error(f"Error deploying project: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def deploy_local(project_dir, project_name):
    """Deploy project locally with virtual environment"""
    try:
        # Create requirements.txt if it doesn't exist
        requirements_file = project_dir / "requirements.txt"
        if not requirements_file.exists():
            with open(requirements_file, 'w') as f:
                f.write("django>=4.2\n")
                f.write("djangorestframework>=3.14\n")
                f.write("react>=18.0\n")
                f.write("stripe>=5.0\n")  # For payment processing

        # Create setup script
        setup_script = project_dir / "setup.sh"
        with open(setup_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("python -m venv venv\n")
            f.write("source venv/bin/activate\n")
            f.write("pip install -r requirements.txt\n")
            f.write("echo 'Setup complete! Activate with: source venv/bin/activate'\n")

        # Make script executable
        os.chmod(setup_script, 0o755)

        return {
            'status': 'ready',
            'message': f'Project ready for local deployment',
            'setup_command': f'cd {project_dir} && ./setup.sh',
            'files_created': ['requirements.txt', 'setup.sh']
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def deploy_docker(project_dir, project_name):
    """Deploy project with Docker"""
    try:
        # Create Dockerfile
        dockerfile = project_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write("FROM python:3.11-slim\n")
            f.write("WORKDIR /app\n")
            f.write("COPY . /app\n")
            f.write("RUN pip install django djangorestframework\n")
            f.write("EXPOSE 8000\n")
            f.write('CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]\n')

        # Create docker-compose.yml
        compose_file = project_dir / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            f.write("version: '3.8'\n")
            f.write("services:\n")
            f.write(f"  {project_name}:\n")
            f.write("    build: .\n")
            f.write("    ports:\n")
            f.write("      - '8001:8000'\n")
            f.write("    volumes:\n")
            f.write("      - .:/app\n")
            f.write("    environment:\n")
            f.write("      - DEBUG=True\n")

        return {
            'status': 'ready',
            'message': 'Docker files created',
            'build_command': f'cd {project_dir} && docker-compose up --build',
            'files_created': ['Dockerfile', 'docker-compose.yml']
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def get_language_from_extension(ext):
    """Get programming language from file extension"""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sh': 'bash',
        '.sql': 'sql'
    }
    return language_map.get(ext, 'text')


@csrf_exempt
def get_recent_project(request):
    """Get the most recently created project"""
    try:
        from core.models import GeneratedProject

        recent_project = GeneratedProject.objects.order_by('-created_at').first()

        if not recent_project:
            return JsonResponse({
                'success': False,
                'error': 'No projects found'
            }, status=404)

        return JsonResponse({
            'success': True,
            'project_name': recent_project.name,
            'project_id': str(recent_project.id),
            'created_at': recent_project.created_at.isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def get_database_files(request):
    """Get all generated files from database for the most recent project"""
    try:
        from core.models import GeneratedProject, GeneratedCode

        # Get the most recent project
        recent_project = GeneratedProject.objects.order_by('-created_at').first()

        if not recent_project:
            return JsonResponse({
                'success': False,
                'error': 'No projects found'
            })

        # Get all files for this project
        files = GeneratedCode.objects.filter(
            project=recent_project,
            is_latest=True
        ).order_by('-created_at')

        file_data = []
        for file in files:
            file_data.append({
                'name': file.filename,
                'content': file.content,
                'size': len(file.content.encode('utf-8')),
                'language': file.language or 'text',
                'created_at': file.created_at.isoformat(),
                'agent': file.agent_creator or 'unknown'
            })

        return JsonResponse({
            'success': True,
            'project': recent_project.name,
            'project_id': str(recent_project.id),
            'files': file_data,
            'total_files': len(file_data)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)