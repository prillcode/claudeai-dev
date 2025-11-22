# aws-resource-discovery

Discover AWS resources and generate comprehensive inventory with properties and dependencies.

## Overview

`aws-resource-discovery` is a Claude Code skill that scans AWS accounts to discover existing resources and exports detailed configurations as structured JSON files. It's designed as the first step in bringing existing AWS infrastructure under CDK management.

**Version**: 1.0 MVP

## Features

- ✅ Discovers 6 core serverless resource types (Lambda, DynamoDB, IAM, S3, EventBridge)
- ✅ Captures complete resource configurations and properties
- ✅ Detects dependencies between resources automatically
- ✅ Supports flexible filtering (tags, name patterns, resource types)
- ✅ Handles AWS SSO profiles and standard profiles
- ✅ Exports structured JSON output for downstream processing
- ✅ Provides detailed error handling and progress reporting

## Quick Start

> **Important**: These setup steps are **required** before using the skill. When you ask Claude to use this skill, Claude will execute the Python script on your machine, which requires Python dependencies and AWS credentials to be configured first.

### Installation

1. **Install Python dependencies**:

**Recommended: Using a virtual environment** (isolates dependencies, prevents conflicts):
```bash
cd aws-resource-discovery

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Alternative: System-wide installation** (simpler but may cause dependency conflicts):
```bash
cd aws-resource-discovery
pip install -r requirements.txt
```

> **Why use a virtual environment?**
> - ✅ Isolates project dependencies from other Python projects
> - ✅ Prevents version conflicts (e.g., if another project needs a different boto3 version)
> - ✅ Easy to clean up (just delete the `venv` folder)
> - ✅ Ensures reproducible environment across different machines

2. **Configure AWS credentials** *(only if not already set up)*:

> **Note**: You can use any AWS profile already configured in your development environment. The `--profile` flag accepts any profile name from your `~/.aws/config` file.

```bash
# For standard profiles (only if creating new profile)
aws configure --profile prod

# For SSO profiles (only if creating new profile)
aws configure sso --profile prod

# For existing SSO profiles, just ensure you're logged in
aws sso login --profile prod

# To list your existing profiles
aws configure list-profiles
```

### Quick Test (Optional but Recommended)

Verify everything is working with a quick test:

```bash
# Make sure your virtual environment is activated
# Make sure you're logged into your AWS SSO profile (if using SSO)

python scripts/discover.py \
  --profile your-profile-name \
  --region us-east-1 \
  --resource-types lambda \
  --output-dir ./test-output

# Check the output
ls -la test-output/
cat test-output/metadata.json
```

If this works, you're ready! 🎉

### Usage Options

You can use this skill in two ways:

#### Option 1: Through Claude Code (Recommended)

**How it works**: You ask Claude to run the discovery, and Claude executes the Python script with the right arguments.

**Prerequisites**: Virtual environment activated, AWS credentials configured (from setup above).

**Simply ask Claude to invoke it**:

**Example requests:**
```
"Use aws-resource-discovery to scan us-east-1 using my 'dev' profile for all Lambda functions"

"Use aws-resource-discovery to find all resources tagged with 'project:myapp' in us-east-1 using profile 'prod'"

"Use aws-resource-discovery to get details for Lambda function 'order-processor' using profile 'staging'"
```

**Benefits of using through Claude**:
- 🎯 Natural language interface (no need to remember command-line flags)
- 🤖 Claude constructs the correct command automatically
- 📊 Claude can analyze and summarize the results for you
- 🔗 Claude can chain this with other skills (like cdk-code-generator)

Claude will:
1. Parse your requirements (profile, region, filters)
2. Execute the discovery script with the right arguments
3. Show you the results and summary

#### Option 2: Direct Python Execution

Run the Python script directly to test or debug:

**Full discovery**:
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1
# Uses default ./resource-inventory/
```

**With output prefix** (recommended for organized output):
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --output-prefix prod
# Creates ./prod-inventory/
```

**Filtered discovery**:
```bash
# By tags with prefix
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --tags project=myapp environment=production \
  --output-prefix myapp-prod

# By resource types with prefix
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda dynamodb \
  --output-prefix serverless

# By name pattern with matching prefix
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --name-pattern "order-*" \
  --output-prefix order
```

**Specific resource lookup**:
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --function-name order-processor \
  --traverse-dependencies \
  --output-prefix order-processor
```

## Output Structure

```
resource-inventory/
├── metadata.json              # Scan metadata and summary
├── lambdas.json              # Lambda function configurations
├── dynamodb-tables.json      # DynamoDB table schemas
├── iam-roles.json           # IAM role configurations
├── iam-policies.json        # IAM policy documents
├── s3-buckets.json          # S3 bucket configurations
├── eventbridge-rules.json   # EventBridge rule definitions
└── dependencies.json        # Resource dependency graph
```

## Supported Resources

| Resource Type | Properties | Dependencies |
|--------------|-----------|--------------|
| Lambda Functions | Runtime, handler, env vars, VPC config, layers | IAM role, DynamoDB tables, S3 buckets |
| DynamoDB Tables | Keys, indexes, streams, encryption, PITR, TTL | None (target of dependencies) |
| IAM Roles | Trust policy, attached policies, inline policies | IAM policies |
| IAM Policies | Policy documents, attachment count | None (target of dependencies) |
| S3 Buckets | Versioning, encryption, lifecycle, CORS, policy | None (target of dependencies) |
| EventBridge Rules | Event patterns, schedules, targets | Lambda functions |

See [supported_resources.md](./references/supported_resources.md) for complete details.

## Dependency Detection

The skill automatically detects these dependency patterns:

- **Lambda → IAM Role**: From function configuration
- **Lambda → DynamoDB**: From IAM policies + environment variables
- **Lambda → S3**: From IAM policies + environment variables
- **EventBridge → Lambda**: From rule targets
- **IAM Role → IAM Policy**: From attached policies

See [dependency_patterns.md](./references/dependency_patterns.md) for detection algorithms.

## Command-Line Options

### Required Arguments

- `--profile PROFILE`: AWS CLI profile name
- `--region REGION`: AWS region (e.g., us-east-1)

### Output Options

- `--output-dir DIR`: Explicit output directory path (default: ./resource-inventory)
- `--output-prefix PREFIX`: Prefix for output directory name (e.g., "cs" creates "./cs-inventory/")
  - If both `--output-dir` and `--output-prefix` are provided, `--output-dir` takes precedence
  - If neither is provided, defaults to "./resource-inventory/"
  - **Recommended**: Use `--output-prefix` matching your search pattern for organized output

### Filter Options

- `--tags KEY=VALUE [KEY=VALUE ...]`: Filter by tags (must match exactly)
- `--name-pattern PATTERN`: Filter by name (Unix glob, e.g., "order-*")
- `--resource-types TYPE [TYPE ...]`: Resource types to scan
  - Choices: `lambda`, `dynamodb`, `iam`, `s3`, `eventbridge`

### Specific Resource Options

- `--function-name NAME`: Scan specific Lambda function
- `--table-name NAME`: Scan specific DynamoDB table
- `--traverse-dependencies`: Also discover dependencies of specific resources

## IAM Permissions

Minimum required IAM permissions:

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
        "dynamodb:DescribeContinuousBackups",
        "dynamodb:DescribeTimeToLive",
        "dynamodb:ListTagsOfResource",
        "iam:ListRoles",
        "iam:GetRole",
        "iam:ListAttachedRolePolicies",
        "iam:ListRolePolicies",
        "iam:GetRolePolicy",
        "iam:ListRoleTags",
        "iam:ListPolicies",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:ListPolicyTags",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning",
        "s3:GetBucketEncryption",
        "s3:GetBucketLifecycleConfiguration",
        "s3:GetBucketCors",
        "s3:GetBucketPolicy",
        "s3:GetPublicAccessBlock",
        "s3:GetBucketTagging",
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

## Error Handling

The skill handles common errors gracefully:

- **Access Denied**: Skips resource types without sufficient permissions
- **SSO Session Expired**: Prompts to re-login with `aws sso login`
- **Invalid Profile**: Provides clear error with configuration instructions
- **API Rate Limiting**: Implements automatic retry with exponential backoff
- **Missing Resources**: Continues scan if individual resources fail

## Performance

Typical scan times:
- Small account (< 50 resources): 5-10 seconds
- Medium account (50-200 resources): 15-30 seconds
- Large account (200+ resources): 30-60 seconds

The tool implements:
- Parallel resource type scanning
- Automatic pagination handling
- Rate limit retry logic
- Efficient API call batching

## Examples

### Example 1: Production Environment Discovery
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --tags environment=production \
  --output-prefix prod
# Creates ./prod-inventory/
```

### Example 2: Specific Application Discovery
```bash
python scripts/discover.py \
  --profile dev \
  --region us-west-2 \
  --tags project=myapp \
  --name-pattern "myapp-*" \
  --output-prefix myapp
# Creates ./myapp-inventory/
```

### Example 3: Resources Starting with "cs-"
```bash
python scripts/discover.py \
  --profile techops \
  --region us-east-2 \
  --resource-types lambda dynamodb \
  --name-pattern "cs-*" \
  --output-prefix cs
# Creates ./cs-inventory/
```

### Example 4: Lambda and DynamoDB Only
```bash
python scripts/discover.py \
  --profile staging \
  --region eu-west-1 \
  --resource-types lambda dynamodb \
  --output-prefix serverless
# Creates ./serverless-inventory/
```

### Example 5: Specific Function with Dependencies
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --function-name order-processor \
  --traverse-dependencies \
  --output-prefix order-processor
# Creates ./order-processor-inventory/
```

### Example 6: Directory Already Exists
```bash
python scripts/discover.py \
  --profile prod \
  --region us-east-1 \
  --output-prefix prod

# Output:
# ⚠️  Warning: Output directory already exists!
#    Location: /path/to/prod-inventory
#
#    This directory contains existing discovery data.
#    Continuing will overwrite these files.
#
#    Do you want to continue? (yes/no): _
```

## Project Structure

```
aws-resource-discovery/
├── SKILL.md                      # Skill usage instructions for Claude
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── scripts/
│   ├── discover.py              # Main discovery script
│   ├── dependency_detector.py   # Dependency detection logic
│   ├── resource_scanners/       # Resource-specific scanners
│   │   ├── lambda_scanner.py
│   │   ├── dynamodb_scanner.py
│   │   ├── iam_scanner.py
│   │   ├── s3_scanner.py
│   │   └── eventbridge_scanner.py
│   └── utils/                   # Utility modules
│       ├── aws_client.py        # AWS client management
│       ├── filters.py           # Filtering logic
│       └── output_formatter.py  # JSON output formatting
├── references/                  # Documentation
│   ├── aws_api_reference.md
│   ├── supported_resources.md
│   └── dependency_patterns.md
└── assets/
    └── output-template/         # Example output files
```

## Troubleshooting

### Issue: "Profile 'prod' not found"
**Solution**: Check `~/.aws/config` for profile configuration.

### Issue: "SSO session expired"
**Solution**: Run `aws sso login --profile <name>` before discovery.

### Issue: "Access denied for Lambda:ListFunctions"
**Solution**: Ensure IAM user/role has required read permissions.

### Issue: "No resources found"
**Solution**:
- Check if filters are too restrictive
- Verify resources exist in specified region
- Try scanning without filters first

## Next Steps

After running discovery:

1. **Review Output**: Examine generated JSON files in output directory
2. **Analyze Dependencies**: Review `dependencies.json` for resource relationships
3. **Generate CDK Code**: Use `cdk-code-generator` skill with inventory output
4. **Organize Stacks**: Use `cdk-stack-organizer` skill to structure CDK project

## Development

### Running Tests
```bash
# Run with sample AWS account
python scripts/discover.py \
  --profile dev \
  --region us-east-1 \
  --resource-types lambda \
  --output-dir ./test-output
```

### Adding New Resource Types
1. Create scanner in `scripts/resource_scanners/`
2. Implement scan() method following existing patterns
3. Update `discover.py` to include new scanner
4. Update `dependency_detector.py` for new dependency patterns
5. Add documentation to `supported_resources.md`

## Roadmap

### v1.1 - Extended Serverless Resources (Planned)
- SQS queues
- SNS topics
- Lambda event source mappings
- Enhanced dependency detection

### v1.2 - API Services (Planned)
- API Gateway REST APIs
- API Gateway HTTP APIs
- AppSync GraphQL APIs

### v1.3 - Advanced Features (Future)
- Multi-region scanning
- Multi-account scanning
- Incremental updates and drift detection
- Cost estimation integration

## Contributing

This skill is part of the AWS Infrastructure Skills suite. See [AWS_CDK_IMPORTER_ROADMAP.md](../AWS_CDK_IMPORTER_ROADMAP.md) for the complete project vision.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please refer to the main project documentation or create an issue in the repository.

---

**Version**: 1.0 MVP
**Status**: Production Ready
**Last Updated**: 2025-11-07
