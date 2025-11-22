# cdk-code-generator

Generate TypeScript CDK v2 code from discovered AWS resources.

## Overview

`cdk-code-generator` is a Claude Code skill that transforms AWS resource inventory JSON files (from `aws-resource-discovery`) into production-ready TypeScript CDK code. It supports both reference-only imports and full management modes.

**Version**: 1.0 MVP

## Features

- ✅ Generates TypeScript CDK v2 code from resource JSON
- ✅ Supports 6 core serverless resource types (Lambda, DynamoDB, IAM, S3, EventBridge)
- ✅ Two generation modes: reference-only and full management
- ✅ Per-resource-type mode overrides
- ✅ Proper TypeScript typing and imports
- ✅ Preserves resource dependencies
- ✅ Organized file structure with barrel exports
- ✅ Includes package.json with CDK dependencies

## Quick Start

> **Important**: No installation required! This skill uses Python standard library only (Python 3.12+).

### Installation

**No external dependencies needed** - uses Python 3.12+ standard library.

```bash
cd cdk-code-generator
# No pip install required!
```

### Quick Test (Optional but Recommended)

Generate code from discovered resources:

```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/test-techops-inventory \
  --output-dir ./test-output \
  --mode reference

# Check the output
ls -la test-output/constructs/
```

If this works, you're ready! 🎉

### Usage Options

You can use this skill in two ways:

#### Option 1: Through Claude Code (Recommended)

**How it works**: You ask Claude to generate CDK code, and Claude executes the Python script.

**Simply ask Claude to invoke it**:

**Example requests:**
```
"Use cdk-code-generator to create reference imports for resources in test-techops-inventory/"

"Use cdk-code-generator to generate full management CDK code from test-techops-inventory/"

"Use cdk-code-generator to generate full Lambda constructs but reference-only DynamoDB imports"
```

**Benefits of using through Claude**:
- 🎯 Natural language interface
- 🤖 Claude constructs the correct command automatically
- 📊 Claude can review and explain the generated code
- 🔗 Claude can chain this with other skills

#### Option 2: Direct Python Execution

Run the Python script directly:

**Reference-only mode** (generate `.fromAttributes()` calls):
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/resource-inventory \
  --output-dir ./cdk-generated \
  --mode reference
```

**Full management mode** (generate complete constructs):
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/resource-inventory \
  --output-dir ./cdk-generated \
  --mode full
```

**Mixed mode** (different modes per resource type):
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/prod-inventory \
  --output-dir ./cdk-generated \
  --lambda-mode full \
  --dynamodb-mode reference \
  --iam-mode reference \
  --s3-mode reference
```

**With specific CDK version**:
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/resource-inventory \
  --output-dir ./cdk-generated \
  --mode full \
  --cdk-version 2.100.0
```

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
│   │   ├── orders-table.ts
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

Use this when you want to reference existing AWS resources in your CDK code without managing them.

**Generated code example:**
```typescript
// constructs/lambdas/order-processor.ts
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class OrderProcessorFunctionRef {
  public readonly function: lambda.IFunction;

  constructor(scope: Construct, id: string) {
    // Reference existing Lambda function
    this.function = lambda.Function.fromFunctionArn(
      scope,
      id,
      'arn:aws:lambda:us-east-1:123456789012:function:order-processor'
    );
  }
}
```

**Use cases:**
- Referencing resources managed outside CDK
- Cross-stack resource references
- Existing resources you don't want CDK to manage
- Gradual migration to CDK

### Full Management Mode

Use this when you want CDK to fully manage the resources.

**Generated code example:**
```typescript
// constructs/lambdas/order-processor.ts
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface OrderProcessorFunctionProps {
  role: iam.IRole;
}

export class OrderProcessorFunction {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: OrderProcessorFunctionProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'order-processor',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('./lambda/order-processor'), // TODO: Update path
      memorySize: 256,
      timeout: Duration.seconds(30),
      role: props.role,
      environment: {
        TABLE_NAME: 'orders-table',
        REGION: 'us-east-1',
      },
      description: 'Process order events from EventBridge',
    });
  }
}
```

**Use cases:**
- Bringing existing resources under CDK management
- Full infrastructure-as-code control
- Using `cdk import` to import existing resources
- New infrastructure following existing patterns

## Supported Resources

| Resource Type | Reference Mode | Full Management Mode |
|--------------|----------------|---------------------|
| Lambda Functions | `.fromFunctionArn()` | `new lambda.Function()` |
| DynamoDB Tables | `.fromTableName()` | `new dynamodb.Table()` |
| IAM Roles | `.fromRoleArn()` | `new iam.Role()` |
| IAM Policies | `.fromManagedPolicyArn()` | `new iam.ManagedPolicy()` |
| S3 Buckets | `.fromBucketName()` | `new s3.Bucket()` |
| EventBridge Rules | `.fromEventRuleArn()` | `new events.Rule()` |

See [references/cdk_construct_mappings.md](./references/cdk_construct_mappings.md) for complete property mappings.

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

## Examples

### Example 1: Reference-Only Generation
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/prod-inventory \
  --output-dir ./cdk-generated-prod-refs \
  --mode reference
# Creates reference imports for all resources
```

### Example 2: Full Management Generation
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/dev-inventory \
  --output-dir ./cdk-generated-dev \
  --mode full
# Creates complete CDK constructs for all resources
```

### Example 3: Mixed Mode (Lambdas Full, Everything Else References)
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/staging-inventory \
  --output-dir ./cdk-generated-staging \
  --lambda-mode full \
  --dynamodb-mode reference \
  --iam-mode reference \
  --s3-mode reference \
  --eventbridge-mode reference
# Lambda functions as full constructs, others as references
```

### Example 4: Specific CDK Version
```bash
python scripts/generate.py \
  --input-dir ../aws-resource-discovery/resource-inventory \
  --output-dir ./cdk-generated \
  --mode full \
  --cdk-version 2.100.0
# Generates code for CDK 2.100.0
```

## Generated Code Structure

### Construct Files

Each resource gets its own TypeScript file with a class that wraps the CDK construct:

```typescript
// constructs/lambdas/my-function.ts
export class MyFunctionRef {
  public readonly function: lambda.IFunction;
  constructor(scope: Construct, id: string) { /* ... */ }
}
```

### Barrel Exports (index.ts)

Each resource type directory includes an `index.ts` that re-exports all constructs:

```typescript
// constructs/lambdas/index.ts
export * from './my-function';
export * from './another-function';
```

### Dependencies File

The `dependencies.json` file maps resource dependencies:

```json
{
  "order-processor": {
    "type": "lambda",
    "dependencies": {
      "iam_role": "arn:aws:iam::123:role/lambda-role",
      "dynamodb_tables": ["orders-table"]
    }
  }
}
```

### Package.json

Includes all required CDK dependencies:

```json
{
  "name": "cdk-generated",
  "version": "1.0.0",
  "dependencies": {
    "aws-cdk-lib": "^2.0.0",
    "constructs": "^10.0.0"
  },
  "devDependencies": {
    "@types/node": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

## Next Steps After Generation

1. **Review Generated Code**:
   ```bash
   cd cdk-generated
   ls -R constructs/
   ```

2. **Install Dependencies**:

   The generated constructs are TypeScript files that need CDK dependencies:

   ```bash
   # Using npm
   npm install

   # Or using pnpm (recommended)
   pnpm install
   ```

3. **Update Placeholders**:
   - Search for `TODO` comments in generated code
   - Update code asset paths (e.g., `lambda.Code.fromAsset('./lambda/...')`)
   - Replace placeholder secrets/sensitive values

4. **Test Compilation**:
   ```bash
   # Using npm
   npm run build

   # Or using pnpm
   pnpm run build

   # Or directly with tsc
   npx tsc
   ```

5. **Organize into Stacks**:
   ```bash
   # Use cdk-stack-organizer skill
   "Use cdk-stack-organizer to organize constructs into logical stacks"
   ```

6. **Deploy or Import**:
   ```bash
   # For new resources
   cdk deploy

   # For existing resources
   cdk import MyStack
   ```

> **Note**: The Python skill itself requires no installation (pure Python stdlib), but the **generated TypeScript constructs** need npm/pnpm to install CDK dependencies.

## Project Structure

```
cdk-code-generator/
├── SKILL.md                      # Skill usage instructions for Claude
├── README.md                     # This file
├── requirements.txt              # Python dependencies (none for MVP)
├── scripts/
│   ├── generate.py              # Main generation script
│   ├── generators/               # Resource-specific generators
│   │   ├── __init__.py
│   │   ├── lambda_generator.py
│   │   ├── dynamodb_generator.py
│   │   ├── iam_generator.py
│   │   ├── s3_generator.py
│   │   └── eventbridge_generator.py
│   ├── templates/                # Code templates
│   │   ├── __init__.py
│   │   └── construct_template.py
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── typescript_formatter.py
│       └── import_resolver.py
├── references/                   # Documentation
│   ├── cdk_construct_mappings.md
│   ├── property_mappings.md
│   └── cdk_patterns.md
└── assets/
    ├── construct-templates/      # TypeScript templates
    │   ├── lambda.ts.template
    │   ├── dynamodb.ts.template
    │   ├── iam-role.ts.template
    │   ├── s3-bucket.ts.template
    │   └── eventbridge-rule.ts.template
    └── package-template/
        ├── package.json.template
        ├── tsconfig.json.template
        └── README.md.template
```

## Troubleshooting

### Issue: "Input directory not found"
**Solution**: Verify the path to your resource inventory directory from aws-resource-discovery.

### Issue: "No resources found in input"
**Solution**: Check that the input directory contains JSON files (lambdas.json, dynamodb-tables.json, etc.).

### Issue: "Generated TypeScript doesn't compile"
**Solution**:
- Ensure you have TypeScript installed: `npm install -g typescript` or `pnpm add -g typescript`
- Check for TODO comments that need manual updates
- Verify CDK dependencies are installed: `npm install` or `pnpm install`

### Issue: "Missing dependencies in generated code"
**Solution**:
- Review `dependencies.json` to see required resources
- Generate dependencies first or use reference mode for them

## Roadmap

### v1.1 - Extended Resources (Planned)
- SQS queues
- SNS topics
- Lambda event source mappings

### v1.2 - API Services (Planned)
- API Gateway REST APIs
- API Gateway HTTP APIs
- AppSync GraphQL APIs

### v1.3 - Advanced Features (Future)
- Custom construct abstractions
- Environment-specific configuration
- Unit test scaffolding
- CDK Aspects generation

## Contributing

This skill is part of the AWS Infrastructure Skills suite. See [AWS_CDK_IMPORTER_ROADMAP.md](../AWS_CDK_IMPORTER_ROADMAP.md) for the complete project vision.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please refer to the main project documentation or create an issue in the repository.

---

**Version**: 1.0 MVP
**Status**: In Development
**Last Updated**: 2025-11-07
