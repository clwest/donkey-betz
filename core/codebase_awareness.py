"""
Codebase Self-Awareness System
Allows the AI to understand, learn from, and modify its own code
"""

import ast
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from django.conf import settings
from core.rag_integration import create_embedding
import json

logger = logging.getLogger(__name__)


class CodebaseAwareness:
    """System for understanding and learning from the codebase"""
    
    def __init__(self):
        self.project_root = Path(settings.BASE_DIR).parent
        self.db_config = {
            'host': 'localhost',
            'database': 'ai_unified_platform',
            'user': 'ai_unified_user',
            'password': '[REDACTED - HISTORICAL SECRET]'
        }
        # Track which files we've already ingested
        self.ingested_files = set()
        self.load_ingested_files()
    
    def load_ingested_files(self):
        """Load list of already ingested files from database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT metadata->>'file_path' 
                FROM unified_embeddings 
                WHERE content_type = 'source_code'
                AND metadata->>'file_path' IS NOT NULL
            """)
            
            for row in cursor.fetchall():
                if row[0]:
                    self.ingested_files.add(row[0])
            
            cursor.close()
            conn.close()
            logger.info(f"Loaded {len(self.ingested_files)} previously ingested files")
            
        except Exception as e:
            logger.error(f"Error loading ingested files: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file contents for change detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()
        except Exception as _e:
            logger.warning(
                "codebase_awareness.get_file_hash: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return ""
    
    def ingest_codebase(self, force_update: bool = False) -> Dict[str, int]:
        """
        Ingest all Python files in the codebase into embeddings
        
        Args:
            force_update: If True, re-ingest all files even if already processed
        
        Returns:
            Statistics about ingestion
        """
        stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'files_updated': 0,
            'embeddings_created': 0,
            'errors': 0
        }
        
        # Python files to process
        python_files = list(self.project_root.rglob("*.py"))
        
        logger.info(f"Found {len(python_files)} Python files to process")
        
        for file_path in python_files:
            # Skip migrations and cache
            if any(skip in str(file_path) for skip in ['/migrations/', '__pycache__', '.pyc']):
                stats['files_skipped'] += 1
                continue
            
            try:
                # Check if file needs processing
                file_str = str(file_path)
                file_hash = self.get_file_hash(file_str)
                
                if not force_update and file_str in self.ingested_files:
                    # Check if file has changed
                    conn = psycopg2.connect(**self.db_config)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT metadata->>'file_hash'
                        FROM unified_embeddings
                        WHERE content_type = 'source_code'
                        AND metadata->>'file_path' = %s
                        LIMIT 1
                    """, (file_str,))
                    
                    result = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if result and result[0] == file_hash:
                        stats['files_skipped'] += 1
                        continue
                    else:
                        stats['files_updated'] += 1
                        logger.info(f"File changed, updating: {file_str}")
                
                # Process the file
                embeddings_created = self.ingest_file(file_path, file_hash)
                stats['embeddings_created'] += embeddings_created
                stats['files_processed'] += 1
                
                if stats['files_processed'] % 10 == 0:
                    logger.info(f"Progress: {stats['files_processed']} files processed")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
        
        logger.info(f"Codebase ingestion complete: {stats}")
        return stats
    
    def ingest_file(self, file_path: Path, file_hash: str) -> int:
        """
        Ingest a single Python file into embeddings
        
        Returns:
            Number of embeddings created
        """
        embeddings_created = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the Python file
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Could not parse {file_path}, storing as text")
                tree = None
            
            # Extract components
            components = []
            
            if tree:
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_content = self.extract_node_content(content, node)
                        components.append({
                            'type': 'class',
                            'name': node.name,
                            'content': class_content,
                            'docstring': ast.get_docstring(node) or ""
                        })
                    
                    elif isinstance(node, ast.FunctionDef):
                        # Only top-level functions
                        if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                                  if hasattr(parent, 'body') and node in parent.body):
                            func_content = self.extract_node_content(content, node)
                            components.append({
                                'type': 'function',
                                'name': node.name,
                                'content': func_content,
                                'docstring': ast.get_docstring(node) or ""
                            })
            
            # If no components found or parsing failed, store the whole file
            if not components:
                components.append({
                    'type': 'file',
                    'name': file_path.name,
                    'content': content[:5000],  # Limit size
                    'docstring': ""
                })
            
            # Create embeddings for each component
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # First, delete old embeddings for this file
            cursor.execute("""
                DELETE FROM unified_embeddings
                WHERE content_type = 'source_code'
                AND metadata->>'file_path' = %s
            """, (str(file_path),))
            
            for component in components:
                # Create searchable text
                search_text = f"{component['type']}: {component['name']}\n"
                search_text += f"File: {file_path.name}\n"
                if component['docstring']:
                    search_text += f"Description: {component['docstring']}\n"
                search_text += f"\n{component['content'][:1000]}"
                
                # Create embedding
                embedding = create_embedding(search_text)
                
                if embedding:
                    # Store in database
                    metadata = {
                        'file_path': str(file_path),
                        'file_hash': file_hash,
                        'component_type': component['type'],
                        'component_name': component['name'],
                        'relative_path': str(file_path.relative_to(self.project_root)),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    cursor.execute("""
                        INSERT INTO unified_embeddings (
                            source_database, source_table, source_id,
                            content_type, content_text, embedding,
                            embedding_model, metadata, importance_score,
                            created_at
                        ) VALUES (
                            'unified_donkey_betz', 'codebase', %s,
                            'source_code', %s, %s,
                            'text-embedding-3-small', %s, %s,
                            NOW()
                        )
                    """, (
                        f"{file_path.name}_{component['name']}",
                        search_text,
                        embedding,
                        json.dumps(metadata),
                        0.8  # High importance for code
                    ))
                    
                    embeddings_created += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Mark file as ingested
            self.ingested_files.add(str(file_path))
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
        
        return embeddings_created
    
    def extract_node_content(self, source: str, node: ast.AST) -> str:
        """Extract source code for an AST node"""
        lines = source.split('\n')
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start = node.lineno - 1
            end = node.end_lineno
            return '\n'.join(lines[start:end])
        return ""
    
    def search_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for code components using semantic search
        
        Args:
            query: Search query
            limit: Maximum results to return
        
        Returns:
            List of matching code components
        """
        from core.rag_integration import search_embeddings
        
        results = search_embeddings(
            query=query,
            limit=limit,
            content_types=['source_code'],
            similarity_threshold=0.5
        )
        
        # Enhance results with file info
        enhanced_results = []
        for result in results:
            metadata = result.get('metadata', {})
            enhanced_results.append({
                'file': metadata.get('relative_path', 'unknown'),
                'component': metadata.get('component_name', 'unknown'),
                'type': metadata.get('component_type', 'unknown'),
                'content': result['content'],
                'similarity': result['similarity_score']
            })
        
        return enhanced_results
    
    def get_implementation(self, component_name: str) -> Optional[str]:
        """
        Get the full implementation of a specific component
        
        Args:
            component_name: Name of class or function
        
        Returns:
            Full source code or None if not found
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content_text, metadata
                FROM unified_embeddings
                WHERE content_type = 'source_code'
                AND metadata->>'component_name' = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (component_name,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return result[0]
            
        except Exception as e:
            logger.error(f"Error getting implementation: {e}")
        
        return None
    
    def explain_system(self, component_or_file: str) -> str:
        """
        Explain how a component or file works
        
        Args:
            component_or_file: Name of component or file path
        
        Returns:
            Explanation of the component
        """
        # Search for the component
        results = self.search_code(component_or_file, limit=1)
        
        if not results:
            return f"No information found about {component_or_file}"
        
        result = results[0]
        
        explanation = f"## {result['component']} ({result['type']})\n\n"
        explanation += f"**File:** {result['file']}\n\n"
        explanation += f"**Implementation:**\n```python\n{result['content'][:1000]}\n```\n\n"
        explanation += f"This component is part of the unified-donkey-betz system."
        
        return explanation


# Singleton instance
codebase_awareness = CodebaseAwareness()