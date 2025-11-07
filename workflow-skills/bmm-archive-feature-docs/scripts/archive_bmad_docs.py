#!/usr/bin/env python3
"""
Archive BMAD feature documentation to prepare for next feature development cycle.

This script moves completed feature documentation files from the root BMAD Docs
directory into an archive subdirectory, allowing the workflow to restart cleanly
for the next major feature.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def get_current_git_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def archive_bmad_docs(bmad_docs_dir, archive_name):
    """
    Archive BMAD documentation files to a subdirectory in the archive folder.

    Args:
        bmad_docs_dir: Path to the BMAD Docs directory (e.g., .bmm-docs)
        archive_name: Name of the archive subdirectory (e.g., feature branch name)

    Returns:
        dict: Summary of archived files with success status and messages
    """
    bmad_path = Path(bmad_docs_dir).resolve()

    if not bmad_path.exists():
        return {
            'success': False,
            'error': f'BMAD Docs directory not found: {bmad_path}'
        }

    # Create archive directory if it doesn't exist
    archive_dir = bmad_path / 'archive'
    archive_dir.mkdir(exist_ok=True)

    # Create subdirectory for this feature
    feature_archive = archive_dir / archive_name
    if feature_archive.exists():
        return {
            'success': False,
            'error': f'Archive directory already exists: {feature_archive}'
        }

    feature_archive.mkdir()

    # Files and directories to archive
    items_to_archive = [
        'PRD.md',
        'epics.md',
        'project-overview.md',
        'project-scan-report.json',
        'sprint-status.yaml',
        'stories'  # directory
    ]

    archived_items = []
    skipped_items = []

    for item_name in items_to_archive:
        source = bmad_path / item_name
        destination = feature_archive / item_name

        if source.exists():
            try:
                if source.is_dir():
                    shutil.move(str(source), str(destination))
                else:
                    shutil.move(str(source), str(destination))
                archived_items.append(item_name)
            except Exception as e:
                skipped_items.append((item_name, str(e)))
        else:
            skipped_items.append((item_name, 'Not found'))

    return {
        'success': True,
        'archive_path': str(feature_archive),
        'archived': archived_items,
        'skipped': skipped_items
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: archive_bmad_docs.py <bmad_docs_dir> <archive_name>")
        print("Example: archive_bmad_docs.py .bmm-docs feature-auth-system")
        sys.exit(1)

    bmad_docs_dir = sys.argv[1]
    archive_name = sys.argv[2]

    result = archive_bmad_docs(bmad_docs_dir, archive_name)

    if result['success']:
        print(f"✅ Successfully archived BMAD docs to: {result['archive_path']}")
        print(f"\nArchived {len(result['archived'])} items:")
        for item in result['archived']:
            print(f"  - {item}")

        if result['skipped']:
            print(f"\nSkipped {len(result['skipped'])} items:")
            for item, reason in result['skipped']:
                print(f"  - {item} ({reason})")
    else:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
