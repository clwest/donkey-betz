#!/usr/bin/env python3
"""
Focused Code Ingestion - Scans only the core project files

This focuses on the main project files, avoiding node_modules, venv, etc.
and safely handles the data to avoid Unicode issues.
"""

import os
import sys
import django
from pathlib import Path
import ast
import json
from typing import Dict, List, Any, Optional

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import SystemConfiguration, PlatformMetrics
from content.models import (
    Document, ContentTemplate, DocumentType, ContentStatus, 
    ContentSource
)

User = get_user_model()


class FocusedCodeIngestion:
    """Focused codebase ingestion for core project files only"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        
        # Focus on core project directories
        self.focus_directories = [
            'core',
            'content', 
            'dashboard',
            'frontend/src',
            'mobile/src'
        ]
        
        # Skip these directories entirely
        self.skip_directories = {
            'node_modules', '.git', '__pycache__', 'venv', 'env',
            '.pytest_cache', '.mypy_cache', 'dist', 'build',
            '.vscode', '.idea', 'coverage', '.tox',
            'frontend/node_modules', 'mobile/node_modules'
        }
        
        self.focus_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx'}
        
    def run_focused_ingestion(self) -> Dict[str, Any]:
        """Run focused ingestion on core project files only"""
        print("🎯 Starting Focused Code Ingestion...")
        print("=" * 50)
        
        # Scan core files
        core_files = self.scan_core_files()
        
        # Extract patterns
        patterns = self.extract_patterns(core_files)
        
        # Store as documents
        documents = self.store_documents(core_files)
        
        # Create templates
        templates = self.create_templates(patterns)
        
        # Store metadata safely
        self.store_metadata(core_files, patterns, len(documents), len(templates))
        
        results = {
            'files_scanned': len(core_files),
            'patterns_extracted': sum(len(v) for v in patterns.values() if isinstance(v, list)),
            'documents_created': len(documents),
            'templates_created': len(templates)
        }
        
        print(f"\n✅ Focused ingestion complete!")
        print(f"   📁 Core files: {results['files_scanned']}")
        print(f"   🎯 Patterns: {results['patterns_extracted']}")
        print(f"   📄 Documents: {results['documents_created']}")
        print(f"   📝 Templates: {results['templates_created']}")
        
        return results
    
    def scan_core_files(self) -> List[Dict[str, Any]]:
        """Scan only core project files"""
        print("🔍 Scanning core project files...")
        
        core_files = []
        
        for focus_dir in self.focus_directories:
            dir_path = self.project_root / focus_dir
            if not dir_path.exists():
                continue
                
            print(f"   Scanning {focus_dir}...")
            
            for file_path in dir_path.rglob('*'):
                if not file_path.is_file():
                    continue
                    
                # Skip if in skip directories
                if any(skip in str(file_path) for skip in self.skip_directories):
                    continue
                    
                # Only process focus extensions
                if file_path.suffix not in self.focus_extensions:
                    continue
                    
                file_info = self.analyze_file(file_path)
                if file_info:
                    core_files.append(file_info)
        
        # Also scan root Python files
        for file_path in self.project_root.glob('*.py'):
            if file_path.is_file():
                file_info = self.analyze_file(file_path)
                if file_info:
                    core_files.append(file_info)
        
        print(f"   Found {len(core_files)} core files")
        return core_files
    
    def analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return None
            
            # Skip very large files
            if len(content) > 50000:  # 50KB limit
                return None
                
            # Clean content to avoid Unicode issues
            content = content.replace('\x00', '').replace('\r', '\n')
            
            relative_path = file_path.relative_to(self.project_root)
            extension = file_path.suffix
            
            language = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript', 
                '.jsx': 'javascript',
                '.tsx': 'typescript'
            }.get(extension, 'text')
            
            return {
                'path': file_path,
                'relative_path': str(relative_path),
                'language': language,
                'extension': extension,
                'content': content,
                'size': len(content),
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            print(f"   Warning: Could not read {file_path}: {e}")
            return None
    
    def extract_patterns(self, files: List[Dict[str, Any]]) -> Dict[str, List]:
        """Extract code patterns safely"""
        print("🎯 Extracting code patterns...")
        
        patterns = {
            'django_models': [],
            'django_views': [],
            'django_urls': [],
            'python_functions': [],
            'python_classes': [],
            'react_components': [],
            'api_endpoints': [],
            'imports': []
        }
        
        for file_info in files:
            if file_info['language'] == 'python':
                file_patterns = self.extract_python_patterns(file_info)
                self.merge_patterns(patterns, file_patterns)
            elif file_info['language'] in ['javascript', 'typescript']:
                file_patterns = self.extract_js_patterns(file_info)
                self.merge_patterns(patterns, file_patterns)
        
        total = sum(len(v) for v in patterns.values() if isinstance(v, list))
        print(f"   Extracted {total} patterns")
        
        return patterns
    
    def extract_python_patterns(self, file_info: Dict[str, Any]) -> Dict[str, List]:
        """Extract Python patterns safely"""
        patterns = {
            'python_classes': [],
            'python_functions': [],
            'django_models': [],
            'django_views': [],
            'api_endpoints': [],
            'imports': []
        }
        
        content = file_info['content']
        file_path = file_info['relative_path']
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)][:5]  # Limit to avoid huge data
                    }
                    
                    patterns['python_classes'].append(class_info)
                    
                    # Detect Django models
                    if any('models.py' in file_path or 'Model' in str(base) for base in node.bases):
                        patterns['django_models'].append(class_info)
                    
                    # Detect Django views
                    if 'views.py' in file_path or any('View' in str(base) for base in node.bases):
                        patterns['django_views'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args][:5]  # Limit args
                    }
                    
                    patterns['python_functions'].append(func_info)
                    
                    # Detect API endpoints
                    if any(dec for dec in node.decorator_list if 'api' in str(dec).lower()):
                        patterns['api_endpoints'].append(func_info)
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return patterns
    
    def extract_js_patterns(self, file_info: Dict[str, Any]) -> Dict[str, List]:
        """Extract JavaScript/TypeScript patterns"""
        patterns = {
            'react_components': [],
            'javascript_functions': []
        }
        
        content = file_info['content']
        file_path = file_info['relative_path']
        
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # React components (simple detection)
            if ('function' in line and ('Component' in line or file_path.endswith(('.jsx', '.tsx')))):
                if 'function' in line and '(' in line:
                    patterns['react_components'].append({
                        'file': file_path,
                        'line': line_num,
                        'content': line[:100]  # Limit content
                    })
            
            # Functions
            elif line.startswith('function ') or line.startswith('const ') and '=>' in line:
                patterns['javascript_functions'].append({
                    'file': file_path,
                    'line': line_num,
                    'content': line[:100]  # Limit content
                })
        
        return patterns
    
    def merge_patterns(self, target: Dict[str, List], source: Dict[str, List]) -> None:
        """Merge patterns safely"""
        for key, values in source.items():
            if key in target:
                target[key].extend(values)
            else:
                target[key] = values[:]
    
    def store_documents(self, files: List[Dict[str, Any]]) -> List[Document]:
        """Store files as documents"""
        print("📄 Storing core files as documents...")
        
        # Get system user
        system_user, _ = User.objects.get_or_create(
            username='code_ingestion',
            defaults={'email': 'code@system.local'}
        )
        
        documents = []
        
        for file_info in files:
            doc_type = {
                'python': DocumentType.PYTHON,
                'javascript': DocumentType.JAVASCRIPT,
                'typescript': DocumentType.TYPESCRIPT
            }.get(file_info['language'], DocumentType.TEXT)
            
            doc = Document.objects.create(
                title=f"Code: {file_info['relative_path']}",
                description=f"{file_info['language']} source file",
                document_type=doc_type,
                raw_content=file_info['content'],
                processed_content=file_info['content'],
                status=ContentStatus.PROCESSED,
                source=ContentSource.IMPORTED,
                language=file_info['language'],
                word_count=len(file_info['content'].split()),
                tags=['code', file_info['language'], 'core_project'],
                category='source_code',
                collection='codebase',
                owner=system_user,
                is_public=False,
                source_system='focused_code_ingestion'
            )
            
            documents.append(doc)
        
        print(f"   Created {len(documents)} documents")
        return documents
    
    def create_templates(self, patterns: Dict[str, List]) -> List[ContentTemplate]:
        """Create code generation templates"""
        print("📝 Creating code templates...")
        
        system_user, _ = User.objects.get_or_create(
            username='code_ingestion',
            defaults={'email': 'code@system.local'}
        )
        
        templates = []
        
        # Django Model Template
        if patterns.get('django_models'):
            template = ContentTemplate.objects.create(
                name='django_model_codebase',
                display_name='Django Model (From Your Codebase)',
                description=f'Generate Django models based on your codebase patterns. Found {len(patterns["django_models"])} existing models.',
                template_type='code',
                system_prompt=f'Generate Django models following the patterns in this codebase. Existing models: {[m["name"] for m in patterns["django_models"][:5]]}',
                user_prompt_template='Create a Django model named {{ model_name }} for {{ purpose }}. Include {{ fields }} fields.',
                variables={'model_name': {'type': 'string'}, 'purpose': {'type': 'string'}, 'fields': {'type': 'string'}},
                output_format='text',
                generation_config={'temperature': 0.3, 'max_tokens': 1000},
                tags=['django', 'model', 'codebase'],
                category='code_generation',
                creator=system_user,
                is_public=True
            )
            templates.append(template)
        
        # Django View Template  
        if patterns.get('django_views'):
            template = ContentTemplate.objects.create(
                name='django_view_codebase',
                display_name='Django View (From Your Codebase)',
                description=f'Generate Django views based on your codebase patterns. Found {len(patterns["django_views"])} existing views.',
                template_type='code',
                system_prompt=f'Generate Django views following the patterns in this codebase. Existing views: {[v["name"] for v in patterns["django_views"][:5]]}',
                user_prompt_template='Create a Django view for {{ view_purpose }} that {{ functionality }}.',
                variables={'view_purpose': {'type': 'string'}, 'functionality': {'type': 'string'}},
                output_format='text',
                generation_config={'temperature': 0.3, 'max_tokens': 1500},
                tags=['django', 'view', 'codebase'],
                category='code_generation',
                creator=system_user,
                is_public=True
            )
            templates.append(template)
        
        # Python Function Template
        if patterns.get('python_functions'):
            template = ContentTemplate.objects.create(
                name='python_function_codebase',
                display_name='Python Function (From Your Codebase)',
                description=f'Generate Python functions based on your codebase style. Found {len(patterns["python_functions"])} existing functions.',
                template_type='code',
                system_prompt=f'Generate Python functions following the coding style in this codebase. Common patterns: {[f["name"] for f in patterns["python_functions"][:10]]}',
                user_prompt_template='Create a Python function {{ function_name }} that {{ purpose }}.',
                variables={'function_name': {'type': 'string'}, 'purpose': {'type': 'string'}},
                output_format='text',
                generation_config={'temperature': 0.3, 'max_tokens': 800},
                tags=['python', 'function', 'codebase'],
                category='code_generation',
                creator=system_user,
                is_public=True
            )
            templates.append(template)
        
        # React Component Template
        if patterns.get('react_components'):
            template = ContentTemplate.objects.create(
                name='react_component_codebase',
                display_name='React Component (From Your Codebase)',
                description=f'Generate React components based on your codebase patterns. Found {len(patterns["react_components"])} existing components.',
                template_type='code',
                system_prompt='Generate React components following the patterns and conventions in this codebase.',
                user_prompt_template='Create a React component {{ component_name }} for {{ purpose }}.',
                variables={'component_name': {'type': 'string'}, 'purpose': {'type': 'string'}},
                output_format='text',
                generation_config={'temperature': 0.3, 'max_tokens': 1200},
                tags=['react', 'component', 'codebase'],
                category='code_generation',
                creator=system_user,
                is_public=True
            )
            templates.append(template)
        
        print(f"   Created {len(templates)} templates")
        return templates
    
    def store_metadata(self, files: List[Dict[str, Any]], patterns: Dict[str, List], 
                      doc_count: int, template_count: int) -> None:
        """Store metadata safely"""
        print("💾 Storing metadata...")
        
        # Create safe summary (avoid complex nested data)
        summary = {
            'timestamp': timezone.now().isoformat(),
            'files_processed': len(files),
            'documents_created': doc_count,
            'templates_created': template_count,
            'languages': list(set(f['language'] for f in files)),
            'pattern_counts': {k: len(v) for k, v in patterns.items()},
            'largest_file': max((f['size'] for f in files), default=0)
        }
        
        # Store as system config
        SystemConfiguration.set_config(
            'focused_code_ingestion',
            summary,
            'Focused codebase ingestion summary',
            'code_generation'
        )
        
        # Record metric
        PlatformMetrics.objects.create(
            metric_name="focused_code_ingestion_completed",
            metric_value=float(len(files)),
            metric_type='counter',
            subsystem='code_generation',
            labels={'files': len(files), 'templates': template_count}
        )
        
        print("   Metadata stored successfully")


if __name__ == "__main__":
    ingestion = FocusedCodeIngestion()
    results = ingestion.run_focused_ingestion()
    
    print("\n" + "=" * 50)
    print("🎉 FOCUSED CODE INGESTION SUCCESS!")
    print("=" * 50)
    print("Your core codebase is now ready for AI code generation!")
    print(f"📁 Core files processed: {results['files_scanned']}")
    print(f"🎯 Code patterns found: {results['patterns_extracted']}")
    print(f"📄 Documents created: {results['documents_created']}")
    print(f"📝 Code templates created: {results['templates_created']}")
    print("\n🚀 The AI can now generate code based on YOUR actual project patterns!")