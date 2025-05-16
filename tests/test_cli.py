"""
Tests for the command-line interface functionality.
"""

import pytest
from unittest.mock import patch, mock_open
import json
import os


def test_ingest_basic(sample_pdf):
    """Test basic ingest functionality with mocked dependencies."""
    from pid_parts.cli import ingest
    from pid_parts.state import Item

    # Mock the drawing_ingestor function
    mock_items = {
        "PT-101": Item(tag="PT-101", type="PT", bbox=(0, 0, 10, 10), conf=0.9)
    }
    mock_markdown = "| Tag | Type | Size | Confidence | Status |\n|-----|------|------|------------|--------|\n| PT-101 | PT |  | 90.00% | INGESTED |"

    with patch("pid_parts.cli.asyncio.run") as mock_run:
        # Set up the mock to return the expected result
        mock_run.return_value = {"items": mock_items, "markdown": mock_markdown}

        # Capture stdout to verify JSON output
        with patch("builtins.print") as mock_print:
            ingest(sample_pdf, False, None)

            # Verify asyncio.run was called
            mock_run.assert_called_once()

            # Verify JSON was printed to stdout
            mock_print.assert_called()


def test_ingest_save_markdown(sample_pdf, tmp_path):
    """Test saving markdown functionality."""
    from pid_parts.cli import ingest
    from pid_parts.state import Item

    # Mock the drawing_ingestor function
    mock_items = {
        "PT-101": Item(tag="PT-101", type="PT", bbox=(0, 0, 10, 10), conf=0.9)
    }
    mock_markdown = "| Tag | Type | Size | Confidence | Status |\n|-----|------|------|------------|--------|\n| PT-101 | PT |  | 90.00% | INGESTED |"

    output_file = os.path.join(tmp_path, "output.md")

    with (
        patch("pid_parts.cli.asyncio.run") as mock_run,
        patch("builtins.open", mock_open()) as mock_file,
    ):

        # Set up the mock to return the expected result
        mock_run.return_value = {"items": mock_items, "markdown": mock_markdown}

        # Test with custom output path
        ingest(sample_pdf, True, output_file)

        # Verify file was opened for writing
        mock_file.assert_called_with(output_file, "w")

        # Verify markdown content was written
        mock_file().write.assert_called_with(mock_markdown)


def test_ingest_default_output_filename(sample_pdf):
    """Test default output filename generation."""
    from pid_parts.cli import ingest
    from pid_parts.state import Item

    # Mock the drawing_ingestor function
    mock_items = {
        "PT-101": Item(tag="PT-101", type="PT", bbox=(0, 0, 10, 10), conf=0.9)
    }
    mock_markdown = "| Tag | Type | Size | Confidence | Status |\n|-----|------|------|------------|--------|\n| PT-101 | PT |  | 90.00% | INGESTED |"

    with (
        patch("pid_parts.cli.asyncio.run") as mock_run,
        patch("builtins.open", mock_open()) as mock_file,
    ):

        # Set up the mock to return the expected result
        mock_run.return_value = {"items": mock_items, "markdown": mock_markdown}

        # Test with default output filename
        ingest(sample_pdf, True, None)

        # Verify file was opened with default filename (sample.md)
        expected_filename = f"{sample_pdf.rsplit('.', 1)[0]}.md"
        mock_file.assert_called_with(expected_filename, "w")
