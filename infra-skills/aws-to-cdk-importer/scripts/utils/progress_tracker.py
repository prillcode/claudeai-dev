"""
Progress Tracker - Displays real-time progress updates during workflow execution

Provides formatted progress output with phase numbers, status indicators,
and detailed messages.
"""

from datetime import datetime
from typing import Optional


class ProgressTracker:
    """Tracks and displays workflow progress."""

    def __init__(self, total_phases: int = 5, verbose: bool = False):
        """
        Initialize the progress tracker.

        Args:
            total_phases: Total number of phases in the workflow
            verbose: Whether to display verbose output
        """
        self.total_phases = total_phases
        self.verbose = verbose
        self.current_phase = 0
        self.phase_start_time = None

    def start_phase(self, phase_num: int, phase_name: str):
        """
        Start tracking a new phase.

        Args:
            phase_num: Phase number (1-5)
            phase_name: Human-readable phase name
        """
        self.current_phase = phase_num
        self.phase_start_time = datetime.now()

        print()
        print(f"[{phase_num}/{self.total_phases}] {phase_name}...")

    def update(self, message: str, indent: int = 6):
        """
        Print a progress update message.

        Args:
            message: Update message to display
            indent: Number of spaces to indent (default: 6)
        """
        print(f"{' ' * indent}{message}")

    def complete_phase(self):
        """Mark the current phase as complete and show duration."""
        if self.phase_start_time:
            duration = (datetime.now() - self.phase_start_time).total_seconds()

            if self.verbose:
                print(f"      ✓ Phase {self.current_phase} completed in {duration:.1f}s")

        self.phase_start_time = None

    def error(self, message: str):
        """
        Display an error message.

        Args:
            message: Error message to display
        """
        print(f"      ❌ {message}")

    def warning(self, message: str):
        """
        Display a warning message.

        Args:
            message: Warning message to display
        """
        print(f"      ⚠️  {message}")

    def info(self, message: str):
        """
        Display an informational message.

        Args:
            message: Info message to display
        """
        print(f"      ℹ️  {message}")

    def success(self, message: str):
        """
        Display a success message.

        Args:
            message: Success message to display
        """
        print(f"      ✓ {message}")

    def print_separator(self, char: str = "-", length: int = 70):
        """
        Print a separator line.

        Args:
            char: Character to use for separator
            length: Length of separator line
        """
        print(char * length)

    def print_header(self, text: str):
        """
        Print a formatted header.

        Args:
            text: Header text
        """
        print()
        self.print_separator("=")
        print(text)
        self.print_separator("=")
        print()

    def print_summary(self, title: str, items: dict):
        """
        Print a formatted summary of key-value pairs.

        Args:
            title: Summary title
            items: Dictionary of items to display
        """
        print()
        print(title)
        self.print_separator("-")
        for key, value in items.items():
            print(f"{key:20}: {value}")
        self.print_separator("-")
        print()

    def verbose_log(self, message: str):
        """
        Print a message only if verbose mode is enabled.

        Args:
            message: Message to display in verbose mode
        """
        if self.verbose:
            print(f"      [DEBUG] {message}")


class PhaseTimer:
    """Context manager for timing individual phases."""

    def __init__(self, tracker: ProgressTracker, phase_num: int, phase_name: str):
        """
        Initialize the phase timer.

        Args:
            tracker: ProgressTracker instance
            phase_num: Phase number
            phase_name: Phase name
        """
        self.tracker = tracker
        self.phase_num = phase_num
        self.phase_name = phase_name

    def __enter__(self):
        """Start the phase when entering context."""
        self.tracker.start_phase(self.phase_num, self.phase_name)
        return self.tracker

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete the phase when exiting context."""
        if exc_type is None:
            # No exception - phase completed successfully
            self.tracker.complete_phase()
        else:
            # Exception occurred - display error
            self.tracker.error(f"Phase failed: {str(exc_val)}")

        # Don't suppress exceptions
        return False


# Utility functions for common progress patterns

def track_file_processing(
    tracker: ProgressTracker,
    total: int,
    current: int,
    filename: str,
    interval: int = 10
):
    """
    Track progress of file processing operations.

    Args:
        tracker: ProgressTracker instance
        total: Total number of files
        current: Current file index (0-based)
        filename: Name of current file being processed
        interval: Update interval (show progress every N files)
    """
    if current % interval == 0 or current == total - 1:
        percentage = int((current + 1) / total * 100)
        tracker.update(f"[{percentage:3}%] Processing {filename}")


def track_resource_counts(
    tracker: ProgressTracker,
    resource_counts: dict
):
    """
    Display resource counts in a formatted way.

    Args:
        tracker: ProgressTracker instance
        resource_counts: Dictionary mapping resource types to counts
    """
    for resource_type, count in sorted(resource_counts.items()):
        tracker.update(f"✓ Found {count} {resource_type}")


def track_generation_progress(
    tracker: ProgressTracker,
    service_type: str,
    generated_count: int
):
    """
    Display code generation progress.

    Args:
        tracker: ProgressTracker instance
        service_type: Type of AWS service (e.g., "Lambda", "DynamoDB")
        generated_count: Number of constructs generated
    """
    tracker.update(f"✓ Generated {generated_count} {service_type} constructs")
