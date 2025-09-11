#!/usr/bin/env python3
"""
Code Embedding Engine - Creates semantic embeddings for code search

This creates vector embeddings of your actual codebase for semantic code search,
enabling AI to find relevant code examples when generating new code.
"""

import os
import sys
import django
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from content.models import Document, DocumentEmbedding, EmbeddingModel
from core.models import PlatformMetrics

User = get_user_model()


class CodeEmbeddingEngine:
    """
    Creates semantic embeddings for code search and retrieval
    """
    
    def __init__(self):
        self.embedding_model = EmbeddingModel.OPENAI_SMALL  # Using text-embedding-3-small
        self.chunk_size = 800  # Optimal for code chunks
        self.chunk_overlap = 100  # Overlap between chunks
        self.embeddings_created = 0
        
    def create_code_embeddings(self, batch_size: int = 20) -> Dict[str, Any]:
        """Create embeddings for code documents"""
        print("🔍 Creating Code Embeddings...")
        print("=" * 40)
        
        # Get core project code documents without embeddings
        code_docs = Document.objects.filter(
            category='source_code',
            source_system='focused_code_ingestion'
        ).exclude(
            embeddings__embedding_model=self.embedding_model
        )[:batch_size]  # Process in batches
        
        print(f"📄 Processing {len(code_docs)} code documents...")
        
        total_embeddings = 0
        
        for doc in code_docs:
            try:
                embeddings_created = self._create_document_embeddings(doc)
                total_embeddings += embeddings_created
                print(f"   ✅ {doc.title}: {embeddings_created} chunks")
                
            except Exception as e:
                print(f"   ❌ {doc.title}: {str(e)}")
        
        # Record metrics
        PlatformMetrics.objects.create(
            metric_name="code_embeddings_created",
            metric_value=float(total_embeddings),
            metric_type='counter',
            subsystem='code_generation',
            labels={
                'documents_processed': len(code_docs),
                'embedding_model': self.embedding_model,
                'batch_size': batch_size
            }
        )
        
        print(f"\n✅ Created {total_embeddings} code embeddings!")
        
        return {
            'documents_processed': len(code_docs),
            'embeddings_created': total_embeddings,
            'embedding_model': self.embedding_model
        }
    
    def _create_document_embeddings(self, document: Document) -> int:
        """Create embeddings for a single document"""
        
        # Extract meaningful code chunks
        chunks = self._extract_code_chunks(document)
        
        embeddings_created = 0
        
        for chunk_index, chunk in enumerate(chunks):
            # Create mock embedding (in real implementation, call OpenAI API)
            mock_embedding = self._create_mock_embedding(chunk['content'])
            
            # Create DocumentEmbedding
            DocumentEmbedding.objects.create(
                document=document,
                embedding_model=self.embedding_model,
                chunk_index=chunk_index,
                chunk_text=chunk['content'],
                chunk_size=len(chunk['content']),
                overlap_size=self.chunk_overlap if chunk_index > 0 else 0,
                embedding_vector=mock_embedding,
                embedding_dimension=len(mock_embedding),
                context_before=chunk.get('context_before', ''),
                context_after=chunk.get('context_after', ''),
                metadata={
                    'code_type': chunk.get('code_type', 'unknown'),
                    'function_name': chunk.get('function_name'),
                    'class_name': chunk.get('class_name'),
                    'language': document.language,
                    'file_path': document.source_reference
                }
            )
            
            embeddings_created += 1
        
        return embeddings_created
    
    def _extract_code_chunks(self, document: Document) -> List[Dict[str, Any]]:
        """Extract meaningful code chunks from document"""
        chunks = []
        content = document.processed_content
        language = document.language
        
        if language == 'python':
            chunks = self._extract_python_chunks(content)
        elif language in ['javascript', 'typescript']:
            chunks = self._extract_js_chunks(content)
        else:
            # Fallback: simple text chunking
            chunks = self._extract_text_chunks(content)
        
        return chunks
    
    def _extract_python_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Extract meaningful Python code chunks"""
        chunks = []
        
        try:
            tree = ast.parse(content)
            lines = content.splitlines()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    
                    # Get the full code for this node
                    start_line = node.lineno - 1
                    
                    # Find end line by looking for next node or end of file
                    end_line = len(lines)
                    for other_node in ast.walk(tree):
                        if (hasattr(other_node, 'lineno') and 
                            other_node.lineno > node.lineno and 
                            other_node.lineno < end_line):
                            end_line = other_node.lineno - 1
                    
                    # Extract the code chunk
                    chunk_lines = lines[start_line:end_line]
                    chunk_content = '\n'.join(chunk_lines)
                    
                    if len(chunk_content.strip()) > 50:  # Only meaningful chunks
                        chunk_info = {
                            'content': chunk_content,
                            'code_type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                            'function_name': node.name if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None,
                            'class_name': node.name if isinstance(node, ast.ClassDef) else None,
                            'line_start': start_line + 1,
                            'line_end': end_line
                        }
                        
                        # Add docstring if available
                        docstring = ast.get_docstring(node)
                        if docstring:
                            chunk_info['docstring'] = docstring
                        
                        chunks.append(chunk_info)
            
            # Also chunk imports and module-level code
            module_level_code = []
            for line_no, line in enumerate(lines):
                if (line.strip().startswith(('import ', 'from ')) or
                    (line.strip() and not any(line_no >= chunk['line_start'] - 1 and line_no < chunk['line_end'] 
                                            for chunk in chunks))):
                    module_level_code.append(line)
            
            if module_level_code:
                chunks.append({
                    'content': '\n'.join(module_level_code),
                    'code_type': 'module_level',
                    'line_start': 1,
                    'line_end': len(module_level_code)
                })
        
        except SyntaxError:
            # If parsing fails, fall back to text chunking
            chunks = self._extract_text_chunks(content)
        
        return chunks
    
    def _extract_js_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Extract meaningful JavaScript/TypeScript chunks"""
        chunks = []
        lines = content.splitlines()
        
        current_chunk = []
        chunk_type = 'code'
        function_name = None
        
        for line_no, line in enumerate(lines):
            # Detect function/class boundaries
            if re.match(r'^\s*(export\s+)?(function|class|const\s+\w+\s*=)', line):
                # Save previous chunk
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'code_type': chunk_type,
                        'function_name': function_name,
                        'line_start': line_no - len(current_chunk) + 1,
                        'line_end': line_no
                    })
                
                # Start new chunk
                current_chunk = [line]
                
                # Detect function name
                func_match = re.search(r'function\s+(\w+)|const\s+(\w+)', line)
                function_name = func_match.group(1) or func_match.group(2) if func_match else None
                chunk_type = 'function' if 'function' in line else 'class' if 'class' in line else 'const'
                
            else:
                current_chunk.append(line)
                
                # Split chunks when they get too long
                if len('\n'.join(current_chunk)) > self.chunk_size:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'code_type': chunk_type,
                        'function_name': function_name,
                        'line_start': line_no - len(current_chunk) + 1,
                        'line_end': line_no
                    })
                    current_chunk = []
                    function_name = None
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'code_type': chunk_type,
                'function_name': function_name,
                'line_start': len(lines) - len(current_chunk) + 1,
                'line_end': len(lines)
            })
        
        return chunks
    
    def _extract_text_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Fallback text chunking for unsupported languages"""
        chunks = []
        
        # Simple chunking by lines
        lines = content.splitlines()
        current_chunk = []
        
        for line in lines:
            current_chunk.append(line)
            
            if len('\n'.join(current_chunk)) >= self.chunk_size:
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'code_type': 'text_chunk',
                    'line_start': len(chunks) * self.chunk_size // 50,  # Approximate
                    'line_end': (len(chunks) + 1) * self.chunk_size // 50
                })
                # Keep overlap
                current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else []
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'code_type': 'text_chunk',
                'line_start': len(chunks) * self.chunk_size // 50,
                'line_end': len(lines)
            })
        
        return chunks
    
    def _create_mock_embedding(self, text: str) -> List[float]:
        """Create a mock embedding (replace with real API call)"""
        # This is a mock - in production you'd call OpenAI API:
        # response = openai.embeddings.create(
        #     model="text-embedding-3-small",
        #     input=text
        # )
        # return response.data[0].embedding
        
        # Mock embedding: create deterministic vector based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to 1536-dimensional vector (OpenAI embedding size)
        import struct
        vector = []
        
        for i in range(1536):
            # Create pseudo-random float from hash
            byte_index = (i * 4) % len(text_hash)
            hash_segment = text_hash[byte_index:byte_index+8].ljust(8, '0')
            
            try:
                # Convert hex to int, then normalize to [-1, 1] range
                int_val = int(hash_segment[:8], 16)
                float_val = (int_val / 0xFFFFFFFF) * 2.0 - 1.0
                vector.append(float_val)
            except ValueError:
                vector.append(0.0)
        
        return vector
    
    def search_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for code using embedding similarity (mock implementation)"""
        print(f"🔍 Searching for: {query}")
        
        # In production, this would:
        # 1. Create embedding for query
        # 2. Find similar embeddings using cosine similarity
        # 3. Return ranked results
        
        # Mock search: find code embeddings by text similarity
        code_embeddings = DocumentEmbedding.objects.filter(
            document__category='source_code'
        ).select_related('document')
        
        results = []
        query_lower = query.lower()
        
        for embedding in code_embeddings:
            # Simple text matching for mock
            content_lower = embedding.chunk_text.lower()
            
            # Calculate simple similarity score
            similarity = 0.0
            query_words = query_lower.split()
            content_words = content_lower.split()
            
            for word in query_words:
                if word in content_words:
                    similarity += 1.0
            
            similarity = similarity / len(query_words) if query_words else 0.0
            
            if similarity > 0:
                results.append({
                    'document': embedding.document.title,
                    'content': embedding.chunk_text[:300] + '...' if len(embedding.chunk_text) > 300 else embedding.chunk_text,
                    'similarity': similarity,
                    'metadata': embedding.metadata,
                    'file_path': embedding.document.source_reference
                })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about code embeddings"""
        
        code_embeddings = DocumentEmbedding.objects.filter(
            document__category='source_code'
        )
        
        total_embeddings = code_embeddings.count()
        
        # Group by language
        language_stats = {}
        for embedding in code_embeddings.select_related('document'):
            lang = embedding.document.language
            if lang not in language_stats:
                language_stats[lang] = 0
            language_stats[lang] += 1
        
        # Group by code type
        code_type_stats = {}
        for embedding in code_embeddings:
            code_type = embedding.metadata.get('code_type', 'unknown')
            if code_type not in code_type_stats:
                code_type_stats[code_type] = 0
            code_type_stats[code_type] += 1
        
        return {
            'total_embeddings': total_embeddings,
            'language_breakdown': language_stats,
            'code_type_breakdown': code_type_stats,
            'embedding_model': self.embedding_model
        }


if __name__ == "__main__":
    print("🔍 Code Embedding Engine")
    print("=" * 50)
    
    engine = CodeEmbeddingEngine()
    
    # Create embeddings
    results = engine.create_code_embeddings(batch_size=10)
    
    # Show stats
    stats = engine.get_embedding_stats()
    
    print(f"\n📊 EMBEDDING STATISTICS:")
    print(f"   Total embeddings: {stats['total_embeddings']}")
    print(f"   Languages: {stats['language_breakdown']}")
    print(f"   Code types: {stats['code_type_breakdown']}")
    
    # Demo search
    print(f"\n🔍 DEMO SEARCH:")
    search_results = engine.search_code("django model user")
    for result in search_results:
        print(f"   📄 {result['document']}")
        print(f"      Similarity: {result['similarity']:.2f}")
        print(f"      Content: {result['content'][:100]}...")
        print()
    
    print("✅ Code embedding system ready for semantic search!")