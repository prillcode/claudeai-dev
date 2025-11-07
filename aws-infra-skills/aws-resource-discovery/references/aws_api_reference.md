# AWS API Reference for Resource Discovery

This document details the boto3 API calls used by each resource scanner.

## Lambda Scanner

### API Calls

**list_functions()**
- Paginated call to list all Lambda functions in the region
- Returns: Function configurations including runtime, handler, memory, timeout

**get_function(FunctionName)**
- Get detailed configuration for a specific function
- Returns: Complete function configuration including VPC config, layers, environment

**list_tags(Resource=function_arn)**
- Get tags for a Lambda function
- Returns: Dictionary of tag key-value pairs

### Response Structure

```python
{
    'FunctionName': 'order-processor',
    'FunctionArn': 'arn:aws:lambda:us-east-1:123:function:order-processor',
    'Runtime': 'nodejs18.x',
    'Handler': 'index.handler',
    'MemorySize': 256,
    'Timeout': 30,
    'Environment': {
        'Variables': {
            'TABLE_NAME': 'orders',
            'BUCKET_NAME': 'assets'
        }
    },
    'Role': 'arn:aws:iam::123:role/lambda-role',
    'VpcConfig': {...},
    'Layers': [...],
    'DeadLetterConfig': {...}
}
```

## DynamoDB Scanner

### API Calls

**list_tables()**
- Paginated call to list all DynamoDB tables
- Returns: List of table names

**describe_table(TableName)**
- Get detailed table configuration
- Returns: Table schema, indexes, billing mode, streams, encryption

**describe_continuous_backups(TableName)**
- Get Point-in-Time Recovery status
- Returns: PITR configuration

**describe_time_to_live(TableName)**
- Get TTL configuration
- Returns: TTL status and attribute name

**list_tags_of_resource(ResourceArn)**
- Get tags for a DynamoDB table
- Returns: List of tag dictionaries

### Response Structure

```python
{
    'TableName': 'users',
    'TableArn': 'arn:aws:dynamodb:us-east-1:123:table/users',
    'KeySchema': [
        {'AttributeName': 'userId', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'userId', 'AttributeType': 'S'}
    ],
    'BillingModeSummary': {'BillingMode': 'PAY_PER_REQUEST'},
    'GlobalSecondaryIndexes': [...],
    'LocalSecondaryIndexes': [...],
    'StreamSpecification': {...},
    'SSEDescription': {...}
}
```

## IAM Scanner

### API Calls

**list_roles()**
- Paginated call to list all IAM roles
- Returns: Role configurations

**get_role(RoleName)**
- Get detailed role configuration
- Returns: Role ARN, assume role policy, metadata

**list_attached_role_policies(RoleName)**
- Get managed policies attached to role
- Returns: List of policy ARNs and names

**list_role_policies(RoleName)**
- Get inline policy names for role
- Returns: List of inline policy names

**get_role_policy(RoleName, PolicyName)**
- Get inline policy document
- Returns: Policy document JSON

**list_role_tags(RoleName)**
- Get tags for an IAM role
- Returns: List of tag dictionaries

**list_policies(Scope='Local')**
- List customer-managed policies (not AWS-managed)
- Returns: Policy metadata

**get_policy(PolicyArn)**
- Get policy metadata
- Returns: Policy ARN, default version ID, attachment count

**get_policy_version(PolicyArn, VersionId)**
- Get policy document for specific version
- Returns: Policy document JSON

### Response Structure

```python
# Role
{
    'RoleName': 'lambda-execution',
    'Arn': 'arn:aws:iam::123:role/lambda-execution',
    'AssumeRolePolicyDocument': {...},
    'MaxSessionDuration': 3600,
    'AttachedManagedPolicies': [...],
    'InlinePolicies': [...]
}

# Policy
{
    'PolicyName': 'custom-policy',
    'Arn': 'arn:aws:iam::123:policy/custom-policy',
    'DefaultVersionId': 'v1',
    'PolicyDocument': {...},
    'AttachmentCount': 2
}
```

## S3 Scanner

### API Calls

**list_buckets()**
- List all S3 buckets (S3 is global)
- Returns: List of bucket names and creation dates

**get_bucket_location(Bucket)**
- Get the region where bucket is located
- Returns: Location constraint (region name)

**get_bucket_versioning(Bucket)**
- Get versioning configuration
- Returns: Versioning status, MFA delete status

**get_bucket_encryption(Bucket)**
- Get server-side encryption configuration
- Returns: SSE algorithm, KMS key ID

**get_bucket_lifecycle_configuration(Bucket)**
- Get lifecycle rules
- Returns: List of lifecycle rules with transitions and expirations

**get_bucket_cors(Bucket)**
- Get CORS configuration
- Returns: CORS rules

**get_bucket_policy(Bucket)**
- Get bucket policy document
- Returns: Policy JSON

**get_public_access_block(Bucket)**
- Get public access block configuration
- Returns: Public access settings

**get_bucket_tagging(Bucket)**
- Get bucket tags
- Returns: List of tag dictionaries

### Response Structure

```python
{
    'BucketName': 'my-assets',
    'Arn': 'arn:aws:s3:::my-assets',
    'Region': 'us-east-1',
    'Versioning': {'Status': 'Enabled'},
    'Encryption': {
        'Enabled': True,
        'SSEAlgorithm': 'AES256'
    },
    'LifecycleRules': [...],
    'CORSRules': [...],
    'BucketPolicy': {...},
    'PublicAccessBlock': {...}
}
```

## EventBridge Scanner

### API Calls

**list_rules()**
- Paginated call to list all EventBridge rules
- Returns: Rule names, ARNs, states

**describe_rule(Name)**
- Get detailed rule configuration
- Returns: Event pattern, schedule expression, targets

**list_targets_by_rule(Rule)**
- Get targets for a rule
- Returns: List of target ARNs and configurations

**list_tags_for_resource(ResourceARN)**
- Get tags for an EventBridge rule
- Returns: List of tag dictionaries

### Response Structure

```python
{
    'Name': 'order-created',
    'Arn': 'arn:aws:events:us-east-1:123:rule/order-created',
    'EventPattern': {...},
    'ScheduleExpression': None,
    'State': 'ENABLED',
    'EventBusName': 'default',
    'Targets': [
        {
            'Id': '1',
            'Arn': 'arn:aws:lambda:us-east-1:123:function:process-order',
            'RoleArn': '...',
            'Input': {...}
        }
    ]
}
```

## Error Handling

All scanners handle these common boto3 exceptions:

### ClientError Codes

- **AccessDeniedException**: Insufficient permissions, skip resource type
- **UnauthorizedOperation**: Insufficient permissions, skip resource type
- **ThrottlingException**: API rate limit, implement retry with backoff
- **RequestLimitExceeded**: API rate limit, implement retry with backoff
- **ExpiredToken**: SSO session expired, prompt user to re-login
- **InvalidClientTokenId**: Invalid credentials, prompt reconfiguration
- **ResourceNotFoundException**: Resource doesn't exist, skip
- **ValidationException**: Invalid parameter, skip

### Best Practices

1. **Pagination**: Always use paginators for list operations
2. **Retry Logic**: Implement exponential backoff for throttling
3. **Error Logging**: Log but don't fail on individual resource errors
4. **Graceful Degradation**: Continue scan if one resource type fails
5. **Rate Limiting**: Add small delays between API calls to avoid throttling

## IAM Permissions Required

Minimum permissions for each scanner:

### Lambda
```json
{
  "Effect": "Allow",
  "Action": [
    "lambda:ListFunctions",
    "lambda:GetFunction",
    "lambda:GetFunctionConfiguration",
    "lambda:ListTags"
  ],
  "Resource": "*"
}
```

### DynamoDB
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:ListTables",
    "dynamodb:DescribeTable",
    "dynamodb:DescribeContinuousBackups",
    "dynamodb:DescribeTimeToLive",
    "dynamodb:ListTagsOfResource"
  ],
  "Resource": "*"
}
```

### IAM
```json
{
  "Effect": "Allow",
  "Action": [
    "iam:ListRoles",
    "iam:GetRole",
    "iam:ListAttachedRolePolicies",
    "iam:ListRolePolicies",
    "iam:GetRolePolicy",
    "iam:ListRoleTags",
    "iam:ListPolicies",
    "iam:GetPolicy",
    "iam:GetPolicyVersion",
    "iam:ListPolicyTags"
  ],
  "Resource": "*"
}
```

### S3
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:ListAllMyBuckets",
    "s3:GetBucketLocation",
    "s3:GetBucketVersioning",
    "s3:GetBucketEncryption",
    "s3:GetBucketLifecycleConfiguration",
    "s3:GetBucketCors",
    "s3:GetBucketPolicy",
    "s3:GetPublicAccessBlock",
    "s3:GetBucketTagging"
  ],
  "Resource": "*"
}
```

### EventBridge
```json
{
  "Effect": "Allow",
  "Action": [
    "events:ListRules",
    "events:DescribeRule",
    "events:ListTargetsByRule",
    "events:ListTagsForResource"
  ],
  "Resource": "*"
}
```

## Performance Considerations

### Typical API Call Counts

For an account with 50 Lambda functions, 20 DynamoDB tables, 30 IAM roles:

- Lambda: ~52 calls (1 list + 50 get + 50 list tags)
- DynamoDB: ~61 calls (1 list + 20 describe + 20 PITR + 20 TTL)
- IAM: ~150 calls (1 list roles + 30 get + 30 list attached + 30 list inline + policy calls)
- S3: ~100 calls (1 list + many get operations per bucket)
- EventBridge: ~40 calls (1 list + rule descriptions + target lists)

**Total**: ~400 API calls for medium-sized account

### Rate Limits

AWS service rate limits (approximate):
- Lambda: 100 requests/second
- DynamoDB: 200 requests/second (DescribeTable)
- IAM: 20 requests/second
- S3: 3,500 PUT/POST/DELETE, 5,500 GET/HEAD per second per prefix
- EventBridge: 300 requests/second

The scanners implement automatic throttling and retry logic to stay within limits.
