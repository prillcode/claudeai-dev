"""
DynamoDB Scanner

Discovers AWS DynamoDB tables with complete configurations.
"""

from typing import List, Dict, Any
from botocore.exceptions import ClientError
import time


class DynamoDBScanner:
    """Scans AWS DynamoDB tables."""

    def __init__(self, client_manager, resource_filter):
        """
        Initialize DynamoDB scanner.

        Args:
            client_manager: AWSClientManager instance
            resource_filter: ResourceFilter instance
        """
        self.client_manager = client_manager
        self.resource_filter = resource_filter
        self.dynamodb_client = client_manager.get_client('dynamodb')

    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for DynamoDB tables.

        Returns:
            List of DynamoDB table dictionaries with complete configurations
        """
        print("\n🔍 Scanning DynamoDB tables...")

        tables = []
        try:
            # List all tables with pagination
            paginator = self.dynamodb_client.get_paginator('list_tables')
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for table_name in page['TableNames']:
                    try:
                        # Get detailed table description
                        table_data = self._get_table_details(table_name)
                        if not table_data:
                            continue

                        # Get tags
                        tags = self._get_table_tags(table_data['table_arn'])

                        # Apply filters
                        if not self.resource_filter.matches(
                            resource=table_data,
                            resource_name=table_name,
                            resource_tags=tags
                        ):
                            continue

                        table_data['tags'] = tags
                        tables.append(table_data)

                    except ClientError as e:
                        if not self.client_manager.handle_client_error(e, 'dynamodb', 'DescribeTable'):
                            continue
                        time.sleep(1)

            print(f"  ✓ Found {len(tables)} DynamoDB tables")

        except ClientError as e:
            if not self.client_manager.handle_client_error(e, 'dynamodb', 'ListTables'):
                print(f"  ❌ Failed to scan DynamoDB tables")
                return []

        return tables

    def _get_table_details(self, table_name: str) -> Dict[str, Any]:
        """Get detailed table configuration."""
        try:
            response = self.dynamodb_client.describe_table(TableName=table_name)
            table = response['Table']

            # Extract key schema
            key_schema = []
            for key in table.get('KeySchema', []):
                key_info = {
                    'attribute_name': key['AttributeName'],
                    'key_type': key['KeyType']  # HASH or RANGE
                }
                key_schema.append(key_info)

            # Extract attribute definitions
            attributes = []
            for attr in table.get('AttributeDefinitions', []):
                attributes.append({
                    'attribute_name': attr['AttributeName'],
                    'attribute_type': attr['AttributeType']  # S, N, or B
                })

            # Extract global secondary indexes
            gsis = []
            for gsi in table.get('GlobalSecondaryIndexes', []):
                gsi_keys = []
                for key in gsi.get('KeySchema', []):
                    gsi_keys.append({
                        'attribute_name': key['AttributeName'],
                        'key_type': key['KeyType']
                    })

                gsis.append({
                    'index_name': gsi['IndexName'],
                    'key_schema': gsi_keys,
                    'projection': gsi.get('Projection', {}),
                    'index_status': gsi.get('IndexStatus'),
                    'provisioned_throughput': self._extract_throughput(gsi)
                })

            # Extract local secondary indexes
            lsis = []
            for lsi in table.get('LocalSecondaryIndexes', []):
                lsi_keys = []
                for key in lsi.get('KeySchema', []):
                    lsi_keys.append({
                        'attribute_name': key['AttributeName'],
                        'key_type': key['KeyType']
                    })

                lsis.append({
                    'index_name': lsi['IndexName'],
                    'key_schema': lsi_keys,
                    'projection': lsi.get('Projection', {})
                })

            # Extract stream specification
            stream_spec = None
            if 'StreamSpecification' in table and table['StreamSpecification'].get('StreamEnabled'):
                stream_spec = {
                    'stream_enabled': True,
                    'stream_view_type': table['StreamSpecification'].get('StreamViewType')
                }
                if 'LatestStreamArn' in table:
                    stream_spec['stream_arn'] = table['LatestStreamArn']

            # Extract SSE description
            sse_description = None
            if 'SSEDescription' in table:
                sse_description = {
                    'status': table['SSEDescription'].get('Status'),
                    'sse_type': table['SSEDescription'].get('SSEType'),
                    'kms_master_key_arn': table['SSEDescription'].get('KMSMasterKeyArn')
                }

            # Build table data
            return {
                'table_name': table['TableName'],
                'table_arn': table['TableArn'],
                'table_status': table['TableStatus'],
                'creation_date_time': str(table.get('CreationDateTime')),
                'key_schema': key_schema,
                'attribute_definitions': attributes,
                'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED'),
                'provisioned_throughput': self._extract_throughput(table),
                'global_secondary_indexes': gsis,
                'local_secondary_indexes': lsis,
                'stream_specification': stream_spec,
                'sse_description': sse_description,
                'point_in_time_recovery': self._get_pitr_status(table['TableName']),
                'ttl_specification': self._get_ttl_status(table['TableName']),
                'item_count': table.get('ItemCount', 0),
                'table_size_bytes': table.get('TableSizeBytes', 0)
            }

        except ClientError as e:
            print(f"  ⚠️  Failed to get table details for '{table_name}': {e}")
            return None

    def _extract_throughput(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Extract provisioned throughput settings."""
        if 'ProvisionedThroughput' not in resource:
            return None

        throughput = resource['ProvisionedThroughput']
        return {
            'read_capacity_units': throughput.get('ReadCapacityUnits', 0),
            'write_capacity_units': throughput.get('WriteCapacityUnits', 0)
        }

    def _get_pitr_status(self, table_name: str) -> Dict[str, Any]:
        """Get Point-in-Time Recovery status."""
        try:
            response = self.dynamodb_client.describe_continuous_backups(TableName=table_name)
            pitr = response.get('ContinuousBackupsDescription', {}).get('PointInTimeRecoveryDescription', {})
            return {
                'enabled': pitr.get('PointInTimeRecoveryStatus') == 'ENABLED',
                'earliest_restorable_date_time': str(pitr.get('EarliestRestorableDateTime', ''))
            }
        except ClientError:
            return {'enabled': False}

    def _get_ttl_status(self, table_name: str) -> Dict[str, Any]:
        """Get Time-to-Live status."""
        try:
            response = self.dynamodb_client.describe_time_to_live(TableName=table_name)
            ttl = response.get('TimeToLiveDescription', {})
            return {
                'enabled': ttl.get('TimeToLiveStatus') == 'ENABLED',
                'attribute_name': ttl.get('AttributeName')
            }
        except ClientError:
            return {'enabled': False}

    def _get_table_tags(self, table_arn: str) -> Dict[str, str]:
        """Get table tags."""
        try:
            response = self.dynamodb_client.list_tags_of_resource(ResourceArn=table_arn)
            tags = {}
            for tag in response.get('Tags', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except ClientError:
            return {}

    def get_table_by_name(self, table_name: str) -> Dict[str, Any]:
        """
        Get a specific table by name.

        Args:
            table_name: Name of the DynamoDB table

        Returns:
            Table data dictionary or None if not found
        """
        try:
            table_data = self._get_table_details(table_name)
            if not table_data:
                return None

            tags = self._get_table_tags(table_data['table_arn'])
            table_data['tags'] = tags
            return table_data

        except ClientError as e:
            print(f"  ❌ Failed to get table '{table_name}': {e}")
            return None
