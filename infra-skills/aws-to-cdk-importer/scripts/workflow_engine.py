#!/usr/bin/env python3
"""
Workflow Engine for AWS to CDK Importer

Handles sequential execution of all 5 phases with error handling,
data validation, and progress tracking.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import utilities
from utils.skill_invoker import SkillInvoker
from utils.data_passer import DataPasser
from utils.progress_tracker import ProgressTracker


class WorkflowEngine:
    """
    Orchestrates the 5-phase workflow for AWS to CDK import.

    Phases:
    1. Resource Discovery
    2. CDK Code Generation
    3. Stack Organization
    4. Import Configuration Generation
    5. Summary Report Generation
    """

    def __init__(self, args, progress_tracker: ProgressTracker, dry_run: bool = False):
        """
        Initialize the workflow engine.

        Args:
            args: Parsed command-line arguments
            progress_tracker: Progress tracker instance
            dry_run: Whether to simulate without making changes
        """
        self.args = args
        self.progress = progress_tracker
        self.dry_run = dry_run

        # Initialize paths
        self.output_dir = Path(args.output)
        self.discovery_dir = self.output_dir / 'discovery'
        self.cdk_generated_dir = self.output_dir / 'cdk-generated'
        self.cdk_organized_dir = self.output_dir / 'cdk-organized'
        self.import_configs_dir = self.output_dir / 'import-configs'

        # Initialize skill invoker and data passer
        self.invoker = SkillInvoker(dry_run=dry_run, verbose=args.verbose)
        self.data_passer = DataPasser(verbose=args.verbose)

        # Track phase results
        self.phase_results = {}

    def execute_workflow(self) -> Dict[str, Any]:
        """
        Execute all 5 phases of the workflow in sequence.

        Returns:
            dict: Result summary with success status and any errors
        """
        try:
            # Phase 1: Resource Discovery
            if not self._should_skip_phase(1):
                result = self._execute_phase_1()
                if not result['success']:
                    return self._failure_result('Phase 1: Resource Discovery', result['error'])

            # Phase 2: CDK Code Generation
            if not self._should_skip_phase(2):
                result = self._execute_phase_2()
                if not result['success']:
                    return self._failure_result('Phase 2: CDK Code Generation', result['error'])

            # Phase 3: Stack Organization
            if not self._should_skip_phase(3):
                result = self._execute_phase_3()
                if not result['success']:
                    return self._failure_result('Phase 3: Stack Organization', result['error'])

            # Phase 4: Import Configuration Generation
            if not self._should_skip_phase(4):
                result = self._execute_phase_4()
                if not result['success']:
                    return self._failure_result('Phase 4: Import Configuration', result['error'])

            # Phase 5: Summary Report Generation
            if not self._should_skip_phase(5):
                result = self._execute_phase_5()
                if not result['success']:
                    return self._failure_result('Phase 5: Summary Report', result['error'])

            # All phases completed successfully
            return {
                'success': True,
                'phase_results': self.phase_results
            }

        except Exception as e:
            return self._failure_result('Workflow Execution', str(e))

    def _should_skip_phase(self, phase_num: int) -> bool:
        """Check if a phase should be skipped."""
        if hasattr(self.args, 'skip_phase') and self.args.skip_phase:
            return str(phase_num) == self.args.skip_phase
        return False

    def _execute_phase_1(self) -> Dict[str, Any]:
        """
        Phase 1: Resource Discovery

        Invokes aws-resource-discovery to scan AWS account and create inventory.
        """
        self.progress.start_phase(1, "Discovering AWS resources")
        self.progress.update(f"Profile: {self.args.profile} | Region: {self.args.region}")

        # Build command arguments for discovery skill
        cmd_args = [
            '--profile', self.args.profile,
            '--region', self.args.region,
            '--output-dir', str(self.discovery_dir)
        ]

        if self.args.resource_types:
            cmd_args.extend(['--resource-types', self.args.resource_types])

        if self.args.tag_filter:
            cmd_args.extend(['--tag-filter', self.args.tag_filter])

        if self.args.name_pattern:
            cmd_args.extend(['--name-pattern', self.args.name_pattern])

        # Invoke discovery skill
        result = self.invoker.invoke_skill(
            skill_name='aws-resource-discovery',
            script_name='discover.py',
            args=cmd_args
        )

        if not result['success']:
            return result

        # Validate discovery output
        resources_file = self.discovery_dir / 'resources.json'
        if not self.dry_run and not resources_file.exists():
            return {
                'success': False,
                'error': f'Expected output file not found: {resources_file}'
            }

        # Parse and display resource counts
        if not self.dry_run:
            try:
                with open(resources_file, 'r') as f:
                    resources = json.load(f)

                resource_counts = self._count_resources(resources)
                for resource_type, count in resource_counts.items():
                    self.progress.update(f"✓ Found {count} {resource_type}")

                # Store phase results
                self.phase_results['phase_1'] = {
                    'resource_counts': resource_counts,
                    'total_resources': sum(resource_counts.values())
                }

            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Invalid JSON in resources file: {str(e)}'
                }

        self.progress.complete_phase()
        return {'success': True}

    def _execute_phase_2(self) -> Dict[str, Any]:
        """
        Phase 2: CDK Code Generation

        Invokes cdk-code-generator to create TypeScript constructs.
        """
        self.progress.start_phase(2, "Generating CDK constructs")
        self.progress.update(f"Mode: {self.args.mode}")

        # Validate input from Phase 1
        resources_file = self.discovery_dir / 'resources.json'
        if not self.dry_run:
            valid, error = self.data_passer.validate_discovery_output(self.discovery_dir)
            if not valid:
                return {'success': False, 'error': error}

        # Build command arguments for code generator skill
        cmd_args = [
            '--input', str(resources_file),
            '--output-dir', str(self.cdk_generated_dir),
            '--mode', self.args.mode
        ]

        # Invoke code generator skill
        result = self.invoker.invoke_skill(
            skill_name='cdk-code-generator',
            script_name='generate.py',
            args=cmd_args
        )

        if not result['success']:
            return result

        # Validate code generation output
        if not self.dry_run:
            valid, error = self.data_passer.validate_code_generation_output(
                self.cdk_generated_dir
            )
            if not valid:
                return {'success': False, 'error': error}

            # Count generated constructs
            construct_count = self._count_generated_constructs(self.cdk_generated_dir)
            self.progress.update(f"✓ Generated {construct_count} construct files")

            self.phase_results['phase_2'] = {
                'construct_count': construct_count,
                'mode': self.args.mode
            }

        self.progress.complete_phase()
        return {'success': True}

    def _execute_phase_3(self) -> Dict[str, Any]:
        """
        Phase 3: Stack Organization

        Invokes cdk-stack-organizer to group constructs into logical stacks.
        """
        self.progress.start_phase(3, "Organizing into CDK stacks")
        self.progress.update(f"Strategy: {self.args.strategy}")

        # Validate input from Phase 2
        if not self.dry_run:
            valid, error = self.data_passer.validate_code_generation_output(
                self.cdk_generated_dir
            )
            if not valid:
                return {'success': False, 'error': error}

        # Build command arguments for stack organizer skill
        cmd_args = [
            '--input-dir', str(self.cdk_generated_dir),
            '--output-dir', str(self.cdk_organized_dir),
            '--strategy', self.args.strategy
        ]

        if self.args.tag_key:
            cmd_args.extend(['--tag-key', self.args.tag_key])

        if self.args.custom_rules:
            cmd_args.extend(['--custom-rules', self.args.custom_rules])

        # Invoke stack organizer skill
        result = self.invoker.invoke_skill(
            skill_name='cdk-stack-organizer',
            script_name='organize.py',
            args=cmd_args
        )

        if not result['success']:
            return result

        # Validate stack organization output
        if not self.dry_run:
            valid, error = self.data_passer.validate_stack_organization_output(
                self.cdk_organized_dir
            )
            if not valid:
                return {'success': False, 'error': error}

            # Count created stacks
            stack_files = self._count_stack_files(self.cdk_organized_dir)
            self.progress.update(f"✓ Created {len(stack_files)} stack files")

            self.phase_results['phase_3'] = {
                'stack_count': len(stack_files),
                'stack_names': stack_files,
                'strategy': self.args.strategy
            }

        self.progress.complete_phase()
        return {'success': True}

    def _execute_phase_4(self) -> Dict[str, Any]:
        """
        Phase 4: Import Configuration Generation

        Invokes cdk-import-config-generator to create import mappings and scripts.
        """
        self.progress.start_phase(4, "Generating import configurations")

        # Validate inputs from Phase 1 and Phase 3
        if not self.dry_run:
            valid, error = self.data_passer.validate_discovery_output(self.discovery_dir)
            if not valid:
                return {'success': False, 'error': error}

            valid, error = self.data_passer.validate_stack_organization_output(
                self.cdk_organized_dir
            )
            if not valid:
                return {'success': False, 'error': error}

        # Build command arguments for import config generator skill
        cmd_args = [
            '--resources-file', str(self.discovery_dir / 'resources.json'),
            '--cdk-dir', str(self.cdk_organized_dir),
            '--output-dir', str(self.import_configs_dir),
            '--profile', self.args.profile,
            '--region', self.args.region
        ]

        # Invoke import config generator skill
        result = self.invoker.invoke_skill(
            skill_name='cdk-import-config-generator',
            script_name='generate_import_configs.py',
            args=cmd_args
        )

        if not result['success']:
            return result

        # Validate import config output
        if not self.dry_run:
            valid, error = self.data_passer.validate_import_config_output(
                self.import_configs_dir
            )
            if not valid:
                return {'success': False, 'error': error}

            # Count import mappings and scripts
            mapping_count = self._count_import_mappings(self.import_configs_dir)
            script_count = self._count_import_scripts(self.import_configs_dir)

            self.progress.update(f"✓ Created import mappings for {mapping_count} resources")
            self.progress.update(f"✓ Generated {script_count} import scripts")

            self.phase_results['phase_4'] = {
                'mapping_count': mapping_count,
                'script_count': script_count
            }

        self.progress.complete_phase()
        return {'success': True}

    def _execute_phase_5(self) -> Dict[str, Any]:
        """
        Phase 5: Summary Report Generation

        Creates a comprehensive final report of the entire workflow.
        """
        self.progress.start_phase(5, "Creating summary report")

        if self.dry_run:
            self.progress.update("✓ (Dry run - report generation skipped)")
            self.progress.complete_phase()
            return {'success': True}

        try:
            # Load report template
            template_path = Path(__file__).parent.parent / 'assets' / 'report-template.md'

            if template_path.exists():
                with open(template_path, 'r') as f:
                    template = f.read()
            else:
                # Use minimal template if asset not found
                template = self._get_minimal_report_template()

            # Generate report content
            report_content = self._generate_report_content(template)

            # Write report to output directory
            report_path = self.output_dir / 'IMPORT_SUMMARY.md'
            with open(report_path, 'w') as f:
                f.write(report_content)

            self.progress.update(f"✓ Report saved to {report_path.name}")

            self.phase_results['phase_5'] = {
                'report_path': str(report_path)
            }

            self.progress.complete_phase()
            return {'success': True}

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate report: {str(e)}'
            }

    def _generate_report_content(self, template: str) -> str:
        """Generate the final report content using the template and phase results."""
        # Get phase results
        phase_1 = self.phase_results.get('phase_1', {})
        phase_2 = self.phase_results.get('phase_2', {})
        phase_3 = self.phase_results.get('phase_3', {})
        phase_4 = self.phase_results.get('phase_4', {})

        # Format resource counts
        resource_counts = phase_1.get('resource_counts', {})
        resource_summary = '\n'.join([
            f"- {resource_type}: {count}"
            for resource_type, count in resource_counts.items()
        ])

        # Format stack names
        stack_names = phase_3.get('stack_names', [])
        stack_summary = '\n'.join([f"- {name}" for name in stack_names])

        # Replace template placeholders
        report = template.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        report = report.replace('{{PROFILE}}', self.args.profile)
        report = report.replace('{{REGION}}', self.args.region)
        report = report.replace('{{TOTAL_RESOURCES}}', str(phase_1.get('total_resources', 0)))
        report = report.replace('{{RESOURCE_SUMMARY}}', resource_summary or 'No resources')
        report = report.replace('{{CONSTRUCT_COUNT}}', str(phase_2.get('construct_count', 0)))
        report = report.replace('{{MODE}}', phase_2.get('mode', 'reference'))
        report = report.replace('{{STACK_COUNT}}', str(phase_3.get('stack_count', 0)))
        report = report.replace('{{STACK_SUMMARY}}', stack_summary or 'No stacks')
        report = report.replace('{{STRATEGY}}', phase_3.get('strategy', 'layer'))
        report = report.replace('{{MAPPING_COUNT}}', str(phase_4.get('mapping_count', 0)))
        report = report.replace('{{SCRIPT_COUNT}}', str(phase_4.get('script_count', 0)))
        report = report.replace('{{OUTPUT_DIR}}', str(self.output_dir))

        return report

    def _get_minimal_report_template(self) -> str:
        """Return a minimal report template if asset file is not found."""
        return """# AWS to CDK Import - Summary Report

Generated: {{DATE}}

## Configuration

- AWS Profile: {{PROFILE}}
- AWS Region: {{REGION}}
- Output Directory: {{OUTPUT_DIR}}

## Phase 1: Resource Discovery

Total Resources Discovered: {{TOTAL_RESOURCES}}

{{RESOURCE_SUMMARY}}

## Phase 2: CDK Code Generation

- Constructs Generated: {{CONSTRUCT_COUNT}}
- Mode: {{MODE}}

## Phase 3: Stack Organization

- Stacks Created: {{STACK_COUNT}}
- Strategy: {{STRATEGY}}

Stacks:
{{STACK_SUMMARY}}

## Phase 4: Import Configuration

- Import Mappings: {{MAPPING_COUNT}}
- Import Scripts: {{SCRIPT_COUNT}}

## Next Steps

1. Install dependencies: `cd {{OUTPUT_DIR}}/cdk-organized && npm install`
2. Review generated code: `cat {{OUTPUT_DIR}}/cdk-organized/lib/stacks/*.ts`
3. Run CDK synthesis: `npm run build && cdk synth`
4. Execute imports: `cd {{OUTPUT_DIR}}/import-configs/scripts && ./import-all.sh`
5. Verify imports: `./verify-imports.sh`
"""

    def _failure_result(self, phase: str, error: str) -> Dict[str, Any]:
        """Create a failure result with error details."""
        # Log error to file
        if not self.dry_run:
            error_log = self.output_dir / 'error.log'
            with open(error_log, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] {phase} failed:\n")
                f.write(f"{error}\n\n")

        return {
            'success': False,
            'failed_phase': phase,
            'error': error,
            'phase_results': self.phase_results
        }

    # Helper methods for counting resources and files

    def _count_resources(self, resources: Dict[str, Any]) -> Dict[str, int]:
        """Count resources by type from discovery output."""
        counts = {}
        for resource_type, items in resources.items():
            if isinstance(items, list):
                counts[resource_type] = len(items)
        return counts

    def _count_generated_constructs(self, output_dir: Path) -> int:
        """Count the number of generated TypeScript construct files."""
        construct_dir = output_dir / 'constructs'
        if not construct_dir.exists():
            return 0

        count = 0
        for file_path in construct_dir.rglob('*.ts'):
            if file_path.is_file():
                count += 1
        return count

    def _count_stack_files(self, output_dir: Path) -> list:
        """Count and list stack files created during organization."""
        stack_dir = output_dir / 'lib' / 'stacks'
        if not stack_dir.exists():
            return []

        stack_files = []
        for file_path in stack_dir.glob('*.ts'):
            if file_path.is_file():
                stack_files.append(file_path.stem)
        return stack_files

    def _count_import_mappings(self, output_dir: Path) -> int:
        """Count the number of import mapping JSON files."""
        mappings_dir = output_dir / 'mappings'
        if not mappings_dir.exists():
            return 0

        return len(list(mappings_dir.glob('*.json')))

    def _count_import_scripts(self, output_dir: Path) -> int:
        """Count the number of import shell scripts."""
        scripts_dir = output_dir / 'scripts'
        if not scripts_dir.exists():
            return 0

        return len(list(scripts_dir.glob('*.sh')))
