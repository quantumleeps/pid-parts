"""
Tests for the markdown generation functionality.
"""

from pid_parts.state import Item


def test_render_md_empty():
    """Test rendering markdown with empty items."""
    from pid_parts.markdown import render_md

    result = render_md({})
    assert result == ""


def test_render_md_single_item():
    """Test rendering markdown with a single item."""
    from pid_parts.markdown import render_md

    items = {
        "PT-101": Item(
            tag="PT-101",
            type="Pressure Transmitter",
            size='2"',
            bbox=(10, 20, 30, 40),
            conf=0.95,
        )
    }

    result = render_md(items)
    assert "| PT-101 |" in result
    assert "| Pressure Transmitter |" in result
    assert '| 2" |' in result
    assert "| 95.00% |" in result
    assert "| INGESTED |" in result


def test_render_md_multiple_items():
    """Test rendering markdown with multiple items."""
    from pid_parts.markdown import render_md

    items = {
        "PT-101": Item(tag="PT-101", type="PT", bbox=(10, 20, 30, 40), conf=0.95),
        "FT-102": Item(tag="FT-102", type="FT", bbox=(50, 60, 70, 80), conf=0.85),
        "LT-103": Item(
            tag="LT-103", type="LT", size='3"', bbox=(90, 100, 110, 120), conf=0.75
        ),
    }

    result = render_md(items)

    # Verify sorting by tag
    lines = result.split("\n")
    assert "FT-102" in lines[2]  # First item after header
    assert "LT-103" in lines[3]  # Second item
    assert "PT-101" in lines[4]  # Third item
