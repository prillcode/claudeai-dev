"""
S3 Scanner

Discovers AWS S3 buckets with complete configurations.
"""

from typing import List, Dict, Any
from botocore.exceptions import ClientError
import time
import json


class S3Scanner:
    """Scans AWS S3 buckets."""

    def __init__(self, client_manager, resource_filter):
        """
        Initialize S3 scanner.

        Args:
            client_manager: AWSClientManager instance
            resource_filter: ResourceFilter instance
        """
        self.client_manager = client_manager
        self.resource_filter = resource_filter
        self.s3_client = client_manager.get_client('s3')
        self.target_region = client_manager.region

    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for S3 buckets.

        Returns:
            List of S3 bucket dictionaries with complete configurations
        """
        print("\n🔍 Scanning S3 buckets...")

        buckets = []
        try:
            # List all buckets (S3 is global, but we filter by region)
            response = self.s3_client.list_buckets()

            for bucket in response['Buckets']:
                bucket_name = bucket['Name']

                try:
                    # Check bucket region
                    bucket_region = self._get_bucket_region(bucket_name)
                    if bucket_region != self.target_region:
                        continue  # Skip buckets in other regions

                    # Get detailed bucket configuration
                    bucket_data = self._get_bucket_details(bucket_name)
                    if not bucket_data:
                        continue

                    # Get tags
                    tags = self._get_bucket_tags(bucket_name)

                    # Apply filters
                    if not self.resource_filter.matches(
                        resource=bucket_data,
                        resource_name=bucket_name,
                        resource_tags=tags
                    ):
                        continue

                    bucket_data['tags'] = tags
                    buckets.append(bucket_data)

                except ClientError as e:
                    if not self.client_manager.handle_client_error(e, 's3', 'GetBucket'):
                        continue
                    time.sleep(0.5)

            print(f"  ✓ Found {len(buckets)} S3 buckets in {self.target_region}")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 's3', 'ListBuckets'):
                print(f"  ❌ Failed to scan S3 buckets")
                return []

        return buckets

    def _get_bucket_region(self, bucket_name: str) -> str:
        """Get the region where the bucket is located."""
        try:
            response = self.s3_client.get_bucket_location(Bucket=bucket_name)
            location = response.get('LocationConstraint')
            # LocationConstraint is None for us-east-1
            return location if location else 'us-east-1'
        except ClientError:
            return None

    def _get_bucket_details(self, bucket_name: str) -> Dict[str, Any]:
        """Get detailed bucket configuration."""
        try:
            # Build bucket ARN
            bucket_arn = f"arn:aws:s3:::{bucket_name}"

            # Get versioning
            versioning = self._get_bucket_versioning(bucket_name)

            # Get encryption
            encryption = self._get_bucket_encryption(bucket_name)

            # Get lifecycle rules
            lifecycle_rules = self._get_lifecycle_configuration(bucket_name)

            # Get CORS
            cors_rules = self._get_cors_configuration(bucket_name)

            # Get bucket policy
            bucket_policy = self._get_bucket_policy(bucket_name)

            # Get public access block configuration
            public_access_block = self._get_public_access_block(bucket_name)

            # Build bucket data
            return {
                'bucket_name': bucket_name,
                'bucket_arn': bucket_arn,
                'region': self._get_bucket_region(bucket_name),
                'versioning': versioning,
                'encryption': encryption,
                'lifecycle_rules': lifecycle_rules,
                'cors_rules': cors_rules,
                'bucket_policy': bucket_policy,
                'public_access_block': public_access_block
            }

        except ClientError as e:
            print(f"  ⚠️  Failed to get bucket details for '{bucket_name}': {e}")
            return None

    def _get_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket versioning configuration."""
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            return {
                'status': response.get('Status', 'Disabled'),
                'mfa_delete': response.get('MFADelete', 'Disabled')
            }
        except ClientError:
            return {'status': 'Disabled', 'mfa_delete': 'Disabled'}

    def _get_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket encryption configuration."""
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
            rules = response.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
            if rules:
                rule = rules[0]
                sse_algorithm = rule.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm')
                kms_key_id = rule.get('ApplyServerSideEncryptionByDefault', {}).get('KMSMasterKeyID')
                return {
                    'enabled': True,
                    'sse_algorithm': sse_algorithm,
                    'kms_key_id': kms_key_id
                }
        except ClientError:
            pass
        return {'enabled': False}

    def _get_lifecycle_configuration(self, bucket_name: str) -> List[Dict[str, Any]]:
        """Get bucket lifecycle rules."""
        try:
            response = self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            rules = []
            for rule in response.get('Rules', []):
                rules.append({
                    'id': rule.get('ID'),
                    'status': rule.get('Status'),
                    'filter': rule.get('Filter', {}),
                    'transitions': rule.get('Transitions', []),
                    'expiration': rule.get('Expiration', {})
                })
            return rules
        except ClientError:
            return []

    def _get_cors_configuration(self, bucket_name: str) -> List[Dict[str, Any]]:
        """Get bucket CORS configuration."""
        try:
            response = self.s3_client.get_bucket_cors(Bucket=bucket_name)
            return response.get('CORSRules', [])
        except ClientError:
            return []

    def _get_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket policy."""
        try:
            response = self.s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_str = response.get('Policy')
            if policy_str:
                return json.loads(policy_str)
        except ClientError:
            pass
        return None

    def _get_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        """Get public access block configuration."""
        try:
            response = self.s3_client.get_public_access_block(Bucket=bucket_name)
            config = response.get('PublicAccessBlockConfiguration', {})
            return {
                'block_public_acls': config.get('BlockPublicAcls', False),
                'ignore_public_acls': config.get('IgnorePublicAcls', False),
                'block_public_policy': config.get('BlockPublicPolicy', False),
                'restrict_public_buckets': config.get('RestrictPublicBuckets', False)
            }
        except ClientError:
            return {
                'block_public_acls': False,
                'ignore_public_acls': False,
                'block_public_policy': False,
                'restrict_public_buckets': False
            }

    def _get_bucket_tags(self, bucket_name: str) -> Dict[str, str]:
        """Get bucket tags."""
        try:
            response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = {}
            for tag in response.get('TagSet', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}

    def get_bucket_by_name(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get a specific bucket by name.

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            Bucket data dictionary or None if not found
        """
        try:
            bucket_data = self._get_bucket_details(bucket_name)
            if not bucket_data:
                return None

            tags = self._get_bucket_tags(bucket_name)
            bucket_data['tags'] = tags
            return bucket_data

        except ClientError as e:
            print(f"  ❌ Failed to get bucket '{bucket_name}': {e}")
            return None
