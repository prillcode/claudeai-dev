---
name: cdk-code-generator
description: Generate TypeScript CDK v2 code from AWS resource discovery JSON files. This skill should be used after aws-resource-discovery to create either reference-only imports or full management constructs for Lambda, DynamoDB, IAM, S3, and EventBridge resources.
---

# cdk-code-generator

Generate TypeScript CDK v2 code from AWS resource discovery JSON files.

## Purpose

This skill generates TypeScript CDK code from the JSON output of `aws-resource-discovery`. It supports both reference-only imports (`.fromAttributes()`) and full management mode (complete construct definitions).

## Usage

### Through Claude Code (Recommended)

Claude will execute the generation script based on your natural language requests.

**Example requests:**

```
"Use cdk-code-generator to create reference imports for the resources in test-techops-inventory/"

"Use cdk-code-generator to generate full CDK constructs for all Lambda functions in test-techops-inventory/"

"Use cdk-code-generator to generate TypeScript CDK code in full management mode from test-techops-inventory/"
```

### Direct Python Execution

```bash
# Reference-only mode (default)
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/test-techops-inventory \
  --output-dir ./cdk-generated \
  --mode reference

# Full management mode
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/test-techops-inventory \
  --output-dir ./cdk-generated \
  --mode full

# Mixed mode (specify per resource type)
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/test-techops-inventory \
  --output-dir ./cdk-generated \
  --lambda-mode full \
  --dynamodb-mode reference \
  --iam-mode reference
```

## Command-Line Options

### Required Arguments
- `--input-dir DIR`: Path to resource inventory directory (from aws-resource-discovery)
- `--output-dir DIR`: Output directory for generated CDK code

### Mode Options
- `--mode MODE`: Default generation mode (choices: `reference`, `full`) [default: reference]
- `--lambda-mode MODE`: Override mode for Lambda functions
- `--dynamodb-mode MODE`: Override mode for DynamoDB tables
- `--iam-mode MODE`: Override mode for IAM roles/policies
- `--s3-mode MODE`: Override mode for S3 buckets
- `--eventbridge-mode MODE`: Override mode for EventBridge rules

### Other Options
- `--cdk-version VERSION`: Target CDK version [default: 2.0.0]
- `--include-comments`: Include detailed comments in generated code [default: true]
- `--format-code`: Auto-format generated TypeScript [default: true]

## Output Structure

```
cdk-generated/
├── metadata.json                      # Generation metadata
├── constructs/
│   ├── lambdas/
│   │   ├── order-processor.ts
│   │   ├── user-service.ts
│   │   └── index.ts                   # Barrel export
│   ├── dynamodb/
│   │   ├── users-table.ts
│   │   └── index.ts
│   ├── iam/
│   │   ├── lambda-execution-role.ts
│   │   └── index.ts
│   ├── s3/
│   │   ├── assets-bucket.ts
│   │   └── index.ts
│   └── eventbridge/
│       ├── order-created-rule.ts
│       └── index.ts
├── dependencies.json                  # Cross-construct dependencies
├── package.json                       # CDK dependencies
└── README.md                          # Instructions for using generated code
```

## Generation Modes

### Reference-Only Mode

Generates `.fromAttributes()` calls for existing resources you need to reference:

```typescript
// lambdas/order-processor.ts
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class OrderProcessorFunction {
  public readonly function: lambda.IFunction;

  constructor(scope: Construct, id: string) {
    this.function = lambda.Function.fromFunctionArn(
      scope,
      id,
      'arn:aws:lambda:us-east-1:123456789012:function:order-processor'
    );
  }
}
```

### Full Management Mode

Generates complete construct definitions for CDK to manage:

```typescript
// lambdas/order-processor.ts
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class OrderProcessorFunction {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, role: iam.IRole) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'order-processor',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('./lambda/order-processor'),
      memorySize: 256,
      timeout: Duration.seconds(30),
      role: role,
      environment: {
        TABLE_NAME: 'orders-table',
        REGION: 'us-east-1',
      },
      description: 'Process order events from EventBridge',
    });
  }
}
```

## Supported Resources (v1.0 MVP)

- ✅ Lambda functions
- ✅ DynamoDB tables
- ✅ IAM roles
- ✅ IAM policies
- ✅ S3 buckets
- ✅ EventBridge rules

## Implementation Details

### Property Mapping

The generator maps AWS API properties to CDK construct properties:
- AWS runtime values → CDK Runtime enums
- Timeout seconds → CDK Duration objects
- IAM policy documents → CDK Policy statements
- Resource configurations → Typed CDK props

### Dependency Handling

The generator preserves resource dependencies:
- Lambda → IAM Role references
- Lambda → DynamoDB table references
- EventBridge → Lambda target references

### Code Quality

Generated code follows best practices:
- Proper TypeScript typing
- CDK v2 constructs
- Idiomatic naming conventions
- Helpful inline comments
- Organized file structure

## Next Steps After Generation

1. **Review Generated Code**: Examine TypeScript files in output directory
2. **Install Dependencies**: Run `npm install` in output directory
3. **Update Code Placeholders**: Replace any TODO comments with actual values
4. **Test Compilation**: Run `npm run build` to verify TypeScript compiles
5. **Create Stacks**: Use `cdk-stack-organizer` skill to organize into stacks
6. **Deploy**: Use `cdk deploy` or `cdk import` as needed

## Version

**Version**: 1.0 MVP
**Status**: In Development
**Last Updated**: 2025-11-07
