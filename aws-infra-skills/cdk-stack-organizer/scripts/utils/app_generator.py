"""
App Generator Utility

Generates the CDK app entry point (bin/app.ts).
"""

from typing import Dict, List, Any


class AppGenerator:
    """Generate CDK app entry point (bin/app.ts)"""

    def __init__(self, cdk_version: str = "2.0.0", stack_prefix: str = ""):
        self.cdk_version = cdk_version
        self.stack_prefix = stack_prefix

    def generate_app(self, stack_plan) -> str:
        """
        Generate the app entry point file

        Args:
            stack_plan: The complete stack plan

        Returns:
            TypeScript code for bin/app.ts
        """
        lines = []

        # Shebang and imports
        lines.append("#!/usr/bin/env node")
        lines.append("import 'source-map-support/register';")
        lines.append("import * as cdk from 'aws-cdk-lib';")
        lines.append("")

        # Import stack classes
        for stack_name in stack_plan.stacks.keys():
            full_stack_name = (
                f"{self.stack_prefix}{stack_name}" if self.stack_prefix else stack_name
            )
            stack_file = stack_name.lower()
            lines.append(
                f"import {{ {full_stack_name} }} from '../lib/{stack_file}';"
            )

        lines.append("")

        # Create app
        lines.append("const app = new cdk.App();")
        lines.append("")

        # Determine deployment order based on dependencies
        ordered_stacks = self._topological_sort(stack_plan)

        # Instantiate stacks in order
        lines.append("// Stacks are instantiated in dependency order")
        lines.append("")

        stack_instances = {}  # Track stack instances for dependency passing

        for stack_name in ordered_stacks:
            full_stack_name = (
                f"{self.stack_prefix}{stack_name}" if self.stack_prefix else stack_name
            )
            stack_id = full_stack_name
            instance_name = self._to_camel_case(stack_name)

            dependencies = stack_plan.dependencies.get(stack_name, [])

            if dependencies:
                # Stack has dependencies, pass them as props
                lines.append(f"const {instance_name} = new {full_stack_name}(app, '{stack_id}', {{")
                lines.append("  env: {")
                lines.append("    account: process.env.CDK_DEFAULT_ACCOUNT,")
                lines.append("    region: process.env.CDK_DEFAULT_REGION,")
                lines.append("  },")

                # Add dependent stacks
                for dep_stack in dependencies:
                    dep_instance = self._to_camel_case(dep_stack)
                    lines.append(f"  {dep_stack.lower()}: {dep_instance},")

                lines.append("});")
            else:
                # Stack has no dependencies
                lines.append(f"const {instance_name} = new {full_stack_name}(app, '{stack_id}', {{")
                lines.append("  env: {")
                lines.append("    account: process.env.CDK_DEFAULT_ACCOUNT,")
                lines.append("    region: process.env.CDK_DEFAULT_REGION,")
                lines.append("  },")
                lines.append("});")

            stack_instances[stack_name] = instance_name
            lines.append("")

        # Add stack dependencies for CDK deployment order
        lines.append("// Define stack dependencies for deployment order")
        for stack_name in ordered_stacks:
            dependencies = stack_plan.dependencies.get(stack_name, [])
            if dependencies:
                instance_name = stack_instances[stack_name]
                for dep_stack in dependencies:
                    dep_instance = stack_instances[dep_stack]
                    lines.append(f"{instance_name}.addDependency({dep_instance});")
        lines.append("")

        # Synth
        lines.append("app.synth();")

        return "\n".join(lines)

    def _topological_sort(self, stack_plan) -> List[str]:
        """
        Topologically sort stacks based on dependencies

        Returns list of stack names in deployment order
        """
        # Simple topological sort using Kahn's algorithm
        in_degree = {}
        adj_list = {}

        # Initialize
        for stack_name in stack_plan.stacks.keys():
            in_degree[stack_name] = 0
            adj_list[stack_name] = []

        # Build adjacency list and calculate in-degrees
        for stack_name, dependencies in stack_plan.dependencies.items():
            for dep in dependencies:
                adj_list[dep].append(stack_name)
                in_degree[stack_name] += 1

        # Find all nodes with no incoming edges
        queue = [stack for stack, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort queue for deterministic output
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            # Reduce in-degree for dependent stacks
            for dependent in adj_list[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(result) != len(stack_plan.stacks):
            # Cycle detected, return original order
            print("Warning: Circular dependency detected, using original order")
            return list(stack_plan.stacks.keys())

        return result

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        words = text.replace("-", " ").replace("_", " ").split()
        if not words:
            return text
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])
