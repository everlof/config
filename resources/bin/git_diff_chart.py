#!/usr/bin/env python3
"""
Generate a pie chart from git diff --stat output.
Usage:
  git diff --stat | python git_diff_chart.py [output_file]
  git diff --stat | python git_diff_chart.py > output.png
  git diff --stat | python git_diff_chart.py output.png
"""

import sys
import re
import io
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_diff_stat(lines):
    """Parse git diff --stat output and extract file changes."""
    file_changes = {}

    for line in lines:
        # Match lines like: " path/to/file.py | 45 +++++-----"
        # The format is: filename | number changes
        match = re.match(r'\s*(.+?)\s*\|\s*(\d+)', line)
        if match:
            filename = match.group(1).strip()
            changes = int(match.group(2))
            file_changes[filename] = changes

    return file_changes

def create_pie_chart(file_changes, output_file=None):
    """Create a pie chart from file changes data."""
    if not file_changes:
        print("No changes found in input.", file=sys.stderr)
        sys.exit(1)

    # Prepare data for pie chart
    files = list(file_changes.keys())
    changes = list(file_changes.values())

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        changes,
        labels=files,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 9}
    )

    # Enhance readability
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    # Add title
    total_changes = sum(changes)
    ax.set_title(f'Git Diff Changes Distribution\nTotal Changes: {total_changes}',
                 fontsize=14, fontweight='bold', pad=20)

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Determine output method
    if output_file:
        # Save to specified file
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {output_file}", file=sys.stderr)
    else:
        # Check if stdout is being redirected
        if not sys.stdout.isatty():
            # stdout is redirected (pipe or file), write binary PNG data
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            sys.stdout.buffer.write(buf.read())
        else:
            # stdout is a terminal, save to default file
            default_file = 'git_diff_chart.png'
            plt.savefig(default_file, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {default_file}", file=sys.stderr)

    plt.close()

def main():
    """Main function to read stdin and generate chart."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate a pie chart from git diff --stat output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git diff --stat | python git_diff_chart.py
  git diff --stat | python git_diff_chart.py output.png
  git diff --stat | python git_diff_chart.py > ~/Downloads/chart.png
        """
    )
    parser.add_argument('output', nargs='?', default=None,
                       help='Output file path (default: auto-detect or git_diff_chart.png)')

    args = parser.parse_args()

    # Read from stdin
    lines = sys.stdin.readlines()

    if not lines:
        print("Error: No input received. Usage: git diff --stat | python git_diff_chart.py",
              file=sys.stderr)
        sys.exit(1)

    # Parse the diff stat output
    file_changes = parse_diff_stat(lines)

    # Create the pie chart
    create_pie_chart(file_changes, args.output)

if __name__ == '__main__':
    main()