"""
EventBridge Scanner

Discovers AWS EventBridge rules with complete configurations.
"""

from typing import List, Dict, Any
from botocore.exceptions import ClientError
import time
import json


class EventBridgeScanner:
    """Scans AWS EventBridge rules."""

    def __init__(self, client_manager, resource_filter):
        """
        Initialize EventBridge scanner.

        Args:
            client_manager: AWSClientManager instance
            resource_filter: ResourceFilter instance
        """
        self.client_manager = client_manager
        self.resource_filter = resource_filter
        self.events_client = client_manager.get_client('events')
        self.region = client_manager.region
        self.account_id = client_manager.get_account_id()

    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for EventBridge rules.

        Returns:
            List of EventBridge rule dictionaries with complete configurations
        """
        print("\n🔍 Scanning EventBridge rules...")

        rules = []
        try:
            # List all rules with pagination
            paginator = self.events_client.get_paginator('list_rules')
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for rule in page['Rules']:
                    rule_name = rule['Name']

                    try:
                        # Get detailed rule configuration
                        rule_data = self._get_rule_details(rule_name)
                        if not rule_data:
                            continue

                        # Get tags
                        tags = self._get_rule_tags(rule['Arn'])

                        # Apply filters
                        if not self.resource_filter.matches(
                            resource=rule_data,
                            resource_name=rule_name,
                            resource_tags=tags
                        ):
                            continue

                        rule_data['tags'] = tags
                        rules.append(rule_data)

                    except ClientError as e:
                        if not self.client_manager.handle_client_error(e, 'events', 'DescribeRule'):
                            continue
                        time.sleep(0.5)

            print(f"  ✓ Found {len(rules)} EventBridge rules")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 'events', 'ListRules'):
                print(f"  ❌ Failed to scan EventBridge rules")
                return []

        return rules

    def _get_rule_details(self, rule_name: str) -> Dict[str, Any]:
        """Get detailed rule configuration."""
        try:
            # Get rule details
            response = self.events_client.describe_rule(Name=rule_name)

            # Parse event pattern if present
            event_pattern = None
            if 'EventPattern' in response and response['EventPattern']:
                try:
                    event_pattern = json.loads(response['EventPattern'])
                except json.JSONDecodeError:
                    event_pattern = response['EventPattern']

            # Get targets
            targets = self._get_rule_targets(rule_name)

            # Build rule data
            return {
                'rule_name': response['Name'],
                'rule_arn': response['Arn'],
                'description': response.get('Description', ''),
                'event_pattern': event_pattern,
                'schedule_expression': response.get('ScheduleExpression'),
                'state': response.get('State', 'ENABLED'),
                'event_bus_name': response.get('EventBusName', 'default'),
                'role_arn': response.get('RoleArn'),
                'managed_by': response.get('ManagedBy'),
                'targets': targets
            }

        except ClientError as e:
            print(f"  ⚠️  Failed to get rule details for '{rule_name}': {e}")
            return None

    def _get_rule_targets(self, rule_name: str) -> List[Dict[str, Any]]:
        """Get targets for a rule."""
        try:
            response = self.events_client.list_targets_by_rule(Rule=rule_name)
            targets = []

            for target in response.get('Targets', []):
                target_data = {
                    'id': target['Id'],
                    'arn': target['Arn'],
                    'role_arn': target.get('RoleArn')
                }

                # Add input configuration if present
                if 'Input' in target:
                    try:
                        target_data['input'] = json.loads(target['Input'])
                    except json.JSONDecodeError:
                        target_data['input'] = target['Input']

                if 'InputPath' in target:
                    target_data['input_path'] = target['InputPath']

                if 'InputTransformer' in target:
                    target_data['input_transformer'] = target['InputTransformer']

                # Add retry policy if present
                if 'RetryPolicy' in target:
                    target_data['retry_policy'] = target['RetryPolicy']

                # Add dead letter config if present
                if 'DeadLetterConfig' in target:
                    target_data['dead_letter_config'] = target['DeadLetterConfig']

                targets.append(target_data)

            return targets

        except ClientError:
            return []

    def _get_rule_tags(self, rule_arn: str) -> Dict[str, str]:
        """Get rule tags."""
        try:
            response = self.events_client.list_tags_for_resource(ResourceARN=rule_arn)
            tags = {}
            for tag in response.get('Tags', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}

    def get_rule_by_name(self, rule_name: str) -> Dict[str, Any]:
        """
        Get a specific rule by name.

        Args:
            rule_name: Name of the EventBridge rule

        Returns:
            Rule data dictionary or None if not found
        """
        try:
            rule_data = self._get_rule_details(rule_name)
            if not rule_data:
                return None

            tags = self._get_rule_tags(rule_data['rule_arn'])
            rule_data['tags'] = tags
            return rule_data

        except ClientError as e:
            print(f"  ❌ Failed to get rule '{rule_name}': {e}")
            return None
