"""
Dependency Detector

Detects and analyzes dependencies between AWS resources.
"""

from typing import List, Dict, Any
import re
import json


class DependencyDetector:
    """Detects dependencies between discovered AWS resources."""

    def __init__(self):
        """Initialize dependency detector."""
        self.dependencies = []

    def detect_dependencies(
        self,
        lambdas: List[Dict[str, Any]],
        dynamodb_tables: List[Dict[str, Any]],
        iam_roles: List[Dict[str, Any]],
        iam_policies: List[Dict[str, Any]],
        s3_buckets: List[Dict[str, Any]],
        eventbridge_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect dependencies between all resources.

        Args:
            lambdas: List of Lambda functions
            dynamodb_tables: List of DynamoDB tables
            iam_roles: List of IAM roles
            iam_policies: List of IAM policies
            s3_buckets: List of S3 buckets
            eventbridge_rules: List of EventBridge rules

        Returns:
            List of dependency relationships
        """
        print("\n🔗 Detecting resource dependencies...")

        self.dependencies = []

        # Create lookup maps for faster searching
        table_names = {table['table_name'] for table in dynamodb_tables}
        table_arns = {table['table_arn'] for table in dynamodb_tables}
        bucket_names = {bucket['bucket_name'] for bucket in s3_buckets}
        bucket_arns = {bucket['bucket_arn'] for bucket in s3_buckets}
        role_arns = {role['role_arn']: role for role in iam_roles}

        # Detect Lambda dependencies
        for lambda_func in lambdas:
            self._detect_lambda_dependencies(
                lambda_func,
                table_names,
                table_arns,
                bucket_names,
                bucket_arns,
                role_arns
            )

        # Detect EventBridge dependencies
        for rule in eventbridge_rules:
            self._detect_eventbridge_dependencies(rule, lambdas)

        # Detect IAM dependencies
        for role in iam_roles:
            self._detect_iam_dependencies(role, iam_policies)

        print(f"  ✓ Detected {len(self.dependencies)} dependencies")

        return self.dependencies

    def _detect_lambda_dependencies(
        self,
        lambda_func: Dict[str, Any],
        table_names: set,
        table_arns: set,
        bucket_names: set,
        bucket_arns: set,
        role_arns: Dict[str, Dict[str, Any]]
    ):
        """Detect dependencies from a Lambda function."""
        function_arn = lambda_func['function_arn']
        function_name = lambda_func['function_name']

        # Lambda → IAM Role
        if lambda_func.get('iam_role_arn'):
            role_arn = lambda_func['iam_role_arn']
            if role_arn in role_arns:
                self._add_dependency(
                    source=function_arn,
                    target=role_arn,
                    relationship='lambda_uses_role',
                    evidence='Lambda execution role from function configuration'
                )

                # Check role's policies for resource permissions
                role = role_arns[role_arn]
                self._detect_lambda_resource_usage_from_role(
                    function_arn,
                    role,
                    table_names,
                    table_arns,
                    bucket_names,
                    bucket_arns
                )

        # Lambda → DynamoDB (from environment variables)
        env_vars = lambda_func.get('environment_variables', {})
        for var_name, var_value in env_vars.items():
            # Check for DynamoDB table names in env vars
            if var_value in table_names:
                # Try to find the table ARN
                matching_arn = next((arn for arn in table_arns if var_value in arn), None)
                if matching_arn:
                    self._add_dependency(
                        source=function_arn,
                        target=matching_arn,
                        relationship='lambda_uses_table',
                        evidence=f'Environment variable {var_name}={var_value}'
                    )

            # Check for S3 bucket names in env vars
            if var_value in bucket_names:
                matching_arn = next((arn for arn in bucket_arns if var_value in arn), None)
                if matching_arn:
                    self._add_dependency(
                        source=function_arn,
                        target=matching_arn,
                        relationship='lambda_uses_bucket',
                        evidence=f'Environment variable {var_name}={var_value}'
                    )

    def _detect_lambda_resource_usage_from_role(
        self,
        function_arn: str,
        role: Dict[str, Any],
        table_names: set,
        table_arns: set,
        bucket_names: set,
        bucket_arns: set
    ):
        """Detect resource usage from Lambda's IAM role policies."""
        # Check inline policies
        for inline_policy in role.get('inline_policies', []):
            policy_doc = inline_policy.get('policy_document', {})
            self._scan_policy_for_resources(
                function_arn,
                policy_doc,
                table_names,
                table_arns,
                bucket_names,
                bucket_arns,
                f"Inline policy {inline_policy['policy_name']}"
            )

        # Note: We don't scan attached managed policies here because we'd need
        # to fetch them separately. That's a potential enhancement for v1.1+

    def _scan_policy_for_resources(
        self,
        function_arn: str,
        policy_doc: Dict[str, Any],
        table_names: set,
        table_arns: set,
        bucket_names: set,
        bucket_arns: set,
        evidence_source: str
    ):
        """Scan IAM policy document for resource references."""
        if not policy_doc or 'Statement' not in policy_doc:
            return

        for statement in policy_doc['Statement']:
            if statement.get('Effect') != 'Allow':
                continue

            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]

            resources = statement.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]

            # Check for DynamoDB permissions
            dynamodb_actions = [a for a in actions if 'dynamodb' in a.lower()]
            if dynamodb_actions:
                for resource in resources:
                    # Check if resource is a DynamoDB table ARN
                    if resource in table_arns:
                        self._add_dependency(
                            source=function_arn,
                            target=resource,
                            relationship='lambda_uses_table',
                            evidence=f'{evidence_source}: Actions {dynamodb_actions}'
                        )
                    # Check if resource contains a table name
                    else:
                        for table_name in table_names:
                            if table_name in resource:
                                matching_arn = next((arn for arn in table_arns if table_name in arn), None)
                                if matching_arn:
                                    self._add_dependency(
                                        source=function_arn,
                                        target=matching_arn,
                                        relationship='lambda_uses_table',
                                        evidence=f'{evidence_source}: Actions {dynamodb_actions}'
                                    )

            # Check for S3 permissions
            s3_actions = [a for a in actions if 's3:' in a.lower()]
            if s3_actions:
                for resource in resources:
                    # Check if resource is an S3 bucket ARN
                    if resource in bucket_arns:
                        self._add_dependency(
                            source=function_arn,
                            target=resource,
                            relationship='lambda_uses_bucket',
                            evidence=f'{evidence_source}: Actions {s3_actions}'
                        )
                    # Check if resource contains a bucket name
                    else:
                        for bucket_name in bucket_names:
                            if bucket_name in resource:
                                matching_arn = next((arn for arn in bucket_arns if bucket_name in arn), None)
                                if matching_arn:
                                    self._add_dependency(
                                        source=function_arn,
                                        target=matching_arn,
                                        relationship='lambda_uses_bucket',
                                        evidence=f'{evidence_source}: Actions {s3_actions}'
                                    )

    def _detect_eventbridge_dependencies(
        self,
        rule: Dict[str, Any],
        lambdas: List[Dict[str, Any]]
    ):
        """Detect dependencies from EventBridge rules."""
        rule_arn = rule['rule_arn']

        # Create Lambda ARN lookup
        lambda_arns = {lam['function_arn'] for lam in lambdas}

        # EventBridge → Lambda (from targets)
        for target in rule.get('targets', []):
            target_arn = target['arn']
            if target_arn in lambda_arns:
                self._add_dependency(
                    source=rule_arn,
                    target=target_arn,
                    relationship='eventbridge_triggers_lambda',
                    evidence=f'Rule target: {target["id"]}'
                )

    def _detect_iam_dependencies(
        self,
        role: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ):
        """Detect IAM role to policy dependencies."""
        role_arn = role['role_arn']

        # Create policy ARN lookup
        policy_arns = {policy['policy_arn'] for policy in policies}

        # Role → Managed Policies
        for attached_policy in role.get('attached_managed_policies', []):
            policy_arn = attached_policy['policy_arn']
            if policy_arn in policy_arns:
                self._add_dependency(
                    source=role_arn,
                    target=policy_arn,
                    relationship='role_uses_policy',
                    evidence=f'Attached managed policy: {attached_policy["policy_name"]}'
                )

    def _add_dependency(
        self,
        source: str,
        target: str,
        relationship: str,
        evidence: str
    ):
        """Add a dependency to the list."""
        # Check for duplicates
        for dep in self.dependencies:
            if (dep['source'] == source and
                dep['target'] == target and
                dep['relationship'] == relationship):
                return  # Already exists

        self.dependencies.append({
            'source': source,
            'target': target,
            'relationship': relationship,
            'evidence': evidence
        })

    def get_dependencies_for_resource(self, resource_arn: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all dependencies for a specific resource.

        Args:
            resource_arn: ARN of the resource

        Returns:
            Dictionary with 'outbound' and 'inbound' dependency lists
        """
        outbound = []
        inbound = []

        for dep in self.dependencies:
            if dep['source'] == resource_arn:
                outbound.append(dep)
            if dep['target'] == resource_arn:
                inbound.append(dep)

        return {
            'outbound': outbound,
            'inbound': inbound
        }
