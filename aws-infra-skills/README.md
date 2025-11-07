# AWS Infrastructure Skills

A suite of composable Claude Code skills for discovering AWS resources and generating CDK TypeScript code to import them into source control.

## Overview

This skill suite enables DevOps engineers to bring existing AWS infrastructure under CDK management through an automated, multi-phase workflow. Skills can be used independently or chained together for end-to-end resource import.

## Skills

### 1. aws-resource-discovery
Scan AWS accounts to discover existing resources with full properties and dependency detection.

**Status:** v1.0 MVP (In Development)
**Outputs:** Resource inventory JSON files organized by resource type

**Supported Resources (v1.0):**
- Lambda functions
- DynamoDB tables
- IAM roles and policies
- S3 buckets
- EventBridge rules

### 2. cdk-code-generator
Generate TypeScript CDK code from discovered AWS resources.

**Status:** Planned
**Inputs:** Resource inventory from `aws-resource-discovery`
**Outputs:** TypeScript CDK constructs

**Modes:**
- Reference-only: `.fromAttributes()` calls for existing resources
- Full management: Complete construct definitions for CDK to manage

### 3. cdk-stack-organizer
Intelligently organize CDK constructs into logical stacks with proper dependency management.

**Status:** Planned
**Inputs:** Generated CDK code from `cdk-code-generator`
**Outputs:** Organized CDK project structure (bin/, lib/, cdk.json)

**Organization Strategies:**
- By architectural layer (data, compute, API)
- By service/application
- By environment (dev/staging/prod)
- By tags

### 4. cdk-import-config-generator
Generate configurations and scripts to execute `cdk import` commands.

**Status:** Planned
**Inputs:** Organized CDK project from `cdk-stack-organizer`
**Outputs:** Import mappings, bash scripts, checklists

### 5. aws-to-cdk-importer (Orchestrator)
Coordinate end-to-end workflow across all component skills.

**Status:** Future (v2.0)
**Purpose:** Automate the complete discovery → generation → organization → import pipeline

## Workflow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Discover   │─────▶│  Generate    │─────▶│  Organize    │─────▶│    Import    │
│  Resources   │      │  CDK Code    │      │    Stacks    │      │    Config    │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
Resource inventory → TypeScript constructs → Organized stacks → Import ready
```

## Use Cases

### Standalone Usage
Each skill works independently:
```bash
# Only discover resources
"Use aws-resource-discovery to scan my production account"

# Only generate CDK code from existing inventory
"Use cdk-code-generator to create reference imports from resource-inventory/"
```

### Chained Usage
Skills naturally chain together via shared data formats:
```bash
# Manual workflow: Run each skill sequentially
1. Discover resources → produces resource-inventory/
2. Generate CDK code → consumes resource-inventory/, produces cdk-generated/
3. Organize stacks → consumes cdk-generated/, produces cdk-organized/
4. Generate import config → consumes cdk-organized/, produces import-ready project
```

### Orchestrated Usage (Future)
```bash
# Automated end-to-end
"Use aws-to-cdk-importer to import all Lambda functions from my prod account into CDK"
```

## Target Users

- AWS DevOps engineers working with TypeScript CDK
- Teams managing multi-account AWS environments
- Developers working with serverless architectures
- Organizations bringing existing AWS infrastructure under IaC management

## Key Features

- ✅ Discovers resources across AWS accounts with complete configurations
- ✅ Detects dependencies between resources (Lambda→DynamoDB, etc.)
- ✅ Generates valid, compilable TypeScript CDK code
- ✅ Supports both reference-only and full management import modes
- ✅ Intelligently organizes resources into logical stacks
- ✅ Handles cross-stack dependencies automatically
- ✅ Generates executable import scripts with preview/rollback capabilities
- ✅ Works with AWS CLI profiles including SSO

## Documentation

- [Complete Roadmap](./AWS_CDK_IMPORTER_ROADMAP.md) - Detailed implementation plan, timelines, and future vision
- Individual skill documentation in each skill's `SKILL.md` file

## Getting Started

### Current Status (Week 1-2)
Building **aws-resource-discovery v1.0 MVP** with core serverless resources (Lambda, DynamoDB, IAM, S3, EventBridge).

### Repository Structure
```
aws-infra-skills/
├── README.md                          # This file
├── AWS_CDK_IMPORTER_ROADMAP.md        # Complete roadmap and vision
├── aws-resource-discovery/            # Skill 1 (In Development)
├── cdk-code-generator/                # Skill 2 (Planned)
├── cdk-stack-organizer/               # Skill 3 (Planned)
├── cdk-import-config-generator/       # Skill 4 (Planned)
└── aws-to-cdk-importer/               # Skill 5 - Orchestrator (Future)
```

## Prerequisites

- AWS CLI configured with profiles
- Appropriate IAM permissions for resource discovery
- Node.js and AWS CDK v2 installed (for code generation skills)
- Python 3.8+ with boto3 (for discovery scripts)

## Contributing

This is part of a mono-repo of Claude Code skills. Each skill follows the standard skill structure:
- `SKILL.md` - Skill documentation and usage instructions
- `scripts/` - Executable code (Python/Bash)
- `references/` - Documentation loaded as needed
- `assets/` - Templates and files used in output

## Version History

- **2025-11-07**: Project initiated, roadmap created
- **Current**: aws-resource-discovery v1.0 MVP in development

## Future Enhancements

See [AWS_CDK_IMPORTER_ROADMAP.md](./AWS_CDK_IMPORTER_ROADMAP.md) for complete roadmap including:
- Extended resource support (SQS, SNS, API Gateway, AppSync)
- Multi-region and multi-account scanning
- Advanced dependency detection
- CDK Pipelines integration
- Drift detection and compliance checking
- Cost optimization suggestions

---

**Maintained by:** Aaron Prill
**Last Updated:** 2025-11-07
**Current Focus:** aws-resource-discovery v1.0
