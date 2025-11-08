"""
Skill Invoker - Invokes component skills' Python scripts via subprocess

Handles invoking the 4 component skills:
- aws-resource-discovery
- cdk-code-generator
- cdk-stack-organizer
- cdk-import-config-generator
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


class SkillInvoker:
    """Invokes component skill scripts via subprocess."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Initialize the skill invoker.

        Args:
            dry_run: Whether to simulate without actually running commands
            verbose: Whether to print detailed output
        """
        self.dry_run = dry_run
        self.verbose = verbose

        # Determine the base directory for skills
        # Assumes orchestrator is in: aws-infra-skills/aws-to-cdk-importer/scripts/
        # And component skills are in: aws-infra-skills/<skill-name>/
        self.skills_base_dir = Path(__file__).parent.parent.parent.parent

    def invoke_skill(
        self,
        skill_name: str,
        script_name: str,
        args: List[str]
    ) -> Dict[str, Any]:
        """
        Invoke a component skill's Python script.

        Args:
            skill_name: Name of the skill (e.g., 'aws-resource-discovery')
            script_name: Name of the script to run (e.g., 'discover.py')
            args: List of command-line arguments to pass to the script

        Returns:
            dict: Result with 'success' boolean and optional 'error' message
        """
        # Construct path to the skill's script
        script_path = self.skills_base_dir / skill_name / 'scripts' / script_name

        if not script_path.exists():
            return {
                'success': False,
                'error': f"Skill script not found: {script_path}"
            }

        # Build the command
        cmd = [sys.executable, str(script_path)] + args

        if self.verbose:
            print(f"  Invoking: {skill_name}/{script_name}")
            print(f"  Command: {' '.join(cmd)}")

        # Dry run - just print what would be executed
        if self.dry_run:
            print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
            return {'success': True}

        # Execute the command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            # Check exit code
            if result.returncode != 0:
                error_msg = f"Skill '{skill_name}' failed with exit code {result.returncode}"

                if result.stderr:
                    error_msg += f"\nError output:\n{result.stderr}"

                if self.verbose and result.stdout:
                    error_msg += f"\nStandard output:\n{result.stdout}"

                return {
                    'success': False,
                    'error': error_msg
                }

            # Success
            if self.verbose and result.stdout:
                print(f"  Output:\n{result.stdout}")

            return {'success': True, 'output': result.stdout}

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Skill '{skill_name}' timed out after 10 minutes"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to invoke skill '{skill_name}': {str(e)}"
            }

    def get_skill_path(self, skill_name: str) -> Path:
        """
        Get the path to a component skill's directory.

        Args:
            skill_name: Name of the skill

        Returns:
            Path: Path to the skill directory
        """
        return self.skills_base_dir / skill_name

    def verify_skill_exists(self, skill_name: str) -> bool:
        """
        Check if a component skill exists.

        Args:
            skill_name: Name of the skill to check

        Returns:
            bool: True if skill directory exists, False otherwise
        """
        skill_path = self.get_skill_path(skill_name)
        return skill_path.exists() and skill_path.is_dir()

    def verify_all_skills_exist(self) -> Dict[str, bool]:
        """
        Verify that all required component skills exist.

        Returns:
            dict: Mapping of skill name to existence boolean
        """
        required_skills = [
            'aws-resource-discovery',
            'cdk-code-generator',
            'cdk-stack-organizer',
            'cdk-import-config-generator'
        ]

        return {
            skill: self.verify_skill_exists(skill)
            for skill in required_skills
        }
