import duckdb
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DataTransformer')

class DataTransformer:
    """Class responsible for validating and transforming the e-commerce data."""

    def __init__(self, db_path: str, raw_dir: str, sql_file: str):
        self.db_path = db_path
        self.raw_dir = raw_dir
        self.sql_file = sql_file
        self.con: Optional[duckdb.DuckDBPyConnection] = None

        # Ensure processed directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self) -> None:
        """Establishes a connection to the DuckDB instance."""
        try:
            logger.info(f"Connecting to DuckDB at {self.db_path}")
            self.con = duckdb.connect(self.db_path)
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB: {e}")
            raise

    def close(self) -> None:
        """Closes the connection to the DuckDB instance."""
        if self.con:
            self.con.close()
            logger.info("DuckDB connection closed.")

    def run_data_quality_checks(self) -> None:
        """Runs basic data quality checks on the raw CSV data."""
        if not self.con:
            raise ConnectionError("No DuckDB connection established.")

        logger.info("Running Data Quality Checks...")
        try:
            # 1. Check for null primary keys in customers
            null_customers = self.con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{self.raw_dir}/customers.csv') WHERE customer_id IS NULL;").fetchone()[0]
            if null_customers > 0:
                logger.warning(f"Data Quality Warning: Found {null_customers} customers with NULL customer_id.")

            # 2. Check for null primary keys in products
            null_products = self.con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{self.raw_dir}/products.csv') WHERE product_id IS NULL;").fetchone()[0]
            if null_products > 0:
                logger.warning(f"Data Quality Warning: Found {null_products} products with NULL product_id.")

            # 3. Check for null primary keys in orders
            null_orders = self.con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{self.raw_dir}/orders.csv') WHERE order_id IS NULL;").fetchone()[0]
            if null_orders > 0:
                logger.warning(f"Data Quality Warning: Found {null_orders} orders with NULL order_id.")

            # 4. Check for negative or zero quantities
            invalid_qty = self.con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{self.raw_dir}/orders.csv') WHERE quantity <= 0;").fetchone()[0]
            if invalid_qty > 0:
                logger.warning(f"Data Quality Warning: Found {invalid_qty} orders with zero or negative quantity.")
                # We could raise an exception here if we wanted the pipeline to strictly fail
                # raise ValueError(f"Found {invalid_qty} orders with zero or negative quantity.")
            else:
                logger.info("All Data Quality Checks passed.")

        except Exception as e:
            logger.error(f"Error during Data Quality Checks: {e}")
            raise

    def execute_transformations(self) -> None:
        """Executes SQL transformations to generate business metrics."""
        if not self.con:
            raise ConnectionError("No DuckDB connection established.")

        try:
            # Read the SQL file
            with open(self.sql_file, 'r') as file:
                sql_script = file.read()

            # Replace template placeholders
            sql_script = sql_script.replace('{{ RAW_DIR }}', self.raw_dir)

            # Split SQL statements if necessary and execute them
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]

            logger.info(f"Running transformations from {self.sql_file}...")

            # Idempotent cleanup before running
            self.con.execute("DROP TABLE IF EXISTS daily_revenue;")
            self.con.execute("DROP TABLE IF EXISTS top_products_per_day;")
            self.con.execute("DROP TABLE IF EXISTS customer_lifetime_value_per_segment;")

            for statement in statements:
                if statement:
                    self.con.execute(statement)

            logger.info("Transformations completed successfully.")

            # Verify the data was loaded by printing some row counts
            rev_count = self.con.execute("SELECT COUNT(*) FROM daily_revenue").fetchone()[0]
            top_count = self.con.execute("SELECT COUNT(*) FROM top_products_per_day").fetchone()[0]
            clv_count = self.con.execute("SELECT COUNT(*) FROM customer_lifetime_value_per_segment").fetchone()[0]
            logger.info(f"Inserted {rev_count} rows into daily_revenue")
            logger.info(f"Inserted {top_count} rows into top_products_per_day")
            logger.info(f"Inserted {clv_count} rows into customer_lifetime_value_per_segment")

        except Exception as e:
            logger.error(f"Error during transformation execution: {e}")
            raise

    def process(self) -> None:
        """Main method to orchestrate the validation and transformation process."""
        try:
            self.connect()
            self.run_data_quality_checks()
            self.execute_transformations()
        finally:
            self.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = os.environ.get('DUCKDB_PATH', os.path.join(current_dir, '..', 'data', 'processed', 'sales.db'))
    raw_dir = os.environ.get('RAW_DATA_DIR', os.path.join(current_dir, '..', 'data', 'raw'))
    sql_file = os.environ.get('SQL_FILE_PATH', os.path.join(current_dir, '..', 'sql', 'transform.sql'))

    transformer = DataTransformer(db_path=db_path, raw_dir=raw_dir, sql_file=sql_file)
    transformer.process()
