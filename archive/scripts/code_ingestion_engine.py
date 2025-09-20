#!/usr/bin/env python3
"""
Code Ingestion Engine - Scans, parses, and ingests the entire codebase

This system scans your project, extracts code patterns, creates embeddings,
and stores everything so the AI can generate code based on your actual patterns.
"""

import os
import sys
import django
from pathlib import Path
import ast
import tokenize
import io
import hashlib
import json
from typing import Dict, List, Any, Optional, Set
import re
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import SystemConfiguration, PlatformMetrics
from content.models import (
    Document, ContentTemplate, DocumentType, ContentStatus, 
    ContentSource, DocumentEmbedding, EmbeddingModel
)

User = get_user_model()


class CodeIngestionEngine:
    """
    Scans and ingests the entire codebase for AI-powered code generation
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sh': 'shell',
            '.dockerfile': 'dockerfile',
            '.env': 'config'
        }
        
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            '.mypy_cache',
            'venv',
            'env',
            '.env',
            'dist',
            'build',
            '.DS_Store',
            '*.pyc',
            '*.pyo',
            '*.egg-info',
            '.coverage',
            'coverage.xml',
            '.tox',
            '.vscode',
            '.idea'
        }
        
        self.ingested_files = []
        self.code_patterns = {}
        self.embeddings_created = 0
        
    def run_full_ingestion(self, create_embeddings: bool = True) -> Dict[str, Any]:
        """Execute complete codebase ingestion"""
        print("📁 Starting Codebase Ingestion...")
        print("=" * 50)
        
        # Step 1: Scan all source files
        source_files = self.scan_codebase()
        
        # Step 2: Parse and extract code patterns
        patterns = self.extract_code_patterns(source_files)
        
        # Step 3: Store files as documents
        documents = self.store_code_documents(source_files)
        
        # Step 4: Create embeddings for semantic search
        if create_embeddings:
            embeddings = self.create_code_embeddings(documents)
        else:
            embeddings = []
        
        # Step 5: Generate code templates based on patterns
        templates = self.create_code_templates(patterns)
        
        # Step 6: Store ingestion metadata
        self.store_ingestion_metadata(source_files, patterns, documents)
        
        print(f"\n✅ Codebase ingestion complete!")
        print(f"   📁 Files scanned: {len(source_files)}")
        print(f"   🎯 Patterns extracted: {len(patterns)}")
        print(f"   📄 Documents created: {len(documents)}")
        print(f"   🔍 Embeddings created: {len(embeddings)}")
        print(f"   📝 Templates generated: {len(templates)}")
        
        return {
            'files_scanned': len(source_files),
            'patterns_extracted': len(patterns),
            'documents_created': len(documents),
            'embeddings_created': len(embeddings),
            'templates_generated': len(templates),
            'project_root': str(self.project_root)
        }
    
    def scan_codebase(self) -> List[Dict[str, Any]]:
        """Scan the codebase and identify all source files"""
        print("🔍 Scanning codebase for source files...")
        
        source_files = []
        
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
                
            # Skip ignored patterns
            if self._should_ignore_file(file_path):
                continue
                
            # Check if it's a supported file type
            file_extension = file_path.suffix.lower()
            if file_extension in self.supported_extensions:
                file_info = self._analyze_file(file_path)
                if file_info:
                    source_files.append(file_info)
        
        print(f"   Found {len(source_files)} source files")
        return source_files
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored"""
        # Check if any parent directory is in ignore patterns
        for part in file_path.parts:
            if part in self.ignore_patterns:
                return True
        
        # Check if filename matches ignore patterns
        if file_path.name in self.ignore_patterns:
            return True
            
        # Check file size (skip very large files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True
            
        return False
    
    def _analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single source file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return None
                
            file_extension = file_path.suffix.lower()
            language = self.supported_extensions.get(file_extension, 'text')
            
            # Calculate relative path from project root
            try:
                relative_path = file_path.relative_to(self.project_root)
            except ValueError:
                relative_path = file_path
            
            return {
                'path': file_path,
                'relative_path': str(relative_path),
                'language': language,
                'extension': file_extension,
                'content': content,
                'size': len(content),
                'lines': len(content.splitlines()),
                'hash': hashlib.sha256(content.encode()).hexdigest()
            }
            
        except Exception as e:
            print(f"   Warning: Could not read {file_path}: {e}")
            return None
    
    def extract_code_patterns(self, source_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract code patterns and structures"""
        print("🎯 Extracting code patterns...")
        
        patterns = {
            'classes': [],
            'functions': [],
            'imports': [],
            'decorators': [],
            'models': [],
            'views': [],
            'apis': [],
            'templates': [],
            'configs': []
        }
        
        for file_info in source_files:
            language = file_info['language']
            content = file_info['content']
            file_path = file_info['relative_path']
            
            if language == 'python':
                file_patterns = self._extract_python_patterns(content, file_path)
                self._merge_patterns(patterns, file_patterns)
            elif language in ['javascript', 'typescript']:
                file_patterns = self._extract_js_patterns(content, file_path)
                self._merge_patterns(patterns, file_patterns)
            elif language == 'sql':
                file_patterns = self._extract_sql_patterns(content, file_path)
                self._merge_patterns(patterns, file_patterns)
            elif language == 'html':
                file_patterns = self._extract_html_patterns(content, file_path)
                self._merge_patterns(patterns, file_patterns)
        
        # Calculate pattern statistics
        total_patterns = sum(len(v) if isinstance(v, list) else 0 for v in patterns.values())
        print(f"   Extracted {total_patterns} code patterns")
        
        return patterns
    
    def _extract_python_patterns(self, content: str, file_path: str) -> Dict[str, List]:
        """Extract patterns from Python code"""
        patterns = {
            'classes': [],
            'functions': [],
            'imports': [],
            'decorators': [],
            'models': [],
            'views': [],
            'apis': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno,
                        'bases': [ast.unparse(base) for base in node.bases],
                        'docstring': ast.get_docstring(node),
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    }
                    
                    patterns['classes'].append(class_info)
                    
                    # Identify Django models
                    if any('Model' in base for base in class_info['bases']):
                        patterns['models'].append(class_info)
                    
                    # Identify Django views
                    if 'views.py' in file_path or any('View' in base for base in class_info['bases']):
                        patterns['views'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'decorators': [ast.unparse(dec) for dec in node.decorator_list],
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    }
                    
                    patterns['functions'].append(func_info)
                    
                    # Identify API endpoints
                    if any('api' in dec.lower() or 'route' in dec.lower() for dec in func_info['decorators']):
                        patterns['apis'].append(func_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        patterns['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'import'
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        patterns['imports'].append({
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'from_import'
                        })
        
        except SyntaxError as e:
            print(f"   Warning: Could not parse {file_path}: {e}")
        
        return patterns
    
    def _extract_js_patterns(self, content: str, file_path: str) -> Dict[str, List]:
        """Extract patterns from JavaScript/TypeScript code"""
        patterns = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'components': []
        }
        
        # Simple regex-based extraction (could be enhanced with proper JS parser)
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Function declarations
            if re.match(r'^\s*(export\s+)?(async\s+)?function\s+(\w+)', line):
                match = re.search(r'function\s+(\w+)', line)
                if match:
                    patterns['functions'].append({
                        'name': match.group(1),
                        'file': file_path,
                        'line': line_num,
                        'type': 'function',
                        'is_exported': 'export' in line,
                        'is_async': 'async' in line
                    })
            
            # Arrow functions
            elif re.match(r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(', line):
                match = re.search(r'(?:const|let|var)\s+(\w+)', line)
                if match:
                    patterns['functions'].append({
                        'name': match.group(1),
                        'file': file_path,
                        'line': line_num,
                        'type': 'arrow_function',
                        'is_exported': 'export' in line,
                        'is_async': 'async' in line
                    })
            
            # Class declarations
            elif re.match(r'^\s*(export\s+)?class\s+(\w+)', line):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    class_info = {
                        'name': match.group(1),
                        'file': file_path,
                        'line': line_num,
                        'is_exported': 'export' in line
                    }
                    patterns['classes'].append(class_info)
                    
                    # Check if it's a React component
                    if 'Component' in line or file_path.endswith(('.jsx', '.tsx')):
                        patterns['components'].append(class_info)
            
            # Imports
            elif re.match(r'^\s*import\s+', line):
                patterns['imports'].append({
                    'statement': line,
                    'file': file_path,
                    'line': line_num
                })
            
            # Exports
            elif re.match(r'^\s*export\s+', line):
                patterns['exports'].append({
                    'statement': line,
                    'file': file_path,
                    'line': line_num
                })
        
        return patterns
    
    def _extract_sql_patterns(self, content: str, file_path: str) -> Dict[str, List]:
        """Extract patterns from SQL code"""
        patterns = {
            'tables': [],
            'views': [],
            'functions': [],
            'queries': []
        }
        
        # Simple regex-based SQL pattern extraction
        lines = content.splitlines()
        current_statement = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Check for complete statements
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                
                # Table creation
                if re.match(r'CREATE\s+TABLE', statement, re.IGNORECASE):
                    match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
                    if match:
                        patterns['tables'].append({
                            'name': match.group(1),
                            'file': file_path,
                            'line': line_num - len(current_statement) + 1,
                            'statement': statement
                        })
                
                # View creation
                elif re.match(r'CREATE\s+VIEW', statement, re.IGNORECASE):
                    match = re.search(r'CREATE\s+VIEW\s+(\w+)', statement, re.IGNORECASE)
                    if match:
                        patterns['views'].append({
                            'name': match.group(1),
                            'file': file_path,
                            'line': line_num - len(current_statement) + 1,
                            'statement': statement
                        })
                
                # Function creation
                elif re.match(r'CREATE\s+FUNCTION', statement, re.IGNORECASE):
                    match = re.search(r'CREATE\s+FUNCTION\s+(\w+)', statement, re.IGNORECASE)
                    if match:
                        patterns['functions'].append({
                            'name': match.group(1),
                            'file': file_path,
                            'line': line_num - len(current_statement) + 1,
                            'statement': statement
                        })
                
                # General queries
                else:
                    patterns['queries'].append({
                        'type': self._identify_query_type(statement),
                        'file': file_path,
                        'line': line_num - len(current_statement) + 1,
                        'statement': statement[:200] + '...' if len(statement) > 200 else statement
                    })
                
                current_statement = []
        
        return patterns
    
    def _extract_html_patterns(self, content: str, file_path: str) -> Dict[str, List]:
        """Extract patterns from HTML templates"""
        patterns = {
            'templates': [],
            'forms': [],
            'components': []
        }
        
        # Simple regex-based HTML pattern extraction
        patterns['templates'].append({
            'file': file_path,
            'type': 'html_template',
            'has_forms': '<form' in content,
            'has_javascript': '<script' in content,
            'has_css': '<style' in content or 'class=' in content,
            'template_tags': len(re.findall(r'\{%.*?%\}', content)),  # Django template tags
            'variables': len(re.findall(r'\{\{.*?\}\}', content))      # Django variables
        })
        
        return patterns
    
    def _identify_query_type(self, statement: str) -> str:
        """Identify the type of SQL query"""
        statement_upper = statement.upper().strip()
        if statement_upper.startswith('SELECT'):
            return 'SELECT'
        elif statement_upper.startswith('INSERT'):
            return 'INSERT'
        elif statement_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif statement_upper.startswith('DELETE'):
            return 'DELETE'
        elif statement_upper.startswith('CREATE'):
            return 'CREATE'
        elif statement_upper.startswith('ALTER'):
            return 'ALTER'
        elif statement_upper.startswith('DROP'):
            return 'DROP'
        else:
            return 'OTHER'
    
    def _merge_patterns(self, target: Dict[str, List], source: Dict[str, List]) -> None:
        """Merge source patterns into target patterns"""
        for key, values in source.items():
            if key in target:
                target[key].extend(values)
            else:
                target[key] = values[:]
    
    def store_code_documents(self, source_files: List[Dict[str, Any]]) -> List[Document]:
        """Store source files as Documents in the content system"""
        print("📄 Storing code files as documents...")
        
        documents = []
        
        # Get or create a user for system-generated content
        system_user, _ = User.objects.get_or_create(
            username='system_code_ingestion',
            defaults={
                'email': 'system@codeingestion.local',
                'first_name': 'System',
                'last_name': 'Code Ingestion'
            }
        )
        
        for file_info in source_files:
            # Determine document type based on language
            doc_type_mapping = {
                'python': DocumentType.PYTHON,
                'javascript': DocumentType.JAVASCRIPT,
                'typescript': DocumentType.TYPESCRIPT,
                'sql': DocumentType.SQL,
                'html': DocumentType.HTML,
                'markdown': DocumentType.MARKDOWN,
                'json': DocumentType.JSON,
                'yaml': DocumentType.YAML
            }
            
            doc_type = doc_type_mapping.get(file_info['language'], DocumentType.TEXT)
            
            # Create document
            document = Document.objects.create(
                title=f"Code: {file_info['relative_path']}",
                description=f"{file_info['language'].title()} source file from codebase",
                document_type=doc_type,
                raw_content=file_info['content'],
                processed_content=file_info['content'],  # For code, raw and processed are the same
                content_hash=file_info['hash'],
                status=ContentStatus.PROCESSED,
                source=ContentSource.IMPORTED,
                language=file_info['language'],
                word_count=len(file_info['content'].split()),
                extracted_metadata={
                    'file_path': file_info['relative_path'],
                    'file_size': file_info['size'],
                    'lines_of_code': file_info['lines'],
                    'language': file_info['language'],
                    'extension': file_info['extension']
                },
                tags=['code', file_info['language'], 'codebase_ingestion'],
                category='source_code',
                collection='codebase',
                owner=system_user,
                is_public=False,  # Keep code private by default
                source_system='code_ingestion',
                source_reference=file_info['relative_path']
            )
            
            documents.append(document)
        
        print(f"   Created {len(documents)} code documents")
        return documents
    
    def create_code_embeddings(self, documents: List[Document]) -> List[DocumentEmbedding]:
        """Create embeddings for code documents (placeholder)"""
        print("🔍 Creating code embeddings...")
        
        # Note: This is a placeholder for embedding creation
        # In a real implementation, you would:
        # 1. Split code into meaningful chunks (functions, classes, etc.)
        # 2. Use a code-aware embedding model (like CodeBERT)
        # 3. Store the embeddings for semantic search
        
        embeddings = []
        print("   Embedding creation deferred - would require OpenAI API or local model")
        
        return embeddings
    
    def create_code_templates(self, patterns: Dict[str, Any]) -> List[ContentTemplate]:
        """Create code generation templates based on extracted patterns"""
        print("📝 Creating code generation templates...")
        
        templates = []
        
        # Get or create a user for system-generated content
        system_user, _ = User.objects.get_or_create(
            username='system_code_ingestion',
            defaults={
                'email': 'system@codeingestion.local',
                'first_name': 'System',
                'last_name': 'Code Ingestion'
            }
        )
        
        # Django Model Template
        if patterns.get('models'):
            model_template = ContentTemplate.objects.create(
                name='django_model_from_codebase',
                display_name='Django Model (Based on Codebase)',
                description='Generate Django models based on existing codebase patterns',
                template_type='code',
                system_prompt='You are a Django expert. Generate Django models that follow the patterns and conventions found in this codebase.',
                user_prompt_template='Create a Django model for {{ model_name }} with fields {{ fields }}. Follow the patterns used in the existing models: {{ existing_patterns }}',
                variables={
                    'model_name': {'type': 'string', 'required': True},
                    'fields': {'type': 'string', 'required': True},
                    'existing_patterns': {'type': 'string', 'required': False}
                },
                output_format='text',
                llm_provider='openai',
                llm_model='gpt-5-mini',
                generation_config={'temperature': 0.3, 'max_tokens': 1500},
                tags=['django', 'model', 'codebase-generated'],
                category='code_generation',
                creator=system_user,
                is_public=True,
                is_verified=True
            )
            templates.append(model_template)
        
        # Django View Template
        if patterns.get('views'):
            view_template = ContentTemplate.objects.create(
                name='django_view_from_codebase',
                display_name='Django View (Based on Codebase)',
                description='Generate Django views based on existing codebase patterns',
                template_type='code',
                system_prompt='You are a Django expert. Generate Django views that follow the patterns and conventions found in this codebase.',
                user_prompt_template='Create a Django view for {{ view_purpose }} that {{ functionality }}. Follow the patterns used in existing views: {{ existing_patterns }}',
                variables={
                    'view_purpose': {'type': 'string', 'required': True},
                    'functionality': {'type': 'string', 'required': True},
                    'existing_patterns': {'type': 'string', 'required': False}
                },
                output_format='text',
                llm_provider='openai',
                llm_model='gpt-5-mini',
                generation_config={'temperature': 0.3, 'max_tokens': 2000},
                tags=['django', 'view', 'codebase-generated'],
                category='code_generation',
                creator=system_user,
                is_public=True,
                is_verified=True
            )
            templates.append(view_template)
        
        # Python Function Template
        if patterns.get('functions'):
            function_template = ContentTemplate.objects.create(
                name='python_function_from_codebase',
                display_name='Python Function (Based on Codebase)',
                description='Generate Python functions based on existing codebase patterns',
                template_type='code',
                system_prompt='You are a Python expert. Generate Python functions that follow the coding style and patterns found in this codebase.',
                user_prompt_template='Create a Python function {{ function_name }} that {{ purpose }}. Follow the coding style and patterns from the codebase: {{ existing_patterns }}',
                variables={
                    'function_name': {'type': 'string', 'required': True},
                    'purpose': {'type': 'string', 'required': True},
                    'existing_patterns': {'type': 'string', 'required': False}
                },
                output_format='text',
                llm_provider='openai',
                llm_model='gpt-5-mini',
                generation_config={'temperature': 0.3, 'max_tokens': 1000},
                tags=['python', 'function', 'codebase-generated'],
                category='code_generation',
                creator=system_user,
                is_public=True,
                is_verified=True
            )
            templates.append(function_template)
        
        # JavaScript/React Component Template
        if patterns.get('components'):
            component_template = ContentTemplate.objects.create(
                name='react_component_from_codebase',
                display_name='React Component (Based on Codebase)',
                description='Generate React components based on existing codebase patterns',
                template_type='code',
                system_prompt='You are a React expert. Generate React components that follow the patterns and conventions found in this codebase.',
                user_prompt_template='Create a React component {{ component_name }} for {{ purpose }}. Follow the patterns used in existing components: {{ existing_patterns }}',
                variables={
                    'component_name': {'type': 'string', 'required': True},
                    'purpose': {'type': 'string', 'required': True},
                    'existing_patterns': {'type': 'string', 'required': False}
                },
                output_format='text',
                llm_provider='openai',
                llm_model='gpt-5-mini',
                generation_config={'temperature': 0.3, 'max_tokens': 1500},
                tags=['react', 'component', 'codebase-generated'],
                category='code_generation',
                creator=system_user,
                is_public=True,
                is_verified=True
            )
            templates.append(component_template)
        
        print(f"   Created {len(templates)} code generation templates")
        return templates
    
    def store_ingestion_metadata(self, source_files: List[Dict[str, Any]], 
                                patterns: Dict[str, Any], documents: List[Document]) -> None:
        """Store metadata about the ingestion process"""
        print("💾 Storing ingestion metadata...")
        
        # Store ingestion summary as system configuration
        ingestion_summary = {
            'timestamp': timezone.now().isoformat(),
            'project_root': str(self.project_root),
            'files_ingested': len(source_files),
            'documents_created': len(documents),
            'patterns_found': {k: len(v) if isinstance(v, list) else 0 for k, v in patterns.items()},
            'languages_detected': list(set(f['language'] for f in source_files)),
            'file_types': {ext: sum(1 for f in source_files if f['extension'] == ext) 
                         for ext in set(f['extension'] for f in source_files)}
        }
        
        SystemConfiguration.set_config(
            'codebase_ingestion_summary',
            ingestion_summary,
            'Summary of the last codebase ingestion process',
            'code_ingestion'
        )
        
        # Store detailed patterns
        SystemConfiguration.set_config(
            'codebase_patterns',
            patterns,
            'Detailed code patterns extracted from codebase',
            'code_ingestion'
        )
        
        # Record metrics
        PlatformMetrics.objects.create(
            metric_name="codebase_ingestion_completed",
            metric_value=1.0,
            metric_type='counter',
            subsystem='code_generation',
            labels=ingestion_summary
        )
        
        print(f"   Stored ingestion metadata and metrics")
    
    def get_ingestion_status(self) -> Dict[str, Any]:
        """Get the status of codebase ingestion"""
        try:
            config = SystemConfiguration.objects.get(
                key='codebase_ingestion_summary',
                category='code_ingestion'
            )
            return config.value
        except SystemConfiguration.DoesNotExist:
            return {'status': 'not_ingested'}


if __name__ == "__main__":
    print("📁 Code Ingestion Engine")
    print("=" * 50)
    
    # Run ingestion on current project
    engine = CodeIngestionEngine()
    results = engine.run_full_ingestion(create_embeddings=False)  # Skip embeddings for now
    
    print("\n" + "=" * 50)
    print("🎉 CODE INGESTION COMPLETE!")
    print("=" * 50)
    print("Your entire codebase is now available for AI code generation:")
    print(f"📁 Files processed: {results['files_scanned']}")
    print(f"🎯 Code patterns extracted: {results['patterns_extracted']}")
    print(f"📄 Documents created: {results['documents_created']}")
    print(f"📝 Templates generated: {results['templates_generated']}")
    
    print(f"\n🚀 Your AI can now generate code based on your actual project patterns!")
    print(f"The system learned from: {results['project_root']}")