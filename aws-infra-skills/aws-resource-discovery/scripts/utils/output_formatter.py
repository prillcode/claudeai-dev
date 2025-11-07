"""
Output Formatter

Handles formatting and writing resource inventory data to JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class OutputFormatter:
    """Formats and writes resource discovery output to JSON files."""

    def __init__(self, output_dir: str):
        """
        Initialize output formatter.

        Args:
            output_dir: Directory path where output files will be written
        """
        self.output_dir = Path(output_dir)
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory: {self.output_dir.absolute()}")

    def write_metadata(
        self,
        account_id: str,
        region: str,
        profile: str,
        filters: Dict[str, Any],
        resource_counts: Dict[str, int]
    ):
        """
        Write scan metadata to metadata.json.

        Args:
            account_id: AWS account ID
            region: AWS region
            profile: AWS profile name
            filters: Applied filters
            resource_counts: Count of resources discovered by type
        """
        metadata = {
            'account_id': account_id,
            'region': region,
            'profile': profile,
            'scan_timestamp': datetime.utcnow().isoformat() + 'Z',
            'filters_applied': filters,
            'resource_counts': resource_counts
        }

        self._write_json_file('metadata.json', metadata)
        print(f"✓ Wrote metadata.json")

    def write_resources(self, resource_type: str, resources: List[Dict[str, Any]]):
        """
        Write resources to a JSON file.

        Args:
            resource_type: Type of resources (e.g., 'lambdas', 'dynamodb-tables')
            resources: List of resource dictionaries
        """
        filename = f"{resource_type}.json"
        self._write_json_file(filename, resources)
        print(f"✓ Wrote {filename} ({len(resources)} resources)")

    def write_dependencies(self, dependencies: List[Dict[str, Any]]):
        """
        Write dependency graph to dependencies.json.

        Args:
            dependencies: List of dependency relationships
        """
        self._write_json_file('dependencies.json', dependencies)
        print(f"✓ Wrote dependencies.json ({len(dependencies)} relationships)")

    def _write_json_file(self, filename: str, data: Any):
        """
        Write data to a JSON file with pretty formatting.

        Args:
            filename: Name of the file to write
            data: Data to write as JSON
        """
        file_path = self.output_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def read_json_file(self, filename: str) -> Any:
        """
        Read and parse a JSON file from the output directory.

        Args:
            filename: Name of the file to read

        Returns:
            Parsed JSON data
        """
        file_path = self.output_dir / filename
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            return json.load(f)

    def generate_summary_report(self, resource_counts: Dict[str, int]) -> str:
        """
        Generate a human-readable summary of discovered resources.

        Args:
            resource_counts: Dictionary of resource type to count

        Returns:
            Formatted summary string
        """
        summary = "\n" + "=" * 60 + "\n"
        summary += "Resource Discovery Summary\n"
        summary += "=" * 60 + "\n\n"

        total_resources = sum(resource_counts.values())
        summary += f"Total resources discovered: {total_resources}\n\n"

        if total_resources == 0:
            summary += "No resources found matching the specified criteria.\n"
            summary += "\nTips:\n"
            summary += "  - Check if filters are too restrictive\n"
            summary += "  - Verify resources exist in the specified region\n"
            summary += "  - Try scanning without filters first\n"
        else:
            summary += "Resources by type:\n"
            for resource_type, count in sorted(resource_counts.items()):
                if count > 0:
                    summary += f"  • {resource_type}: {count}\n"

        summary += "\n" + "=" * 60 + "\n"
        summary += f"Output location: {self.output_dir.absolute()}\n"
        summary += "=" * 60 + "\n"

        return summary


def format_arn(service: str, region: str, account_id: str, resource_type: str, resource_id: str) -> str:
    """
    Format an AWS ARN.

    Args:
        service: AWS service name (e.g., 'lambda', 'dynamodb')
        region: AWS region
        account_id: AWS account ID
        resource_type: Resource type (e.g., 'function', 'table')
        resource_id: Resource identifier

    Returns:
        Formatted ARN string
    """
    return f"arn:aws:{service}:{region}:{account_id}:{resource_type}/{resource_id}"


def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        dictionary: Dictionary to search
        *keys: Chain of keys to follow
        default: Default value if key path doesn't exist

    Returns:
        Value at key path or default

    Example:
        >>> safe_get({'a': {'b': {'c': 1}}}, 'a', 'b', 'c')
        1
        >>> safe_get({'a': {'b': {}}}, 'a', 'b', 'c', default='not found')
        'not found'
    """
    current = dictionary
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
