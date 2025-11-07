# Supported Resources

Comprehensive reference for all resources supported by aws-resource-discovery.

## Version 1.0 MVP - Core Serverless Resources

### Lambda Functions

**Properties Discovered:**
- Function name and ARN
- Runtime (nodejs18.x, python3.11, etc.)
- Handler (entry point)
- Memory size (MB)
- Timeout (seconds)
- Description
- Environment variables (all key-value pairs)
- IAM execution role ARN
- VPC configuration (VPC ID, subnet IDs, security group IDs)
- Layers (ARNs and code sizes)
- Dead letter queue configuration
- Code size and SHA256
- Architectures (x86_64, arm64)
- Ephemeral storage size
- Last modified timestamp
- Tags

**Use Cases:**
- Importing serverless applications to CDK
- Documenting Lambda-based microservices
- Analyzing compute resources and configurations

**Limitations:**
- Does not download function code
- Does not capture runtime settings beyond basic configuration
- Event source mappings not included (coming in v1.1)

---

### DynamoDB Tables

**Properties Discovered:**
- Table name and ARN
- Table status (ACTIVE, CREATING, etc.)
- Creation timestamp
- Key schema (partition key, sort key)
- Attribute definitions (name and type: S, N, B)
- Billing mode (PROVISIONED, PAY_PER_REQUEST)
- Provisioned throughput (read/write capacity units)
- Global Secondary Indexes (GSIs):
  - Index name
  - Key schema
  - Projection type
  - Provisioned throughput
  - Index status
- Local Secondary Indexes (LSIs):
  - Index name
  - Key schema
  - Projection type
- Stream specification:
  - Stream enabled/disabled
  - Stream view type (NEW_IMAGE, OLD_IMAGE, etc.)
  - Stream ARN
- Server-side encryption (SSE):
  - Encryption status
  - SSE type (KMS, AWS managed)
  - KMS master key ARN
- Point-in-Time Recovery (PITR):
  - Enabled/disabled
  - Earliest restorable time
- Time-to-Live (TTL):
  - Enabled/disabled
  - TTL attribute name
- Item count (approximate)
- Table size in bytes
- Tags

**Use Cases:**
- Importing data layer to CDK
- Documenting database schemas
- Analyzing storage and billing configurations

**Limitations:**
- Does not capture table data/items
- Does not include DAX cluster configurations
- Global tables not fully supported

---

### IAM Roles

**Properties Discovered:**
- Role name and ARN
- Role ID (unique identifier)
- Path (organizational path)
- Description
- Assume role policy document (trust policy)
- Creation date
- Max session duration
- Attached managed policies:
  - Policy name
  - Policy ARN
- Inline policies:
  - Policy name
  - Policy document (JSON)
- Tags

**Use Cases:**
- Understanding Lambda execution roles
- Documenting service-to-service permissions
- Analyzing security posture

**Limitations:**
- Only scans roles, not IAM users or groups
- Permission boundaries not explicitly tracked
- Does not analyze policy effectiveness

---

### IAM Policies (Customer-Managed)

**Properties Discovered:**
- Policy name and ARN
- Policy ID
- Path
- Description
- Default version ID
- Policy document (JSON):
  - Statements (Effect, Action, Resource, Condition)
- Attachment count (how many entities use this policy)
- Permissions boundary usage count
- Is attachable flag
- Creation date
- Last update date
- Tags

**Use Cases:**
- Understanding custom permission sets
- Documenting security policies
- Analyzing least-privilege implementations

**Limitations:**
- Only discovers customer-managed policies (not AWS-managed)
- Does not track which specific entities use the policy
- Does not analyze policy conflicts or overlaps

---

### S3 Buckets

**Properties Discovered:**
- Bucket name and ARN
- Region (location)
- Versioning:
  - Status (Enabled, Suspended, Disabled)
  - MFA delete status
- Server-side encryption:
  - Enabled/disabled
  - SSE algorithm (AES256, aws:kms)
  - KMS key ID (if using KMS)
- Lifecycle rules:
  - Rule ID
  - Status (Enabled/Disabled)
  - Filter (prefix, tags)
  - Transitions (storage class changes)
  - Expiration settings
- CORS configuration:
  - Allowed origins
  - Allowed methods
  - Allowed headers
  - Max age
- Bucket policy (full policy document)
- Public access block configuration:
  - Block public ACLs
  - Ignore public ACLs
  - Block public policy
  - Restrict public buckets
- Tags

**Use Cases:**
- Importing storage infrastructure to CDK
- Documenting asset and data storage
- Analyzing security and compliance configurations

**Limitations:**
- Does not list bucket contents/objects
- Does not capture bucket metrics or analytics
- Replication configurations not included
- Static website hosting settings not included

---

### EventBridge Rules

**Properties Discovered:**
- Rule name and ARN
- Description
- Event pattern (JSON):
  - Source
  - Detail-type
  - Detail matching rules
- Schedule expression (cron or rate)
- State (ENABLED/DISABLED)
- Event bus name (default or custom)
- IAM role ARN (if used for targets)
- Managed by (if rule is AWS-managed)
- Targets:
  - Target ID
  - Target ARN (Lambda, SNS, SQS, etc.)
  - IAM role ARN
  - Input configuration
  - Input path
  - Input transformer
  - Retry policy
  - Dead letter queue config
- Tags

**Use Cases:**
- Importing event-driven architectures to CDK
- Documenting async workflows
- Understanding trigger patterns

**Limitations:**
- Only discovers rules on default event bus (custom buses in v1.1+)
- Does not capture EventBridge schemas
- Archive and replay configurations not included

---

## Resource Type Identifiers

When filtering by resource type, use these identifiers:

| Resource Type | Identifier | Output File |
|--------------|------------|-------------|
| Lambda Functions | `lambda` | `lambdas.json` |
| DynamoDB Tables | `dynamodb` | `dynamodb-tables.json` |
| IAM Roles and Policies | `iam` | `iam-roles.json`, `iam-policies.json` |
| S3 Buckets | `s3` | `s3-buckets.json` |
| EventBridge Rules | `eventbridge` | `eventbridge-rules.json` |

## Resource Naming Conventions

The discovery tool uses AWS's official resource identifiers:

- **Lambda**: Function name (not ARN)
- **DynamoDB**: Table name (not ARN)
- **IAM Role**: Role name (not ARN)
- **IAM Policy**: Policy name (not ARN)
- **S3**: Bucket name (not ARN)
- **EventBridge**: Rule name (not ARN)

All resources also include their full ARN in the output for unambiguous identification.

## Future Resources (v1.1+)

### v1.1 - Extended Serverless Resources
- SQS queues
- SNS topics
- Lambda event source mappings

### v1.2 - API Services
- API Gateway REST APIs
- API Gateway HTTP APIs
- AppSync GraphQL APIs

### v1.3 - Additional Resources
- CloudWatch Log Groups
- Step Functions state machines
- Secrets Manager secrets
- Systems Manager parameters
- Cognito user pools
- CloudFront distributions
- ECR repositories
- ECS/Fargate services

## Tag-Based Discovery

All supported resources can be filtered by tags using the `--tags` flag:

```bash
python discover.py --profile prod --region us-east-1 --tags environment=prod project=myapp
```

Tags must match exactly (case-sensitive).

## Name Pattern Discovery

All supported resources can be filtered by name pattern using the `--name-pattern` flag:

```bash
python discover.py --profile prod --region us-east-1 --name-pattern "order-*"
```

Uses Unix-style glob patterns:
- `*` matches any characters
- `?` matches single character
- `[abc]` matches any character in brackets
- `[!abc]` matches any character not in brackets

## Resource Discovery Order

Resources are scanned in parallel for performance, but output is organized as:

1. Lambda functions
2. DynamoDB tables
3. IAM roles
4. IAM policies
5. S3 buckets
6. EventBridge rules

Dependencies are detected after all resources are discovered.

## Output File Sizes

Approximate output file sizes for reference:

| Resource Count | Lambda JSON | DynamoDB JSON | IAM JSON | S3 JSON | EventBridge JSON |
|----------------|-------------|---------------|----------|---------|------------------|
| 10 resources | ~50 KB | ~40 KB | ~80 KB | ~30 KB | ~20 KB |
| 50 resources | ~250 KB | ~200 KB | ~400 KB | ~150 KB | ~100 KB |
| 200 resources | ~1 MB | ~800 KB | ~1.6 MB | ~600 KB | ~400 KB |

Dependencies JSON is typically 10-20% of total resource data size.

## Regional Resources

All discovered resources are region-specific except:

- **IAM**: Global service, but scanned from specified region
- **S3**: Global namespace, but buckets are region-specific
  - Discovery filters buckets by specified region

## Resource Limits

AWS has default limits per resource type:

- Lambda functions: 1,000 per region
- DynamoDB tables: 2,500 per region
- IAM roles: 1,000 per account (global)
- IAM policies: 1,500 per account (global)
- S3 buckets: 100 per account (global)
- EventBridge rules: 300 per event bus

The discovery tool handles pagination and can scan accounts at or near limits.
