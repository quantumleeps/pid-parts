"""
Drawing ingestion module for PID parts extraction.

This module handles the process of extracting parts information from PID drawings
using a multimodal LLM. It processes PDF drawings by:
1. Converting the PDF to an image
2. Slicing the image into overlapping tiles
3. Processing each tile with an LLM to detect parts
4. Combining the results into a unified state
"""

from __future__ import annotations
import asyncio, base64, json
from io import BytesIO
from typing import TypedDict

from langchain.schema import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from pid_parts.configure import app_settings
from pid_parts.markdown import render_md
from pid_parts.models import ingestor_llm
from pid_parts.state import Item, State
from pid_parts.tiler import pdf_page_to_image, slice_image

# System prompt that defines the LLM's role and expected output format
_SYSTEM = SystemMessage(
    content=(
        "You are an OCR-plus detector for process & instrumentation diagrams. "
        "Return ONLY valid JSON. Keys are tag strings; values are objects with "
        "fields: tag (string), type (string), size (string), bbox (list of 4 "
        "integers [x1, y1, x2, y2] representing the bounding box coordinates), "
        "conf (float)."
    )
)

# User prompt template for each image tile
_USER_TEXT = (
    "Detect every instrument, valve or line class in this tile. "
    "Return `{}` if none. BBox coords are ABSOLUTE pixels on the full page."
)

# Initialize the LLM with the configured model
_llm = ingestor_llm(app_settings.ingestion_model)


def _b64(pil_img) -> str:
    """Convert a PIL image to base64 encoded string.

    Args:
        pil_img: PIL Image object to convert

    Returns:
        Base64 encoded string representation of the image
    """
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


class IngestUpdate(TypedDict):
    """Type definition for the return value of drawing_ingestor."""

    items: dict[str, Item]
    markdown: str


async def drawing_ingestor(
    state: State,
    config: RunnableConfig,
) -> IngestUpdate:
    """Process a PDF drawing to extract PID parts information.

    This function orchestrates the entire ingestion process:
    1. Converts the PDF to an image
    2. Slices the image into tiles
    3. Processes each tile with the LLM in parallel
    4. Combines and normalizes the results
    5. Updates the state with detected items

    Args:
        state: The current application state to update with detected items
        config: Configuration containing the PDF path and other settings

    Returns:
        IngestUpdate containing the updated items dictionary and markdown
    """
    pdf_path: str = config["configurable"]["pdf_path"]

    # Convert the PDF to an image
    page_img = pdf_page_to_image(pdf_path)

    async def call(tile):
        """Process a single image tile with the LLM.

        Args:
            tile: A Tile object containing the image crop and position information

        Returns:
            Tuple of (JSON response content, original tile)
        """
        # Create a multimodal message with text prompt and image
        msg = HumanMessage(
            content=[
                {"type": "text", "text": _USER_TEXT},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64," + _b64(tile.crop),
                        "detail": "high",
                    },
                },
            ]
        )
        # Send the message to the LLM and await response
        resp = await _llm.ainvoke([_SYSTEM, msg])
        content = resp.content

        # Extract JSON from Markdown code block if needed
        # This handles cases where the LLM wraps JSON in markdown code blocks
        if content.startswith("```"):
            # Find the start and end of the JSON content
            if "```json" in content:
                start = content.find("```json") + 7
            elif "```" in content:
                start = content.find("```") + 3
            else:
                start = 0

            if "```" in content[start:]:
                end = content.rfind("```")
            else:
                end = len(content)

            content = content[start:end].strip()

        return content, tile

    # Process all tiles in parallel using asyncio.gather
    for raw, tile in await asyncio.gather(*(call(t) for t in slice_image(page_img))):
        try:
            # Parse the JSON response from the LLM
            json_data = json.loads(raw)
            for tag, det in json_data.items():
                try:
                    # Adjust bounding box coordinates to the full image
                    # by adding the tile's offset
                    x1, y1, x2, y2 = det["bbox"]
                    det["bbox"] = [
                        x1 + tile.x_off,
                        y1 + tile.y_off,
                        x2 + tile.x_off,
                        y2 + tile.y_off,
                    ]

                    # Data normalization: ensure all fields meet expected formats
                    # Ensure tag is a string
                    if det.get("tag") is None:
                        det["tag"] = f"unknown_{tag}"

                    # Ensure size is a string if it's a list
                    if "size" in det and isinstance(det["size"], list):
                        det["size"] = str(det["size"])

                    # Ensure conf is a float
                    if det.get("conf") is None:
                        det["conf"] = 0.5  # Default confidence value

                    # Create Item object and add to state
                    # Only keep items with higher confidence if duplicates exist
                    item = Item(**det, status="INGESTED")
                    if (tag not in state.items) or (item.conf > state.items[tag].conf):
                        state.items[tag] = item
                except Exception as e:
                    print(f"Error processing item {tag}: {e}")
                    continue
        except json.JSONDecodeError as e:
            # Handle cases where the LLM response isn't valid JSON
            print(f"Error decoding JSON: {e}")
            continue

    # Generate markdown representation of the items
    state.markdown = render_md(state.items)
    return {"items": state.items, "markdown": state.markdown}
