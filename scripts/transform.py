import duckdb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_transformations(db_path: str, raw_dir: str, sql_file: str):
    """Executes SQL transformations using DuckDB."""
    try:
        logger.info(f"Connecting to DuckDB at {db_path}")
        # Create processed dir if it doesn't exist to store db
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connect to DuckDB instance
        con = duckdb.connect(db_path)

        # Read the SQL file
        with open(sql_file, 'r') as file:
            sql_script = file.read()

        # Replace template placeholders
        sql_script = sql_script.replace('{{ RAW_DIR }}', raw_dir)

        # Split SQL statements if necessary and execute them
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]

        logger.info(f"Running transformations from {sql_file}")

        # In a real ETL, we might TRUNCATE or DROP tables before reloading them
        # to ensure idempotent operations.
        con.execute("DROP TABLE IF EXISTS daily_revenue;")
        con.execute("DROP TABLE IF EXISTS top_products_per_day;")

        for statement in statements:
            con.execute(statement)

        logger.info("Transformations completed successfully.")

        # Verify the data was loaded by printing some row counts
        rev_count = con.execute("SELECT COUNT(*) FROM daily_revenue").fetchone()[0]
        top_count = con.execute("SELECT COUNT(*) FROM top_products_per_day").fetchone()[0]
        logger.info(f"Inserted {rev_count} rows into daily_revenue")
        logger.info(f"Inserted {top_count} rows into top_products_per_day")

    except Exception as e:
        logger.error(f"Error during transformation: {str(e)}")
        raise
    finally:
        if 'con' in locals():
            con.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = os.environ.get('DUCKDB_PATH', os.path.join(current_dir, '..', 'data', 'processed', 'sales.db'))
    raw_dir = os.environ.get('RAW_DATA_DIR', os.path.join(current_dir, '..', 'data', 'raw'))
    sql_file = os.environ.get('SQL_FILE_PATH', os.path.join(current_dir, '..', 'sql', 'transform.sql'))

    run_transformations(db_path, raw_dir, sql_file)
