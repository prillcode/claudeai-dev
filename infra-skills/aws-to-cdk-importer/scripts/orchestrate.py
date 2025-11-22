#!/usr/bin/env python3
"""
AWS to CDK Importer - Orchestrator
Main entry point for the end-to-end AWS resource import workflow.

This script coordinates all four component skills in sequence:
1. aws-resource-discovery
2. cdk-code-generator
3. cdk-stack-organizer
4. cdk-import-config-generator

Usage:
    python orchestrate.py --profile <profile> --region <region> --output <dir>

Example:
    python orchestrate.py \\
        --profile prod \\
        --region us-east-1 \\
        --resource-types lambda,dynamodb \\
        --strategy layer \\
        --output ./my-cdk-project
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add utils directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from workflow_engine import WorkflowEngine
from progress_tracker import ProgressTracker


# Exit codes for different failure scenarios
EXIT_SUCCESS = 0
EXIT_DISCOVERY_FAILURE = 1
EXIT_CODE_GEN_FAILURE = 2
EXIT_ORGANIZATION_FAILURE = 3
EXIT_IMPORT_CONFIG_FAILURE = 4
EXIT_REPORT_FAILURE = 5
EXIT_INVALID_ARGS = 100


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='AWS to CDK Importer - Orchestrate end-to-end import workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s --profile prod --region us-east-1 --output ./my-project

  # Import specific resource types with layer strategy
  %(prog)s --profile prod --region us-east-1 \\
    --resource-types lambda,dynamodb \\
    --strategy layer \\
    --output ./my-project

  # Import resources with specific tag, organized by service
  %(prog)s --profile dev --region us-west-2 \\
    --tag-filter "Environment=Production" \\
    --strategy service \\
    --output ./prod-infrastructure

  # Full management mode
  %(prog)s --profile staging --region eu-west-1 \\
    --resource-types lambda,dynamodb,s3,iam \\
    --mode full \\
    --strategy service \\
    --output ./staging-cdk

  # Dry run to preview workflow
  %(prog)s --profile prod --region us-east-1 \\
    --resource-types lambda \\
    --dry-run \\
    --verbose
        """
    )

    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--profile',
        required=True,
        help='AWS CLI profile name for authentication'
    )
    required.add_argument(
        '--region',
        required=True,
        help='AWS region to scan for resources (e.g., us-east-1)'
    )
    required.add_argument(
        '--output',
        required=True,
        help='Output directory path for all generated files'
    )

    # Optional filter arguments
    filters = parser.add_argument_group('resource filters')
    filters.add_argument(
        '--resource-types',
        help='Comma-separated list of AWS resource types (e.g., lambda,dynamodb,s3)'
    )
    filters.add_argument(
        '--tag-filter',
        help='Filter resources by tag in Key=Value format (e.g., "Environment=Production")'
    )
    filters.add_argument(
        '--name-pattern',
        help='Filter resources by name pattern (regex)'
    )

    # Optional configuration arguments
    config = parser.add_argument_group('configuration options')
    config.add_argument(
        '--mode',
        choices=['reference', 'full'],
        default='reference',
        help='Code generation mode: reference (default) or full management'
    )
    config.add_argument(
        '--strategy',
        choices=['layer', 'service', 'tag', 'custom'],
        default='layer',
        help='Stack organization strategy (default: layer)'
    )
    config.add_argument(
        '--tag-key',
        help='Tag key for grouping when using --strategy tag'
    )
    config.add_argument(
        '--custom-rules',
        help='Path to custom rules file when using --strategy custom'
    )

    # Optional behavior flags
    behavior = parser.add_argument_group('behavior options')
    behavior.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate the workflow without making changes'
    )
    behavior.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )
    behavior.add_argument(
        '--skip-phase',
        choices=['1', '2', '3', '4', '5'],
        help='Skip a specific phase (for testing/resume scenarios)'
    )

    args = parser.parse_args()

    # Validate argument combinations
    if args.strategy == 'tag' and not args.tag_key:
        parser.error('--tag-key is required when using --strategy tag')

    if args.strategy == 'custom' and not args.custom_rules:
        parser.error('--custom-rules is required when using --strategy custom')

    if args.custom_rules and not os.path.exists(args.custom_rules):
        parser.error(f'Custom rules file not found: {args.custom_rules}')

    return args


def validate_environment(args):
    """
    Validate that the environment is properly configured.

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Check if component skills exist
    script_dir = Path(__file__).parent.parent.parent

    required_skills = [
        'aws-resource-discovery',
        'cdk-code-generator',
        'cdk-stack-organizer',
        'cdk-import-config-generator'
    ]

    missing_skills = []
    for skill in required_skills:
        skill_path = script_dir / skill
        if not skill_path.exists():
            missing_skills.append(skill)

    if missing_skills:
        error_msg = (
            f"Missing required component skills: {', '.join(missing_skills)}\n"
            f"Expected location: {script_dir}\n"
            f"Please ensure all component skills are installed."
        )
        return False, error_msg

    # Check if AWS CLI is configured
    if not os.path.exists(os.path.expanduser('~/.aws/config')):
        return False, "AWS CLI not configured. Run 'aws configure' first."

    # Validate output directory
    output_path = Path(args.output)
    if output_path.exists() and not args.dry_run:
        # Check if directory is empty
        if list(output_path.iterdir()):
            return False, f"Output directory already exists and is not empty: {args.output}"

    return True, None


def print_configuration_summary(args):
    """Print a summary of the workflow configuration."""
    print("=" * 70)
    print("AWS to CDK Importer - Configuration Summary")
    print("=" * 70)
    print(f"AWS Profile:       {args.profile}")
    print(f"AWS Region:        {args.region}")
    print(f"Output Directory:  {args.output}")
    print(f"Generation Mode:   {args.mode}")
    print(f"Stack Strategy:    {args.strategy}")

    if args.resource_types:
        print(f"Resource Types:    {args.resource_types}")
    if args.tag_filter:
        print(f"Tag Filter:        {args.tag_filter}")
    if args.name_pattern:
        print(f"Name Pattern:      {args.name_pattern}")
    if args.tag_key:
        print(f"Tag Key:           {args.tag_key}")
    if args.custom_rules:
        print(f"Custom Rules:      {args.custom_rules}")

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")

    print("=" * 70)
    print()


def main():
    """Main orchestrator entry point."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Print configuration summary
        print_configuration_summary(args)

        # Validate environment
        valid, error_msg = validate_environment(args)
        if not valid:
            print(f"❌ Environment validation failed:", file=sys.stderr)
            print(f"   {error_msg}", file=sys.stderr)
            return EXIT_INVALID_ARGS

        # Create output directory
        output_path = Path(args.output)
        if not args.dry_run:
            output_path.mkdir(parents=True, exist_ok=True)

        # Initialize progress tracker
        progress = ProgressTracker(total_phases=5, verbose=args.verbose)

        # Initialize workflow engine
        engine = WorkflowEngine(
            args=args,
            progress_tracker=progress,
            dry_run=args.dry_run
        )

        # Start workflow
        start_time = datetime.now()
        print(f"🚀 Starting workflow at {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Execute workflow phases
        result = engine.execute_workflow()

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print final status
        print()
        if result['success']:
            print("=" * 70)
            print("✅ Workflow completed successfully!")
            print("=" * 70)
            print(f"Duration: {duration:.1f} seconds")
            print(f"Output location: {args.output}")
            print(f"\nNext steps:")
            print(f"1. Review the summary report: {args.output}/IMPORT_SUMMARY.md")
            print(f"2. Install dependencies: cd {args.output}/cdk-organized && npm install")
            print(f"3. Review generated code: cat {args.output}/cdk-organized/lib/stacks/*.ts")
            print(f"4. Run import scripts: cd {args.output}/import-configs/scripts && ./import-all.sh")
            print("=" * 70)
            return EXIT_SUCCESS
        else:
            print("=" * 70)
            print("❌ Workflow failed")
            print("=" * 70)
            print(f"Failed at: {result.get('failed_phase', 'Unknown')}")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Duration: {duration:.1f} seconds")

            # Check if error log exists
            error_log = output_path / 'error.log'
            if error_log.exists():
                print(f"\nDetailed error log: {error_log}")

            print("\nIntermediate outputs have been preserved for debugging.")
            print("=" * 70)

            # Return appropriate exit code based on failed phase
            phase_exit_codes = {
                'Phase 1: Resource Discovery': EXIT_DISCOVERY_FAILURE,
                'Phase 2: CDK Code Generation': EXIT_CODE_GEN_FAILURE,
                'Phase 3: Stack Organization': EXIT_ORGANIZATION_FAILURE,
                'Phase 4: Import Configuration': EXIT_IMPORT_CONFIG_FAILURE,
                'Phase 5: Summary Report': EXIT_REPORT_FAILURE,
            }
            return phase_exit_codes.get(result.get('failed_phase'), EXIT_INVALID_ARGS)

    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user", file=sys.stderr)
        return EXIT_INVALID_ARGS

    except Exception as e:
        print(f"\n❌ Unexpected error:", file=sys.stderr)
        print(f"   {str(e)}", file=sys.stderr)

        if args.verbose:
            import traceback
            print("\nStack trace:", file=sys.stderr)
            traceback.print_exc()

        return EXIT_INVALID_ARGS


if __name__ == '__main__':
    sys.exit(main())
