#!/usr/bin/env python3
"""
CDK Stack Organizer - Organize CDK constructs into logical stacks

This script takes generated CDK constructs from cdk-code-generator and
organizes them into a complete, deployable CDK application with proper
stack boundaries and dependency management.

Usage:
    python organize.py --input-dir PATH --output-dir PATH --strategy STRATEGY
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

# Import strategy modules
from strategies.by_layer import ByLayerStrategy
from strategies.by_service import ByServiceStrategy
from strategies.by_tags import ByTagsStrategy

# Import utility modules
from utils.stack_generator import StackGenerator
from utils.app_generator import AppGenerator


class ConstructInventory:
    """Represents the inventory of constructs from cdk-code-generator"""

    def __init__(self, input_dir: Path):
        self.input_dir = input_dir
        self.metadata = self._load_metadata()
        self.dependencies = self._load_dependencies()
        self.constructs = self._discover_constructs()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata.json from input directory"""
        metadata_path = self.input_dir / "metadata.json"
        if not metadata_path.exists():
            print(f"Error: metadata.json not found in {self.input_dir}")
            sys.exit(1)

        with open(metadata_path, "r") as f:
            return json.load(f)

    def _load_dependencies(self) -> Dict[str, Any]:
        """Load dependencies.json from input directory (optional)"""
        deps_path = self.input_dir / "dependencies.json"
        if not deps_path.exists():
            return {}

        with open(deps_path, "r") as f:
            return json.load(f)

    def _discover_constructs(self) -> Dict[str, List[Path]]:
        """Discover all construct TypeScript files organized by resource type"""
        constructs_dir = self.input_dir / "constructs"
        if not constructs_dir.exists():
            print(f"Error: constructs/ directory not found in {self.input_dir}")
            sys.exit(1)

        constructs = {}
        resource_types = ["lambdas", "dynamodb", "iam", "s3", "eventbridge"]

        for resource_type in resource_types:
            type_dir = constructs_dir / resource_type
            if type_dir.exists():
                # Get all .ts files except index.ts
                ts_files = [
                    f for f in type_dir.glob("*.ts") if f.name != "index.ts"
                ]
                if ts_files:
                    constructs[resource_type] = ts_files

        if not constructs:
            print(f"Error: No construct files found in {constructs_dir}")
            sys.exit(1)

        return constructs

    def get_construct_count(self) -> int:
        """Get total number of constructs"""
        return sum(len(files) for files in self.constructs.values())


class StackOrganizer:
    """Main orchestrator for stack organization"""

    def __init__(self, args):
        self.args = args
        self.input_dir = Path(args.input_dir)
        self.output_dir = Path(args.output_dir)
        self.strategy_name = args.strategy
        self.cdk_version = args.cdk_version
        self.stack_prefix = args.stack_prefix
        self.cross_stack_refs = args.cross_stack_refs

        # Load construct inventory
        self.inventory = ConstructInventory(self.input_dir)

        # Select organization strategy
        self.strategy = self._select_strategy()

        # Initialize generators
        self.stack_generator = StackGenerator(self.cdk_version, self.stack_prefix)
        self.app_generator = AppGenerator(self.cdk_version, self.stack_prefix)

    def _select_strategy(self):
        """Select the appropriate organization strategy"""
        strategies = {
            "layer": ByLayerStrategy,
            "service": ByServiceStrategy,
            "tags": ByTagsStrategy,
        }

        if self.strategy_name not in strategies:
            print(f"Error: Unknown strategy '{self.strategy_name}'")
            print(f"Available strategies: {', '.join(strategies.keys())}")
            sys.exit(1)

        return strategies[self.strategy_name](
            self.inventory, self.cross_stack_refs
        )

    def organize(self):
        """Main organization workflow"""
        print(f"🎯 CDK Stack Organizer v1.0")
        print(f"📂 Input: {self.input_dir}")
        print(f"📁 Output: {self.output_dir}")
        print(f"📋 Strategy: {self.strategy_name}")
        print(f"📦 Constructs found: {self.inventory.get_construct_count()}")
        print()

        # Step 1: Analyze and organize constructs into stacks
        print("🔍 Step 1: Analyzing constructs and organizing into stacks...")
        stack_plan = self.strategy.organize()
        print(f"✅ Created {len(stack_plan.stacks)} stack(s)")
        for stack_name in stack_plan.stacks.keys():
            construct_count = len(stack_plan.stacks[stack_name])
            print(f"   - {stack_name}: {construct_count} construct(s)")
        print()

        # Step 2: Create output directory structure
        print("📁 Step 2: Creating CDK project structure...")
        self._create_directory_structure()
        print("✅ Directory structure created")
        print()

        # Step 3: Generate stack files
        print("📝 Step 3: Generating stack files...")
        self._generate_stack_files(stack_plan)
        print(f"✅ Generated {len(stack_plan.stacks)} stack file(s)")
        print()

        # Step 4: Generate app entry point
        print("🚀 Step 4: Generating app entry point (bin/app.ts)...")
        self._generate_app_file(stack_plan)
        print("✅ App entry point generated")
        print()

        # Step 5: Generate CDK configuration files
        print("⚙️  Step 5: Generating CDK configuration files...")
        self._generate_config_files()
        print("✅ Configuration files generated")
        print()

        # Step 6: Generate documentation
        print("📚 Step 6: Generating documentation...")
        self._generate_documentation(stack_plan)
        print("✅ Documentation generated")
        print()

        # Step 7: Save organization metadata
        print("💾 Step 7: Saving organization metadata...")
        self._save_metadata(stack_plan)
        print("✅ Metadata saved")
        print()

        print("🎉 Stack organization complete!")
        print()
        print("📋 Next steps:")
        print(f"   1. cd {self.output_dir}")
        print("   2. npm install  (or: pnpm install)")
        print("   3. npm run build  (or: pnpm run build)")
        print("   4. cdk synth")
        print("   5. cdk diff")
        print("   6. cdk deploy --all")
        print()

    def _create_directory_structure(self):
        """Create the CDK project directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "bin").mkdir(exist_ok=True)
        (self.output_dir / "lib").mkdir(exist_ok=True)

    def _generate_stack_files(self, stack_plan):
        """Generate stack TypeScript files"""
        for stack_name, constructs in stack_plan.stacks.items():
            stack_file = self.stack_generator.generate_stack(
                stack_name, constructs, stack_plan
            )
            output_path = self.output_dir / "lib" / f"{stack_name.lower()}.ts"
            output_path.write_text(stack_file)

    def _generate_app_file(self, stack_plan):
        """Generate the app entry point (bin/app.ts)"""
        app_file = self.app_generator.generate_app(stack_plan)
        output_path = self.output_dir / "bin" / "app.ts"
        output_path.write_text(app_file)

    def _generate_config_files(self):
        """Generate CDK configuration files"""
        # Copy configuration templates
        assets_dir = Path(__file__).parent.parent / "assets" / "cdk-project-template"

        # cdk.json
        cdk_json = self._load_template(assets_dir / "cdk.json")
        (self.output_dir / "cdk.json").write_text(cdk_json)

        # tsconfig.json
        tsconfig = self._load_template(assets_dir / "tsconfig.json")
        (self.output_dir / "tsconfig.json").write_text(tsconfig)

        # package.json
        package_json = self._load_template(assets_dir / "package.json")
        # Update CDK version in package.json
        package_data = json.loads(package_json)
        package_data["dependencies"]["aws-cdk-lib"] = f"^{self.cdk_version}"
        (self.output_dir / "package.json").write_text(
            json.dumps(package_data, indent=2)
        )

        # .gitignore
        gitignore = self._load_template(assets_dir / ".gitignore")
        (self.output_dir / ".gitignore").write_text(gitignore)

    def _load_template(self, template_path: Path) -> str:
        """Load a template file"""
        if template_path.exists():
            return template_path.read_text()
        return ""

    def _generate_documentation(self, stack_plan):
        """Generate README and documentation"""
        readme_content = self._generate_readme(stack_plan)
        (self.output_dir / "README.md").write_text(readme_content)

    def _generate_readme(self, stack_plan) -> str:
        """Generate README content"""
        readme = f"""# CDK Project - Organized Infrastructure

This CDK project was automatically generated by **cdk-stack-organizer**.

## Project Information

- **Organization Strategy**: {self.strategy_name}
- **CDK Version**: {self.cdk_version}
- **Generated**: {datetime.now(timezone.utc).isoformat()}
- **Total Constructs**: {self.inventory.get_construct_count()}
- **Number of Stacks**: {len(stack_plan.stacks)}

## Stacks

"""
        for stack_name, constructs in stack_plan.stacks.items():
            readme += f"### {stack_name}\n\n"
            readme += f"Contains {len(constructs)} construct(s):\n"
            for construct in constructs:
                readme += f"- {construct['name']} ({construct['type']})\n"
            readme += "\n"

        readme += """## Setup

1. **Install dependencies**:
   ```bash
   # Using npm
   npm install

   # Or using pnpm
   pnpm install
   ```

2. **Build the project**:
   ```bash
   # Using npm
   npm run build

   # Or using pnpm
   pnpm run build
   ```

3. **Synthesize CloudFormation**:
   ```bash
   cdk synth
   ```

4. **Preview changes**:
   ```bash
   cdk diff
   ```

5. **Deploy stacks**:
   ```bash
   # Deploy all stacks
   cdk deploy --all

   # Or deploy specific stack
   cdk deploy STACK_NAME
   ```

## Stack Dependencies

"""
        if stack_plan.dependencies:
            for stack_name, deps in stack_plan.dependencies.items():
                if deps:
                    readme += f"- **{stack_name}** depends on: {', '.join(deps)}\n"
        else:
            readme += "No cross-stack dependencies detected.\n"

        readme += """
## Project Structure

```
.
├── bin/
│   └── app.ts              # CDK app entry point
├── lib/
│   └── *.ts                # Stack definitions
├── cdk.json                # CDK configuration
├── tsconfig.json           # TypeScript configuration
├── package.json            # Node.js dependencies
└── README.md               # This file
```

## Next Steps

1. Review the generated stack organization
2. Update any TODO comments in the code
3. Test the stacks: `npm run build && cdk synth`
4. Deploy to your AWS account: `cdk deploy --all`

## Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CDK TypeScript Reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-construct-library.html)

---

**Generated by**: cdk-stack-organizer v1.0
**Part of**: AWS Infrastructure Skills Suite
"""
        return readme

    def _save_metadata(self, stack_plan):
        """Save organization metadata"""
        metadata = {
            "organized_at": datetime.now(timezone.utc).isoformat(),
            "organizer_version": "1.0.0-mvp",
            "strategy": self.strategy_name,
            "cdk_version": self.cdk_version,
            "stack_prefix": self.stack_prefix,
            "cross_stack_refs": self.cross_stack_refs,
            "source_input_dir": str(self.input_dir),
            "source_metadata": self.inventory.metadata,
            "stacks": {
                stack_name: {
                    "construct_count": len(constructs),
                    "constructs": [c["name"] for c in constructs],
                }
                for stack_name, constructs in stack_plan.stacks.items()
            },
            "dependencies": stack_plan.dependencies,
        }

        output_path = self.output_dir / "organization-metadata.json"
        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Organize CDK constructs into logical stacks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize by layer (default)
  python organize.py --input-dir ../cdk-generated --output-dir ./my-app

  # Organize by service
  python organize.py --input-dir ../cdk-generated --output-dir ./my-app --strategy service

  # With stack prefix
  python organize.py --input-dir ../cdk-generated --output-dir ./my-app --stack-prefix MyApp
        """,
    )

    # Required arguments
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing generated CDK constructs (from cdk-code-generator)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for organized CDK project",
    )

    # Optional arguments
    parser.add_argument(
        "--strategy",
        choices=["layer", "service", "tags"],
        default="layer",
        help="Organization strategy (default: layer)",
    )
    parser.add_argument(
        "--cdk-version",
        default="2.0.0",
        help="Target CDK version (default: 2.0.0)",
    )
    parser.add_argument(
        "--stack-prefix",
        default="",
        help="Prefix for stack names (default: none)",
    )
    parser.add_argument(
        "--cross-stack-refs",
        action="store_true",
        default=True,
        help="Enable cross-stack references (default: true)",
    )

    args = parser.parse_args()

    # Validate input directory
    if not Path(args.input_dir).exists():
        print(f"Error: Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    # Run organizer
    try:
        organizer = StackOrganizer(args)
        organizer.organize()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
