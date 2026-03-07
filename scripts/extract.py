import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_mock_data(output_dir: str):
    """Generates mock CSV data for Orders, Customers, and Products."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        num_customers = 100
        num_products = 50
        num_orders = 1000

        # 1. Generate Customers
        logger.info("Generating Customers data...")
        customer_ids = range(1, num_customers + 1)
        customers_df = pd.DataFrame({
            'customer_id': customer_ids,
            'name': [f'Customer_{i}' for i in customer_ids],
            'email': [f'customer_{i}@example.com' for i in customer_ids],
            'signup_date': pd.date_range(start='2023-01-01', periods=num_customers, freq='D')
        })
        customers_path = os.path.join(output_dir, 'customers.csv')
        customers_df.to_csv(customers_path, index=False)
        logger.info(f"Saved customers to {customers_path}")

        # 2. Generate Products
        logger.info("Generating Products data...")
        product_ids = range(1, num_products + 1)
        categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Toys']
        products_df = pd.DataFrame({
            'product_id': product_ids,
            'product_name': [f'Product_{i}' for i in product_ids],
            'category': np.random.choice(categories, num_products),
            'price': np.round(np.random.uniform(10.0, 500.0, num_products), 2)
        })
        products_path = os.path.join(output_dir, 'products.csv')
        products_df.to_csv(products_path, index=False)
        logger.info(f"Saved products to {products_path}")

        # 3. Generate Orders
        logger.info("Generating Orders data...")
        # Generate dates over the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Random dates between start and end
        random_dates = [start_date + timedelta(seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(num_orders)]

        orders_df = pd.DataFrame({
            'order_id': range(1, num_orders + 1),
            'customer_id': np.random.choice(customer_ids, num_orders),
            'product_id': np.random.choice(product_ids, num_orders),
            'order_date': random_dates,
            'quantity': np.random.randint(1, 5, num_orders)
        })
        orders_path = os.path.join(output_dir, 'orders.csv')
        orders_df.to_csv(orders_path, index=False)
        logger.info(f"Saved orders to {orders_path}")

        logger.info("Mock data generation completed successfully.")

    except Exception as e:
        logger.error(f"Error generating mock data: {str(e)}")
        raise

if __name__ == "__main__":
    # When running locally from the script dir, output goes to ../data/raw/
    # In airflow docker, it maps to /opt/airflow/data/raw/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.environ.get('RAW_DATA_DIR', os.path.join(current_dir, '..', 'data', 'raw'))
    generate_mock_data(output_dir)
