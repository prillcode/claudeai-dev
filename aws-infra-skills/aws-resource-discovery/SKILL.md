# aws-resource-discovery

Scan AWS accounts to discover existing resources and generate a comprehensive inventory with properties and dependencies.

## Purpose

This skill enables you to:
- Discover AWS resources across your accounts with complete configurations
- Filter resources by tags, name patterns, or resource types
- Detect dependencies between resources (Lambda→DynamoDB, Lambda→S3, etc.)
- Export detailed resource inventories as structured JSON files
- Prepare resource data for CDK code generation

## Version

**v1.0 MVP** - Core serverless resource discovery

## Supported Resources

- **Lambda Functions**: Runtime, handler, environment variables, layers, VPC config, IAM roles
- **DynamoDB Tables**: Billing mode, GSIs, LSIs, streams, encryption, TTL, PITR
- **IAM Roles**: Trust policies, attached policies, inline policies
- **IAM Policies**: Managed and inline policy documents
- **S3 Buckets**: Versioning, encryption, lifecycle rules, CORS, bucket policies
- **EventBridge Rules**: Event patterns, targets, schedules

## How to Use This Skill

### Basic Discovery

When the user wants to discover AWS resources, invoke the discovery script with appropriate parameters:

```python
# In your skill invocation:
# 1. Parse user's request to extract:
#    - AWS profile name
#    - AWS region
#    - Filter criteria (tags, name patterns, resource types)
#    - Output prefix (optional, for organized output)
#
# 2. Execute the discovery script:
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --output-prefix myprefix  # Optional: creates "myprefix-inventory" folder
```

### Output Directory Options

**Option 1: Use prefix (Recommended)**
When user searches for specific resources (e.g., "cs-*"), use that prefix for the output directory:

```bash
# Creates "./cs-inventory/" directory
python scripts/discover.py --profile prod --region us-east-1 --output-prefix cs
```

**Option 2: Explicit directory**
```bash
# Creates "./my-custom-dir/" directory
python scripts/discover.py --profile prod --region us-east-1 --output-dir ./my-custom-dir
```

**Option 3: Default**
```bash
# Creates "./resource-inventory/" directory
python scripts/discover.py --profile prod --region us-east-1
```

**Important Notes:**
- The script shows a preview of where output will be saved before starting
- If the directory already exists, the script prompts for confirmation before overwriting
- When user provides a name pattern like "cs-*", infer the prefix "cs" for --output-prefix

### Discovery Modes

#### 1. Full Discovery (All Resources)
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --output-dir ./resource-inventory
```

#### 2. Filtered by Tags
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --tags project=myapp environment=production \
  --output-dir ./resource-inventory
```

#### 3. Filtered by Resource Types
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda dynamodb \
  --output-dir ./resource-inventory
```

#### 4. Filtered by Name Pattern
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --name-pattern "order-service-*" \
  --output-dir ./resource-inventory
```

#### 5. Specific Resource Lookup with Dependencies
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --function-name order-processor \
  --traverse-dependencies \
  --output-dir ./resource-inventory
```

## Understanding User Requests

### Request Pattern: Full Discovery
**User says:** "Use aws-resource-discovery to scan us-east-1 using profile 'prod' for all resources"

**Action:**
```bash
python scripts/discover.py --profile prod --region us-east-1 --output-dir ./resource-inventory
```

### Request Pattern: Tag-Based Discovery
**User says:** "Use aws-resource-discovery to find all resources tagged with 'project:myapp' in us-east-1"

**Action:**
```bash
python scripts/discover.py --profile prod --region us-east-1 --tags project=myapp --output-dir ./resource-inventory
```

### Request Pattern: Resource Type Filtering
**User says:** "Use aws-resource-discovery to find all Lambda functions and DynamoDB tables in us-east-1 using profile 'dev'"

**Action:**
```bash
python scripts/discover.py --profile dev --region us-east-1 --resource-types lambda dynamodb --output-dir ./resource-inventory
```

### Request Pattern: Name Pattern Search
**User says:** "Use aws-resource-discovery to find all resources with 'order-service' in the name using profile 'prod' in us-east-1"

**Action:**
```bash
python scripts/discover.py --profile prod --region us-east-1 --name-pattern "*order-service*" --output-prefix order-service
```

**User says:** "Find all Lambda and DynamoDB resources which names beginning with 'cs-' in my techops account"

**Action:**
```bash
# Infer prefix "cs" from the "cs-*" pattern
python scripts/discover.py --profile techops --region us-east-2 --resource-types lambda dynamodb --name-pattern "cs-*" --output-prefix cs
```

### Request Pattern: Specific Resource with Dependencies
**User says:** "Use aws-resource-discovery to get details for Lambda function 'order-processor' and all its dependencies using profile 'prod'"

**Action:**
```bash
python scripts/discover.py --profile prod --region us-east-1 --function-name order-processor --traverse-dependencies --output-dir ./resource-inventory
```

## Output Format

The skill generates a directory structure with separate JSON files for each resource type:

```
resource-inventory/
├── metadata.json                  # Scan metadata (account, region, timestamp, filters)
├── lambdas.json                   # All discovered Lambda functions
├── dynamodb-tables.json           # All discovered DynamoDB tables
├── iam-roles.json                 # All discovered IAM roles
├── iam-policies.json              # All discovered IAM policies
├── s3-buckets.json                # All discovered S3 buckets
├── eventbridge-rules.json         # All discovered EventBridge rules
└── dependencies.json              # Cross-resource dependencies
```

## Output Schema

### metadata.json
```json
{
  "account_id": "123456789012",
  "region": "us-east-1",
  "scan_timestamp": "2025-01-07T10:30:00Z",
  "profile": "prod",
  "filters_applied": {
    "tags": {"project": "myapp"},
    "name_pattern": "order-*",
    "resource_types": ["lambda", "dynamodb"]
  },
  "resource_counts": {
    "lambdas": 5,
    "dynamodb_tables": 3,
    "iam_roles": 8,
    "iam_policies": 12,
    "s3_buckets": 2,
    "eventbridge_rules": 4
  }
}
```

### lambdas.json
```json
[
  {
    "function_name": "order-processor",
    "function_arn": "arn:aws:lambda:us-east-1:123:function:order-processor",
    "runtime": "nodejs18.x",
    "handler": "index.handler",
    "memory_size": 256,
    "timeout": 30,
    "environment_variables": {
      "TABLE_NAME": "orders-table",
      "BUCKET_NAME": "order-assets"
    },
    "iam_role_arn": "arn:aws:iam::123:role/order-processor-role",
    "vpc_config": null,
    "layers": [],
    "tags": {
      "project": "myapp",
      "service": "orders"
    }
  }
]
```

### dependencies.json
```json
[
  {
    "source": "arn:aws:lambda:us-east-1:123:function:order-processor",
    "target": "arn:aws:dynamodb:us-east-1:123:table/orders-table",
    "relationship": "lambda_uses_table",
    "evidence": "IAM policy allows dynamodb:PutItem, environment variable TABLE_NAME"
  },
  {
    "source": "arn:aws:lambda:us-east-1:123:function:order-processor",
    "target": "arn:aws:s3:::order-assets",
    "relationship": "lambda_uses_bucket",
    "evidence": "IAM policy allows s3:PutObject, environment variable BUCKET_NAME"
  }
]
```

## Dependency Detection

The skill automatically detects these dependency patterns:

1. **Lambda → IAM Role**: From function configuration
2. **Lambda → DynamoDB Table**: From IAM policy permissions + environment variables
3. **Lambda → S3 Bucket**: From IAM policy permissions + environment variables
4. **Lambda → EventBridge**: Lambda is a target of EventBridge rule
5. **EventBridge → Lambda**: Rule has Lambda as target
6. **IAM Role → IAM Policy**: Attached managed and inline policies

## Authentication

### AWS CLI Profiles
The skill uses standard AWS CLI profiles configured in `~/.aws/config` and `~/.aws/credentials`.

```bash
# Standard profile
--profile prod

# Default profile (if not specified)
--profile default
```

### SSO Profiles
For AWS SSO profiles, ensure you're logged in before running discovery:

```bash
# Login to SSO profile first
aws sso login --profile prod

# Then run discovery
python scripts/discover.py --profile prod --region us-east-1
```

If the profile requires SSO login, the script will detect this and provide a helpful error message with login instructions.

## Error Handling

The skill handles common errors gracefully:

- **Missing Permissions**: Reports which resource types couldn't be scanned
- **Invalid Profile**: Provides clear error about profile not found
- **SSO Not Logged In**: Prompts to run `aws sso login --profile <name>`
- **Invalid Region**: Reports region error with available regions
- **API Rate Limiting**: Automatically implements retry with exponential backoff
- **Pagination**: Handles large resource lists automatically

## Prerequisites

- Python 3.8+
- boto3 installed (`pip install boto3`)
- AWS CLI configured with appropriate profiles
- IAM permissions for resource discovery (see below)

## Required IAM Permissions

The discovery script requires read-only permissions for the resources being discovered:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:ListTags",
        "dynamodb:ListTables",
        "dynamodb:DescribeTable",
        "dynamodb:ListTagsOfResource",
        "iam:ListRoles",
        "iam:GetRole",
        "iam:ListRolePolicies",
        "iam:GetRolePolicy",
        "iam:ListAttachedRolePolicies",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:ListPolicies",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning",
        "s3:GetBucketEncryption",
        "s3:GetBucketCors",
        "s3:GetBucketPolicy",
        "s3:GetBucketTagging",
        "s3:GetLifecycleConfiguration",
        "events:ListRules",
        "events:DescribeRule",
        "events:ListTargetsByRule",
        "events:ListTagsForResource"
      ],
      "Resource": "*"
    }
  ]
}
```

## Performance Considerations

- **Parallel Scanning**: Resource types are scanned in parallel for speed
- **Pagination Handling**: Automatically handles large resource lists
- **Rate Limit Handling**: Implements exponential backoff for API throttling
- **Typical Scan Times**:
  - Small account (< 50 resources): 5-10 seconds
  - Medium account (50-200 resources): 15-30 seconds
  - Large account (200+ resources): 30-60 seconds

## Limitations (v1.0)

- Single region per scan (multi-region support in v1.3)
- Single account per scan (multi-account support in v1.3)
- Resource types limited to 6 core serverless services (more in v1.1+)
- Dependency detection is heuristic-based (may not catch all relationships)

## Next Steps

After running discovery, use the generated inventory files with:
- **cdk-code-generator**: Generate TypeScript CDK code from inventory
- **Manual Review**: Review discovered resources and dependencies
- **Filtering**: Re-run with refined filters if needed

## Troubleshooting

### Issue: "Profile 'prod' not found"
**Solution**: Check `~/.aws/config` for profile configuration. Ensure profile name matches exactly.

### Issue: "SSO session expired"
**Solution**: Run `aws sso login --profile <name>` before running discovery.

### Issue: "Access denied for Lambda:ListFunctions"
**Solution**: Ensure IAM user/role has required read permissions (see IAM Permissions section).

### Issue: "No resources found"
**Solution**:
- Check if filters are too restrictive
- Verify resources exist in specified region
- Try scanning without filters first

### Issue: "Script hangs or times out"
**Solution**:
- Large accounts may take time; be patient
- Check AWS console for API throttling issues
- Try filtering by resource type to reduce scope

## Examples

### Example 1: Discover All Production Resources
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --tags environment=production \
  --output-dir ./prod-inventory
```

### Example 2: Discover Specific Application
```bash
python scripts/discover.py \
  --profile dev \
  --region us-west-2 \
  --tags project=myapp \
  --output-dir ./myapp-inventory
```

### Example 3: Discover Only Lambda and DynamoDB
```bash
python scripts/discover.py \
  --profile staging \
  --region eu-west-1 \
  --resource-types lambda dynamodb \
  --output-dir ./serverless-inventory
```

### Example 4: Discover Resources Matching Pattern
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --name-pattern "order-*" \
  --output-dir ./order-service-inventory
```

## Skill Development Notes

This skill is part of a larger AWS to CDK importer workflow. See `AWS_CDK_IMPORTER_ROADMAP.md` for the complete vision and roadmap.

**Current Version**: v1.0 MVP
**Next Version**: v1.1 - Extended Serverless Resources (SQS, SNS, Lambda event source mappings)
**Status**: In Development
