"""
By Service Organization Strategy

Organizes constructs by service/application name.
Groups all resources belonging to the same service together.
"""

from collections import defaultdict
from .base_strategy import BaseStrategy, StackPlan


class ByServiceStrategy(BaseStrategy):
    """Organize constructs by service/application"""

    def organize(self) -> StackPlan:
        """
        Organize constructs into stacks by service name

        Service names are inferred from:
        1. Tags (service, application, app)
        2. Resource naming patterns (prefix before first hyphen)
        3. Default to "shared" for ungrouped resources
        """
        plan = StackPlan()

        # Group constructs by service
        service_groups = defaultdict(list)

        # Process each resource type
        for resource_type, construct_files in self.inventory.constructs.items():
            for ts_file in construct_files:
                construct_info = self._extract_construct_info(ts_file, resource_type)
                service_name = construct_info["service"]
                service_groups[service_name].append(construct_info)

        # Create a stack for each service
        for service_name, constructs in service_groups.items():
            # Convert service name to PascalCase for stack name
            stack_name = self._to_pascal_case(service_name) + "Stack"

            for construct in constructs:
                plan.add_construct_to_stack(stack_name, construct)

        # Analyze and add dependencies
        plan = self._analyze_dependencies(plan)

        return plan

    def _analyze_dependencies(self, plan: StackPlan) -> StackPlan:
        """
        For service-based organization, we need to detect cross-service dependencies

        For MVP, we'll use a simple heuristic:
        - If there's a SharedStack, other stacks may depend on it
        """
        stack_names = list(plan.stacks.keys())

        # If there's a SharedStack, make other stacks depend on it
        if "SharedStack" in stack_names:
            for stack_name in stack_names:
                if stack_name != "SharedStack":
                    plan.add_dependency(stack_name, "SharedStack")

        return plan
