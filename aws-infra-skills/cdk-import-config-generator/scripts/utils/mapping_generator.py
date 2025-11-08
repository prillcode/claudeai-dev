"""
Mapping Generator

Generates resource identifier mappings for CDK import.
Maps CDK logical IDs to AWS physical resource identifiers.
"""

from typing import Dict, List, Any
from .resource_identifier import ResourceIdentifier


class MappingGenerator:
    """Generate resource identifier mappings for CDK import"""

    def __init__(
        self,
        org_metadata: Dict[str, Any],
        resource_inventory: Dict[str, List[Dict[str, Any]]],
    ):
        self.org_metadata = org_metadata
        self.resource_inventory = resource_inventory
        self.identifier = ResourceIdentifier()

    def generate_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Generate resource mappings for all stacks

        Returns:
            Dictionary mapping stack names to resource mappings
            Format: {
                "StackName": {
                    "LogicalID": "physical-resource-id"
                }
            }
        """
        mappings = {}

        stacks = self.org_metadata.get("stacks", {})

        for stack_name, stack_info in stacks.items():
            constructs = stack_info.get("constructs", [])

            if constructs:
                stack_mappings = self._generate_stack_mappings(constructs)
                if stack_mappings:
                    mappings[stack_name] = stack_mappings

        return mappings

    def _generate_stack_mappings(
        self, constructs: List[str]
    ) -> Dict[str, str]:
        """
        Generate mappings for constructs in a stack

        Args:
            constructs: List of construct names in the stack

        Returns:
            Dictionary mapping logical IDs to physical resource IDs
        """
        mappings = {}

        for construct_name in constructs:
            # Try to find matching resource in inventory
            resource_info = self._find_resource(construct_name)

            if resource_info:
                resource_type = resource_info["type"]
                resource_data = resource_info["data"]

                # Get physical identifier for this resource
                identifier = self.identifier.get_identifier(
                    resource_data, resource_type
                )

                if identifier:
                    # Convert construct name to LogicalID (PascalCase)
                    logical_id = self._to_logical_id(construct_name)
                    mappings[logical_id] = identifier

        return mappings

    def _find_resource(self, construct_name: str) -> Dict[str, Any] | None:
        """
        Find a resource in the inventory by name

        Args:
            construct_name: Name of the construct (from organized stack)

        Returns:
            Dictionary with 'type' and 'data' keys, or None if not found
        """
        # Normalize the construct name for comparison
        normalized_name = self.identifier.normalize_name(construct_name)

        # Search in each resource type
        for resource_type, resources in self.resource_inventory.items():
            for resource in resources:
                resource_name = self.identifier.get_resource_name(
                    resource, resource_type
                )

                if resource_name:
                    normalized_resource_name = self.identifier.normalize_name(
                        resource_name
                    )

                    if normalized_name == normalized_resource_name:
                        return {"type": resource_type, "data": resource}

        return None

    def _to_logical_id(self, construct_name: str) -> str:
        """
        Convert construct name to CDK logical ID (PascalCase)

        Args:
            construct_name: Name like "my-function" or "my_function"

        Returns:
            Logical ID like "MyFunction"
        """
        # Split by hyphens and underscores
        words = construct_name.replace("-", " ").replace("_", " ").split()

        # Capitalize each word and join
        return "".join(word.capitalize() for word in words)
