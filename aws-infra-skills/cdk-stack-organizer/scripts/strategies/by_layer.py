"""
By Layer Organization Strategy

Organizes constructs by architectural layer:
- IAM Stack: IAM roles and policies
- Data Stack: DynamoDB tables, S3 buckets
- Compute Stack: Lambda functions
- API Stack: API Gateway, EventBridge rules
"""

from .base_strategy import BaseStrategy, StackPlan


class ByLayerStrategy(BaseStrategy):
    """Organize constructs by architectural layer"""

    def organize(self) -> StackPlan:
        """
        Organize constructs into stacks by architectural layer

        Layers:
        - IAM: IAM roles and policies
        - Data: DynamoDB, S3
        - Compute: Lambda
        - API/Events: EventBridge, API Gateway
        """
        plan = StackPlan()

        # Define layer mappings
        layer_mapping = {
            "iam": "IamStack",
            "dynamodb": "DataStack",
            "s3": "DataStack",
            "lambdas": "ComputeStack",
            "eventbridge": "ApiStack",
        }

        # Process each resource type
        for resource_type, construct_files in self.inventory.constructs.items():
            # Determine which stack this resource type belongs to
            stack_name = layer_mapping.get(resource_type, "SharedStack")

            # Process each construct file
            for ts_file in construct_files:
                construct_info = self._extract_construct_info(ts_file, resource_type)
                plan.add_construct_to_stack(stack_name, construct_info)

        # Analyze and add dependencies
        plan = self._analyze_dependencies(plan)

        return plan
