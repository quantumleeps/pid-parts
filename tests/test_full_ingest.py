"""
Tests for the full ingestion process with real LLM calls.

These tests are marked as 'expensive' and will be skipped by default.
Run with `pytest -m expensive` to include them.
"""

import pytest
import asyncio
import os
import subprocess


@pytest.mark.expensive
def test_full_pdf_live(sample_pdf):
    """Test full PDF ingestion with live LLM calls."""
    from pid_parts.state import State
    from pid_parts.drawing_ingestor import drawing_ingestor

    state = State()
    config = {"configurable": {"pdf_path": sample_pdf}}

    result = asyncio.run(drawing_ingestor(state, config))

    # Basic sanity checks
    assert len(result["items"]) >= 4
    assert result["markdown"].startswith("| Tag |")

    # Verify some expected item types are present
    item_types = {item.type for item in result["items"].values()}
    assert len(item_types) >= 2  # Should detect at least 2 different types


@pytest.mark.expensive
def test_cli_end_to_end(sample_pdf, tmp_path):
    """Test CLI end-to-end with live LLM calls."""
    import subprocess
    import os

    output_file = os.path.join(tmp_path, "output.md")

    # Run the CLI command
    result = subprocess.run(
        [
            "poetry",
            "run",
            "pid-ingest",
            sample_pdf,
            "--save-markdown",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    # Check command succeeded
    assert result.returncode == 0

    # Check output file was created
    assert os.path.exists(output_file)

    # Check file content
    with open(output_file, "r") as f:
        content = f.read()
        assert "| Tag |" in content
        assert "| Type |" in content


@pytest.mark.expensive
def test_different_confidence_levels(sample_pdf):
    """Test that items are detected with varying confidence levels."""
    from pid_parts.state import State
    from pid_parts.drawing_ingestor import drawing_ingestor

    state = State()
    config = {"configurable": {"pdf_path": sample_pdf}}

    result = asyncio.run(drawing_ingestor(state, config))

    # Get confidence values
    confidence_values = [item.conf for item in result["items"].values()]

    # All confidence values should be between 0 and 1
    assert all(0 <= conf <= 1 for conf in confidence_values)
