# Retail Sales ETL Pipeline

This project implements a robust, production-style Extract, Transform, Load (ETL) pipeline for retail sales data using Python and Pandas.

## Project Structure

- `src/`: Source code for the ETL pipeline.
  - `etl.py`: Main ETL logic (Extraction, Transformation, Loading).
  - `utils.py`: Utility functions for configuration and logging.
- `config/`: Configuration files.
  - `config.yaml`: Centralized configuration for paths, logging, and validation rules.
- `data/`: Data storage.
  - `input/`: Raw input data (e.g., `sales_data.csv`).
  - `output/`: Processed output data.
- `tests/`: Unit tests using `pytest`.

## Prerequisites

- Python 3.8+
- pip

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the ETL pipeline:

```bash
python src/etl.py --config config/config.yaml
```

The pipeline will:
1. Read the input CSV file defined in `config.yaml`.
2. Validate and clean the data (remove rows with missing critical fields).
3. Standardize date formats to ISO 8601.
4. Calculate the `total_amount` for each transaction.
5. Save the processed data to the output directory.
6. Log execution details to `etl.log` and the console.

## Running Tests

To run the unit tests:

```bash
pytest
```

## Configuration

The pipeline is fully configurable via `config/config.yaml`. You can modify:
- Input/Output file paths.
- Logging levels and formats.
- Critical columns required for data validation.
