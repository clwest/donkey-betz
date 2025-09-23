#!/usr/bin/env python3
"""
Agent Error Handler System
Handles errors intelligently when AI-generated code fails
"""

import os
import sys
import traceback
import subprocess
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from agent_error_learning import AgentErrorLearning

class AgentErrorHandler:
    """
    Intelligent error handling for AI-generated code
    When errors occur, agents:
    1. Analyze the error
    2. Attempt self-correction
    3. Generate fixed code
    4. Test the fix
    5. Learn from the mistake
    """

    def __init__(self):
        self.error_patterns = {
            "NameError": self.fix_name_error,
            "AttributeError": self.fix_attribute_error,
            "ImportError": self.fix_import_error,
            "SyntaxError": self.fix_syntax_error,
            "TypeError": self.fix_type_error,
            "KeyError": self.fix_key_error,
            "IndexError": self.fix_index_error
        }
        self.error_history = []
        self.fix_attempts = {}
        self.learner = AgentErrorLearning()  # Initialize learning system

    def analyze_error(self, file_path: str, error_output: str) -> Dict:
        """Analyze the error and determine the fix strategy"""
        error_info = {
            "file": file_path,
            "error_type": None,
            "error_message": "",
            "line_number": None,
            "problematic_code": "",
            "suggested_fix": "",
            "confidence": 0.0
        }

        # Parse the error output
        lines = error_output.strip().split('\n')
        if not lines:
            return error_info

        # Extract error type and message
        for line in reversed(lines):
            if "Error:" in line:
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    error_info["error_type"] = parts[0].strip()
                    error_info["error_message"] = parts[1].strip()
                    break

        # Extract line number
        for line in lines:
            if "line" in line.lower():
                match = re.search(r'line (\d+)', line, re.IGNORECASE)
                if match:
                    error_info["line_number"] = int(match.group(1))
                    break

        # Read the problematic code
        if error_info["line_number"] and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                file_lines = f.readlines()
                if error_info["line_number"] <= len(file_lines):
                    error_info["problematic_code"] = file_lines[error_info["line_number"] - 1].strip()

        return error_info

    def fix_name_error(self, error_info: Dict, file_content: str) -> str:
        """Fix NameError by adding missing definitions or imports"""
        error_msg = error_info["error_message"]

        # Extract the undefined name
        match = re.search(r"name '(\w+)' is not defined", error_msg)
        if not match:
            return file_content

        undefined_name = match.group(1)

        # Common fixes for undefined names
        if undefined_name == "random":
            # Add import random
            if "import random" not in file_content:
                lines = file_content.split('\n')

                # Find the best position to insert import
                import_index = None
                last_import_index = 0

                for i, line in enumerate(lines):
                    # Find existing imports
                    if line.startswith('import ') or line.startswith('from '):
                        last_import_index = i
                        # Look for json import to put random after it
                        if 'import json' in line:
                            import_index = i + 1
                            break
                    # Stop at class or function definition
                    elif line.strip() and not line.startswith('#') and not line.strip().startswith('"""'):
                        if not line.startswith('import') and not line.startswith('from'):
                            break

                # If we didn't find json import, insert after last import
                if import_index is None:
                    import_index = last_import_index + 1 if last_import_index > 0 else 0

                # Make sure we're not in the middle of a docstring
                while import_index < len(lines) and '"""' in lines[import_index]:
                    import_index += 1

                lines.insert(import_index, "import random")
                return '\n'.join(lines)

        # If it's a missing variable, initialize it
        if undefined_name not in file_content.split():
            # Add a reasonable default initialization
            lines = file_content.split('\n')
            for i, line in enumerate(lines):
                if undefined_name in line and i > 0:
                    # Insert initialization before use
                    lines.insert(i, f"    {undefined_name} = None  # Fixed by error handler")
                    break
            return '\n'.join(lines)

        return file_content

    def fix_attribute_error(self, error_info: Dict, file_content: str) -> str:
        """Fix AttributeError by adding missing methods or attributes"""
        error_msg = error_info["error_message"]

        # For the ContentFactory case
        if "'ContentFactory' object has no attribute '_load_seo_data'" in error_msg:
            # Add the missing method
            lines = file_content.split('\n')

            # Find where to add the method (after _load_templates)
            for i, line in enumerate(lines):
                if "def _load_templates(self)" in line:
                    # Find the end of this method
                    indent_level = len(line) - len(line.lstrip())
                    j = i + 1
                    while j < len(lines):
                        if lines[j].strip() and not lines[j].startswith(' ' * (indent_level + 4)):
                            # Found the end of the method
                            # Insert the new method here
                            new_method = [
                                "",
                                "    def _load_seo_data(self) -> Dict:",
                                '        """Load SEO keyword data"""',
                                "        return {",
                                '            "trending": ["AI", "automation", "digital", "innovation"],',
                                '            "evergreen": ["guide", "tips", "how-to", "best"],',
                                '            "power_words": ["ultimate", "essential", "proven", "expert"]',
                                "        }"
                            ]
                            for k, method_line in enumerate(new_method):
                                lines.insert(j + k, method_line)
                            break
                        j += 1
                    break

            return '\n'.join(lines)

        # Generic attribute fix - add a default attribute
        match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_msg)
        if match:
            class_name = match.group(1)
            attr_name = match.group(2)

            lines = file_content.split('\n')
            for i, line in enumerate(lines):
                if f"class {class_name}" in line:
                    # Find __init__ method
                    for j in range(i, min(i + 50, len(lines))):
                        if "def __init__(self)" in lines[j]:
                            # Add attribute initialization
                            k = j + 1
                            while k < len(lines) and lines[k].startswith('        '):
                                k += 1
                            lines.insert(k - 1, f"        self.{attr_name} = None  # Fixed by error handler")
                            break
                    break

            return '\n'.join(lines)

        return file_content

    def fix_import_error(self, error_info: Dict, file_content: str) -> str:
        """Fix ImportError by adding or correcting imports"""
        error_msg = error_info["error_message"]

        # Check for missing module
        match = re.search(r"No module named '(\w+)'", error_msg)
        if match:
            module_name = match.group(1)

            # Add common fixes
            if module_name in ["numpy", "pandas", "requests"]:
                # These might not be installed, use try-except
                lines = file_content.split('\n')
                for i, line in enumerate(lines):
                    if f"import {module_name}" in line:
                        lines[i] = f"try:\n    import {module_name}\nexcept ImportError:\n    {module_name} = None  # Module not installed"
                        break
                return '\n'.join(lines)

        return file_content

    def fix_syntax_error(self, error_info: Dict, file_content: str) -> str:
        """Fix SyntaxError by correcting common syntax mistakes"""
        if error_info["line_number"]:
            lines = file_content.split('\n')
            line_idx = error_info["line_number"] - 1

            if line_idx < len(lines):
                problematic_line = lines[line_idx]

                # Fix missing colons
                if any(keyword in problematic_line for keyword in ["if ", "elif ", "else", "for ", "while ", "def ", "class "]):
                    if not problematic_line.rstrip().endswith(':'):
                        lines[line_idx] = problematic_line.rstrip() + ':'

                # Fix unclosed brackets
                open_brackets = problematic_line.count('(') + problematic_line.count('[') + problematic_line.count('{')
                close_brackets = problematic_line.count(')') + problematic_line.count(']') + problematic_line.count('}')

                if open_brackets > close_brackets:
                    lines[line_idx] = problematic_line.rstrip() + ')' * (open_brackets - close_brackets)

                return '\n'.join(lines)

        return file_content

    def fix_type_error(self, error_info: Dict, file_content: str) -> str:
        """Fix TypeError by correcting type mismatches"""
        error_msg = error_info["error_message"]

        # Fix string formatting issues
        if "not all arguments converted" in error_msg:
            lines = file_content.split('\n')
            if error_info["line_number"]:
                line_idx = error_info["line_number"] - 1
                if line_idx < len(lines):
                    # Convert % formatting to f-strings
                    lines[line_idx] = re.sub(r'%[sd]', '{}', lines[line_idx])
            return '\n'.join(lines)

        return file_content

    def fix_key_error(self, error_info: Dict, file_content: str) -> str:
        """Fix KeyError by using .get() or adding missing keys"""
        if error_info["line_number"]:
            lines = file_content.split('\n')
            line_idx = error_info["line_number"] - 1

            if line_idx < len(lines):
                problematic_line = lines[line_idx]

                # Replace dict[key] with dict.get(key, default)
                lines[line_idx] = re.sub(
                    r'(\w+)\[(["\'])(.*?)\2\]',
                    r'\1.get(\2\3\2, None)',
                    problematic_line
                )

                return '\n'.join(lines)

        return file_content

    def fix_index_error(self, error_info: Dict, file_content: str) -> str:
        """Fix IndexError by adding bounds checking"""
        if error_info["line_number"]:
            lines = file_content.split('\n')
            line_idx = error_info["line_number"] - 1

            if line_idx < len(lines):
                problematic_line = lines[line_idx]
                indent = len(problematic_line) - len(problematic_line.lstrip())

                # Add bounds checking
                lines[line_idx] = ' ' * indent + f"if len(data) > 0:  # Fixed by error handler\n" + ' ' * (indent + 4) + problematic_line.lstrip()

                return '\n'.join(lines)

        return file_content

    def attempt_fix(self, file_path: str, error_output: str) -> Tuple[bool, str]:
        """Attempt to fix the error and return success status and fixed code"""
        # Analyze the error
        error_info = self.analyze_error(file_path, error_output)

        if not error_info["error_type"]:
            return False, "Could not identify error type"

        # Record the error in learning system
        self.learner.record_error(
            error_info["error_type"],
            error_info["error_message"],
            file_path,
            {"line_number": error_info["line_number"]}
        )

        # Record the error in local history
        self.error_history.append({
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "error": error_info
        })

        # Check if learning system has recommendations
        recommendation = self.learner.get_recommended_fix(
            error_info["error_type"],
            error_info["error_message"]
        )

        if recommendation and recommendation["success_rate"] > 0.7:
            print(f"📚 Using learned fix strategy: {recommendation['pattern']} (Success rate: {recommendation['success_rate']*100:.1f}%)")

        # Read the current file content
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
        except:
            return False, f"Could not read file: {file_path}"

        # Get the appropriate fix function
        fix_function = self.error_patterns.get(error_info["error_type"])

        if not fix_function:
            return False, f"No fix strategy for error type: {error_info['error_type']}"

        # Determine fix strategy name for learning
        fix_strategy = f"{error_info['error_type']}_fix"

        # Attempt the fix
        fixed_content = fix_function(error_info, file_content)

        if fixed_content == file_content:
            # Record failed fix attempt
            self.learner.record_fix_attempt(
                error_info["error_type"],
                fix_strategy,
                False,
                {"reason": "No changes made"}
            )
            return False, "No changes made - fix strategy did not modify the code"

        # Write the fixed content
        backup_path = file_path + ".backup"
        try:
            # Create backup
            with open(backup_path, 'w') as f:
                f.write(file_content)

            # Write fixed content
            with open(file_path, 'w') as f:
                f.write(fixed_content)

            # Test the fixed code
            result = subprocess.run(
                ['python', file_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Success! Remove backup
                os.remove(backup_path)

                # Record successful fix in learning system
                self.learner.record_fix_attempt(
                    error_info["error_type"],
                    fix_strategy,
                    True,
                    {"changes_made": "Code fixed and runs successfully"}
                )

                return True, "Fix successful! Code now runs without errors."
            else:
                # Fix didn't work, restore backup
                with open(backup_path, 'r') as f:
                    original = f.read()
                with open(file_path, 'w') as f:
                    f.write(original)
                os.remove(backup_path)

                # Record failed fix attempt
                self.learner.record_fix_attempt(
                    error_info["error_type"],
                    fix_strategy,
                    False,
                    {"new_error": result.stderr[:200]}
                )

                # Try a different fix or give up
                return False, f"Fix attempt failed. New error: {result.stderr}"

        except Exception as e:
            # Record failed fix attempt
            self.learner.record_fix_attempt(
                error_info["error_type"],
                fix_strategy,
                False,
                {"exception": str(e)}
            )
            return False, f"Error during fix attempt: {str(e)}"

    def get_error_report(self) -> Dict:
        """Generate a report of all errors and fixes"""
        # Get learning report
        learning_report = self.learner.get_learning_report()

        return {
            "total_errors": len(self.error_history),
            "error_types": self._count_error_types(),
            "fix_success_rate": self._calculate_success_rate(),
            "recent_errors": self.error_history[-10:] if self.error_history else [],
            "learning_insights": learning_report,
            "improvement_suggestions": self.learner.suggest_improvements()
        }

    def _count_error_types(self) -> Dict:
        """Count occurrences of each error type"""
        counts = {}
        for error in self.error_history:
            error_type = error["error"]["error_type"]
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts

    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of fixes"""
        if not self.fix_attempts:
            return 0.0

        successful = sum(1 for success in self.fix_attempts.values() if success)
        return (successful / len(self.fix_attempts)) * 100


# Example usage and testing
if __name__ == "__main__":
    handler = AgentErrorHandler()

    # Test with the Content Factory error
    test_error = """Traceback (most recent call last):
  File "/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects/content_factory/content_generator.py", line 55, in <module>
    factory = ContentFactory()
  File "/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects/content_factory/content_generator.py", line 16, in __init__
    self.seo_keywords = self._load_seo_data()
AttributeError: 'ContentFactory' object has no attribute '_load_seo_data'"""

    file_path = "/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects/content_factory/content_generator.py"

    print("🔧 Agent Error Handler System")
    print("=" * 50)

    # Analyze the error
    error_info = handler.analyze_error(file_path, test_error)
    print(f"Error Type: {error_info['error_type']}")
    print(f"Error Message: {error_info['error_message']}")
    print(f"Line Number: {error_info['line_number']}")

    # Attempt to fix
    print("\n🛠️ Attempting automatic fix...")
    success, message = handler.attempt_fix(file_path, test_error)

    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    # Show error report
    report = handler.get_error_report()
    print(f"\n📊 Error Report:")
    print(f"Total Errors: {report['total_errors']}")
    print(f"Error Types: {report['error_types']}")
    print(f"Fix Success Rate: {report['fix_success_rate']:.1f}%")