# AWS to CDK Importer - Complete Workflow Guide

This guide provides a comprehensive walkthrough of the entire AWS to CDK import workflow, from initial resource discovery through final import execution.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase-by-Phase Walkthrough](#phase-by-phase-walkthrough)
4. [Real-World Examples](#real-world-examples)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)

## Overview

The AWS to CDK Importer orchestrates a 5-phase workflow that transforms existing AWS infrastructure into a fully-functional CDK project ready for `cdk import`.

**Workflow Summary:**

```
AWS Account → Discovery → Code Gen → Organization → Import Configs → CDK Project
```

**Time Estimate:**
- Small environments (10-20 resources): 2-5 minutes
- Medium environments (50-100 resources): 5-15 minutes
- Large environments (200+ resources): 15-30 minutes

## Prerequisites

### Required Tools

1. **AWS CLI** - Configured with credentials
   ```bash
   aws configure
   ```

2. **Python 3.8+** - For orchestrator scripts
   ```bash
   python3 --version
   ```

3. **Node.js 16+** - For CDK project
   ```bash
   node --version
   ```

4. **AWS CDK** - For import execution
   ```bash
   npm install -g aws-cdk
   ```

### Required IAM Permissions

The AWS profile used must have permissions to:
- **Read** access to all resource types being imported
- **Describe** operations for resource discovery
- **List** operations for resource enumeration

Example minimal IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "dynamodb:ListTables",
        "dynamodb:DescribeTable",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "iam:ListRoles",
        "iam:GetRole"
      ],
      "Resource": "*"
    }
  ]
}
```

### Component Skills

All four component skills must be installed:
- `aws-resource-discovery`
- `cdk-code-generator`
- `cdk-stack-organizer`
- `cdk-import-config-generator`

## Phase-by-Phase Walkthrough

### Phase 1: Resource Discovery

**Purpose:** Scan AWS account and create a comprehensive inventory of existing resources.

**What Happens:**
1. Connects to AWS using specified profile and region
2. Enumerates all resources of specified types (or all supported types if not filtered)
3. Retrieves detailed configuration for each resource
4. Saves results to `discovery/resources.json`

**Inputs:**
- AWS profile name
- AWS region
- Optional: Resource type filters
- Optional: Tag filters
- Optional: Name pattern filters

**Output Structure:**
```json
{
  "lambda": [
    {
      "name": "my-function",
      "arn": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
      "runtime": "python3.9",
      "handler": "index.handler",
      ...
    }
  ],
  "dynamodb": [
    {
      "name": "my-table",
      "arn": "arn:aws:dynamodb:us-east-1:123456789012:table/my-table",
      "attributes": [...],
      "keySchema": [...],
      ...
    }
  ]
}
```

**Common Issues:**
- **Insufficient permissions:** Ensure IAM policy allows read access
- **No resources found:** Check filters and verify resources exist in specified region
- **Timeout:** Large accounts may need longer timeout (adjust in skill_invoker.py)

### Phase 2: CDK Code Generation

**Purpose:** Generate TypeScript CDK constructs for each discovered resource.

**What Happens:**
1. Reads resource inventory from Phase 1
2. For each resource, generates a TypeScript construct file
3. Maps AWS resource properties to CDK construct properties
4. Resolves cross-resource references (e.g., Lambda using DynamoDB table)
5. Creates `dependencies.json` with required NPM packages
6. Creates `metadata.json` with generation information

**Modes:**

**Reference Mode (default):**
- Generates constructs that reference existing resources
- Uses `from*` methods (e.g., `Function.fromFunctionArn()`)
- Read-only access to resources
- Best for: Initial imports, documentation, gradual migration

**Full Management Mode:**
- Generates constructs that fully define resources
- Uses constructor methods (e.g., `new Function()`)
- Allows full lifecycle management
- Best for: Complete IaC migration, new CDK-managed infrastructure

**Output Structure:**
```
cdk-generated/
├── constructs/
│   ├── lambdas/
│   │   ├── my-function.ts
│   │   └── another-function.ts
│   ├── dynamodb/
│   │   └── my-table.ts
│   └── s3/
│       └── my-bucket.ts
├── dependencies.json
└── metadata.json
```

**Example Generated Construct (Reference Mode):**
```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class MyFunctionConstruct extends cdk.Construct {
  public readonly function: lambda.IFunction;

  constructor(scope: cdk.Construct, id: string) {
    super(scope, id);

    this.function = lambda.Function.fromFunctionArn(
      this,
      'MyFunction',
      'arn:aws:lambda:us-east-1:123456789012:function:my-function'
    );
  }
}
```

### Phase 3: Stack Organization

**Purpose:** Group individual constructs into logical CDK stacks based on organizational strategy.

**What Happens:**
1. Analyzes generated constructs
2. Applies organizational strategy to group resources
3. Creates stack files with proper imports
4. Generates CDK app entry point (`bin/app.ts`)
5. Creates CDK project configuration files
6. Moves constructs to organized project structure

**Organization Strategies:**

**Layer Strategy (default):**
Groups by architectural layer:
- `compute-stack.ts` - Lambda, ECS, EC2
- `data-stack.ts` - DynamoDB, RDS, ElastiCache
- `storage-stack.ts` - S3, EFS
- `networking-stack.ts` - VPC, Subnets, Security Groups
- `iam-stack.ts` - Roles, Policies

**Service Strategy:**
Groups by AWS service:
- `lambda-stack.ts` - All Lambda functions
- `dynamodb-stack.ts` - All DynamoDB tables
- `s3-stack.ts` - All S3 buckets

**Tag Strategy:**
Groups by AWS resource tag value:
- `--tag-key Application` groups by Application tag
- `--tag-key Environment` groups by Environment tag

**Custom Strategy:**
Groups by user-defined rules in JSON file:
```json
{
  "stacks": {
    "api-stack": {
      "resources": ["*api*", "*gateway*"]
    },
    "data-stack": {
      "resources": ["*table*", "*bucket*"]
    }
  }
}
```

**Output Structure:**
```
cdk-organized/
├── bin/
│   └── app.ts                    # CDK app entry point
├── lib/
│   ├── stacks/
│   │   ├── compute-stack.ts      # Stack definitions
│   │   ├── data-stack.ts
│   │   └── storage-stack.ts
│   └── constructs/               # Individual constructs
│       ├── lambdas/
│       ├── dynamodb/
│       └── s3/
├── cdk.json                      # CDK configuration
├── package.json                  # NPM dependencies
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # Project documentation
```

**Example Stack File:**
```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MyFunctionConstruct } from '../constructs/lambdas/my-function';
import { AnotherFunctionConstruct } from '../constructs/lambdas/another-function';

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new MyFunctionConstruct(this, 'MyFunction');
    new AnotherFunctionConstruct(this, 'AnotherFunction');
  }
}
```

### Phase 4: Import Configuration Generation

**Purpose:** Create CDK import mapping files and shell scripts to execute imports.

**What Happens:**
1. Reads resource inventory from Phase 1
2. Reads stack definitions from Phase 3
3. Maps CDK logical IDs to AWS physical resource IDs
4. Generates import configuration JSON for each stack
5. Creates shell scripts to execute `cdk import` commands
6. Creates verification scripts to check import status

**Import Mapping Format:**

Each stack gets an import configuration file that maps logical IDs to physical IDs:

```json
{
  "MyFunction": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
  "AnotherFunction": "arn:aws:lambda:us-east-1:123456789012:function:another-function"
}
```

**Output Structure:**
```
import-configs/
├── mappings/
│   ├── compute-stack-import.json
│   ├── data-stack-import.json
│   └── storage-stack-import.json
└── scripts/
    ├── import-all.sh              # Import all stacks
    ├── import-compute.sh          # Import compute stack
    ├── import-data.sh             # Import data stack
    ├── import-storage.sh          # Import storage stack
    └── verify-imports.sh          # Verify import success
```

**Example Import Script:**
```bash
#!/bin/bash
set -e

echo "Importing Compute Stack..."
cd ../../cdk-organized

cdk import ComputeStack \
  --resource-mapping ../import-configs/mappings/compute-stack-import.json \
  --profile prod \
  --region us-east-1

echo "✓ Compute Stack imported successfully"
```

### Phase 5: Summary Report Generation

**Purpose:** Create a comprehensive report of the entire workflow with statistics and next steps.

**What Happens:**
1. Aggregates results from all previous phases
2. Calculates totals and summaries
3. Generates formatted markdown report
4. Saves to `IMPORT_SUMMARY.md` in output directory

**Report Contents:**
- Configuration summary (profile, region, filters)
- Resource discovery statistics
- Code generation statistics
- Stack organization details
- Import configuration details
- File location references
- Next steps for user

## Real-World Examples

### Example 1: Import Microservices API

**Scenario:** Import a microservices API with Lambda functions, API Gateway, and DynamoDB tables.

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb,apigateway \
  --tag-filter "Project=MyAPI" \
  --strategy layer \
  --output ./my-api-cdk
```

**Expected Output:**
- 15 Lambda functions
- 5 DynamoDB tables
- 1 API Gateway
- 3 stacks: compute, data, api
- Total time: ~5 minutes

### Example 2: Import Data Pipeline

**Scenario:** Import a data processing pipeline with S3 buckets, Lambda functions, and Glue jobs.

```bash
python scripts/orchestrate.py \
  --profile data-engineering \
  --region us-west-2 \
  --resource-types s3,lambda,glue \
  --name-pattern "^data-pipeline-.*" \
  --strategy service \
  --output ./data-pipeline-cdk
```

**Expected Output:**
- 10 S3 buckets
- 8 Lambda functions
- 3 Glue jobs
- 3 stacks: s3, lambda, glue
- Total time: ~8 minutes

### Example 3: Import Multi-Environment Resources

**Scenario:** Import production resources organized by application.

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region eu-west-1 \
  --tag-filter "Environment=Production" \
  --strategy tag \
  --tag-key Application \
  --output ./prod-infrastructure-cdk
```

**Expected Output:**
- Resources grouped by Application tag value
- One stack per application
- Total time: ~12 minutes

## Advanced Usage

### Dry Run Mode

Preview the workflow without making changes:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --dry-run \
  --verbose
```

### Verbose Logging

Enable detailed logging for troubleshooting:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --verbose \
  --output ./my-project
```

### Custom Organization Rules

Create a custom rules file `my-rules.json`:

```json
{
  "stacks": {
    "frontend-stack": {
      "resources": ["*cloudfront*", "*s3*website*"]
    },
    "backend-stack": {
      "resources": ["*lambda*", "*apigateway*"]
    },
    "database-stack": {
      "resources": ["*dynamodb*", "*rds*"]
    }
  }
}
```

Use it:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --strategy custom \
  --custom-rules ./my-rules.json \
  --output ./my-project
```

## Best Practices

### 1. Start with Read-Only Reference Mode

Always start with reference mode (default) to:
- Document existing infrastructure
- Validate generated code
- Test imports without risk
- Gradually migrate to full management

### 2. Use Tag Filters for Large Environments

For accounts with many resources:
- Tag resources before import
- Use `--tag-filter` to limit scope
- Import incrementally by tag

### 3. Organize by Architecture, Not Service

Use layer strategy for most projects:
- More maintainable
- Better separation of concerns
- Clearer dependencies
- Easier to understand

### 4. Review Generated Code Before Import

Always review before importing:
```bash
cd my-project/cdk-organized
cat lib/stacks/*.ts
cat lib/constructs/**/*.ts
```

### 5. Test Synthesis First

Validate generated CDK code:
```bash
cd my-project/cdk-organized
npm install
npm run build
cdk synth
```

### 6. Import One Stack at a Time

Don't use `import-all.sh` initially:
```bash
cd import-configs/scripts
./import-compute.sh      # Test with one stack first
./verify-imports.sh      # Check it worked
./import-data.sh         # Continue with others
```

### 7. Version Control Immediately

Initialize git right after generation:
```bash
cd my-project/cdk-organized
git init
git add .
git commit -m "Initial CDK project from AWS import"
```

### 8. Keep Discovery Output

Preserve the `discovery/` directory:
- Useful for debugging
- Can regenerate code if needed
- Documents original AWS configuration

### 9. Use Incremental Imports

For large environments:
1. Import critical resources first
2. Test and validate
3. Import additional resources
4. Iterate until complete

### 10. Document Custom Decisions

Add comments to generated code explaining:
- Why certain organization was chosen
- Any manual modifications made
- Resource relationships and dependencies
- Future migration plans

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  User provides: --profile, --region, --resource-types, etc.    │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │   Phase 1: Resource Discovery             │
        │   • Connect to AWS                        │
        │   • Enumerate resources                   │
        │   • Save to resources.json                │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │   Phase 2: CDK Code Generation            │
        │   • Read resources.json                   │
        │   • Generate TypeScript constructs        │
        │   • Create dependencies.json              │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │   Phase 3: Stack Organization             │
        │   • Group constructs by strategy          │
        │   • Create stack files                    │
        │   • Generate CDK app                      │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │   Phase 4: Import Configuration           │
        │   • Map logical IDs to physical IDs       │
        │   • Generate import JSON files            │
        │   • Create shell scripts                  │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │   Phase 5: Summary Report                 │
        │   • Aggregate statistics                  │
        │   • Generate IMPORT_SUMMARY.md            │
        │   • Display next steps                    │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Output: Complete CDK project ready for cdk import             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Next Steps After Completion

After the orchestrator completes successfully:

1. **Review the summary report**
   ```bash
   cat my-project/IMPORT_SUMMARY.md
   ```

2. **Install dependencies**
   ```bash
   cd my-project/cdk-organized
   npm install
   ```

3. **Build and synthesize**
   ```bash
   npm run build
   cdk synth
   ```

4. **Review generated code**
   - Check stack files
   - Review construct definitions
   - Verify resource mappings

5. **Test import with one stack**
   ```bash
   cd ../import-configs/scripts
   ./import-compute.sh
   ```

6. **Verify import**
   ```bash
   ./verify-imports.sh
   ```

7. **Import remaining stacks**
   ```bash
   ./import-all.sh
   ```

8. **Initialize version control**
   ```bash
   cd ../../cdk-organized
   git init
   git add .
   git commit -m "Initial commit: AWS to CDK import"
   ```

9. **Set up CI/CD**
   - Add GitHub Actions / GitLab CI
   - Configure automated testing
   - Set up deployment pipelines

10. **Document and share**
    - Add README with context
    - Document architecture decisions
    - Share with team

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CDK Import Documentation](https://docs.aws.amazon.com/cdk/latest/guide/cli.html#cli-import)
- Component Skill Documentation:
  - `aws-resource-discovery/README.md`
  - `cdk-code-generator/README.md`
  - `cdk-stack-organizer/README.md`
  - `cdk-import-config-generator/README.md`
