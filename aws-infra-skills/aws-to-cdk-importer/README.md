# AWS to CDK Importer (Orchestrator)

**Version:** 2.0 MVP

Orchestrate the complete end-to-end workflow of importing existing AWS resources into AWS CDK projects with a single command.

## Overview

The AWS to CDK Importer is an orchestrator skill that coordinates four specialized component skills to automate the complete workflow from AWS resource discovery through CDK import configuration generation. It provides a single command interface that eliminates the need to manually invoke each component skill separately.

**What it does:**
- Discovers existing AWS resources
- Generates TypeScript CDK constructs
- Organizes constructs into logical stacks
- Creates CDK import configurations and scripts
- Produces comprehensive summary reports

**What you get:**
A complete, ready-to-use CDK project with:
- TypeScript construct definitions
- Organized stack files
- CDK app entry point
- Import mapping configurations
- Executable import scripts
- Comprehensive documentation

## Quick Start

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **AWS CLI** configured with credentials
   ```bash
   aws configure
   ```

3. **Node.js 16+** and AWS CDK
   ```bash
   node --version
   npm install -g aws-cdk
   ```

4. **Component Skills Installed**
   - aws-resource-discovery
   - cdk-code-generator
   - cdk-stack-organizer
   - cdk-import-config-generator

### Basic Usage

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb \
  --strategy layer \
  --output ./my-cdk-project
```

This single command will:
1. Discover all Lambda and DynamoDB resources
2. Generate CDK constructs for each resource
3. Organize constructs into stacks by architectural layer
4. Generate import configurations and scripts
5. Create a comprehensive summary report

### Next Steps

After the orchestrator completes:

```bash
# 1. Install dependencies
cd my-cdk-project/cdk-organized
npm install

# 2. Build and synthesize
npm run build
cdk synth

# 3. Execute imports
cd ../import-configs/scripts
./import-all.sh

# 4. Verify
./verify-imports.sh
```

## Command-Line Options

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--profile` | AWS CLI profile name for authentication |
| `--region` | AWS region to scan (e.g., us-east-1) |
| `--output` | Output directory path for all generated files |

### Optional Filters

| Argument | Description |
|----------|-------------|
| `--resource-types` | Comma-separated resource types (e.g., lambda,dynamodb,s3) |
| `--tag-filter` | Filter by tag in Key=Value format |
| `--name-pattern` | Filter by name using regex pattern |

### Optional Configuration

| Argument | Default | Description |
|----------|---------|-------------|
| `--mode` | reference | Code generation mode: reference or full |
| `--strategy` | layer | Stack organization: layer, service, tag, or custom |
| `--tag-key` | - | Tag key for grouping (when strategy=tag) |
| `--custom-rules` | - | Path to custom rules JSON (when strategy=custom) |

### Optional Behavior Flags

| Argument | Description |
|----------|-------------|
| `--dry-run` | Simulate workflow without making changes |
| `--verbose` | Enable detailed logging |
| `--skip-phase` | Skip a specific phase (for testing/resume) |

## Usage Examples

### Example 1: Basic Lambda and DynamoDB Import

Import all Lambda functions and DynamoDB tables from production:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb \
  --output ./prod-import
```

**Result:**
- Reference-mode constructs (read-only)
- Organized by architectural layer
- Ready to import in ~5 minutes

### Example 2: Tagged Resources with Custom Organization

Import resources tagged with specific environment, organized by application:

```bash
python scripts/orchestrate.py \
  --profile dev \
  --region us-west-2 \
  --tag-filter "Environment=Production" \
  --strategy tag \
  --tag-key Application \
  --output ./prod-by-app
```

**Result:**
- Resources grouped by Application tag value
- One stack per application
- Filtered to Production environment only

### Example 3: Full Management Mode

Import resources for complete lifecycle management:

```bash
python scripts/orchestrate.py \
  --profile staging \
  --region eu-west-1 \
  --resource-types lambda,dynamodb,s3,iam \
  --mode full \
  --strategy service \
  --output ./staging-full
```

**Result:**
- Full management mode (can modify via CDK)
- Organized by AWS service
- Complete resource definitions

### Example 4: Dry Run Preview

Preview what would be imported without making changes:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda \
  --dry-run \
  --verbose
```

**Result:**
- Shows what would be executed
- No files created
- Useful for testing filters

### Example 5: Custom Organization Rules

Import with custom stack organization:

```bash
# Create custom rules file
cat > my-rules.json << EOF
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
EOF

python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --strategy custom \
  --custom-rules ./my-rules.json \
  --output ./custom-organized
```

**Result:**
- Resources organized by custom rules
- Flexible grouping patterns
- Tailored to your architecture

## 5-Phase Workflow

The orchestrator executes five sequential phases:

### Phase 1: Resource Discovery
**Skill:** aws-resource-discovery

Scans AWS account and creates resource inventory.

**Output:** `discovery/resources.json`

### Phase 2: CDK Code Generation
**Skill:** cdk-code-generator

Generates TypeScript CDK constructs for each resource.

**Output:** `cdk-generated/constructs/**/*.ts`

### Phase 3: Stack Organization
**Skill:** cdk-stack-organizer

Groups constructs into logical stacks based on strategy.

**Output:** `cdk-organized/` (complete CDK project)

### Phase 4: Import Configuration Generation
**Skill:** cdk-import-config-generator

Creates import mappings and executable scripts.

**Output:** `import-configs/mappings/` and `import-configs/scripts/`

### Phase 5: Summary Report Generation
**Orchestrator:** Internal

Generates comprehensive summary report.

**Output:** `IMPORT_SUMMARY.md`

## Output Directory Structure

```
my-cdk-project/
├── IMPORT_SUMMARY.md           # Summary report with next steps
│
├── discovery/
│   └── resources.json          # Phase 1: Resource inventory
│
├── cdk-generated/
│   ├── constructs/             # Phase 2: Generated constructs
│   │   ├── lambdas/
│   │   ├── dynamodb/
│   │   └── s3/
│   ├── dependencies.json
│   └── metadata.json
│
├── cdk-organized/              # Phase 3: CDK project
│   ├── bin/
│   │   └── app.ts              # CDK app entry point
│   ├── lib/
│   │   ├── stacks/             # Stack definitions
│   │   │   ├── compute-stack.ts
│   │   │   ├── data-stack.ts
│   │   │   └── storage-stack.ts
│   │   └── constructs/         # Construct files
│   ├── cdk.json
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
└── import-configs/             # Phase 4: Import configurations
    ├── mappings/
    │   ├── compute-stack-import.json
    │   ├── data-stack-import.json
    │   └── storage-stack-import.json
    └── scripts/
        ├── import-all.sh       # Import all stacks
        ├── import-compute.sh   # Individual stack imports
        ├── import-data.sh
        ├── import-storage.sh
        └── verify-imports.sh   # Verify import success
```

## Organization Strategies

### Layer Strategy (Default)

Groups by architectural layer:
- **compute-stack** - Lambda, ECS, EC2
- **data-stack** - DynamoDB, RDS, ElastiCache
- **storage-stack** - S3, EFS
- **networking-stack** - VPC, Subnets, Security Groups
- **iam-stack** - Roles, Policies

**Best for:** Most projects, clear separation of concerns

### Service Strategy

Groups by AWS service:
- **lambda-stack** - All Lambda functions
- **dynamodb-stack** - All DynamoDB tables
- **s3-stack** - All S3 buckets

**Best for:** Service-focused teams, simple architectures

### Tag Strategy

Groups by AWS resource tag value:
- Specify `--tag-key Application`
- Creates one stack per Application value

**Best for:** Multi-tenant systems, application-based organization

### Custom Strategy

Groups by user-defined rules in JSON file:

```json
{
  "stacks": {
    "frontend-stack": {
      "resources": ["*cloudfront*", "*s3*website*"]
    },
    "backend-stack": {
      "resources": ["*lambda*", "*api*"]
    }
  }
}
```

**Best for:** Complex requirements, specific organizational needs

## Generation Modes

### Reference Mode (Default)

- Generates constructs using `from*` methods
- Example: `Function.fromFunctionArn()`
- Read-only access to resources
- Does not manage resource lifecycle
- **Best for:** Initial imports, documentation, gradual migration

### Full Management Mode

- Generates constructs using constructors
- Example: `new Function()`
- Full lifecycle management
- Can modify resource configuration through CDK
- **Best for:** Complete IaC migration, new CDK-managed infrastructure

## Error Handling

The orchestrator includes comprehensive error handling:

### Phase Failure Behavior

If any phase fails:
1. Execution stops immediately
2. Error logged to `<output-dir>/error.log`
3. All intermediate outputs preserved
4. Clear error message indicates which phase failed

### Exit Codes

- `0` - Success (all phases completed)
- `1` - Phase 1 failure (discovery)
- `2` - Phase 2 failure (code generation)
- `3` - Phase 3 failure (organization)
- `4` - Phase 4 failure (import config)
- `5` - Phase 5 failure (report generation)
- `100` - Invalid arguments or configuration

### Troubleshooting

For detailed troubleshooting guidance, see:
- `references/troubleshooting.md` - Common issues and solutions
- `references/workflow_guide.md` - Complete workflow documentation
- `references/component_skills.md` - Component skill details

## Architecture

### Orchestrator Components

```
orchestrate.py              # Main entry point, CLI interface
│
├── workflow_engine.py      # Sequential phase execution
│   │
│   ├── Phase 1 execution
│   ├── Phase 2 execution
│   ├── Phase 3 execution
│   ├── Phase 4 execution
│   └── Phase 5 execution
│
└── utils/
    ├── skill_invoker.py    # Invoke component skills
    ├── data_passer.py      # Validate outputs
    └── progress_tracker.py # Display progress
```

### Skill Invocation

The orchestrator invokes component skills via subprocess:

```python
subprocess.run([
    'python',
    '../aws-resource-discovery/scripts/discover.py',
    '--profile', profile,
    '--region', region,
    '--output', output_path
])
```

Each skill's output directory becomes input for the next skill.

### Data Validation

Between each phase, the orchestrator validates:
- Expected output files exist
- File formats are correct
- Required data is present
- No corruption or missing fields

## Advanced Features

### Dry Run Mode

Simulate the workflow without making changes:

```bash
python scripts/orchestrate.py --dry-run --verbose ...
```

**Uses:**
- Test filters before running
- Verify configuration
- Estimate time and resource counts

### Verbose Logging

Enable detailed logging for troubleshooting:

```bash
python scripts/orchestrate.py --verbose ...
```

**Shows:**
- Detailed command execution
- Phase-by-phase progress
- Validation results
- Timing information

### Skip Phase (Advanced)

Skip a specific phase for testing or resume:

```bash
python scripts/orchestrate.py --skip-phase 1 ...
```

**Use cases:**
- Resume after fixing errors
- Test specific phases
- Development and debugging

**Warning:** Only use if you understand the workflow.

## Performance Considerations

### Small Environments (10-20 resources)
- **Time:** 2-5 minutes
- **Optimizations:** None needed

### Medium Environments (50-100 resources)
- **Time:** 5-15 minutes
- **Optimizations:** Consider filtering by resource type

### Large Environments (200+ resources)
- **Time:** 15-30 minutes
- **Optimizations:**
  - Use resource type filters
  - Import incrementally
  - Run from EC2 in same region

## Best Practices

1. **Start with Read-Only Reference Mode**
   - Always start with reference mode (default)
   - Validate generated code
   - Test imports without risk

2. **Use Tag Filters for Large Environments**
   - Tag resources before import
   - Use `--tag-filter` to limit scope
   - Import incrementally

3. **Review Generated Code Before Import**
   ```bash
   cd my-project/cdk-organized
   cat lib/stacks/*.ts
   ```

4. **Test Synthesis First**
   ```bash
   npm install
   npm run build
   cdk synth
   ```

5. **Import One Stack at a Time**
   ```bash
   cd import-configs/scripts
   ./import-compute.sh  # Test one first
   ./verify-imports.sh
   ./import-data.sh     # Then continue
   ```

6. **Version Control Immediately**
   ```bash
   git init
   git add .
   git commit -m "Initial CDK project from AWS import"
   ```

## Version Information

**Current Version:** 2.0 MVP

### Features Included

- Sequential execution of all 5 phases
- Basic error handling with clear messages
- Progress tracking with resource counts
- Support for all component skill features
- Comprehensive summary report generation

### Future Enhancements (v2.1+)

- **Interactive mode** - Prompt at each phase for approval
- **Resume capability** - Resume from failed phase
- **Configuration profiles** - Save commonly-used parameter combinations
- **Parallel discovery** - Discover multiple regions simultaneously
- **Incremental imports** - Detect changes and only import new/modified resources

## Component Skills

This orchestrator requires four component skills:

1. **aws-resource-discovery** - Phase 1: Discovers AWS resources
2. **cdk-code-generator** - Phase 2: Generates CDK constructs
3. **cdk-stack-organizer** - Phase 3: Organizes into stacks
4. **cdk-import-config-generator** - Phase 4: Creates import configs

Each component skill can also be used independently for specific tasks.

## Documentation

- **SKILL.md** - Complete skill documentation for Claude Code
- **references/workflow_guide.md** - End-to-end workflow guide
- **references/component_skills.md** - Component skill reference
- **references/troubleshooting.md** - Troubleshooting guide
- **assets/workflow-diagram.md** - Visual workflow diagrams
- **assets/report-template.md** - Summary report template

## Support

### Getting Help

1. **Check documentation:**
   - Read `references/workflow_guide.md`
   - Review `references/troubleshooting.md`

2. **Check error logs:**
   ```bash
   cat <output-dir>/error.log
   ```

3. **Run with verbose mode:**
   ```bash
   python scripts/orchestrate.py --verbose ...
   ```

4. **Review component skill logs:**
   - Each skill may have additional logs

### Reporting Issues

When reporting issues, include:
- Error messages
- Relevant configuration
- Output of `--dry-run --verbose`
- Component skill versions

## License

This skill is part of the AWS Infrastructure Skills suite.

## Authors

- AWS Infrastructure Skills Team
- Version 2.0 MVP - November 2025

## Acknowledgments

- AWS CDK Team for import functionality
- boto3 for AWS API access
- Component skill developers

---

**Ready to get started?** Run your first import:

```bash
python scripts/orchestrate.py \
  --profile your-profile \
  --region your-region \
  --output ./my-first-import
```
