"""
Real-time conversation memory and learning system
Saves all conversations to build knowledge over time
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
import psycopg2
from django.contrib.auth import get_user_model
from core.rag_integration import create_embedding

logger = logging.getLogger(__name__)
User = get_user_model()


class ConversationMemory:
    """Persistent conversation memory that learns from every interaction"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'unified_donkey_betz',
            'user': 'postgres',
            'password': ''
        }
    
    def save_conversation(self, user_id, user_message: str, 
                         assistant_response: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save a conversation to persistent memory for learning
        
        Args:
            user_id: User ID
            user_message: User's message
            assistant_response: Assistant's response
            metadata: Additional context (timestamp, session_id, etc)
        
        Returns:
            True if saved successfully
        """
        logger.info(f"=== save_conversation called ===")
        logger.info(f"User ID: {user_id}")
        logger.info(f"User message: {user_message[:50]}...")
        logger.info(f"Assistant response: {assistant_response[:50]}...")
        
        # CRITICAL: Don't save conversations that contain known hallucinations
        hallucination_indicators = [
            'dashboard_page.dart',
            'main_navigation_page.dart', 
            'FITNESS DASHBOARD',
            'Flutter',
            'weight tracking',
            'Walking, Herd, Profile'
        ]
        
        for indicator in hallucination_indicators:
            if indicator in assistant_response:
                logger.warning(f"Detected potential hallucination ('{indicator}'), not saving conversation")
                return False
        
        try:
            # Create embedding for the conversation
            conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"
            logger.info(f"Creating embedding for text of length: {len(conversation_text)}")
            embedding = create_embedding(conversation_text)
            
            if not embedding:
                logger.warning("Could not create embedding for conversation")
                embedding = None
            else:
                logger.info(f"Embedding created successfully, length: {len(embedding)}")
            
            # Connect to ai_unified_platform database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insert into unified_embeddings table
            insert_sql = """
                INSERT INTO unified_embeddings (
                    source_database, source_table, source_id, 
                    content_type, content_text, embedding,
                    embedding_model, metadata, importance_score,
                    created_at
                ) VALUES (
                    'unified_donkey_betz', 'conversations', %s,
                    'conversation', %s, %s,
                    'text-embedding-3-small', %s, %s,
                    NOW()
                )
            """
            
            # Prepare metadata
            meta = metadata or {}
            meta.update({
                'user_id': str(user_id),  # Ensure user_id is string for JSON
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'assistant_response': assistant_response,
                'learned': True  # Mark as new learning
            })
            
            # Calculate importance based on response length and content
            importance = min(1.0, len(assistant_response) / 1000)
            
            # Generate unique ID
            import uuid
            conversation_id = str(uuid.uuid4())
            
            logger.info(f"Executing SQL insert for conversation_id: {conversation_id}")
            cursor.execute(insert_sql, (
                conversation_id,
                conversation_text,
                embedding,
                json.dumps(meta),
                importance
            ))
            
            logger.info(f"SQL executed, committing transaction...")
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Successfully saved conversation to memory: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False
    
    def get_conversation_history(self, user_id: int, limit: int = 10) -> list:
        """
        Get recent conversation history for a user
        
        Args:
            user_id: User ID
            limit: Number of conversations to retrieve
        
        Returns:
            List of conversation records
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            query = """
                SELECT content_text, metadata, created_at
                FROM unified_embeddings
                WHERE content_type = 'conversation'
                AND metadata->>'user_id' = %s
                AND metadata->>'learned' = 'true'
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (str(user_id), limit))
            results = cursor.fetchall()
            
            conversations = []
            for content, metadata, created_at in results:
                meta = json.loads(metadata) if isinstance(metadata, str) else metadata
                conversations.append({
                    'content': content,
                    'user_message': meta.get('user_message', ''),
                    'assistant_response': meta.get('assistant_response', ''),
                    'timestamp': created_at.isoformat() if created_at else None
                })
            
            cursor.close()
            conn.close()
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def update_knowledge_metrics(self, user_id: int) -> Dict[str, int]:
        """
        Update and return knowledge metrics for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with knowledge metrics
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Count total conversations
            cursor.execute("""
                SELECT COUNT(*) 
                FROM unified_embeddings 
                WHERE content_type = 'conversation'
                AND metadata->>'user_id' = %s
            """, (str(user_id),))
            total_conversations = cursor.fetchone()[0]
            
            # Count today's conversations
            cursor.execute("""
                SELECT COUNT(*) 
                FROM unified_embeddings 
                WHERE content_type = 'conversation'
                AND metadata->>'user_id' = %s
                AND created_at >= CURRENT_DATE
            """, (str(user_id),))
            today_conversations = cursor.fetchone()[0]
            
            # Count total embeddings
            cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
            total_embeddings = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'today_conversations': today_conversations,
                'total_knowledge_base': total_embeddings,
                'learning_rate': today_conversations  # New learnings today
            }
            
        except Exception as e:
            logger.error(f"Failed to update knowledge metrics: {e}")
            return {
                'total_conversations': 0,
                'today_conversations': 0,
                'total_knowledge_base': 0,
                'learning_rate': 0
            }


# Singleton instance
conversation_memory = ConversationMemory()