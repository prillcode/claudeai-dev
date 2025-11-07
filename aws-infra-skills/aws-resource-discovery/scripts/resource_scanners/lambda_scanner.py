"""
Lambda Scanner

Discovers AWS Lambda functions with complete configurations.
"""

from typing import List, Dict, Any
from botocore.exceptions import ClientError
import time


class LambdaScanner:
    """Scans AWS Lambda functions."""

    def __init__(self, client_manager, resource_filter):
        """
        Initialize Lambda scanner.

        Args:
            client_manager: AWSClientManager instance
            resource_filter: ResourceFilter instance
        """
        self.client_manager = client_manager
        self.resource_filter = resource_filter
        self.lambda_client = client_manager.get_client('lambda')

    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for Lambda functions.

        Returns:
            List of Lambda function dictionaries with complete configurations
        """
        print("\n🔍 Scanning Lambda functions...")

        functions = []
        try:
            # List all functions with pagination
            paginator = self.lambda_client.get_paginator('list_functions')
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for function in page['Functions']:
                    function_name = function['FunctionName']

                    # Get detailed function configuration
                    try:
                        detailed_function = self._get_function_details(function_name)
                        if not detailed_function:
                            continue

                        # Get tags
                        tags = self._get_function_tags(function['FunctionArn'])

                        # Apply filters
                        if not self.resource_filter.matches(
                            resource=detailed_function,
                            resource_name=function_name,
                            resource_tags=tags
                        ):
                            continue

                        # Build function data
                        function_data = self._build_function_data(detailed_function, tags)
                        functions.append(function_data)

                    except ClientError as e:
                        if not self.client_manager.handle_client_error(e, 'lambda', 'GetFunction'):
                            continue
                        time.sleep(1)  # Brief pause on errors

            print(f"  ✓ Found {len(functions)} Lambda functions")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 'lambda', 'ListFunctions'):
                print(f"  ❌ Failed to scan Lambda functions")
                return []

        return functions

    def _get_function_details(self, function_name: str) -> Dict[str, Any]:
        """Get detailed function configuration."""
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
            return response['Configuration']
        except ClientError:
            return None

    def _get_function_tags(self, function_arn: str) -> Dict[str, str]:
        """Get function tags."""
        try:
            response = self.lambda_client.list_tags(Resource=function_arn)
            return response.get('Tags', {})
        except ClientError:
            return {}

    def _build_function_data(self, function: Dict[str, Any], tags: Dict[str, str]) -> Dict[str, Any]:
        """Build standardized function data structure."""
        # Extract environment variables
        env_vars = {}
        if 'Environment' in function and 'Variables' in function['Environment']:
            env_vars = function['Environment']['Variables']

        # Extract VPC configuration
        vpc_config = None
        if 'VpcConfig' in function and function['VpcConfig'].get('VpcId'):
            vpc_config = {
                'vpc_id': function['VpcConfig'].get('VpcId'),
                'subnet_ids': function['VpcConfig'].get('SubnetIds', []),
                'security_group_ids': function['VpcConfig'].get('SecurityGroupIds', [])
            }

        # Extract layers
        layers = []
        if 'Layers' in function:
            layers = [
                {
                    'arn': layer['Arn'],
                    'code_size': layer.get('CodeSize', 0)
                }
                for layer in function['Layers']
            ]

        # Extract dead letter config
        dead_letter_config = None
        if 'DeadLetterConfig' in function and 'TargetArn' in function['DeadLetterConfig']:
            dead_letter_config = {
                'target_arn': function['DeadLetterConfig']['TargetArn']
            }

        # Build function data
        return {
            'function_name': function['FunctionName'],
            'function_arn': function['FunctionArn'],
            'runtime': function.get('Runtime'),
            'handler': function.get('Handler'),
            'memory_size': function.get('MemorySize', 128),
            'timeout': function.get('Timeout', 3),
            'description': function.get('Description', ''),
            'environment_variables': env_vars,
            'iam_role_arn': function.get('Role'),
            'vpc_config': vpc_config,
            'layers': layers,
            'dead_letter_config': dead_letter_config,
            'last_modified': function.get('LastModified'),
            'code_size': function.get('CodeSize', 0),
            'code_sha256': function.get('CodeSha256'),
            'architectures': function.get('Architectures', ['x86_64']),
            'ephemeral_storage': function.get('EphemeralStorage', {}).get('Size', 512),
            'tags': tags
        }

    def get_function_by_name(self, function_name: str) -> Dict[str, Any]:
        """
        Get a specific function by name.

        Args:
            function_name: Name of the Lambda function

        Returns:
            Function data dictionary or None if not found
        """
        try:
            function = self._get_function_details(function_name)
            if not function:
                return None

            tags = self._get_function_tags(function['FunctionArn'])
            return self._build_function_data(function, tags)

        except ClientError as e:
            print(f"  ❌ Failed to get function '{function_name}': {e}")
            return None
