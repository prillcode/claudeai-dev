#!/usr/bin/env python3
"""
CDK Import Config Generator - Generate configurations for importing AWS resources into CDK

This script takes an organized CDK project and the original resource inventory,
then generates import configurations and scripts for `cdk import`.

Usage:
    python generate_import_configs.py --cdk-project PATH --resource-inventory PATH --output-dir PATH
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

# Import utility modules
from utils.mapping_generator import MappingGenerator
from utils.script_generator import ScriptGenerator
from utils.resource_identifier import ResourceIdentifier


class ImportConfigGenerator:
    """Main orchestrator for import configuration generation"""

    def __init__(self, args):
        self.args = args
        self.cdk_project_dir = Path(args.cdk_project)
        self.inventory_dir = Path(args.resource_inventory)
        self.output_dir = Path(args.output_dir)
        self.dry_run = args.dry_run
        self.skip_preview = args.skip_preview_scripts

        # Load metadata
        self.org_metadata = self._load_org_metadata()
        self.inventory_metadata = self._load_inventory_metadata()
        self.resource_inventory = self._load_resource_inventory()

        # Initialize generators
        self.mapping_generator = MappingGenerator(
            self.org_metadata, self.resource_inventory
        )
        self.script_generator = ScriptGenerator(
            self.cdk_project_dir, self.skip_preview
        )

    def _load_org_metadata(self) -> Dict[str, Any]:
        """Load organization metadata from CDK project"""
        metadata_path = self.cdk_project_dir / "organization-metadata.json"
        if not metadata_path.exists():
            print(
                f"Error: organization-metadata.json not found in {self.cdk_project_dir}"
            )
            print("Make sure you're pointing to an organized CDK project from cdk-stack-organizer")
            sys.exit(1)

        with open(metadata_path, "r") as f:
            return json.load(f)

    def _load_inventory_metadata(self) -> Dict[str, Any]:
        """Load metadata from resource inventory"""
        metadata_path = self.inventory_dir / "metadata.json"
        if not metadata_path.exists():
            print(f"Error: metadata.json not found in {self.inventory_dir}")
            print(
                "Make sure you're pointing to a resource inventory from aws-resource-discovery"
            )
            sys.exit(1)

        with open(metadata_path, "r") as f:
            return json.load(f)

    def _load_resource_inventory(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all resource inventory JSON files"""
        inventory = {}

        resource_files = {
            "lambdas": "lambdas.json",
            "dynamodb": "dynamodb-tables.json",
            "iam_roles": "iam-roles.json",
            "iam_policies": "iam-policies.json",
            "s3": "s3-buckets.json",
            "eventbridge": "eventbridge-rules.json",
        }

        for resource_type, filename in resource_files.items():
            file_path = self.inventory_dir / filename
            if file_path.exists():
                with open(file_path, "r") as f:
                    resources = json.load(f)
                    if resources:  # Only add if not empty
                        inventory[resource_type] = resources

        if not inventory:
            print(f"Error: No resource files found in {self.inventory_dir}")
            sys.exit(1)

        return inventory

    def generate(self):
        """Main generation workflow"""
        print(f"🎯 CDK Import Config Generator v1.0")
        print(f"📂 CDK Project: {self.cdk_project_dir}")
        print(f"📦 Resource Inventory: {self.inventory_dir}")
        print(f"📁 Output: {self.output_dir}")
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be created")
        print()

        # Step 1: Generate resource mappings
        print("🔍 Step 1: Generating resource identifier mappings...")
        mappings = self.mapping_generator.generate_mappings()
        print(f"✅ Generated mappings for {len(mappings)} stack(s)")
        for stack_name, resources in mappings.items():
            print(f"   - {stack_name}: {len(resources)} resource(s)")
        print()

        if not self.dry_run:
            # Step 2: Create output directory structure
            print("📁 Step 2: Creating output directory structure...")
            self._create_directory_structure()
            print("✅ Directory structure created")
            print()

            # Step 3: Write mapping files
            print("💾 Step 3: Writing mapping files...")
            self._write_mapping_files(mappings)
            print(f"✅ Wrote {len(mappings)} mapping file(s)")
            print()

            # Step 4: Generate import scripts
            print("📝 Step 4: Generating import scripts...")
            self._generate_scripts(mappings)
            script_count = len(mappings) + 1  # Individual + import-all.sh
            if not self.skip_preview:
                script_count += 1  # preview-all.sh
            print(f"✅ Generated {script_count} script(s)")
            print()

            # Step 5: Generate documentation
            print("📚 Step 5: Generating documentation...")
            self._generate_documentation(mappings)
            print("✅ Documentation generated")
            print()

            print("🎉 Import configuration generation complete!")
            print()
            print("📋 Next steps:")
            print(f"   1. cd {self.output_dir}/scripts")
            if not self.skip_preview:
                print("   2. ./preview-all.sh  # Preview what will be imported")
                print("   3. Review the output carefully")
                print("   4. ./import-all.sh  # Execute the import")
            else:
                print("   2. ./import-all.sh  # Execute the import")
            print(f"   5. cd {self.cdk_project_dir}")
            print("   6. cdk diff  # Verify no changes (should be empty)")
            print()
        else:
            print("🔍 Dry run complete - no files were created")
            print()
            print("Preview of what would be generated:")
            print(f"  - {len(mappings)} mapping file(s)")
            print(f"  - {len(mappings) + 2} script file(s)")
            print(f"  - 2 documentation file(s)")
            print()

    def _create_directory_structure(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "import-mappings").mkdir(exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)

    def _write_mapping_files(self, mappings: Dict[str, Dict[str, str]]):
        """Write resource mapping JSON files"""
        for stack_name, resources in mappings.items():
            # Create mapping file with stack name
            mapping_data = {stack_name: resources}

            output_file = (
                self.output_dir
                / "import-mappings"
                / f"{stack_name.lower()}-mappings.json"
            )

            with open(output_file, "w") as f:
                json.dump(mapping_data, f, indent=2)

    def _generate_scripts(self, mappings: Dict[str, Dict[str, str]]):
        """Generate import scripts"""
        scripts_dir = self.output_dir / "scripts"

        # Get stack deployment order
        stacks = self.org_metadata.get("stacks", {})
        dependencies = self.org_metadata.get("dependencies", {})
        ordered_stacks = self._topological_sort(stacks, dependencies)

        # Generate individual stack import scripts
        for stack_name in mappings.keys():
            script_content = self.script_generator.generate_stack_import_script(
                stack_name, self.org_metadata
            )
            script_file = scripts_dir / f"import-{stack_name.lower()}.sh"
            script_file.write_text(script_content)
            script_file.chmod(0o755)  # Make executable

        # Generate import-all script
        import_all_content = self.script_generator.generate_import_all_script(
            ordered_stacks
        )
        import_all_file = scripts_dir / "import-all.sh"
        import_all_file.write_text(import_all_content)
        import_all_file.chmod(0o755)

        # Generate preview-all script (unless skipped)
        if not self.skip_preview:
            preview_all_content = self.script_generator.generate_preview_all_script(
                ordered_stacks
            )
            preview_all_file = scripts_dir / "preview-all.sh"
            preview_all_file.write_text(preview_all_content)
            preview_all_file.chmod(0o755)

    def _generate_documentation(self, mappings: Dict[str, Dict[str, str]]):
        """Generate README and checklist"""
        # Generate README
        readme_content = self._generate_readme(mappings)
        (self.output_dir / "README.md").write_text(readme_content)

        # Generate checklist
        checklist_content = self._generate_checklist(mappings)
        (self.output_dir / "IMPORT_CHECKLIST.md").write_text(checklist_content)

    def _generate_readme(self, mappings: Dict[str, Dict[str, str]]) -> str:
        """Generate README content"""
        readme = f"""# CDK Import Configurations

Generated by **cdk-import-config-generator** on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## Overview

This directory contains everything needed to import your existing AWS resources into CDK management using `cdk import`.

**⚠️ IMPORTANT**: Read the [IMPORT_CHECKLIST.md](./IMPORT_CHECKLIST.md) before proceeding!

## What's Included

### Import Mappings (`import-mappings/`)

JSON files mapping CDK logical IDs to AWS physical resource identifiers:

"""
        for stack_name in mappings.keys():
            readme += f"- `{stack_name.lower()}-mappings.json` - Mappings for {stack_name}\n"

        readme += """
### Import Scripts (`scripts/`)

"""
        if not self.skip_preview:
            readme += """- `preview-all.sh` - **RUN THIS FIRST** - Preview all imports without making changes
"""
        readme += """- `import-all.sh` - Import all stacks in dependency order
"""

        for stack_name in mappings.keys():
            readme += f"- `import-{stack_name.lower()}.sh` - Import {stack_name} only\n"

        readme += f"""

## Quick Start

### 1. Prerequisites

- AWS CDK CLI installed (`npm install -g aws-cdk` or `pnpm add -g aws-cdk`)
- AWS credentials configured (same account as discovered resources)
- CDK project is built and synthesizes successfully
- **BACKUP**: Ensure CloudFormation state is backed up

### 2. Verify CDK Project

```bash
cd {self.cdk_project_dir.name}

# Build the project
pnpm install  # or npm install
pnpm run build  # or npm run build

# Synthesize CloudFormation templates
cdk synth

# Should succeed without errors
```

### 3. Preview the Import (Dry Run)

"""
        if not self.skip_preview:
            readme += """```bash
cd scripts
./preview-all.sh
```

This will show you what resources will be imported **without making any changes**.

Review the output carefully:
- Verify resource identifiers are correct
- Check for any warnings or errors
- Ensure no unexpected resources are included

"""
        else:
            readme += """```bash
# Preview disabled - use cdk import with manual verification
```

"""

        readme += """### 4. Execute the Import

```bash
# Still in scripts/ directory
./import-all.sh
```

This will import all stacks in dependency order. You'll be prompted to confirm at each step.

### 5. Verify the Import

```bash
cd ../{self.cdk_project_dir.name}

# Check that CDK now manages the resources
cdk diff

# Should show NO changes (resources are now managed by CDK)
```

If `cdk diff` shows changes, something went wrong. See Troubleshooting below.

## Resource Inventory

**Source Account**: {self.inventory_metadata.get('account_id', 'N/A')}
**Source Region**: {self.inventory_metadata.get('region', 'N/A')}
**Discovered On**: {self.inventory_metadata.get('scan_timestamp', 'N/A')}

**Resources to Import**:
"""

        # Count total resources
        total_resources = sum(len(resources) for resources in mappings.values())
        readme += f"\n**Total**: {total_resources} resource(s) across {len(mappings)} stack(s)\n\n"

        for stack_name, resources in mappings.items():
            readme += f"- **{stack_name}**: {len(resources)} resource(s)\n"

        readme += """

## Troubleshooting

### Issue: Preview shows unexpected resources
**Solution**: Review the mapping files in `import-mappings/`. Remove any resources you don't want to import.

### Issue: Import fails with "Resource not found"
**Solution**:
- Verify the resource still exists in AWS
- Check that you're using the correct AWS profile/credentials
- Resource may have been deleted since discovery

### Issue: Import fails with "Resource already exists in stack"
**Solution**:
- Resource may already be managed by another CloudFormation stack
- Check CloudFormation console for conflicts
- You may need to remove the resource from the other stack first

### Issue: `cdk diff` shows changes after import
**Solution**:
- Generated CDK code may not match actual resource configuration
- Review the differences and update CDK code to match
- Some properties can't be imported (e.g., Lambda code)

### Issue: Need to rollback
**Solution**:
- CDK import modifies CloudFormation state - there's no automatic rollback
- You'll need to manually remove imported resources from CloudFormation
- See AWS CloudFormation console → Stack → Resources → Remove

## Important Notes

- **One-way operation**: `cdk import` modifies CloudFormation state permanently
- **Test first**: Always test in dev/staging before production
- **Backup**: Ensure CloudFormation state is backed up before importing
- **Permissions**: Requires both read (for verification) and CloudFormation write permissions
- **State management**: After import, resources are managed by CDK/CloudFormation

## Resources

- [CDK Import Documentation](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-import)
- [Checklist](./IMPORT_CHECKLIST.md)

---

**Generated by**: cdk-import-config-generator v1.0
**Part of**: AWS Infrastructure Skills Suite
"""
        return readme

    def _generate_checklist(self, mappings: Dict[str, Dict[str, str]]) -> str:
        """Generate import checklist"""
        checklist = f"""# CDK Import Checklist

Complete this checklist before importing resources into CDK management.

## Pre-Import Checklist

### 1. Environment Verification

- [ ] Verified correct AWS account ({self.inventory_metadata.get('account_id', 'N/A')})
- [ ] Verified correct region ({self.inventory_metadata.get('region', 'N/A')})
- [ ] AWS credentials are configured and valid
- [ ] Have necessary IAM permissions (read resources + CloudFormation write)

### 2. CDK Project Verification

- [ ] CDK project is built successfully (`pnpm run build`)
- [ ] CDK synthesizes without errors (`cdk synth`)
- [ ] All stack files are present in `lib/`
- [ ] Reviewed generated CDK code for accuracy

### 3. Resource Verification

- [ ] Reviewed all mapping files in `import-mappings/`
- [ ] Verified resource identifiers are correct
- [ ] Confirmed all resources still exist in AWS
- [ ] No resources are already managed by other CloudFormation stacks

### 4. Backup and Safety

- [ ] CloudFormation state has been backed up
- [ ] Tested import process in dev/staging environment first
- [ ] Have rollback plan documented
- [ ] Team has been notified of upcoming import

### 5. Preview (Dry Run)

"""
        if not self.skip_preview:
            checklist += """- [ ] Ran `./preview-all.sh` successfully
- [ ] Reviewed preview output carefully
- [ ] No unexpected resources in preview
- [ ] No errors in preview output
"""
        else:
            checklist += """- [ ] Manually verified resources using `cdk import --help`
"""

        checklist += """
## Import Execution

### During Import

- [ ] Running from correct directory (`scripts/`)
- [ ] Monitoring output for errors
- [ ] Resources are being imported successfully

### After Import

- [ ] All stacks imported successfully
- [ ] No errors in import output
- [ ] Verified with `cdk diff` (should show no changes)
- [ ] CloudFormation console shows resources under CDK stack

## Post-Import Verification

### 1. Resource Verification

- [ ] All expected resources are in CloudFormation
- [ ] Resource configurations match CDK code
- [ ] No drift detected (`cdk diff` shows nothing)

### 2. Functionality Testing

- [ ] Tested application functionality
- [ ] Resources are accessible and working
- [ ] No unexpected behavior changes

### 3. Documentation

- [ ] Documented the import process
- [ ] Updated team documentation
- [ ] Noted any issues or gotchas for future reference

## Rollback (If Needed)

If something goes wrong:

- [ ] Documented what went wrong
- [ ] Have a plan to fix/remove imported resources
- [ ] Contacted AWS support if needed

## Sign-Off

- **Performed by**: _______________
- **Date**: _______________
- **Environment**: _______________
- **Status**: [ ] Success  [ ] Failed  [ ] Partial

---

**Notes**:

"""
        return checklist

    def _topological_sort(
        self, stacks: Dict[str, Any], dependencies: Dict[str, List[str]]
    ) -> List[str]:
        """Topologically sort stacks based on dependencies"""
        in_degree = {}
        adj_list = {}

        # Initialize
        for stack_name in stacks.keys():
            in_degree[stack_name] = 0
            adj_list[stack_name] = []

        # Build adjacency list
        for stack_name, deps in dependencies.items():
            for dep in deps:
                adj_list[dep].append(stack_name)
                in_degree[stack_name] += 1

        # Kahn's algorithm
        queue = [stack for stack, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            queue.sort()  # Deterministic order
            current = queue.pop(0)
            result.append(current)

            for dependent in adj_list[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate CDK import configurations and scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation
  python generate_import_configs.py \\
    --cdk-project ../cdk-stack-organizer/my-app \\
    --resource-inventory ../aws-resource-discovery/inventory \\
    --output-dir ./import-configs

  # Dry run to preview
  python generate_import_configs.py \\
    --cdk-project ../cdk-stack-organizer/my-app \\
    --resource-inventory ../aws-resource-discovery/inventory \\
    --output-dir ./import-configs \\
    --dry-run
        """,
    )

    # Required arguments
    parser.add_argument(
        "--cdk-project",
        required=True,
        help="Path to organized CDK project directory (from cdk-stack-organizer)",
    )
    parser.add_argument(
        "--resource-inventory",
        required=True,
        help="Path to resource inventory directory (from aws-resource-discovery)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for import configurations",
    )

    # Optional arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without creating files",
    )
    parser.add_argument(
        "--skip-preview-scripts",
        action="store_true",
        help="Don't generate preview scripts",
    )

    args = parser.parse_args()

    # Validate input directories
    if not Path(args.cdk_project).exists():
        print(f"Error: CDK project directory does not exist: {args.cdk_project}")
        sys.exit(1)

    if not Path(args.resource_inventory).exists():
        print(
            f"Error: Resource inventory directory does not exist: {args.resource_inventory}"
        )
        sys.exit(1)

    # Run generator
    try:
        generator = ImportConfigGenerator(args)
        generator.generate()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
