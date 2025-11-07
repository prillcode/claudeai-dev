"""
DynamoDB Table CDK Code Generator
"""

from typing import Dict, Any, List


class DynamoDBGenerator:
    """Generates CDK code for DynamoDB tables."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, table: Dict[str, Any], mode: str) -> str:
        """Generate TypeScript CDK code for a DynamoDB table."""
        if mode == 'reference':
            return self._generate_reference(table)
        else:
            return self._generate_full(table)

    def _generate_reference(self, table: Dict[str, Any]) -> str:
        """Generate reference-only import."""
        class_name = self._to_class_name(table['table_name'])
        table_name = table['table_name']
        table_arn = table['table_arn']

        code = f"""import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import {{ Construct }} from 'constructs';

/**
 * Reference to existing DynamoDB table: {table_name}
 * ARN: {table_arn}
 */
export class {class_name}Ref {{
  public readonly table: dynamodb.ITable;

  constructor(scope: Construct, id: string) {{
    // Reference existing DynamoDB table
    this.table = dynamodb.Table.fromTableName(
      scope,
      id,
      '{table_name}'
    );
  }}
}}
"""
        return code

    def _generate_full(self, table: Dict[str, Any]) -> str:
        """Generate full management construct."""
        class_name = self._to_class_name(table['table_name'])
        table_name = table['table_name']

        # Get partition key and sort key
        partition_key = table.get('partition_key', {})
        sort_key = table.get('sort_key')

        # Build key schema
        partition_key_code = self._generate_key_attribute(partition_key, 'partitionKey')
        sort_key_code = ""
        if sort_key:
            sort_key_code = self._generate_key_attribute(sort_key, 'sortKey')

        # Get billing mode
        billing_mode = table.get('billing_mode', 'PAY_PER_REQUEST')
        billing_code = self._generate_billing_mode(billing_mode, table.get('provisioned_throughput'))

        # Get encryption settings
        encryption = table.get('encryption', {})
        encryption_code = self._generate_encryption(encryption)

        # Get stream settings
        stream_enabled = table.get('stream_enabled', False)
        stream_code = ""
        if stream_enabled:
            stream_view_type = table.get('stream_view_type', 'NEW_AND_OLD_IMAGES')
            stream_code = f"""      stream: dynamodb.StreamViewType.{stream_view_type},"""

        # Point-in-time recovery
        pitr = table.get('point_in_time_recovery', False)
        pitr_code = f"""      pointInTimeRecovery: {str(pitr).lower()},"""

        # TTL
        ttl_attr = table.get('ttl_attribute')
        ttl_code = ""
        if ttl_attr:
            ttl_code = f"""      timeToLiveAttribute: '{ttl_attr}',"""

        # Build GSIs and LSIs
        gsi_code = self._generate_gsis(table.get('global_secondary_indexes', []))
        lsi_code = self._generate_lsis(table.get('local_secondary_indexes', []))

        # Build tags
        tags = table.get('tags', {})
        tags_code = self._generate_tags(tags)

        code = f"""import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import {{ RemovalPolicy, Tags }} from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';

/**
 * DynamoDB table: {table_name}
 * Billing mode: {billing_mode}
 * Stream enabled: {stream_enabled}
 * PITR enabled: {pitr}
 */
export class {class_name} {{
  public readonly table: dynamodb.Table;

  constructor(scope: Construct, id: string) {{
    this.table = new dynamodb.Table(scope, id, {{
      tableName: '{table_name}',
{partition_key_code}{sort_key_code}{billing_code}{encryption_code}{stream_code}{pitr_code}{ttl_code}      removalPolicy: RemovalPolicy.RETAIN,
    }});
{gsi_code}{lsi_code}{tags_code}  }}
}}
"""
        return code

    def _generate_key_attribute(self, key: Dict[str, Any], key_type: str) -> str:
        """Generate key attribute definition."""
        if not key:
            return ""

        attr_name = key.get('name', key.get('AttributeName', ''))
        attr_type = key.get('type', key.get('AttributeType', 'S'))

        # Map DynamoDB types to CDK types
        type_map = {
            'S': 'STRING',
            'N': 'NUMBER',
            'B': 'BINARY',
        }
        cdk_type = type_map.get(attr_type, 'STRING')

        return f"""      {key_type}: {{ name: '{attr_name}', type: dynamodb.AttributeType.{cdk_type} }},
"""

    def _generate_billing_mode(self, billing_mode: str, provisioned: Dict[str, Any] = None) -> str:
        """Generate billing mode configuration."""
        if billing_mode == 'PROVISIONED' and provisioned:
            rcu = provisioned.get('ReadCapacityUnits', 5)
            wcu = provisioned.get('WriteCapacityUnits', 5)
            return f"""      billingMode: dynamodb.BillingMode.PROVISIONED,
      readCapacity: {rcu},
      writeCapacity: {wcu},
"""
        else:
            return f"""      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
"""

    def _generate_encryption(self, encryption: Dict[str, Any]) -> str:
        """Generate encryption configuration."""
        if not encryption:
            return """      encryption: dynamodb.TableEncryption.AWS_MANAGED,
"""

        sse_type = encryption.get('SSEType', 'AES256')
        if sse_type == 'KMS':
            kms_key_id = encryption.get('KMSMasterKeyId', '')
            if kms_key_id:
                return f"""      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      // TODO: Import KMS key: {kms_key_id}
"""

        return """      encryption: dynamodb.TableEncryption.AWS_MANAGED,
"""

    def _generate_gsis(self, gsis: List[Dict[str, Any]]) -> str:
        """Generate Global Secondary Indexes."""
        if not gsis:
            return ""

        gsi_code = []
        for gsi in gsis:
            index_name = gsi.get('IndexName', '')
            partition_key = gsi.get('KeySchema', [{}])[0]

            pk_name = partition_key.get('AttributeName', '')
            pk_type = 'STRING'  # Default, should be looked up from AttributeDefinitions

            sort_key_name = None
            if len(gsi.get('KeySchema', [])) > 1:
                sort_key = gsi['KeySchema'][1]
                sort_key_name = sort_key.get('AttributeName')

            projection_type = gsi.get('Projection', {}).get('ProjectionType', 'ALL')

            gsi_code.append(f"""
    // Add Global Secondary Index: {index_name}
    this.table.addGlobalSecondaryIndex({{
      indexName: '{index_name}',
      partitionKey: {{ name: '{pk_name}', type: dynamodb.AttributeType.{pk_type} }},""")

            if sort_key_name:
                gsi_code.append(f"""
      sortKey: {{ name: '{sort_key_name}', type: dynamodb.AttributeType.{pk_type} }},""")

            gsi_code.append(f"""
      projectionType: dynamodb.ProjectionType.{projection_type},
    }});""")

        return '\n'.join(gsi_code)

    def _generate_lsis(self, lsis: List[Dict[str, Any]]) -> str:
        """Generate Local Secondary Indexes."""
        if not lsis:
            return ""

        lsi_code = []
        for lsi in lsis:
            index_name = lsi.get('IndexName', '')
            sort_key = lsi.get('KeySchema', [{}])[1] if len(lsi.get('KeySchema', [])) > 1 else {}
            sk_name = sort_key.get('AttributeName', '')
            projection_type = lsi.get('Projection', {}).get('ProjectionType', 'ALL')

            lsi_code.append(f"""
    // Add Local Secondary Index: {index_name}
    this.table.addLocalSecondaryIndex({{
      indexName: '{index_name}',
      sortKey: {{ name: '{sk_name}', type: dynamodb.AttributeType.STRING }},
      projectionType: dynamodb.ProjectionType.{projection_type},
    }});""")

        return '\n'.join(lsi_code)

    def _generate_tags(self, tags: Dict[str, str]) -> str:
        """Generate tags."""
        if not tags:
            return ""

        tag_lines = []
        for key, value in tags.items():
            tag_lines.append(f"""    Tags.of(this.table).add('{key}', '{value}');""")

        if tag_lines:
            return '\n' + '\n'.join(tag_lines) + '\n'
        return ""

    @staticmethod
    def _to_class_name(table_name: str) -> str:
        """Convert table name to PascalCase class name."""
        # Split on hyphens and underscores
        parts = table_name.replace('-', '_').split('_')
        # Capitalize each part
        return ''.join(word.capitalize() for word in parts)
