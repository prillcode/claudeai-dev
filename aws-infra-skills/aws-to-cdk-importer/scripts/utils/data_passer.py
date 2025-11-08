"""
Data Passer - Validates outputs and passes data between workflow phases

Ensures that each phase produces the expected output files
and that subsequent phases can consume them correctly.
"""

import json
from pathlib import Path
from typing import Tuple, Dict, Any


class DataPasser:
    """Validates outputs and facilitates data passing between phases."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the data passer.

        Args:
            verbose: Whether to print detailed validation messages
        """
        self.verbose = verbose

    def validate_discovery_output(self, discovery_dir: Path) -> Tuple[bool, str]:
        """
        Validate Phase 1 (Resource Discovery) output.

        Expected structure:
            discovery/
            └── resources.json

        Args:
            discovery_dir: Path to the discovery output directory

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not discovery_dir.exists():
            return False, f"Discovery directory not found: {discovery_dir}"

        resources_file = discovery_dir / 'resources.json'
        if not resources_file.exists():
            return False, f"Resources file not found: {resources_file}"

        # Validate JSON structure
        try:
            with open(resources_file, 'r') as f:
                resources = json.load(f)

            if not isinstance(resources, dict):
                return False, "Resources file must contain a JSON object"

            if len(resources) == 0:
                return False, "No resources found in resources.json"

            if self.verbose:
                print(f"  ✓ Discovery output validated: {len(resources)} resource types")

            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in resources.json: {str(e)}"

        except Exception as e:
            return False, f"Failed to validate discovery output: {str(e)}"

    def validate_code_generation_output(self, cdk_generated_dir: Path) -> Tuple[bool, str]:
        """
        Validate Phase 2 (CDK Code Generation) output.

        Expected structure:
            cdk-generated/
            ├── constructs/
            │   └── (service-type)/
            │       └── *.ts files
            ├── dependencies.json
            └── metadata.json

        Args:
            cdk_generated_dir: Path to the code generation output directory

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not cdk_generated_dir.exists():
            return False, f"CDK generated directory not found: {cdk_generated_dir}"

        constructs_dir = cdk_generated_dir / 'constructs'
        if not constructs_dir.exists():
            return False, f"Constructs directory not found: {constructs_dir}"

        # Check for at least one TypeScript file
        ts_files = list(constructs_dir.rglob('*.ts'))
        if len(ts_files) == 0:
            return False, "No TypeScript construct files found"

        # Validate dependencies.json if present
        dependencies_file = cdk_generated_dir / 'dependencies.json'
        if dependencies_file.exists():
            try:
                with open(dependencies_file, 'r') as f:
                    dependencies = json.load(f)

                if not isinstance(dependencies, dict):
                    return False, "dependencies.json must contain a JSON object"

            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in dependencies.json: {str(e)}"

        # Validate metadata.json if present
        metadata_file = cdk_generated_dir / 'metadata.json'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                if not isinstance(metadata, dict):
                    return False, "metadata.json must contain a JSON object"

            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in metadata.json: {str(e)}"

        if self.verbose:
            print(f"  ✓ Code generation output validated: {len(ts_files)} construct files")

        return True, None

    def validate_stack_organization_output(self, cdk_organized_dir: Path) -> Tuple[bool, str]:
        """
        Validate Phase 3 (Stack Organization) output.

        Expected structure:
            cdk-organized/
            ├── lib/
            │   ├── stacks/
            │   │   └── *-stack.ts
            │   └── constructs/
            │       └── *.ts
            ├── bin/
            │   └── app.ts
            ├── cdk.json
            ├── package.json
            └── tsconfig.json

        Args:
            cdk_organized_dir: Path to the organized CDK project directory

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not cdk_organized_dir.exists():
            return False, f"CDK organized directory not found: {cdk_organized_dir}"

        # Check for required directories
        lib_dir = cdk_organized_dir / 'lib'
        if not lib_dir.exists():
            return False, f"lib directory not found: {lib_dir}"

        stacks_dir = lib_dir / 'stacks'
        if not stacks_dir.exists():
            return False, f"stacks directory not found: {stacks_dir}"

        bin_dir = cdk_organized_dir / 'bin'
        if not bin_dir.exists():
            return False, f"bin directory not found: {bin_dir}"

        # Check for at least one stack file
        stack_files = list(stacks_dir.glob('*.ts'))
        if len(stack_files) == 0:
            return False, "No stack files found in lib/stacks/"

        # Check for required CDK project files
        required_files = ['cdk.json', 'package.json', 'tsconfig.json']
        missing_files = []

        for filename in required_files:
            if not (cdk_organized_dir / filename).exists():
                missing_files.append(filename)

        if missing_files:
            return False, f"Missing required CDK project files: {', '.join(missing_files)}"

        # Check for app.ts
        app_file = bin_dir / 'app.ts'
        if not app_file.exists():
            return False, f"CDK app entry point not found: {app_file}"

        if self.verbose:
            print(f"  ✓ Stack organization output validated: {len(stack_files)} stacks")

        return True, None

    def validate_import_config_output(self, import_configs_dir: Path) -> Tuple[bool, str]:
        """
        Validate Phase 4 (Import Configuration Generation) output.

        Expected structure:
            import-configs/
            ├── mappings/
            │   └── *-import.json
            └── scripts/
                ├── import-*.sh
                └── verify-imports.sh

        Args:
            import_configs_dir: Path to the import configurations directory

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not import_configs_dir.exists():
            return False, f"Import configs directory not found: {import_configs_dir}"

        mappings_dir = import_configs_dir / 'mappings'
        if not mappings_dir.exists():
            return False, f"Mappings directory not found: {mappings_dir}"

        scripts_dir = import_configs_dir / 'scripts'
        if not scripts_dir.exists():
            return False, f"Scripts directory not found: {scripts_dir}"

        # Check for at least one mapping file
        mapping_files = list(mappings_dir.glob('*.json'))
        if len(mapping_files) == 0:
            return False, "No import mapping files found"

        # Validate mapping JSON files
        for mapping_file in mapping_files:
            try:
                with open(mapping_file, 'r') as f:
                    mapping = json.load(f)

                if not isinstance(mapping, dict):
                    return False, f"Invalid mapping file {mapping_file.name}: must be JSON object"

            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in {mapping_file.name}: {str(e)}"

        # Check for at least one import script
        import_scripts = list(scripts_dir.glob('import-*.sh'))
        if len(import_scripts) == 0:
            return False, "No import scripts found"

        # Check for verify script
        verify_script = scripts_dir / 'verify-imports.sh'
        if not verify_script.exists():
            return False, f"Verification script not found: {verify_script}"

        if self.verbose:
            print(f"  ✓ Import config output validated: {len(mapping_files)} mappings, {len(import_scripts)} scripts")

        return True, None

    def get_resource_inventory(self, discovery_dir: Path) -> Dict[str, Any]:
        """
        Load the resource inventory from Phase 1 output.

        Args:
            discovery_dir: Path to the discovery output directory

        Returns:
            dict: Resource inventory

        Raises:
            FileNotFoundError: If resources.json not found
            json.JSONDecodeError: If resources.json is invalid
        """
        resources_file = discovery_dir / 'resources.json'

        with open(resources_file, 'r') as f:
            return json.load(f)

    def get_dependencies(self, cdk_generated_dir: Path) -> Dict[str, str]:
        """
        Load the NPM dependencies from Phase 2 output.

        Args:
            cdk_generated_dir: Path to the code generation output directory

        Returns:
            dict: NPM dependencies mapping

        Raises:
            FileNotFoundError: If dependencies.json not found
            json.JSONDecodeError: If dependencies.json is invalid
        """
        dependencies_file = cdk_generated_dir / 'dependencies.json'

        if not dependencies_file.exists():
            return {}

        with open(dependencies_file, 'r') as f:
            return json.load(f)

    def get_metadata(self, cdk_generated_dir: Path) -> Dict[str, Any]:
        """
        Load the generation metadata from Phase 2 output.

        Args:
            cdk_generated_dir: Path to the code generation output directory

        Returns:
            dict: Generation metadata

        Raises:
            FileNotFoundError: If metadata.json not found
            json.JSONDecodeError: If metadata.json is invalid
        """
        metadata_file = cdk_generated_dir / 'metadata.json'

        if not metadata_file.exists():
            return {}

        with open(metadata_file, 'r') as f:
            return json.load(f)
