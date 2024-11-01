import pytest
import pandas as pd
import numpy as np
from utils.data_processor import BMRSDataProcessor

@pytest.fixture
def sample_raw_data():
    """Create sample raw data for testing"""
    dates = pd.date_range(
        start='2024-03-01',
        periods=48,  # One day of half-hourly periods
        freq='30min'
    )
    
    data = {
        'timestamp': dates,
        'systemSellPrice': np.random.uniform(80, 90, 48),
        'systemBuyPrice': np.random.uniform(90, 100, 48),
        'netImbalanceVolume': np.random.uniform(-1000, 1000, 48)
    }
    
    # Insert some missing values
    data['systemSellPrice'][5] = np.nan
    data['systemBuyPrice'][6] = np.nan
    data['netImbalanceVolume'][7] = np.nan
    
    return pd.DataFrame(data)

def test_clean_and_process_data(sample_raw_data):
    """Test basic data cleaning and processing"""
    prices_df, volumes_df = BMRSDataProcessor.clean_and_process_data(sample_raw_data)
    
    # Check basic structure
    assert len(prices_df) == len(sample_raw_data)
    assert len(volumes_df) == len(sample_raw_data)
    
    # Check columns
    assert all(col in prices_df.columns for col in ['timestamp', 'system_sell_price', 'system_buy_price', 'price_spread', 'price_quality'])
    assert all(col in volumes_df.columns for col in ['timestamp', 'net_imbalance_volume', 'abs_imbalance_volume', 'volume_quality'])

def test_interpolation(sample_raw_data):
    """Test that interpolation works correctly"""
    prices_df, volumes_df = BMRSDataProcessor.clean_and_process_data(sample_raw_data)
    
    # Check interpolated values are flagged
    assert (prices_df['price_quality'] == 'Interpolated').any()
    assert (volumes_df['volume_quality'] == 'Interpolated').any()

def test_data_quality_summary(sample_raw_data):
    """Test the data quality summary function"""
    prices_df, volumes_df = BMRSDataProcessor.clean_and_process_data(sample_raw_data)
    summary = BMRSDataProcessor.get_data_quality_summary(prices_df, volumes_df)
    
    # Check summary structure
    assert 'prices' in summary
    assert 'volumes' in summary
    assert 'missing_periods' in summary['prices']
    assert 'interpolated_periods' in summary['prices']
    assert 'missing_periods_pct' in summary['prices']

def test_anomaly_detection(sample_raw_data):
    """Test detection of price anomalies"""
    # Create an anomaly where sell price is higher than buy price
    sample_raw_data.loc[10, 'systemSellPrice'] = 110
    sample_raw_data.loc[10, 'systemBuyPrice'] = 100
    
    prices_df, _ = BMRSDataProcessor.clean_and_process_data(sample_raw_data)
    
    # Check anomaly is flagged
    assert (prices_df['price_quality'] == 'Anomaly').any()