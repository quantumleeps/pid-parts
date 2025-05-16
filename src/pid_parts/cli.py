"""
Command-line interface for PID parts extraction.

This module provides the command-line entry points for the PID parts
extraction functionality, allowing users to process PDF drawings and
extract parts information.

Usage examples:
    ▶  poetry run pid-ingest sample.pdf
    ▶  poetry run pid-ingest sample.pdf --save-markdown
    ▶  poetry run pid-ingest sample.pdf -m --output custom_name.md
"""

import asyncio
import json

import typer

from pid_parts.drawing_ingestor import drawing_ingestor
from pid_parts.state import State

# Create a Typer app with help text shown when no arguments are provided
app = typer.Typer(no_args_is_help=True)


@app.command()
def ingest(
    pdf: str,
    save_markdown: bool = typer.Option(
        False, "--save-markdown", "-m", help="Save the generated markdown to a file"
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output filename for the markdown (default: <pdf_name>.md)",
    ),
):
    """Extract parts list from a PDF drawing.

    Processes the provided PDF file to identify and extract information about
    parts, instruments, valves, and line classes. The results are printed as
    JSON to stdout and can optionally be saved as a Markdown table.

    Args:
        pdf: Path to the PDF file to process
        save_markdown: Whether to save the generated markdown to a file
        output: Custom filename for the markdown output
    """
    # Initialize the application state
    state = State()

    # Configure the ingestion process with the PDF path
    config = {"configurable": {"pdf_path": pdf}}

    # Run the drawing ingestion process
    res = asyncio.run(drawing_ingestor(state, config))

    # Print the extracted items as JSON to stdout
    print(json.dumps({k: v.model_dump() for k, v in res["items"].items()}, indent=2))

    # If save_markdown flag is set, save the markdown to a file
    if save_markdown:
        # Use the provided output filename or generate one based on the PDF name
        output_file = output or f"{pdf.rsplit('.', 1)[0]}.md"

        # Write the markdown to the file
        with open(output_file, "w") as f:
            f.write(res["markdown"])

        # Inform the user where the markdown was saved
        print(f"Markdown saved to {output_file}")


if __name__ == "__main__":
    app()
