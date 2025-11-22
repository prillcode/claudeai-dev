# CDK Cross-Stack Dependency Management

Guide to managing dependencies between CDK stacks.

## Why Dependencies Matter

CDK stacks often need to reference resources from other stacks. Proper dependency management ensures:
- Correct deployment order
- Safe updates and rollbacks
- Resource sharing across stacks
- Avoiding circular dependencies

## Types of Dependencies

### 1. Explicit Dependencies
Manually defined dependencies using `addDependency()`:

```typescript
const stackA = new StackA(app, 'StackA');
const stackB = new StackB(app, 'StackB');

// StackB must be deployed after StackA
stackB.addDependency(stackA);
```

### 2. Implicit Dependencies
Automatically created when passing stack references:

```typescript
const dataStack = new DataStack(app, 'DataStack');

// Passing dataStack creates implicit dependency
const computeStack = new ComputeStack(app, 'ComputeStack', {
  usersTable: dataStack.usersTable,
});
```

### 3. CloudFormation Exports/Imports
Using CloudFormation exports for loose coupling:

```typescript
// Exporting stack
export class DataStack extends cdk.Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const table = new dynamodb.Table(this, 'Table', { /* ... */ });

    new cdk.CfnOutput(this, 'TableNameExport', {
      value: table.tableName,
      exportName: 'MyTableName',
    });
  }
}

// Importing stack
export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const tableName = cdk.Fn.importValue('MyTableName');

    new lambda.Function(this, 'Function', {
      // ...
      environment: {
        TABLE_NAME: tableName,
      },
    });
  }
}
```

## Best Practices

### ✅ DO: Pass Direct References
```typescript
// GOOD: Type-safe, explicit dependency
export interface ComputeStackProps extends cdk.StackProps {
  readonly dataStack: DataStack;
}

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    // Direct access to table
    const table = props.dataStack.usersTable;
  }
}
```

**Benefits:**
- Type safety
- Clear dependencies
- IDE autocomplete
- Refactoring support

### ✅ DO: Use Public Properties
```typescript
export class DataStack extends cdk.Stack {
  // Expose resources as public readonly properties
  public readonly usersTable: dynamodb.Table;
  public readonly ordersBucket: s3.Bucket;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.usersTable = new dynamodb.Table(this, 'Users', { /* ... */ });
    this.ordersBucket = new s3.Bucket(this, 'Orders', { /* ... */ });
  }
}
```

### ✅ DO: Layer Your Dependencies
```typescript
// Clear layered architecture
const iamStack = new IamStack(app, 'Iam');
const dataStack = new DataStack(app, 'Data', { iamStack });
const computeStack = new ComputeStack(app, 'Compute', { dataStack, iamStack });
const apiStack = new ApiStack(app, 'Api', { computeStack });
```

**Dependency flow:**
```
ApiStack → ComputeStack → DataStack → IamStack
```

### ❌ DON'T: Create Circular Dependencies
```typescript
// BAD: Circular dependency
export class StackA extends cdk.Stack {
  public readonly resourceA: SomeResource;

  constructor(scope: Construct, id: string, props: { stackB: StackB }) {
    super(scope, id);
    this.resourceA = new SomeResource(this, 'A', {
      dependency: props.stackB.resourceB, // Uses B
    });
  }
}

export class StackB extends cdk.Stack {
  public readonly resourceB: SomeResource;

  constructor(scope: Construct, id: string, props: { stackA: StackA }) {
    super(scope, id);
    this.resourceB = new SomeResource(this, 'B', {
      dependency: props.stackA.resourceA, // Uses A - CIRCULAR!
    });
  }
}
```

**Solution:** Refactor to remove circularity
```typescript
// GOOD: Break circular dependency
const sharedStack = new SharedStack(app, 'Shared');
const stackA = new StackA(app, 'A', { sharedStack });
const stackB = new StackB(app, 'B', { sharedStack });
```

### ❌ DON'T: Overuse CloudFormation Exports
```typescript
// AVOID: String-based exports are brittle
const tableName = cdk.Fn.importValue('MyTable'); // What if name changes?
```

**Problems:**
- No type safety
- Hard to refactor
- Can't delete exports while in use
- String-based (typo-prone)

**When to use exports:**
- Cross-account/region references
- Loose coupling requirements
- External consumers

## Dependency Patterns

### Pattern 1: Foundation Stack
Base infrastructure that other stacks depend on:

```typescript
export class FoundationStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly executionRole: iam.Role;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.vpc = new ec2.Vpc(this, 'Vpc');
    this.executionRole = new iam.Role(this, 'ExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });
  }
}

// All other stacks depend on foundation
const foundation = new FoundationStack(app, 'Foundation');
const dataStack = new DataStack(app, 'Data', { foundation });
const computeStack = new ComputeStack(app, 'Compute', { foundation });
```

### Pattern 2: Layered Architecture
```typescript
// Layer 1: IAM
const iamStack = new IamStack(app, 'Iam');

// Layer 2: Data (depends on IAM)
const dataStack = new DataStack(app, 'Data', {
  roles: {
    dynamodbRole: iamStack.dynamodbRole,
  },
});

// Layer 3: Compute (depends on Data and IAM)
const computeStack = new ComputeStack(app, 'Compute', {
  roles: {
    lambdaRole: iamStack.lambdaRole,
  },
  data: {
    usersTable: dataStack.usersTable,
    assetsBucket: dataStack.assetsBucket,
  },
});

// Layer 4: API (depends on Compute)
const apiStack = new ApiStack(app, 'Api', {
  functions: {
    apiHandler: computeStack.apiHandler,
  },
});
```

### Pattern 3: Service Stacks with Shared Infrastructure
```typescript
// Shared infrastructure
const sharedStack = new SharedStack(app, 'Shared');

// Independent service stacks
const orderService = new OrderServiceStack(app, 'OrderService', {
  sharedInfra: sharedStack,
});

const userService = new UserServiceStack(app, 'UserService', {
  sharedInfra: sharedStack,
});

const paymentService = new PaymentServiceStack(app, 'PaymentService', {
  sharedInfra: sharedStack,
});
```

## Detecting Dependencies

### Automatic Detection
CDK automatically detects dependencies in these cases:

1. **Direct resource references:**
   ```typescript
   const table = dataStack.usersTable; // Automatic dependency
   ```

2. **ARN/Name references:**
   ```typescript
   const table = dynamodb.Table.fromTableArn(
     this,
     'Table',
     dataStack.usersTable.tableArn // Automatic dependency
   );
   ```

3. **CloudFormation references:**
   ```typescript
   const tableName = cdk.Fn.importValue('TableName'); // Automatic dependency
   ```

### Manual Dependency Analysis
For complex scenarios, analyze dependencies manually:

```typescript
export class DependencyAnalyzer {
  static analyzeDependencies(stacks: cdk.Stack[]): Map<cdk.Stack, Set<cdk.Stack>> {
    const deps = new Map<cdk.Stack, Set<cdk.Stack>>();

    for (const stack of stacks) {
      deps.set(stack, new Set(stack.dependencies));
    }

    return deps;
  }

  static topologicalSort(stacks: cdk.Stack[]): cdk.Stack[] {
    // Implement topological sort for deployment order
    // ...
  }
}
```

## Deployment Order

### Viewing Deployment Order
```bash
# Preview deployment order
cdk deploy --all --dry-run

# Deploy in order
cdk deploy Stack1 Stack2 Stack3 --require-approval never
```

### Parallel Deployments
Independent stacks can be deployed in parallel:
```bash
# Deploy independent stacks in parallel
cdk deploy StackA StackB --concurrency 2
```

## Troubleshooting

### Issue: Circular Dependency
**Error:**
```
Circular dependency between stacks: StackA → StackB → StackA
```

**Solution:**
1. Identify the cycle
2. Move shared resources to a common stack
3. Refactor to remove back-references

### Issue: Export in Use
**Error:**
```
Export MyTableName cannot be deleted as it is in use by StackB
```

**Solution:**
1. Remove import from dependent stack first
2. Deploy dependent stack
3. Remove export from source stack
4. Deploy source stack

### Issue: Wrong Deployment Order
**Error:**
```
Stack StackB cannot be deployed before StackA
```

**Solution:**
```typescript
// Add explicit dependency
stackB.addDependency(stackA);
```

## Testing Dependencies

### Unit Tests
```typescript
test('Stack has correct dependencies', () => {
  const app = new cdk.App();
  const dataStack = new DataStack(app, 'Data');
  const computeStack = new ComputeStack(app, 'Compute', { dataStack });

  // Check dependencies
  expect(computeStack.dependencies).toContain(dataStack);
});
```

### Integration Tests
```typescript
test('Stacks deploy in correct order', async () => {
  const result = await deployStacks(['Data', 'Compute', 'Api']);
  expect(result.order).toEqual(['Data', 'Compute', 'Api']);
});
```

## Resources

- [CDK Stack Dependencies](https://docs.aws.amazon.com/cdk/v2/guide/stacks.html#stack_dependencies)
- [CloudFormation Exports](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-exports.html)
- [CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)

---

**Version**: 1.0
**Last Updated**: 2025-11-07
