import pytest
import os
import duckdb
import pandas as pd
from scripts.transform import DataTransformer
from scripts.extract import DataExtractor

@pytest.fixture
def mock_data_dir(tmp_path):
    # Create mock raw data
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    # Simple test data
    customers_df = pd.DataFrame({
        'customer_id': [1, 2],
        'name': ['Alice', 'Bob'],
        'email': ['alice@test.com', 'bob@test.com'],
        'segment': ['Retail', 'Corporate'],
        'signup_date': ['2023-01-01', '2023-02-01']
    })
    customers_df.to_csv(raw_dir / "customers.csv", index=False)

    orders_df = pd.DataFrame({
        'order_id': [1, 2, 3],
        'customer_id': [1, 2, 1],
        'product_id': [101, 102, 101],
        'order_date': ['2023-10-01', '2023-10-01', '2023-10-02'],
        'quantity': [2, 1, 3]
    })
    orders_df.to_csv(raw_dir / "orders.csv", index=False)

    products_df = pd.DataFrame({
        'product_id': [101, 102],
        'product_name': ['Laptop', 'Mouse'],
        'category': ['Electronics', 'Electronics'],
        'price': [1000.0, 50.0]
    })
    products_df.to_csv(raw_dir / "products.csv", index=False)

    return str(raw_dir)

@pytest.fixture
def mock_sql_file():
    return os.path.join(os.path.dirname(__file__), '..', 'sql', 'transform.sql')

def test_daily_revenue_transformation(mock_data_dir, tmp_path, mock_sql_file):
    db_path = str(tmp_path / "test.db")

    # Initialize and run transformer
    transformer = DataTransformer(db_path, mock_data_dir, mock_sql_file)
    transformer.process()

    # Connect and verify
    con = duckdb.connect(db_path)

    # 2023-10-01: (2 * 1000) + (1 * 50) = 2050
    # 2023-10-02: (3 * 1000) = 3000
    res = con.execute("SELECT * FROM daily_revenue ORDER BY order_date ASC").df()

    assert len(res) == 2
    assert res.iloc[0]['total_revenue'] == 2050.0
    assert res.iloc[1]['total_revenue'] == 3000.0
    con.close()

def test_top_products_transformation(mock_data_dir, tmp_path, mock_sql_file):
    db_path = str(tmp_path / "test.db")

    # Initialize and run transformer
    transformer = DataTransformer(db_path, mock_data_dir, mock_sql_file)
    transformer.process()

    # Connect and verify
    con = duckdb.connect(db_path)

    res = con.execute("SELECT * FROM top_products_per_day ORDER BY order_date ASC, rank ASC").df()

    assert len(res) == 3
    # 2023-10-01: Laptop (2000), Mouse (50)
    assert res.iloc[0]['product_id'] == 101
    assert res.iloc[0]['total_sales'] == 2000.0
    assert res.iloc[0]['rank'] == 1

    assert res.iloc[1]['product_id'] == 102
    assert res.iloc[1]['total_sales'] == 50.0
    assert res.iloc[1]['rank'] == 2

    # 2023-10-02: Laptop (3000)
    assert res.iloc[2]['product_id'] == 101
    assert res.iloc[2]['total_sales'] == 3000.0
    assert res.iloc[2]['rank'] == 1
    con.close()

def test_clv_transformation(mock_data_dir, tmp_path, mock_sql_file):
    db_path = str(tmp_path / "test.db")

    # Initialize and run transformer
    transformer = DataTransformer(db_path, mock_data_dir, mock_sql_file)
    transformer.process()

    # Connect and verify
    con = duckdb.connect(db_path)

    res = con.execute("SELECT * FROM customer_lifetime_value_per_segment ORDER BY segment ASC").df()

    # Alice (Retail): 2 * 1000 + 3 * 1000 = 5000
    # Bob (Corporate): 1 * 50 = 50
    assert len(res) == 2

    # Check Corporate
    assert res.iloc[0]['segment'] == 'Corporate'
    assert res.iloc[0]['average_clv'] == 50.0
    assert res.iloc[0]['total_revenue'] == 50.0

    # Check Retail
    assert res.iloc[1]['segment'] == 'Retail'
    assert res.iloc[1]['average_clv'] == 5000.0
    assert res.iloc[1]['total_revenue'] == 5000.0

    con.close()

def test_data_quality_warning(mock_data_dir, tmp_path, mock_sql_file, caplog):
    db_path = str(tmp_path / "test.db")

    # Intentionally insert bad data into orders
    bad_orders_df = pd.DataFrame({
        'order_id': [4],
        'customer_id': [1],
        'product_id': [101],
        'order_date': ['2023-10-03'],
        'quantity': [-5] # Invalid quantity
    })
    bad_orders_df.to_csv(os.path.join(mock_data_dir, "orders.csv"), mode='a', index=False, header=False)

    transformer = DataTransformer(db_path, mock_data_dir, mock_sql_file)
    transformer.process()

    # Check that warning was logged
    assert "Data Quality Warning: Found 1 orders with zero or negative quantity." in caplog.text
