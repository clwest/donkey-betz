#!/usr/bin/env python3
"""
FIX AGENT EXECUTION RESULTS
This script fixes the issue where agent executions complete but don't save results
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import AgentExecution
import json

def analyze_execution_issues():
    """Analyze why executions have no results"""
    
    print("="*60)
    print("ANALYZING EXECUTION RESULTS ISSUE")
    print("="*60)
    
    # Get recent executions
    executions = AgentExecution.objects.all().order_by('-created_at')[:10]
    
    for exec in executions:
        print(f"\n📝 Execution: {exec.execution_id}")
        print(f"   Status: {exec.status}")
        print(f"   Task: {exec.task_description[:100] if exec.task_description else 'None'}...")
        
        # Check all output fields
        output_fields = {
            'result': exec.result,
            'output_data': exec.output_data,
            'llm_response': exec.llm_response,
            'output_files': exec.output_files
        }
        
        has_output = False
        for field, value in output_fields.items():
            if value:
                has_output = True
                if isinstance(value, (dict, list)):
                    print(f"   {field}: {json.dumps(value, indent=2)[:200]}...")
                else:
                    print(f"   {field}: {str(value)[:200]}...")
        
        if not has_output:
            print("   ⚠️ NO OUTPUT STORED")
            
        # Check errors
        if exec.error_message:
            print(f"   ❌ Error: {exec.error_message}")
        
    # Check if the executor is properly saving results
    print("\n" + "="*60)
    print("CHECKING EXECUTOR IMPLEMENTATION")
    print("="*60)
    
    # Look at content executor
    from agents.content_executor import DonkeyBetzContentExecutor
    import inspect
    
    source = inspect.getsource(DonkeyBetzContentExecutor.execute_content_creation)
    
    # Check if it's saving results
    if 'execution.result' in source or 'execution.output_data' in source:
        print("✅ Executor appears to save results")
    else:
        print("❌ Executor may not be saving results properly")
    
    # Check for save() calls
    if 'execution.save()' in source:
        save_count = source.count('execution.save()')
        print(f"✅ Found {save_count} save() calls")
    else:
        print("❌ No save() calls found")
    
    print("\n" + "="*60)
    print("RECOMMENDED FIXES")
    print("="*60)
    
    print("""
1. UPDATE EXECUTOR to save results:
   - Set execution.result = generated_content
   - Set execution.output_data = {'content': content, 'metadata': {...}}
   - Set execution.llm_response = raw_llm_response
   - Call execution.save() after setting results

2. VERIFY LLM CALLS are working:
   - Check LLMEnforcer configuration
   - Verify API keys are set
   - Test direct LLM calls

3. CHECK CELERY if using async:
   - Ensure workers are running
   - Check task results backend
   
4. RUN the test script:
   python execute_test_agent.py --check
   python execute_test_agent.py --agent content-creator --task "Test task"
   """)


def patch_executor():
    """Create a patched version of the executor that properly saves results"""
    
    patch_content = '''"""
PATCHED Donkey Betz Content Creator Execution Engine
This version properly saves results to the database
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone

from core.llm_enforcer import LLMEnforcer
from agents.models import AgentExecution, AgentStatus

logger = logging.getLogger(__name__)


class DonkeyBetzContentExecutor:
    """Execution engine for Donkey Betz Content Creator (PATCHED)"""

    def __init__(self):
        self.llm_enforcer = LLMEnforcer()
        self.logger = logging.getLogger(__name__)

    def execute_content_creation(self, execution_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content creation task for Donkey Betz (PATCHED VERSION)

        Args:
            execution_id: Unique execution identifier
            task_data: Task parameters and requirements

        Returns:
            Dict containing execution results
        """
        try:
            # Get execution record
            execution = AgentExecution.objects.get(id=execution_id)
            execution.status = AgentStatus.RUNNING
            execution.started_at = timezone.now()
            execution.progress_percentage = 20
            execution.current_step = "Initializing content generation"
            execution.save()

            # Extract task parameters
            task_description = task_data.get('task', 'Create content about Donkey Betz')
            content_type = task_data.get('content_type', 'blog_post')
            target_audience = task_data.get('target_audience', 'sports betting enthusiasts')
            tone = task_data.get('tone', 'professional and engaging')
            
            self.logger.info(f"Generating {content_type} for {target_audience}")
            
            # Update progress
            execution.progress_percentage = 40
            execution.current_step = "Generating content with LLM"
            execution.save()
            
            # Generate content using LLM
            prompt = f"""
            Task: {task_description}
            Content Type: {content_type}
            Target Audience: {target_audience}
            Tone: {tone}
            
            Generate high-quality content that:
            1. Engages the target audience
            2. Maintains the specified tone
            3. Provides value and insights
            4. Is well-structured and formatted
            
            Content:
            """
            
            llm_response = self.llm_enforcer.generate_completion(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7
            )
            
            # Update progress
            execution.progress_percentage = 80
            execution.current_step = "Processing and formatting content"
            execution.save()
            
            # Process the response
            generated_content = llm_response.strip()
            
            # Create result structure
            result = {
                'success': True,
                'content': generated_content,
                'metadata': {
                    'content_type': content_type,
                    'target_audience': target_audience,
                    'tone': tone,
                    'word_count': len(generated_content.split()),
                    'generated_at': timezone.now().isoformat()
                },
                'task': task_description
            }
            
            # CRITICAL: Save results to execution
            execution.status = AgentStatus.COMPLETED
            execution.result = result  # Store full result
            execution.output_data = result['metadata']  # Store metadata
            execution.llm_response = generated_content  # Store raw content
            execution.completed_at = timezone.now()
            execution.progress_percentage = 100
            execution.current_step = "Content generation completed"
            
            # Calculate execution time
            if execution.started_at:
                execution.execution_time_seconds = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
            
            # Estimate token usage (rough estimate)
            execution.token_usage = {
                'prompt_tokens': len(prompt.split()) * 1.3,
                'completion_tokens': len(generated_content.split()) * 1.3,
                'total_tokens': (len(prompt.split()) + len(generated_content.split())) * 1.3
            }
            
            # Save all changes
            execution.save()
            
            self.logger.info(f"✅ Content generation completed for execution {execution_id}")
            self.logger.info(f"   Generated {result['metadata']['word_count']} words")
            
            return result
            
        except AgentExecution.DoesNotExist:
            self.logger.error(f"Execution {execution_id} not found")
            return {
                'success': False,
                'error': f'Execution {execution_id} not found'
            }
        except Exception as e:
            self.logger.error(f"Error executing content creation: {str(e)}")
            
            # Update execution with error
            try:
                execution = AgentExecution.objects.get(id=execution_id)
                execution.status = AgentStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = timezone.now()
                execution.save()
            except:
                pass
                
            return {
                'success': False,
                'error': str(e)
            }
'''
    
    print("\n" + "="*60)
    print("CREATING PATCHED EXECUTOR")
    print("="*60)
    
    # Save the patched version
    with open('/Users/donkeyking/development/unified-donkey-betz/agents/content_executor_patched.py', 'w') as f:
        f.write(patch_content)
    
    print("✅ Created patched executor: content_executor_patched.py")
    print("\nTo use the patched version:")
    print("1. Backup original: cp agents/content_executor.py agents/content_executor_original.py")
    print("2. Replace with patch: cp agents/content_executor_patched.py agents/content_executor.py")
    print("3. Test: python execute_test_agent.py")


if __name__ == "__main__":
    analyze_execution_issues()
    patch_executor()
