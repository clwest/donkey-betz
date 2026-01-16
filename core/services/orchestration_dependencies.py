"""
Orchestration Dependency Resolver
=================================

Session 764: Resolves step dependencies for parallel and dependency-based execution.
"""

import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class DependencyResolver:
    """
    Resolves step dependencies for workflow execution ordering.

    Used for dependency-based execution mode to determine
    which steps can run in parallel and which must wait.
    """

    def get_ready_steps(
        self,
        steps: List,
        completed_outputs: Dict[str, Any]
    ) -> List:
        """
        Get steps that are ready to execute.

        A step is ready if:
        1. It has no dependencies, OR
        2. All its dependencies are in completed_outputs

        Args:
            steps: List of CustomWorkflowStep instances
            completed_outputs: Dict mapping step order -> output

        Returns:
            List of steps ready to execute
        """
        ready = []
        completed_orders = set(completed_outputs.keys())

        for step in steps:
            # Skip already completed
            if str(step.order) in completed_orders:
                continue

            # Check dependencies
            deps = step.depends_on_steps or []
            if not deps:
                # No dependencies - ready to go
                ready.append(step)
            else:
                # Check if all deps are satisfied
                deps_met = all(str(d) in completed_orders for d in deps)
                if deps_met:
                    ready.append(step)

        return ready

    def get_blocked_steps(self, failed_step, all_steps: List) -> List:
        """
        Get steps that are blocked by a failed step.

        Args:
            failed_step: The step that failed
            all_steps: All workflow steps

        Returns:
            List of steps that depend on the failed step (directly or transitively)
        """
        blocked = []
        failed_order = failed_step.order

        # Find direct dependents
        direct_dependents: Set[int] = set()
        for step in all_steps:
            deps = step.depends_on_steps or []
            if failed_order in deps:
                direct_dependents.add(step.order)
                blocked.append(step)

        # Find transitive dependents (steps that depend on direct dependents)
        found_new = True
        while found_new:
            found_new = False
            for step in all_steps:
                if step.order in direct_dependents:
                    continue
                deps = step.depends_on_steps or []
                if any(d in direct_dependents for d in deps):
                    direct_dependents.add(step.order)
                    blocked.append(step)
                    found_new = True

        return blocked

    def build_execution_order(self, steps: List) -> List[List]:
        """
        Build execution order as layers of parallelizable steps.

        Returns:
            List of lists, where each inner list contains steps
            that can be executed in parallel
        """
        if not steps:
            return []

        completed: Set[str] = set()
        layers = []

        remaining = list(steps)

        while remaining:
            # Find steps ready in this layer
            layer = []
            for step in remaining:
                deps = step.depends_on_steps or []
                if all(str(d) in completed for d in deps):
                    layer.append(step)

            if not layer:
                # Circular dependency or missing step
                logger.error("Could not resolve dependencies - possible cycle")
                # Add remaining steps anyway to avoid infinite loop
                layers.append(remaining)
                break

            layers.append(layer)

            # Mark layer as completed
            for step in layer:
                completed.add(str(step.order))

            # Remove from remaining
            remaining = [s for s in remaining if s not in layer]

        return layers

    def validate_dependencies(self, steps: List) -> List[str]:
        """
        Validate that all dependencies reference valid steps.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        step_orders = {step.order for step in steps}

        for step in steps:
            deps = step.depends_on_steps or []
            for dep in deps:
                if dep not in step_orders:
                    errors.append(
                        f"Step {step.order} depends on non-existent step {dep}"
                    )
                if dep >= step.order:
                    errors.append(
                        f"Step {step.order} depends on later step {dep}"
                    )
                if dep == step.order:
                    errors.append(
                        f"Step {step.order} depends on itself"
                    )

        return errors


# Singleton instance
dependency_resolver = DependencyResolver()
