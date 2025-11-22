# Component Skills Reference

This document describes the four component skills that the AWS to CDK Importer orchestrator coordinates.

## Table of Contents

1. [Overview](#overview)
2. [aws-resource-discovery](#aws-resource-discovery)
3. [cdk-code-generator](#cdk-code-generator)
4. [cdk-stack-organizer](#cdk-stack-organizer)
5. [cdk-import-config-generator](#cdk-import-config-generator)
6. [Integration Points](#integration-points)

## Overview

The orchestrator coordinates four specialized skills in sequence. Each skill is responsible for one phase of the workflow and produces outputs that the next skill consumes.

```
aws-resource-discovery
         ↓
    resources.json
         ↓
cdk-code-generator
         ↓
  constructs/*.ts
         ↓
cdk-stack-organizer
         ↓
   stacks/*.ts
         ↓
cdk-import-config-generator
         ↓
  import configs & scripts
```

## aws-resource-discovery

### Purpose

Scans an AWS account to discover existing resources and create a comprehensive inventory.

### Responsibilities

- Connect to AWS using boto3
- Enumerate resources by type (Lambda, DynamoDB, S3, IAM, etc.)
- Retrieve detailed configuration for each resource
- Apply filters (resource types, tags, name patterns)
- Serialize results to JSON

### Input Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--profile` | Yes | AWS CLI profile name |
| `--region` | Yes | AWS region to scan |
| `--output-dir` | Yes | Directory to write results |
| `--resource-types` | No | Comma-separated list of resource types |
| `--tag-filter` | No | Filter by tag (Key=Value) |
| `--name-pattern` | No | Filter by name regex |

### Output Files

**`resources.json`** - Complete resource inventory

Structure:
```json
{
  "lambda": [
    {
      "name": "function-name",
      "arn": "arn:aws:lambda:...",
      "runtime": "python3.9",
      "handler": "index.handler",
      "role": "arn:aws:iam:...",
      "environment": {...},
      "tags": {...}
    }
  ],
  "dynamodb": [
    {
      "name": "table-name",
      "arn": "arn:aws:dynamodb:...",
      "attributes": [...],
      "keySchema": [...],
      "billingMode": "PAY_PER_REQUEST",
      "tags": {...}
    }
  ]
}
```

### Supported Resource Types

- `lambda` - Lambda Functions
- `dynamodb` - DynamoDB Tables
- `s3` - S3 Buckets
- `iam` - IAM Roles and Policies
- `sqs` - SQS Queues
- `sns` - SNS Topics
- `apigateway` - API Gateway REST APIs
- `eventbridge` - EventBridge Rules
- `stepfunctions` - Step Functions State Machines
- `ecs` - ECS Services and Task Definitions

### Key Features

- **Pagination handling** - Automatically handles AWS API pagination
- **Rate limiting** - Respects AWS API rate limits
- **Error handling** - Gracefully handles missing permissions
- **Parallel discovery** - Discovers multiple resource types concurrently
- **Resource relationships** - Captures cross-resource references

### Script Location

`aws-resource-discovery/scripts/discover.py`

### Example Invocation

```bash
python discover.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb \
  --output-dir ./discovery
```

## cdk-code-generator

### Purpose

Generates TypeScript CDK construct code from discovered AWS resources.

### Responsibilities

- Read resource inventory JSON
- Generate TypeScript construct for each resource
- Map AWS properties to CDK construct properties
- Resolve cross-resource references
- Create dependency manifest
- Generate metadata about generation process

### Input Files

**`resources.json`** - From aws-resource-discovery

### Input Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Path to resources.json |
| `--output-dir` | Yes | Directory for generated code |
| `--mode` | No | Generation mode: `reference` (default) or `full` |

### Generation Modes

**Reference Mode (`--mode reference`)**
- Generates constructs using `from*` methods
- Example: `Function.fromFunctionArn()`
- Read-only access to resources
- Does not manage resource lifecycle
- Best for: Initial imports, documentation

**Full Management Mode (`--mode full`)**
- Generates constructs using constructors
- Example: `new Function()`
- Full lifecycle management
- Can modify resource configuration
- Best for: Complete IaC migration

### Output Files

**`constructs/<resource-type>/<resource-name>.ts`** - Individual construct files

Example (`constructs/lambdas/my-function.ts`):
```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class MyFunctionConstruct extends Construct {
  public readonly function: lambda.IFunction;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Reference mode
    this.function = lambda.Function.fromFunctionArn(
      this,
      'MyFunction',
      'arn:aws:lambda:us-east-1:123456789012:function:my-function'
    );
  }
}
```

**`dependencies.json`** - NPM dependencies needed

```json
{
  "aws-cdk-lib": "^2.100.0",
  "constructs": "^10.0.0"
}
```

**`metadata.json`** - Generation metadata

```json
{
  "mode": "reference",
  "timestamp": "2025-11-08T10:30:00Z",
  "resourceCount": 25,
  "generatedFiles": 25
}
```

### Key Features

- **Property mapping** - Intelligent mapping of AWS → CDK properties
- **Reference resolution** - Handles cross-resource dependencies
- **Naming conventions** - Follows CDK and TypeScript best practices
- **Import statements** - Generates correct AWS CDK v2 imports
- **Type safety** - Generates fully typed TypeScript

### Script Location

`cdk-code-generator/scripts/generate.py`

### Example Invocation

```bash
python generate.py \
  --input ./discovery/resources.json \
  --output-dir ./cdk-generated \
  --mode reference
```

## cdk-stack-organizer

### Purpose

Organizes individual constructs into logical CDK stacks based on organizational strategy.

### Responsibilities

- Read generated construct files
- Apply organizational strategy to group resources
- Create stack definition files
- Generate CDK app entry point
- Create CDK project files (cdk.json, package.json, tsconfig.json)
- Copy/move constructs to organized structure

### Input Files

- **`constructs/**/*.ts`** - From cdk-code-generator
- **`dependencies.json`** - From cdk-code-generator
- **`metadata.json`** - From cdk-code-generator

### Input Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input-dir` | Yes | Directory with generated constructs |
| `--output-dir` | Yes | Directory for organized CDK project |
| `--strategy` | Yes | Organization strategy: `layer`, `service`, `tag`, `custom` |
| `--tag-key` | Conditional | Required if `--strategy tag` |
| `--custom-rules` | Conditional | Required if `--strategy custom` |

### Organization Strategies

**Layer Strategy (`--strategy layer`)**

Groups by architectural layer:
- `compute-stack` - Lambda, ECS, EC2, Batch
- `data-stack` - DynamoDB, RDS, ElastiCache, Redshift
- `storage-stack` - S3, EFS, FSx
- `messaging-stack` - SQS, SNS, EventBridge
- `networking-stack` - VPC, Subnets, Security Groups
- `iam-stack` - Roles, Policies, Users

**Service Strategy (`--strategy service`)**

Groups by AWS service:
- `lambda-stack` - All Lambda functions
- `dynamodb-stack` - All DynamoDB tables
- `s3-stack` - All S3 buckets
- etc.

**Tag Strategy (`--strategy tag --tag-key <key>`)**

Groups by tag value:
- If `--tag-key Application`:
  - `app-frontend-stack` - Resources tagged `Application=frontend`
  - `app-backend-stack` - Resources tagged `Application=backend`

**Custom Strategy (`--strategy custom --custom-rules <file>`)**

Groups by custom rules defined in JSON file.

### Output Structure

```
cdk-organized/
├── bin/
│   └── app.ts                      # CDK app entry point
├── lib/
│   ├── stacks/
│   │   ├── compute-stack.ts
│   │   ├── data-stack.ts
│   │   └── storage-stack.ts
│   └── constructs/
│       ├── lambdas/
│       ├── dynamodb/
│       └── s3/
├── cdk.json                        # CDK configuration
├── package.json                    # NPM package definition
├── tsconfig.json                   # TypeScript configuration
└── README.md                       # Project documentation
```

### Generated Stack Example

`lib/stacks/compute-stack.ts`:
```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MyFunctionConstruct } from '../constructs/lambdas/my-function';
import { ProcessorFunctionConstruct } from '../constructs/lambdas/processor-function';

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda functions
    new MyFunctionConstruct(this, 'MyFunction');
    new ProcessorFunctionConstruct(this, 'ProcessorFunction');
  }
}
```

### Generated App Entry Point

`bin/app.ts`:
```typescript
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ComputeStack } from '../lib/stacks/compute-stack';
import { DataStack } from '../lib/stacks/data-stack';
import { StorageStack } from '../lib/stacks/storage-stack';

const app = new cdk.App();

new ComputeStack(app, 'ComputeStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

new DataStack(app, 'DataStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

new StorageStack(app, 'StorageStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

app.synth();
```

### Key Features

- **Flexible strategies** - Multiple ways to organize
- **CDK best practices** - Follows official CDK patterns
- **Complete project** - Generates all required config files
- **Dependency management** - Properly sets up package.json
- **TypeScript config** - Correct tsconfig.json for CDK

### Script Location

`cdk-stack-organizer/scripts/organize.py`

### Example Invocation

```bash
python organize.py \
  --input-dir ./cdk-generated \
  --output-dir ./cdk-organized \
  --strategy layer
```

## cdk-import-config-generator

### Purpose

Generates CDK import configuration files and shell scripts to execute `cdk import` commands.

### Responsibilities

- Read resource inventory from discovery
- Read stack definitions from organized CDK project
- Map CDK logical IDs to AWS physical resource IDs
- Generate import configuration JSON for each stack
- Create shell scripts to run `cdk import`
- Create verification scripts

### Input Files

- **`resources.json`** - From aws-resource-discovery
- **`lib/stacks/*.ts`** - From cdk-stack-organizer

### Input Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--resources-file` | Yes | Path to resources.json |
| `--cdk-dir` | Yes | Path to organized CDK project |
| `--output-dir` | Yes | Directory for import configs |
| `--profile` | Yes | AWS CLI profile for imports |
| `--region` | Yes | AWS region for imports |

### Output Files

**`mappings/<stack-name>-import.json`** - Import mappings

Example (`mappings/compute-stack-import.json`):
```json
{
  "MyFunction": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
  "ProcessorFunction": "arn:aws:lambda:us-east-1:123456789012:function:processor-function"
}
```

**`scripts/import-<stack-name>.sh`** - Import script for individual stack

Example (`scripts/import-compute.sh`):
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

**`scripts/import-all.sh`** - Import all stacks sequentially

```bash
#!/bin/bash
set -e

echo "Importing all stacks..."

./import-compute.sh
./import-data.sh
./import-storage.sh

echo "✓ All stacks imported successfully"
```

**`scripts/verify-imports.sh`** - Verify import success

```bash
#!/bin/bash

echo "Verifying imports..."
cd ../../cdk-organized

for stack in ComputeStack DataStack StorageStack; do
  echo "Checking $stack..."
  cdk diff $stack --profile prod --region us-east-1
done

echo "✓ Verification complete"
```

### Key Features

- **Logical ID mapping** - Maps construct IDs to resource ARNs
- **Import scripts** - Executable shell scripts for imports
- **Error handling** - Scripts include error checking
- **Verification** - Automated verification of import success
- **Incremental imports** - Individual stack import scripts

### Script Location

`cdk-import-config-generator/scripts/generate_import_configs.py`

### Example Invocation

```bash
python generate_import_configs.py \
  --resources-file ./discovery/resources.json \
  --cdk-dir ./cdk-organized \
  --output-dir ./import-configs \
  --profile prod \
  --region us-east-1
```

## Integration Points

### Phase 1 → Phase 2

**Output:** `discovery/resources.json`
**Input:** `cdk-code-generator --input resources.json`

**Contract:**
- JSON object with resource types as keys
- Each resource type contains array of resource objects
- Each resource must have: `name`, `arn`, and type-specific properties

### Phase 2 → Phase 3

**Output:** `cdk-generated/constructs/**/*.ts`
**Input:** `cdk-stack-organizer --input-dir cdk-generated`

**Contract:**
- TypeScript construct files organized by resource type
- Each construct exports a class extending `Construct`
- File naming: `<resource-name>.ts`
- dependencies.json and metadata.json present

### Phase 3 → Phase 4

**Output:** `cdk-organized/lib/stacks/*.ts`
**Input:** `cdk-import-config-generator --cdk-dir cdk-organized`

**Contract:**
- Complete CDK project structure
- Stack files in `lib/stacks/`
- Each stack file contains construct instantiations
- Construct IDs must be extractable from code

### Phase 1 & Phase 3 → Phase 4

**Inputs:**
- `resources.json` (Phase 1)
- `lib/stacks/*.ts` (Phase 3)

**Contract:**
- Ability to map construct logical IDs to resource ARNs
- ARNs in resources.json match those referenced in constructs
- Resource names are consistent across both files

## Skill Independence

Each component skill can be used independently:

**aws-resource-discovery alone:**
- Document existing AWS infrastructure
- Audit resource configurations
- Export infrastructure inventory

**cdk-code-generator alone:**
- Generate CDK code from exported infrastructure
- Create reference constructs for documentation
- Bootstrap CDK migration projects

**cdk-stack-organizer alone:**
- Reorganize existing CDK projects
- Refactor stack boundaries
- Apply new organizational strategies

**cdk-import-config-generator alone:**
- Generate import configs for hand-written CDK code
- Create import scripts for existing projects
- Automate manual import processes

## Error Handling Between Skills

The orchestrator validates outputs between phases:

1. **After Phase 1:** Validates `resources.json` structure
2. **After Phase 2:** Validates construct files exist
3. **After Phase 3:** Validates CDK project structure
4. **After Phase 4:** Validates import configs and scripts

If validation fails, the workflow stops and reports the error.

## Extending the Skills

Each skill can be extended independently:

**Adding new resource types:**
- Update aws-resource-discovery discovery logic
- Add generator in cdk-code-generator
- Update cdk-stack-organizer strategy mappings
- Update cdk-import-config-generator ID extraction

**Adding new strategies:**
- Add strategy to cdk-stack-organizer
- Update orchestrator to pass new strategy parameters

**Adding new generation modes:**
- Add mode to cdk-code-generator
- Update orchestrator to pass mode parameter

## Troubleshooting Integration Issues

### resources.json not found

**Cause:** Phase 1 failed or didn't write output
**Solution:** Check Phase 1 logs, verify output directory permissions

### No constructs generated

**Cause:** Phase 2 couldn't parse resources.json
**Solution:** Validate resources.json structure, check for unsupported resource types

### Stack organization failed

**Cause:** Invalid strategy or missing constructs
**Solution:** Verify strategy parameters, ensure Phase 2 completed successfully

### Import config generation failed

**Cause:** Can't extract construct IDs from stack files
**Solution:** Verify stack files are valid TypeScript, check for non-standard patterns

## Version Compatibility

All component skills must use compatible versions:

- **v1.x** - Initial release (Lambda, DynamoDB, S3, IAM)
- **v2.x** - Current version (adds EventBridge, Step Functions, ECS)
- **v3.x** - Future (will add CloudFront, Route53, EC2)

Orchestrator v2.0 requires all component skills to be v2.x.

Check versions:
```bash
python aws-resource-discovery/scripts/discover.py --version
python cdk-code-generator/scripts/generate.py --version
python cdk-stack-organizer/scripts/organize.py --version
python cdk-import-config-generator/scripts/generate_import_configs.py --version
```
