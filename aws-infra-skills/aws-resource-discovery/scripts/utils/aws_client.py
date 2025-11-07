"""
AWS Client Manager

Handles boto3 client initialization, session management, and error handling.
"""

import boto3
from botocore.exceptions import ClientError, ProfileNotFound, NoCredentialsError
from typing import Dict, Optional
import sys


class AWSClientManager:
    """Manages AWS client initialization and session handling."""

    def __init__(self, profile: str, region: str):
        """
        Initialize AWS client manager.

        Args:
            profile: AWS CLI profile name
            region: AWS region name
        """
        self.profile = profile
        self.region = region
        self.session = None
        self.clients: Dict[str, any] = {}
        self._initialize_session()

    def _initialize_session(self):
        """Initialize boto3 session with profile and region."""
        try:
            self.session = boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
            # Test credentials by getting caller identity
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✓ Authenticated as: {identity['Arn']}")
            print(f"✓ Account ID: {identity['Account']}")
            print(f"✓ Region: {self.region}")
        except ProfileNotFound:
            print(f"❌ Error: AWS profile '{self.profile}' not found.")
            print(f"\nAvailable profiles can be found in ~/.aws/config")
            print(f"To configure a new profile, run: aws configure --profile {self.profile}")
            sys.exit(1)
        except NoCredentialsError:
            print(f"❌ Error: No AWS credentials found for profile '{self.profile}'")
            print(f"\nPlease configure credentials:")
            print(f"  aws configure --profile {self.profile}")
            sys.exit(1)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ExpiredToken':
                print(f"❌ Error: AWS SSO session has expired for profile '{self.profile}'")
                print(f"\nPlease login again:")
                print(f"  aws sso login --profile {self.profile}")
                sys.exit(1)
            elif error_code == 'InvalidClientTokenId':
                print(f"❌ Error: Invalid AWS credentials for profile '{self.profile}'")
                print(f"\nPlease reconfigure credentials:")
                print(f"  aws configure --profile {self.profile}")
                sys.exit(1)
            else:
                print(f"❌ Error authenticating with AWS: {e}")
                sys.exit(1)

    def get_client(self, service: str):
        """
        Get or create a boto3 client for the specified service.

        Args:
            service: AWS service name (e.g., 'lambda', 'dynamodb')

        Returns:
            Boto3 client for the service
        """
        if service not in self.clients:
            self.clients[service] = self.session.client(service)
        return self.clients[service]

    def get_account_id(self) -> str:
        """Get the AWS account ID for the current session."""
        sts = self.get_client('sts')
        return sts.get_caller_identity()['Account']

    def handle_client_error(self, error: ClientError, service: str, operation: str) -> bool:
        """
        Handle boto3 client errors with user-friendly messages.

        Args:
            error: The ClientError exception
            service: AWS service name
            operation: Operation being performed

        Returns:
            True if error is recoverable, False otherwise
        """
        error_code = error.response['Error']['Code']

        if error_code == 'AccessDeniedException' or error_code == 'UnauthorizedOperation':
            print(f"⚠️  Warning: Access denied for {service}:{operation}")
            print(f"   Skipping {service} resource discovery due to insufficient permissions.")
            return True
        elif error_code == 'ThrottlingException' or error_code == 'RequestLimitExceeded':
            print(f"⚠️  Warning: API rate limit exceeded for {service}:{operation}")
            print(f"   Will retry with backoff...")
            return True
        else:
            print(f"❌ Error: {service}:{operation} failed: {error}")
            return False


def validate_region(region: str) -> bool:
    """
    Validate that the region name is valid.

    Args:
        region: AWS region name

    Returns:
        True if valid, False otherwise
    """
    try:
        ec2 = boto3.client('ec2', region_name=region)
        # Attempt to describe regions to validate
        regions = ec2.describe_regions()
        valid_regions = [r['RegionName'] for r in regions['Regions']]
        if region in valid_regions:
            return True
        else:
            print(f"❌ Error: Invalid region '{region}'")
            print(f"\nValid regions include: {', '.join(valid_regions[:10])}...")
            return False
    except ClientError as e:
        print(f"❌ Error validating region: {e}")
        return False
