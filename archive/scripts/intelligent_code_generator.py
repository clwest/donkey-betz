#!/usr/bin/env python3
"""
Intelligent Code Generator with Context Retrieval
This uses embeddings to find relevant code from your codebase to help generate new code.
"""
import os
import sys
import json
import sqlite3
from typing import List, Dict, Optional, Tuple
import openai
from dataclasses import dataclass
import re
from pathlib import Path

@dataclass
class CodeContext:
    file_path: str
    code_snippet: str
    function_name: str
    similarity_score: float
    description: str

class IntelligentCodeGenerator:
    def __init__(self, embeddings_db: str = "code_embeddings.db"):
        self.embeddings_db = embeddings_db
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b:
            return 0.0
        
        import numpy as np
        np_a = np.array(a)
        np_b = np.array(b)
        
        dot_product = np.dot(np_a, np_b)
        norm_a = np.linalg.norm(np_a)
        norm_b = np.linalg.norm(np_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def find_relevant_code(self, task_description: str, limit: int = 5) -> List[CodeContext]:
        """Find relevant code examples from the codebase"""
        if not os.path.exists(self.embeddings_db):
            print(f"⚠️  No embeddings database found at {self.embeddings_db}")
            return []
        
        query_embedding = self._get_embedding(task_description)
        if not query_embedding:
            return []
        
        contexts = []
        
        try:
            conn = sqlite3.connect(self.embeddings_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT file_path, code_snippet, function_name, embedding, context
                FROM code_embeddings
            """)
            
            for row in cursor.fetchall():
                file_path, code_snippet, function_name, embedding_json, context = row
                
                try:
                    embedding = json.loads(embedding_json)
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    
                    if similarity > 0.3:  # Lower threshold for more examples
                        contexts.append(CodeContext(
                            file_path=file_path,
                            code_snippet=code_snippet,
                            function_name=function_name or "global",
                            similarity_score=similarity,
                            description=context or ""
                        ))
                        
                except (json.JSONDecodeError, TypeError):
                    continue
            
            conn.close()
            
            # Sort by similarity and return top matches
            contexts.sort(key=lambda x: x.similarity_score, reverse=True)
            return contexts[:limit]
            
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
    
    def analyze_codebase_patterns(self, file_type: str = "python") -> Dict[str, List[str]]:
        """Analyze common patterns in the codebase"""
        patterns = {
            'imports': [],
            'class_definitions': [],
            'function_patterns': [],
            'frameworks': []
        }
        
        # Common patterns to look for
        python_patterns = {
            'django_imports': [
                'from django.db import models',
                'from django.contrib.auth import',
                'from rest_framework import',
                'from django.http import'
            ],
            'react_patterns': [
                'import React from',
                'useState',
                'useEffect',
                'export default'
            ],
            'common_frameworks': ['django', 'react', 'fastapi', 'flask', 'express']
        }
        
        if not os.path.exists(self.embeddings_db):
            return patterns
        
        try:
            conn = sqlite3.connect(self.embeddings_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT code_snippet FROM code_embeddings")
            
            for (code_snippet,) in cursor.fetchall():
                # Analyze imports
                import_lines = re.findall(r'^(?:from|import)\s+[\w.]+', code_snippet, re.MULTILINE)
                patterns['imports'].extend(import_lines[:3])  # Limit to first 3
                
                # Analyze class definitions
                class_defs = re.findall(r'^class\s+(\w+)', code_snippet, re.MULTILINE)
                patterns['class_definitions'].extend(class_defs)
                
                # Analyze function definitions
                func_defs = re.findall(r'^(?:\s*)def\s+(\w+)', code_snippet, re.MULTILINE)
                patterns['function_patterns'].extend(func_defs)
                
                # Check for frameworks
                for framework in python_patterns['common_frameworks']:
                    if framework in code_snippet.lower():
                        if framework not in patterns['frameworks']:
                            patterns['frameworks'].append(framework)
            
            conn.close()
            
            # Deduplicate and limit
            for key in patterns:
                patterns[key] = list(set(patterns[key]))[:10]
                
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
        
        return patterns
    
    def generate_code(self, task_description: str, file_type: str = "python", style: str = "professional") -> str:
        """Generate code using relevant context from the codebase"""
        print(f"🤖 Generating {file_type} code for: {task_description}")
        
        # Find relevant code examples
        relevant_contexts = self.find_relevant_code(task_description, limit=3)
        
        # Analyze codebase patterns
        patterns = self.analyze_codebase_patterns(file_type)
        
        # Build context for the AI
        context_prompt = f"""
You are generating {file_type} code for: {task_description}

Based on the existing codebase patterns:

COMMON IMPORTS:
{chr(10).join(patterns['imports'][:5])}

COMMON FRAMEWORKS USED:
{', '.join(patterns['frameworks'])}

"""
        
        if relevant_contexts:
            context_prompt += "RELEVANT CODE EXAMPLES FROM CODEBASE:\n\n"
            for i, ctx in enumerate(relevant_contexts, 1):
                context_prompt += f"Example {i} (similarity: {ctx.similarity_score:.2f}):\n"
                context_prompt += f"From: {ctx.file_path}\n"
                context_prompt += f"Function: {ctx.function_name}\n"
                context_prompt += f"Code:\n```{file_type}\n{ctx.code_snippet[:500]}...\n```\n\n"
        
        # Style guidelines
        style_guidelines = {
            'professional': "Write clean, professional code with proper error handling and documentation.",
            'minimal': "Write minimal, concise code focusing only on core functionality.",
            'comprehensive': "Write comprehensive code with extensive error handling, logging, and documentation.",
            'modern': "Use modern language features and best practices."
        }
        
        prompt = f"""{context_prompt}

TASK: {task_description}

STYLE: {style_guidelines.get(style, style_guidelines['professional'])}

REQUIREMENTS:
1. Follow the patterns and conventions from the examples above
2. Use the same imports and frameworks when appropriate
3. Write idiomatic {file_type} code
4. Include appropriate error handling
5. Add brief comments for complex logic
6. Make the code production-ready

Generate the complete code:
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"You are an expert {file_type} developer. Generate clean, production-ready code that follows the patterns shown in the examples."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=2000
            )
            
            generated_code = response.choices[0].message.content
            
            # Clean up the code (remove markdown if present)
            if f"```{file_type}" in generated_code:
                generated_code = generated_code.split(f"```{file_type}")[1].split("```")[0].strip()
            elif "```" in generated_code:
                generated_code = generated_code.split("```")[1].split("```")[0].strip()
            
            return generated_code
            
        except Exception as e:
            print(f"❌ Error generating code: {e}")
            return f"# Error generating code: {e}"
    
    def save_generated_code(self, code: str, filename: str, overwrite: bool = False) -> bool:
        """Save generated code to a file"""
        if os.path.exists(filename) and not overwrite:
            print(f"⚠️  File {filename} already exists. Use overwrite=True to replace it.")
            return False
        
        try:
            with open(filename, 'w') as f:
                f.write(code)
            print(f"✅ Code saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving code: {e}")
            return False
    
    def interactive_generation(self):
        """Interactive code generation session"""
        print("🤖 Intelligent Code Generator")
        print("=" * 50)
        print("Type 'quit' to exit, 'help' for commands")
        
        while True:
            try:
                task = input("\n📝 Describe what you want to build: ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    break
                elif task.lower() == 'help':
                    print("""
Commands:
  help - Show this help
  quit - Exit the generator
  
Examples:
  - Create a Django model for user profiles
  - Build a React component for displaying data
  - Write a function to process API responses
  - Create an authentication middleware
""")
                    continue
                elif not task:
                    continue
                
                # Ask for file type
                file_type = input("📄 File type (python/javascript/typescript): ").strip().lower() or "python"
                
                # Ask for style
                style = input("🎨 Style (professional/minimal/comprehensive/modern): ").strip().lower() or "professional"
                
                # Generate code
                print("\n🤖 Generating code...")
                generated_code = self.generate_code(task, file_type, style)
                
                print("\n" + "="*50)
                print("GENERATED CODE:")
                print("="*50)
                print(generated_code)
                print("="*50)
                
                # Ask to save
                save = input("\n💾 Save to file? (y/n): ").strip().lower()
                if save in ['y', 'yes']:
                    filename = input("📂 Filename: ").strip()
                    if filename:
                        self.save_generated_code(generated_code, filename)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

def main():
    generator = IntelligentCodeGenerator()
    
    if len(sys.argv) > 1:
        task_description = " ".join(sys.argv[1:])
        code = generator.generate_code(task_description)
        print("\n" + "="*50)
        print("GENERATED CODE:")
        print("="*50)
        print(code)
    else:
        generator.interactive_generation()

if __name__ == "__main__":
    main()