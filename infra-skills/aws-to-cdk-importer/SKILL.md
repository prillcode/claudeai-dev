---
name: aws-to-cdk-importer
description: Orchestrate end-to-end AWS resource import workflow by coordinating aws-resource-discovery, cdk-code-generator, cdk-stack-organizer, and cdk-import-config-generator skills in sequence. This skill should be used when importing entire AWS environments into CDK projects with a single command, automating the complete workflow from resource discovery through import configuration generation.
---

# AWS to CDK Importer (Orchestrator)

## Overview

The AWS to CDK Importer orchestrator automates the complete workflow of importing existing AWS resources into AWS CDK projects. It coordinates four specialized component skills in a sequential pipeline, passing data between each phase and providing comprehensive progress tracking and error handling.

This skill eliminates the need to manually invoke each component skill separately, instead providing a single command that takes users from AWS account credentials to a complete CDK project ready for `cdk import`.

## When to Use This Skill

Use this skill when:

- Importing an entire AWS environment (or filtered subset) into a new CDK project
- Migrating existing AWS infrastructure to Infrastructure as Code using CDK
- Documenting existing AWS resources as CDK constructs
- Creating CDK import configurations for existing resources
- User requests to "import AWS resources to CDK" or "generate CDK code from AWS"

Do NOT use this skill when:

- Only a single phase is needed (e.g., just resource discovery) - use the specific component skill instead
- The user wants to customize or modify the workflow between phases
- Working with CloudFormation stacks (not supported in v2.0)

## Quick Start

Basic usage for importing Lambda and DynamoDB resources:

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb \
  --strategy layer \
  --output ./my-cdk-project
```

This single command will:
1. Discover all Lambda and DynamoDB resources in the account
2. Generate CDK TypeScript constructs for each resource
3. Organize constructs into stacks by architectural layer
4. Generate import configuration files and scripts
5. Create a comprehensive summary report

## Workflow Phases

The orchestrator executes five sequential phases:

### Phase 1: Resource Discovery

Invokes the `aws-resource-discovery` skill to scan the AWS account and create an inventory.

**What happens:**
- Connects to AWS using provided profile and region
- Applies resource type filters and tag filters
- Creates `resources.json` with all discovered resources
- Reports resource counts by type

**Output:** `<output-dir>/discovery/resources.json`

### Phase 2: CDK Code Generation

Invokes the `cdk-code-generator` skill to create TypeScript constructs.

**What happens:**
- Reads resource inventory from Phase 1
- Generates individual TypeScript construct files for each resource
- Creates proper CDK imports and dependencies
- Handles cross-resource references

**Modes:**
- `reference` (default): Generate constructs that reference existing resources
- `full`: Generate constructs for full management including creation

**Output:** `<output-dir>/cdk-generated/constructs/`

### Phase 3: Stack Organization

Invokes the `cdk-stack-organizer` skill to group constructs into logical stacks.

**What happens:**
- Analyzes generated constructs
- Groups resources by selected strategy
- Creates stack files with proper imports
- Generates main CDK app entry point

**Strategies:**
- `layer`: Group by architectural layer (compute, data, networking)
- `service`: Group by AWS service (all Lambda together, all DynamoDB together)
- `tag`: Group by AWS resource tags (requires tag-key parameter)
- `custom`: Group by custom rules (requires custom-rules file)

**Output:** `<output-dir>/cdk-organized/lib/stacks/`

### Phase 4: Import Configuration Generation

Invokes the `cdk-import-config-generator` skill to create import mappings and scripts.

**What happens:**
- Maps CDK construct logical IDs to AWS physical resource IDs
- Generates import configuration JSON files
- Creates shell scripts to run `cdk import` commands
- Creates verification scripts to check import status

**Output:**
- `<output-dir>/import-configs/mappings/*.json`
- `<output-dir>/import-configs/scripts/import-*.sh`
- `<output-dir>/import-configs/scripts/verify-imports.sh`

### Phase 5: Summary Report Generation

Creates a comprehensive final report of the entire workflow.

**What happens:**
- Aggregates statistics from all phases
- Lists all generated files and their locations
- Provides next steps for the user
- Includes troubleshooting guidance if issues occurred

**Output:** `<output-dir>/IMPORT_SUMMARY.md`

## Input Parameters

### Required Parameters

- `--profile`: AWS CLI profile name for authentication
- `--region`: AWS region to scan for resources
- `--output`: Output directory path for all generated files

### Optional Filters

- `--resource-types`: Comma-separated list of AWS resource types (e.g., `lambda,dynamodb,s3`)
- `--tag-filter`: Filter resources by tag (format: `Key=Value`)
- `--name-pattern`: Filter resources by name pattern (regex)

### Optional Configuration

- `--mode`: Code generation mode (`reference` or `full`), default: `reference`
- `--strategy`: Stack organization strategy (`layer`, `service`, `tag`, `custom`), default: `layer`
- `--tag-key`: Tag key for grouping when using `--strategy tag`
- `--custom-rules`: Path to custom rules file when using `--strategy custom`
- `--dry-run`: Simulate the workflow without making changes
- `--verbose`: Enable detailed logging

## Error Handling

The orchestrator includes comprehensive error handling:

### Phase Failure Behavior

If any phase fails:
1. Execution stops immediately
2. Error details are logged to `<output-dir>/error.log`
3. All intermediate outputs are preserved for debugging
4. User receives clear error message indicating which phase failed and why

### Common Error Scenarios

**Phase 1 Failure - Discovery Issues:**
- AWS credentials invalid or expired
- Insufficient IAM permissions
- No resources found matching filters
- Region not accessible

**Phase 2 Failure - Code Generation Issues:**
- Invalid resource types in discovery output
- Missing required resource properties
- Unsupported resource configuration

**Phase 3 Failure - Organization Issues:**
- Invalid stack strategy
- Missing tag key when using tag strategy
- Custom rules file not found or invalid

**Phase 4 Failure - Import Config Issues:**
- Resource ARN format issues
- Logical ID conflicts
- Missing physical resource IDs

### Partial Success Handling

If Phase 1-3 complete but Phase 4 fails, the user still has:
- Complete resource inventory
- Generated CDK constructs
- Organized stack files

The import configurations can be generated manually or by re-running just Phase 4.

## Progress Tracking

The orchestrator provides real-time progress updates:

```
[1/5] Discovering AWS resources...
      Profile: prod | Region: us-east-1
      ✓ Found 15 Lambda functions
      ✓ Found 8 DynamoDB tables
      ✓ Found 3 S3 buckets

[2/5] Generating CDK constructs...
      Mode: reference
      ✓ Generated 26 construct files

[3/5] Organizing into CDK stacks...
      Strategy: layer
      ✓ Created 3 stack files (compute, data, storage)

[4/5] Generating import configurations...
      ✓ Created import mappings for 26 resources
      ✓ Generated import scripts

[5/5] Creating summary report...
      ✓ Report saved to ./my-cdk-project/IMPORT_SUMMARY.md

✅ Workflow completed successfully!
   Output location: ./my-cdk-project
   Next steps: See IMPORT_SUMMARY.md
```

## Output Structure

The complete output directory structure:

```
my-cdk-project/
├── IMPORT_SUMMARY.md           # Final report with all statistics
├── discovery/
│   └── resources.json          # Phase 1: Resource inventory
├── cdk-generated/
│   ├── constructs/             # Phase 2: Individual construct files
│   │   ├── lambdas/
│   │   ├── dynamodb/
│   │   └── s3/
│   ├── dependencies.json       # NPM dependencies needed
│   └── metadata.json           # Generation metadata
├── cdk-organized/
│   ├── lib/
│   │   ├── stacks/             # Phase 3: Organized stack files
│   │   │   ├── compute-stack.ts
│   │   │   ├── data-stack.ts
│   │   │   └── storage-stack.ts
│   │   └── constructs/         # Construct files (moved from cdk-generated)
│   ├── bin/
│   │   └── app.ts              # CDK app entry point
│   ├── cdk.json
│   ├── package.json
│   └── tsconfig.json
└── import-configs/
    ├── mappings/               # Phase 4: Import mapping files
    │   ├── compute-stack-import.json
    │   ├── data-stack-import.json
    │   └── storage-stack-import.json
    └── scripts/                # Import execution scripts
        ├── import-all.sh       # Import all stacks
        ├── import-compute.sh
        ├── import-data.sh
        ├── import-storage.sh
        └── verify-imports.sh   # Verification script
```

## Usage Examples

### Example 1: Import All Lambda and DynamoDB (Basic)

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda,dynamodb \
  --output ./my-project
```

### Example 2: Import Resources with Specific Tag

```bash
python scripts/orchestrate.py \
  --profile dev \
  --region us-west-2 \
  --tag-filter "Environment=Production" \
  --strategy tag \
  --tag-key Application \
  --output ./prod-infrastructure
```

### Example 3: Full Management Mode (Not Just References)

```bash
python scripts/orchestrate.py \
  --profile staging \
  --region eu-west-1 \
  --resource-types lambda,dynamodb,s3,iam \
  --mode full \
  --strategy service \
  --output ./staging-cdk
```

### Example 4: Dry Run to Preview

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --resource-types lambda \
  --dry-run \
  --verbose
```

### Example 5: Custom Organization Rules

```bash
python scripts/orchestrate.py \
  --profile prod \
  --region us-east-1 \
  --strategy custom \
  --custom-rules ./my-org-rules.json \
  --output ./custom-organized
```

## Resources

### Scripts

The orchestrator includes several key scripts:

**Main Entry Point:**
- `scripts/orchestrate.py` - Main CLI interface that parses arguments and initiates the workflow

**Workflow Engine:**
- `scripts/workflow_engine.py` - Sequential phase execution engine with error handling

**Utilities:**
- `scripts/utils/skill_invoker.py` - Invokes component skills' Python scripts via subprocess
- `scripts/utils/data_passer.py` - Validates outputs and passes data between phases
- `scripts/utils/progress_tracker.py` - Displays real-time progress to the user

**Invocation Method:**

The orchestrator invokes component skills by calling their Python scripts directly:

```python
import subprocess

# Phase 1: Invoke aws-resource-discovery
result = subprocess.run([
    'python', '../aws-resource-discovery/scripts/discover.py',
    '--profile', profile,
    '--region', region,
    '--output', discovery_output_path
], capture_output=True, text=True)
```

Each skill's output directory becomes the input for the next skill.

### References

Detailed documentation files:

- `references/workflow_guide.md` - Complete end-to-end workflow explanation with detailed examples
- `references/component_skills.md` - Descriptions of all four component skills and their responsibilities
- `references/troubleshooting.md` - Common issues across all phases and how to resolve them

Load these reference files when:
- User asks "how does the orchestrator work?"
- User encounters errors and needs troubleshooting guidance
- User wants to understand what each component skill does

### Assets

Templates and visual aids:

- `assets/report-template.md` - Template for the final IMPORT_SUMMARY.md report
- `assets/workflow-diagram.md` - ASCII/Markdown diagram showing the 5-phase workflow

These assets are used by the orchestrator scripts to generate output files, not loaded into Claude's context.

## Version Notes

**Current Version: v2.0 MVP**

Features included:
- Sequential execution of all 5 phases
- Basic error handling with clear error messages
- Progress tracking with resource counts
- Support for all component skill features
- Comprehensive summary report generation

**Future Enhancements (v2.1+):**
- Interactive mode: Prompt user at each phase for approval before continuing
- Resume capability: Resume from a failed phase after fixing issues
- Configuration profiles: Save commonly-used parameter combinations
- Parallel discovery: Discover multiple regions simultaneously
- Incremental imports: Detect changes and only import new/modified resources

## Next Steps After Orchestration

Once the orchestrator completes successfully, users should:

1. **Review the Summary Report**
   ```bash
   cat <output-dir>/IMPORT_SUMMARY.md
   ```

2. **Install NPM Dependencies**
   ```bash
   cd <output-dir>/cdk-organized
   npm install
   ```

3. **Review Generated CDK Code**
   ```bash
   # Review stack files
   cat lib/stacks/*.ts

   # Review construct files
   cat lib/constructs/**/*.ts
   ```

4. **Run CDK Synthesis to Validate**
   ```bash
   npm run build
   cdk synth
   ```

5. **Execute Import Scripts**
   ```bash
   cd <output-dir>/import-configs/scripts
   ./import-all.sh
   ```

6. **Verify Imports**
   ```bash
   ./verify-imports.sh
   ```

7. **Commit to Version Control**
   ```bash
   git init
   git add .
   git commit -m "Initial CDK project from AWS import"
   ```

## Technical Architecture Notes

### Skill Coordination

The orchestrator acts as a workflow coordinator, not a library. It:
- Does NOT import component skills as Python modules
- Does invoke component skills' CLI scripts via subprocess
- Does validate outputs between phases
- Does provide unified error reporting

### Data Flow

```
AWS Account (Input)
    ↓
[Phase 1: Discovery] → resources.json
    ↓
[Phase 2: Code Gen] → constructs/*.ts
    ↓
[Phase 3: Organization] → stacks/*.ts + app.ts
    ↓
[Phase 4: Import Config] → mappings/*.json + scripts/*.sh
    ↓
[Phase 5: Report] → IMPORT_SUMMARY.md
    ↓
CDK Project Ready for cdk import (Output)
```

### Exit Codes

The orchestrator script uses standard exit codes:
- `0`: Success (all phases completed)
- `1`: Phase 1 failure (discovery)
- `2`: Phase 2 failure (code generation)
- `3`: Phase 3 failure (organization)
- `4`: Phase 4 failure (import config)
- `5`: Phase 5 failure (report generation)
- `100`: Invalid arguments or configuration

These exit codes allow scripts and CI/CD pipelines to detect which phase failed.
