# AWS to CDK Importer - Complete Project Roadmap

## Project Vision

Create a suite of composable Claude Code skills that discover existing AWS resources and generate CDK TypeScript code to import them into source control. Skills work both independently and as part of an orchestrated workflow.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   aws-to-cdk-importer                           │
│              (Orchestrator - Future Phase)                      │
│    Coordinates end-to-end workflow across all component skills  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Discovery  │──────▶  Code Gen    │─────▶ Organization  │
│              │      │              │     │              │
│  Resource    │      │  CDK Code    │     │  Stack       │
│  Inventory   │      │  Generator   │     │  Organizer   │
└──────────────┘      └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
                                           ┌──────────────┐
                                           │   Import     │
                                           │   Config     │
                                           │   Generator  │
                                           └──────────────┘
```

## Data Flow & Contracts

### Output from Discovery → Input to Code Generator
```json
{
  "metadata": {
    "account_id": "123456789012",
    "region": "us-east-1",
    "scan_timestamp": "2025-01-07T10:30:00Z",
    "profile": "prod",
    "filters_applied": {
      "tags": {"environment": "prod"},
      "name_pattern": "myapp-*",
      "resource_types": ["lambda", "dynamodb"]
    }
  },
  "resources": {
    "lambdas": [...],
    "dynamodb_tables": [...],
    "iam_roles": [...],
    "iam_policies": [...],
    "s3_buckets": [...],
    "eventbridge_rules": [...]
  },
  "dependencies": [
    {
      "source": "arn:aws:lambda:...",
      "target": "arn:aws:dynamodb:...",
      "relationship": "lambda_uses_table"
    }
  ]
}
```

### Output from Code Generator → Input to Stack Organizer
```
cdk-generated/
├── metadata.json                 # Generation metadata
├── constructs/
│   ├── lambdas/
│   │   ├── order-processor.ts
│   │   └── user-service.ts
│   ├── dynamodb/
│   │   └── users-table.ts
│   └── iam/
│       └── lambda-execution-role.ts
└── dependencies.json             # Cross-resource dependencies
```

### Output from Stack Organizer → Input to Import Config Generator
```
cdk-organized/
├── lib/
│   ├── core-stack.ts
│   ├── data-stack.ts
│   └── compute-stack.ts
├── bin/
│   └── app.ts
└── organization-metadata.json
```

---

## Skill 1: aws-resource-discovery

### Purpose
Scan AWS accounts to discover existing resources and generate a comprehensive inventory with properties and dependencies.

### v1.0 - MVP (Current Focus)

**Target Resources:**
- Lambda functions (runtime, handler, environment vars, layers, VPC config, IAM role)
- DynamoDB tables (billing mode, GSIs, LSIs, streams, encryption, TTL, PITR)
- IAM roles (trust policy, attached policies, inline policies)
- IAM policies (managed and inline policy documents)
- S3 buckets (versioning, encryption, lifecycle rules, CORS, policies)
- EventBridge rules (event pattern, targets, schedule)

**Discovery Modes:**
- **Filtered Discovery**:
  - By tag (key:value pairs)
  - By name pattern (prefix, contains, suffix)
  - By resource type (lambda, dynamodb, iam, s3, eventbridge)
- **Specific Resource Lookup**:
  - Fetch details for specific ARN/name
  - Traverse dependencies from a starting resource

**Authentication:**
- AWS CLI profiles only (`--profile` flag)
- Single region per scan (user-specified)
- SSO support with login prompt/warning

**Dependency Detection:**
- Lambda → IAM role (from function configuration)
- Lambda → DynamoDB table (from IAM policy, environment variables)
- Lambda → S3 bucket (from IAM policy, environment variables)
- Lambda → EventBridge rule (rule targets)
- EventBridge rule → Lambda (targets)
- IAM role → IAM policy (attached policies)

**Output Format:**
```
resource-inventory/
├── metadata.json
├── lambdas.json
├── dynamodb-tables.json
├── iam-roles.json
├── iam-policies.json
├── s3-buckets.json
├── eventbridge-rules.json
└── dependencies.json
```

**Usage Examples:**
```bash
# Filtered discovery
"Use aws-resource-discovery to scan us-east-1 using profile 'prod' for all resources
tagged with 'project:myapp'"

# Resource type filtering
"Use aws-resource-discovery to find all Lambda functions and DynamoDB tables in
us-east-1 using profile 'dev'"

# Name pattern search
"Use aws-resource-discovery to find all resources with 'order-service' in the name
using profile 'prod' in us-east-1"

# Specific resource lookup
"Use aws-resource-discovery to get details for Lambda function 'order-processor'
and all its dependencies using profile 'prod'"
```

**Success Criteria:**
- ✅ Discovers all 6 resource types with complete properties
- ✅ Supports tag filtering, name pattern matching, resource type filtering
- ✅ Detects basic dependencies (Lambda→DynamoDB, Lambda→S3, etc.)
- ✅ Handles pagination for large resource lists
- ✅ Handles missing permissions gracefully with clear error messages
- ✅ Outputs separate JSON files per resource type
- ✅ SSO profile warning/guidance included

**Implementation:**
```
aws-resource-discovery/
├── SKILL.md
├── scripts/
│   ├── discover.py                    # Main discovery script (boto3)
│   ├── resource_scanners/
│   │   ├── lambda_scanner.py
│   │   ├── dynamodb_scanner.py
│   │   ├── iam_scanner.py
│   │   ├── s3_scanner.py
│   │   └── eventbridge_scanner.py
│   ├── dependency_detector.py         # Cross-resource dependency detection
│   └── utils/
│       ├── aws_client.py              # Boto3 client management
│       ├── filters.py                 # Tag/name filtering logic
│       └── output_formatter.py        # JSON output generation
├── references/
│   ├── aws_api_reference.md           # Boto3 API call documentation
│   ├── supported_resources.md         # Detailed resource type documentation
│   └── dependency_patterns.md         # How dependencies are detected
└── assets/
    └── output-template/               # Example output structure
```

---

### v1.1 - Extended Serverless Resources

**New Resources:**
- SQS queues (FIFO, dead letter queues, encryption, policies)
- SNS topics (subscriptions, encryption, policies)
- Lambda event source mappings (SQS, DynamoDB streams, Kinesis)

**Enhanced Dependency Detection:**
- Lambda → SQS queue (event source mappings, IAM policy)
- Lambda → SNS topic (IAM policy, environment variables)
- SQS → Lambda (event source mapping)
- DynamoDB streams → Lambda (event source mapping)
- SNS → SQS (subscriptions)
- SNS → Lambda (subscriptions)

**New Output Files:**
```
resource-inventory/
├── ... (existing files)
├── sqs-queues.json
├── sns-topics.json
└── lambda-event-source-mappings.json
```

---

### v1.2 - API Services

**New Resources:**
- API Gateway REST APIs (resources, methods, integrations, stages, authorizers)
- API Gateway HTTP APIs (routes, integrations, stages, authorizers)
- AppSync GraphQL APIs (schemas, resolvers, data sources)

**Enhanced Dependency Detection:**
- API Gateway → Lambda (integrations)
- API Gateway → DynamoDB (direct integrations)
- AppSync → Lambda (resolvers)
- AppSync → DynamoDB (data sources)

**New Output Files:**
```
resource-inventory/
├── ... (existing files)
├── apigateway-rest-apis.json
├── apigateway-http-apis.json
└── appsync-apis.json
```

---

### v1.3 - Future Enhancements (Post-MVP)

**Additional Resources:**
- CloudWatch Log Groups (retention, subscriptions)
- Step Functions state machines
- Secrets Manager secrets
- Systems Manager parameters
- Cognito user pools
- CloudFront distributions
- ECR repositories
- ECS/Fargate services

**Advanced Features:**
- Multi-region scanning (parallel scans across regions)
- Multi-account scanning (assume role in multiple accounts)
- Incremental updates (compare with previous scan, detect drifts)
- Resource tagging suggestions (detect untagged resources)
- Cost estimation (integrate with AWS Cost Explorer)
- Dependency graph visualization (generate DOT/Mermaid diagrams)
- Export to other formats (CSV, Excel, Terraform import blocks)

---

## Skill 2: cdk-code-generator

### Purpose
Generate TypeScript CDK code from discovered AWS resources. Supports both reference-only imports (`.fromAttributes()`) and full management imports (complete construct definitions).

### v1.0 - MVP

**Input:**
- Resource inventory JSON files from `aws-resource-discovery`
- User preferences (reference-only vs full management mode)

**Supported Resource Types:**
- Lambda functions
- DynamoDB tables
- IAM roles
- IAM policies
- S3 buckets
- EventBridge rules

**Generation Modes:**

**1. Reference-Only Mode:**
```typescript
// Only generate .fromAttributes() calls for resources you need to reference
const existingTable = dynamodb.Table.fromTableName(
  this, 'ExistingUsersTable', 'users-table'
);

const existingFunction = lambda.Function.fromFunctionArn(
  this, 'ExistingOrderProcessor',
  'arn:aws:lambda:us-east-1:123:function:order-processor'
);
```

**2. Full Management Mode:**
```typescript
// Generate complete construct definitions for CDK to manage
const table = new dynamodb.Table(this, 'UsersTable', {
  tableName: 'users-table',
  partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
  encryption: dynamodb.TableEncryption.AWS_MANAGED,
  pointInTimeRecovery: true,
});
```

**Features:**
- Proper TypeScript typing with CDK v2 constructs
- Include all discovered properties (environment vars, configurations, policies)
- Generate required CDK package imports
- Preserve resource naming for easier identification
- Include comments with original ARNs and metadata
- Handle optional vs required properties correctly
- Generate placeholder values for secrets/sensitive data

**Output Structure:**
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
└── README.md                          # Instructions for using generated code
```

**Usage Examples:**
```bash
# Reference-only mode
"Use cdk-code-generator to create reference imports for the resources in
resource-inventory/ so I can use them in my CDK stack"

# Full management mode
"Use cdk-code-generator to generate full CDK constructs for all Lambda functions
and DynamoDB tables in resource-inventory/"

# Mixed mode
"Use cdk-code-generator to create full management constructs for Lambda functions
but reference-only imports for DynamoDB tables"
```

**Success Criteria:**
- ✅ Generates valid, compilable TypeScript CDK code
- ✅ Properly maps all resource properties to CDK construct props
- ✅ Handles both reference-only and full management modes
- ✅ Includes proper imports and TypeScript types
- ✅ Preserves resource relationships and dependencies
- ✅ Generates clean, idiomatic CDK code
- ✅ Includes helpful comments and documentation

**Implementation:**
```
cdk-code-generator/
├── SKILL.md
├── scripts/
│   ├── generate.py                    # Main generation script
│   ├── generators/
│   │   ├── lambda_generator.py
│   │   ├── dynamodb_generator.py
│   │   ├── iam_generator.py
│   │   ├── s3_generator.py
│   │   └── eventbridge_generator.py
│   ├── templates/
│   │   ├── construct_template.py      # Base construct template
│   │   └── reference_template.py      # Reference-only template
│   └── utils/
│       ├── typescript_formatter.py    # Code formatting/indentation
│       └── import_resolver.py         # CDK package import management
├── references/
│   ├── cdk_construct_mappings.md      # AWS resource → CDK construct reference
│   ├── property_mappings.md           # AWS API properties → CDK props
│   └── cdk_patterns.md                # Common CDK patterns and idioms
└── assets/
    ├── construct-templates/           # TypeScript templates
    │   ├── lambda.ts.template
    │   ├── dynamodb.ts.template
    │   ├── iam-role.ts.template
    │   ├── s3-bucket.ts.template
    │   └── eventbridge-rule.ts.template
    └── package.json.template          # CDK dependencies template
```

---

### v1.1 - Extended Resources

**New Resources:**
- SQS queues
- SNS topics
- Lambda event source mappings

**Enhanced Features:**
- Generate event source mapping configurations
- Handle queue/topic subscriptions
- Preserve message filtering policies

---

### v1.2 - API Services

**New Resources:**
- API Gateway REST APIs
- API Gateway HTTP APIs
- AppSync GraphQL APIs

**Enhanced Features:**
- Generate API Gateway resource hierarchies
- Create route/method configurations
- Generate AppSync schema definitions and resolvers
- Handle API Gateway authorizers

---

### v1.3 - Future Enhancements

**Advanced Code Generation:**
- Custom construct abstractions (higher-level patterns)
- Environment-specific configuration (dev/staging/prod)
- Secret placeholder generation (with instructions for manual updates)
- Code splitting strategies for large stacks
- TypeScript interfaces for construct props
- Unit test scaffolding for generated constructs
- CDK Aspects for cross-cutting concerns
- Custom resource handlers for unsupported features

---

## Skill 3: cdk-stack-organizer

### Purpose
Intelligently organize generated CDK constructs into logical stacks with proper dependency management and best practices.

### v1.0 - MVP

**Input:**
- Generated CDK constructs from `cdk-code-generator`
- Dependencies graph
- User preferences for organization strategy

**Organization Strategies:**

**1. By Service/Application:**
```
lib/
├── order-service-stack.ts        # All order-service resources
├── user-service-stack.ts         # All user-service resources
└── shared-infrastructure-stack.ts # Shared resources (databases, queues)
```

**2. By Layer (Clean Architecture):**
```
lib/
├── data-layer-stack.ts           # DynamoDB, S3
├── compute-layer-stack.ts        # Lambda functions
├── api-layer-stack.ts            # API Gateway
└── event-layer-stack.ts          # EventBridge, SNS, SQS
```

**3. By Environment:**
```
lib/
├── dev-stack.ts
├── staging-stack.ts
└── prod-stack.ts
```

**4. By Tag-Based Grouping:**
```
lib/
├── project-myapp-stack.ts        # All resources tagged project:myapp
├── project-backend-stack.ts      # All resources tagged project:backend
└── shared-stack.ts               # Untagged or shared resources
```

**Features:**
- Detect cross-stack dependencies automatically
- Generate stack exports for shared resources
- Create proper stack references (`.fromAttributes()` across stacks)
- Ensure deployment order based on dependencies
- Generate `bin/app.ts` with proper stack initialization
- Include environment configuration
- Generate `cdk.json` with proper context

**Output Structure:**
```
cdk-organized/
├── bin/
│   └── app.ts                         # CDK app entry point
├── lib/
│   ├── data-stack.ts
│   ├── compute-stack.ts
│   ├── api-stack.ts
│   └── shared/
│       └── constructs/                # Reusable constructs
├── cdk.json                           # CDK configuration
├── tsconfig.json                      # TypeScript configuration
├── package.json                       # Dependencies
├── README.md                          # Setup and deployment instructions
└── organization-metadata.json         # Stack organization details
```

**Usage Examples:**
```bash
# Organize by layer
"Use cdk-stack-organizer to organize the generated CDK code from cdk-generated/
into stacks by architectural layer (data, compute, API)"

# Organize by service
"Use cdk-stack-organizer to group resources by service name (extracted from tags)"

# Custom organization
"Use cdk-stack-organizer to create separate stacks for Lambda functions,
DynamoDB tables, and everything else in a shared stack"
```

**Success Criteria:**
- ✅ Creates logical stack boundaries based on chosen strategy
- ✅ Detects and properly handles cross-stack dependencies
- ✅ Generates valid CDK app structure (bin/app.ts, lib/stacks)
- ✅ Ensures correct deployment order
- ✅ Includes proper TypeScript configuration
- ✅ Generates comprehensive README with instructions

**Implementation:**
```
cdk-stack-organizer/
├── SKILL.md
├── scripts/
│   ├── organize.py                    # Main organization script
│   ├── strategies/
│   │   ├── by_service.py
│   │   ├── by_layer.py
│   │   ├── by_environment.py
│   │   └── by_tags.py
│   ├── dependency_analyzer.py         # Analyze cross-stack dependencies
│   └── utils/
│       ├── stack_generator.py         # Generate stack files
│       └── app_generator.py           # Generate bin/app.ts
├── references/
│   ├── stack_organization_patterns.md # Best practices for stack organization
│   ├── dependency_management.md       # Cross-stack dependency patterns
│   └── cdk_project_structure.md       # CDK project conventions
└── assets/
    ├── cdk-project-template/          # Full CDK project template
    │   ├── bin/app.ts.template
    │   ├── lib/stack.ts.template
    │   ├── cdk.json
    │   ├── tsconfig.json
    │   ├── package.json
    │   └── README.md
    └── github-workflows/              # CI/CD templates (optional)
        └── deploy.yml
```

---

### v1.1 - Enhanced Organization

**New Features:**
- Multi-environment stack organization (dev/staging/prod)
- Stack nesting and composition
- Shared construct library generation
- Custom construct patterns for repeated resource combinations

---

### v1.2 - Advanced Features

**New Features:**
- CDK Pipelines integration
- Automated testing structure (unit and integration tests)
- Cost allocation tags
- Stack-level permissions boundaries
- Custom CloudFormation conditions

---

### v1.3 - Future Enhancements

**Enterprise Features:**
- Multi-region stack organization
- Multi-account organization (AWS Organizations integration)
- Service catalog integration
- Stack set generation
- Compliance checking (tag requirements, naming conventions)
- Stack dependency visualization

---

## Skill 4: cdk-import-config-generator

### Purpose
Generate CDK import configurations and scripts to execute `cdk import` for bringing existing AWS resources under CDK management.

### v1.0 - MVP

**Input:**
- Organized CDK project from `cdk-stack-organizer`
- Resource inventory from `aws-resource-discovery`

**Features:**
- Generate resource identifier mappings for `cdk import`
- Create import scripts for each stack
- Generate preview/dry-run scripts
- Include rollback instructions
- Create backup/state management scripts

**Output Structure:**
```
cdk-import-configs/
├── import-mappings/
│   ├── data-stack-mappings.json       # Resource identifiers for data stack
│   ├── compute-stack-mappings.json    # Resource identifiers for compute stack
│   └── api-stack-mappings.json        # Resource identifiers for API stack
├── scripts/
│   ├── preview-all.sh                 # Preview all imports (dry-run)
│   ├── import-all.sh                  # Execute all imports
│   ├── import-data-stack.sh           # Import specific stack
│   ├── import-compute-stack.sh
│   ├── import-api-stack.sh
│   └── rollback.sh                    # Rollback instructions
├── README.md                          # Detailed import instructions
└── IMPORT_CHECKLIST.md                # Step-by-step checklist
```

**Resource Identifier Mapping Format:**
```json
{
  "DataStack": {
    "UsersTable": "users-table",
    "OrdersTable": "orders-table"
  },
  "ComputeStack": {
    "OrderProcessorFunction": "order-processor",
    "UserServiceFunction": "user-service"
  }
}
```

**Generated Import Script Example:**
```bash
#!/bin/bash
# Import Data Stack

echo "Preview mode - checking what will be imported..."
cdk import DataStack --resource-mapping import-mappings/data-stack-mappings.json --dry-run

echo ""
read -p "Proceed with import? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Importing Data Stack resources..."
    cdk import DataStack --resource-mapping import-mappings/data-stack-mappings.json
    echo "Import complete!"
else
    echo "Import cancelled."
fi
```

**Usage Examples:**
```bash
# Generate import configurations
"Use cdk-import-config-generator to create import mappings and scripts for
the CDK project in cdk-organized/"

# Generate preview script only
"Use cdk-import-config-generator to create a preview script that shows what
will be imported without making changes"
```

**Success Criteria:**
- ✅ Generates valid resource identifier mappings for `cdk import`
- ✅ Creates working import scripts for each stack
- ✅ Includes preview/dry-run capability
- ✅ Provides clear instructions and checklist
- ✅ Includes rollback/recovery guidance
- ✅ Handles errors gracefully with helpful messages

**Implementation:**
```
cdk-import-config-generator/
├── SKILL.md
├── scripts/
│   ├── generate_import_configs.py     # Main script
│   ├── mapping_generator.py           # Create resource mappings
│   ├── script_generator.py            # Generate bash scripts
│   └── utils/
│       └── resource_identifier.py     # Extract resource identifiers
├── references/
│   ├── cdk_import_guide.md            # CDK import documentation
│   ├── resource_identifiers.md        # How to identify each resource type
│   └── troubleshooting.md             # Common import issues
└── assets/
    ├── script-templates/
    │   ├── preview.sh.template
    │   ├── import.sh.template
    │   └── rollback.sh.template
    ├── IMPORT_CHECKLIST.md.template
    └── README.md.template
```

---

### v1.1 - Enhanced Import

**New Features:**
- Incremental import (import additional resources to existing stacks)
- Import validation (verify resources exist before import)
- Conflict detection (check for naming conflicts)
- State backup before import

---

### v1.2 - Advanced Import

**New Features:**
- Multi-stack import coordination
- Dependency-aware import order
- Automated testing after import
- Drift detection post-import
- Integration with CI/CD pipelines

---

### v1.3 - Future Enhancements

**Enterprise Features:**
- Multi-account import orchestration
- Import progress tracking and logging
- Rollback automation
- Import audit trail
- Integration with change management systems

---

## Skill 5: aws-to-cdk-importer (Orchestrator)

### Purpose
Coordinate end-to-end AWS resource import workflow by orchestrating the four component skills.

### v2.0 - Initial Orchestrator (After Component Skills Mature)

**Features:**
- Invoke component skills in proper sequence
- Pass data between skills automatically
- Handle errors and retry logic
- Provide progress tracking
- Generate comprehensive reports

**Workflow:**
```
1. Discovery Phase
   └─→ Invoke aws-resource-discovery
       └─→ Output: resource-inventory/

2. Code Generation Phase
   └─→ Invoke cdk-code-generator
       └─→ Input: resource-inventory/
       └─→ Output: cdk-generated/

3. Organization Phase
   └─→ Invoke cdk-stack-organizer
       └─→ Input: cdk-generated/
       └─→ Output: cdk-organized/

4. Import Configuration Phase
   └─→ Invoke cdk-import-config-generator
       └─→ Input: cdk-organized/ + resource-inventory/
       └─→ Output: cdk-import-configs/

5. Summary Report
   └─→ Generate comprehensive report with next steps
```

**Usage Example:**
```bash
"Use aws-to-cdk-importer to import all my production Lambda functions and
DynamoDB tables from us-east-1 (profile: prod) into a new CDK project organized
by architectural layer"
```

**Implementation:**
```
aws-to-cdk-importer/
├── SKILL.md
├── scripts/
│   ├── orchestrate.py                 # Main orchestration script
│   ├── workflow_engine.py             # Execute skill sequence
│   └── utils/
│       ├── skill_invoker.py           # Invoke component skills
│       └── data_passer.py             # Pass data between skills
├── references/
│   ├── workflow_guide.md              # End-to-end workflow documentation
│   ├── component_skills.md            # When to use each component skill
│   └── troubleshooting.md             # Common workflow issues
└── assets/
    └── report-template.md             # Final summary report template
```

---

### v2.1 - Enhanced Orchestration

**New Features:**
- Interactive mode (prompt for user decisions at each phase)
- Configuration profiles (save/reuse common workflows)
- Parallel processing (multi-region, multi-account)
- Resume capability (restart from failed phase)

---

### v2.2 - Enterprise Orchestration

**New Features:**
- GitOps integration (automatic commits and PRs)
- Approval workflows
- Scheduled imports (continuous sync)
- Change notifications (Slack, email, webhooks)
- Metrics and dashboards

---

## Implementation Timeline

### Phase 1: Component Skills (v1.0) - Weeks 1-8
**Focus: Build core functionality for each skill independently**

- **Weeks 1-2:** aws-resource-discovery v1.0
  - Core 6 resource types
  - Filtered discovery
  - Dependency detection
  - Output format

- **Weeks 3-4:** cdk-code-generator v1.0
  - Reference-only mode
  - Full management mode
  - Core 6 resource types
  - TypeScript generation

- **Weeks 5-6:** cdk-stack-organizer v1.0
  - Organization strategies
  - Dependency handling
  - CDK project structure

- **Weeks 7-8:** cdk-import-config-generator v1.0
  - Import mappings
  - Import scripts
  - Documentation

### Phase 2: Testing & Refinement - Weeks 9-10
**Focus: Integration testing and user feedback**

- Test each skill independently
- Test skill chaining (manual workflow)
- Gather feedback and refine
- Documentation improvements

### Phase 3: Extended Resources (v1.1) - Weeks 11-14
**Focus: Add SQS, SNS, event source mappings**

- Update all 4 skills to support new resource types
- Enhanced dependency detection
- Integration testing

### Phase 4: API Services (v1.2) - Weeks 15-18
**Focus: Add API Gateway and AppSync**

- Complex resource hierarchies
- API configuration generation
- Integration testing

### Phase 5: Orchestrator (v2.0) - Weeks 19-22
**Focus: Build coordinated workflow**

- Orchestrator skill implementation
- Automated workflow execution
- Progress tracking
- Comprehensive testing

### Phase 6: Polish & Release - Weeks 23-24
**Focus: Production readiness**

- Performance optimization
- Documentation completion
- Example projects
- Public release

---

## Success Metrics

### For Each Component Skill:
- ✅ Successfully processes resources from real AWS accounts
- ✅ Generates valid, working output (JSON, TypeScript, scripts)
- ✅ Handles errors gracefully with helpful messages
- ✅ Includes comprehensive documentation and examples
- ✅ User can complete workflow independently

### For Complete System:
- ✅ End-to-end workflow completes successfully
- ✅ Generated CDK code compiles without errors
- ✅ `cdk import` successfully brings resources under management
- ✅ No manual intervention required (except AWS authentication)
- ✅ Works across different AWS accounts and resource configurations

---

## Risk Mitigation

### Technical Risks:
1. **AWS API Changes** → Pin boto3 versions, test regularly
2. **CDK Breaking Changes** → Support specific CDK v2 versions
3. **Complex Dependencies** → Start simple, add complexity gradually
4. **Import Failures** → Comprehensive preview and rollback

### Scope Risks:
1. **Feature Creep** → Stick to MVP scope for each version
2. **Resource Coverage** → Focus on common serverless resources first
3. **Edge Cases** → Document limitations clearly

### User Adoption Risks:
1. **Complexity** → Provide clear examples and documentation
2. **AWS Permissions** → Include IAM policy templates
3. **Learning Curve** → Video tutorials and walkthroughs

---

## Future Vision (Beyond v2.2)

### Advanced Capabilities:
- **AI-Powered Optimization**: Suggest improvements to discovered infrastructure
- **Cost Optimization**: Identify cost-saving opportunities
- **Security Analysis**: Detect security misconfigurations
- **Compliance Checking**: Verify against company policies
- **Terraform Compatibility**: Generate Terraform code as alternative
- **CloudFormation Import**: Support existing CFN stacks
- **Infrastructure as Code Translation**: Convert between IaC tools

### Ecosystem Integration:
- **AWS Control Tower**: Multi-account organization support
- **AWS Service Catalog**: Publish as service catalog product
- **CDK Construct Hub**: Publish reusable patterns
- **Marketplace**: AWS Marketplace listing

---

## Getting Started

### Immediate Next Steps:
1. ✅ Initialize `aws-resource-discovery` skill structure
2. ✅ Implement core discovery script for Lambda and DynamoDB
3. ✅ Test with real AWS account
4. ✅ Iterate based on testing results
5. → Move to `cdk-code-generator` skill

### Repository Structure:
```
claude-skills/
├── aws-resource-discovery/
├── cdk-code-generator/
├── cdk-stack-organizer/
├── cdk-import-config-generator/
├── aws-to-cdk-importer/           # (Future orchestrator)
├── AWS_CDK_IMPORTER_ROADMAP.md    # This file
└── examples/
    ├── simple-lambda-import/
    ├── multi-service-import/
    └── full-serverless-app-import/
```

---

**Last Updated:** 2025-01-07
**Current Focus:** aws-resource-discovery v1.0 MVP
**Next Milestone:** Discovery skill working end-to-end
