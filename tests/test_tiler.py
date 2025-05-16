"""
Tests for the PDF processing and tiling functionality.
"""

import numpy as np
from PIL import Image
import pytest

from pid_parts.constants import TILE_PX, OVERLAP, DPI
from pid_parts.tiler import pdf_page_to_image, slice_image


def test_slice_and_reconstruct(sample_pdf):
    """Test that slicing and reconstructing an image preserves all pixels."""
    img = pdf_page_to_image(sample_pdf, dpi=DPI)
    tiles = slice_image(img, tile=TILE_PX, overlap=OVERLAP)

    recon = Image.new("RGB", img.size)
    for t in tiles:
        recon.paste(t.crop, (t.x_off, t.y_off))

    assert np.array_equal(np.asarray(img), np.asarray(recon))


def test_slice_image_parameters():
    """Test slice_image with different parameters."""
    # Create a test image
    img = Image.new("RGB", (1000, 800), color="white")

    # Test with different tile sizes
    tiles_large = slice_image(img, tile=500, overlap=0.1)
    tiles_small = slice_image(img, tile=200, overlap=0.1)

    assert len(tiles_large) < len(tiles_small)

    # Test with different overlap percentages
    tiles_low_overlap = slice_image(img, tile=300, overlap=0.05)
    tiles_high_overlap = slice_image(img, tile=300, overlap=0.3)

    assert len(tiles_low_overlap) < len(tiles_high_overlap)


def test_tile_coordinates():
    """Test that tile coordinates are correctly calculated."""
    img = Image.new("RGB", (1000, 800), color="white")

    # No overlap case
    tiles = slice_image(img, tile=500, overlap=0)

    # Should have 4 tiles for a 1000x800 image with 500px tiles
    assert len(tiles) == 4

    # Check coordinates of each tile
    expected_coords = [(0, 0), (500, 0), (0, 500), (500, 500)]
    for tile, (exp_x, exp_y) in zip(tiles, expected_coords):
        assert tile.x_off == exp_x
        assert tile.y_off == exp_y
