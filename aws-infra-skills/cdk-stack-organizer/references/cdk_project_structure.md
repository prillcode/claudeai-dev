# CDK Project Structure Conventions

Standard conventions and best practices for CDK TypeScript project structure.

## Standard Project Structure

```
my-cdk-project/
├── bin/
│   └── app.ts                 # CDK app entry point
├── lib/
│   ├── stacks/                # Stack definitions
│   │   ├── data-stack.ts
│   │   ├── compute-stack.ts
│   │   └── api-stack.ts
│   └── constructs/            # Custom constructs
│       ├── custom-lambda.ts
│       └── custom-table.ts
├── test/                      # Unit and integration tests
│   ├── unit/
│   └── integration/
├── lambda/                    # Lambda function code
│   ├── function1/
│   │   └── index.ts
│   └── function2/
│       └── index.ts
├── cdk.json                   # CDK configuration
├── tsconfig.json              # TypeScript configuration
├── package.json               # Dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## Directory Breakdown

### `/bin` - Application Entry Point

Contains the CDK app entry point that instantiates stacks.

**bin/app.ts:**
```typescript
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DataStack } from '../lib/stacks/data-stack';
import { ComputeStack } from '../lib/stacks/compute-stack';

const app = new cdk.App();

const dataStack = new DataStack(app, 'DataStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

const computeStack = new ComputeStack(app, 'ComputeStack', {
  dataStack: dataStack,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

app.synth();
```

**Key points:**
- Shebang for direct execution: `#!/usr/bin/env node`
- Source map support for better error messages
- Environment configuration
- Stack instantiation and dependency setup
- Call `app.synth()` at the end

### `/lib` - Infrastructure Code

Contains all CDK infrastructure definitions.

#### `/lib/stacks` - Stack Definitions

One file per stack, following naming convention: `{purpose}-stack.ts`

**Example: lib/stacks/data-stack.ts:**
```typescript
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class DataStack extends cdk.Stack {
  public readonly usersTable: dynamodb.Table;
  public readonly assetsBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create resources
    this.usersTable = new dynamodb.Table(this, 'UsersTable', {
      partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    this.assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
    });
  }
}
```

**Stack naming conventions:**
- `DataStack` - Data layer (databases, storage)
- `ComputeStack` - Compute resources (Lambda, containers)
- `ApiStack` - API layer (API Gateway, EventBridge)
- `IamStack` - IAM roles and policies
- `NetworkStack` - VPC, subnets, security groups
- `MonitoringStack` - CloudWatch, alarms, dashboards

#### `/lib/constructs` - Custom Constructs

Reusable infrastructure patterns as L3 constructs.

**Example: lib/constructs/api-lambda.ts:**
```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export interface ApiLambdaProps {
  readonly functionName: string;
  readonly handler: string;
  readonly runtime: lambda.Runtime;
}

export class ApiLambda extends Construct {
  public readonly function: lambda.Function;
  public readonly api: apigateway.LambdaRestApi;

  constructor(scope: Construct, id: string, props: ApiLambdaProps) {
    super(scope, id);

    this.function = new lambda.Function(this, 'Function', {
      functionName: props.functionName,
      handler: props.handler,
      runtime: props.runtime,
      code: lambda.Code.fromAsset(`lambda/${props.functionName}`),
    });

    this.api = new apigateway.LambdaRestApi(this, 'Api', {
      handler: this.function,
      restApiName: `${props.functionName}-api`,
    });
  }
}
```

### `/test` - Tests

#### Unit Tests
Test individual constructs and stacks:

**test/unit/data-stack.test.ts:**
```typescript
import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { DataStack } from '../../lib/stacks/data-stack';

test('DataStack creates DynamoDB table', () => {
  const app = new cdk.App();
  const stack = new DataStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::DynamoDB::Table', {
    BillingMode: 'PAY_PER_REQUEST',
  });
});
```

#### Integration Tests
Test deployed resources:

**test/integration/api.test.ts:**
```typescript
import * as AWS from 'aws-sdk';

test('API returns 200', async () => {
  const apiUrl = process.env.API_URL!;
  const response = await fetch(apiUrl);
  expect(response.status).toBe(200);
});
```

### `/lambda` - Lambda Function Code

One directory per Lambda function:

```
lambda/
├── api-handler/
│   ├── index.ts
│   ├── package.json
│   └── tsconfig.json
└── background-processor/
    ├── index.py
    └── requirements.txt
```

**Benefits:**
- Clear separation between infrastructure and application code
- Each function can have its own dependencies
- Easy to locate function code

### Configuration Files

#### `cdk.json`
CDK toolkit configuration:

```json
{
  "app": "npx ts-node --prefer-ts-exts bin/app.ts",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": false,
    "@aws-cdk/core:stackRelativeExports": true
  }
}
```

#### `tsconfig.json`
TypeScript compiler configuration:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["es2022"],
    "strict": true,
    "esModuleInterop": true
  }
}
```

#### `package.json`
Dependencies and scripts:

```json
{
  "name": "my-cdk-project",
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
    "cdk": "cdk"
  },
  "dependencies": {
    "aws-cdk-lib": "^2.0.0",
    "constructs": "^10.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "ts-node": "^10.0.0",
    "typescript": "^5.0.0"
  }
}
```

## Alternative Structures

### Monorepo Structure
For multiple related CDK apps:

```
monorepo/
├── packages/
│   ├── infrastructure/        # CDK infrastructure
│   │   ├── bin/
│   │   └── lib/
│   ├── api-functions/         # Lambda functions
│   │   └── src/
│   └── shared-lib/            # Shared code
│       └── src/
├── package.json               # Root package.json
└── pnpm-workspace.yaml        # Workspace config
```

### Large Project Structure
For complex applications:

```
large-project/
├── bin/
│   ├── app.ts                 # Main app
│   └── dev-app.ts             # Dev environment app
├── lib/
│   ├── core/                  # Core infrastructure
│   │   ├── network-stack.ts
│   │   └── security-stack.ts
│   ├── services/              # Service-specific stacks
│   │   ├── api/
│   │   │   ├── api-stack.ts
│   │   │   └── api-constructs/
│   │   ├── data/
│   │   └── compute/
│   └── shared/                # Shared constructs
│       ├── base-stack.ts
│       └── constructs/
├── config/                    # Configuration files
│   ├── dev.ts
│   ├── staging.ts
│   └── prod.ts
└── scripts/                   # Deployment scripts
    ├── deploy-dev.sh
    └── deploy-prod.sh
```

## Naming Conventions

### Files
- **Kebab case**: `data-stack.ts`, `api-lambda.ts`
- **Stack files**: `{purpose}-stack.ts`
- **Construct files**: `{name}.ts`

### Classes
- **PascalCase**: `DataStack`, `ApiLambda`
- **Stack classes**: end with `Stack`
- **Construct classes**: descriptive names

### Resources
- **PascalCase for IDs**: `UsersTable`, `AssetsBucket`
- **Descriptive names**: Indicate purpose clearly

### Variables
- **camelCase**: `usersTable`, `apiHandler`
- **Const for resources**: `const usersTable = new Table(...)`

## Best Practices

### ✅ DO
- Keep stacks focused and single-purpose
- Use meaningful names
- Export public resources from stacks
- Group related constructs
- Use consistent naming conventions
- Document complex logic
- Write tests for infrastructure

### ❌ DON'T
- Mix infrastructure and application code
- Create deeply nested directories
- Use inconsistent naming
- Hardcode values (use parameters/context)
- Skip documentation
- Ignore TypeScript errors

## Environment Management

### Using CDK Context
```typescript
// Read from cdk.json context
const vpc = app.node.tryGetContext('vpcId');

// Or pass as parameters
const app = new cdk.App({
  context: {
    environment: 'dev',
  },
});
```

### Environment-Specific Configuration
```typescript
// config/environments.ts
export interface EnvironmentConfig {
  account: string;
  region: string;
  vpcId: string;
}

export const environments: Record<string, EnvironmentConfig> = {
  dev: {
    account: '111111111111',
    region: 'us-east-1',
    vpcId: 'vpc-dev',
  },
  prod: {
    account: '222222222222',
    region: 'us-east-1',
    vpcId: 'vpc-prod',
  },
};

// Use in app.ts
const envName = app.node.tryGetContext('environment') || 'dev';
const envConfig = environments[envName];
```

## Scripts

### Common npm Scripts
```json
{
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint . --ext .ts",
    "lint:fix": "eslint . --ext .ts --fix",
    "cdk": "cdk",
    "cdk:synth": "cdk synth",
    "cdk:diff": "cdk diff",
    "cdk:deploy": "cdk deploy --all",
    "cdk:destroy": "cdk destroy --all"
  }
}
```

## Resources

- [CDK Project Structure](https://docs.aws.amazon.com/cdk/v2/guide/work-with.html)
- [CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
- [CDK Examples](https://github.com/aws-samples/aws-cdk-examples)

---

**Version**: 1.0
**Last Updated**: 2025-11-07
