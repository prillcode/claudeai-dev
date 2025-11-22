# Stack Organization Patterns

Best practices and patterns for organizing CDK stacks.

## Why Organize Stacks?

Proper stack organization provides:
- **Better deployment control**: Deploy only what changed
- **Reduced blast radius**: Changes affect fewer resources
- **Improved team collaboration**: Different teams can own different stacks
- **Easier rollbacks**: Roll back individual stacks without affecting others
- **Better cost tracking**: Stack-level cost allocation

## Organization Strategies

### 1. By Layer (Recommended for Most Projects)

Organizes resources by architectural layer following clean architecture principles.

**Structure:**
```
├── IamStack         # IAM roles and policies
├── DataStack        # DynamoDB tables, S3 buckets
├── ComputeStack     # Lambda functions
└── ApiStack         # API Gateway, EventBridge rules
```

**Benefits:**
- Clear separation of concerns
- Easy to understand and maintain
- Natural dependency flow (IAM → Data → Compute → API)
- Good for serverless applications

**When to use:**
- New CDK projects
- Serverless applications
- Projects with clear architectural layers
- Teams organized by technical expertise

**Dependencies:**
```
ApiStack → ComputeStack → DataStack → IamStack
```

### 2. By Service/Application

Groups all resources belonging to the same service together.

**Structure:**
```
├── OrderServiceStack      # All order service resources
├── UserServiceStack       # All user service resources
├── PaymentServiceStack    # All payment service resources
└── SharedStack            # Shared resources (databases, queues)
```

**Benefits:**
- Service autonomy
- Easier microservices management
- Each service can be deployed independently
- Clear service boundaries

**When to use:**
- Microservices architectures
- Multiple applications in one AWS account
- Teams organized by service/domain
- Services with different deployment schedules

**Dependencies:**
```
OrderServiceStack → SharedStack
UserServiceStack → SharedStack
PaymentServiceStack → SharedStack
```

### 3. By Environment

Separates resources by environment (dev/staging/prod).

**Structure:**
```
├── DevStack
├── StagingStack
└── ProdStack
```

**Benefits:**
- Environment isolation
- Consistent structure across environments
- Easy to replicate environments

**When to use:**
- Single application deployed to multiple environments
- Environment-specific configurations
- Testing infrastructure changes in lower environments

**Note:** This is less common in CDK as environments are usually handled through CDK context or separate app instances.

### 4. By Tags

Groups resources based on AWS resource tags.

**Structure:**
```
├── Project-MyAppStack       # All resources tagged project:myapp
├── Project-BackendStack     # All resources tagged project:backend
└── SharedStack              # Untagged or shared resources
```

**Benefits:**
- Flexible organization based on existing tagging
- Matches organizational tagging strategies
- Easy cost allocation by tag

**When to use:**
- Organizations with strict tagging policies
- Multiple projects in one account
- Cost allocation by project/department
- Existing resources with good tagging

## Stack Size Guidelines

### Optimal Stack Size
- **Small stacks**: 10-30 resources
  - Faster deployments
  - Easier rollbacks
  - Better isolation

- **Medium stacks**: 30-100 resources
  - Balanced approach
  - Good for related resources

- **Large stacks**: 100-200 resources
  - Can be slower to deploy
  - Higher risk on updates
  - Consider splitting

### CloudFormation Limits
- **Max resources per stack**: 500 (hard limit)
- **Recommended max**: 200 resources per stack

## Cross-Stack References

### Exporting Values
```typescript
// In DataStack
export class DataStack extends cdk.Stack {
  public readonly usersTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.usersTable = new dynamodb.Table(this, 'UsersTable', {
      // ...
    });

    // Export for other stacks
    new cdk.CfnOutput(this, 'UsersTableName', {
      value: this.usersTable.tableName,
      exportName: 'UsersTableName',
    });
  }
}
```

### Importing Values
```typescript
// In ComputeStack
export interface ComputeStackProps extends cdk.StackProps {
  readonly dataStack: DataStack;
}

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    // Direct reference (preferred)
    const table = props.dataStack.usersTable;

    // Or use Fn.importValue
    const tableName = cdk.Fn.importValue('UsersTableName');
  }
}
```

## Dependency Management

### Explicit Dependencies
```typescript
// In app.ts
const iamStack = new IamStack(app, 'IamStack');
const dataStack = new DataStack(app, 'DataStack');
const computeStack = new ComputeStack(app, 'ComputeStack', {
  dataStack: dataStack,
});

// Explicit dependency
computeStack.addDependency(dataStack);
dataStack.addDependency(iamStack);
```

### Implicit Dependencies
CDK automatically creates dependencies when you pass stack references:
```typescript
const computeStack = new ComputeStack(app, 'ComputeStack', {
  dataStack: dataStack, // Creates implicit dependency
});
```

## Common Patterns

### Nested Stacks
For very large applications, use nested stacks:
```typescript
export class ParentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new DataNestedStack(this, 'DataNested');
    new ComputeNestedStack(this, 'ComputeNested');
  }
}
```

### Stack Sets
For multi-account/multi-region:
```typescript
// Deploy same stack to multiple accounts/regions
new StackSet(this, 'MyStackSet', {
  template: // ...
  targets: [
    { account: '111111111111', region: 'us-east-1' },
    { account: '222222222222', region: 'eu-west-1' },
  ],
});
```

### Stage-Based Organization
```typescript
export class ApplicationStage extends cdk.Stage {
  constructor(scope: Construct, id: string, props?: cdk.StageProps) {
    super(scope, id, props);

    const dataStack = new DataStack(this, 'Data');
    const computeStack = new ComputeStack(this, 'Compute', { dataStack });
  }
}

// Deploy stage to different environments
const devStage = new ApplicationStage(app, 'Dev', {
  env: { account: '111111111111', region: 'us-east-1' },
});

const prodStage = new ApplicationStage(app, 'Prod', {
  env: { account: '222222222222', region: 'us-east-1' },
});
```

## Anti-Patterns to Avoid

### ❌ Monolithic Stacks
```typescript
// BAD: Everything in one stack
export class MonolithStack extends cdk.Stack {
  // 200+ resources
  // IAM + Data + Compute + API all together
}
```
**Problem**: Slow deployments, high risk, hard to maintain

### ❌ Too Many Small Stacks
```typescript
// BAD: One stack per resource
export class Function1Stack extends cdk.Stack { }
export class Function2Stack extends cdk.Stack { }
// ... 50 more stacks
```
**Problem**: Deployment complexity, dependency hell

### ❌ Circular Dependencies
```typescript
// BAD: Circular references
export class StackA extends cdk.Stack {
  constructor(scope: Construct, id: string, props: { stackB: StackB }) {
    // Uses stackB
  }
}

export class StackB extends cdk.Stack {
  constructor(scope: Construct, id: string, props: { stackA: StackA }) {
    // Uses stackA - CIRCULAR!
  }
}
```
**Problem**: Cannot deploy, CloudFormation will fail

## Decision Tree

```
Start
  ↓
Is this a microservices architecture?
  ├─ Yes → Use By Service strategy
  └─ No → Continue
           ↓
         Do you have good tagging?
           ├─ Yes → Consider By Tags strategy
           └─ No → Use By Layer strategy (default)
```

## Resources

- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
- [CloudFormation Stack Limits](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html)
- [CDK Patterns](https://cdkpatterns.com/)

---

**Version**: 1.0
**Last Updated**: 2025-11-07
