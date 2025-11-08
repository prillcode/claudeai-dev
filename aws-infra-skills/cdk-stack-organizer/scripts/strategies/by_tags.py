"""
By Tags Organization Strategy

Organizes constructs based on AWS resource tags.
Groups resources with matching tag values together.
"""

from collections import defaultdict
from .base_strategy import BaseStrategy, StackPlan


class ByTagsStrategy(BaseStrategy):
    """Organize constructs by resource tags"""

    def organize(self) -> StackPlan:
        """
        Organize constructs into stacks by tags

        Strategy:
        1. Look for common grouping tags (environment, project, team, application)
        2. Group resources with matching tag values
        3. Resources without tags go to SharedStack
        """
        plan = StackPlan()

        # Priority order for tag keys (first match wins)
        tag_priority = ["project", "application", "team", "service", "environment"]

        # Group constructs by tag value
        tag_groups = defaultdict(list)

        # Process each resource type
        for resource_type, construct_files in self.inventory.constructs.items():
            for ts_file in construct_files:
                construct_info = self._extract_construct_info(ts_file, resource_type)
                tags = construct_info["tags"]

                # Find the first matching tag from priority list
                group_key = None
                for tag_key in tag_priority:
                    if tag_key in tags:
                        group_key = f"{tag_key}-{tags[tag_key]}"
                        break

                # If no matching tag, use "shared"
                if not group_key:
                    group_key = "shared"

                tag_groups[group_key].append(construct_info)

        # Create a stack for each tag group
        for group_key, constructs in tag_groups.items():
            # Convert group key to PascalCase for stack name
            stack_name = self._to_pascal_case(group_key) + "Stack"

            for construct in constructs:
                plan.add_construct_to_stack(stack_name, construct)

        # Analyze and add dependencies
        plan = self._analyze_dependencies(plan)

        return plan

    def _analyze_dependencies(self, plan: StackPlan) -> StackPlan:
        """
        For tag-based organization, SharedStack should be a base dependency
        """
        stack_names = list(plan.stacks.keys())

        # If there's a SharedStack, make other stacks depend on it
        if "SharedStack" in stack_names:
            for stack_name in stack_names:
                if stack_name != "SharedStack":
                    plan.add_dependency(stack_name, "SharedStack")

        return plan
