"""
Tests for the state management functionality.
"""

from pid_parts.state import Item, State


def test_item_defaults():
    """Test Item creation with defaults."""
    itm = Item(
        tag="PT-101", type="Pressure Transmitter", bbox=(0, 0, 10, 10), conf=0.99
    )
    assert itm.status == "INGESTED"
    assert itm.size is None


def test_state_initialization():
    """Test State initialization."""
    state = State()
    assert state.items == {}
    assert state.markdown == ""
    assert state.pending_questions == []


def test_state_item_management():
    """Test adding and updating items in State."""
    state = State()

    # Add an item
    item1 = Item(tag="PT-101", type="PT", bbox=(0, 0, 10, 10), conf=0.8)
    state.items["PT-101"] = item1

    assert "PT-101" in state.items
    assert state.items["PT-101"].conf == 0.8

    # Update with higher confidence
    item2 = Item(tag="PT-101", type="PT", bbox=(5, 5, 15, 15), conf=0.9)
    state.items["PT-101"] = item2

    assert state.items["PT-101"].conf == 0.9
    assert state.items["PT-101"].bbox == (5, 5, 15, 15)
