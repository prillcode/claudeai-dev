"""
Resource Filters

Handles filtering resources by tags, name patterns, and resource types.
"""

import fnmatch
from typing import Dict, List, Optional, Any


class ResourceFilter:
    """Filters resources based on tags, name patterns, and resource types."""

    def __init__(
        self,
        tags: Optional[Dict[str, str]] = None,
        name_pattern: Optional[str] = None,
        resource_types: Optional[List[str]] = None
    ):
        """
        Initialize resource filter.

        Args:
            tags: Dictionary of tag key-value pairs to filter by
            name_pattern: Unix-style glob pattern for resource names
            resource_types: List of resource types to include (e.g., ['lambda', 'dynamodb'])
        """
        self.tags = tags or {}
        self.name_pattern = name_pattern
        self.resource_types = set(resource_types) if resource_types else set()

    def should_include_resource_type(self, resource_type: str) -> bool:
        """
        Check if a resource type should be included based on filters.

        Args:
            resource_type: Resource type (e.g., 'lambda', 'dynamodb')

        Returns:
            True if resource type should be included, False otherwise
        """
        if not self.resource_types:
            # No resource type filter, include all
            return True
        return resource_type in self.resource_types

    def matches_tags(self, resource_tags: Dict[str, str]) -> bool:
        """
        Check if resource tags match the filter criteria.

        Args:
            resource_tags: Dictionary of resource tags

        Returns:
            True if tags match, False otherwise
        """
        if not self.tags:
            # No tag filter, match all
            return True

        if not resource_tags:
            # Resource has no tags, doesn't match
            return False

        # All filter tags must match
        for key, value in self.tags.items():
            if key not in resource_tags:
                return False
            if resource_tags[key] != value:
                return False

        return True

    def matches_name(self, resource_name: str) -> bool:
        """
        Check if resource name matches the pattern.

        Args:
            resource_name: Name of the resource

        Returns:
            True if name matches, False otherwise
        """
        if not self.name_pattern:
            # No name filter, match all
            return True

        # Use fnmatch for Unix-style glob matching
        return fnmatch.fnmatch(resource_name, self.name_pattern)

    def matches(self, resource: Dict[str, Any], resource_name: str, resource_tags: Dict[str, str]) -> bool:
        """
        Check if a resource matches all filter criteria.

        Args:
            resource: The resource dictionary
            resource_name: Name of the resource
            resource_tags: Tags associated with the resource

        Returns:
            True if resource matches all filters, False otherwise
        """
        return self.matches_name(resource_name) and self.matches_tags(resource_tags)

    def has_filters(self) -> bool:
        """Check if any filters are configured."""
        return bool(self.tags) or bool(self.name_pattern) or bool(self.resource_types)

    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Get a summary of active filters.

        Returns:
            Dictionary describing active filters
        """
        summary = {}
        if self.tags:
            summary['tags'] = self.tags
        if self.name_pattern:
            summary['name_pattern'] = self.name_pattern
        if self.resource_types:
            summary['resource_types'] = list(self.resource_types)
        return summary


def parse_tags(tag_strings: List[str]) -> Dict[str, str]:
    """
    Parse tag strings in format 'key=value' into a dictionary.

    Args:
        tag_strings: List of strings in format 'key=value'

    Returns:
        Dictionary of tag key-value pairs

    Example:
        >>> parse_tags(['project=myapp', 'environment=prod'])
        {'project': 'myapp', 'environment': 'prod'}
    """
    tags = {}
    for tag_str in tag_strings:
        if '=' not in tag_str:
            print(f"⚠️  Warning: Invalid tag format '{tag_str}', expected 'key=value'. Skipping.")
            continue
        key, value = tag_str.split('=', 1)
        tags[key.strip()] = value.strip()
    return tags


def normalize_aws_tags(aws_tags: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Convert AWS tag format to simple key-value dict.

    Args:
        aws_tags: List of AWS tag dicts with 'Key' and 'Value' fields

    Returns:
        Simple dictionary of tag key-value pairs

    Example:
        >>> normalize_aws_tags([{'Key': 'project', 'Value': 'myapp'}])
        {'project': 'myapp'}
    """
    if not aws_tags:
        return {}
    return {tag['Key']: tag['Value'] for tag in aws_tags}
