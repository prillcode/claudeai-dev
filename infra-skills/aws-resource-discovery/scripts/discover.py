#!/usr/bin/env python3
"""
AWS Resource Discovery Script

Discovers AWS resources and generates comprehensive inventory with dependencies.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.aws_client import AWSClientManager
from utils.filters import ResourceFilter, parse_tags
from utils.output_formatter import OutputFormatter

from resource_scanners.lambda_scanner import LambdaScanner
from resource_scanners.dynamodb_scanner import DynamoDBScanner
from resource_scanners.iam_scanner import IAMScanner
from resource_scanners.s3_scanner import S3Scanner
from resource_scanners.eventbridge_scanner import EventBridgeScanner

from dependency_detector import DependencyDetector


def main():
    """Main entry point for resource discovery."""
    parser = argparse.ArgumentParser(
        description='Discover AWS resources and generate inventory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Full discovery
  python discover.py --profile prod --region us-east-1

  # With output prefix (creates "cs-inventory" folder)
  python discover.py --profile prod --region us-east-1 --output-prefix cs

  # Filter by tags
  python discover.py --profile prod --region us-east-1 --tags project=myapp environment=prod

  # Filter by resource types with prefix
  python discover.py --profile prod --region us-east-1 --resource-types lambda dynamodb --output-prefix myapp

  # Filter by name pattern
  python discover.py --profile prod --region us-east-1 --name-pattern "order-*" --output-prefix order-service

  # Specific function with dependencies
  python discover.py --profile prod --region us-east-1 --function-name order-processor --traverse-dependencies
        '''
    )

    # Required arguments
    parser.add_argument(
        '--profile',
        required=True,
        help='AWS CLI profile name'
    )
    parser.add_argument(
        '--region',
        required=True,
        help='AWS region (e.g., us-east-1)'
    )

    # Output options
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory for inventory files (default: ./resource-inventory or <prefix>-inventory if prefix specified)'
    )
    parser.add_argument(
        '--output-prefix',
        help='Prefix for output directory name (e.g., "cs" creates "cs-inventory" folder)'
    )

    # Filter options
    parser.add_argument(
        '--tags',
        nargs='+',
        metavar='KEY=VALUE',
        help='Filter by tags (format: key=value)'
    )
    parser.add_argument(
        '--name-pattern',
        help='Filter by name pattern (Unix glob style, e.g., "order-*")'
    )
    parser.add_argument(
        '--resource-types',
        nargs='+',
        choices=['lambda', 'dynamodb', 'iam', 's3', 'eventbridge'],
        help='Resource types to scan (default: all)'
    )

    # Specific resource lookup
    parser.add_argument(
        '--function-name',
        help='Scan a specific Lambda function by name'
    )
    parser.add_argument(
        '--table-name',
        help='Scan a specific DynamoDB table by name'
    )
    parser.add_argument(
        '--traverse-dependencies',
        action='store_true',
        help='When used with specific resource flags, also discover all dependencies'
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    elif args.output_prefix:
        output_dir = f"./{args.output_prefix}-inventory"
    else:
        output_dir = "./resource-inventory"

    # Check if output directory exists and prompt for confirmation
    if Path(output_dir).exists():
        print("\n⚠️  Warning: Output directory already exists!")
        print(f"   Location: {Path(output_dir).absolute()}")
        print(f"\n   This directory contains existing discovery data.")
        print(f"   Continuing will overwrite these files.")

        response = input("\n   Do you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Discovery cancelled by user.")
            return 1

    # Print header
    print("\n" + "=" * 60)
    print("AWS Resource Discovery")
    print("=" * 60)

    # Initialize AWS client manager
    client_manager = AWSClientManager(args.profile, args.region)

    # Parse and create filter
    tag_filter = parse_tags(args.tags) if args.tags else {}
    resource_filter = ResourceFilter(
        tags=tag_filter,
        name_pattern=args.name_pattern,
        resource_types=args.resource_types
    )

    # Show preview of output location
    if args.output_prefix:
        print(f"\n💡 Using prefix '{args.output_prefix}' for output directory")
    print(f"📁 Output will be saved to: {Path(output_dir).absolute()}")

    # Initialize output formatter
    output_formatter = OutputFormatter(output_dir)

    # Display filter information
    if resource_filter.has_filters():
        print("\n📋 Active Filters:")
        filter_summary = resource_filter.get_filter_summary()
        if 'tags' in filter_summary:
            print(f"  • Tags: {filter_summary['tags']}")
        if 'name_pattern' in filter_summary:
            print(f"  • Name pattern: {filter_summary['name_pattern']}")
        if 'resource_types' in filter_summary:
            print(f"  • Resource types: {', '.join(filter_summary['resource_types'])}")
    else:
        print("\n📋 Scanning all resource types with no filters")

    # Determine scan mode
    if args.function_name or args.table_name:
        # Specific resource mode
        resources = scan_specific_resources(
            client_manager,
            resource_filter,
            args.function_name,
            args.table_name,
            args.traverse_dependencies
        )
    else:
        # Full scan mode
        resources = scan_all_resources(client_manager, resource_filter)

    # Detect dependencies
    dependency_detector = DependencyDetector()
    dependencies = dependency_detector.detect_dependencies(
        lambdas=resources['lambdas'],
        dynamodb_tables=resources['dynamodb_tables'],
        iam_roles=resources['iam_roles'],
        iam_policies=resources['iam_policies'],
        s3_buckets=resources['s3_buckets'],
        eventbridge_rules=resources['eventbridge_rules']
    )

    # Write output files
    print("\n📝 Writing output files...")

    resource_counts = {}

    if resources['lambdas']:
        output_formatter.write_resources('lambdas', resources['lambdas'])
        resource_counts['lambdas'] = len(resources['lambdas'])

    if resources['dynamodb_tables']:
        output_formatter.write_resources('dynamodb-tables', resources['dynamodb_tables'])
        resource_counts['dynamodb_tables'] = len(resources['dynamodb_tables'])

    if resources['iam_roles']:
        output_formatter.write_resources('iam-roles', resources['iam_roles'])
        resource_counts['iam_roles'] = len(resources['iam_roles'])

    if resources['iam_policies']:
        output_formatter.write_resources('iam-policies', resources['iam_policies'])
        resource_counts['iam_policies'] = len(resources['iam_policies'])

    if resources['s3_buckets']:
        output_formatter.write_resources('s3-buckets', resources['s3_buckets'])
        resource_counts['s3_buckets'] = len(resources['s3_buckets'])

    if resources['eventbridge_rules']:
        output_formatter.write_resources('eventbridge-rules', resources['eventbridge_rules'])
        resource_counts['eventbridge_rules'] = len(resources['eventbridge_rules'])

    # Write dependencies
    if dependencies:
        output_formatter.write_dependencies(dependencies)

    # Write metadata
    output_formatter.write_metadata(
        account_id=client_manager.get_account_id(),
        region=args.region,
        profile=args.profile,
        filters=resource_filter.get_filter_summary(),
        resource_counts=resource_counts
    )

    # Print summary
    summary = output_formatter.generate_summary_report(resource_counts)
    print(summary)

    return 0


def scan_all_resources(client_manager, resource_filter):
    """Scan all resource types."""
    resources = {
        'lambdas': [],
        'dynamodb_tables': [],
        'iam_roles': [],
        'iam_policies': [],
        's3_buckets': [],
        'eventbridge_rules': []
    }

    # Scan Lambda functions
    if resource_filter.should_include_resource_type('lambda'):
        scanner = LambdaScanner(client_manager, resource_filter)
        resources['lambdas'] = scanner.scan()

    # Scan DynamoDB tables
    if resource_filter.should_include_resource_type('dynamodb'):
        scanner = DynamoDBScanner(client_manager, resource_filter)
        resources['dynamodb_tables'] = scanner.scan()

    # Scan IAM roles and policies
    if resource_filter.should_include_resource_type('iam'):
        scanner = IAMScanner(client_manager, resource_filter)
        roles, policies = scanner.scan()
        resources['iam_roles'] = roles
        resources['iam_policies'] = policies

    # Scan S3 buckets
    if resource_filter.should_include_resource_type('s3'):
        scanner = S3Scanner(client_manager, resource_filter)
        resources['s3_buckets'] = scanner.scan()

    # Scan EventBridge rules
    if resource_filter.should_include_resource_type('eventbridge'):
        scanner = EventBridgeScanner(client_manager, resource_filter)
        resources['eventbridge_rules'] = scanner.scan()

    return resources


def scan_specific_resources(
    client_manager,
    resource_filter,
    function_name,
    table_name,
    traverse_dependencies
):
    """Scan specific resources by name."""
    print(f"\n🎯 Specific resource mode")

    resources = {
        'lambdas': [],
        'dynamodb_tables': [],
        'iam_roles': [],
        'iam_policies': [],
        's3_buckets': [],
        'eventbridge_rules': []
    }

    # Get specific Lambda function
    if function_name:
        print(f"  • Looking up Lambda function: {function_name}")
        scanner = LambdaScanner(client_manager, resource_filter)
        function = scanner.get_function_by_name(function_name)
        if function:
            resources['lambdas'].append(function)
            print(f"    ✓ Found function: {function_name}")

            if traverse_dependencies:
                print(f"    🔗 Traversing dependencies...")
                # Get IAM role if present
                if function.get('iam_role_arn'):
                    role_name = function['iam_role_arn'].split('/')[-1]
                    iam_scanner = IAMScanner(client_manager, resource_filter)
                    role = iam_scanner.get_role_by_name(role_name)
                    if role:
                        resources['iam_roles'].append(role)
                        print(f"      ✓ Found IAM role: {role_name}")
        else:
            print(f"    ❌ Function not found: {function_name}")
            sys.exit(1)

    # Get specific DynamoDB table
    if table_name:
        print(f"  • Looking up DynamoDB table: {table_name}")
        scanner = DynamoDBScanner(client_manager, resource_filter)
        table = scanner.get_table_by_name(table_name)
        if table:
            resources['dynamodb_tables'].append(table)
            print(f"    ✓ Found table: {table_name}")
        else:
            print(f"    ❌ Table not found: {table_name}")
            sys.exit(1)

    return resources


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Discovery interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
