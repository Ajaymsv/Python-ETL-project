import pytest
import pandas as pd
import os
import shutil
from src.etl import SalesETL

# Sample configuration for testing
TEST_CONFIG = {
    'paths': {
        'input': 'tests/test_input.csv',
        'output': 'tests/test_output.csv'
    },
    'logging': {
        'level': 'DEBUG',
        'file': 'tests/test_etl.log'
    },
    'transform': {
        'critical_columns': ['order_id', 'date', 'product_id', 'quantity', 'price']
    }
}

@pytest.fixture
def etl_instance(tmp_path):
    # Create a temporary config file
    config_path = tmp_path / "test_config.yaml"
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(TEST_CONFIG, f)

    etl = SalesETL(str(config_path))
    return etl

def test_transform_valid_data(etl_instance):
    # Create sample DataFrame
    data = {
        'order_id': [1, 2],
        'date': ['2023-10-01', '2023/10/02'],
        'product_id': ['P1', 'P2'],
        'quantity': [2, 1],
        'price': [10.0, 20.0],
        'customer_id': ['C1', 'C2']
    }
    df = pd.DataFrame(data)

    transformed_df = etl_instance.transform(df)

    # Check assertions
    assert len(transformed_df) == 2
    assert 'total_amount' in transformed_df.columns
    assert transformed_df.iloc[0]['total_amount'] == 20.0
    assert transformed_df.iloc[1]['total_amount'] == 20.0
    assert transformed_df.iloc[1]['date'] == '2023-10-02' # ISO format check

def test_transform_missing_critical_fields(etl_instance):
    # Data with missing values
    data = {
        'order_id': [1, 2],
        'date': ['2023-10-01', '2023-10-02'],
        'product_id': ['P1', None], # Missing product_id
        'quantity': [2, 1],
        'price': [10.0, 20.0]
    }
    df = pd.DataFrame(data)

    transformed_df = etl_instance.transform(df)

    # Should drop the second row
    assert len(transformed_df) == 1
    assert transformed_df.iloc[0]['order_id'] == 1

def test_transform_missing_columns(etl_instance):
    # Data missing a whole column (e.g. price)
    data = {
        'order_id': [1],
        'date': ['2023-10-01'],
        'product_id': ['P1'],
        'quantity': [2]
        # price is missing
    }
    df = pd.DataFrame(data)

    with pytest.raises(ValueError):
        etl_instance.transform(df)
