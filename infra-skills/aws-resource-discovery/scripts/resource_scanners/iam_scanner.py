"""
IAM Scanner

Discovers AWS IAM roles and policies.
"""

from typing import List, Dict, Any, Tuple
from botocore.exceptions import ClientError
import time
import json


class IAMScanner:
    """Scans AWS IAM roles and policies."""

    def __init__(self, client_manager, resource_filter):
        """
        Initialize IAM scanner.

        Args:
            client_manager: AWSClientManager instance
            resource_filter: ResourceFilter instance
        """
        self.client_manager = client_manager
        self.resource_filter = resource_filter
        self.iam_client = client_manager.get_client('iam')

    def scan(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Scan for IAM roles and policies.

        Returns:
            Tuple of (roles_list, policies_list)
        """
        roles = self._scan_roles()
        policies = self._scan_policies()
        return roles, policies

    def _scan_roles(self) -> List[Dict[str, Any]]:
        """Scan for IAM roles."""
        print("\n🔍 Scanning IAM roles...")

        roles = []
        try:
            paginator = self.iam_client.get_paginator('list_roles')
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for role in page['Roles']:
                    role_name = role['RoleName']

                    try:
                        # Get detailed role information
                        role_data = self._get_role_details(role_name)
                        if not role_data:
                            continue

                        # Get tags
                        tags = self._get_role_tags(role_name)

                        # Apply filters
                        if not self.resource_filter.matches(
                            resource=role_data,
                            resource_name=role_name,
                            resource_tags=tags
                        ):
                            continue

                        role_data['tags'] = tags
                        roles.append(role_data)

                    except ClientError as e:
                        if not self.client_manager.handle_client_error(e, 'iam', 'GetRole'):
                            continue
                        time.sleep(0.5)

            print(f"  ✓ Found {len(roles)} IAM roles")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 'iam', 'ListRoles'):
                print(f"  ❌ Failed to scan IAM roles")
                return []

        return roles

    def _get_role_details(self, role_name: str) -> Dict[str, Any]:
        """Get detailed role configuration."""
        try:
            # Get role
            response = self.iam_client.get_role(RoleName=role_name)
            role = response['Role']

            # Get attached managed policies
            attached_policies = []
            try:
                paginator = self.iam_client.get_paginator('list_attached_role_policies')
                for page in paginator.paginate(RoleName=role_name):
                    for policy in page['AttachedPolicies']:
                        attached_policies.append({
                            'policy_name': policy['PolicyName'],
                            'policy_arn': policy['PolicyArn']
                        })
            except ClientError:
                pass

            # Get inline policies
            inline_policies = []
            try:
                paginator = self.iam_client.get_paginator('list_role_policies')
                for page in paginator.paginate(RoleName=role_name):
                    for policy_name in page['PolicyNames']:
                        try:
                            policy_response = self.iam_client.get_role_policy(
                                RoleName=role_name,
                                PolicyName=policy_name
                            )
                            inline_policies.append({
                                'policy_name': policy_name,
                                'policy_document': policy_response['PolicyDocument']
                            })
                        except ClientError:
                            pass
            except ClientError:
                pass

            # Build role data
            return {
                'role_name': role['RoleName'],
                'role_arn': role['Arn'],
                'role_id': role['RoleId'],
                'path': role.get('Path', '/'),
                'description': role.get('Description', ''),
                'assume_role_policy_document': role['AssumeRolePolicyDocument'],
                'create_date': str(role.get('CreateDate')),
                'max_session_duration': role.get('MaxSessionDuration', 3600),
                'attached_managed_policies': attached_policies,
                'inline_policies': inline_policies
            }

        except ClientError:
            return None

    def _get_role_tags(self, role_name: str) -> Dict[str, str]:
        """Get role tags."""
        try:
            response = self.iam_client.list_role_tags(RoleName=role_name)
            tags = {}
            for tag in response.get('Tags', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}

    def _scan_policies(self) -> List[Dict[str, Any]]:
        """Scan for customer-managed IAM policies."""
        print("\n🔍 Scanning IAM policies (customer-managed)...")

        policies = []
        try:
            # Only scan customer-managed policies (not AWS-managed)
            paginator = self.iam_client.get_paginator('list_policies')
            page_iterator = paginator.paginate(Scope='Local')

            for page in page_iterator:
                for policy in page['Policies']:
                    policy_name = policy['PolicyName']

                    try:
                        # Get detailed policy information
                        policy_data = self._get_policy_details(policy['Arn'])
                        if not policy_data:
                            continue

                        # Get tags
                        tags = self._get_policy_tags(policy['Arn'])

                        # Apply filters
                        if not self.resource_filter.matches(
                            resource=policy_data,
                            resource_name=policy_name,
                            resource_tags=tags
                        ):
                            continue

                        policy_data['tags'] = tags
                        policies.append(policy_data)

                    except ClientError as e:
                        if not self.client_manager.handle_client_error(e, 'iam', 'GetPolicy'):
                            continue
                        time.sleep(0.5)

            print(f"  ✓ Found {len(policies)} customer-managed IAM policies")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 'iam', 'ListPolicies'):
                print(f"  ❌ Failed to scan IAM policies")
                return []

        return policies

    def _get_policy_details(self, policy_arn: str) -> Dict[str, Any]:
        """Get detailed policy configuration."""
        try:
            # Get policy
            response = self.iam_client.get_policy(PolicyArn=policy_arn)
            policy = response['Policy']

            # Get default policy version document
            policy_document = None
            try:
                version_response = self.iam_client.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=policy['DefaultVersionId']
                )
                policy_document = version_response['PolicyVersion']['Document']
            except ClientError:
                pass

            # Build policy data
            return {
                'policy_name': policy['PolicyName'],
                'policy_arn': policy['Arn'],
                'policy_id': policy['PolicyId'],
                'path': policy.get('Path', '/'),
                'description': policy.get('Description', ''),
                'default_version_id': policy['DefaultVersionId'],
                'policy_document': policy_document,
                'attachment_count': policy.get('AttachmentCount', 0),
                'permissions_boundary_usage_count': policy.get('PermissionsBoundaryUsageCount', 0),
                'is_attachable': policy.get('IsAttachable', True),
                'create_date': str(policy.get('CreateDate')),
                'update_date': str(policy.get('UpdateDate'))
            }

        except ClientError:
            return None

    def _get_policy_tags(self, policy_arn: str) -> Dict[str, str]:
        """Get policy tags."""
        try:
            response = self.iam_client.list_policy_tags(PolicyArn=policy_arn)
            tags = {}
            for tag in response.get('Tags', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}

    def get_role_by_name(self, role_name: str) -> Dict[str, Any]:
        """
        Get a specific role by name.

        Args:
            role_name: Name of the IAM role

        Returns:
            Role data dictionary or None if not found
        """
        try:
            role_data = self._get_role_details(role_name)
            if not role_data:
                return None

            tags = self._get_role_tags(role_name)
            role_data['tags'] = tags
            return role_data

        except ClientError as e:
            print(f"  ❌ Failed to get role '{role_name}': {e}")
            return None

    def get_policy_by_arn(self, policy_arn: str) -> Dict[str, Any]:
        """
        Get a specific policy by ARN.

        Args:
            policy_arn: ARN of the IAM policy

        Returns:
            Policy data dictionary or None if not found
        """
        try:
            policy_data = self._get_policy_details(policy_arn)
            if not policy_data:
                return None

            tags = self._get_policy_tags(policy_arn)
            policy_data['tags'] = tags
            return policy_data

        except ClientError as e:
            print(f"  ❌ Failed to get policy '{policy_arn}': {e}")
            return None
