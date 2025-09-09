"""
Content Management System Services

Business logic services for content generation, workflow execution, and RAG operations.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ContentTemplate, Document, KnowledgeBase, ContentGeneration,
    ContentWorkflow, WorkflowExecution, EmbeddingModel, ContentStatus
)
from .embeddings import rag_system
from .ai_providers import AIProviderManager

User = get_user_model()
logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Service for handling content generation requests"""
    
    def __init__(self, user: User):
        self.user = user
        self.ai_provider = AIProviderManager()
    
    def generate_content(self, generation_request: Dict[str, Any]) -> ContentGeneration:
        """Generate content based on request parameters"""
        try:
            # Create ContentGeneration record
            generation = ContentGeneration.objects.create(
                user=self.user,
                template_id=generation_request.get('template_id'),
                prompt=generation_request['prompt'],
                system_prompt=generation_request.get('system_prompt', ''),
                generation_config=generation_request.get('generation_config', {}),
                knowledge_base_id=generation_request.get('knowledge_base_id'),
                source_system=generation_request.get('source_system', 'api'),
                status=ContentStatus.PENDING
            )
            
            # Process template if provided
            if generation.template:
                variables = generation_request.get('variables', {})
                generation.prompt = generation.template.render_prompt(**variables)
                generation.system_prompt = generation.template.system_prompt
                generation.generation_config.update(generation.template.generation_config)
                generation.save()
            
            # Handle RAG if requested
            if generation_request.get('use_rag', False):
                self._add_rag_context(generation, generation_request)
            
            # Generate content
            self._execute_generation(generation)
            
            # Create document if requested
            if generation_request.get('save_as_document', True) and generation.generated_content:
                generation.create_document()
            
            return generation
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            if 'generation' in locals():
                generation.status = ContentStatus.FAILED
                generation.error_message = str(e)
                generation.save()
            raise
    
    def _add_rag_context(self, generation: ContentGeneration, request: Dict[str, Any]):
        """Add RAG context to generation"""
        try:
            rag_query = request.get('rag_query', generation.prompt)
            knowledge_base = None
            
            if generation.knowledge_base_id:
                knowledge_base = KnowledgeBase.objects.get(
                    id=generation.knowledge_base_id
                )
            
            # Perform RAG retrieval
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            rag_context = loop.run_until_complete(
                rag_system.retrieve_and_generate(
                    query=rag_query,
                    generation_prompt=generation.prompt,
                    knowledge_base=knowledge_base,
                    embedding_model=EmbeddingModel.OPENAI_SMALL,
                    max_results=5,
                    max_context_length=4000
                )
            )
            
            # Update generation with RAG context
            generation.rag_context = rag_context['context']
            generation.save()
            
            # Update system prompt with context
            context_prompt = f"""You have access to the following relevant context from the knowledge base:

{rag_context['context']}

Use this context to inform your response, but don't explicitly mention that you're using a knowledge base unless relevant.

Original system prompt:
{generation.system_prompt}"""
            
            generation.system_prompt = context_prompt
            generation.save()
            
        except Exception as e:
            logger.error(f"RAG context addition failed: {str(e)}")
            # Continue without RAG context
    
    def _execute_generation(self, generation: ContentGeneration):
        """Execute the actual content generation"""
        try:
            start_time = time.time()
            generation.status = ContentStatus.PROCESSING
            generation.save()
            
            # Determine AI provider and model
            if generation.template:
                provider = generation.template.llm_provider
                model = generation.template.llm_model
                config = generation.template.generation_config
            else:
                provider = generation.generation_config.get('llm_provider', 'openai')
                model = generation.generation_config.get('llm_model', 'gpt-4-turbo-preview')
                config = generation.generation_config
            
            # Generate content using AI provider
            result = self.ai_provider.generate_content(
                provider=provider,
                model=model,
                system_prompt=generation.system_prompt,
                user_prompt=generation.prompt,
                config=config
            )
            
            generation_time = int((time.time() - start_time) * 1000)
            
            if result.success:
                generation.generated_content = result.content
                generation.status = ContentStatus.PROCESSED
                generation.generation_time_ms = generation_time
                generation.token_usage = result.token_usage
                generation.generation_cost = Decimal(str(result.cost))
                
                # Update template statistics
                if generation.template:
                    generation.template.update_stats(
                        generation_time=generation_time / 1000.0,
                        success=True
                    )
            else:
                generation.status = ContentStatus.FAILED
                generation.error_message = result.error_message
                
                # Update template statistics
                if generation.template:
                    generation.template.update_stats(
                        generation_time=generation_time / 1000.0,
                        success=False
                    )
            
            generation.save()
            
        except Exception as e:
            logger.error(f"Content generation execution failed: {str(e)}")
            generation.status = ContentStatus.FAILED
            generation.error_message = str(e)
            generation.save()


class WorkflowExecutionService:
    """Service for executing content workflows"""
    
    def __init__(self, user: User):
        self.user = user
        self.generation_service = ContentGenerationService(user)
    
    def execute_workflow(self, workflow: ContentWorkflow, execution_request: Dict[str, Any]) -> WorkflowExecution:
        """Execute a content workflow"""
        try:
            # Create WorkflowExecution record
            execution = WorkflowExecution.objects.create(
                workflow=workflow,
                user=self.user,
                input_data=execution_request['input_data'],
                execution_config=execution_request.get('execution_config', {}),
                websocket_channel=execution_request.get('websocket_channel', ''),
                status=ContentStatus.PENDING,
                started_at=timezone.now()
            )
            
            # Execute workflow steps
            if execution_request.get('async_execution', True):
                # In production, this would be handled by Celery
                self._execute_workflow_async(execution)
            else:
                self._execute_workflow_sync(execution)
            
            return execution
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            if 'execution' in locals():
                execution.status = ContentStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = timezone.now()
                execution.save()
            raise
    
    def _execute_workflow_sync(self, execution: WorkflowExecution):
        """Execute workflow synchronously"""
        try:
            execution.status = ContentStatus.PROCESSING
            execution.save()
            
            workflow_steps = execution.workflow.workflow_steps
            step_results = []
            
            for i, step in enumerate(workflow_steps):
                try:
                    execution.current_step = i
                    execution.progress_percentage = int((i / len(workflow_steps)) * 100)
                    execution.save()
                    
                    # Execute step
                    step_result = self._execute_workflow_step(
                        execution, step, step_results
                    )
                    step_results.append(step_result)
                    
                    # Check for step failure
                    if not step_result.get('success', True):
                        raise Exception(f"Step {i} failed: {step_result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    execution.status = ContentStatus.FAILED
                    execution.error_message = str(e)
                    execution.error_step = i
                    execution.completed_at = timezone.now()
                    execution.save()
                    return
            
            # Workflow completed successfully
            execution.status = ContentStatus.PROCESSED
            execution.progress_percentage = 100
            execution.completed_at = timezone.now()
            execution.step_results = step_results
            execution.final_output = self._aggregate_workflow_results(step_results)
            
            if execution.started_at:
                execution.execution_time_seconds = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
            
            execution.save()
            
            # Update workflow statistics
            workflow = execution.workflow
            workflow.execution_count += 1
            if execution.execution_time_seconds:
                total_time = workflow.avg_execution_time * (workflow.execution_count - 1)
                total_time += execution.execution_time_seconds
                workflow.avg_execution_time = total_time / workflow.execution_count
            
            # Update success rate
            total_success = workflow.success_rate * (workflow.execution_count - 1) + 1
            workflow.success_rate = total_success / workflow.execution_count
            workflow.save()
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            execution.status = ContentStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
    
    def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute workflow asynchronously (placeholder for Celery task)"""
        # In production, this would trigger a Celery task
        # For now, we'll just mark it as processing
        execution.status = ContentStatus.PROCESSING
        execution.save()
    
    def _execute_workflow_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                              previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_type = step.get('type', 'unknown')
        
        try:
            if step_type == 'content_generation':
                return self._execute_generation_step(execution, step, previous_results)
            elif step_type == 'document_processing':
                return self._execute_document_processing_step(execution, step, previous_results)
            elif step_type == 'rag_search':
                return self._execute_rag_search_step(execution, step, previous_results)
            elif step_type == 'template_application':
                return self._execute_template_step(execution, step, previous_results)
            elif step_type == 'data_transformation':
                return self._execute_data_transformation_step(execution, step, previous_results)
            else:
                return {
                    'success': False,
                    'error': f'Unknown step type: {step_type}',
                    'step_name': step.get('name', 'Unknown'),
                    'step_type': step_type
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_name': step.get('name', 'Unknown'),
                'step_type': step_type
            }
    
    def _execute_generation_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                               previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute content generation step"""
        try:
            # Build generation request from step config and previous results
            generation_request = {
                'prompt': self._resolve_template_variables(
                    step.get('prompt', ''), execution.input_data, previous_results
                ),
                'system_prompt': self._resolve_template_variables(
                    step.get('system_prompt', ''), execution.input_data, previous_results
                ),
                'template_id': step.get('template_id'),
                'generation_config': step.get('generation_config', {}),
                'use_rag': step.get('use_rag', False),
                'knowledge_base_id': step.get('knowledge_base_id'),
                'save_as_document': step.get('save_as_document', True),
                'source_system': 'workflow'
            }
            
            # Generate content
            generation = self.generation_service.generate_content(generation_request)
            
            # Add to workflow execution
            execution.generated_content.add(generation)
            
            return {
                'success': generation.status == ContentStatus.PROCESSED,
                'step_name': step.get('name', 'Content Generation'),
                'step_type': 'content_generation',
                'generation_id': str(generation.id),
                'content': generation.generated_content if generation.generated_content else None,
                'error': generation.error_message if generation.error_message else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_name': step.get('name', 'Content Generation'),
                'step_type': 'content_generation'
            }
    
    def _execute_document_processing_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                                        previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute document processing step"""
        # Placeholder for document processing logic
        return {
            'success': True,
            'step_name': step.get('name', 'Document Processing'),
            'step_type': 'document_processing',
            'message': 'Document processing completed'
        }
    
    def _execute_rag_search_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                               previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute RAG search step"""
        try:
            query = self._resolve_template_variables(
                step.get('query', ''), execution.input_data, previous_results
            )
            
            knowledge_base = None
            if step.get('knowledge_base_id'):
                knowledge_base = KnowledgeBase.objects.get(
                    id=step['knowledge_base_id']
                )
            
            # Perform search
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            search_results = loop.run_until_complete(
                rag_system.semantic_search(
                    query=query,
                    knowledge_base=knowledge_base,
                    limit=step.get('limit', 5)
                )
            )
            
            return {
                'success': True,
                'step_name': step.get('name', 'RAG Search'),
                'step_type': 'rag_search',
                'query': query,
                'results_count': len(search_results),
                'results': [
                    {
                        'document_title': result.document_title,
                        'similarity_score': result.similarity_score,
                        'chunk_text': result.chunk_text[:200]
                    }
                    for result in search_results
                ]
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_name': step.get('name', 'RAG Search'),
                'step_type': 'rag_search'
            }
    
    def _execute_template_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                             previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute template application step"""
        try:
            template = ContentTemplate.objects.get(id=step['template_id'])
            variables = self._resolve_template_variables(
                step.get('variables', {}), execution.input_data, previous_results
            )
            
            rendered_prompt = template.render_prompt(**variables)
            
            return {
                'success': True,
                'step_name': step.get('name', 'Template Application'),
                'step_type': 'template_application',
                'template_name': template.display_name,
                'rendered_prompt': rendered_prompt
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_name': step.get('name', 'Template Application'),
                'step_type': 'template_application'
            }
    
    def _execute_data_transformation_step(self, execution: WorkflowExecution, step: Dict[str, Any], 
                                        previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute data transformation step"""
        # Placeholder for data transformation logic
        return {
            'success': True,
            'step_name': step.get('name', 'Data Transformation'),
            'step_type': 'data_transformation',
            'message': 'Data transformation completed'
        }
    
    def _resolve_template_variables(self, template: Any, input_data: Dict[str, Any], 
                                   previous_results: List[Dict[str, Any]]) -> Any:
        """Resolve template variables from input data and previous step results"""
        if isinstance(template, str):
            # Simple string interpolation
            resolved = template
            
            # Replace input data variables
            for key, value in input_data.items():
                resolved = resolved.replace(f'{{input.{key}}}', str(value))
            
            # Replace previous step results
            for i, result in enumerate(previous_results):
                for key, value in result.items():
                    if isinstance(value, (str, int, float)):
                        resolved = resolved.replace(f'{{step{i}.{key}}}', str(value))
            
            return resolved
        
        elif isinstance(template, dict):
            # Recursively resolve dictionary values
            return {
                key: self._resolve_template_variables(value, input_data, previous_results)
                for key, value in template.items()
            }
        
        elif isinstance(template, list):
            # Recursively resolve list items
            return [
                self._resolve_template_variables(item, input_data, previous_results)
                for item in template
            ]
        
        else:
            return template
    
    def _aggregate_workflow_results(self, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from all workflow steps"""
        generated_content = []
        documents = []
        search_results = []
        
        for result in step_results:
            if result.get('step_type') == 'content_generation' and result.get('content'):
                generated_content.append({
                    'step_name': result.get('step_name'),
                    'content': result['content'],
                    'generation_id': result.get('generation_id')
                })
            
            elif result.get('step_type') == 'rag_search' and result.get('results'):
                search_results.extend(result['results'])
        
        return {
            'generated_content': generated_content,
            'documents': documents,
            'search_results': search_results,
            'total_steps': len(step_results),
            'successful_steps': len([r for r in step_results if r.get('success')]),
            'execution_summary': f"Workflow completed {len(generated_content)} content generations"
        }