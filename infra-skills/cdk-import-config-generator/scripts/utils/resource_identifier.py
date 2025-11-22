"""
Resource Identifier Utility

Extracts physical resource identifiers from AWS resource inventory.
Different resource types use different identifiers for CDK import.
"""

from typing import Dict, Any, Optional


class ResourceIdentifier:
    """Utility class to extract resource identifiers"""

    @staticmethod
    def get_identifier(resource: Dict[str, Any], resource_type: str) -> Optional[str]:
        """
        Get the physical resource identifier for CDK import

        Args:
            resource: Resource dictionary from inventory
            resource_type: Type of resource (lambdas, dynamodb, etc.)

        Returns:
            Physical resource identifier or None if not found
        """
        identifier_map = {
            "lambdas": ResourceIdentifier._get_lambda_identifier,
            "dynamodb": ResourceIdentifier._get_dynamodb_identifier,
            "iam_roles": ResourceIdentifier._get_iam_role_identifier,
            "iam_policies": ResourceIdentifier._get_iam_policy_identifier,
            "s3": ResourceIdentifier._get_s3_identifier,
            "eventbridge": ResourceIdentifier._get_eventbridge_identifier,
        }

        getter = identifier_map.get(resource_type)
        if getter:
            return getter(resource)

        return None

    @staticmethod
    def _get_lambda_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get Lambda function identifier (function name)"""
        return resource.get("function_name")

    @staticmethod
    def _get_dynamodb_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get DynamoDB table identifier (table name)"""
        return resource.get("table_name")

    @staticmethod
    def _get_iam_role_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get IAM role identifier (role name)"""
        return resource.get("role_name")

    @staticmethod
    def _get_iam_policy_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get IAM policy identifier (policy ARN)"""
        # For managed policies, use ARN
        return resource.get("policy_arn")

    @staticmethod
    def _get_s3_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get S3 bucket identifier (bucket name)"""
        return resource.get("bucket_name")

    @staticmethod
    def _get_eventbridge_identifier(resource: Dict[str, Any]) -> Optional[str]:
        """Get EventBridge rule identifier (rule name)"""
        return resource.get("rule_name")

    @staticmethod
    def get_resource_name(resource: Dict[str, Any], resource_type: str) -> Optional[str]:
        """
        Get the resource name (used for matching with CDK constructs)

        This is the same as the identifier for most resources
        """
        return ResourceIdentifier.get_identifier(resource, resource_type)

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a resource name for comparison

        Converts to lowercase and replaces special characters
        """
        if not name:
            return ""
        return name.lower().replace("_", "-")
