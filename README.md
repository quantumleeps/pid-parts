# PID Parts

Convert Process & Instrumentation Diagram (P&ID) PDFs to a Markdown parts list.

## Description

PID Parts is a tool that uses OCR and AI to extract information from P&ID diagrams in PDF format. It identifies instruments, valves, and line classes, and generates a structured parts list in both JSON and Markdown formats.

## Installation

```bash
# Clone the repository
git clone https://github.com/quantumleeps/pid-parts.git
cd pid-parts

# Install with Poetry
poetry install
```

## Usage

### Basic Usage

```bash
# Process a PDF and output JSON to stdout
poetry run pid-ingest sample.pdf
```

### Save Markdown Output

```bash
# Process a PDF and save the markdown to a file (default: <pdf_name>.md)
poetry run pid-ingest sample.pdf --save-markdown

# Specify a custom output filename
poetry run pid-ingest sample.pdf -m --output custom_name.md
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--save-markdown` | `-m` | Save the generated markdown to a file |
| `--output` | `-o` | Output filename for the markdown (default: `<pdf_name>.md`) |

## How It Works

1. The tool takes a P&ID PDF as input
2. It converts the PDF to an image and slices it into tiles
3. Each tile is processed using AI vision to detect components
4. The results are combined, deduplicated, and formatted
5. Output is provided as JSON (to stdout) and optionally as a Markdown table

## Features

- Extract instruments, valves, and line classes from P&ID PDFs
- Generate a structured parts list in JSON format
- Create a formatted Markdown table of detected components
- Deduplicate items based on tag names and confidence scores

## Data Model

The tool extracts the following information for each component:

| Field | Type | Description |
|-------|------|-------------|
| `tag` | string | The component tag (e.g., PT-101) |
| `type` | string | The component type (e.g., PT, FT, MOV) |
| `size` | string | The component size (if available) |
| `bbox` | tuple | Bounding box coordinates (x1, y1, x2, y2) |
| `conf` | float | Confidence score (0.0 to 1.0) |
| `status` | string | Processing status (e.g., "INGESTED") |

## Configuration

The tool uses environment variables for configuration. Copy `.env.example` to `.env` and adjust as needed:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OPENROUTER_API_KEY` | API key for OpenRouter | (required) |
| `OPENROUTER_BASE_URL` | Base URL for OpenRouter API | https://openrouter.ai/api/v1 |
| `INGESTION_MODEL` | Model name for the ingestion process | google/gemini-2.0-flash-lite-001 |

## Technical Details

### Tiling Process

The PDF is converted to an image and sliced into tiles of 1200x1200 pixels with a 15% overlap. This tiling approach helps improve detection accuracy for components that might be split across tile boundaries.

### Markdown Format

The generated markdown table includes the following columns:
- Tag
- Type
- Size
- Confidence (as percentage)
- Status

### JSON Output

The JSON output includes all detected components with their full details, including bounding box coordinates.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run only non-expensive tests (excludes tests that make real LLM calls)
python -m pytest -m "not expensive"

# Run only expensive tests (includes tests that make real LLM calls)
python -m pytest -m "expensive"
```

## License

MIT
