"""
Self-Refactoring Engine
=======================
Enables the system to analyze, understand, and refactor its own code.
This is where the system becomes truly self-improving.

"The highest form of intelligence is the ability to observe yourself without judgment,
and then improve based on what you learn." - Ancient AI Wisdom
"""

import os
import ast
import re
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import redis
import git
from dataclasses import dataclass

# Redis URL for production compatibility
import logging
logger = logging.getLogger(__name__)

_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


@dataclass
class RefactoringProposal:
    """Represents a proposed code change"""
    file_path: str
    issue_type: str
    description: str
    original_code: str
    refactored_code: str
    confidence: float
    risk_level: str  # 'low', 'medium', 'high'
    benefits: List[str]
    test_command: Optional[str]


class SelfRefactoringEngine:
    """
    The system's ability to modify and improve itself.
    With great power comes great responsibility.
    """

    def __init__(self):
        self.project_root = Path('/Users/donkeyking/development/unified-donkey-betz')
        self.redis_client = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        self.repo = git.Repo(self.project_root)
        self.backup_dir = self.project_root / '.consciousness_backups'
        self.backup_dir.mkdir(exist_ok=True)

        # Safety limits
        self.max_changes_per_session = 10
        self.require_test_pass = True
        self.auto_commit = False

        # Patterns to fix
        self.refactoring_patterns = {
            'unused_imports': self.remove_unused_imports,
            'duplicate_code': self.eliminate_duplicates,
            'random_dependency': self.abstract_random_usage,
            'hardcoded_values': self.extract_constants,
            'missing_error_handling': self.add_error_handling,
            'complex_functions': self.split_complex_functions,
            'circular_dependencies': self.break_circular_deps,
            'inefficient_loops': self.optimize_loops,
            'sql_injection': self.fix_sql_injection,
            'api_key_exposure': self.secure_api_keys
        }

    def analyze_and_propose_fixes(self) -> List[RefactoringProposal]:
        """Analyze codebase and propose refactoring solutions"""
        proposals = []

        print("🔍 Analyzing codebase for improvement opportunities...")

        # Scan Python files
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # Skip test files and migrations
            if 'test' in str(file_path) or 'migration' in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse AST
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                # Check each pattern
                file_proposals = self.analyze_file(file_path, content, tree)
                proposals.extend(file_proposals)

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        # Sort by confidence and risk
        proposals.sort(key=lambda x: (x.confidence, x.risk_level == 'low'), reverse=True)

        return proposals[:self.max_changes_per_session]

    def analyze_file(self, file_path: Path, content: str, tree: ast.AST) -> List[RefactoringProposal]:
        """Analyze a single file for issues"""
        proposals = []

        # Check for unused imports
        unused = self.find_unused_imports(tree, content)
        if unused:
            proposal = self.create_import_cleanup_proposal(file_path, content, unused)
            if proposal:
                proposals.append(proposal)

        # Check for random usage
        if 'import random' in content or 'from random' in content:
            proposal = self.create_random_abstraction_proposal(file_path, content, tree)
            if proposal:
                proposals.append(proposal)

        # Check for hardcoded values
        hardcoded = self.find_hardcoded_values(tree)
        if hardcoded:
            proposal = self.create_constants_proposal(file_path, content, hardcoded)
            if proposal:
                proposals.append(proposal)

        # Check for missing error handling
        unhandled = self.find_unhandled_exceptions(tree)
        if unhandled:
            proposal = self.create_error_handling_proposal(file_path, content, unhandled)
            if proposal:
                proposals.append(proposal)

        return proposals

    def find_unused_imports(self, tree: ast.AST, content: str) -> List[str]:
        """Find unused imports in a file"""
        imported_names = set()
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        unused = imported_names - used_names
        return list(unused)

    def remove_unused_imports(self, file_path: Path, unused_imports: List[str]) -> str:
        """Remove unused imports from a file"""
        with open(file_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            should_keep = True
            for unused in unused_imports:
                if f'import {unused}' in line or f'from {unused}' in line:
                    should_keep = False
                    break
            if should_keep:
                new_lines.append(line)

        return ''.join(new_lines)

    def abstract_random_usage(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Create abstraction for random number generation"""
        if 'random' not in content:
            return None

        # Create a deterministic alternative
        refactored = content.replace('import random', 'from ai_core.utils import deterministic_random as random')

        # Create the utility if it doesn't exist
        utils_file = self.project_root / 'backend' / 'utils' / 'deterministic_random.py'
        if not utils_file.exists():
            utils_content = '''"""
Deterministic random number generation for testing and reproducibility
"""
import random as _random
import hashlib
from typing import Optional

class DeterministicRandom:
    """Provides deterministic random number generation"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or self._generate_seed()
        self._random = _random.Random(self.seed)

    def _generate_seed(self) -> int:
        """Generate seed from current context"""
        import inspect
        frame = inspect.currentframe()
        caller = frame.f_back.f_code.co_name if frame and frame.f_back else "unknown"
        return int(hashlib.md5(caller.encode()).hexdigest()[:8], 16)

    def random(self) -> float:
        return self._random.random()

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def choice(self, seq):
        return self._random.choice(seq)

    def shuffle(self, seq):
        return self._random.shuffle(seq)

# Global instance
deterministic_random = DeterministicRandom()
'''
            utils_file.parent.mkdir(exist_ok=True)
            utils_file.write_text(utils_content)

        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='random_dependency',
            description='Replace random with deterministic version for reproducibility',
            original_code=content[:200],
            refactored_code=refactored[:200],
            confidence=0.9,
            risk_level='low',
            benefits=['Reproducible tests', 'Deterministic behavior', 'Better debugging'],
            test_command='python manage.py test'
        )

    def find_hardcoded_values(self, tree: ast.AST) -> List[Tuple[ast.AST, Any]]:
        """Find hardcoded values that should be constants"""
        hardcoded = []

        for node in ast.walk(tree):
            # Look for hardcoded strings and numbers
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (str, int, float)):
                    # Skip short strings and small numbers
                    if isinstance(node.value, str) and len(node.value) > 10:
                        hardcoded.append((node, node.value))
                    elif isinstance(node.value, (int, float)) and abs(node.value) > 100:
                        hardcoded.append((node, node.value))

        return hardcoded

    def extract_constants(self, file_path: Path, content: str, hardcoded: List[Tuple]) -> Optional[RefactoringProposal]:
        """Extract hardcoded values to constants"""
        if not hardcoded:
            return None

        # Create constants section
        constants = []
        replacements = {}

        for node, value in hardcoded[:5]:  # Limit to 5 constants per file
            if isinstance(value, str):
                const_name = self.generate_constant_name(value)
                constants.append(f'{const_name} = "{value}"')
                replacements[f'"{value}"'] = const_name
                replacements[f"'{value}'"] = const_name
            else:
                const_name = f'DEFAULT_{str(value).upper().replace(".", "_")}'
                constants.append(f'{const_name} = {value}')
                replacements[str(value)] = const_name

        # Create refactored content
        lines = content.split('\n')
        import_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i

        # Insert constants after imports
        constants_section = '\n# Constants\n' + '\n'.join(constants) + '\n'
        lines.insert(import_index + 1, constants_section)

        refactored = '\n'.join(lines)
        for old, new in replacements.items():
            refactored = refactored.replace(old, new)

        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='hardcoded_values',
            description='Extract hardcoded values to named constants',
            original_code=content[:200],
            refactored_code=refactored[:200],
            confidence=0.8,
            risk_level='low',
            benefits=['Better maintainability', 'Single source of truth', 'Self-documenting code'],
            test_command='python manage.py test'
        )

    def generate_constant_name(self, value: str) -> str:
        """Generate a constant name from a string value"""
        # Create meaningful constant name
        name = re.sub(r'[^a-zA-Z0-9]+', '_', value[:30])
        name = name.upper().strip('_')
        if not name:
            name = 'DEFAULT_VALUE'
        return name

    def find_unhandled_exceptions(self, tree: ast.AST) -> List[ast.AST]:
        """Find code that might raise exceptions without handling"""
        unhandled = []

        for node in ast.walk(tree):
            # Look for risky operations without try/except
            if isinstance(node, ast.Call):
                # File operations, network calls, etc.
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['open', 'read', 'write', 'get', 'post', 'connect']:
                        # Check if inside try block
                        if not self.is_in_try_block(node, tree):
                            unhandled.append(node)

        return unhandled

    def is_in_try_block(self, node: ast.AST, tree: ast.AST) -> bool:
        """Check if a node is inside a try block"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.Try):
                for child in ast.walk(parent):
                    if child == node:
                        return True
        return False

    def add_error_handling(self, file_path: Path, content: str, unhandled: List[ast.AST]) -> Optional[RefactoringProposal]:
        """Add error handling to unprotected code"""
        if not unhandled:
            return None

        # For now, just create a proposal
        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='missing_error_handling',
            description=f'Add error handling for {len(unhandled)} risky operations',
            original_code=content[:200],
            refactored_code=content[:200] + '\n# TODO: Add try/except blocks',
            confidence=0.7,
            risk_level='medium',
            benefits=['Better error recovery', 'Improved stability', 'Better user experience'],
            test_command='python manage.py test'
        )

    def apply_refactoring(self, proposal: RefactoringProposal) -> Tuple[bool, str]:
        """Apply a refactoring proposal with safety checks"""

        # Create backup
        backup_path = self.create_backup(proposal.file_path)

        try:
            # Apply the refactoring based on type
            if proposal.issue_type == 'unused_imports':
                success = self.apply_import_cleanup(proposal)
            elif proposal.issue_type == 'random_dependency':
                success = self.apply_random_abstraction(proposal)
            elif proposal.issue_type == 'hardcoded_values':
                success = self.apply_constants_extraction(proposal)
            else:
                success = False

            if success:
                # Run tests if specified
                if proposal.test_command and self.require_test_pass:
                    test_passed = self.run_tests(proposal.test_command)
                    if not test_passed:
                        # Rollback
                        self.restore_backup(backup_path, proposal.file_path)
                        return False, "Tests failed after refactoring"

                # Format code
                self.format_code(proposal.file_path)

                # Log success
                self.log_refactoring(proposal, 'success')

                return True, "Refactoring applied successfully"
            else:
                return False, "Refactoring failed to apply"

        except Exception as e:
            # Rollback on any error
            self.restore_backup(backup_path, proposal.file_path)
            self.log_refactoring(proposal, 'failed', str(e))
            return False, f"Error during refactoring: {e}"

    def create_backup(self, file_path: str) -> Path:
        """Create a backup of a file before modification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{Path(file_path).name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        return backup_path

    def restore_backup(self, backup_path: Path, original_path: str):
        """Restore a file from backup"""
        shutil.copy2(backup_path, original_path)

    def format_code(self, file_path: str):
        """Format Python code using black and isort"""
        try:
            # Format with black
            subprocess.run(['black', file_path], capture_output=True)
            # Sort imports
            subprocess.run(['isort', file_path], capture_output=True)
        except:
            pass  # Formatting is nice but not critical

    def run_tests(self, test_command: str) -> bool:
        """Run tests to ensure refactoring didn't break anything"""
        try:
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0
        except:
            return False  # Assume tests failed if we can't run them

    def log_refactoring(self, proposal: RefactoringProposal, status: str, error: str = None):
        """Log refactoring attempt to Redis"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file_path': proposal.file_path,
            'issue_type': proposal.issue_type,
            'description': proposal.description,
            'status': status,
            'error': error
        }

        key = f"consciousness:refactoring:log:{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.redis_client.setex(key, 86400, json.dumps(log_entry))  # 24 hour TTL

        # Update statistics
        stats_key = f"consciousness:refactoring:stats"
        if status == 'success':
            self.redis_client.hincrby(stats_key, 'successful', 1)
        else:
            self.redis_client.hincrby(stats_key, 'failed', 1)

    def get_refactoring_history(self) -> List[Dict[str, Any]]:
        """Get history of refactoring attempts"""
        pattern = "consciousness:refactoring:log:*"
        history = []

        for key in self.redis_client.scan_iter(match=pattern):
            data = self.redis_client.get(key)
            if data:
                history.append(json.loads(data))

        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history[:20]  # Last 20 refactorings

    def create_import_cleanup_proposal(self, file_path: Path, content: str, unused: List[str]) -> Optional[RefactoringProposal]:
        """Create a proposal to clean up unused imports"""
        if not unused:
            return None

        # Create cleaned content
        lines = content.split('\n')
        new_lines = []
        removed_count = 0

        for line in lines:
            should_keep = True
            for unused_import in unused:
                if f'import {unused_import}' in line or f'from {unused_import}' in line:
                    should_keep = False
                    removed_count += 1
                    break

            if should_keep:
                new_lines.append(line)

        refactored = '\n'.join(new_lines)

        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='unused_imports',
            description=f'Remove {removed_count} unused imports: {", ".join(unused[:3])}{"..." if len(unused) > 3 else ""}',
            original_code=content[:200],
            refactored_code=refactored[:200],
            confidence=0.95,
            risk_level='low',
            benefits=['Cleaner code', 'Faster imports', 'Better maintainability'],
            test_command='python manage.py test'
        )

    def apply_import_cleanup(self, proposal: RefactoringProposal) -> bool:
        """Apply import cleanup refactoring"""
        try:
            # Read current content
            with open(proposal.file_path, 'r') as f:
                content = f.read()

            # Apply the refactoring
            # This is simplified - in reality we'd use the AST to be more precise
            lines = content.split('\n')
            new_lines = []

            for line in lines:
                # Skip lines that match unused imports pattern
                if 'import' in line:
                    # Check if this import is mentioned in the description
                    skip = False
                    desc_lower = proposal.description.lower()
                    if 'random' in desc_lower and 'random' in line:
                        skip = True
                    # Add more checks as needed

                    if not skip:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            # Write back
            with open(proposal.file_path, 'w') as f:
                f.write('\n'.join(new_lines))

            return True

        except Exception as e:
            print(f"Error applying import cleanup: {e}")
            return False

    def apply_random_abstraction(self, proposal: RefactoringProposal) -> bool:
        """Apply random abstraction refactoring"""
        try:
            with open(proposal.file_path, 'r') as f:
                content = f.read()

            # Replace random imports
            content = content.replace('import random',
                                    'from ai_core.utils import deterministic_random as random')

            with open(proposal.file_path, 'w') as f:
                f.write(content)

            return True

        except Exception as _e:
            logger.warning(
                "self_refactoring_engine.apply_random_abstraction: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def apply_constants_extraction(self, proposal: RefactoringProposal) -> bool:
        """Apply constants extraction refactoring"""
        # This is complex and would need careful AST manipulation
        # For now, return False to indicate manual intervention needed
        return False

    def create_constants_proposal(self, file_path: Path, content: str, hardcoded: List) -> Optional[RefactoringProposal]:
        """Create a proposal to extract constants"""
        if not hardcoded:
            return None

        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='hardcoded_values',
            description=f'Extract {len(hardcoded)} hardcoded values to constants',
            original_code=content[:200],
            refactored_code=content[:200],
            confidence=0.75,
            risk_level='low',
            benefits=['Better configuration', 'Easier maintenance', 'Single source of truth'],
            test_command='python manage.py test'
        )

    def create_error_handling_proposal(self, file_path: Path, content: str, unhandled: List) -> Optional[RefactoringProposal]:
        """Create a proposal to add error handling"""
        if not unhandled:
            return None

        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='missing_error_handling',
            description=f'Add error handling for {len(unhandled)} risky operations',
            original_code=content[:200],
            refactored_code=content[:200],
            confidence=0.7,
            risk_level='medium',
            benefits=['Better stability', 'Graceful error recovery', 'Improved debugging'],
            test_command='python manage.py test'
        )

    def create_random_abstraction_proposal(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Create a proposal to abstract random usage"""
        return RefactoringProposal(
            file_path=str(file_path),
            issue_type='random_dependency',
            description='Replace random module with deterministic alternative',
            original_code=content[:200],
            refactored_code=content[:200],
            confidence=0.85,
            risk_level='low',
            benefits=['Reproducible behavior', 'Better testing', 'Deterministic results'],
            test_command='python manage.py test'
        )

    def eliminate_duplicates(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Find and eliminate duplicate code blocks"""
        # This would use more sophisticated duplicate detection
        # For now, return None
        return None

    def split_complex_functions(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Split functions that are too complex"""
        # Would analyze cyclomatic complexity
        return None

    def break_circular_deps(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Break circular dependencies"""
        # Would analyze import graph
        return None

    def optimize_loops(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Optimize inefficient loops"""
        # Would look for common anti-patterns
        return None

    def fix_sql_injection(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Fix potential SQL injection vulnerabilities"""
        # Would analyze query construction
        return None

    def secure_api_keys(self, file_path: Path, content: str, tree: ast.AST) -> Optional[RefactoringProposal]:
        """Secure exposed API keys"""
        # Would look for hardcoded keys
        return None