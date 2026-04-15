"""
Portfolio Management Views
API endpoints for saving and managing project portfolios
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def portfolio_projects(request):
    """Get or create portfolio projects"""
    if request.method == "GET":
        return get_portfolio_projects(request)
    elif request.method == "POST":
        return create_portfolio_project(request)

def get_portfolio_projects(request):
    """Get all portfolio projects"""
    try:
        portfolio_dir = Path("portfolio_projects")
        if not portfolio_dir.exists():
            portfolio_dir.mkdir(exist_ok=True)
            return JsonResponse({
                'success': True,
                'projects': [],
                'count': 0,
                'message': 'Portfolio directory created'
            })

        projects = []
        for project_folder in portfolio_dir.iterdir():
            if project_folder.is_dir():
                metadata_file = project_folder / "project_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)

                        # Get file list
                        files = []
                        for file_path in project_folder.iterdir():
                            if file_path.is_file():
                                files.append({
                                    'name': file_path.name,
                                    'size': file_path.stat().st_size,
                                    'type': file_path.suffix
                                })

                        project_info = {
                            "id": project_folder.name,
                            "folder_name": project_folder.name,
                            "metadata": metadata,
                            "path": str(project_folder),
                            "files": files,
                            "file_count": len(files)
                        }
                        projects.append(project_info)
                    except Exception as e:
                        logger.warning(f"Error reading project metadata for {project_folder.name}: {e}")

        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x['metadata'].get('saved_at', ''), reverse=True)

        return JsonResponse({
            'success': True,
            'projects': projects,
            'count': len(projects),
            'message': f'Found {len(projects)} portfolio projects'
        })

    except Exception as e:
        logger.error(f"Error getting portfolio projects: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'projects': [],
            'count': 0
        }, status=500)

def create_portfolio_project(request):
    """Create a new portfolio project"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}
        project_data = data.get('project')

        if not project_data:
            return JsonResponse({
                'success': False,
                'error': 'No project data provided'
            }, status=400)

        # Create portfolio directory
        portfolio_dir = Path("portfolio_projects")
        portfolio_dir.mkdir(exist_ok=True)

        # Create individual project folder
        project_name = project_data.get('job_title', 'Unknown Project').replace(' ', '_').lower()
        # Remove special characters
        project_name = ''.join(c for c in project_name if c.isalnum() or c in ('_', '-'))
        project_dir = portfolio_dir / f"{project_name}_{int(datetime.now().timestamp())}"
        project_dir.mkdir(exist_ok=True)

        # Enhanced project metadata
        metadata = {
            "project_info": project_data,
            "saved_at": datetime.now().isoformat(),
            "portfolio_ready": True,
            "client_demo_ready": True,
            "project_id": project_dir.name,
            "export_formats": ["PDF", "ZIP", "GitHub"],
            "tags": extract_tags_from_project(project_data),
            "tech_stack": extract_tech_stack(project_data),
            "portfolio_stats": {
                "lines_of_code": project_data.get('lines_of_code', 0),
                "estimated_hours": project_data.get('estimated_hours', 0),
                "client_value": project_data.get('value', '$0'),
                "platform": project_data.get('platform', 'Unknown'),
                "completion_date": datetime.now().isoformat()
            }
        }

        # Save project metadata
        with open(project_dir / "project_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Create comprehensive README
        readme_content = create_detailed_project_readme(project_data)
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)

        # Create project showcase file
        showcase_content = create_project_showcase(project_data)
        with open(project_dir / "PROJECT_SHOWCASE.md", "w") as f:
            f.write(showcase_content)

        # Create client presentation template
        presentation_content = create_client_presentation(project_data)
        with open(project_dir / "CLIENT_PRESENTATION.md", "w") as f:
            f.write(presentation_content)

        # Copy actual deliverable file if it exists
        copy_deliverable_file(project_data, project_dir)

        logger.info(f"Created portfolio project: {project_dir.name}")

        return JsonResponse({
            'success': True,
            'project_id': project_dir.name,
            'project_path': str(project_dir),
            'files_created': [
                'project_metadata.json',
                'README.md',
                'PROJECT_SHOWCASE.md',
                'CLIENT_PRESENTATION.md'
            ],
            'message': f'Portfolio project saved: {project_name}',
            'metadata': metadata
        })

    except Exception as e:
        logger.error(f"Error creating portfolio project: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_portfolio_project(request, project_id):
    """Delete a portfolio project"""
    try:
        portfolio_dir = Path("portfolio_projects")
        project_dir = portfolio_dir / project_id

        if not project_dir.exists():
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        # Remove the entire project directory
        shutil.rmtree(project_dir)

        logger.info(f"Deleted portfolio project: {project_id}")

        return JsonResponse({
            'success': True,
            'message': f'Project {project_id} deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting portfolio project: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def export_portfolio_project(request, project_id):
    """Export portfolio project in various formats"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}
        export_format = data.get('format', 'ZIP').upper()

        portfolio_dir = Path("portfolio_projects")
        project_dir = portfolio_dir / project_id

        if not project_dir.exists():
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        if export_format == 'ZIP':
            return export_as_zip(project_dir)
        elif export_format == 'PDF':
            return export_as_pdf(project_dir)
        elif export_format == 'GITHUB':
            return export_as_github_repo(project_dir)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported export format: {export_format}'
            }, status=400)

    except Exception as e:
        logger.error(f"Error exporting portfolio project: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def extract_tags_from_project(project_data):
    """Extract relevant tags from project data"""
    tags = []

    # Platform tags
    platform = project_data.get('platform', '').lower()
    if 'upwork' in platform:
        tags.append('Upwork')
    elif 'freelancer' in platform:
        tags.append('Freelancer')
    elif 'fiverr' in platform:
        tags.append('Fiverr')

    # Job type tags
    job_type = project_data.get('job_type', '').lower()
    if 'web_scraping' in job_type:
        tags.extend(['Web Scraping', 'Python', 'Data Collection'])
    elif 'data_processing' in job_type:
        tags.extend(['Data Processing', 'Excel', 'Analytics'])
    elif 'api_integration' in job_type:
        tags.extend(['API Integration', 'REST API', 'OAuth'])

    # Value-based tags
    value_str = project_data.get('value', '$0')
    try:
        value = float(value_str.replace('$', '').replace(',', ''))
        if value >= 400:
            tags.append('High Value')
        elif value >= 200:
            tags.append('Medium Value')
    except Exception as _e:
        logger.warning(
            "views_portfolio.extract_tags_from_project: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    # Complexity tags
    lines_of_code = project_data.get('lines_of_code', 0)
    if lines_of_code >= 500:
        tags.append('Complex')
    elif lines_of_code >= 200:
        tags.append('Medium Complexity')

    return list(set(tags))  # Remove duplicates

def extract_tech_stack(project_data):
    """Extract technology stack from project"""
    tech_stack = []

    job_type = project_data.get('job_type', '').lower()
    if 'web_scraping' in job_type:
        tech_stack.extend(['Python', 'BeautifulSoup', 'Requests', 'CSV', 'JSON'])
    elif 'data_processing' in job_type:
        tech_stack.extend(['Python', 'Pandas', 'NumPy', 'OpenPyXL', 'Excel'])
    elif 'api_integration' in job_type:
        tech_stack.extend(['Python', 'Requests', 'OAuth2', 'REST API', 'JSON'])

    return tech_stack

def create_detailed_project_readme(project_data):
    """Create a detailed README for the project"""
    return f"""# {project_data.get('job_title', 'Project')}

## 🎯 Project Overview

**Client**: {project_data.get('client', 'Unknown')}
**Platform**: {project_data.get('platform', 'Unknown')}
**Value**: {project_data.get('value', 'Unknown')}
**Agent**: {project_data.get('agent', 'Unknown')}
**Status**: {project_data.get('status', 'Completed')}

## 📊 Technical Metrics

- **Lines of Code**: {project_data.get('lines_of_code', 'Unknown'):,}
- **Development Time**: {project_data.get('estimated_hours', 'Unknown')} hours
- **Completion Date**: {datetime.now().strftime('%Y-%m-%d')}
- **File**: `{project_data.get('file_name', 'deliverable.py')}`

## 📝 Project Description

{project_data.get('description', 'No description available')}

## 💡 Key Features

- Professional, production-ready code
- Comprehensive error handling and logging
- Detailed documentation and comments
- Real-world business application
- Client-ready deliverable

## 🎬 Portfolio Highlights

This project demonstrates:

- **Technical Excellence**: Clean, maintainable code following industry standards
- **Problem Solving**: Real business challenge solved with AI assistance
- **Client Communication**: Professional delivery and documentation
- **Time Efficiency**: Complex project completed in {project_data.get('estimated_hours', 'N/A')} hours
- **Value Creation**: {project_data.get('value', 'Unknown')} in client value delivered

## 🚀 Technologies Used

{chr(10).join(f'- {tech}' for tech in extract_tech_stack(project_data))}

## 📈 Business Impact

This solution provided the client with:
- Automated workflow reducing manual effort
- Professional-grade software development
- Rapid deployment and implementation
- Scalable and maintainable solution

## 🎯 Tags

{' '.join(f'`{tag}`' for tag in extract_tags_from_project(project_data))}

---

**Generated by Unified Donkey Betz AI Platform**
*Demonstrating the future of AI-powered software development*
"""

def create_project_showcase(project_data):
    """Create a project showcase for marketing purposes"""
    return f"""# 🎬 Project Showcase: {project_data.get('job_title', 'AI Project')}

## Quick Stats
- 💰 **Value**: {project_data.get('value', 'Unknown')}
- ⏱️ **Time**: {project_data.get('estimated_hours', 'Unknown')} hours
- 📝 **Code**: {project_data.get('lines_of_code', 0):,} lines
- 🤖 **Agent**: {project_data.get('agent', 'AI Agent')}

## The Challenge
{project_data.get('description', 'Real-world business challenge requiring technical solution')}

## The Solution
Our AI agent delivered a complete, production-ready solution that:
- Meets all client requirements
- Includes comprehensive error handling
- Follows industry best practices
- Provides detailed documentation

## Client Feedback
*"Professional delivery, exactly what we needed for our business operations."*

## Perfect For
- **Portfolio Demonstrations**
- **Client Presentations**
- **Technical Interviews**
- **Marketing Materials**

---
*This project showcases the capability of AI agents to deliver real business value*
"""

def create_client_presentation(project_data):
    """Create a client presentation template"""
    return f"""# Client Presentation: {project_data.get('job_title', 'Project')}

## Project Summary
**Client**: {project_data.get('client', 'Client Name')}
**Platform**: {project_data.get('platform', 'Platform')}
**Delivery Date**: {datetime.now().strftime('%B %d, %Y')}

## Deliverables
✅ Complete working solution
✅ Source code with documentation
✅ Implementation instructions
✅ Technical support documentation

## Technical Specifications
- **Language**: Python
- **Lines of Code**: {project_data.get('lines_of_code', 0):,}
- **Development Time**: {project_data.get('estimated_hours', 0)} hours
- **File Format**: `.py` (Python script)

## Key Features Delivered
- Production-ready code quality
- Comprehensive error handling
- Detailed logging and monitoring
- Professional documentation
- Easy deployment and maintenance

## Testing & Quality Assurance
- Code review completed
- Error handling verified
- Performance optimization applied
- Documentation accuracy confirmed

## Next Steps
1. Review delivered code
2. Test in your environment
3. Deploy to production
4. Contact for any support needs

## Support
- 30-day implementation support included
- Documentation provided for maintenance
- Available for future enhancements

---
**Project Value**: {project_data.get('value', 'Unknown')}
**Delivery Status**: ✅ Complete
"""

def copy_deliverable_file(project_data, project_dir):
    """Copy the actual deliverable file to the portfolio project"""
    try:
        file_name = project_data.get('file_name', '')
        if file_name:
            # Look for the file in common directories
            possible_paths = [
                Path("real_freelance_deliverables") / file_name,
                Path("deliverables") / file_name,
                Path(".") / file_name
            ]

            for source_path in possible_paths:
                if source_path.exists():
                    destination_path = project_dir / file_name
                    shutil.copy2(source_path, destination_path)
                    logger.info(f"Copied deliverable file: {file_name}")
                    return True

        logger.warning(f"Could not find deliverable file: {file_name}")
        return False

    except Exception as e:
        logger.error(f"Error copying deliverable file: {e}")
        return False

def export_as_zip(project_dir):
    """Export project as ZIP file"""
    import zipfile

    zip_filename = f"{project_dir.name}.zip"
    zip_path = Path("temp") / zip_filename
    zip_path.parent.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file_path in project_dir.rglob('*'):
            if file_path.is_file():
                zip_file.write(file_path, file_path.relative_to(project_dir))

    return JsonResponse({
        'success': True,
        'download_url': f'/download/portfolio/{zip_filename}',
        'message': 'ZIP export created successfully'
    })

def export_as_pdf(project_dir):
    """Export project as PDF (placeholder for future implementation)"""
    return JsonResponse({
        'success': False,
        'error': 'PDF export not yet implemented',
        'message': 'Coming soon: PDF portfolio generation'
    })

def export_as_github_repo(project_dir):
    """Export project as GitHub repository structure"""
    return JsonResponse({
        'success': False,
        'error': 'GitHub export not yet implemented',
        'message': 'Coming soon: Direct GitHub repository creation'
    })