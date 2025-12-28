"""
Project Builder Agent Base - Extends AIEnforcedAgent with real project building capabilities
"""

import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .ai_enforced_base import AIEnforcedAgent

logger = logging.getLogger(__name__)


class ProjectBuilderAgent(AIEnforcedAgent):
    """
    Base class for agents that can build real projects with file system access
    """

    def __init__(self, agent_name: str = None, user=None, workspace_root: str = None):
        super().__init__(agent_name, user)

        # Set up project workspace
        if workspace_root:
            self.workspace_root = Path(workspace_root)
        else:
            project_root = Path(__file__).parent.parent.parent
            self.workspace_root = project_root / "ai_generated_projects"

        self.workspace_root.mkdir(exist_ok=True)

        # Track files and commands for implementation verification
        self.files_created = []
        self.files_modified = []
        self.commands_executed = []
        self.build_output = []

        logger.info(f"🏗️ Initialized ProjectBuilderAgent: {self.agent_name}")
        logger.info(f"📁 Workspace: {self.workspace_root}")

    def create_project_workspace(self, project_name: str) -> Path:
        """
        Create a dedicated workspace directory for a project

        Args:
            project_name: Name of the project

        Returns:
            Path to the created workspace
        """
        # Sanitize project name
        safe_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        project_path = self.workspace_root / safe_name

        # If directory exists, append timestamp
        if project_path.exists():
            timestamp = datetime.now().strftime('%H%M%S')
            project_path = self.workspace_root / f"{safe_name}_{timestamp}"

        project_path.mkdir(parents=True, exist_ok=True)

        # Create basic structure
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)

        self.current_project_path = project_path

        logger.info(f"📁 Created project workspace: {project_path}")
        return project_path

    def write_file(self, filepath: str, content: str, project_path: Path = None) -> bool:
        """
        Write content to a file in the project workspace

        Args:
            filepath: Relative path to the file
            content: Content to write
            project_path: Project directory (uses current if not specified)

        Returns:
            True if successful
        """
        try:
            if project_path is None:
                if not hasattr(self, 'current_project_path'):
                    raise ValueError("No project path set. Call create_project_workspace first.")
                project_path = self.current_project_path

            full_path = project_path / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists to track creation vs modification
            file_exists = full_path.exists()

            full_path.write_text(content, encoding='utf-8')

            # Track the file operation
            if file_exists:
                self.files_modified.append(str(full_path))
                logger.info(f"📝 Modified file: {filepath}")
            else:
                self.files_created.append(str(full_path))
                logger.info(f"📄 Created file: {filepath}")

            self.build_output.append(f"✅ Written {filepath} ({len(content)} bytes)")
            return True

        except Exception as e:
            error_msg = f"❌ Failed to write {filepath}: {str(e)}"
            logger.error(error_msg)
            self.build_output.append(error_msg)
            return False

    def read_file(self, filepath: str, project_path: Path = None) -> Optional[str]:
        """
        Read content from a file in the project workspace

        Args:
            filepath: Relative path to the file
            project_path: Project directory (uses current if not specified)

        Returns:
            File content or None if failed
        """
        try:
            if project_path is None:
                project_path = self.current_project_path

            full_path = project_path / filepath
            content = full_path.read_text(encoding='utf-8')

            logger.info(f"📖 Read file: {filepath}")
            return content

        except Exception as e:
            logger.error(f"❌ Failed to read {filepath}: {str(e)}")
            return None

    def execute_command(self, command: str, project_path: Path = None, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a shell command in the project workspace

        Args:
            command: Command to execute
            project_path: Project directory (uses current if not specified)
            timeout: Command timeout in seconds

        Returns:
            Dictionary with execution results
        """
        try:
            if project_path is None:
                project_path = self.current_project_path

            logger.info(f"🔧 Executing: {command}")
            self.build_output.append(f"🔧 Executing: {command}")

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Track execution
            execution_record = {
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0,
                'timestamp': datetime.now().isoformat()
            }

            self.commands_executed.append(execution_record)

            if result.returncode == 0:
                logger.info(f"✅ Command succeeded: {command}")
                self.build_output.append(f"✅ Command succeeded")
                if result.stdout.strip():
                    self.build_output.append(f"Output: {result.stdout.strip()}")
            else:
                logger.error(f"❌ Command failed: {command} (exit code: {result.returncode})")
                self.build_output.append(f"❌ Command failed (exit code: {result.returncode})")
                if result.stderr.strip():
                    self.build_output.append(f"Error: {result.stderr.strip()}")

            return execution_record

        except subprocess.TimeoutExpired:
            error_msg = f"⏰ Command timed out after {timeout}s: {command}"
            logger.error(error_msg)
            self.build_output.append(error_msg)

            execution_record = {
                'command': command,
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

            self.commands_executed.append(execution_record)
            return execution_record

        except Exception as e:
            error_msg = f"❌ Failed to execute {command}: {str(e)}"
            logger.error(error_msg)
            self.build_output.append(error_msg)

            execution_record = {
                'command': command,
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

            self.commands_executed.append(execution_record)
            return execution_record

    def install_dependencies(self, package_manager: str = "npm") -> bool:
        """
        Install project dependencies

        Args:
            package_manager: Package manager to use (npm, pip, etc.)

        Returns:
            True if successful
        """
        commands_map = {
            "npm": "npm install",
            "yarn": "yarn install",
            "pip": "pip install -r requirements.txt",
            "poetry": "poetry install",
            "composer": "composer install"
        }

        command = commands_map.get(package_manager, package_manager)
        result = self.execute_command(command)

        return result['success']

    def run_build(self, build_command: str = "npm run build") -> bool:
        """
        Run project build process

        Args:
            build_command: Build command to execute

        Returns:
            True if successful
        """
        result = self.execute_command(build_command)
        return result['success']

    def run_tests(self, test_command: str = "npm test") -> bool:
        """
        Run project tests

        Args:
            test_command: Test command to execute

        Returns:
            True if successful
        """
        result = self.execute_command(test_command)
        return result['success']

    def create_dockerfile(self, base_image: str = "node:18", port: int = 3000) -> bool:
        """
        Create a basic Dockerfile for the project

        Args:
            base_image: Base Docker image
            port: Application port

        Returns:
            True if successful
        """
        dockerfile_content = f"""FROM {base_image}

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE {port}

# Start the application
CMD ["npm", "start"]
"""

        return self.write_file("Dockerfile", dockerfile_content)

    def create_docker_compose(self, services: Dict[str, Any] = None) -> bool:
        """
        Create a docker-compose.yml file

        Args:
            services: Service configurations

        Returns:
            True if successful
        """
        if services is None:
            services = {
                "app": {
                    "build": ".",
                    "ports": ["3000:3000"],
                    "environment": ["NODE_ENV=production"]
                }
            }

        compose_content = {
            "version": "3.8",
            "services": services
        }

        # Convert to YAML-like string (simplified)
        yaml_content = "version: '3.8'\nservices:\n"
        for service_name, config in services.items():
            yaml_content += f"  {service_name}:\n"
            for key, value in config.items():
                if isinstance(value, list):
                    yaml_content += f"    {key}:\n"
                    for item in value:
                        yaml_content += f"      - {item}\n"
                else:
                    yaml_content += f"    {key}: {value}\n"

        return self.write_file("docker-compose.yml", yaml_content)

    def initialize_git(self) -> bool:
        """
        Initialize git repository in project

        Returns:
            True if successful
        """
        commands = [
            "git init",
            "git add .",
            'git commit -m "Initial commit by AI agent"'
        ]

        success = True
        for command in commands:
            result = self.execute_command(command)
            if not result['success']:
                success = False
                break

        return success

    def get_project_structure(self, project_path: Path = None) -> Dict[str, Any]:
        """
        Get the current project structure

        Args:
            project_path: Project directory (uses current if not specified)

        Returns:
            Dictionary representing project structure
        """
        if project_path is None:
            project_path = self.current_project_path

        def scan_directory(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}

            structure = {}
            try:
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue

                    if item.is_file():
                        structure[item.name] = {
                            'type': 'file',
                            'size': item.stat().st_size
                        }
                    elif item.is_dir():
                        structure[item.name] = {
                            'type': 'directory',
                            'contents': scan_directory(item, max_depth, current_depth + 1)
                        }
            except PermissionError:
                pass

            return structure

        return {
            'project_name': project_path.name,
            'structure': scan_directory(project_path)
        }

    def get_implementation_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about what the agent has implemented

        Returns:
            Implementation metrics dictionary
        """
        # Calculate lines added safely
        lines_added = 0
        try:
            for f in self.files_created:
                content = self.read_file(Path(f).name)
                if content and isinstance(content, str):
                    lines_added += len(content.split('\n'))
        except Exception:
            lines_added = 0

        return {
            'files_created': len(self.files_created),
            'files_modified': len(self.files_modified),
            'commands_executed': len(self.commands_executed),
            'successful_commands': len([cmd for cmd in self.commands_executed if cmd.get('success', False)]),
            'failed_commands': len([cmd for cmd in self.commands_executed if not cmd.get('success', False)]),
            'lines_added': lines_added,
            'workspace_path': str(self.workspace_root),
            'current_project': str(getattr(self, 'current_project_path', 'None')),
            'build_output_lines': len(self.build_output)
        }

    def get_build_log(self) -> List[str]:
        """
        Get the build output log

        Returns:
            List of build output messages
        """
        return self.build_output.copy()

    async def generate_project_files(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate project files based on specification using AI

        Args:
            project_spec: Project specification dictionary

        Returns:
            Generation results
        """
        try:
            project_name = project_spec.get('name', 'ai_project')
            tech_stack = project_spec.get('tech_stack', {})
            features = project_spec.get('features', [])

            # Create workspace
            project_path = self.create_project_workspace(project_name)

            # Generate package.json for Node.js projects
            if tech_stack.get('frontend') in ['react', 'vue', 'angular'] or tech_stack.get('backend') == 'node':
                package_json = await self.generate_package_json(project_spec)
                self.write_file('package.json', package_json)

            # Generate requirements.txt for Python projects
            if tech_stack.get('backend') == 'django' or 'python' in str(tech_stack).lower():
                requirements = await self.generate_requirements_txt(project_spec)
                self.write_file('requirements.txt', requirements)

            # Generate main application file
            if tech_stack.get('frontend') == 'react':
                app_js = await self.generate_react_app(project_spec)
                self.write_file('src/App.js', app_js)

                index_html = await self.generate_html_template(project_spec)
                self.write_file('public/index.html', index_html)

            elif tech_stack.get('backend') == 'django':
                django_files = await self.generate_django_project(project_spec)
                for filename, content in django_files.items():
                    self.write_file(filename, content)

            # Generate README
            readme = await self.generate_readme(project_spec)
            self.write_file('README.md', readme)

            # Generate Docker files
            if project_spec.get('containerize', True):
                self.create_dockerfile()
                self.create_docker_compose()

            # Initialize git
            if project_spec.get('git_init', True):
                self.initialize_git()

            return {
                'success': True,
                'project_path': str(project_path),
                'files_created': self.files_created,
                'metrics': self.get_implementation_metrics(),
                'build_log': self.get_build_log()
            }

        except Exception as e:
            error_msg = f"Failed to generate project files: {str(e)}"
            logger.error(error_msg)
            self.build_output.append(f"❌ {error_msg}")

            return {
                'success': False,
                'error': error_msg,
                'build_log': self.get_build_log()
            }

    async def generate_package_json(self, project_spec: Dict[str, Any]) -> str:
        """Generate package.json using AI"""
        prompt = f"""
        Create a package.json file for a {project_spec.get('tech_stack', {}).get('frontend', 'React')} project.

        Project: {project_spec.get('name')}
        Description: {project_spec.get('description')}
        Features: {', '.join(project_spec.get('features', []))}

        Include:
        - Appropriate dependencies for the tech stack
        - Development dependencies
        - Scripts for build, test, start, dev
        - Proper versioning and metadata

        Return only the JSON content, properly formatted.
        """

        return self.generate_ai_text(prompt, task_type="code", max_tokens=800)

    async def generate_requirements_txt(self, project_spec: Dict[str, Any]) -> str:
        """Generate requirements.txt using AI"""
        prompt = f"""
        Create a requirements.txt file for a Python/Django project.

        Project: {project_spec.get('name')}
        Description: {project_spec.get('description')}
        Features: {', '.join(project_spec.get('features', []))}

        Include appropriate Python packages with version constraints.
        Focus on: Django, DRF, database drivers, common utilities.

        Return only the requirements content, one package per line.
        """

        return self.generate_ai_text(prompt, task_type="code", max_tokens=400)

    async def generate_react_app(self, project_spec: Dict[str, Any]) -> str:
        """Generate React App.js using AI"""
        prompt = f"""
        Create a React App.js component for a {project_spec.get('name')} application.

        Description: {project_spec.get('description')}
        Features to implement: {', '.join(project_spec.get('features', []))}

        Include:
        - Modern React with hooks
        - Component structure
        - Basic styling
        - Responsive design
        - Professional UI

        Return only the JavaScript code.
        """

        return self.generate_ai_text(prompt, task_type="code", max_tokens=1200)

    async def generate_html_template(self, project_spec: Dict[str, Any]) -> str:
        """Generate HTML template using AI"""
        prompt = f"""
        Create an index.html file for a React application.

        Project: {project_spec.get('name')}
        Description: {project_spec.get('description')}

        Include:
        - Modern HTML5 structure
        - Meta tags for SEO
        - Proper viewport settings
        - React root div
        - Professional title and description

        Return only the HTML content.
        """

        return self.generate_ai_text(prompt, task_type="code", max_tokens=600)

    async def generate_django_project(self, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Django project files using AI"""
        files = {}

        # Generate settings.py
        settings_prompt = f"""
        Create a Django settings.py file for {project_spec.get('name')}.

        Features: {', '.join(project_spec.get('features', []))}
        Database: {project_spec.get('tech_stack', {}).get('database', 'sqlite')}

        Include:
        - Proper security settings
        - Database configuration
        - Django REST framework setup
        - CORS headers
        - Static/media files setup

        Return only the Python code.
        """

        files['settings.py'] = self.generate_ai_text(settings_prompt, task_type="code", max_tokens=1000)

        # Generate models.py
        models_prompt = f"""
        Create Django models for {project_spec.get('name')}.

        Features: {', '.join(project_spec.get('features', []))}

        Create appropriate models with:
        - Proper field types
        - Relationships
        - Meta classes
        - String representations

        Return only the Python code.
        """

        files['models.py'] = self.generate_ai_text(models_prompt, task_type="code", max_tokens=800)

        return files

    async def generate_readme(self, project_spec: Dict[str, Any]) -> str:
        """Generate README.md using AI"""
        prompt = f"""
        Create a comprehensive README.md for {project_spec.get('name')}.

        Description: {project_spec.get('description')}
        Tech Stack: {project_spec.get('tech_stack', {})}
        Features: {', '.join(project_spec.get('features', []))}

        Include:
        - Project description
        - Installation instructions
        - Usage examples
        - API documentation if applicable
        - Contributing guidelines
        - License information

        Use proper Markdown formatting.
        """

        return self.generate_ai_text(prompt, task_type="documentation", max_tokens=1200)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Default execute method for base ProjectBuilderAgent.
        Subclasses should override this for specific functionality.
        """
        return {
            'success': True,
            'message': 'ProjectBuilderAgent base execute method called',
            'agent': self.agent_name,
            'capabilities': 'file_system_access, command_execution, workspace_management'
        }


class FullStackBuilderAgent(ProjectBuilderAgent):
    """Specialized agent for building complete full-stack applications"""

    async def execute(self, project_idea: str, tech_stack: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
        """Build a complete full-stack application"""
        try:
            # Create project specification
            project_spec = {
                'name': kwargs.get('project_name', 'fullstack_app'),
                'description': project_idea,
                'tech_stack': tech_stack or {
                    'frontend': 'react',
                    'backend': 'node',
                    'database': 'postgres'
                },
                'features': kwargs.get('features', ['user_auth', 'dashboard', 'api']),
                'containerize': kwargs.get('containerize', True),
                'git_init': kwargs.get('git_init', True)
            }

            # Generate project files
            result = await self.generate_project_files(project_spec)

            if result['success']:
                # Install dependencies
                self.build_output.append("📦 Installing dependencies...")
                deps_installed = self.install_dependencies()

                # Run build if dependencies installed
                if deps_installed:
                    self.build_output.append("🔨 Building project...")
                    build_success = self.run_build()
                    result['build_success'] = build_success

                # Run tests
                self.build_output.append("🧪 Running tests...")
                test_success = self.run_tests()
                result['test_success'] = test_success

            result['agent'] = self.agent_name
            result['ai_stats'] = self.get_ai_usage_stats()
            result['build_log'] = self.get_build_log()
            result['metrics'] = self.get_implementation_metrics()

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent': self.agent_name,
                'build_log': self.get_build_log()
            }