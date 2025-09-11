#!/usr/bin/env python3
"""
Reality Check Agent - Verify what actually works vs what's documented
"""

import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime, timedelta
import requests
import sqlite3
import psycopg2

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from core.models import UserProfile, SystemConfiguration, PlatformMetrics
from content.models import Document, ContentGeneration, ContentAnalytics, Feedback

User = get_user_model()


class SystemVerificationAgent:
    def __init__(self):
        self.claimed_features = []
        self.verified_features = []
        self.broken_features = []
        self.test_results = {}
        
    def run_all_tests(self):
        """Run comprehensive system verification"""
        print("🔍 Starting System Verification...")
        print("=" * 50)
        
        tests = [
            ("Database Connectivity", self.test_database_connectivity),
            ("Learning Loops", self.test_learning_loops),
            ("Feature Request System", self.test_feature_requests),
            ("RAG Feedback", self.test_rag_feedback),
            ("Conversation Memory", self.test_conversation_memory),
            ("API Endpoints", self.test_api_endpoints),
            ("Auto-Optimization", self.test_auto_optimization),
            ("Code Generation", self.test_code_generation),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result.get('success', False):
                    self.verified_features.append(test_name)
                    print(f"✅ {test_name}: PASSED")
                else:
                    self.broken_features.append(test_name)
                    print(f"❌ {test_name}: FAILED")
                    if result.get('error'):
                        print(f"   Error: {result['error']}")
            except Exception as e:
                self.broken_features.append(f"{test_name}: {str(e)}")
                print(f"💥 {test_name}: CRASHED - {str(e)}")
                
        self.generate_report()
    
    def test_database_connectivity(self):
        """Test if we can connect to the database"""
        try:
            # Use Django ORM instead of raw SQL
            user_count = User.objects.count()
            profile_count = UserProfile.objects.count()
                
            return {
                'success': True,
                'details': f"Connected to database with {user_count} users and {profile_count} profiles",
                'user_count': user_count,
                'profile_count': profile_count
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_learning_loops(self):
        """Test if the learning loops actually work"""
        try:
            # Check if PlatformMetrics table exists and has learning-related data
            metrics_count = PlatformMetrics.objects.count()
            
            # Look for any learning-related metrics
            learning_metrics = PlatformMetrics.objects.filter(
                metric_name__icontains='learning'
            ).count()
            
            # Check for optimization metrics
            optimization_metrics = PlatformMetrics.objects.filter(
                metric_name__icontains='optimization'
            ).count()
            
            # Check for any system configurations related to learning
            learning_configs = SystemConfiguration.objects.filter(
                key__icontains='learning'
            ).count()
            
            return {
                'success': metrics_count > 0,
                'details': f"Metrics: {metrics_count}, Learning metrics: {learning_metrics}, Optimization metrics: {optimization_metrics}, Learning configs: {learning_configs}",
                'metrics_count': metrics_count,
                'learning_metrics': learning_metrics,
                'optimization_metrics': optimization_metrics,
                'learning_configs': learning_configs
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_feature_requests(self):
        """Can the system actually file feature requests?"""
        try:
            # Check if we have any content generation requests
            generation_count = ContentGeneration.objects.count()
            
            # Check recent requests
            recent_generations = ContentGeneration.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=7)
            ).count()
            
            # Check documents created
            document_count = Document.objects.count()
            
            return {
                'success': generation_count > 0,
                'details': f"Content generations: {generation_count}, Recent (7d): {recent_generations}, Documents: {document_count}",
                'generation_count': generation_count,
                'recent_generations': recent_generations,
                'document_count': document_count
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_rag_feedback(self):
        """Test RAG feedback mechanisms"""
        try:
            # Look for feedback entries
            feedback_count = Feedback.objects.count()
            
            # Check for analytics entries related to feedback
            analytics_count = ContentAnalytics.objects.filter(
                metric_name__icontains='feedback'
            ).count()
            
            # Check for conversation-related analytics
            conversation_analytics = ContentAnalytics.objects.filter(
                metric_name__icontains='conversation'
            ).count()
            
            return {
                'success': feedback_count > 0 or analytics_count > 0,
                'details': f"Feedback entries: {feedback_count}, Analytics: {analytics_count}, Conversation analytics: {conversation_analytics}",
                'feedback_count': feedback_count,
                'analytics_count': analytics_count,
                'conversation_analytics': conversation_analytics
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_conversation_memory(self):
        """Test if conversation memory actually works"""
        try:
            # Get recent system configurations that might store memory
            configs_count = SystemConfiguration.objects.count()
            
            # Check if we can create and retrieve a test configuration
            test_key = f"test_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            test_config = SystemConfiguration.objects.create(
                key=test_key,
                value={"test": "memory entry", "timestamp": datetime.now().isoformat()},
                description="Test memory entry for verification",
                category="system"
            )
            
            # Try to retrieve it
            retrieved = SystemConfiguration.objects.filter(key=test_key).first()
            
            # Clean up test data
            if retrieved:
                retrieved.delete()
            
            return {
                'success': retrieved is not None,
                'details': f"System configs: {configs_count}, Test retrieval: {'Success' if retrieved else 'Failed'}",
                'configs_count': configs_count,
                'test_retrieval': retrieved is not None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_api_endpoints(self):
        """Test if API endpoints are actually accessible"""
        try:
            endpoints_to_test = [
                'http://localhost:8000/api/health/',
                'http://localhost:8000/api/v1/status/',
            ]
            
            accessible_endpoints = []
            failed_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        accessible_endpoints.append(endpoint)
                    else:
                        failed_endpoints.append(f"{endpoint} ({response.status_code})")
                except requests.RequestException as e:
                    failed_endpoints.append(f"{endpoint} (Connection error)")
            
            return {
                'success': len(accessible_endpoints) > 0,
                'details': f"Accessible: {len(accessible_endpoints)}, Failed: {len(failed_endpoints)}",
                'accessible': accessible_endpoints,
                'failed': failed_endpoints
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_auto_optimization(self):
        """Test if auto-optimization features exist"""
        try:
            # Look for optimization-related metrics
            optimization_metrics = PlatformMetrics.objects.filter(
                metric_name__icontains='optimization'
            )
            
            # Check for optimization configurations
            optimization_configs = SystemConfiguration.objects.filter(
                key__icontains='optimization'
            )
            
            # Get table names through Django's introspection
            from django.db import connections
            db_connection = connections['default']
            table_names = db_connection.introspection.table_names(db_connection.cursor())
            optimization_tables = [table for table in table_names if 'optimization' in table.lower()]
            
            return {
                'success': len(optimization_metrics) > 0 or len(optimization_configs) > 0 or len(optimization_tables) > 0,
                'details': f"Optimization metrics: {len(optimization_metrics)}, Configs: {len(optimization_configs)}, Tables: {len(optimization_tables)}",
                'metrics_count': len(optimization_metrics),
                'configs_count': len(optimization_configs),
                'related_tables': optimization_tables
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_code_generation(self):
        """Test if code generation features are available"""
        try:
            # Look for code-related content generation
            code_generations = ContentGeneration.objects.filter(
                prompt__icontains='code'
            )
            
            # Check for code-related documents
            code_documents = Document.objects.filter(
                document_type__in=['python', 'javascript', 'typescript', 'sql']
            )
            
            # Check for code-related analytics
            code_analytics = ContentAnalytics.objects.filter(
                metric_name__icontains='code'
            ).count()
            
            return {
                'success': len(code_generations) > 0 or len(code_documents) > 0,
                'details': f"Code generations: {len(code_generations)}, Code documents: {len(code_documents)}, Analytics: {code_analytics}",
                'generation_count': len(code_generations),
                'document_count': len(code_documents),
                'analytics_count': code_analytics
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def show_last_feature_request(self):
        """Show the last content generation that was filed"""
        try:
            last_generation = ContentGeneration.objects.order_by('-created_at').first()
            if last_generation:
                return {
                    'id': str(last_generation.id),
                    'prompt': last_generation.prompt[:200] + '...' if len(last_generation.prompt) > 200 else last_generation.prompt,
                    'created_at': last_generation.created_at.isoformat(),
                    'status': last_generation.status,
                    'user': last_generation.user.username if last_generation.user else 'Unknown'
                }
            return None
        except Exception as e:
            print(f"Error retrieving last content generation: {e}")
            return None
    
    def show_recent_optimizations(self):
        """Show optimizations that ran in the last 24 hours"""
        try:
            recent_optimizations = PlatformMetrics.objects.filter(
                metric_name__icontains='optimization',
                created_at__gte=datetime.now() - timedelta(hours=24)
            ).order_by('-created_at')
            
            return [
                {
                    'metric_name': opt.metric_name,
                    'value': str(opt.metric_value),
                    'subsystem': opt.subsystem,
                    'created_at': opt.created_at.isoformat()
                }
                for opt in recent_optimizations
            ]
        except Exception as e:
            print(f"Error retrieving recent optimizations: {e}")
            return []
    
    def show_conversation_memory(self):
        """Display the conversation memory from recent chats"""
        try:
            conversation_configs = SystemConfiguration.objects.filter(
                key__icontains='conversation'
            ).order_by('-created_at')[:10]
            
            return [
                {
                    'key': config.key,
                    'value': str(config.value)[:200] + '...' if len(str(config.value)) > 200 else str(config.value),
                    'created_at': config.created_at.isoformat()
                }
                for config in conversation_configs
            ]
        except Exception as e:
            print(f"Error retrieving conversation memory: {e}")
            return []
    
    def show_learning_insights(self):
        """List the 5 most recent learning loop insights"""
        try:
            learning_metrics = PlatformMetrics.objects.filter(
                metric_name__icontains='learning'
            ).order_by('-created_at')[:5]
            
            return [
                {
                    'metric_name': metric.metric_name,
                    'value': str(metric.metric_value),
                    'subsystem': metric.subsystem,
                    'created_at': metric.created_at.isoformat()
                }
                for metric in learning_metrics
            ]
        except Exception as e:
            print(f"Error retrieving learning insights: {e}")
            return []
    
    def generate_report(self):
        """Generate a comprehensive reality check report"""
        print("\n" + "=" * 50)
        print("📊 SYSTEM VERIFICATION REPORT")
        print("=" * 50)
        
        print(f"\n✅ VERIFIED FEATURES ({len(self.verified_features)}):")
        for feature in self.verified_features:
            print(f"   • {feature}")
        
        print(f"\n❌ BROKEN/MISSING FEATURES ({len(self.broken_features)}):")
        for feature in self.broken_features:
            print(f"   • {feature}")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test_name, result in self.test_results.items():
            print(f"\n{test_name}:")
            if isinstance(result.get('details'), str):
                print(f"   {result['details']}")
            else:
                for key, value in result.items():
                    if key != 'success':
                        print(f"   {key}: {value}")
        
        # Show concrete examples
        print(f"\n🔍 CONCRETE EXAMPLES:")
        
        print("\nLast Content Generation:")
        last_request = self.show_last_feature_request()
        if last_request:
            print(f"   ID: {last_request['id']}, User: {last_request['user']}")
            print(f"   Created: {last_request['created_at']}")
            print(f"   Status: {last_request['status']}")
            print(f"   Prompt: {last_request['prompt']}")
        else:
            print("   No content generations found")
        
        print("\nRecent Optimizations (24h):")
        optimizations = self.show_recent_optimizations()
        if optimizations:
            for opt in optimizations:
                print(f"   • {opt['metric_name']}: {opt['value']} ({opt['subsystem']})")
        else:
            print("   No recent optimizations found")
        
        print("\nConversation Memory:")
        conv_memory = self.show_conversation_memory()
        if conv_memory:
            for mem in conv_memory[:3]:  # Show top 3
                print(f"   • {mem['key']}: {mem['value']}")
        else:
            print("   No conversation memory found")
        
        print("\nLearning Insights:")
        insights = self.show_learning_insights()
        if insights:
            for insight in insights:
                print(f"   • {insight['metric_name']}: {insight['value']} ({insight['subsystem']})")
        else:
            print("   No learning insights found")
        
        # Overall assessment
        total_tests = len(self.verified_features) + len(self.broken_features)
        success_rate = (len(self.verified_features) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Verified: {len(self.verified_features)}/{total_tests}")
        
        if success_rate < 50:
            print("   🚨 CRITICAL: Many features appear to be non-functional")
        elif success_rate < 80:
            print("   ⚠️  WARNING: Some features need attention")
        else:
            print("   ✅ GOOD: Most features are working as expected")


if __name__ == "__main__":
    agent = SystemVerificationAgent()
    agent.run_all_tests()