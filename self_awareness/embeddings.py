"""
Codebase Embedding and Semantic Search System for Self-Awareness

This module implements:
- Code embedding generation using AI models
- Vector-based semantic code search
- Architecture analysis and understanding
- Code relationship mapping
"""

import ast
import re
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
# Session 985: sklearn loaded lazily to reduce Celery parent process memory

from content.ai_providers import AIProviderManager
from .models import CodeEmbedding, CodebaseSnapshot


logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a chunk of code for embedding"""
    content: str
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    imports: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.dependencies is None:
            self.dependencies = []


class CodebaseEmbeddingManager:
    """
    Manage embeddings for the entire codebase
    """
    
    def __init__(self):
        self.ai_provider = AIProviderManager()
        self.base_dir = Path(settings.BASE_DIR)
        self.embedding_model = 'text-embedding-3-small'
        self.max_chunk_size = 2000  # characters
        
    def embed_entire_codebase(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Generate embeddings for the entire codebase
        """
        logger.info("Starting complete codebase embedding process...")
        
        start_time = timezone.now()
        stats = {
            'files_processed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'errors': 0,
            'skipped': 0
        }
        
        # Get all relevant code files
        code_files = self._get_code_files()
        logger.info(f"Found {len(code_files)} code files to process")
        
        for file_path in code_files:
            try:
                file_stats = self._process_file(file_path, force_refresh)
                stats['files_processed'] += 1
                stats['chunks_created'] += file_stats['chunks_created']
                stats['embeddings_generated'] += file_stats['embeddings_generated']
                stats['skipped'] += file_stats['skipped']
                
                if stats['files_processed'] % 10 == 0:
                    logger.info(f"Processed {stats['files_processed']}/{len(code_files)} files")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
                
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Codebase embedding completed in {duration:.2f}s: {stats}")
        
        # Update codebase snapshot with embedding info
        self._update_codebase_snapshot(stats)
        
        return {
            'status': 'completed',
            'duration': duration,
            'stats': stats,
            'timestamp': end_time.isoformat()
        }
        
    def _get_code_files(self) -> List[Path]:
        """Get list of code files to process"""
        extensions = {'.py', '.js', '.tsx', '.jsx', '.vue', '.sql'}
        exclude_patterns = {'venv', '.venv', 'node_modules', '__pycache__', '.git', 'migrations', 'dist', 'build', '.tox', 'venv_ml'}

        code_files = []

        for ext in extensions:
            for file_path in self.base_dir.rglob(f'*{ext}'):
                # Skip excluded directories - check each part of the path
                path_parts = file_path.parts
                if any(pattern in path_parts for pattern in exclude_patterns):
                    continue

                # Also check if pattern is in the string path
                if any(f'/{pattern}/' in str(file_path) for pattern in exclude_patterns):
                    continue

                # Skip empty files or very small files
                try:
                    if file_path.stat().st_size < 50:  # Less than 50 bytes
                        continue
                except:
                    continue

                code_files.append(file_path)

        return sorted(code_files)
        
    def _process_file(self, file_path: Path, force_refresh: bool) -> Dict[str, int]:
        """Process a single file and generate embeddings"""
        stats = {'chunks_created': 0, 'embeddings_generated': 0, 'skipped': 0}
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                stats['skipped'] += 1
                return stats
                
            # Calculate file hash for change detection
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            relative_path = str(file_path.relative_to(self.base_dir))
            
            # Check if we already have embeddings for this file version
            if not force_refresh:
                existing = CodeEmbedding.objects.filter(
                    file_path=relative_path,
                    code_hash=file_hash
                ).exists()
                
                if existing:
                    stats['skipped'] += 1
                    return stats
                    
            # Remove old embeddings for this file
            CodeEmbedding.objects.filter(file_path=relative_path).delete()
            
            # Split file into chunks
            chunks = self._split_file_into_chunks(content, file_path)
            stats['chunks_created'] = len(chunks)
            
            # Generate embeddings for each chunk (no atomic transaction to allow partial success)
            for chunk in chunks:
                try:
                    embedding = self._generate_embedding(chunk)
                    if embedding:
                        self._save_embedding(chunk, embedding, file_hash)
                        stats['embeddings_generated'] += 1
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk in {file_path}: {e}")
                    # Continue processing other chunks even if one fails
                    continue
                        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
            
        return stats
        
    def _split_file_into_chunks(self, content: str, file_path: Path) -> List[CodeChunk]:
        """Split file content into meaningful chunks"""
        chunks = []
        
        if file_path.suffix == '.py':
            chunks = self._split_python_file(content, str(file_path))
        elif file_path.suffix in {'.js', '.jsx', '.tsx', '.vue'}:
            chunks = self._split_javascript_file(content, str(file_path))
        else:
            # Generic splitting for other file types
            chunks = self._split_generic_file(content, str(file_path))
            
        return chunks
        
    def _split_python_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """Split Python file into logical chunks"""
        chunks = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Extract module-level imports and docstring
            module_imports = []
            module_docstring = ""
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_imports.append(alias.name)
                    else:
                        module_imports.append(node.module or '')
                        
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                    module_docstring = node.value.s
                    break
                    
            # Create chunk for module-level code
            if module_imports or module_docstring:
                module_chunk = self._extract_module_chunk(lines, module_imports, module_docstring)
                if module_chunk:
                    chunk = CodeChunk(
                        content=module_chunk,
                        file_path=file_path,
                        imports=module_imports
                    )
                    chunks.append(chunk)
                    
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk = self._extract_function_chunk(node, lines, file_path, module_imports)
                    if chunk:
                        chunks.append(chunk)
                        
                elif isinstance(node, ast.ClassDef):
                    chunk = self._extract_class_chunk(node, lines, file_path, module_imports)
                    if chunk:
                        chunks.append(chunk)
                        
        except SyntaxError as e:
            logger.debug(f"Syntax error in {file_path}, using generic splitting: {e}")
            chunks = self._split_generic_file(content, file_path)
            
        return chunks
        
    def _extract_module_chunk(self, lines: List[str], imports: List[str], docstring: str) -> str:
        """Extract module-level information"""
        chunk_lines = []
        
        if docstring:
            chunk_lines.extend(['"""', docstring, '"""', ''])
            
        if imports:
            chunk_lines.append("# Module imports:")
            chunk_lines.extend(f"# - {imp}" for imp in imports[:10])  # Limit to first 10
            chunk_lines.append("")
            
        # Add module-level constants and variables (first 20 lines after imports)
        in_imports = True
        added_lines = 0
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                continue
                
            if stripped.startswith(('import ', 'from ')):
                continue
                
            if stripped.startswith(('def ', 'class ', 'async def ')):
                break
                
            if not in_imports and added_lines < 20:
                chunk_lines.append(line)
                added_lines += 1
                
            if not stripped.startswith(('import ', 'from ')) and in_imports:
                in_imports = False
                
        return '\n'.join(chunk_lines) if chunk_lines else ""
        
    def _extract_function_chunk(self, node: ast.AST, lines: List[str], file_path: str, module_imports: List[str]) -> Optional[CodeChunk]:
        """Extract function definition and context"""
        try:
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
            
            # Get function content
            func_lines = lines[start_line:end_line]
            content = '\n'.join(func_lines)
            
            if len(content) > self.max_chunk_size:
                # Truncate very long functions
                content = content[:self.max_chunk_size] + "\n# ... (truncated)"
                
            # Extract function dependencies
            dependencies = self._extract_function_dependencies(node)
            
            return CodeChunk(
                content=content,
                file_path=file_path,
                function_name=node.name,
                start_line=start_line,
                end_line=end_line,
                imports=module_imports,
                dependencies=dependencies
            )
            
        except Exception as e:
            logger.debug(f"Error extracting function {node.name}: {e}")
            return None
            
    def _extract_class_chunk(self, node: ast.ClassDef, lines: List[str], file_path: str, module_imports: List[str]) -> Optional[CodeChunk]:
        """Extract class definition and key methods"""
        try:
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
            
            # For large classes, extract just the class definition and key methods
            class_content = []
            
            # Add class definition line
            class_line = lines[start_line]
            class_content.append(class_line)
            
            # Add docstring if present
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Str)):
                docstring_lines = lines[start_line + 1:start_line + 5]  # First few lines
                class_content.extend(docstring_lines)
                class_content.append("")
                
            # Add key methods (first 3 methods or __init__, __str__, etc.)
            method_count = 0
            important_methods = {'__init__', '__str__', '__repr__', 'save', 'delete'}
            
            for method_node in node.body:
                if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if method_node.name in important_methods or method_count < 3:
                        method_start = method_node.lineno - 1
                        method_end = method_node.end_lineno if hasattr(method_node, 'end_lineno') else method_start + 5
                        method_lines = lines[method_start:min(method_end, method_start + 10)]  # Limit method size
                        class_content.extend(method_lines)
                        class_content.append("")
                        method_count += 1
                        
            content = '\n'.join(class_content)
            
            if len(content) > self.max_chunk_size:
                content = content[:self.max_chunk_size] + "\n# ... (truncated)"
                
            return CodeChunk(
                content=content,
                file_path=file_path,
                class_name=node.name,
                start_line=start_line,
                end_line=end_line,
                imports=module_imports
            )
            
        except Exception as e:
            logger.debug(f"Error extracting class {node.name}: {e}")
            return None
            
    def _extract_function_dependencies(self, node: ast.AST) -> List[str]:
        """Extract function dependencies and calls"""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        dependencies.append(f"{child.func.value.id}.{child.func.attr}")
                        
        return list(set(dependencies))[:10]  # Limit to 10 unique dependencies
        
    def _split_javascript_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """Split JavaScript/TypeScript file into chunks"""
        chunks = []
        lines = content.split('\n')
        
        # Simple regex-based extraction for JS/TS
        function_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*[^;]+=>|export\s+function\s+\w+)'
        class_pattern = r'(class\s+\w+|export\s+class\s+\w+)'
        
        current_chunk = []
        in_function = False
        brace_count = 0
        
        for i, line in enumerate(lines):
            if re.search(function_pattern, line) or re.search(class_pattern, line):
                # Save previous chunk if exists
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    if len(chunk_content.strip()) > 50:
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=i - len(current_chunk),
                            end_line=i
                        ))
                        
                current_chunk = [line]
                in_function = True
                brace_count = line.count('{') - line.count('}')
                
            elif in_function:
                current_chunk.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count <= 0 and len(current_chunk) > 1:
                    # End of function/class
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=i - len(current_chunk) + 1,
                        end_line=i + 1
                    ))
                    current_chunk = []
                    in_function = False
                    
                elif len(current_chunk) > 50:  # Prevent overly long chunks
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=i - len(current_chunk) + 1,
                        end_line=i + 1
                    ))
                    current_chunk = []
                    in_function = False
                    
        # Handle remaining chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) > 50:
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=len(lines) - len(current_chunk),
                    end_line=len(lines)
                ))
                
        return chunks
        
    def _split_generic_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """Generic file splitting for unknown file types"""
        chunks = []
        lines = content.split('\n')
        
        # Split into chunks of reasonable size
        chunk_size = 50  # lines per chunk
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            if len(chunk_content.strip()) > 50:
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=i,
                    end_line=min(i + chunk_size, len(lines))
                ))
                
        return chunks
        
    def _generate_embedding(self, chunk: CodeChunk) -> Optional[List[float]]:
        """Generate embedding vector for a code chunk"""
        try:
            # Prepare text for embedding
            embedding_text = self._prepare_embedding_text(chunk)
            
            if not embedding_text.strip():
                return None
                
            # Generate embedding using AI provider
            response = self.ai_provider.generate_embeddings(
                texts=[embedding_text],
                model=self.embedding_model
            )
            
            if response and response.get('embeddings'):
                return response['embeddings'][0]
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            
        return None
        
    def _prepare_embedding_text(self, chunk: CodeChunk) -> str:
        """Prepare code chunk text for embedding"""
        parts = []
        
        # Add file context
        file_name = Path(chunk.file_path).name
        parts.append(f"File: {file_name}")
        
        # Add function/class name if available
        if chunk.function_name:
            parts.append(f"Function: {chunk.function_name}")
        elif chunk.class_name:
            parts.append(f"Class: {chunk.class_name}")
            
        # Add imports context
        if chunk.imports:
            import_summary = ", ".join(chunk.imports[:5])  # First 5 imports
            parts.append(f"Imports: {import_summary}")
            
        # Add dependencies
        if chunk.dependencies:
            dep_summary = ", ".join(chunk.dependencies[:5])  # First 5 dependencies
            parts.append(f"Uses: {dep_summary}")
            
        # Add the actual code
        parts.append("Code:")
        parts.append(chunk.content)
        
        return "\n".join(parts)
        
    def _save_embedding(self, chunk: CodeChunk, embedding: List[float], file_hash: str):
        """Save embedding to database"""
        # Calculate chunk statistics
        tokens = len(chunk.content.split())
        complexity_score = self._calculate_chunk_complexity(chunk)
        importance_score = self._calculate_importance_score(chunk)

        # Create unique hash for this specific chunk (not the whole file)
        chunk_hash = hashlib.sha256(chunk.content.encode()).hexdigest()

        # Use update_or_create to handle duplicates gracefully
        CodeEmbedding.objects.update_or_create(
            file_path=chunk.file_path,
            code_hash=chunk_hash,  # Use chunk-specific hash
            defaults={
                'file_type': Path(chunk.file_path).suffix,
                'function_name': chunk.function_name or "",
                'class_name': chunk.class_name or "",
                'code_snippet': chunk.content,
                'embedding_vector': embedding,
                'embedding_model': self.embedding_model,
                'tokens': tokens,
                'complexity_score': complexity_score,
                'importance_score': importance_score,
                'dependencies': chunk.dependencies,
                'imports': chunk.imports
            }
        )
        
    def _calculate_chunk_complexity(self, chunk: CodeChunk) -> float:
        """Calculate complexity score for a code chunk"""
        # Simple heuristics for complexity
        content = chunk.content
        
        complexity = 0
        
        # Count control structures
        complexity += content.count('if ')
        complexity += content.count('for ')
        complexity += content.count('while ')
        complexity += content.count('try:')
        complexity += content.count('except')
        complexity += content.count('elif')
        
        # Normalize by content length
        normalized = complexity / max(1, len(content.split('\n')))
        
        return min(10.0, normalized * 10)
        
    def _calculate_importance_score(self, chunk: CodeChunk) -> float:
        """Calculate importance score for a code chunk"""
        score = 0.5  # Base score
        
        # Higher score for classes and main functions
        if chunk.class_name:
            score += 0.3
        elif chunk.function_name:
            score += 0.2
            
            # Special functions get higher scores
            if chunk.function_name in {'__init__', 'main', 'run', 'execute', 'process'}:
                score += 0.2
                
        # Higher score for files with many imports (likely important modules)
        if len(chunk.imports) > 5:
            score += 0.1
            
        # Higher score for longer, more detailed chunks
        if len(chunk.content) > 500:
            score += 0.1
            
        return min(1.0, score)
        
    def _update_codebase_snapshot(self, stats: Dict[str, int]):
        """Update codebase snapshot with embedding statistics"""
        try:
            latest_snapshot = CodebaseSnapshot.objects.latest('timestamp')
            # Could add embedding-specific fields to the snapshot model
            # For now, just log the completion
            logger.info(f"Embedding stats: {stats}")
        except CodebaseSnapshot.DoesNotExist:
            logger.info("No codebase snapshot found")


class SemanticCodeSearchEngine:
    """
    Semantic search engine for code using embeddings
    """
    
    def __init__(self):
        self.ai_provider = AIProviderManager()
        self.embedding_model = 'text-embedding-3-small'
        
    def search_code(self, query: str, limit: int = 10, min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search for code using semantic similarity
        """
        logger.info(f"Searching code for: '{query}' (limit: {limit})")
        
        # Generate query embedding
        query_embedding = self._generate_query_embedding(query)
        if not query_embedding:
            return []
            
        # Get all code embeddings
        embeddings = CodeEmbedding.objects.all().order_by('-importance_score')
        
        results = []
        
        for embedding_obj in embeddings:
            try:
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, embedding_obj.embedding_vector)
                
                if similarity >= min_similarity:
                    results.append({
                        'id': embedding_obj.id,
                        'file_path': embedding_obj.file_path,
                        'function_name': embedding_obj.function_name,
                        'class_name': embedding_obj.class_name,
                        'code_snippet': embedding_obj.code_snippet[:500],  # Truncate for display
                        'similarity': similarity,
                        'importance_score': embedding_obj.importance_score,
                        'complexity_score': embedding_obj.complexity_score,
                        'dependencies': embedding_obj.dependencies,
                        'imports': embedding_obj.imports,
                        'timestamp': embedding_obj.timestamp.isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Error calculating similarity for embedding {embedding_obj.id}: {e}")
                continue
                
        # Sort by similarity and importance
        results.sort(key=lambda x: (x['similarity'], x['importance_score']), reverse=True)
        
        return results[:limit]
        
    def find_similar_code(self, file_path: str, function_name: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find code similar to a specific function or file
        """
        # Get the reference embedding
        query_filter = {'file_path': file_path}
        if function_name:
            query_filter['function_name'] = function_name
            
        try:
            reference_embedding = CodeEmbedding.objects.filter(**query_filter).first()
            if not reference_embedding:
                return []
                
            # Find similar embeddings
            all_embeddings = CodeEmbedding.objects.exclude(id=reference_embedding.id)
            
            results = []
            
            for embedding_obj in all_embeddings:
                try:
                    similarity = self._calculate_similarity(
                        reference_embedding.embedding_vector,
                        embedding_obj.embedding_vector
                    )
                    
                    if similarity > 0.7:  # High similarity threshold
                        results.append({
                            'file_path': embedding_obj.file_path,
                            'function_name': embedding_obj.function_name,
                            'class_name': embedding_obj.class_name,
                            'similarity': similarity,
                            'code_snippet': embedding_obj.code_snippet[:300]
                        })
                        
                except Exception as e:
                    logger.error(f"Error comparing embeddings: {e}")
                    continue
                    
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar code: {e}")
            return []
            
    def analyze_code_relationships(self) -> Dict[str, Any]:
        """
        Analyze relationships and patterns in the codebase
        """
        logger.info("Analyzing code relationships...")
        
        analysis = {
            'clusters': self._find_code_clusters(),
            'dependencies': self._analyze_dependency_patterns(),
            'complexity_distribution': self._analyze_complexity_distribution(),
            'file_relationships': self._analyze_file_relationships()
        }
        
        return analysis
        
    def _generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for search query"""
        try:
            # Enhance query with code context
            enhanced_query = f"Code search query: {query}\nFind relevant functions, classes, and code patterns."
            
            response = self.ai_provider.generate_embeddings(
                texts=[enhanced_query],
                model=self.embedding_model
            )
            
            if response and response.get('embeddings'):
                return response['embeddings'][0]
                
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            
        return None
        
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(vec1, vec2)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
            
    def _find_code_clusters(self) -> List[Dict[str, Any]]:
        """Find clusters of similar code"""
        # This would use clustering algorithms like K-means on embeddings
        # For now, return placeholder data
        return [
            {
                'cluster_id': 1,
                'theme': 'Database Models',
                'files': ['models.py', 'migrations'],
                'similarity_avg': 0.85
            },
            {
                'cluster_id': 2,
                'theme': 'API Views',
                'files': ['views.py', 'serializers.py'],
                'similarity_avg': 0.78
            }
        ]
        
    def _analyze_dependency_patterns(self) -> Dict[str, Any]:
        """Analyze dependency patterns across the codebase"""
        # Analyze import patterns and function calls
        all_embeddings = CodeEmbedding.objects.all()
        
        import_counts = {}
        dependency_counts = {}
        
        for embedding in all_embeddings:
            for imp in embedding.imports:
                import_counts[imp] = import_counts.get(imp, 0) + 1
                
            for dep in embedding.dependencies:
                dependency_counts[dep] = dependency_counts.get(dep, 0) + 1
                
        return {
            'most_imported': sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_used_functions': sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'total_unique_imports': len(import_counts),
            'total_unique_dependencies': len(dependency_counts)
        }
        
    def _analyze_complexity_distribution(self) -> Dict[str, Any]:
        """Analyze complexity distribution across the codebase"""
        embeddings = CodeEmbedding.objects.all()
        
        complexities = [e.complexity_score for e in embeddings if e.complexity_score > 0]
        
        if not complexities:
            return {'error': 'No complexity data available'}
            
        return {
            'average': sum(complexities) / len(complexities),
            'min': min(complexities),
            'max': max(complexities),
            'high_complexity_count': len([c for c in complexities if c > 7.0]),
            'total_functions': len(complexities)
        }
        
    def _analyze_file_relationships(self) -> List[Dict[str, Any]]:
        """Analyze relationships between files"""
        # Group embeddings by file
        file_groups = {}
        
        for embedding in CodeEmbedding.objects.all():
            if embedding.file_path not in file_groups:
                file_groups[embedding.file_path] = []
            file_groups[embedding.file_path].append(embedding)
            
        relationships = []
        
        # Find files with similar import patterns
        for file1, embeddings1 in file_groups.items():
            imports1 = set()
            for e in embeddings1:
                imports1.update(e.imports)
                
            for file2, embeddings2 in file_groups.items():
                if file1 >= file2:  # Avoid duplicates
                    continue
                    
                imports2 = set()
                for e in embeddings2:
                    imports2.update(e.imports)
                    
                if imports1 and imports2:
                    overlap = len(imports1.intersection(imports2))
                    total = len(imports1.union(imports2))
                    
                    if overlap > 0 and total > 0:
                        similarity = overlap / total
                        
                        if similarity > 0.3:  # Significant overlap
                            relationships.append({
                                'file1': file1,
                                'file2': file2,
                                'similarity': similarity,
                                'shared_imports': list(imports1.intersection(imports2))[:5]
                            })
                            
        return sorted(relationships, key=lambda x: x['similarity'], reverse=True)[:20]


class ArchitectureAnalyzer:
    """
    Analyze system architecture using code embeddings
    """
    
    def __init__(self):
        self.search_engine = SemanticCodeSearchEngine()
        
    def analyze_system_architecture(self) -> Dict[str, Any]:
        """
        Comprehensive architecture analysis
        """
        logger.info("Analyzing system architecture...")
        
        return {
            'overview': self._get_architecture_overview(),
            'patterns': self._identify_design_patterns(),
            'layers': self._analyze_architectural_layers(),
            'dependencies': self._map_dependencies(),
            'quality_metrics': self._calculate_quality_metrics(),
            'recommendations': self._generate_architecture_recommendations()
        }
        
    def _get_architecture_overview(self) -> Dict[str, Any]:
        """Get high-level architecture overview"""
        embeddings = CodeEmbedding.objects.all()
        
        file_types = {}
        for embedding in embeddings:
            ext = Path(embedding.file_path).suffix
            file_types[ext] = file_types.get(ext, 0) + 1
            
        apps = set()
        for embedding in embeddings:
            parts = embedding.file_path.split('/')
            if len(parts) > 0:
                apps.add(parts[0])
                
        return {
            'total_files': len(set(e.file_path for e in embeddings)),
            'total_functions': len([e for e in embeddings if e.function_name]),
            'total_classes': len([e for e in embeddings if e.class_name]),
            'file_types': file_types,
            'apps': list(apps),
            'avg_complexity': sum(e.complexity_score for e in embeddings) / max(1, len(embeddings))
        }
        
    def _identify_design_patterns(self) -> List[Dict[str, Any]]:
        """Identify design patterns in the codebase"""
        patterns = []
        
        # Look for Django patterns
        model_files = self.search_engine.search_code("class Model Django database", limit=20, min_similarity=0.6)
        if model_files:
            patterns.append({
                'pattern': 'Django Model Pattern',
                'description': 'Django ORM models for database interaction',
                'files': [f['file_path'] for f in model_files[:5]],
                'confidence': 0.9
            })
            
        view_files = self.search_engine.search_code("def APIView Django REST", limit=20, min_similarity=0.6)
        if view_files:
            patterns.append({
                'pattern': 'Django REST API Pattern',
                'description': 'REST API views using Django REST Framework',
                'files': [f['file_path'] for f in view_files[:5]],
                'confidence': 0.85
            })
            
        agent_files = self.search_engine.search_code("class Agent execute run task", limit=10, min_similarity=0.6)
        if agent_files:
            patterns.append({
                'pattern': 'Agent Pattern',
                'description': 'Agent-based architecture for task execution',
                'files': [f['file_path'] for f in agent_files[:5]],
                'confidence': 0.8
            })
            
        return patterns
        
    def _analyze_architectural_layers(self) -> Dict[str, Any]:
        """Analyze architectural layers"""
        return {
            'presentation': {
                'description': 'Views, templates, and API endpoints',
                'files': ['views.py', 'urls.py', 'serializers.py'],
                'complexity': 'medium'
            },
            'business_logic': {
                'description': 'Models, agents, and core logic',
                'files': ['models.py', 'agents/', 'core/'],
                'complexity': 'high'
            },
            'data_access': {
                'description': 'Database models and data management',
                'files': ['models.py', 'migrations/'],
                'complexity': 'medium'
            },
            'integration': {
                'description': 'External API integrations',
                'files': ['ai_providers.py', 'external_apis/'],
                'complexity': 'high'
            }
        }
        
    def _map_dependencies(self) -> Dict[str, Any]:
        """Map system dependencies"""
        relationships = self.search_engine.analyze_code_relationships()
        
        return {
            'internal_dependencies': relationships.get('dependencies', {}),
            'external_dependencies': relationships.get('most_imported', []),
            'circular_dependencies': [],  # Would need dependency graph analysis
            'dependency_depth': 3  # Average depth estimate
        }
        
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate architecture quality metrics"""
        embeddings = CodeEmbedding.objects.all()
        
        if not embeddings:
            return {'error': 'No embeddings available'}
            
        total_complexity = sum(e.complexity_score for e in embeddings)
        avg_complexity = total_complexity / len(embeddings)
        
        high_complexity_ratio = len([e for e in embeddings if e.complexity_score > 7.0]) / len(embeddings)
        
        # Calculate cohesion and coupling estimates
        file_groups = {}
        for e in embeddings:
            if e.file_path not in file_groups:
                file_groups[e.file_path] = []
            file_groups[e.file_path].append(e)
            
        cohesion_scores = []
        for file_path, file_embeddings in file_groups.items():
            if len(file_embeddings) > 1:
                # Estimate cohesion by similarity of functions in same file
                similarities = []
                for i in range(len(file_embeddings)):
                    for j in range(i + 1, len(file_embeddings)):
                        try:
                            sim = self.search_engine._calculate_similarity(
                                file_embeddings[i].embedding_vector,
                                file_embeddings[j].embedding_vector
                            )
                            similarities.append(sim)
                        except:
                            continue
                            
                if similarities:
                    cohesion_scores.append(sum(similarities) / len(similarities))
                    
        avg_cohesion = sum(cohesion_scores) / max(1, len(cohesion_scores))
        
        return {
            'complexity_score': avg_complexity,
            'complexity_distribution': 1.0 - high_complexity_ratio,
            'cohesion': avg_cohesion,
            'coupling': 0.6,  # Estimate - would need detailed analysis
            'maintainability': (1.0 - high_complexity_ratio + avg_cohesion) / 2,
            'overall_quality': (1.0 - high_complexity_ratio + avg_cohesion + 0.4) / 3  # 0.4 is coupling estimate
        }
        
    def _generate_architecture_recommendations(self) -> List[Dict[str, Any]]:
        """Generate architecture improvement recommendations"""
        metrics = self._calculate_quality_metrics()
        recommendations = []
        
        if metrics.get('complexity_score', 0) > 6.0:
            recommendations.append({
                'category': 'complexity',
                'priority': 'high',
                'title': 'Reduce Code Complexity',
                'description': 'Several functions have high cyclomatic complexity and should be refactored',
                'impact': 'Improved maintainability and reduced bugs'
            })
            
        if metrics.get('cohesion', 0) < 0.6:
            recommendations.append({
                'category': 'cohesion',
                'priority': 'medium',
                'title': 'Improve Module Cohesion',
                'description': 'Some modules contain unrelated functionality and should be reorganized',
                'impact': 'Better code organization and understanding'
            })
            
        if metrics.get('coupling', 0) > 0.7:
            recommendations.append({
                'category': 'coupling',
                'priority': 'medium',
                'title': 'Reduce Coupling',
                'description': 'High coupling between modules makes the system brittle',
                'impact': 'Increased flexibility and testability'
            })
            
        return recommendations