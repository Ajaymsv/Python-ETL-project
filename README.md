# Python ETL Project

This project implements an end-to-end data pipeline to extract, transform, and load e-commerce sales data. The pipeline is orchestrated using Apache Airflow, uses Python and Pandas for data extraction/generation, and DuckDB for transformations and storage.

## Architecture

1. **Ingestion Layer**: A Python script (`scripts/extract.py`) generates mock e-commerce data (Customers, Products, Orders) and saves it as CSV files in the `data/raw/` directory.
2. **Transformation Layer**: A Python script (`scripts/transform.py`) connects to a local DuckDB instance, reads the raw CSV files, and executes SQL transformations (`sql/transform.sql`). It calculates:
   - **Daily Total Revenue**: The sum of all sales per day.
   - **Top 5 Selling Products Per Day**: The highest-grossing products for each day.
   The processed data is loaded into tables in the DuckDB database located at `data/processed/sales.db`.
3. **Orchestration**: Apache Airflow (`dags/sales_pipeline.py`) schedules and stitches together the ingestion and transformation steps.
4. **Infrastructure**: The stack runs in Docker using `docker-compose`.
5. **CI/CD**: A GitHub Actions workflow runs unit tests on the transformation logic (`tests/test_transform.py`) for every pull request to ensure data quality.

## Project Structure

```
├── dags/                  # Airflow DAGs
│   └── sales_pipeline.py
├── scripts/               # Python scripts for extract and transform
│   ├── extract.py
│   └── transform.py
├── sql/                   # SQL scripts for transformation
│   └── transform.sql
├── data/                  # Local data storage (mounted to Airflow)
│   ├── raw/               # Raw CSV files
│   └── processed/         # Processed DuckDB database
├── tests/                 # Unit tests
│   └── test_transform.py
├── .github/workflows/     # CI/CD configurations
│   └── ci.yml
├── Dockerfile             # Custom Airflow image with dependencies
├── docker-compose.yml     # Docker Compose for Airflow and Postgres
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Prerequisites

- Docker and Docker Compose installed on your system.
- Python 3.10+ (for local development and testing).

## How to Run the Pipeline Locally

1. **Build and start the Docker containers:**
   ```bash
   docker-compose up -d --build
   ```

2. **Access the Airflow Web UI:**
   - Open your browser and navigate to `http://localhost:8080`.
   - Log in with the default credentials:
     - Username: `airflow`
     - Password: `airflow`

3. **Run the DAG:**
   - In the Airflow UI, locate the `sales_pipeline` DAG.
   - Unpause it using the toggle on the left.
   - Trigger it manually using the "Trigger DAG" play button.

4. **Verify the Results:**
   - Wait for the tasks to complete successfully.
   - The raw data will be populated in `./data/raw/`.
   - The processed data will be saved in a DuckDB database at `./data/processed/sales.db`.
   - You can connect to this database using the DuckDB CLI or a Python script to query the `daily_revenue` and `top_products_per_day` tables.

## Running Tests Locally

To run the unit tests, ensure you have installed the required dependencies, then run `pytest`:

```bash
pip install -r requirements.txt
pytest tests/
```
