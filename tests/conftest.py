"""
Global pytest fixtures and configuration.
"""

import pytest
import json
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "expensive: runs the real vision LLM or hits the network"
    )


@pytest.fixture
def sample_pdf():
    """Return path to the sample PDF for testing."""
    return str(Path(__file__).parent / "test_sample.pdf")


@pytest.fixture
def sample_tile_response():
    """Return sample tile response data for testing."""
    response_path = (
        Path(__file__).parent / "fixtures" / "sample_responses" / "tile_response.json"
    )
    with open(response_path, "r") as f:
        return json.load(f)
