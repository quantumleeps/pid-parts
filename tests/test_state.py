# tests/test_state.py
from pid_parts.state import Item


def test_item_defaults():
    itm = Item(
        tag="PT-101", type="Pressure Transmitter", bbox=(0, 0, 10, 10), conf=0.99
    )
    assert itm.status == "INGESTED"
