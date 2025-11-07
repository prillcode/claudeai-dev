# Dependency Detection Patterns

This document explains how the discovery tool detects dependencies between AWS resources.

## Overview

Dependencies are relationships where one resource uses or depends on another resource. The dependency detector uses multiple heuristics to identify these relationships:

1. **Direct configuration references** (most reliable)
2. **IAM policy analysis** (permission-based inference)
3. **Environment variable analysis** (convention-based inference)
4. **Event target analysis** (trigger relationships)

## Dependency Types

### Lambda → IAM Role

**Relationship**: `lambda_uses_role`

**Detection Method**: Direct configuration reference

**Evidence**: Lambda execution role from function configuration

**Example**:
```json
{
  "source": "arn:aws:lambda:us-east-1:123:function:order-processor",
  "target": "arn:aws:iam::123:role/lambda-execution-role",
  "relationship": "lambda_uses_role",
  "evidence": "Lambda execution role from function configuration"
}
```

**CDK Usage**: Lambda function needs to reference the IAM role for execution

---

### Lambda → DynamoDB Table

**Relationship**: `lambda_uses_table`

**Detection Methods**:

1. **IAM Policy Analysis** (Primary):
   - Scan Lambda's IAM role inline policies
   - Look for DynamoDB actions (PutItem, GetItem, Query, etc.)
   - Check Resource field for table ARNs or names

2. **Environment Variable Analysis** (Secondary):
   - Check environment variables for table names
   - Common patterns: `TABLE_NAME`, `DYNAMODB_TABLE`, `*_TABLE`
   - Match against discovered table names

**Evidence Examples**:
- "Inline policy lambda-policy: Actions ['dynamodb:PutItem', 'dynamodb:GetItem']"
- "Environment variable TABLE_NAME=orders-table"

**Example**:
```json
{
  "source": "arn:aws:lambda:us-east-1:123:function:order-processor",
  "target": "arn:aws:dynamodb:us-east-1:123:table/orders",
  "relationship": "lambda_uses_table",
  "evidence": "IAM policy allows dynamodb:PutItem, environment variable TABLE_NAME"
}
```

**CDK Usage**: Lambda needs IAM permissions to access the table

**Reliability**: High (policy-based), Medium (environment variable-based)

---

### Lambda → S3 Bucket

**Relationship**: `lambda_uses_bucket`

**Detection Methods**:

1. **IAM Policy Analysis** (Primary):
   - Scan Lambda's IAM role inline policies
   - Look for S3 actions (PutObject, GetObject, etc.)
   - Check Resource field for bucket ARNs or names

2. **Environment Variable Analysis** (Secondary):
   - Check environment variables for bucket names
   - Common patterns: `BUCKET_NAME`, `S3_BUCKET`, `*_BUCKET`
   - Match against discovered bucket names

**Evidence Examples**:
- "Inline policy s3-access: Actions ['s3:PutObject', 's3:GetObject']"
- "Environment variable BUCKET_NAME=assets-bucket"

**Example**:
```json
{
  "source": "arn:aws:lambda:us-east-1:123:function:image-processor",
  "target": "arn:aws:s3:::image-assets",
  "relationship": "lambda_uses_bucket",
  "evidence": "IAM policy allows s3:GetObject, environment variable BUCKET_NAME"
}
```

**CDK Usage**: Lambda needs IAM permissions to access the bucket

**Reliability**: High (policy-based), Medium (environment variable-based)

---

### EventBridge Rule → Lambda

**Relationship**: `eventbridge_triggers_lambda`

**Detection Method**: Direct target configuration

**Evidence**: Rule target from EventBridge rule configuration

**Example**:
```json
{
  "source": "arn:aws:events:us-east-1:123:rule/order-created",
  "target": "arn:aws:lambda:us-east-1:123:function:process-order",
  "relationship": "eventbridge_triggers_lambda",
  "evidence": "Rule target: 1"
}
```

**CDK Usage**: Lambda needs EventBridge invocation permissions

**Reliability**: Very High (direct configuration)

---

### IAM Role → IAM Policy

**Relationship**: `role_uses_policy`

**Detection Method**: Direct attachment configuration

**Evidence**: Attached managed policy from role configuration

**Example**:
```json
{
  "source": "arn:aws:iam::123:role/lambda-execution",
  "target": "arn:aws:iam::123:policy/dynamodb-access",
  "relationship": "role_uses_policy",
  "evidence": "Attached managed policy: dynamodb-access"
}
```

**CDK Usage**: Role must attach the policy for permissions

**Reliability**: Very High (direct configuration)

---

## Detection Heuristics

### IAM Policy Resource Matching

When analyzing IAM policies, the detector looks for these patterns:

**Exact ARN Match**:
```json
"Resource": "arn:aws:dynamodb:us-east-1:123:table/orders"
```
→ High confidence match

**Wildcard ARN**:
```json
"Resource": "arn:aws:dynamodb:us-east-1:123:table/*"
```
→ Potential match (lower confidence)

**Resource Name in Path**:
```json
"Resource": "arn:aws:dynamodb:*:*:table/orders"
```
→ Match if table name found

### Environment Variable Patterns

Common environment variable naming conventions:

**DynamoDB Tables**:
- `TABLE_NAME`
- `DYNAMODB_TABLE`
- `ORDERS_TABLE`
- `USER_TABLE_NAME`

**S3 Buckets**:
- `BUCKET_NAME`
- `S3_BUCKET`
- `ASSETS_BUCKET`
- `UPLOAD_BUCKET_NAME`

The detector checks if the variable value matches any discovered resource name.

### Action-Based Service Detection

**DynamoDB Actions**:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:UpdateItem`
- `dynamodb:DeleteItem`
- `dynamodb:BatchGetItem`
- `dynamodb:BatchWriteItem`

**S3 Actions**:
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`
- `s3:ListBucket`
- `s3:GetBucketLocation`

## Limitations

### Current Version (v1.0)

**Not Detected**:
- Dependencies through managed policies (AWS or customer-managed policies attached to roles)
  - *Reason*: Would require fetching and parsing each policy separately
  - *Future*: v1.1 will include managed policy analysis

- Implicit dependencies (not declared in IAM or configuration)
  - Example: Lambda writes to CloudWatch Logs (implicit permission)
  - *Future*: May add common implicit dependencies in v1.2

- Cross-account dependencies
  - Example: Lambda in Account A accessing DynamoDB in Account B
  - *Future*: Multi-account support in v1.3

- Runtime-determined dependencies
  - Example: Lambda determines table name at runtime based on logic
  - *Reason*: Requires code analysis, not configuration analysis

**Partial Detection**:
- Wildcard IAM policies
  - Example: `Resource: "*"` grants access but doesn't identify specific resources
  - *Detection*: Notes the action but can't map to specific resource

### False Positives

**Rare Cases Where Dependencies May Be Incorrect**:

1. **Name Collisions**:
   - If environment variable `TABLE_NAME=orders` but Lambda actually doesn't use it
   - Mitigation: Multiple evidence sources increase confidence

2. **Unused Permissions**:
   - IAM policy grants DynamoDB access but Lambda never uses it
   - Mitigation: This is actually useful for security auditing

3. **String Matching**:
   - Environment variable happens to contain a table name but isn't used for that purpose
   - Mitigation: Focus on conventional variable names (TABLE_NAME, etc.)

### False Negatives

**Cases Where Dependencies May Be Missed**:

1. **Managed Policies** (v1.0 limitation):
   - Lambda uses managed policy with DynamoDB permissions
   - *Current*: Not detected
   - *Workaround*: Use inline policies or wait for v1.1

2. **Computed Resource Names**:
   - Lambda constructs resource name at runtime
   - Example: `const table = process.env.STAGE + '-orders'`
   - *Current*: Not detected
   - *Mitigation*: No workaround for dynamic construction

3. **SDK Default Credentials**:
   - Lambda uses SDK with default credentials to access resources
   - Permissions granted but not explicitly configured
   - *Current*: Partially detected through IAM role analysis

## Dependency Graph

Dependencies form a directed graph:

```
┌──────────────┐
│  EventBridge │
│     Rule     │
└──────┬───────┘
       │ triggers
       ▼
┌──────────────┐
│    Lambda    │
│   Function   │
└──┬────┬────┬─┘
   │    │    │
   │    │    └──── uses ────▶ ┌──────────────┐
   │    │                     │  S3 Bucket   │
   │    │                     └──────────────┘
   │    │
   │    └──────── uses ────▶ ┌──────────────┐
   │                         │   DynamoDB   │
   │                         │    Table     │
   │                         └──────────────┘
   │
   └──────────── uses ────▶ ┌──────────────┐
                             │   IAM Role   │
                             └──────┬───────┘
                                    │ uses
                                    ▼
                             ┌──────────────┐
                             │  IAM Policy  │
                             └──────────────┘
```

## Using Dependency Information

### In CDK Code Generation

Dependencies inform:

1. **Import Order**: Create dependent resources first
2. **References**: Pass resource references between constructs
3. **Permissions**: Grant IAM permissions based on detected usage
4. **Stack Organization**: Group related resources in same stack

### Example CDK Usage

Based on detected dependencies:

```typescript
// Create DynamoDB table first (no dependencies)
const ordersTable = new dynamodb.Table(this, 'OrdersTable', {...});

// Create IAM role with policy for DynamoDB access
const lambdaRole = new iam.Role(this, 'ProcessorRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
});

// Grant Lambda role permission to DynamoDB table
ordersTable.grantReadWriteData(lambdaRole);

// Create Lambda function with role and environment variable
const processorFunction = new lambda.Function(this, 'Processor', {
  role: lambdaRole,
  environment: {
    TABLE_NAME: ordersTable.tableName,
  },
});

// Create EventBridge rule targeting Lambda
const rule = new events.Rule(this, 'OrderCreatedRule', {
  eventPattern: {...},
});
rule.addTarget(new targets.LambdaFunction(processorFunction));
```

## Future Enhancements

### v1.1 - Enhanced Dependency Detection
- Managed policy analysis (fetch and parse attached managed policies)
- SQS queue dependencies (Lambda → SQS, EventBridge → SQS)
- SNS topic dependencies (Lambda → SNS, EventBridge → SNS)
- Lambda event source mappings (SQS → Lambda, DynamoDB Streams → Lambda)

### v1.2 - API Service Dependencies
- API Gateway → Lambda integrations
- API Gateway → DynamoDB direct integrations
- AppSync → Lambda resolvers
- AppSync → DynamoDB data sources

### v1.3 - Advanced Dependency Analysis
- CloudWatch Logs implicit dependencies
- Step Functions state machine integrations
- Secrets Manager → Lambda dependencies
- VPC networking dependencies (security groups, subnets)
- Cross-account dependency detection
