---
name: cdk-import-config-generator
description: Generate CDK import configurations and scripts to import existing AWS resources into CDK management. This skill should be used after cdk-stack-organizer to create resource mappings, import scripts, and documentation for executing cdk import commands.
---

# cdk-import-config-generator

Generate CDK import configurations and scripts to import existing AWS resources into CDK management.

## What This Skill Does

Takes an organized CDK project (from `cdk-stack-organizer`) and the original resource inventory (from `aws-resource-discovery`), then generates:
- Resource identifier mappings for `cdk import`
- Import scripts for each stack
- Preview/dry-run scripts
- Rollback documentation
- Import checklist

## When to Use This Skill

Use this skill **after** organizing your CDK stacks and **before** running `cdk import` to actually import resources.

**Trigger phrases:**
- "generate CDK import configurations"
- "create import mappings for my CDK stacks"
- "prepare for cdk import"
- "generate import scripts"

## Input Requirements

1. **Organized CDK project directory** (from cdk-stack-organizer)
   - Must contain `organization-metadata.json`
   - Must contain stack files in `lib/`

2. **Original resource inventory directory** (from aws-resource-discovery)
   - Must contain resource JSON files (lambdas.json, dynamodb-tables.json, etc.)
   - Must contain `metadata.json`

## Output Structure

```
cdk-import-configs/
├── import-mappings/
│   ├── computestack-mappings.json    # Resource ID mappings per stack
│   ├── datastack-mappings.json
│   └── iamstack-mappings.json
├── scripts/
│   ├── preview-all.sh                 # Preview all imports (dry-run)
│   ├── import-all.sh                  # Import all stacks
│   ├── import-computestack.sh         # Import specific stack
│   ├── import-datastack.sh
│   └── import-iamstack.sh
├── README.md                          # Import instructions
└── IMPORT_CHECKLIST.md                # Step-by-step checklist
```

## What Gets Generated

### 1. Resource Mapping Files

JSON files mapping CDK logical IDs to AWS physical resource IDs:

```json
{
  "ComputeStack": {
    "OrderProcessorFunction": "order-processor",
    "UserServiceFunction": "user-service"
  }
}
```

### 2. Import Scripts

Bash scripts that execute `cdk import` with proper mappings:

- `preview-all.sh` - Dry-run to see what will be imported
- `import-all.sh` - Import all stacks in dependency order
- `import-{stack}.sh` - Import individual stacks

### 3. Documentation

- `README.md` - Complete import instructions
- `IMPORT_CHECKLIST.md` - Step-by-step checklist
- Rollback guidance

## Usage Examples

### Basic Usage
```
Use cdk-import-config-generator to create import configurations for the CDK project
in ./my-cdk-app using the resource inventory from ../aws-resource-discovery/resource-inventory
```

### With Custom Paths
```
Generate CDK import configs for the organized project in ./cdk-organized
using resources from ./prod-inventory
```

## How Claude Should Invoke This Skill

When the user requests import configuration generation:

1. **Locate both input directories**:
   - Organized CDK project (from cdk-stack-organizer)
   - Original resource inventory (from aws-resource-discovery)

2. **Execute the generate script**:
   ```bash
   python scripts/generate_import_configs.py \
     --cdk-project PATH_TO_CDK_PROJECT \
     --resource-inventory PATH_TO_INVENTORY \
     --output-dir PATH_TO_OUTPUT
   ```

3. **Report the results** and guide user through next steps

## Command-Line Interface

### Required Arguments
- `--cdk-project DIR`: Path to organized CDK project directory
- `--resource-inventory DIR`: Path to resource inventory directory
- `--output-dir DIR`: Output directory for import configurations

### Optional Arguments
- `--dry-run`: Generate configs without creating files [default: false]
- `--skip-preview-scripts`: Don't generate preview scripts [default: false]

### Examples

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

## What Happens After Generation

Claude should guide the user through:

1. **Review Generated Mappings**:
   ```bash
   cat import-configs/import-mappings/datastack-mappings.json
   ```

2. **Run Preview (Dry-Run)**:
   ```bash
   cd import-configs/scripts
   ./preview-all.sh
   ```

3. **Review Preview Output**:
   - Check which resources will be imported
   - Verify resource identifiers are correct
   - Check for any conflicts

4. **Execute Import** (if preview looks good):
   ```bash
   ./import-all.sh
   ```

5. **Verify Import**:
   ```bash
   cd ../../my-cdk-app
   cdk diff  # Should show no changes
   ```

## Resource Identifier Mappings

Different AWS resource types require different identifiers:

| Resource Type | Identifier | Example |
|--------------|------------|---------|
| Lambda Function | Function name | `"my-function"` |
| DynamoDB Table | Table name | `"users-table"` |
| S3 Bucket | Bucket name | `"my-bucket"` |
| IAM Role | Role name | `"my-role"` |
| EventBridge Rule | Rule name | `"my-rule"` |

See [references/resource_identifiers.md](./references/resource_identifiers.md) for complete details.

## Error Handling

Common issues and solutions:

- **"CDK project not found"**: Check path to organized CDK project
- **"Resource inventory not found"**: Check path to discovery output
- **"Missing organization metadata"**: Ensure CDK project was organized with cdk-stack-organizer
- **"Resource mismatch"**: Some resources in CDK don't match inventory - manual review needed

## Dependencies

- Python 3.12+ (standard library only)
- No external Python packages required
- Bash shell (for generated scripts)
- AWS CDK CLI (for running imports)

## Success Criteria

After running this skill:
- ✅ Resource mapping files created for all stacks
- ✅ Import scripts generated and executable
- ✅ Preview scripts work correctly
- ✅ Documentation is complete and clear
- ✅ Checklist guides user through import process

## Integration with Other Skills

**Upstream (Input from):**
- `cdk-stack-organizer`: Provides organized CDK project
- `aws-resource-discovery`: Provides original resource inventory

**Downstream (Output to):**
- User runs `cdk import` with generated configurations
- Resources are imported into CloudFormation

**Full Workflow:**
1. `aws-resource-discovery` → discovers resources
2. `cdk-code-generator` → generates constructs
3. `cdk-stack-organizer` → organizes into stacks
4. **`cdk-import-config-generator`** → creates import configs ← YOU ARE HERE
5. User runs `cdk import` → imports resources

## Important Notes

- **Backup First**: Always backup CloudFormation state before importing
- **Test in Lower Environments**: Test import process in dev/staging first
- **One-Way Operation**: `cdk import` modifies CloudFormation state
- **Resource Conflicts**: Existing CloudFormation resources may conflict
- **Permissions**: Ensure IAM permissions for both read and CloudFormation write

## Version

**Version**: 1.0 MVP
**Status**: Active Development
**Last Updated**: 2025-11-08
