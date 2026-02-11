# Scan Lab Analysis

Barcode scan timing analysis for classifying compliant and non-compliant scanning behavior.

## Purpose

This repository analyzes barcode scan timing data to:

- Classify scanning behavior as compliant or non-compliant based on timing patterns
- Detect anomalous timing patterns within compliant behavior
- Identify clustering and pause structures in scan sequences

The analysis uses only scan timing patterns and does not evaluate barcode correctness or workflow logic.

## Setup

### Using Dev Container (Recommended)

1. Open this repository in VS Code
2. When prompted, click "Reopen in Container"
3. The container will automatically install Poetry and all dependencies
4. Wait for the post-create command to complete

### Manual Setup with Poetry

If not using the dev container:

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Project Structure

```
scan-lab-analysis/
├── data/
│   ├── raw/           # Raw CSV files from scan capture tool
│   ├── interim/       # Intermediate processing artifacts
│   └── processed/     # Final processed datasets (Parquet)
├── notebooks/         # Jupyter notebooks for analysis
├── prompts/           # Analysis prompts and specifications
├── figures/           # Generated visualizations
├── reports/           # Analysis reports and summaries
├── src/               # Python modules for data processing
└── tests/             # Test suite for validation logic
```

## Usage

### Start Jupyter Lab

```bash
poetry run jupyter lab
```

This will start Jupyter Lab on port 8888. The server will open in your browser automatically.

### Run Tests

```bash
poetry run pytest
```

### Add Dependencies

```bash
poetry add <package-name>
```

## Data Schema

See [prompts/10_data_schema.prompt.txt](prompts/10_data_schema.prompt.txt) for the complete data schema specification.

Each row represents one scan event with:
- Experiment metadata (ID, user, scan style, cluster size)
- Timing data (timestamp, delta, elapsed time)
- Scan sequence information (scan index)
- Barcode value

## Analysis Workflow

1. **Data Loading** - Load raw CSV files and validate against schema
2. **Data Processing** - Transform and consolidate into Parquet format
3. **Exploratory Analysis** - Interactive notebooks for pattern discovery
4. **Classification** - Identify compliant vs non-compliant behavior
5. **Anomaly Detection** - Flag unusual timing patterns

## Development

This project uses:
- **Poetry** for dependency management
- **Python 3.12** as the target version
- **Ruff** for linting and formatting
- **pytest** for testing
- **Jupyter Lab** for interactive analysis

Code formatting and linting run automatically on save when using the dev container.