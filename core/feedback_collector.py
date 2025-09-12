"""
Feedback collection and learning system for agent responses
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Collects and processes user feedback on agent responses
    """
    
    def __init__(self):
        self.feedback_weights = {
            'positive': 1.0,
            'negative': -1.0,
            'neutral': 0.0,
            'helpful': 0.8,
            'not_helpful': -0.8,
            'accurate': 0.9,
            'inaccurate': -0.9,
            'too_verbose': -0.3,
            'too_brief': -0.2,
            'off_topic': -0.7
        }
    
    def collect_implicit_feedback(self, execution_id: str, response: str, 
                                 response_time: float, user: User) -> Dict[str, Any]:
        """
        Collect implicit feedback based on response characteristics
        """
        feedback = {
            'execution_id': execution_id,
            'type': 'implicit',
            'timestamp': datetime.now(),
            'metrics': {}
        }
        
        # Response time feedback
        if response_time < 2.0:
            feedback['metrics']['speed'] = 'fast'
            feedback['score'] = 0.2
        elif response_time < 5.0:
            feedback['metrics']['speed'] = 'normal'
            feedback['score'] = 0.1
        else:
            feedback['metrics']['speed'] = 'slow'
            feedback['score'] = -0.1
        
        # Response length feedback
        response_length = len(response)
        if response_length < 50:
            feedback['metrics']['length'] = 'too_brief'
            feedback['score'] -= 0.2
        elif response_length > 2000:
            feedback['metrics']['length'] = 'too_verbose'
            feedback['score'] -= 0.3
        else:
            feedback['metrics']['length'] = 'appropriate'
            feedback['score'] += 0.1
        
        # Check if response asks for clarification (bad signal)
        clarification_phrases = [
            'could you clarify',
            'what do you mean',
            'can you be more specific',
            'i need more information',
            'which one do you',
            'do you want me to'
        ]
        
        response_lower = response.lower()
        asks_clarification = any(phrase in response_lower for phrase in clarification_phrases)
        
        if asks_clarification:
            feedback['metrics']['clarity'] = 'asks_clarification'
            feedback['score'] -= 0.5
            feedback['issues'] = ['Asked for unnecessary clarification']
        else:
            feedback['metrics']['clarity'] = 'direct_response'
            feedback['score'] += 0.2
        
        return feedback
    
    def collect_explicit_feedback(self, execution_id: str, feedback_type: str, 
                                 user: User, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect explicit user feedback
        """
        score = self.feedback_weights.get(feedback_type, 0.0)
        
        feedback = {
            'execution_id': execution_id,
            'type': 'explicit',
            'feedback_type': feedback_type,
            'score': score,
            'user_id': user.id,
            'timestamp': datetime.now(),
            'details': details or {}
        }
        
        # Process the feedback to update agent learning
        self._process_feedback(feedback)
        
        return feedback
    
    def _process_feedback(self, feedback: Dict[str, Any]):
        """
        Process feedback to update agent learning metrics
        """
        try:
            from agents.models import AgentExecution
            
            # Get the execution
            execution = AgentExecution.objects.filter(
                execution_id=feedback['execution_id']
            ).first()
            
            if not execution:
                logger.warning(f"Execution {feedback['execution_id']} not found for feedback")
                return
            
            # Update execution with feedback
            if not hasattr(execution, 'feedback_score'):
                execution.feedback_score = feedback['score']
            else:
                # Average with existing feedback
                execution.feedback_score = (execution.feedback_score + feedback['score']) / 2
            
            # Store feedback details
            if not execution.metadata:
                execution.metadata = {}
            
            if 'feedback' not in execution.metadata:
                execution.metadata['feedback'] = []
            
            execution.metadata['feedback'].append({
                'type': feedback.get('type'),
                'score': feedback['score'],
                'timestamp': feedback['timestamp'].isoformat(),
                'metrics': feedback.get('metrics', {})
            })
            
            execution.save()
            
            # Update agent's learning metrics
            agent = execution.template
            if agent and agent.learning_enabled:
                self._update_agent_learning(agent, feedback)
                
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
    
    def _update_agent_learning(self, agent, feedback: Dict[str, Any]):
        """
        Update agent's learning metrics based on feedback
        """
        try:
            # Adjust agent's routing keywords based on feedback
            if feedback['score'] > 0.5:
                # Positive feedback - this agent performed well
                # Could enhance routing keywords or increase confidence
                
                # Update user rating
                if agent.avg_user_rating == 0:
                    agent.avg_user_rating = min(5.0, 3.0 + feedback['score'])
                else:
                    # Rolling average
                    agent.avg_user_rating = min(5.0, 
                        (agent.avg_user_rating * 0.9) + ((3.0 + feedback['score']) * 0.1)
                    )
                
            elif feedback['score'] < -0.3:
                # Negative feedback - this agent needs improvement
                # Could adjust routing to use this agent less frequently
                
                # Update user rating
                if agent.avg_user_rating == 0:
                    agent.avg_user_rating = max(1.0, 3.0 + feedback['score'])
                else:
                    # Rolling average with higher weight on negative feedback
                    agent.avg_user_rating = max(1.0,
                        (agent.avg_user_rating * 0.8) + ((3.0 + feedback['score']) * 0.2)
                    )
            
            # Check for specific issues
            if feedback.get('metrics', {}).get('clarity') == 'asks_clarification':
                # This agent asks for too much clarification
                # Store this pattern for improvement
                if not agent.metadata:
                    agent.metadata = {}
                
                if 'learning_patterns' not in agent.metadata:
                    agent.metadata['learning_patterns'] = {}
                
                agent.metadata['learning_patterns']['asks_clarification_count'] = \
                    agent.metadata['learning_patterns'].get('asks_clarification_count', 0) + 1
            
            agent.save()
            
            # Log learning event
            logger.info(f"Agent {agent.name} learning update: score={feedback['score']:.2f}, rating={agent.avg_user_rating:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating agent learning: {e}")


class ResponseAnalyzer:
    """
    Analyzes agent responses for quality and learning signals
    """
    
    def analyze_response_quality(self, response: str, original_query: str) -> Dict[str, Any]:
        """
        Analyze response quality for learning signals
        """
        analysis = {
            'quality_score': 0.5,  # Start neutral
            'signals': [],
            'improvements_needed': []
        }
        
        # Check if response is relevant to query
        query_words = set(original_query.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate relevance
        common_words = query_words.intersection(response_words)
        if len(query_words) > 0:
            relevance = len(common_words) / len(query_words)
            if relevance > 0.3:
                analysis['quality_score'] += 0.2
                analysis['signals'].append('relevant')
            else:
                analysis['quality_score'] -= 0.3
                analysis['signals'].append('potentially_off_topic')
                analysis['improvements_needed'].append('improve_relevance')
        
        # Check for action vs clarification
        action_phrases = ['i will', "i'll", 'here is', 'here are', 'the answer', 'to do this']
        clarification_phrases = ['could you', 'do you mean', 'which', 'what exactly']
        
        response_lower = response.lower()
        
        has_action = any(phrase in response_lower for phrase in action_phrases)
        has_clarification = any(phrase in response_lower for phrase in clarification_phrases)
        
        if has_action and not has_clarification:
            analysis['quality_score'] += 0.3
            analysis['signals'].append('action_oriented')
        elif has_clarification and not has_action:
            analysis['quality_score'] -= 0.4
            analysis['signals'].append('asks_clarification')
            analysis['improvements_needed'].append('be_more_decisive')
        
        # Check response structure
        if response.count('\n') > 2 and len(response) > 200:
            analysis['signals'].append('well_structured')
            analysis['quality_score'] += 0.1
        
        # Normalize score
        analysis['quality_score'] = max(0.0, min(1.0, analysis['quality_score']))
        
        return analysis