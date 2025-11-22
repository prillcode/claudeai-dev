# CDK Import Resource Identifiers

Reference guide for resource identifiers used in CDK import operations.

## Overview

When importing resources into CDK, you need to provide the physical resource identifier that uniquely identifies the resource in AWS. Different resource types use different identifiers.

## Identifier Format by Resource Type

### Lambda Functions

**Identifier**: Function name

**Format**: `string`

**Example**:
```json
{
  "MyFunction": "order-processor"
}
```

**Notes**:
- Use the function name, not the ARN
- Function must exist in the AWS account/region
- Case-sensitive

### DynamoDB Tables

**Identifier**: Table name

**Format**: `string`

**Example**:
```json
{
  "MyTable": "users-table"
}
```

**Notes**:
- Use the table name, not the ARN
- Table must be in ACTIVE state
- Case-sensitive

### IAM Roles

**Identifier**: Role name

**Format**: `string`

**Example**:
```json
{
  "MyRole": "lambda-execution-role"
}
```

**Notes**:
- Use the role name, not the ARN
- Role must exist
- Do not include path prefix

### IAM Policies

**Identifier**: Policy ARN

**Format**: `arn:aws:iam::account-id:policy/policy-name`

**Example**:
```json
{
  "MyPolicy": "arn:aws:iam::123456789012:policy/my-custom-policy"
}
```

**Notes**:
- Must use full ARN (unlike roles)
- For AWS managed policies, use AWS account ID (e.g., `arn:aws:iam::aws:policy/...`)
- For customer managed policies, use your account ID

### S3 Buckets

**Identifier**: Bucket name

**Format**: `string`

**Example**:
```json
{
  "MyBucket": "my-assets-bucket"
}
```

**Notes**:
- Use the bucket name, not the ARN
- Bucket must exist
- Must be in the same region as the stack

### EventBridge Rules

**Identifier**: Rule name

**Format**: `string`

**Example**:
```json
{
  "MyRule": "order-created-rule"
}
```

**Notes**:
- Use the rule name, not the ARN
- Rule must be enabled or disabled (not in ERROR state)
- Event bus name is not part of the identifier

## Common Issues

### Issue: Resource Not Found

**Error**: `Resource not found during import`

**Causes**:
- Resource was deleted after discovery
- Wrong region or account
- Identifier format is incorrect

**Solution**:
- Verify resource still exists: `aws lambda get-function --function-name my-function`
- Check AWS credentials point to correct account/region
- Verify identifier format matches resource type

### Issue: Resource Already Managed

**Error**: `Resource is already managed by another stack`

**Causes**:
- Resource is in another CloudFormation stack
- Resource was previously imported

**Solution**:
- Check CloudFormation console for existing stacks
- Remove resource from other stack first
- Use `cdk import` with `--force` (use with caution)

### Issue: Permission Denied

**Error**: `Access denied` or `Insufficient permissions`

**Causes**:
- IAM permissions insufficient
- Resource policy blocks access

**Solution**:
- Ensure IAM user/role has both:
  - Read permissions for the resource type
  - `cloudformation:*` permissions
- Check resource policies (S3, KMS, etc.)

## Verification

Before importing, verify resource identifiers:

### Lambda Function
```bash
aws lambda get-function --function-name order-processor
```

### DynamoDB Table
```bash
aws dynamodb describe-table --table-name users-table
```

### IAM Role
```bash
aws iam get-role --role-name lambda-execution-role
```

### IAM Policy
```bash
aws iam get-policy --policy-arn arn:aws:iam::123456789012:policy/my-policy
```

### S3 Bucket
```bash
aws s3api head-bucket --bucket my-assets-bucket
```

### EventBridge Rule
```bash
aws events describe-rule --name order-created-rule
```

## Mapping File Format

Complete example mapping file:

```json
{
  "MyStack": {
    "OrderProcessorFunction": "order-processor",
    "UsersTable": "users-table",
    "LambdaExecutionRole": "lambda-execution-role",
    "CustomPolicy": "arn:aws:iam::123456789012:policy/my-policy",
    "AssetsBucket": "my-assets-bucket",
    "OrderCreatedRule": "order-created-rule"
  }
}
```

## Best Practices

### 1. Verify Before Import
Always verify identifiers exist before importing:
```bash
# Verify Lambda
aws lambda get-function --function-name my-function

# Verify DynamoDB
aws dynamodb describe-table --table-name my-table
```

### 2. Use Consistent Naming
- Keep resource names consistent across AWS and CDK
- Use naming conventions that are easy to map
- Avoid special characters that differ between AWS and CDK

### 3. Document Exceptions
- Some resources may have been renamed
- Document any manual mappings
- Keep a log of identifier changes

### 4. Test in Dev First
- Always test import in dev/staging
- Verify the process works
- Document any issues for production

## Resources

- [CDK Import Command Reference](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-import)
- [CloudFormation Resource Import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import.html)

---

**Version**: 1.0
**Last Updated**: 2025-11-08
