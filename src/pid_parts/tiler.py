"""
Image processing utilities for PDF documents.

This module handles the conversion of PDF documents to images and the
slicing of those images into overlapping tiles for processing by the
multimodal LLM.
"""

from pydantic import BaseModel
from typing import List

from pdf2image import convert_from_path
from PIL import Image

from pid_parts.constants import TILE_PX, OVERLAP, DPI


class Tile(BaseModel):
    """A square tile of an image with its offset coordinates.

    Represents a portion of a larger image along with metadata about
    its position in the original image, allowing for reconstruction
    and coordinate mapping.

    Attributes:
        crop: The actual image tile as a PIL Image
        x_off: X-coordinate offset (left pixel) on the full page
        y_off: Y-coordinate offset (top pixel) on the full page
    """

    crop: Image.Image
    x_off: int  # left pixel on full page
    y_off: int  # top pixel on full page

    model_config = {"arbitrary_types_allowed": True}


def pdf_page_to_image(pdf_path: str, dpi: int = DPI) -> Image.Image:
    """Convert the first page of a PDF to a PIL Image.

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for the conversion in dots per inch

    Returns:
        PIL Image object of the first page of the PDF

    Note:
        Only processes the first page of multi-page PDFs
    """
    return convert_from_path(pdf_path, dpi=dpi, fmt="png", thread_count=2)[0]


def slice_image(
    img: Image.Image,
    tile: int = TILE_PX,
    overlap: float = OVERLAP,
) -> List[Tile]:
    """Slice an image into overlapping square tiles.

    Creates a grid of overlapping tiles that completely cover the input image.
    The overlap helps ensure that elements that might be split across tile
    boundaries can still be properly detected.

    Args:
        img: The input image to slice
        tile: Size of each square tile in pixels
        overlap: Fraction of overlap between adjacent tiles (0.0-1.0)

    Returns:
        List of Tile objects containing image crops and their positions
    """
    # Calculate stride based on tile size and desired overlap
    stride = int(tile * (1 - overlap))
    tiles: list[Tile] = []

    # Generate tiles by moving across the image in a grid pattern
    for y in range(0, img.height, stride):
        for x in range(0, img.width, stride):
            # Create a crop, handling edge cases where tile would exceed image bounds
            crop = img.crop((x, y, min(x + tile, img.width), min(y + tile, img.height)))
            tiles.append(Tile(crop=crop, x_off=x, y_off=y))

    return tiles
