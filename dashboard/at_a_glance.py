#!/usr/bin/env python3
"""
At-a-Glance Error Analysis System
Transforms verbose error logs into actionable insights
"""

import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib


class AtAGlanceSystem:
    """
    Intelligent error analysis that shows what matters:
    - The actual problem (not symptoms)
    - The real impact (not noise)
    - The exact fix (not guesswork)
    """
    
    def __init__(self):
        self.error_patterns = {
            'database': {
                'patterns': [
                    r'database "([^"]+)" does not exist',
                    r'relation "([^"]+)" does not exist',
                    r'could not connect to database "([^"]+)"',
                    r'FATAL:.*database "([^"]+)"'
                ],
                'category': 'Database Configuration',
                'severity': 'CRITICAL',
                'icon': '🔴'
            },
            'connection': {
                'patterns': [
                    r'Connection refused.*port (\d+)',
                    r'could not connect to server.*port (\d+)',
                    r'Failed to connect to ([^:]+):(\d+)'
                ],
                'category': 'Service Connectivity',
                'severity': 'HIGH',
                'icon': '🟠'
            },
            'authentication': {
                'patterns': [
                    r'password authentication failed for user "([^"]+)"',
                    r'FATAL:.*user "([^"]+)"',
                    r'Invalid credentials for ([^"]+)'
                ],
                'category': 'Authentication',
                'severity': 'HIGH',
                'icon': '🟡'
            },
            'import': {
                'patterns': [
                    r'ModuleNotFoundError.*No module named [\'"]([^"\']+)',
                    r'ImportError.*cannot import name [\'"]([^"\']+)',
                    r'No module named [\'"]([^"\']+)'
                ],
                'category': 'Missing Dependencies',
                'severity': 'MEDIUM',
                'icon': '🟣'
            },
            'file': {
                'patterns': [
                    r'FileNotFoundError.*No such file.*[\'"]([^"\']+)',
                    r'IOError.*No such file.*[\'"]([^"\']+)',
                    r'cannot open [\'"]([^"\']+)'
                ],
                'category': 'File System',
                'severity': 'LOW',
                'icon': '🔵'
            }
        }
        
        self.fix_database = {
            'database_missing': {
                'unified_donkey_betz': 'createdb unified_donkey_betz',
                'ai_unified_platform': 'sed -i "" "s/ai_unified_platform/unified_donkey_betz/g" ai_core/settings.py',
                'default': 'createdb {db_name}'
            },
            'table_missing': {
                'default': 'python manage.py migrate'
            },
            'connection_failed': {
                'default': 'sudo service postgresql start'
            }
        }
        
        self.learned_fixes = defaultdict(list)
        
    def analyze(self, error_log: str) -> Dict:
        """
        Main analysis entry point
        Returns a beautiful, actionable summary
        """
        lines = error_log.strip().split('\n')
        
        # Deduplicate errors
        unique_errors = self._deduplicate_errors(lines)
        
        # Analyze each unique error
        analyses = []
        for error_hash, error_info in unique_errors.items():
            analysis = self._analyze_single_error(error_info)
            if analysis:
                analyses.append(analysis)
        
        # Generate summary
        return self._generate_summary(analyses)
    
    def _deduplicate_errors(self, lines: List[str]) -> Dict:
        """
        Group identical errors together with counts
        """
        error_groups = defaultdict(lambda: {'count': 0, 'first_seen': None, 
                                            'last_seen': None, 'sample': None,
                                            'locations': set()})
        
        current_error = []
        for line in lines:
            # Simple heuristic: new error starts with timestamp or known pattern
            if self._is_error_start(line):
                if current_error:
                    # Process previous error
                    error_text = '\n'.join(current_error)
                    error_hash = self._hash_error(error_text)
                    error_groups[error_hash]['count'] += 1
                    error_groups[error_hash]['sample'] = error_text
                    
                    # Extract location if present
                    location = self._extract_location(error_text)
                    if location:
                        error_groups[error_hash]['locations'].add(location)
                    
                current_error = [line]
            else:
                current_error.append(line)
        
        # Don't forget the last error
        if current_error:
            error_text = '\n'.join(current_error)
            error_hash = self._hash_error(error_text)
            error_groups[error_hash]['count'] += 1
            error_groups[error_hash]['sample'] = error_text
            
        return error_groups
    
    def _hash_error(self, error_text: str) -> str:
        """
        Create a hash for error deduplication
        Ignores timestamps and specific values
        """
        # Remove timestamps, IDs, specific values
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2}', '', error_text)
        normalized = re.sub(r'\b\d+\b', 'NUM', normalized)
        normalized = re.sub(r'0x[0-9a-fA-F]+', 'HEX', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()[:8]
    
    def _is_error_start(self, line: str) -> bool:
        """
        Detect if a line starts a new error
        """
        error_indicators = [
            r'^\d{4}-\d{2}-\d{2}',  # Timestamp
            r'^ERROR',
            r'^FATAL',
            r'^WARNING',
            r'^Traceback',
            r'^[A-Z][a-zA-Z]*Error:',
            r'^\[ERROR\]',
            r'^\[CRITICAL\]'
        ]
        
        return any(re.match(pattern, line) for pattern in error_indicators)
    
    def _extract_location(self, error_text: str) -> Optional[str]:
        """
        Extract file location from error
        """
        patterns = [
            r'File "([^"]+)", line (\d+)',
            r'at ([^:]+):(\d+)',
            r'in ([^:]+):(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text)
            if match:
                return f"{match.group(1)}:{match.group(2)}"
        
        return None
    
    def _analyze_single_error(self, error_info: Dict) -> Optional[Dict]:
        """
        Analyze a single unique error
        """
        error_text = error_info['sample']
        
        # Match against known patterns
        for error_type, config in self.error_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, error_text, re.IGNORECASE)
                if match:
                    return {
                        'type': error_type,
                        'category': config['category'],
                        'severity': config['severity'],
                        'icon': config['icon'],
                        'count': error_info['count'],
                        'locations': list(error_info['locations'])[:3],  # Top 3 locations
                        'match': match.group(1) if match.groups() else None,
                        'fix': self._suggest_fix(error_type, match),
                        'pattern': pattern,
                        'sample': error_text[:200]  # First 200 chars
                    }
        
        # Unknown error
        return {
            'type': 'unknown',
            'category': 'Unknown Error',
            'severity': 'INFO',
            'icon': '⚪',
            'count': error_info['count'],
            'locations': list(error_info['locations'])[:3],
            'sample': error_text[:200]
        }
    
    def _suggest_fix(self, error_type: str, match) -> Dict:
        """
        Suggest specific fixes based on error type
        """
        fixes = {
            'quick': None,
            'command': None,
            'explanation': None,
            'confidence': 0.0
        }
        
        if error_type == 'database':
            db_name = match.group(1) if match.groups() else 'unknown'
            
            if 'does not exist' in match.string:
                if db_name == 'ai_unified_platform':
                    fixes['quick'] = 'Update database name in settings'
                    fixes['command'] = 'sed -i "" "s/ai_unified_platform/unified_donkey_betz/g" ai_core/settings.py && createdb unified_donkey_betz'
                    fixes['explanation'] = 'Database name mismatch - using old name'
                    fixes['confidence'] = 0.95
                else:
                    fixes['quick'] = f'Create database {db_name}'
                    fixes['command'] = f'createdb {db_name}'
                    fixes['explanation'] = 'Database does not exist'
                    fixes['confidence'] = 0.85
                    
        elif error_type == 'connection':
            port = match.group(1) if match.groups() else 'unknown'
            fixes['quick'] = f'Start service on port {port}'
            
            if port == '5432':
                fixes['command'] = 'brew services start postgresql@14'
                fixes['explanation'] = 'PostgreSQL not running'
                fixes['confidence'] = 0.9
            elif port == '6379':
                fixes['command'] = 'brew services start redis'
                fixes['explanation'] = 'Redis not running'
                fixes['confidence'] = 0.9
            elif port == '8000':
                fixes['command'] = 'python manage.py runserver'
                fixes['explanation'] = 'Django server not running'
                fixes['confidence'] = 0.85
                
        elif error_type == 'import':
            module = match.group(1) if match.groups() else 'unknown'
            fixes['quick'] = f'Install missing module: {module}'
            fixes['command'] = f'pip install {module}'
            fixes['explanation'] = 'Python module not installed'
            fixes['confidence'] = 0.75
            
        return fixes
    
    def _generate_summary(self, analyses: List[Dict]) -> Dict:
        """
        Generate the beautiful "At a Glance" summary
        """
        if not analyses:
            return {
                'status': 'healthy',
                'message': 'No errors detected',
                'icon': '✅'
            }
        
        # Sort by severity and count
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
        analyses.sort(key=lambda x: (severity_order.get(x['severity'], 5), -x['count']))
        
        # Take the most critical error
        top_error = analyses[0]
        
        # Calculate total impact
        total_errors = sum(a['count'] for a in analyses)
        unique_errors = len(analyses)
        
        # Build the glance view
        glance = {
            'status': 'error',
            'icon': top_error['icon'],
            'severity': top_error['severity'],
            'headline': f"{top_error['category']}: {top_error.get('match', 'Issue Detected')}",
            'impact': {
                'total_errors': total_errors,
                'unique_errors': unique_errors,
                'frequency': f"{total_errors} occurrences of {unique_errors} unique errors",
                'top_locations': top_error.get('locations', [])
            },
            'top_issue': {
                'description': top_error['sample'][:100] + '...' if len(top_error['sample']) > 100 else top_error['sample'],
                'count': top_error['count'],
                'fix': top_error.get('fix', {})
            },
            'all_issues': analyses[:5],  # Top 5 issues
            'quick_actions': self._generate_quick_actions(analyses)
        }
        
        return glance
    
    def _generate_quick_actions(self, analyses: List[Dict]) -> List[Dict]:
        """
        Generate prioritized quick actions
        """
        actions = []
        
        for analysis in analyses[:3]:  # Top 3 issues
            fix = analysis.get('fix', {})
            if fix.get('command'):
                actions.append({
                    'command': fix['command'],
                    'description': fix.get('quick', 'Fix issue'),
                    'confidence': fix.get('confidence', 0.5),
                    'impact': f"Resolves {analysis['count']} errors"
                })
        
        return actions
    
    def format_display(self, summary: Dict) -> str:
        """
        Format the summary for beautiful terminal display
        """
        if summary['status'] == 'healthy':
            return f"\n{summary['icon']} {summary['message']}\n"
        
        # Build the beautiful display
        output = []
        
        # Header with severity
        output.append(f"\n{summary['icon']} {summary['severity']}: {summary['headline']}")
        output.append("━" * 50)
        
        # Impact
        output.append(f"📊 Impact: {summary['impact']['frequency']}")
        
        # Top issue with fix
        if summary['top_issue']['fix'].get('command'):
            output.append(f"🔧 Fix: {summary['top_issue']['fix']['quick']}")
            output.append(f"⚡ Command: `{summary['top_issue']['fix']['command']}`")
            output.append(f"🎯 Confidence: {summary['top_issue']['fix']['confidence']*100:.0f}%")
        
        # Location if available
        if summary['impact']['top_locations']:
            output.append(f"📍 Location: {summary['impact']['top_locations'][0]}")
        
        output.append("━" * 50)
        
        # Quick actions
        if summary['quick_actions']:
            output.append("\n⚡ Quick Actions:")
            for i, action in enumerate(summary['quick_actions'], 1):
                output.append(f"  {i}. {action['description']}")
                output.append(f"     `{action['command']}`")
                output.append(f"     → {action['impact']}")
        
        # Other issues summary
        if len(summary['all_issues']) > 1:
            output.append(f"\n📋 Also found {len(summary['all_issues'])-1} other issue(s)")
        
        return '\n'.join(output) + '\n'


def main():
    """
    Demo the At-a-Glance system
    """
    # Example error log
    error_log = '''
    2024-01-09 10:23:45 ERROR: database "ai_unified_platform" does not exist
    2024-01-09 10:23:46 ERROR: database "ai_unified_platform" does not exist
    2024-01-09 10:23:47 ERROR: database "ai_unified_platform" does not exist
    File "ai_core/settings.py", line 136
    2024-01-09 10:24:01 ERROR: Connection refused on port 6379
    2024-01-09 10:24:02 ERROR: ModuleNotFoundError: No module named 'redis'
    '''
    
    system = AtAGlanceSystem()
    summary = system.analyze(error_log)
    print(system.format_display(summary))
    
    # Also output JSON for programmatic use
    print("\n📊 JSON Output:")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == '__main__':
    main()