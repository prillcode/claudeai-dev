# AWS Infrastructure Skills

A suite of composable Claude Code skills for discovering AWS resources and generating CDK TypeScript code to import them into source control.

## Overview

This skill suite enables DevOps engineers to bring existing AWS infrastructure under CDK management through an automated, multi-phase workflow. Skills can be used independently or chained together for end-to-end resource import.

## Skills

### 1. aws-resource-discovery ✅
Scan AWS accounts to discover existing resources with full properties and dependency detection.

**Status:** v2.0 Complete
**Outputs:** Resource inventory JSON files organized by resource type

**Supported Resources:**
- Lambda functions
- DynamoDB tables
- IAM roles and policies
- S3 buckets
- EventBridge rules

### 2. cdk-code-generator ✅
Generate TypeScript CDK code from discovered AWS resources.

**Status:** v2.0 Complete
**Inputs:** Resource inventory from `aws-resource-discovery`
**Outputs:** TypeScript CDK constructs

**Modes:**
- Reference-only: `.fromAttributes()` calls for existing resources
- Full management: Complete construct definitions for CDK to manage

### 3. cdk-stack-organizer ✅
Intelligently organize CDK constructs into logical stacks with proper dependency management.

**Status:** v2.0 Complete
**Inputs:** Generated CDK code from `cdk-code-generator`
**Outputs:** Organized CDK project structure (bin/, lib/, cdk.json)

**Organization Strategies:**
- By architectural layer (data, compute, API)
- By service/application
- By tags
- Custom rules

### 4. cdk-import-config-generator ✅
Generate configurations and scripts to execute `cdk import` commands.

**Status:** v2.0 Complete
**Inputs:** Organized CDK project from `cdk-stack-organizer`
**Outputs:** Import mappings, bash scripts, verification scripts

### 5. aws-to-cdk-importer (Orchestrator) ✅
Coordinate end-to-end workflow across all component skills.

**Status:** v2.0 MVP Complete
**Purpose:** Automate the complete discovery → generation → organization → import pipeline in a single command

## Workflow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Discover   │─────▶│  Generate    │─────▶│  Organize    │─────▶│    Import    │
│  Resources   │      │  CDK Code    │      │    Stacks    │      │    Config    │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
Resource inventory → TypeScript constructs → Organized stacks → Import ready
```

## Use Cases

### Orchestrated Usage (Recommended)
Use the **aws-to-cdk-importer** orchestrator for end-to-end automation:
```bash
# Import serverless resources in one command
"Use aws-to-cdk-importer to import my Lambda functions and DynamoDB tables
from prod account in us-east-1, organized by layer"

# With filters
"Import resources tagged 'Project=MyApp' from dev account"
```

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

**👉 See [USE_CASES.md](./USE_CASES.md) for detailed conversation examples and common scenarios!**

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

- **[Use Cases & Examples](./USE_CASES.md)** - Natural language conversation examples showing how to use each skill with Claude Code
- [Complete Roadmap](./AWS_CDK_IMPORTER_ROADMAP.md) - Detailed implementation plan, timelines, and future vision
- Individual skill documentation in each skill's `SKILL.md` file

## Getting Started

### Quick Start

The fastest way to get started is with natural language:

```
"Use aws-to-cdk-importer to import Lambda and DynamoDB resources
from my prod account in us-east-1"
```

See **[USE_CASES.md](./USE_CASES.md)** for comprehensive examples and conversation templates!

### Current Status

✅ **Phase 1 & 2 Complete** - All 5 skills implemented and ready to use:
- aws-resource-discovery (v2.0)
- cdk-code-generator (v2.0)
- cdk-stack-organizer (v2.0)
- cdk-import-config-generator (v2.0)
- aws-to-cdk-importer orchestrator (v2.0 MVP)

### Repository Structure
```
aws-infra-skills/
├── README.md                          # This file
├── USE_CASES.md                       # Natural language usage examples (NEW!)
├── AWS_CDK_IMPORTER_ROADMAP.md        # Complete roadmap and vision
├── aws-resource-discovery/            # Skill 1 ✅
├── cdk-code-generator/                # Skill 2 ✅
├── cdk-stack-organizer/               # Skill 3 ✅
├── cdk-import-config-generator/       # Skill 4 ✅
└── aws-to-cdk-importer/               # Skill 5 - Orchestrator ✅
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
- **2025-11-08**: Phase 1 & 2 complete - All 5 skills implemented (v2.0)
  - aws-resource-discovery v2.0
  - cdk-code-generator v2.0
  - cdk-stack-organizer v2.0
  - cdk-import-config-generator v2.0
  - aws-to-cdk-importer orchestrator v2.0 MVP
  - USE_CASES.md with natural language examples added

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
**Last Updated:** 2025-11-08
**Current Status:** Phase 1 & 2 Complete - All 5 skills ready for use!
