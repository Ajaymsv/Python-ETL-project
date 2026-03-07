import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DataExtractor')

class DataExtractor:
    """Class responsible for generating and extracting mock e-commerce data."""

    def __init__(self, output_dir: str, num_customers: int = 500, num_products: int = 100, num_orders: int = 5000):
        self.output_dir = output_dir
        self.num_customers = num_customers
        self.num_products = num_products
        self.num_orders = num_orders
        self.fake = Faker()

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_customers(self) -> None:
        """Generates realistic customer data using Faker."""
        logger.info(f"Generating {self.num_customers} customers...")
        try:
            customers = []
            for i in range(1, self.num_customers + 1):
                customers.append({
                    'customer_id': i,
                    'name': self.fake.name(),
                    'email': self.fake.email(),
                    'segment': np.random.choice(['Retail', 'Wholesale', 'Corporate', 'Guest'], p=[0.6, 0.2, 0.1, 0.1]),
                    'signup_date': self.fake.date_between(start_date='-2y', end_date='today')
                })

            df = pd.DataFrame(customers)
            output_path = os.path.join(self.output_dir, 'customers.csv')
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved customers to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate customers: {e}")
            raise

    def generate_products(self) -> None:
        """Generates product data with realistic categories."""
        logger.info(f"Generating {self.num_products} products...")
        try:
            categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports & Outdoors', 'Beauty', 'Toys']
            products = []
            for i in range(1, self.num_products + 1):
                products.append({
                    'product_id': i,
                    'product_name': f"{self.fake.word().capitalize()} {self.fake.word().capitalize()}",
                    'category': np.random.choice(categories),
                    'price': round(np.random.uniform(5.0, 1000.0), 2)
                })

            df = pd.DataFrame(products)
            output_path = os.path.join(self.output_dir, 'products.csv')
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved products to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate products: {e}")
            raise

    def generate_orders(self, batch_size: int = 1000) -> None:
        """Generates order data and writes to CSV in batches to simulate large datasets."""
        logger.info(f"Generating {self.num_orders} orders in batches of {batch_size}...")
        try:
            output_path = os.path.join(self.output_dir, 'orders.csv')

            # Remove file if it exists
            if os.path.exists(output_path):
                os.remove(output_path)

            end_date = datetime.now()
            start_date = end_date - timedelta(days=365) # 1 year of data

            customer_ids = range(1, self.num_customers + 1)
            product_ids = range(1, self.num_products + 1)

            total_generated = 0
            while total_generated < self.num_orders:
                current_batch_size = min(batch_size, self.num_orders - total_generated)

                # Generate random dates for the batch
                random_dates = [start_date + timedelta(seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(current_batch_size)]

                batch_data = pd.DataFrame({
                    'order_id': range(total_generated + 1, total_generated + current_batch_size + 1),
                    'customer_id': np.random.choice(customer_ids, current_batch_size),
                    'product_id': np.random.choice(product_ids, current_batch_size),
                    'order_date': random_dates,
                    'quantity': np.random.randint(1, 10, current_batch_size) # 1 to 9 items
                })

                # Append to CSV
                header = total_generated == 0
                batch_data.to_csv(output_path, mode='a', index=False, header=header)

                total_generated += current_batch_size
                logger.info(f"Wrote batch of {current_batch_size} orders. Progress: {total_generated}/{self.num_orders}")

            logger.info(f"Successfully saved all orders to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate orders: {e}")
            raise

    def run_extraction(self) -> None:
        """Runs the full extraction process."""
        logger.info("Starting data extraction process...")
        self.generate_customers()
        self.generate_products()
        self.generate_orders()
        logger.info("Data extraction process completed successfully.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.environ.get('RAW_DATA_DIR', os.path.join(current_dir, '..', 'data', 'raw'))

    extractor = DataExtractor(output_dir=output_dir, num_customers=1000, num_products=200, num_orders=10000)
    extractor.run_extraction()
