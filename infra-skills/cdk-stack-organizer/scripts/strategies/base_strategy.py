"""
Base Strategy for Stack Organization

Defines the interface and common functionality for all organization strategies.
"""

from typing import Dict, List, Any
from pathlib import Path
from abc import ABC, abstractmethod


class StackPlan:
    """Represents the plan for organizing constructs into stacks"""

    def __init__(self):
        # Stack name -> List of constructs
        self.stacks: Dict[str, List[Dict[str, Any]]] = {}
        # Stack name -> List of dependent stack names
        self.dependencies: Dict[str, List[str]] = {}

    def add_stack(self, stack_name: str):
        """Add a new stack"""
        if stack_name not in self.stacks:
            self.stacks[stack_name] = []
            self.dependencies[stack_name] = []

    def add_construct_to_stack(self, stack_name: str, construct: Dict[str, Any]):
        """Add a construct to a stack"""
        if stack_name not in self.stacks:
            self.add_stack(stack_name)
        self.stacks[stack_name].append(construct)

    def add_dependency(self, stack_name: str, depends_on: str):
        """Add a dependency between stacks"""
        if stack_name not in self.dependencies:
            self.dependencies[stack_name] = []
        if depends_on not in self.dependencies[stack_name]:
            self.dependencies[stack_name].append(depends_on)


class BaseStrategy(ABC):
    """Base class for all organization strategies"""

    def __init__(self, inventory, cross_stack_refs: bool = True):
        """
        Initialize the strategy

        Args:
            inventory: ConstructInventory object containing all constructs
            cross_stack_refs: Whether to enable cross-stack references
        """
        self.inventory = inventory
        self.cross_stack_refs = cross_stack_refs

    @abstractmethod
    def organize(self) -> StackPlan:
        """
        Organize constructs into stacks

        Returns:
            StackPlan object with stack organization
        """
        pass

    def _extract_construct_info(self, ts_file: Path, resource_type: str) -> Dict[str, Any]:
        """
        Extract information from a construct TypeScript file

        Args:
            ts_file: Path to the TypeScript construct file
            resource_type: Type of resource (lambdas, dynamodb, etc.)

        Returns:
            Dictionary with construct information
        """
        content = ts_file.read_text()

        # Extract class name
        class_name = self._extract_class_name(content)

        # Extract function/resource name
        resource_name = ts_file.stem  # File name without extension

        # Extract original resource name (from comments or code)
        original_name = self._extract_original_name(content, resource_type)

        # Extract tags (if available in comments)
        tags = self._extract_tags(content)

        # Determine service/application name
        service_name = self._infer_service_name(resource_name, tags)

        return {
            "name": resource_name,
            "class_name": class_name,
            "original_name": original_name,
            "type": resource_type,
            "file_path": ts_file,
            "tags": tags,
            "service": service_name,
            "content": content,
        }

    def _extract_class_name(self, content: str) -> str:
        """Extract the exported class name from TypeScript content"""
        for line in content.split("\n"):
            if "export class" in line:
                # Extract class name: "export class MyClass {" -> "MyClass"
                parts = line.split("export class")[1].strip().split()
                if parts:
                    return parts[0].rstrip(" {")
        return "UnknownClass"

    def _extract_original_name(self, content: str, resource_type: str) -> str:
        """Extract the original AWS resource name from the construct"""
        # Look for functionName, tableName, bucketName, etc.
        name_keys = {
            "lambdas": "functionName:",
            "dynamodb": "tableName:",
            "s3": "bucketName:",
            "iam": "roleName:",
            "eventbridge": "ruleName:",
        }

        key = name_keys.get(resource_type, "")
        if key:
            for line in content.split("\n"):
                if key in line:
                    # Extract value: "functionName: 'my-function'," -> "my-function"
                    value = line.split(key)[1].strip().strip("',\"")
                    if value:
                        return value

        return ""

    def _extract_tags(self, content: str) -> Dict[str, str]:
        """Extract tags from comments or metadata in the construct"""
        tags = {}

        # Look for tags in comments (e.g., "// Tags: environment=prod, team=backend")
        for line in content.split("\n"):
            if "// Tags:" in line or "// tags:" in line:
                tag_str = line.split("Tags:")[1].strip()
                for tag_pair in tag_str.split(","):
                    if "=" in tag_pair:
                        key, value = tag_pair.strip().split("=", 1)
                        tags[key.strip()] = value.strip()

        return tags

    def _infer_service_name(self, resource_name: str, tags: Dict[str, str]) -> str:
        """
        Infer service/application name from resource name or tags

        Common patterns:
        - service-name-function -> service-name
        - app-environment-resource -> app
        - prefixed-resource-name -> prefixed
        """
        # First check tags
        if "service" in tags:
            return tags["service"]
        if "application" in tags:
            return tags["application"]
        if "app" in tags:
            return tags["app"]

        # Infer from resource name
        # Split by hyphens and take the first meaningful part
        parts = resource_name.split("-")
        if len(parts) > 1:
            # Common patterns:
            # - cs-lambda-registration -> cs
            # - order-processor-function -> order
            # - myapp-dev-lambda -> myapp
            return parts[0]

        return "shared"

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase for stack names"""
        # Replace hyphens and underscores with spaces, then title case
        words = text.replace("-", " ").replace("_", " ").split()
        return "".join(word.capitalize() for word in words)

    def _analyze_dependencies(self, plan: StackPlan) -> StackPlan:
        """
        Analyze dependencies between stacks based on construct dependencies

        This is a basic implementation. Override in specific strategies for
        more sophisticated dependency analysis.
        """
        # For MVP, we'll use a simple heuristic:
        # - IAM stack is always a dependency (if it exists)
        # - Data layer (DynamoDB, S3) comes before compute layer (Lambda)

        stack_names = list(plan.stacks.keys())

        # Define dependency order by layer
        layer_order = {
            "iam": 0,
            "data": 1,
            "compute": 2,
            "api": 3,
        }

        # Determine layer for each stack
        stack_layers = {}
        for stack_name in stack_names:
            stack_lower = stack_name.lower()
            if "iam" in stack_lower:
                stack_layers[stack_name] = "iam"
            elif "data" in stack_lower or "storage" in stack_lower:
                stack_layers[stack_name] = "data"
            elif "compute" in stack_lower or "lambda" in stack_lower:
                stack_layers[stack_name] = "compute"
            elif "api" in stack_lower or "event" in stack_lower:
                stack_layers[stack_name] = "api"
            else:
                stack_layers[stack_name] = "compute"  # Default

        # Add dependencies based on layer order
        for stack_name in stack_names:
            current_layer = stack_layers[stack_name]
            current_order = layer_order.get(current_layer, 99)

            for other_stack in stack_names:
                if other_stack == stack_name:
                    continue

                other_layer = stack_layers[other_stack]
                other_order = layer_order.get(other_layer, 99)

                # If other stack has lower order, it's a dependency
                if other_order < current_order:
                    plan.add_dependency(stack_name, other_stack)

        return plan
