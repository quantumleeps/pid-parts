"""
Markdown generation utilities for PID parts.

This module provides functions to convert extracted PID parts data
into formatted Markdown tables for easy viewing and reporting.
"""

from pid_parts.state import Item


def render_md(items: dict[str, Item]) -> str:
    """Convert a dictionary of items into a formatted Markdown table.

    Creates a table with columns for tag, type, size, confidence score,
    and processing status, sorted by tag name for consistent output.

    Args:
        items: Dictionary of Item objects keyed by their tag strings

    Returns:
        Formatted Markdown table as a string, or empty string if no items
    """
    # Return empty string if there are no items
    if not items:
        return ""

    # Create the table header and separator row
    head = (
        "| Tag | Type | Size | Confidence | Status |"
        "\n|-----|------|------|------------|--------|"
    )

    # Generate a row for each item, sorted by tag for consistent output
    rows = [
        f"| {it.tag} | {it.type} | {it.size or ''} " f"| {it.conf:.2%} | {it.status} |"
        for it in sorted(items.values(), key=lambda i: i.tag)
    ]

    # Combine header and rows into a complete table
    return "\n".join([head, *rows])
