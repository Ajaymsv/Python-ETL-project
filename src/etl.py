import pandas as pd
import logging
import os
from .utils import load_config, setup_logging

class SalesETL:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config)
        self.logger.info("ETL process initialized.")

    def extract(self):
        """Extracts data from the configured input CSV file."""
        input_path = self.config['paths']['input']
        self.logger.info(f"Extracting data from {input_path}")

        if not os.path.exists(input_path):
            self.logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}")

        try:
            df = pd.read_csv(input_path)
            self.logger.info(f"Extracted {len(df)} rows.")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting data: {e}")
            raise

    def transform(self, df):
        """
        Cleans and transforms the data.
        - Removes rows with missing critical fields.
        - Standardizes date format.
        - Calculates total amount.
        """
        self.logger.info("Starting transformation.")

        initial_count = len(df)

        # 1. Validation & Cleaning: Drop rows with missing critical fields
        critical_cols = self.config['transform']['critical_columns']

        # Check if critical columns exist in the dataframe
        missing_cols = [col for col in critical_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing critical columns in input data: {missing_cols}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        df_clean = df.dropna(subset=critical_cols).copy()
        dropped_count = initial_count - len(df_clean)

        if dropped_count > 0:
            self.logger.warning(f"Dropped {dropped_count} rows due to missing values in critical columns.")

        # 2. Formatting: Standardize date strings to ISO format
        try:
            # parsing with mixed formats can be tricky, to_datetime is generally smart
            df_clean['date'] = pd.to_datetime(df_clean['date'], format='mixed').dt.strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Error parsing dates: {e}")
            raise

        # 3. Calculation: Create total_amount = quantity * price
        try:
            df_clean['total_amount'] = df_clean['quantity'] * df_clean['price']
        except Exception as e:
            self.logger.error(f"Error calculating total_amount: {e}")
            raise

        self.logger.info(f"Transformation complete. Resulting rows: {len(df_clean)}")
        return df_clean

    def load(self, df):
        """Loads the processed data to the configured output CSV file."""
        output_path = self.config['paths']['output']
        self.logger.info(f"Loading data to {output_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            df.to_csv(output_path, index=False)
            self.logger.info("Data loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise

    def run(self):
        """Runs the full ETL pipeline."""
        self.logger.info("Starting ETL pipeline execution.")
        try:
            data = self.extract()
            processed_data = self.transform(data)
            self.load(processed_data)
            self.logger.info("ETL pipeline execution completed successfully.")
        except Exception as e:
            self.logger.critical(f"ETL pipeline failed: {e}")
            raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Sales ETL Pipeline")
    parser.add_argument("--config", default="config/config.yaml", help="Path to configuration file")
    args = parser.parse_args()

    etl = SalesETL(args.config)
    etl.run()
