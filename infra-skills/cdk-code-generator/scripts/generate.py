#!/usr/bin/env python3
"""
CDK Code Generator - Main Script
Generates TypeScript CDK code from AWS resource discovery JSON files.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add generators to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generators'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# Import generators
from lambda_generator import LambdaGenerator
from dynamodb_generator import DynamoDBGenerator
from iam_generator import IAMGenerator
from s3_generator import S3Generator
from eventbridge_generator import EventBridgeGenerator


class CDKCodeGenerator:
    """Main CDK code generator orchestrator."""

    def __init__(self, input_dir: str, output_dir: str, config: Dict[str, Any]):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.config = config
        self.metadata = {}
        self.resources = {}
        self.dependencies = {}

        # Initialize generators
        self.lambda_gen = LambdaGenerator(config)
        self.dynamodb_gen = DynamoDBGenerator(config)
        self.iam_gen = IAMGenerator(config)
        self.s3_gen = S3Generator(config)
        self.eventbridge_gen = EventBridgeGenerator(config)

    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("CDK Code Generator")
        print("=" * 60)

        # Validate input directory
        if not self.input_dir.exists():
            print(f"❌ Error: Input directory not found: {self.input_dir}")
            sys.exit(1)

        print(f"📂 Input directory: {self.input_dir}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🔧 Generation mode: {self.config['default_mode']}")
        print()

        # Load input files
        self._load_input_files()

        # Create output directory structure
        self._create_output_structure()

        # Generate supporting files first
        self._generate_package_json()
        self._generate_tsconfig()
        self._generate_readme()
        self._write_dependencies_json()
        self._write_metadata()

        # Generate constructs
        self._generate_constructs()

        # Print summary
        self._print_summary()

        print("=" * 60)
        print(f"✅ Code generation complete!")
        print(f"📁 Output location: {self.output_dir.absolute()}")
        print()
        print("Next steps:")
        print("  1. cd", self.output_dir.absolute())
        print("  2. npm install")
        print("  3. npm run build")
        print("  4. Review generated constructs in constructs/")
        print("=" * 60)

    def _load_input_files(self):
        """Load JSON files from input directory."""
        print("📖 Loading input files...")

        # Load metadata
        metadata_file = self.input_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            print(f"  ✓ Loaded metadata.json")

        # Load resource files
        resource_files = {
            'lambdas': 'lambdas.json',
            'dynamodb': 'dynamodb-tables.json',
            'iam_roles': 'iam-roles.json',
            'iam_policies': 'iam-policies.json',
            's3': 's3-buckets.json',
            'eventbridge': 'eventbridge-rules.json',
        }

        for resource_type, filename in resource_files.items():
            file_path = self.input_dir / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.resources[resource_type] = json.load(f)
                print(f"  ✓ Loaded {filename} ({len(self.resources[resource_type])} resources)")
            else:
                self.resources[resource_type] = []

        # Load dependencies
        dep_file = self.input_dir / 'dependencies.json'
        if dep_file.exists():
            with open(dep_file, 'r') as f:
                self.dependencies = json.load(f)
            print(f"  ✓ Loaded dependencies.json")

        print()

    def _create_output_structure(self):
        """Create output directory structure."""
        print("📁 Creating output directory structure...")

        # Create main directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'constructs').mkdir(exist_ok=True)

        # Create resource type directories
        for resource_type in ['lambdas', 'dynamodb', 'iam', 's3', 'eventbridge']:
            (self.output_dir / 'constructs' / resource_type).mkdir(exist_ok=True)

        print(f"  ✓ Created {self.output_dir}")
        print()

    def _generate_package_json(self):
        """Generate package.json with CDK dependencies."""
        cdk_version = self.config.get('cdk_version', '2.0.0')

        package_json = {
            "name": "cdk-generated",
            "version": "1.0.0",
            "description": "Generated CDK constructs from aws-resource-discovery",
            "main": "lib/index.js",
            "types": "lib/index.d.ts",
            "scripts": {
                "build": "tsc",
                "watch": "tsc -w",
                "test": "jest"
            },
            "dependencies": {
                "aws-cdk-lib": f"^{cdk_version}",
                "constructs": "^10.0.0"
            },
            "devDependencies": {
                "@types/node": "^18.0.0",
                "typescript": "^5.0.0",
                "ts-node": "^10.0.0"
            }
        }

        with open(self.output_dir / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

        print("  ✓ Generated package.json")

    def _generate_tsconfig(self):
        """Generate tsconfig.json."""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["es2020"],
                "declaration": True,
                "strict": True,
                "noImplicitAny": True,
                "strictNullChecks": True,
                "noImplicitThis": True,
                "alwaysStrict": True,
                "noUnusedLocals": False,
                "noUnusedParameters": False,
                "noImplicitReturns": True,
                "noFallthroughCasesInSwitch": False,
                "inlineSourceMap": True,
                "inlineSources": True,
                "experimentalDecorators": True,
                "strictPropertyInitialization": False,
                "typeRoots": ["./node_modules/@types"],
                "outDir": "lib",
                "rootDir": "constructs"
            },
            "include": ["constructs/**/*.ts"],
            "exclude": ["node_modules"]
        }

        with open(self.output_dir / 'tsconfig.json', 'w') as f:
            json.dump(tsconfig, f, indent=2)

        print("  ✓ Generated tsconfig.json")

    def _generate_readme(self):
        """Generate README.md for generated code."""
        readme_content = f"""# Generated CDK Constructs

This directory contains TypeScript CDK constructs generated from AWS resource discovery.

## Source Information

- **Account ID**: {self.metadata.get('account_id', 'N/A')}
- **Region**: {self.metadata.get('region', 'N/A')}
- **Profile**: {self.metadata.get('profile', 'N/A')}
- **Discovery Timestamp**: {self.metadata.get('scan_timestamp', 'N/A')}
- **Generation Timestamp**: {datetime.utcnow().isoformat()}Z

## Installation

```bash
npm install
```

## Build

```bash
npm run build
```

## Usage

Import the generated constructs in your CDK stack:

```typescript
import {{ MyFunctionRef }} from './constructs/lambdas/my-function';
import {{ MyTableRef }} from './constructs/dynamodb/my-table';

// Use in your stack
const myFunction = new MyFunctionRef(this, 'MyFunction');
const myTable = new MyTableRef(this, 'MyTable');
```

## Next Steps

1. Review the generated constructs in `constructs/`
2. Update any TODO comments with actual values
3. For full management mode: Update code asset paths
4. Test compilation: `npm run build`
5. Organize into CDK stacks
6. Deploy with `cdk deploy` or import with `cdk import`

## Generation Configuration

- **Default Mode**: {self.config['default_mode']}
- **Lambda Mode**: {self.config.get('lambda_mode', 'default')}
- **DynamoDB Mode**: {self.config.get('dynamodb_mode', 'default')}
- **IAM Mode**: {self.config.get('iam_mode', 'default')}
- **S3 Mode**: {self.config.get('s3_mode', 'default')}
- **EventBridge Mode**: {self.config.get('eventbridge_mode', 'default')}
- **CDK Version**: {self.config.get('cdk_version', '2.0.0')}

---

Generated by `cdk-code-generator` v1.0
"""

        with open(self.output_dir / 'README.md', 'w') as f:
            f.write(readme_content)

        print("  ✓ Generated README.md")

    def _write_dependencies_json(self):
        """Write dependencies.json to output."""
        with open(self.output_dir / 'dependencies.json', 'w') as f:
            json.dump(self.dependencies, f, indent=2)

        print("  ✓ Wrote dependencies.json")

    def _write_metadata(self):
        """Write generation metadata."""
        metadata = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'generator_version': '1.0.0-mvp',
            'source_metadata': self.metadata,
            'generation_config': self.config,
            'resource_counts': {
                'lambdas': len(self.resources.get('lambdas', [])),
                'dynamodb': len(self.resources.get('dynamodb', [])),
                'iam_roles': len(self.resources.get('iam_roles', [])),
                'iam_policies': len(self.resources.get('iam_policies', [])),
                's3': len(self.resources.get('s3', [])),
                'eventbridge': len(self.resources.get('eventbridge', [])),
            }
        }

        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        print("  ✓ Wrote metadata.json")

    def _generate_constructs(self):
        """Generate TypeScript CDK constructs for all resources."""
        print()
        print("🏗️  Generating CDK constructs...")
        print()

        generated_count = 0

        # Generate Lambda functions
        if self.resources.get('lambdas'):
            mode = self.config.get('lambda_mode', self.config['default_mode'])
            print(f"  • Generating {len(self.resources['lambdas'])} Lambda functions (mode: {mode})...")
            for lambda_func in self.resources['lambdas']:
                code = self.lambda_gen.generate(lambda_func, mode)
                filename = self._sanitize_filename(lambda_func['function_name']) + '.ts'
                filepath = self.output_dir / 'constructs' / 'lambdas' / filename
                with open(filepath, 'w') as f:
                    f.write(code)
                generated_count += 1
            print(f"    ✓ Generated {len(self.resources['lambdas'])} Lambda constructs")

        # Generate DynamoDB tables
        if self.resources.get('dynamodb'):
            mode = self.config.get('dynamodb_mode', self.config['default_mode'])
            print(f"  • Generating {len(self.resources['dynamodb'])} DynamoDB tables (mode: {mode})...")
            for table in self.resources['dynamodb']:
                code = self.dynamodb_gen.generate(table, mode)
                filename = self._sanitize_filename(table['table_name']) + '.ts'
                filepath = self.output_dir / 'constructs' / 'dynamodb' / filename
                with open(filepath, 'w') as f:
                    f.write(code)
                generated_count += 1
            print(f"    ✓ Generated {len(self.resources['dynamodb'])} DynamoDB constructs")

        # Generate IAM roles
        if self.resources.get('iam_roles'):
            mode = self.config.get('iam_mode', self.config['default_mode'])
            print(f"  • Generating {len(self.resources['iam_roles'])} IAM roles (mode: {mode})...")
            for role in self.resources['iam_roles']:
                code = self.iam_gen.generate(role, mode)
                filename = self._sanitize_filename(role['role_name']) + '.ts'
                filepath = self.output_dir / 'constructs' / 'iam' / filename
                with open(filepath, 'w') as f:
                    f.write(code)
                generated_count += 1
            print(f"    ✓ Generated {len(self.resources['iam_roles'])} IAM role constructs")

        # Generate S3 buckets
        if self.resources.get('s3'):
            mode = self.config.get('s3_mode', self.config['default_mode'])
            print(f"  • Generating {len(self.resources['s3'])} S3 buckets (mode: {mode})...")
            for bucket in self.resources['s3']:
                code = self.s3_gen.generate(bucket, mode)
                filename = self._sanitize_filename(bucket['bucket_name']) + '.ts'
                filepath = self.output_dir / 'constructs' / 's3' / filename
                with open(filepath, 'w') as f:
                    f.write(code)
                generated_count += 1
            print(f"    ✓ Generated {len(self.resources['s3'])} S3 bucket constructs")

        # Generate EventBridge rules
        if self.resources.get('eventbridge'):
            mode = self.config.get('eventbridge_mode', self.config['default_mode'])
            print(f"  • Generating {len(self.resources['eventbridge'])} EventBridge rules (mode: {mode})...")
            for rule in self.resources['eventbridge']:
                code = self.eventbridge_gen.generate(rule, mode)
                filename = self._sanitize_filename(rule['rule_name']) + '.ts'
                filepath = self.output_dir / 'constructs' / 'eventbridge' / filename
                with open(filepath, 'w') as f:
                    f.write(code)
                generated_count += 1
            print(f"    ✓ Generated {len(self.resources['eventbridge'])} EventBridge rule constructs")

        print()
        print(f"  ✅ Total constructs generated: {generated_count}")
        print()

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Convert resource name to valid filename."""
        # Replace invalid characters with hyphens
        sanitized = name.lower()
        sanitized = sanitized.replace('_', '-')
        sanitized = sanitized.replace(' ', '-')
        # Remove any other special characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '-')
        return sanitized

    def _print_summary(self):
        """Print generation summary."""
        print()
        print("=" * 60)
        print("Generation Summary")
        print("=" * 60)
        print()

        total_resources = sum([
            len(self.resources.get('lambdas', [])),
            len(self.resources.get('dynamodb', [])),
            len(self.resources.get('iam_roles', [])),
            len(self.resources.get('s3', [])),
            len(self.resources.get('eventbridge', [])),
        ])

        print(f"Total resources discovered: {total_resources}")
        print()
        print("Resources by type:")
        if self.resources.get('lambdas'):
            print(f"  • Lambda functions: {len(self.resources['lambdas'])}")
        if self.resources.get('dynamodb'):
            print(f"  • DynamoDB tables: {len(self.resources['dynamodb'])}")
        if self.resources.get('iam_roles'):
            print(f"  • IAM roles: {len(self.resources['iam_roles'])}")
        if self.resources.get('s3'):
            print(f"  • S3 buckets: {len(self.resources['s3'])}")
        if self.resources.get('eventbridge'):
            print(f"  • EventBridge rules: {len(self.resources['eventbridge'])}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Generate TypeScript CDK code from AWS resource discovery JSON files.'
    )

    # Required arguments
    parser.add_argument(
        '--input-dir',
        required=True,
        help='Path to resource inventory directory (from aws-resource-discovery)'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Output directory for generated CDK code'
    )

    # Mode options
    parser.add_argument(
        '--mode',
        choices=['reference', 'full'],
        default='reference',
        help='Default generation mode (default: reference)'
    )
    parser.add_argument(
        '--lambda-mode',
        choices=['reference', 'full'],
        help='Override mode for Lambda functions'
    )
    parser.add_argument(
        '--dynamodb-mode',
        choices=['reference', 'full'],
        help='Override mode for DynamoDB tables'
    )
    parser.add_argument(
        '--iam-mode',
        choices=['reference', 'full'],
        help='Override mode for IAM roles/policies'
    )
    parser.add_argument(
        '--s3-mode',
        choices=['reference', 'full'],
        help='Override mode for S3 buckets'
    )
    parser.add_argument(
        '--eventbridge-mode',
        choices=['reference', 'full'],
        help='Override mode for EventBridge rules'
    )

    # Other options
    parser.add_argument(
        '--cdk-version',
        default='2.0.0',
        help='Target CDK version (default: 2.0.0)'
    )

    args = parser.parse_args()

    # Build configuration
    config = {
        'default_mode': args.mode,
        'cdk_version': args.cdk_version,
        'include_comments': True,
        'format_code': True,
    }

    # Add mode overrides
    if args.lambda_mode:
        config['lambda_mode'] = args.lambda_mode
    if args.dynamodb_mode:
        config['dynamodb_mode'] = args.dynamodb_mode
    if args.iam_mode:
        config['iam_mode'] = args.iam_mode
    if args.s3_mode:
        config['s3_mode'] = args.s3_mode
    if args.eventbridge_mode:
        config['eventbridge_mode'] = args.eventbridge_mode

    # Run generator
    generator = CDKCodeGenerator(args.input_dir, args.output_dir, config)
    generator.run()


if __name__ == '__main__':
    main()
