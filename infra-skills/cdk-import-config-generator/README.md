# cdk-import-config-generator

Generate CDK import configurations and scripts to import existing AWS resources into CDK management.

## Overview

`cdk-import-config-generator` is a Claude Code skill that bridges the gap between your generated CDK code and actually bringing existing AWS resources under CDK management. It generates:
- Resource identifier mappings for `cdk import`
- Import scripts for each stack
- Preview/dry-run scripts
- Complete documentation and checklists

**Version**: 1.0 MVP

## Features

- ✅ Automatic resource identifier mapping
- ✅ Per-stack import scripts
- ✅ Import-all orchestration script
- ✅ Preview/dry-run capability
- ✅ Comprehensive import checklist
- ✅ Complete documentation

## Quick Start

> **Important**: No installation required! This skill uses Python standard library only (Python 3.12+).

### Installation

**No external dependencies needed** - uses Python 3.12+ standard library.

```bash
cd cdk-import-config-generator
# No pip install required!
```

### Usage Options

#### Option 1: Through Claude Code (Recommended)

Simply ask Claude to generate import configurations:

```
"Use cdk-import-config-generator to create import configs for the CDK project
in ./test-organized-output using resources from ../aws-resource-discovery/test-techops-inventory"

"Generate CDK import configurations for my organized project"

"Prepare import configs for cdk import"
```

**Benefits:**
- 🎯 Natural language interface
- 🤖 Claude finds the right paths automatically
- 📊 Claude reviews and explains the output
- 🔗 Claude chains with other skills

#### Option 2: Direct Python Execution

Run the Python script directly:

**Basic generation:**
```bash
python scripts/generate_import_configs.py \
  --cdk-project ../cdk-stack-organizer/my-app \
  --resource-inventory ../aws-resource-discovery/inventory \
  --output-dir ./import-configs
```

**Dry-run to preview:**
```bash
python scripts/generate_import_configs.py \
  --cdk-project ../cdk-stack-organizer/my-app \
  --resource-inventory ../aws-resource-discovery/inventory \
  --output-dir ./import-configs \
  --dry-run
```

**Skip preview scripts:**
```bash
python scripts/generate_import_configs.py \
  --cdk-project ../cdk-stack-organizer/my-app \
  --resource-inventory ../aws-resource-discovery/inventory \
  --output-dir ./import-configs \
  --skip-preview-scripts
```

## What Gets Generated

### Output Structure

```
import-configs/
├── import-mappings/
│   ├── computestack-mappings.json    # Resource ID mappings
│   ├── datastack-mappings.json
│   └── iamstack-mappings.json
├── scripts/
│   ├── preview-all.sh                 # Preview all imports
│   ├── import-all.sh                  # Import all stacks
│   ├── import-computestack.sh         # Import specific stack
│   ├── import-datastack.sh
│   └── import-iamstack.sh
├── README.md                          # Import instructions
└── IMPORT_CHECKLIST.md                # Step-by-step checklist
```

### 1. Resource Mapping Files

JSON files mapping CDK logical IDs to AWS physical resource identifiers:

```json
{
  "ComputeStack": {
    "OrderProcessorFunction": "order-processor",
    "UserServiceFunction": "user-service"
  }
}
```

### 2. Import Scripts

Executable bash scripts that:
- Change to CDK project directory
- Run `cdk import` with correct mappings
- Show preview before importing
- Prompt for confirmation
- Handle errors gracefully

### 3. Documentation

- **README.md**: Complete import instructions
- **IMPORT_CHECKLIST.md**: Step-by-step checklist
- Resource verification commands
- Troubleshooting guide

## Command-Line Options

### Required Arguments

- `--cdk-project DIR`: Path to organized CDK project directory (from cdk-stack-organizer)
- `--resource-inventory DIR`: Path to resource inventory directory (from aws-resource-discovery)
- `--output-dir DIR`: Output directory for import configurations

### Optional Arguments

- `--dry-run`: Preview what would be generated without creating files
- `--skip-preview-scripts`: Don't generate preview scripts

### Examples

**Basic generation:**
```bash
python scripts/generate_import_configs.py \
  --cdk-project ../cdk-stack-organizer/my-app \
  --resource-inventory ../aws-resource-discovery/prod-inventory \
  --output-dir ./prod-import-configs
```

**Dry-run mode:**
```bash
python scripts/generate_import_configs.py \
  --cdk-project ../cdk-stack-organizer/my-app \
  --resource-inventory ../aws-resource-discovery/inventory \
  --output-dir ./import-configs \
  --dry-run
```

## After Generation - The Import Process

### 1. Review Generated Mappings

```bash
cd import-configs
cat import-mappings/computestack-mappings.json
```

Verify:
- All expected resources are mapped
- Resource identifiers are correct
- No unexpected resources

### 2. Run Preview (Dry-Run)

```bash
cd scripts
./preview-all.sh
```

This shows what will be imported **without making changes**.

### 3. Review Preview Output

Check for:
- Correct resource identifiers
- No conflicts with existing CloudFormation stacks
- Warnings or errors

### 4. Execute the Import

```bash
# Still in scripts/ directory
./import-all.sh
```

Follow the prompts and confirm each stack import.

### 5. Verify the Import

```bash
cd ../../my-cdk-app
cdk diff --all
```

Should show **no changes** - resources are now under CDK management.

## Resource Identifier Mappings

Different AWS resource types use different identifiers:

| Resource Type | Identifier | Example |
|--------------|------------|---------|
| Lambda Function | Function name | `"order-processor"` |
| DynamoDB Table | Table name | `"users-table"` |
| S3 Bucket | Bucket name | `"my-bucket"` |
| IAM Role | Role name | `"my-role"` |
| IAM Policy | Policy ARN | `"arn:aws:iam::123:policy/my-policy"` |
| EventBridge Rule | Rule name | `"my-rule"` |

See [references/resource_identifiers.md](./references/resource_identifiers.md) for complete details.

## Project Structure

```
cdk-import-config-generator/
├── SKILL.md                      # Skill usage for Claude
├── README.md                     # This file
├── scripts/
│   ├── generate_import_configs.py  # Main generation script
│   └── utils/
│       ├── mapping_generator.py    # Generate resource mappings
│       ├── script_generator.py     # Generate bash scripts
│       └── resource_identifier.py  # Resource ID utilities
├── references/
│   └── resource_identifiers.md     # ID format reference
└── assets/
    └── script-templates/           # Script templates
```

## Troubleshooting

### Issue: "CDK project not found"
**Solution**: Verify the path to your organized CDK project from cdk-stack-organizer.

### Issue: "Resource inventory not found"
**Solution**: Verify the path to your resource inventory from aws-resource-discovery.

### Issue: "Missing organization metadata"
**Solution**: Ensure the CDK project was organized with cdk-stack-organizer (needs organization-metadata.json).

### Issue: "No resources matched"
**Solution**:
- Resource names in inventory must match construct names
- Check that resources still exist in AWS
- Verify resource naming conventions

### Issue: Import fails with "Resource not found"
**Solution**:
- Verify resource still exists: `aws lambda get-function --function-name my-function`
- Check AWS credentials/region
- Resource may have been deleted since discovery

### Issue: Import fails with "Resource already managed"
**Solution**:
- Resource is in another CloudFormation stack
- Check CloudFormation console
- Remove from other stack first or use `--force` (caution!)

## Important Notes

- **Backup First**: Always backup CloudFormation state before importing
- **Test First**: Test in dev/staging environments before production
- **One-Way Operation**: `cdk import` modifies CloudFormation state permanently
- **Permissions**: Requires both resource read and CloudFormation write permissions
- **Resource Conflicts**: Can't import resources already in CloudFormation

## Workflow Integration

**Full workflow:**
1. `aws-resource-discovery` → Discovers AWS resources
2. `cdk-code-generator` → Generates CDK constructs
3. `cdk-stack-organizer` → Organizes into stacks
4. **`cdk-import-config-generator`** → Creates import configs ← **YOU ARE HERE**
5. User runs `cdk import` → Imports resources into CloudFormation
6. Resources are now managed by CDK!

**Upstream (Input from):**
- `cdk-stack-organizer`: Provides organized CDK project
- `aws-resource-discovery`: Provides original resource inventory

**Downstream (Output to):**
- User executes generated import scripts
- Resources imported into CloudFormation
- CDK now manages the resources

## Roadmap

### v1.0 - MVP (Current) ✅
- [x] Resource identifier mapping
- [x] Import script generation
- [x] Preview scripts
- [x] Documentation generation
- [x] Support for 6 core resource types

### v1.1 - Enhanced Import (Planned)
- [ ] Incremental import support
- [ ] Import validation before execution
- [ ] Conflict detection and resolution
- [ ] State backup automation

### v1.2 - Advanced Features (Planned)
- [ ] Multi-stack import coordination
- [ ] Dependency-aware import order
- [ ] Automated testing after import
- [ ] Drift detection post-import

### v1.3 - Enterprise Features (Future)
- [ ] Multi-account import orchestration
- [ ] Import progress tracking
- [ ] Rollback automation
- [ ] Import audit trail

## Contributing

This skill is part of the AWS Infrastructure Skills suite. See [AWS_CDK_IMPORTER_ROADMAP.md](../AWS_CDK_IMPORTER_ROADMAP.md) for the complete project vision.

## Resources

- [Resource Identifiers Reference](./references/resource_identifiers.md)
- [CDK Import Command](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-import)
- [CloudFormation Resource Import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import.html)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please refer to the main project documentation.

---

**Version**: 1.0 MVP
**Status**: Active Development
**Last Updated**: 2025-11-08
