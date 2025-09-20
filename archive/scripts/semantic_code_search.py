#!/usr/bin/env python3
"""
Semantic Code Search - AI-powered code search using embeddings
This enables finding relevant code examples from your codebase when generating new code.
"""
import os
import sys
import sqlite3
import numpy as np
from typing import List, Dict, Tuple, Optional
import openai
from dataclasses import dataclass
import json
import re

@dataclass
class CodeMatch:
    file_path: str
    function_name: str
    code_snippet: str
    similarity_score: float
    context: str
    line_start: int
    line_end: int

class SemanticCodeSearch:
    def __init__(self, db_path: str = "code_embeddings.db"):
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the embeddings database exists"""
        if not os.path.exists(self.db_path):
            print(f"❌ Embeddings database not found at {self.db_path}")
            print("Run code_embedding_engine.py first to create embeddings")
            sys.exit(1)
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for search query"""
        try:
            response = self.client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error getting query embedding: {e}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b:
            return 0.0
        
        np_a = np.array(a)
        np_b = np.array(b)
        
        dot_product = np.dot(np_a, np_b)
        norm_a = np.linalg.norm(np_a)
        norm_b = np.linalg.norm(np_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def search(self, query: str, limit: int = 10, min_similarity: float = 0.7) -> List[CodeMatch]:
        """Search for relevant code using semantic similarity"""
        print(f"🔍 Searching for: '{query}'")
        
        # Get query embedding
        query_embedding = self._get_query_embedding(query)
        if not query_embedding:
            return []
        
        matches = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all embeddings from database
            cursor.execute("""
                SELECT file_path, function_name, code_snippet, embedding, 
                       context, line_start, line_end
                FROM code_embeddings
            """)
            
            for row in cursor.fetchall():
                file_path, function_name, code_snippet, embedding_json, context, line_start, line_end = row
                
                try:
                    # Parse embedding from JSON
                    embedding = json.loads(embedding_json)
                    
                    # Calculate similarity
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    
                    if similarity >= min_similarity:
                        matches.append(CodeMatch(
                            file_path=file_path,
                            function_name=function_name or "global",
                            code_snippet=code_snippet,
                            similarity_score=similarity,
                            context=context or "",
                            line_start=line_start or 0,
                            line_end=line_end or 0
                        ))
                        
                except (json.JSONDecodeError, TypeError) as e:
                    continue
            
            conn.close()
            
            # Sort by similarity and limit results
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            return matches[:limit]
            
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
    
    def search_by_technology(self, tech: str, limit: int = 5) -> List[CodeMatch]:
        """Search for examples of specific technology usage"""
        queries = {
            'react': "React component JSX hooks useState useEffect",
            'django': "Django models views serializers API endpoints",
            'api': "REST API endpoints HTTP requests responses",
            'database': "database queries models ORM SQL",
            'authentication': "authentication login JWT tokens",
            'websocket': "WebSocket real-time connections",
            'testing': "unit tests pytest testing fixtures",
            'forms': "form validation input handling",
            'async': "async await asynchronous functions",
            'typescript': "TypeScript interfaces types definitions"
        }
        
        query = queries.get(tech.lower(), tech)
        return self.search(query, limit=limit)
    
    def find_similar_functions(self, function_description: str, limit: int = 5) -> List[CodeMatch]:
        """Find functions similar to the described functionality"""
        return self.search(f"function that {function_description}", limit=limit)
    
    def get_implementation_examples(self, feature: str, limit: int = 3) -> List[CodeMatch]:
        """Get examples of how a feature is implemented"""
        return self.search(f"implementation of {feature}", limit=limit)
    
    def print_matches(self, matches: List[CodeMatch]):
        """Pretty print search matches"""
        if not matches:
            print("❌ No matches found")
            return
        
        print(f"\n✅ Found {len(matches)} matches:\n")
        
        for i, match in enumerate(matches, 1):
            print(f"🔍 Match {i}: {match.function_name} (similarity: {match.similarity_score:.3f})")
            print(f"📁 {match.file_path}:{match.line_start}-{match.line_end}")
            
            if match.context:
                print(f"📝 Context: {match.context}")
            
            # Show code snippet (truncated if too long)
            snippet = match.code_snippet.strip()
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."
            
            print(f"💻 Code:\n```\n{snippet}\n```\n")
            print("-" * 60)

def main():
    search_engine = SemanticCodeSearch()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        matches = search_engine.search(query)
        search_engine.print_matches(matches)
    else:
        print("🔍 Semantic Code Search")
        print("=" * 50)
        print("Usage examples:")
        print("  python semantic_code_search.py 'React component with hooks'")
        print("  python semantic_code_search.py 'Django API endpoint'")
        print("  python semantic_code_search.py 'authentication middleware'")
        print("\nInteractive mode:")
        
        while True:
            try:
                query = input("\n🔍 Search query (or 'quit'): ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                matches = search_engine.search(query)
                search_engine.print_matches(matches)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()