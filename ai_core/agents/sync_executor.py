"""
Synchronous Wrapper for Agent Execution
========================================
This allows synchronous code to call async agents
"""

import asyncio
from typing import Dict, Any, Optional
from ai_core.agents.concrete_executor import ConcreteAgentExecutor

class SyncAgentExecutor:
    """Synchronous wrapper for async agent execution"""

    def __init__(self):
        self.executor = ConcreteAgentExecutor()

    def execute(self, agent_name: str, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute an agent synchronously

        Args:
            agent_name: Name of the agent to execute
            task_description: Description of the task
            context: Optional context dictionary

        Returns:
            Execution result dictionary
        """
        task = {
            "description": task_description,
            "context": context or {},
            "type": "general"
        }

        # Handle event loop properly
        try:
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(
                    self.executor.execute_agent(agent_name, task)
                )
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(
                    self.executor.execute_agent(agent_name, task)
                )
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent_name
            }

    def execute_content(self, content_request: str, max_length: int = 500) -> Dict[str, Any]:
        """Execute content generation agent"""
        request = {
            "prompt": content_request,
            "max_length": max_length,
            "type": "content_generation"
        }

        try:
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(
                    self.executor.execute_content_agent("content_creator", request)
                )
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(
                    self.executor.execute_content_agent("content_creator", request)
                )
        except Exception as e:
            return {"success": False, "error": str(e)}