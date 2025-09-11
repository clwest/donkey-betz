#!/usr/bin/env python3
"""
Learning Data Seeder - Populates system with sample learning data

This script creates sample feedback, conversations, and metrics to demonstrate
the learning system capabilities immediately after installation.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import SystemConfiguration, PlatformMetrics
from content.models import (
    ContentGeneration, ContentTemplate, Feedback,
    ContentAnalytics, Document, KnowledgeBase
)
from conversation_memory import ConversationMemory

User = get_user_model()


class LearningDataSeeder:
    """Seeds the system with realistic learning data"""
    
    def __init__(self):
        self.users = []
        self.templates = []
        self.conversations = []
        self.feedback_entries = []
        
    def seed_all_data(self):
        """Seed all types of learning data"""
        print("🌱 Seeding Learning System Data...")
        print("=" * 50)
        
        # Create users if needed
        self.create_sample_users()
        
        # Create content templates
        self.create_content_templates()
        
        # Create content generations with realistic performance
        self.create_content_generations()
        
        # Create user feedback
        self.create_user_feedback()
        
        # Create conversation history
        self.create_conversation_history()
        
        # Create system configurations
        self.create_system_configs()
        
        # Create initial platform metrics
        self.create_platform_metrics()
        
        # Create learning insights
        self.create_learning_insights()
        
        print("\n✅ Learning data seeding complete!")
        print(f"   • Created {len(self.users)} users")
        print(f"   • Created {len(self.templates)} templates")
        print(f"   • Created conversation history")
        print(f"   • Created feedback data")
        print(f"   • Created performance metrics")
        
        return {
            'users_created': len(self.users),
            'templates_created': len(self.templates),
            'conversations_created': len(self.conversations),
            'feedback_created': len(self.feedback_entries)
        }
    
    def create_sample_users(self):
        """Create sample users for testing"""
        print("👤 Creating sample users...")
        
        sample_users = [
            {'username': 'alice_writer', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Writer'},
            {'username': 'bob_analyst', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Analyst'},
            {'username': 'carol_marketer', 'email': 'carol@example.com', 'first_name': 'Carol', 'last_name': 'Marketer'},
            {'username': 'dave_developer', 'email': 'dave@example.com', 'first_name': 'Dave', 'last_name': 'Developer'},
        ]
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            
            if created:
                self.users.append(user)
                print(f"   Created user: {user.username}")
            else:
                self.users.append(user)
    
    def create_content_templates(self):
        """Create realistic content templates"""
        print("📝 Creating content templates...")
        
        templates_data = [
            {
                'name': 'blog_post_technical',
                'display_name': 'Technical Blog Post',
                'description': 'Generate technical blog posts with code examples',
                'template_type': 'article',
                'system_prompt': 'You are a technical writer creating detailed, accurate blog posts.',
                'user_prompt_template': 'Write a technical blog post about {{ topic }} including code examples and best practices.',
                'output_format': 'markdown',
                'generation_config': {'temperature': 0.7, 'max_tokens': 2000}
            },
            {
                'name': 'social_media_engaging',
                'display_name': 'Engaging Social Media Post',
                'description': 'Create engaging social media content',
                'template_type': 'social_post',
                'system_prompt': 'You create engaging, viral-worthy social media content.',
                'user_prompt_template': 'Create an engaging social media post about {{ topic }} that encourages interaction.',
                'output_format': 'text',
                'generation_config': {'temperature': 0.8, 'max_tokens': 280}
            },
            {
                'name': 'email_newsletter',
                'display_name': 'Email Newsletter',
                'description': 'Professional email newsletter content',
                'template_type': 'email',
                'system_prompt': 'You write professional, informative newsletter content.',
                'user_prompt_template': 'Write a newsletter section about {{ topic }} for {{ audience }}.',
                'output_format': 'html',
                'generation_config': {'temperature': 0.6, 'max_tokens': 1500}
            },
            {
                'name': 'product_description',
                'display_name': 'Product Description',
                'description': 'Compelling product descriptions for e-commerce',
                'template_type': 'creative',
                'system_prompt': 'You write compelling, SEO-friendly product descriptions.',
                'user_prompt_template': 'Write a product description for {{ product_name }} highlighting {{ key_features }}.',
                'output_format': 'html',
                'generation_config': {'temperature': 0.75, 'max_tokens': 800}
            },
            {
                'name': 'code_documentation',
                'display_name': 'Code Documentation',
                'description': 'Generate comprehensive code documentation',
                'template_type': 'documentation',
                'system_prompt': 'You create clear, comprehensive technical documentation.',
                'user_prompt_template': 'Document the {{ code_type }} code for {{ functionality }} including usage examples.',
                'output_format': 'markdown',
                'generation_config': {'temperature': 0.4, 'max_tokens': 1800}
            }
        ]
        
        for template_data in templates_data:
            template, created = ContentTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'variables': {
                        'topic': {'type': 'string', 'required': True},
                        'audience': {'type': 'string', 'required': False},
                        'product_name': {'type': 'string', 'required': False},
                        'key_features': {'type': 'string', 'required': False},
                        'code_type': {'type': 'string', 'required': False},
                        'functionality': {'type': 'string', 'required': False}
                    },
                    'tags': ['sample', 'seeded'],
                    'is_public': True,
                    'is_verified': True
                }
            )
            
            if created:
                self.templates.append(template)
                print(f"   Created template: {template.display_name}")
            else:
                self.templates.append(template)
    
    def create_content_generations(self):
        """Create realistic content generations with varying performance"""
        print("🎨 Creating content generations...")
        
        if not self.users or not self.templates:
            print("   Skipping - no users or templates available")
            return
        
        # Create generations with realistic distribution
        generation_scenarios = [
            # Successful generations
            {
                'status': 'completed',
                'generation_time_range': (5000, 15000),  # 5-15 seconds
                'quality_score_range': (0.8, 0.95),
                'probability': 0.7
            },
            # Slow but successful generations
            {
                'status': 'completed', 
                'generation_time_range': (20000, 45000),  # 20-45 seconds
                'quality_score_range': (0.6, 0.85),
                'probability': 0.15
            },
            # Failed generations
            {
                'status': 'failed',
                'generation_time_range': (30000, 60000),  # Failed after timeout
                'quality_score_range': (0.0, 0.3),
                'probability': 0.1
            },
            # Processing generations (stuck)
            {
                'status': 'processing',
                'generation_time_range': (0, 0),  # No completion time yet
                'quality_score_range': (0.0, 0.0),
                'probability': 0.05
            }
        ]
        
        prompts = [
            "Write a blog post about artificial intelligence trends",
            "Create content about sustainable technology",
            "Generate a product description for smart home devices", 
            "Write documentation for our new API",
            "Create a social media post about our latest feature",
            "Write an email newsletter about industry updates",
            "Generate content about machine learning applications",
            "Create a technical guide for developers",
            "Write marketing copy for our new product launch",
            "Generate educational content about data science"
        ]
        
        # Create generations over the past 30 days
        for day_offset in range(30):
            date = timezone.now() - timedelta(days=day_offset)
            generations_per_day = random.randint(1, 4)
            
            for _ in range(generations_per_day):
                # Choose scenario based on probability
                rand_val = random.random()
                cumulative_prob = 0
                chosen_scenario = generation_scenarios[0]  # Default
                
                for scenario in generation_scenarios:
                    cumulative_prob += scenario['probability']
                    if rand_val <= cumulative_prob:
                        chosen_scenario = scenario
                        break
                
                # Create generation
                user = random.choice(self.users)
                template = random.choice(self.templates)
                prompt = random.choice(prompts)
                
                generation_time = None
                if chosen_scenario['status'] in ['completed', 'failed']:
                    generation_time = random.randint(*chosen_scenario['generation_time_range'])
                
                quality_score = None
                if chosen_scenario['status'] == 'completed':
                    quality_score = random.uniform(*chosen_scenario['quality_score_range'])
                
                generation = ContentGeneration.objects.create(
                    user=user,
                    template=template,
                    prompt=prompt,
                    system_prompt=template.system_prompt,
                    generated_content=f"Generated content for: {prompt}" if chosen_scenario['status'] == 'completed' else "",
                    status=chosen_scenario['status'],
                    generation_time_ms=generation_time,
                    quality_score=quality_score,
                    generation_config=template.generation_config,
                    token_usage={
                        'prompt_tokens': random.randint(50, 200),
                        'completion_tokens': random.randint(200, 800),
                        'total_tokens': random.randint(250, 1000)
                    },
                    generation_cost=Decimal(str(random.uniform(0.001, 0.05))),
                    source_system='seeded_data'
                )
                
                # Update the creation date
                generation.created_at = date
                generation.save()
    
    def create_user_feedback(self):
        """Create realistic user feedback"""
        print("📊 Creating user feedback...")
        
        # Get recent content generations
        recent_generations = ContentGeneration.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        feedback_scenarios = [
            {'rating': 5, 'comments': ['Excellent quality!', 'Perfect for my needs', 'Exceeded expectations'], 'probability': 0.3},
            {'rating': 4, 'comments': ['Very good', 'Minor improvements needed', 'Mostly satisfied'], 'probability': 0.4},
            {'rating': 3, 'comments': ['Average quality', 'Could be better', 'Mixed results'], 'probability': 0.2},
            {'rating': 2, 'comments': ['Below expectations', 'Several issues', 'Not quite right'], 'probability': 0.08},
            {'rating': 1, 'comments': ['Poor quality', 'Major issues', 'Very disappointed'], 'probability': 0.02}
        ]
        
        # Create feedback for ~30% of completed generations
        generations_to_rate = random.sample(list(recent_generations), min(len(recent_generations), int(len(recent_generations) * 0.3)))
        
        for generation in generations_to_rate:
            # Choose scenario based on probability
            rand_val = random.random()
            cumulative_prob = 0
            chosen_scenario = feedback_scenarios[0]  # Default
            
            for scenario in feedback_scenarios:
                cumulative_prob += scenario['probability']
                if rand_val <= cumulative_prob:
                    chosen_scenario = scenario
                    break
            
            # Create feedback
            feedback = Feedback.objects.create(
                content_type='text',  # Assuming text content
                content_id=random.randint(1, 999999),  # Simple random ID
                user=generation.user,
                overall_rating=chosen_scenario['rating'],
                quality_rating=chosen_scenario['rating'],
                usefulness_rating=random.randint(max(1, chosen_scenario['rating'] - 1), min(5, chosen_scenario['rating'] + 1)),
                feedback_type='general',
                comments=random.choice(chosen_scenario['comments']),
                would_recommend=chosen_scenario['rating'] >= 4,
                met_expectations=chosen_scenario['rating'] >= 3,
                saved_time=chosen_scenario['rating'] >= 3,
                generation_params={
                    'template': generation.template.name if generation.template else 'unknown',
                    'generation_time': generation.generation_time_ms
                }
            )
            
            # Set creation date to match generation
            feedback.created_at = generation.created_at + timedelta(hours=random.randint(1, 48))
            feedback.save()
            
            self.feedback_entries.append(feedback)
    
    def create_conversation_history(self):
        """Create realistic conversation history"""
        print("💬 Creating conversation history...")
        
        memory = ConversationMemory()
        
        conversation_scenarios = [
            {
                'user_input': 'Help me write a blog post about AI',
                'assistant_response': 'I\'d be happy to help you write a blog post about AI. Let me create an outline covering current trends, applications, and future implications...',
                'context': {'task_type': 'content_creation', 'content_type': 'blog_post'}
            },
            {
                'user_input': 'Make it more technical and include code examples',
                'assistant_response': 'I\'ll adjust the blog post to be more technical. Here are some Python code examples for machine learning implementations...',
                'context': {'task_type': 'content_refinement', 'technical_level': 'advanced'}
            },
            {
                'user_input': 'Can you optimize this code for better performance?',
                'assistant_response': 'I\'ll analyze your code and suggest performance optimizations. Here are the main bottlenecks I found...',
                'context': {'task_type': 'code_optimization', 'language': 'python'}
            },
            {
                'user_input': 'Explain how machine learning works',
                'assistant_response': 'Machine learning is a subset of AI that enables computers to learn from data without being explicitly programmed. There are three main types...',
                'context': {'task_type': 'explanation', 'topic': 'machine_learning'}
            },
            {
                'user_input': 'Create a social media post about our new feature',
                'assistant_response': 'Here\'s an engaging social media post for your new feature: "🚀 Exciting news! Our latest feature will revolutionize how you...',
                'context': {'task_type': 'social_media', 'purpose': 'promotion'}
            },
            {
                'user_input': 'Write a product description for smart home devices',
                'assistant_response': 'Here\'s a compelling product description for your smart home devices that highlights key features and benefits...',
                'context': {'task_type': 'product_description', 'category': 'smart_home'}
            },
            {
                'user_input': 'How can I improve my content generation process?',
                'assistant_response': 'Here are several strategies to improve your content generation process: 1. Use more specific prompts, 2. Provide context...',
                'context': {'task_type': 'consultation', 'topic': 'process_improvement'}
            }
        ]
        
        # Create conversations for each user over the past 14 days
        for user in self.users:
            num_conversations = random.randint(3, 12)  # Varying engagement levels
            
            for i in range(num_conversations):
                # Pick random scenarios for a conversation thread
                thread_length = random.randint(2, 5)
                conversation_date = timezone.now() - timedelta(days=random.randint(0, 14))
                
                for j in range(thread_length):
                    scenario = random.choice(conversation_scenarios)
                    
                    interaction_id = memory.store_interaction(
                        user.id,
                        scenario['user_input'],
                        scenario['assistant_response'],
                        scenario['context']
                    )
                    
                    # Update the timestamp to be in the past
                    config_key = f"conversation_interaction_{user.id}_{interaction_id}"
                    config = SystemConfiguration.objects.get(key=config_key)
                    config.created_at = conversation_date + timedelta(minutes=j * 5)
                    config.save()
                    
                    self.conversations.append(interaction_id)
        
        # Learn some user preferences
        for user in self.users:
            preferences = {
                'content_style': random.choice(['professional', 'casual', 'technical']),
                'preferred_length': random.choice(['short', 'medium', 'long']),
                'tone': random.choice(['formal', 'conversational', 'enthusiastic']),
                'topics_of_interest': random.sample(['AI', 'technology', 'business', 'marketing', 'development'], 2)
            }
            
            for pref_key, pref_value in preferences.items():
                memory.store_user_preference(user.id, pref_key, pref_value)
    
    def create_system_configs(self):
        """Create system configuration entries"""
        print("⚙️ Creating system configurations...")
        
        configs = [
            ('monitoring_enabled', True, 'Enable system performance monitoring', 'performance'),
            ('content_generation_rate_limit', {'requests_per_hour': 100, 'requests_per_minute': 10}, 'Rate limits for content generation', 'performance'),
            ('feedback_prompt_frequency', {'show_after_generations': 3, 'show_probability': 0.3}, 'Settings for feedback collection prompts', 'user_experience'),
            ('auto_optimization_enabled', True, 'Enable automatic performance optimizations', 'optimization'),
            ('learning_cycles_enabled', True, 'Enable learning loop cycles', 'learning'),
            ('conversation_memory_retention_days', 90, 'Days to retain conversation memory', 'conversation'),
            ('performance_baseline_success_rate', 85.0, 'Target success rate for content generation', 'performance'),
            ('quality_threshold', 0.7, 'Minimum quality threshold for content', 'content_quality')
        ]
        
        for key, value, description, category in configs:
            SystemConfiguration.set_config(key, value, description, category)
            print(f"   Set config: {key}")
    
    def create_platform_metrics(self):
        """Create initial platform metrics"""
        print("📈 Creating platform metrics...")
        
        # Create metrics over the past 7 days
        for day_offset in range(7):
            date = timezone.now() - timedelta(days=day_offset)
            
            # Daily performance metrics
            metrics = [
                ('daily_content_generations', random.randint(10, 50), 'counter', 'content'),
                ('avg_generation_time_ms', random.randint(8000, 25000), 'gauge', 'performance'),
                ('success_rate_percentage', random.uniform(75, 95), 'gauge', 'performance'),
                ('user_satisfaction_avg', random.uniform(3.2, 4.6), 'gauge', 'user_experience'),
                ('active_users', random.randint(5, 15), 'gauge', 'usage'),
                ('feedback_submissions', random.randint(2, 8), 'counter', 'feedback'),
                ('template_usage_count', random.randint(15, 40), 'counter', 'templates')
            ]
            
            for metric_name, value, metric_type, subsystem in metrics:
                metric = PlatformMetrics.objects.create(
                    metric_name=metric_name,
                    metric_value=value,
                    metric_type=metric_type,
                    subsystem=subsystem,
                    labels={'date': date.date().isoformat(), 'seeded': True}
                )
                metric.created_at = date
                metric.save()
    
    def create_learning_insights(self):
        """Create sample learning insights and optimization records"""
        print("🧠 Creating learning insights...")
        
        # Create learning cycle completions
        for day_offset in [1, 3, 5, 7]:
            date = timezone.now() - timedelta(days=day_offset)
            
            # Learning cycle completion
            metric = PlatformMetrics.objects.create(
                metric_name="learning_cycle_completed",
                metric_value=1.0,
                metric_type='counter',
                subsystem='learning',
                labels={
                    'timestamp': date.isoformat(),
                    'insights_generated': random.randint(5, 15),
                    'optimizations_identified': random.randint(2, 8),
                    'seeded': True
                }
            )
            metric.created_at = date
            metric.save()
            
            # Auto-optimization completion  
            metric = PlatformMetrics.objects.create(
                metric_name="auto_optimization_cycle_completed",
                metric_value=1.0,
                metric_type='counter',
                subsystem='optimization',
                labels={
                    'timestamp': date.isoformat(),
                    'optimizations_applied': random.randint(1, 5),
                    'baseline_success_rate': random.uniform(80, 90),
                    'seeded': True
                }
            )
            metric.created_at = date
            metric.save()
            
            # Specific optimization actions
            optimization_actions = [
                'monitoring_enabled',
                'rate_limits_configured', 
                'feedback_enhancement',
                'template_optimization',
                'performance_tuning'
            ]
            
            for action in random.sample(optimization_actions, random.randint(1, 3)):
                metric = PlatformMetrics.objects.create(
                    metric_name=f"optimization_applied_{action}",
                    metric_value=1.0,
                    metric_type='counter',
                    subsystem='optimization',
                    labels={
                        'timestamp': date.isoformat(),
                        'auto_applied': True,
                        'seeded': True
                    }
                )
                metric.created_at = date
                metric.save()


if __name__ == "__main__":
    seeder = LearningDataSeeder()
    results = seeder.seed_all_data()
    
    print("\n" + "=" * 50)
    print("🎉 LEARNING DATA SEEDING COMPLETE!")
    print("=" * 50)
    print("Your learning system now has realistic data to work with:")
    print(f"✅ {results['users_created']} users with conversation history")
    print(f"✅ {results['templates_created']} content templates")
    print(f"✅ Content generations with realistic performance variations")
    print(f"✅ User feedback with quality ratings")
    print(f"✅ System configurations and optimization settings")
    print(f"✅ Historical metrics and learning insights")
    
    print("\n🚀 Ready to test the learning system!")
    print("Run verification_agent.py again to see the learning loops in action!")