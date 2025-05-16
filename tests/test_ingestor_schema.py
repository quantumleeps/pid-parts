"""
Tests for the drawing ingestor schema with mocked LLM.
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock
from pid_parts.state import Item, State
from pid_parts.markdown import render_md


def test_sample_tile_response_structure(sample_tile_response):
    """Test that the sample tile response has the expected structure."""
    # Verify the sample response has the expected items
    assert "PT-101" in sample_tile_response
    assert "FT-102" in sample_tile_response
    assert "LT-103" in sample_tile_response
    assert "MOV-104" in sample_tile_response

    # Verify each item has the expected fields
    for tag, item in sample_tile_response.items():
        assert "tag" in item
        assert "type" in item
        assert "bbox" in item
        assert "conf" in item
        assert "status" in item

        # Verify bbox is a list of 4 integers
        assert len(item["bbox"]) == 4
        assert all(isinstance(coord, int) for coord in item["bbox"])


def test_render_md_with_sample_data(sample_tile_response):
    """Test rendering markdown with sample data."""
    # Convert sample data to Item objects
    items = {}
    for tag, data in sample_tile_response.items():
        items[tag] = Item(
            tag=data["tag"],
            type=data["type"],
            size=data["size"],
            bbox=tuple(data["bbox"]),
            conf=data["conf"],
            status=data["status"],
        )

    # Render markdown
    markdown = render_md(items)

    # Verify markdown contains all items
    for tag in sample_tile_response.keys():
        assert tag in markdown


@patch("pid_parts.drawing_ingestor.slice_image")
@patch("pid_parts.drawing_ingestor._llm")
def test_ingestor_with_sample_data(
    mock_llm, mock_slice_image, sample_tile_response, sample_pdf
):
    """Test drawing_ingestor with sample data."""
    from pid_parts.drawing_ingestor import drawing_ingestor

    # Create a mock tile
    mock_tile = MagicMock()
    mock_tile.x_off = 0
    mock_tile.y_off = 0
    mock_slice_image.return_value = [mock_tile]

    # Create a modified version of sample_tile_response without the status field
    # since it's added by default in the Item constructor
    modified_response = {}
    for tag, item_data in sample_tile_response.items():
        modified_response[tag] = {
            "tag": item_data["tag"],
            "type": item_data["type"],
            "size": item_data["size"],
            "bbox": item_data["bbox"],
            "conf": item_data["conf"],
        }

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = json.dumps(modified_response)

    # Set up the mock to return the response when ainvoke is called
    async def mock_ainvoke(*args, **kwargs):
        return mock_response

    mock_llm.ainvoke = mock_ainvoke

    # Create state and config
    state = State()
    config = {"configurable": {"pdf_path": sample_pdf}}

    # Run the ingestor
    result = asyncio.run(drawing_ingestor(state, config))

    # Verify the result contains expected keys
    assert "items" in result
    assert "markdown" in result

    # Verify items were added to state
    for tag in modified_response.keys():
        assert tag in result["items"]
        assert result["items"][tag].tag == modified_response[tag]["tag"]
        assert result["items"][tag].type == modified_response[tag]["type"]
        assert result["items"][tag].conf == modified_response[tag]["conf"]

        if modified_response[tag]["size"]:
            assert result["items"][tag].size == modified_response[tag]["size"]


@patch("pid_parts.drawing_ingestor.slice_image")
@patch("pid_parts.drawing_ingestor._llm")
def test_ingestor_json_extraction(mock_llm, mock_slice_image, sample_pdf):
    """Test JSON extraction from markdown code blocks."""
    from pid_parts.drawing_ingestor import drawing_ingestor

    # Create a mock tile
    mock_tile = MagicMock()
    mock_tile.x_off = 0
    mock_tile.y_off = 0
    mock_slice_image.return_value = [mock_tile]

    # Mock LLM response with markdown code block
    # Note: No indentation in the JSON content
    markdown_response = """```json
{"PIT-102": {"tag":"PIT-102","type":"PT","size":"2","bbox":[10,20,30,40],"conf":0.95}}
```"""
    mock_response = MagicMock()
    mock_response.content = markdown_response

    # Set up the mock to return the response when ainvoke is called
    async def mock_ainvoke(*args, **kwargs):
        return mock_response

    mock_llm.ainvoke = mock_ainvoke

    # Create state and config
    state = State()
    config = {"configurable": {"pdf_path": sample_pdf}}

    # Run the ingestor
    result = asyncio.run(drawing_ingestor(state, config))

    # Verify JSON was extracted correctly from markdown code block
    assert "PIT-102" in result["items"]
    assert result["items"]["PIT-102"].tag == "PIT-102"
    assert result["items"]["PIT-102"].type == "PT"
    assert result["items"]["PIT-102"].size == "2"
    assert result["items"]["PIT-102"].bbox == (10, 20, 30, 40)
    assert result["items"]["PIT-102"].conf == 0.95


@patch("pid_parts.drawing_ingestor.slice_image")
@patch("pid_parts.drawing_ingestor._llm")
def test_ingestor_error_handling(mock_llm, mock_slice_image, sample_pdf):
    """Test error handling for invalid JSON responses."""
    from pid_parts.drawing_ingestor import drawing_ingestor

    # Create a mock tile
    mock_tile = MagicMock()
    mock_tile.x_off = 0
    mock_tile.y_off = 0
    mock_slice_image.return_value = [mock_tile]

    # Mock LLM response with invalid JSON
    invalid_json = "This is not valid JSON"
    mock_response = MagicMock()
    mock_response.content = invalid_json

    # Set up the mock to return the response when ainvoke is called
    async def mock_ainvoke(*args, **kwargs):
        return mock_response

    mock_llm.ainvoke = mock_ainvoke

    # Create state and config
    state = State()
    config = {"configurable": {"pdf_path": sample_pdf}}

    # Run the ingestor
    result = asyncio.run(drawing_ingestor(state, config))

    # Verify the result contains expected keys
    assert "items" in result
    assert "markdown" in result

    # Items should be empty since JSON was invalid
    assert len(result["items"]) == 0
